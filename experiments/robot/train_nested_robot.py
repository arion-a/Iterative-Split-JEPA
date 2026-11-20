"""E77: a JEPA with the nested pair terms trained from scratch on the stored robot videos (registered in docs/EVIDENCE.md).
    python train_nested_robot.py DATA_DIR OUT_DIR [SEEDS=0,1,2,3,4] [STEPS=6000]
As train_jepa_robot.py (same data, split, encoder, predictor, adjacent-frame prediction), plus one pair-agreement term per rung. The 64 numbers are cut into fixed slices:
camera h[0:4] | trajectory h[4:16] | progress h[16:32] | layout h[32:64]. Pairs: rung 1 = the two cameras of one frame (order random); rung 2 = two different train trajectories, same group, same frame, same camera;
rung 3 = two frames >= 3 apart of one trajectory and camera. L = L_pred + sum_k [ L_inv,k + L_var,k ] + W ||Cov(h) - I||_F^2 + 0.01 L_var + 0.04 L_cov;
L_inv,k = mean squared difference of the slices slower than rung k across its pairs; L_var,k = mean over slice k's coordinates of max(0, sqrt(2) - std of the pair difference).
Writes OUT_DIR/E_N_s<seed>.npy ((G, 8, 30, 2, 64) float32), train_s<seed>.json, W.json."""
import sys, os, glob, json, math, time, numpy as np, torch, torch.nn as nn
ddir, out = sys.argv[1], sys.argv[2]; seeds = [int(s) for s in (sys.argv[3] if len(sys.argv) > 3 else "0,1,2,3,4").split(",")]; steps = int(sys.argv[4]) if len(sys.argv) > 4 else 6000
dev = "cuda" if torch.cuda.is_available() else "cpu"; os.makedirs(out, exist_ok=True); torch.set_num_threads(4)
SL = [(0, 4), (4, 16), (16, 32), (32, 64)]
files = sorted(glob.glob(f"{ddir}/group_*.npz")); G = len(files)
def load(f):
    x = np.load(f)["images"].astype(np.float32); x = x.reshape(*x.shape[:-3], 64, 2, 64, 2, 3).mean((-4, -2)); return x.astype(np.uint8)
X = torch.from_numpy(np.stack([load(f) for f in files])).permute(0, 1, 2, 3, 6, 4, 5).contiguous()
_, TT, K = X.shape[:3]; n_val = max(1, round(0.2 * TT)); g0 = torch.Generator().manual_seed(0)
perm = torch.stack([torch.randperm(TT, generator=g0) for _ in range(G)]); tr_idx = perm[:, n_val:]; NT = tr_idx.shape[1]
X = X.to(dev); tr_idx = tr_idx.to(dev); print("videos", tuple(X.shape), "train traj per group", NT, flush=True)
def make_enc():
    c = lambda i, o: nn.Sequential(nn.Conv2d(i, o, 4, 2, 1), nn.GELU()); return nn.Sequential(c(3, 32), c(32, 64), c(64, 128), c(128, 128), nn.Flatten(), nn.Linear(128 * 16, 64))
def make_pred(): return nn.Sequential(nn.Linear(64, 256), nn.GELU(), nn.Linear(256, 256), nn.GELU(), nn.Linear(256, 64))
def variance_hinge(h): return torch.relu(1 - torch.sqrt(h.var(0) + 1e-4)).sum()
def covariance_penalty(h):
    h = h - h.mean(0); c = h.T @ h / (len(h) - 1); off = c - torch.diag(torch.diag(c)); return off.square().sum() / h.shape[1]
R = lambda hi, gen, B: torch.randint(0, hi, (B,), generator=gen).to(dev)
def batches(B, gen):
    gg, kk, cc, ti = R(G, gen, B), R(K - 1, gen, B), R(2, gen, B), R(NT, gen, B); t = tr_idx[gg, ti]
    pred = (X[gg, t, kk, cc].float() / 255, X[gg, t, kk + 1, cc].float() / 255)
    gg, ti, kk = R(G, gen, B), R(NT, gen, B), R(K, gen, B); t = tr_idx[gg, ti]; sw = R(2, gen, B)                              # rung 1: the two cameras of one frame, order random
    p1 = (X[gg, t, kk, sw].float() / 255, X[gg, t, kk, 1 - sw].float() / 255)
    gg, ti, kk, cc = R(G, gen, B), R(NT, gen, B), R(K, gen, B), R(2, gen, B); t1 = tr_idx[gg, ti]; t2 = tr_idx[gg, (ti + 1 + R(NT - 1, gen, B)) % NT]   # rung 2: two different trajectories
    p2 = (X[gg, t1, kk, cc].float() / 255, X[gg, t2, kk, cc].float() / 255)
    gg, ti, cc, k1 = R(G, gen, B), R(NT, gen, B), R(2, gen, B), R(K, gen, B); t = tr_idx[gg, ti]; k2 = (k1 + 3 + R(K - 5, gen, B)) % K                      # rung 3: two frames >= 3 apart
    p3 = (X[gg, t, k1, cc].float() / 255, X[gg, t, k2, cc].float() / 255)
    return pred, (p1, p2, p3)
def pair_terms(g, pairs):
    tot, parts = 0.0, []
    for k, (u, v) in enumerate(pairs, 1):
        hu, hv = g(u), g(v); tail = slice(SL[k - 1][1], 64); lo, hi = SL[k - 1]
        inv = (hu[:, tail] - hv[:, tail]).square().mean(); var = torch.relu(math.sqrt(2.0) - (hu[:, lo:hi] - hv[:, lo:hi]).std(0)).mean()
        tot = tot + inv + var; parts.append((float(inv), float(var)))
    return tot, parts
def train(seed, W, n):
    torch.manual_seed(seed); g, f = make_enc().to(dev), make_pred().to(dev); gen = torch.Generator().manual_seed(seed); opt = torch.optim.AdamW(list(g.parameters()) + list(f.parameters()), lr=1e-3); log = []
    for s in range(n):
        lr = 1e-3 if s < n // 2 else 1e-3 * (1 + math.cos(math.pi * (s - n // 2) / max(n - n // 2, 1))) / 2
        for pg in opt.param_groups: pg["lr"] = lr
        (x1, x2), pairs = batches(256, gen); h1, h2 = g(x1), g(x2); pl = (f(h1) - h2.detach()).square().mean(); h = torch.cat([h1, h2]); pt, parts = pair_terms(g, pairs)
        loss = pl + pt + W * (torch.cov(h.T) - torch.eye(64, device=dev)).square().sum() + 0.01 * variance_hinge(h) + 0.04 * covariance_penalty(h)
        opt.zero_grad(); loss.backward(); opt.step()
        if s % 500 == 0 or s == n - 1: log.append({"step": s, "loss": float(loss), "pred": float(pl), "inv_var": parts}); print(seed, s, round(float(loss), 3), round(float(pl), 4), [(round(a, 3), round(b, 3)) for a, b in parts], flush=True)
    return g, f, log
def health(g):
    gen = torch.Generator().manual_seed(0)
    with torch.no_grad(): h = torch.cat([g(batches(512, gen)[0][0]) for _ in range(8)]).double()
    ev = torch.linalg.eigvalsh(torch.cov(h.T)); return float(ev.min()), int((ev > 1e-3 * ev.max()).sum())
def embed(g, path):
    parts = []
    with torch.no_grad():
        for i in range(G): parts.append(g(X[i].reshape(-1, 3, 64, 64).float() / 255).reshape(TT, K, 2, 64).cpu())
    np.save(path, torch.stack(parts).numpy().astype(np.float32))
W = None; pilot = {}
for cand in ([] if os.environ.get("FORCE_W") else (1, 10)):
    g, f, _ = train(0, cand, min(2000, steps)); lm, rk = health(g); pilot[cand] = lm; print("pilot W", cand, "min eig", round(lm, 3), flush=True)
    if lm >= 0.5: W = cand; break
W = float(os.environ["FORCE_W"]) if os.environ.get("FORCE_W") else W; json.dump({"W": W, "pilot_min_eig": pilot}, open(f"{out}/W.json", "w"))
if W is None: raise SystemExit("no healthy W: not run")
for seed in seeds:
    t0 = time.time(); g, f, log = train(seed, W, steps); lm, rk = health(g); embed(g, f"{out}/E_N_s{seed}.npy")
    json.dump({"seed": seed, "W": W, "steps": steps, "log": log, "final_pred": log[-1]["pred"], "health_N": lm, "rank_N": rk, "seconds": round(time.time() - t0)}, open(f"{out}/train_s{seed}.json", "w"), indent=1)
    print("seed", seed, "done", round(time.time() - t0), "s; health", round(lm, 3), "rank", rk, flush=True)
