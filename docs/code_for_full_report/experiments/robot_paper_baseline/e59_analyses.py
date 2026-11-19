"""E59 (registered in docs/EVIDENCE.md): two analyses on the downloaded paper-trained embeddings (CPU).
A: eigen-split of viewpoint-pair differences in the RAW embedding (no whitening), block size = d_H; score = viewpoint ratio like the paper's halves.
B: paper's halves as rung 1; whiten inside r_H (first d_H coords); rung 2 on trajectory pairs (same group, same progress, camera 0).
Fit on the 6 training trajectories per group, score on the 2 held-out (same seed-0 split as embed_and_ladder.py).
    python e59_analyses.py TASK FEAT_DIR OUT_JSON D_H"""
import sys, glob, json
import numpy as np, torch
task, feat, out, dH = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
E = torch.from_numpy(np.stack([np.load(f) for f in sorted(glob.glob(f"{feat}/group_*.npy"))])).double()  # (G,T,K,2,D)
G, T, K, _, D = E.shape; g = torch.Generator().manual_seed(0)
perm = torch.stack([torch.randperm(T, generator=g) for _ in range(G)]); nv = max(1, round(0.2 * T))
val = torch.stack([E[i, perm[i, :nv]] for i in range(G)]); tr = torch.stack([E[i, perm[i, nv:]] for i in range(G)])
def resp(P, u, v):  # same definition as the paper-baseline script, in a projected basis
    bu, bv = u @ P, v @ P; a = torch.cat([bu, bv]); rms = (a - a.mean(0)).square().sum(1).mean().sqrt()
    return float((bu - bv).square().sum(1).mean().sqrt() / (2 ** 0.5 * rms))
def view(X): return X[..., 0, :].reshape(-1, D), X[..., 1, :].reshape(-1, D)
def traj(X): return X[:, 0, :, 0, :].reshape(-1, D), X[:, 1, :, 0, :].reshape(-1, D)
res = {"task": task, "D": D, "d_H": dH, "groups": G, "train_traj": T - nv, "val_traj": nv}
# --- paper's fixed halves (reference, recomputed here)
I = torch.eye(D, dtype=torch.double); vu, vv = view(val); tu, tv = traj(val)
res["paper_halves"] = {"view_ratio": resp(I[:, dH:], vu, vv) / resp(I[:, :dH], vu, vv), "traj_ratio": resp(I[:, dH:], tu, tv) / resp(I[:, :dH], tu, tv)}
# --- A: no whitening, eigen-split of viewpoint-pair differences
a, b = view(tr); Dm = a - b; M = Dm.T @ Dm / len(Dm); lam, V = torch.linalg.eigh(M)  # ascending
Vinv, Vvar = V[:, :dH], V[:, dH:]  # smallest-variance directions = invariant block; the rest = variant
res["A_no_whitening"] = {"view_ratio": resp(Vvar, vu, vv) / resp(Vinv, vu, vv), "traj_ratio": resp(Vvar, tu, tv) / resp(Vinv, tu, tv),
                         "eig_ratio_at_dH": float(lam[dH] / lam[dH - 1]), "eig_smallest": [float(x) for x in lam[:3]], "eig_largest": [float(x) for x in lam[-3:]]}
# --- B: paper halves as rung 1; whiten inside r_H; rung 2 on trajectory pairs
H = tr[..., :dH]; flat = H.reshape(-1, dH); mu = flat.mean(0); C = torch.cov((flat - mu).T); w, U = torch.linalg.eigh(C)
W = U @ torch.diag(w.clamp_min(1e-9).rsqrt()) @ U.T
def white(x): return (x - mu) @ W
a, b = traj(tr); Dm = white(a[..., :dH]) - white(b[..., :dH]); M2 = Dm.T @ Dm / len(Dm); l2, V2 = torch.linalg.eigh(M2); l2, V2 = l2.flip(0), V2.flip(1)
ratios = l2[:-1] / l2[1:]; dmax = int(ratios[:16].argmax()) + 1
res["B_rung2_inside_rH"] = {"eig_top10": [float(x) for x in l2[:10]], "gap_at_best_d<=16": float(ratios[dmax - 1]), "best_d": dmax, "gap_at_d4": float(ratios[3]), "n_dims": dH}
# readouts from found block vs leftover core on held-out data (ridge, R^2): progress, start state
Hv = white(val[..., :dH].reshape(-1, dH)); Z = Hv @ V2; Blk, Core = Z[:, :dmax], Z[:, dmax:]
Hq = white(val[:, :, :, 0, :dH].reshape(-1, dH)); Zq = Hq @ V2; Bq, Cq = Zq[:, :dmax], Zq[:, dmax:]
pg = torch.arange(K).double().div(K - 1).repeat(G * nv)
def r2(X, y, lam=1.0):  # ridge fit on first half of groups, test on rest
    n = len(X); idx = torch.arange(n); cut = n // 2; tri, tei = idx[:cut], idx[cut:]
    Xa = torch.cat([X, torch.ones(n, 1, dtype=X.dtype)], 1); A = Xa[tri].T @ Xa[tri] + lam * torch.eye(Xa.shape[1], dtype=X.dtype)
    beta = torch.linalg.solve(A, Xa[tri].T @ y[tri]); p = Xa[tei] @ beta; return float(1 - ((y[tei] - p) ** 2).sum() / ((y[tei] - y[tei].mean(0)) ** 2).sum())
res["B_rung2_inside_rH"]["progress_R2_from_found_block"] = r2(Bq, pg); res["B_rung2_inside_rH"]["progress_R2_from_core"] = r2(Cq, pg)
tu2, tv2 = traj(val); Ptraj = white(tu2[..., :dH]) @ V2; Qtraj = white(tv2[..., :dH]) @ V2
def r_(Pu, Pv): a_ = torch.cat([Pu, Pv]); rms = (a_ - a_.mean(0)).square().sum(1).mean().sqrt(); return float((Pu - Pv).square().sum(1).mean().sqrt() / (2 ** 0.5 * rms))
res["B_rung2_inside_rH"]["traj_ratio_found_block_over_rest"] = r_(Ptraj[:, :dmax], Qtraj[:, :dmax]) / r_(Ptraj[:, dmax:], Qtraj[:, dmax:])
json.dump(res, open(out, "w"), indent=1); print(json.dumps(res, indent=1))
