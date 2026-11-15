"""After training: (1) the paper's own split = the fixed slices [r_H ; r_L] of the trained encoder: how far apart do matched pairs end up in each slice on held-out trajectories;
(2) our iterated splitting on the same frozen embedding (viewpoint pairs for rung 1, trajectory pairs for rung 2), using experiments/robot/run_stage_c.py.
    python embed_and_ladder.py TASK CHECKPOINT"""
import sys, os, json, glob, subprocess
import numpy as np, torch
sys.path.insert(0, "robot")
from hl_maniskill.models import VisualEncoder
from hl_maniskill.data import image_norm_params
task, ckpt = sys.argv[1], sys.argv[2]; dev = "cuda"
ck = torch.load(ckpt, map_location=dev); c = ck["encoder_cfg"]
enc = VisualEncoder(backbone=c["backbone"], pretrained=False, zh_dim=c["zh_dim"], zl_dim=c["zl_dim"], pool="avg", normalize=c["normalize"]).to(dev); enc.load_state_dict(ck["state_dict"]); enc.eval()
mean, std = image_norm_params(c["image_norm"]); m = torch.tensor(mean, device=dev).view(1, 3, 1, 1); s = torch.tensor(std, device=dev).view(1, 3, 1, 1)
files = sorted(glob.glob(f"data/robot/{task}/group_*.npz")); out = "data/robot_paper"; os.makedirs(f"{out}/feat/{task}", exist_ok=True); os.makedirs(f"{out}/{task}", exist_ok=True)
E = []
with torch.no_grad():
    for f in files:
        d = np.load(f); img = torch.from_numpy(d["images"]).reshape(-1, 128, 128, 3).to(dev).permute(0, 3, 1, 2).float() / 255.0
        zs = []
        for i in range(0, len(img), 240):
            zh, zl = enc((img[i:i + 240] - m) / s); zs.append(torch.cat([zh, zl], 1).float().cpu())
        z = torch.cat(zs).reshape(*d["images"].shape[:3], -1).numpy(); E.append(z)
        base = os.path.basename(f)[:-4]; np.save(f"{out}/feat/{task}/{base}.npy", z); np.savez(f"{out}/{task}/{base}.npz", state=d["state"])
E = torch.from_numpy(np.stack(E)); G, T, K, _, D = E.shape; dH = c["zh_dim"]; print("embedded", tuple(E.shape), flush=True)
g = torch.Generator().manual_seed(0); perm = torch.stack([torch.randperm(T, generator=g) for _ in range(G)]); n_val = max(1, round(0.2 * T)); val = perm[:, :n_val]
Ev = torch.stack([E[i, val[i]] for i in range(G)])                       # (G, n_val, K, 2, D) held-out trajectories
def resp(B, u, v):
    bu, bv = u[:, B], v[:, B]; allb = torch.cat([bu, bv]); rms = (allb - allb.mean(0)).square().sum(1).mean().sqrt()
    return float((bu - bv).square().sum(1).mean().sqrt() / (2 ** 0.5 * rms))
H, L = list(range(dH)), list(range(dH, D))
vu, vv = Ev[..., 0, :].reshape(-1, D), Ev[..., 1, :].reshape(-1, D); tu, tv = Ev[:, 0, :, 0, :].reshape(-1, D), Ev[:, 1, :, 0, :].reshape(-1, D)
res = {"task": task, "embedding_dim": D, "d_H": dH, "view_response": {"H(invariant)": resp(H, vu, vv), "L(variant)": resp(L, vu, vv)}, "traj_response": {"H(invariant)": resp(H, tu, tv), "L(variant)": resp(L, tu, tv)}}
res["paper_ratio_view_L_over_H"] = res["view_response"]["L(variant)"] / res["view_response"]["H(invariant)"]; res["paper_ratio_traj_L_over_H"] = res["traj_response"]["L(variant)"] / res["traj_response"]["H(invariant)"]
os.makedirs("results/paper_baseline", exist_ok=True); json.dump(res, open(f"results/paper_baseline/{task}_paper_fixed_slice.json", "w"), indent=1); print(json.dumps(res, indent=1), flush=True)
subprocess.run([sys.executable, "experiments/robot/run_stage_c.py", "--task", task, "--data", out, "--encoder", "pca", "--pca", str(D), "--out", "results/paper_baseline/ladder"], check=True, env={**os.environ, "PYTHONPATH": "src"})
