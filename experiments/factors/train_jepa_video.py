"""E75: a JEPA trained on the rendered videos, then its embeddings of the E62 evaluation images (registered in docs/EVIDENCE.md).
    python train_jepa_video.py VIDEO_DIR IMAGES_NPZ OUT_DIR [SEEDS=0,1,2,3,4] [STEPS=6000]
encoder g = the E62 conv encoder (3-32-64-128-128, 4 x 4 kernels, stride 2, GELU, linear to 48); predictor f = MLP 48-256-256-48 (GELU).
Loss = mean||f(h_t) - sg(h_t+1)||^2 + W ||Cov(h) - I||_F^2 + 0.01 L_var + 0.04 L_cov; W = the smaller of {1, 10} whose 2,000-step pilot (seed 0) keeps lambda_min(Cov h) >= 0.5.
Writes OUT_DIR/emb_J_s<seed>.npz (trained), emb_U_s<seed>.npz (same random start, untrained), train_s<seed>.json. Embeddings: Zp, Zu1..8, Zv1..8 of IMAGES_NPZ."""
import sys, os, glob, json, math, time, numpy as np, torch, torch.nn as nn
vdir, images, out = sys.argv[1], sys.argv[2], sys.argv[3]; seeds = [int(s) for s in (sys.argv[4] if len(sys.argv) > 4 else "0,1,2,3,4").split(",")]; steps = int(sys.argv[5]) if len(sys.argv) > 5 else 6000
dev = "cuda" if torch.cuda.is_available() else "cpu"; os.makedirs(out, exist_ok=True)
def make_enc():
    c = lambda i, o: nn.Sequential(nn.Conv2d(i, o, 4, 2, 1), nn.GELU())
    return nn.Sequential(c(3, 32), c(32, 64), c(64, 128), c(128, 128), nn.Flatten(), nn.Linear(128 * 36, 48))
def make_pred(): return nn.Sequential(nn.Linear(48, 256), nn.GELU(), nn.Linear(256, 256), nn.GELU(), nn.Linear(256, 48))
def variance_hinge(h): return torch.relu(1 - torch.sqrt(h.var(0) + 1e-4)).sum()
def covariance_penalty(h):
    h = h - h.mean(0); c = h.T @ h / (len(h) - 1); off = c - torch.diag(torch.diag(c)); return off.square().sum() / h.shape[1]
def jepa_loss(g, f, x1, x2, W):
    h1, h2 = g(x1), g(x2); pred = (f(h1) - h2.detach()).square().mean(); h = torch.cat([h1, h2]); cov = torch.cov(h.T)
    return pred + W * (cov - torch.eye(48, device=h.device)).square().sum() + 0.01 * variance_hinge(h) + 0.04 * covariance_penalty(h), float(pred)
files = sorted(glob.glob(f"{vdir}/videos_*.npz")); X = torch.from_numpy(np.concatenate([np.load(f)["x"] for f in files])); NV, T = X.shape[0], X.shape[1]
X = X.permute(0, 1, 4, 2, 3).contiguous().to(dev); print("videos", tuple(X.shape), flush=True)
def batch(B, gen):
    v = torch.randint(0, NV, (B,), generator=gen, device="cpu"); t = torch.randint(0, T - 1, (B,), generator=gen, device="cpu")
    return X[v.to(dev), t.to(dev)].float() / 255, X[v.to(dev), (t + 1).to(dev)].float() / 255
def train(seed, W, n):
    torch.manual_seed(seed); g, f = make_enc().to(dev), make_pred().to(dev); gen = torch.Generator().manual_seed(seed); opt = torch.optim.AdamW(list(g.parameters()) + list(f.parameters()), lr=1e-3); log = []
    for s in range(n):
        lr = 1e-3 if s < n // 2 else 1e-3 * (1 + math.cos(math.pi * (s - n // 2) / max(n - n // 2, 1))) / 2
        for pg in opt.param_groups: pg["lr"] = lr
        x1, x2 = batch(256, gen); loss, pl = jepa_loss(g, f, x1, x2, W); opt.zero_grad(); loss.backward(); opt.step()
        if s % 500 == 0 or s == n - 1: log.append({"step": s, "loss": float(loss), "pred": pl}); print(seed, s, round(float(loss), 4), round(pl, 4), flush=True)
    return g, f, log
def health(g, gen_seed=0):
    gen = torch.Generator().manual_seed(gen_seed)
    with torch.no_grad(): h = torch.cat([g(batch(512, gen)[0]) for _ in range(8)]).double()
    ev = torch.linalg.eigvalsh(torch.cov(h.T)); return float(ev.min()), int((ev > 1e-3 * ev.max()).sum())
def embed(g, D, path):
    res = {}
    for key in ["probe"] + [f"{a}{k}" for k in range(1, 9) for a in "uv"]:
        Xi = D[key]; parts = []
        with torch.no_grad():
            for i in range(0, len(Xi), 500): parts.append(g(torch.from_numpy(Xi[i:i + 500]).permute(0, 3, 1, 2).float().div(255).to(dev)).cpu())
        res["Zp" if key == "probe" else f"Z{key}"] = torch.cat(parts).numpy().astype(np.float32)
    np.savez(path, **res)
D = np.load(images); W = None; pilot = {}
for cand in ([] if os.environ.get("FORCE_W") else (1, 10)):  # FORCE_W: smoke tests only
    g, f, _ = train(0, cand, min(2000, steps)); lm, rk = health(g); pilot[cand] = lm; print("pilot W", cand, "min eig", round(lm, 3), flush=True)
    if lm >= 0.5: W = cand; break
W = float(os.environ["FORCE_W"]) if os.environ.get("FORCE_W") else W
json.dump({"W": W, "pilot_min_eig": pilot}, open(f"{out}/W.json", "w"))
if W is None: raise SystemExit("no healthy W: not run")
for seed in seeds:
    t0 = time.time(); torch.manual_seed(seed); gu = make_enc().to(dev); lmu, rku = health(gu)
    g, f, log = train(seed, W, steps); lm, rk = health(g)
    embed(g, D, f"{out}/emb_J_s{seed}.npz"); embed(gu, D, f"{out}/emb_U_s{seed}.npz")
    json.dump({"seed": seed, "W": W, "steps": steps, "log": log, "final_pred": log[-1]["pred"], "health_J": lm, "rank_J": rk, "health_U": lmu, "rank_U": rku, "seconds": round(time.time() - t0)}, open(f"{out}/train_s{seed}.json", "w"), indent=1)
    print("seed", seed, "done", round(time.time() - t0), "s; health J", round(lm, 3), "rank", rk, "| U", round(lmu, 3), rku, flush=True)
