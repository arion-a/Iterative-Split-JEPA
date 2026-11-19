"""E60 (registered in docs/EVIDENCE.md): robot ladder to rung 3 on the paper-trained 200-epoch embeddings.
rung 1 camera pairs (no-whitening eigen-split, E59-A), rung 2 trajectory pairs, rung 3 progress pairs; engine functions as in Stage C.
    PYTHONPATH=src python e60_ladder3.py TASK FEAT_DIR STATE_DIR OUT_JSON D_H"""
import sys, glob, json
import numpy as np, torch
from isj import audits
from isj.engine import fit_rung, fit_whitener, select_block_count
task, feat, st, out, dH = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
fs = sorted(glob.glob(f"{feat}/group_*.npy"))
E = torch.from_numpy(np.stack([np.load(f) for f in fs])).double()                       # (G,T,K,2,D)
S = torch.from_numpy(np.stack([np.load(f"{st}/{f.split('/')[-1][:-4]}.npz")["state"] for f in fs])).double()   # (G,T,K,9)
G, T, K, _, D = E.shape; g = torch.Generator().manual_seed(0)
perm = torch.stack([torch.randperm(T, generator=g) for _ in range(G)]); nv = max(1, round(0.2 * T))
take = lambda X, idx: torch.stack([X[i, idx[i]] for i in range(G)])
Etr, Eva = take(E, perm[:, nv:]), take(E, perm[:, :nv]); Str, Sva = take(S, perm[:, nv:]), take(S, perm[:, :nv]); nt = Etr.shape[1]
gen = torch.Generator().manual_seed(5)
def swap(ru, rv):
    m = torch.rand(len(ru), generator=gen) < 0.5; return torch.where(m[:, None], rv, ru), torch.where(m[:, None], ru, rv)
def fit_rule(ru, rv, h_prev, k):
    probe = fit_rung(ru, rv, h_prev, k=k, d_k=1); vals = probe.eigvals.double(); d = select_block_count(vals, 0.1 * float(vals[0])); flagged = False
    if d == 0: d = int(torch.argmax(vals[:32] / vals[1:33].clamp_min(1e-12))) + 1; flagged = True
    f = fit_rung(ru, rv, h_prev, k=k, d_k=d)
    return f, {"d": d, "gap_ratio": f.gap_ratio, "no_cliff_fallback": flagged, "top_eigvals": [float(x) for x in f.eigvals[:8]]}
res = {"task": task, "D": D, "d_H": dH, "groups": G, "train_traj": nt, "val_traj": int(nv)}
# ---- rung 1: camera pairs, no whitening (E59-A)
a, b = Etr[..., 0, :].reshape(-1, D), Etr[..., 1, :].reshape(-1, D); M1 = (a - b).T @ (a - b) / len(a); lam1, V = torch.linalg.eigh(M1)
Vinv, V1 = V[:, :dH], V[:, dH:]; res["rung1"] = {"block_variant": D - dH, "eig_ratio_at_cut": float(lam1[dH] / lam1[dH - 1])}
mu = Etr.reshape(-1, D).mean(0); cont = lambda X: (X - mu) @ Vinv                     # content after rung 1 (d_H dims)
wh = fit_whitener(cont(Etr.reshape(-1, D)).float(), 1e-5)
R = lambda X: wh(cont(X.reshape(-1, D)).float()).double().reshape(*X.shape[:-1], dH)
Rtr, Rva = R(Etr), R(Eva)                                                                # (G,n,K,2,dH), whitened inside the content
c0tr, c0va = Rtr[..., 0, :], Rva[..., 0, :]                                              # camera 0
# ---- rung 2: trajectory pairs (same group, same progress, same camera)
ia, ib = torch.triu_indices(nt, nt, offset=1); u2, v2 = swap(c0tr[:, ia].reshape(-1, dH), c0tr[:, ib].reshape(-1, dH))
f2, i2 = fit_rule(u2, v2, torch.eye(dH), 2); res["rung2"] = i2
# ---- rung 3: progress pairs (same group, same trajectory, same camera, >= 3 steps apart), inside the content left by rung 2
gp = torch.Generator().manual_seed(9); npair = 40
k1 = torch.randint(0, K, (G, nt, npair), generator=gp); k2 = (k1 + torch.randint(3, K - 2, (G, nt, npair), generator=gp)) % K
gi = torch.arange(G)[:, None, None].expand_as(k1); ti = torch.arange(nt)[None, :, None].expand_as(k1)
u3, v3 = swap(c0tr[gi, ti, k1].reshape(-1, dH), c0tr[gi, ti, k2].reshape(-1, dH))
f3, i3 = fit_rule(u3, v3, f2.Q, 3); res["rung3"] = i3; res["rung3"]["n_pairs"] = len(u3)
sh = fit_rung(u3, v3[torch.randperm(len(v3), generator=torch.Generator().manual_seed(3))], f2.Q, k=3, d_k=i3["d"]); res["rung3"]["shuffled_pairs_gap"] = sh.gap_ratio
# ---- readouts (ridge, held-out)
lay = lambda S_: torch.cat([S_[:, :, 0, 3:5].unsqueeze(2).expand(-1, -1, K, -1), S_[:, :, :, 6:9]], 3).reshape(-1, 5)
prog = lambda S_: torch.linspace(0, 1, K).view(1, 1, K).expand(S_.shape[0], S_.shape[1], K).reshape(-1, 1).double()
Ltr, Lva, Ptr, Pva = lay(Str), lay(Sva), prog(Str), prog(Sva)
xt, xv = c0tr.reshape(-1, dH), c0va.reshape(-1, dH)
def r2(B, y_tr, y_va): return audits.linear_r2(xt @ B, y_tr, xv @ B, y_va)
I = torch.eye(dH, dtype=torch.double); Q3, V3, V2, Q2 = f3.Q.double(), f3.V.double(), f2.V.double(), f2.Q.double()
Qr, _ = torch.linalg.qr(torch.randn(dH, dH, generator=torch.Generator().manual_seed(7)).double()); Rb = Qr[:, : i3["d"]]
res["readout"] = {"layout_R2": {"full_embedding": audits.linear_r2(Etr[..., 0, :].reshape(-1, D), Ltr, Eva[..., 0, :].reshape(-1, D), Lva), "after_rung1_content": r2(I, Ltr, Lva),
                                "after_rung2_core": r2(Q2, Ltr, Lva), "after_rung3_core": r2(Q3, Ltr, Lva), "rung2_block": r2(V2, Ltr, Lva), "rung3_block": r2(V3, Ltr, Lva)},
                  "progress_R2": {"rung3_block": r2(V3, Ptr, Pva), "final_core": r2(Q3, Ptr, Pva), "rung2_block": r2(V2, Ptr, Pva), "random_block_same_size": r2(Rb, Ptr, Pva), "content_after_rung1": r2(I, Ptr, Pva)}}
def cam_acc(B, Xtr_, Xva_):
    xa = torch.cat([Xtr_[..., 0, :].reshape(-1, D), Xtr_[..., 1, :].reshape(-1, D)]) @ B; ya = torch.cat([-torch.ones(len(xa) // 2), torch.ones(len(xa) // 2)]).double()
    w = audits.ridge_fit(xa, ya[:, None]); xb = torch.cat([Xva_[..., 0, :].reshape(-1, D), Xva_[..., 1, :].reshape(-1, D)]) @ B; yb = torch.cat([-torch.ones(len(xb) // 2), torch.ones(len(xb) // 2)]).double()
    return float(((torch.cat([xb, torch.ones(len(xb), 1, dtype=xb.dtype)], 1) @ w).squeeze(1).sign() == yb).float().mean())
res["readout"]["camera_acc"] = {"from_rung1_variant_block": cam_acc(V1, Etr, Eva), "from_content": cam_acc(Vinv, Etr, Eva)}
res["readout"]["progress_gain_block_minus_core"] = res["readout"]["progress_R2"]["rung3_block"] - res["readout"]["progress_R2"]["final_core"]
json.dump(res, open(out, "w"), indent=1); print(json.dumps(res, indent=1))
