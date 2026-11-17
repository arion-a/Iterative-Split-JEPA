"""E66 training: the paper's robot recipe (code unchanged except this file) with the invariant half split into a static head z_S and a progress head z_P,
and ONE added invariance term: same-trajectory pairs, same camera, >= LAG_MIN steps apart, must agree on z_S.
    python train_split3.py TASK EPOCHS      (run from the work directory; TASK = PickCube or PushCube)
env: MAX_STEPS (smoke test), LAG_MIN (default 10)."""
import sys, os, time, json
os.chdir("robot"); sys.path.insert(0, ".")
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from tqdm import tqdm
from hl_maniskill.config import load_config
from hl_maniskill.data import TemporalDataset, PairDataset, EpisodeStore, preprocess_image, image_norm_params, load_episode_lens, make_split_pair_arrays
from hl_maniskill.models import LatentPredictor, predictive_loss, invariance_loss, variance_loss, covariance_loss, _build_backbone
from hl_maniskill.utils import default_device, load_json, make_run_dir, save_json
task, epochs = sys.argv[1], int(sys.argv[2]); LAG_MIN = int(os.environ.get("LAG_MIN", 10)); MAX_STEPS = int(os.environ.get("MAX_STEPS", 0))
class ThreeHeadEncoder(nn.Module):
    def __init__(self, backbone, pretrained, ds, dp, dl):
        super().__init__(); self.shared_trunk, f = _build_backbone(backbone, pretrained); self.dims = (ds, dp, dl)
        mk = lambda d: nn.Sequential(nn.Linear(f, 512), nn.ReLU(inplace=True), nn.Linear(512, d)); self.head_s, self.head_p, self.head_l = mk(ds), mk(dp), mk(dl)
    def forward(self, x): h = self.shared_trunk(x); return self.head_s(h), self.head_p(h), self.head_l(h)
class LagDataset(Dataset):
    """same trajectory, base camera, two time steps at least lag_min apart (the added pair kind)"""
    def __init__(self, ep_dir, episode_ids, lens, per_ep, lag_min, size, mean, std, seed=0):
        self.store = EpisodeStore(ep_dir); self.size, self.mean, self.std = size, mean, std; rng = np.random.RandomState(seed); self.items = []
        for ep in episode_ids:
            T = lens[ep]
            for _ in range(per_ep):
                ta = rng.randint(0, T - lag_min); tb = rng.randint(ta + lag_min, T); self.items.append((ep, ta, tb) if rng.rand() < .5 else (ep, tb, ta))
    def __len__(self): return len(self.items)
    def __getitem__(self, i):
        ep, ta, tb = self.items[i]; d = self.store[ep]
        return dict(x_a=preprocess_image(d["image_base"][ta], self.size, self.mean, self.std), x_b=preprocess_image(d["image_base"][tb], self.size, self.mean, self.std))
cfg = load_config([f"configs/{task.lower()}.yaml"], overrides=[f"rep.epochs={epochs}"], root="."); rep = cfg.rep; mt = cfg.experiment
dtot = int(rep.zh_dim) + int(rep.zl_dim); ds_, dp_, dl_ = int(rep.zh_dim) // 2, int(rep.zh_dim) - int(rep.zh_dim) // 2, int(rep.zl_dim)
torch.manual_seed(0); device = torch.device(default_device(rep.get("device", None))); mean, std = image_norm_params(rep.encoder.get("image_norm", "none"))
root = Path(cfg.paths.data_root) / f"{cfg.data.task}_{mt.tag}"; split = load_json(root / "split.json"); lens = load_episode_lens(root); train_eps = sorted(map(int, split["train"]))
size = int(rep.image_size); bs = int(rep.batch_size); la = dict(batch_size=bs, shuffle=True, drop_last=True, num_workers=int(rep.get("num_workers", 0)))
pred_loader = DataLoader(TemporalDataset(root / "episodes", train_eps, lens, size, mean, std), **la)
pair_loader = DataLoader(PairDataset(root / "episodes", make_split_pair_arrays(root, "train"), size, mean, std), **la)
lag_loader = DataLoader(LagDataset(root / "episodes", train_eps, lens, 90, LAG_MIN, size, mean, std), **la); steps = len(pred_loader)
enc = ThreeHeadEncoder(rep.encoder.backbone, bool(rep.encoder.get("pretrained", False)), ds_, dp_, dl_).to(device); pred = LatentPredictor(dtot, int(mt.require_action_dim), hidden=int(rep.predictor.hidden)).to(device)
params = list(enc.parameters()) + list(pred.parameters()); opt = torch.optim.AdamW(params, lr=float(rep.lr), weight_decay=float(rep.get("weight_decay", 1e-4))); sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
W = dict(rep.loss_weights); run_dir = make_run_dir(Path(cfg.paths.exp_root), "representation", f"{task.lower()}_split3_seed0"); metrics = {"task": task, "dims": [ds_, dp_, dl_], "lag_min": LAG_MIN, "train": []}
mv = lambda b: {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in b.items()}
def cyc(loader):
    while True:
        for b in loader: yield b
pair_it, lag_it = cyc(pair_loader), cyc(lag_loader); step_total = 0
for epoch in range(epochs):
    enc.train(); pred.train(); tot = {}; bar = tqdm(pred_loader, total=steps, desc=f"split3 {task} epoch={epoch}")
    for step, p in enumerate(bar):
        p, q, l = mv(p), mv(next(pair_it)), mv(next(lag_it)); B = p["x_t"].shape[0]
        zs, zp, zl = enc(torch.cat([p["x_t"], p["x_t1"], q["x_a"], q["x_b"], l["x_a"], l["x_b"]], 0)); zs, zp, zl = zs.split(B), zp.split(B), zl.split(B)
        z = [torch.cat([zs[i], zp[i], zl[i]], -1) for i in range(6)]
        l_pred = predictive_loss(pred(z[0], p["a_t"]), z[1]); l_inv = invariance_loss(torch.cat([zs[2], zp[2]], -1), torch.cat([zs[3], zp[3]], -1)); l_lag = invariance_loss(zs[4], zs[5])
        bz = torch.cat([z[0], z[1], z[2], z[3], z[4], z[5]]); l_var = variance_loss(bz); l_cov = covariance_loss(bz)
        loss = W["pred"] * l_pred + W["inv"] * l_inv + W["inv"] * l_lag + W["variance"] * l_var + W["covariance"] * l_cov
        opt.zero_grad(set_to_none=True); loss.backward(); nn.utils.clip_grad_norm_(params, float(rep.get("grad_clip", 10.0))); opt.step()
        for k, v in (("pred", l_pred), ("inv", l_inv), ("lag", l_lag), ("variance", l_var), ("covariance", l_cov)): tot[k] = tot.get(k, 0.0) + float(v.detach())
        bar.set_postfix({k: f"{v / (step + 1):.4f}" for k, v in tot.items()}); step_total += 1
        if MAX_STEPS and step_total >= MAX_STEPS: break
    sched.step(); metrics["train"].append({"epoch": epoch, **{k: v / max(1, step + 1) for k, v in tot.items()}})
    if MAX_STEPS and step_total >= MAX_STEPS: break
torch.save({"state_dict": enc.state_dict(), "dims": [ds_, dp_, dl_], "backbone": rep.encoder.backbone, "image_norm": str(rep.encoder.get("image_norm", "none")), "image_size": size}, run_dir / "encoder.pt")
save_json(run_dir / "metrics.json", metrics); print("DONE", run_dir, flush=True)
