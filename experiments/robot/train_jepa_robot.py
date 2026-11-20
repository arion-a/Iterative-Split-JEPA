"""E76: a JEPA trained from scratch on the stored robot videos (pixels), then its embedding of every frame (registered in docs/EVIDENCE.md).
    python train_jepa_robot.py DATA_DIR OUT_DIR [SEEDS=0,1,2,3,4] [STEPS=6000]        DATA_DIR = data/robot/PickCube (group_*.npz: images (8, 30, 2, 128, 128, 3), state, ...)
Images are reduced to 64 x 64 (2 x 2 averages). Train/validation trajectories per group: the same seed-0 split as experiments/robot/run_stage_c.py (6 train, 2 validation of 8); the JEPA sees train trajectories only.
Training example: two ADJACENT frames of the same trajectory and the same camera. encoder g: conv 3-32-64-128-128 (4 x 4, stride 2, GELU) + linear -> 64 numbers; predictor f: MLP 64-256-256-64.
Loss = mean||f(h_t) - sg(h_t+1)||^2 + W ||Cov(h) - I||_F^2 + 0.01 L_var + 0.04 L_cov; W = the smaller of {1, 10} whose 2,000-step pilot keeps lambda_min(Cov h) >= 0.5.
Writes OUT_DIR/E_J_s<seed>.npy and E_U_s<seed>.npy (trained / same random start untrained; shape (G, 8, 30, 2, 64) float32), train_s<seed>.json, W.json."""
import sys, os, glob, json, math, time, numpy as np, torch, torch.nn as nn
ddir, out = sys.argv[1], sys.argv[2]; seeds = [int(s) for s in (sys.argv[3] if len(sys.argv) > 3 else "0,1,2,3,4").split(",")]; steps = int(sys.argv[4]) if len(sys.argv) > 4 else 6000
dev = "cuda" if torch.cuda.is_available() else "cpu"; os.makedirs(out, exist_ok=True); torch.set_num_threads(4)
files = sorted(glob.glob(f"{ddir}/group_*.npz")); G = len(files)
def load(f):
    x = np.load(f)["images"].astype(np.float32); x = x.reshape(*x.shape[:-3], 64, 2, 64, 2, 3).mean((-4, -2)); return x.astype(np.uint8)       # (8, 30, 2, 64, 64, 3)
X = torch.from_numpy(np.stack([load(f) for f in files])).permute(0, 1, 2, 3, 6, 4, 5).contiguous()                    # (G, 8, K, 2, 3, 64, 64)
_, TT, K = X.shape[:3]; n_val = max(1, round(0.2 * TT)); g0 = torch.Generator().manual_seed(0)
perm = torch.stack([torch.randperm(TT, generator=g0) for _ in range(G)]); tr_idx = perm[:, n_val:]
X = X.to(dev); tr_idx = tr_idx.to(dev); print("videos", tuple(X.shape), "train traj per group", tr_idx.shape[1], flush=True)
def make_enc():
    c = lambda i, o: nn.Sequential(nn.Conv2d(i, o, 4, 2, 1), nn.GELU()); return nn.Sequential(c(3, 32), c(32, 64), c(64, 128), c(128, 128), nn.Flatten(), nn.Linear(128 * 16, 64))
def make_pred(): return nn.Sequential(nn.Linear(64, 256), nn.GELU(), nn.Linear(256, 256), nn.GELU(), nn.Linear(256, 64))
def variance_hinge(h): return torch.relu(1 - torch.sqrt(h.var(0) + 1e-4)).sum()
def covariance_penalty(h):
    h = h - h.mean(0); c = h.T @ h / (len(h) - 1); off = c - torch.diag(torch.diag(c)); return off.square().sum() / h.shape[1]
def batch(B, gen):
    gg = torch.randint(0, G, (B,), generator=gen).to(dev); tt = tr_idx[gg, torch.randint(0, tr_idx.shape[1], (B,), generator=gen).to(dev)]
    kk = torch.randint(0, K - 1, (B,), generator=gen).to(dev); cc = torch.randint(0, 2, (B,), generator=gen).to(dev)
    return X[gg, tt, kk, cc].float() / 255, X[gg, tt, kk + 1, cc].float() / 255
def train(seed, W, n):
    torch.manual_seed(seed); g, f = make_enc().to(dev), make_pred().to(dev); gen = torch.Generator().manual_seed(seed); opt = torch.optim.AdamW(list(g.parameters()) + list(f.parameters()), lr=1e-3); log = []
    for s in range(n):
        lr = 1e-3 if s < n // 2 else 1e-3 * (1 + math.cos(math.pi * (s - n // 2) / max(n - n // 2, 1))) / 2
        for pg in opt.param_groups: pg["lr"] = lr
        x1, x2 = batch(256, gen); h1, h2 = g(x1), g(x2); pl = (f(h1) - h2.detach()).square().mean(); h = torch.cat([h1, h2])
        loss = pl + W * (torch.cov(h.T) - torch.eye(64, device=dev)).square().sum() + 0.01 * variance_hinge(h) + 0.04 * covariance_penalty(h)
        opt.zero_grad(); loss.backward(); opt.step()
        if s % 500 == 0 or s == n - 1: log.append({"step": s, "loss": float(loss), "pred": float(pl)}); print(seed, s, round(float(loss), 4), round(float(pl), 4), flush=True)
    return g, f, log
def health(g):
    gen = torch.Generator().manual_seed(0)
    with torch.no_grad(): h = torch.cat([g(batch(512, gen)[0]) for _ in range(8)]).double()
    ev = torch.linalg.eigvalsh(torch.cov(h.T)); return float(ev.min()), int((ev > 1e-3 * ev.max()).sum())
def embed(g, path):
    parts = []
    with torch.no_grad():
        for i in range(0, G):
            parts.append(g(X[i].reshape(-1, 3, 64, 64).float() / 255).reshape(TT, K, 2, 64).cpu())
    np.save(path, torch.stack(parts).numpy().astype(np.float32))
W = None; pilot = {}
for cand in ([] if os.environ.get("FORCE_W") else (1, 10)):
    g, f, _ = train(0, cand, min(2000, steps)); lm, rk = health(g); pilot[cand] = lm; print("pilot W", cand, "min eig", round(lm, 3), flush=True)
    if lm >= 0.5: W = cand; break
W = float(os.environ["FORCE_W"]) if os.environ.get("FORCE_W") else W; json.dump({"W": W, "pilot_min_eig": pilot}, open(f"{out}/W.json", "w"))
if W is None: raise SystemExit("no healthy W: not run")
for seed in seeds:
    t0 = time.time(); torch.manual_seed(seed); gu = make_enc().to(dev); lmu, rku = health(gu); g, f, log = train(seed, W, steps); lm, rk = health(g)
    embed(g, f"{out}/E_J_s{seed}.npy"); embed(gu, f"{out}/E_U_s{seed}.npy")
    json.dump({"seed": seed, "W": W, "steps": steps, "log": log, "final_pred": log[-1]["pred"], "health_J": lm, "rank_J": rk, "health_U": lmu, "rank_U": rku, "seconds": round(time.time() - t0)}, open(f"{out}/train_s{seed}.json", "w"), indent=1)
    print("seed", seed, "done", round(time.time() - t0), "s; health J", round(lm, 3), "rank", rk, "| U", round(lmu, 3), rku, flush=True)
