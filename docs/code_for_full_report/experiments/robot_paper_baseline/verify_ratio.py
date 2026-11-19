"""Verification: re-score the 200-epoch embeddings with the paper's own block-response definition (Appendix D.2):
D_B(x,x') = (1/sqrt(d_B)) * || (r_B(x) - r_B(x')) / sigma_B ||_2, sigma_B = coordinate-wise std over held-out pair endpoints; ratio = D_L / D_H on viewpoint pairs.
Also: the E59-A split recomputed with centered pair differences (the paper's released code centers them; its text says uncentered).
    python verify_ratio.py TASK FEAT_DIR D_H OUT_JSON"""
import sys, glob, json, numpy as np, torch
task, feat, dH, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
E = torch.from_numpy(np.stack([np.load(f) for f in sorted(glob.glob(f"{feat}/group_*.npy"))])).double(); G, T, K, _, D = E.shape
g = torch.Generator().manual_seed(0); perm = torch.stack([torch.randperm(T, generator=g) for _ in range(G)]); nv = max(1, round(0.2 * T))
val = torch.stack([E[i, perm[i, :nv]] for i in range(G)]); tr = torch.stack([E[i, perm[i, nv:]] for i in range(G)])
vu, vv = val[..., 0, :].reshape(-1, D), val[..., 1, :].reshape(-1, D)
def D_B(P, u, v):                                    # paper's normalized response; P = (D, d_B) projection
    a, b = u @ P, v @ P; sig = torch.cat([a, b]).std(0); d = (((a - b) / sig).square().sum(1) / P.shape[1]).sqrt(); return float(d.mean()), float(d.square().mean().sqrt())
def ours(P, u, v):
    a, b = u @ P, v @ P; al = torch.cat([a, b]); rms = (al - al.mean(0)).square().sum(1).mean().sqrt(); return float((a - b).square().sum(1).mean().sqrt() / (2 ** .5 * rms))
I = torch.eye(D, dtype=torch.double); res = {"task": task}
def report(name, Pinv, Pvar):
    pm, pr = D_B(Pvar, vu, vv), D_B(Pinv, vu, vv); res[name] = {"paper_def_ratio_mean_of_norms": pm[0] / pr[0], "paper_def_ratio_rms": pm[1] / pr[1], "our_resp_ratio": ours(Pvar, vu, vv) / ours(Pinv, vu, vv), "D_L": pm[0], "D_H": pr[0]}
report("paper_halves", I[:, :dH], I[:, dH:])
a, b = tr[..., 0, :].reshape(-1, D), tr[..., 1, :].reshape(-1, D)
for nm, center in (("A_uncentered", False), ("A_centered", True)):
    Dm = a - b; Dm = Dm - Dm.mean(0) if center else Dm; lam, V = torch.linalg.eigh(Dm.T @ Dm / (len(Dm) - 1 if center else len(Dm))); report(nm, V[:, :dH], V[:, dH:])
json.dump(res, open(out, "w"), indent=1); print(json.dumps(res, indent=1))
