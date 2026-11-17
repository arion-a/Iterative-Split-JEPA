"""E66 evaluation (registered in docs/EVIDENCE.md), on the encoder's own seed-0 held-out trajectories.
(A) direct readouts from the trained heads [z_S, z_P, z_L]; (B) the iterated splitting on the new embedding.
    PYTHONPATH=src python e66_analyse.py TASK FEAT_DIR STATE_DIR D_S D_P D_L OUT_JSON"""
import sys, glob, json, numpy as np, torch
from isj import audits
from isj.engine import fit_rung, fit_whitener, select_block_count
task, feat, st, dS, dP, dL, out = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
fs = sorted(glob.glob(f"{feat}/group_*.npy")); E = torch.from_numpy(np.stack([np.load(f) for f in fs])).double()
S = torch.from_numpy(np.stack([np.load(f"{st}/{f.split('/')[-1][:-4]}.npz")["state"] for f in fs])).double(); G, T, K, _, D = E.shape; assert D == dS + dP + dL
g = torch.Generator().manual_seed(0); perm = torch.stack([torch.randperm(T, generator=g) for _ in range(G)]); nv = 2
take = lambda X, idx: torch.stack([X[i, idx[i]] for i in range(G)]); Etr, Eva = take(E, perm[:, nv:]), take(E, perm[:, :nv]); Str, Sva = take(S, perm[:, nv:]), take(S, perm[:, :nv]); nt = Etr.shape[1]
lay = lambda S_: torch.cat([S_[:, :, 0, 3:5].unsqueeze(2).expand(-1, -1, K, -1), S_[:, :, :, 6:9]], 3).reshape(-1, 5)
Ltr, Lva = lay(Str), lay(Sva); prog = lambda n: torch.linspace(0, 1, K).view(1, 1, K).expand(G, n, K).reshape(-1, 1).double(); Ptr, Pva = prog(nt), prog(nv)
res = {"task": task, "dims": [dS, dP, dL]}
# ---------- (A) direct readouts, camera 0 for progress and layout
cols = {"z_S": slice(0, dS), "z_P": slice(dS, dS + dP), "z_L": slice(dS + dP, D), "z_SP": slice(0, dS + dP)}
c0tr, c0va = Etr[..., 0, :].reshape(-1, D), Eva[..., 0, :].reshape(-1, D)
mlp = lambda x, xv, y, yv: audits.mlp_r2(x[::3].float(), y[::3].float(), xv.float(), yv.float(), hidden=128, steps=1500)
res["direct"] = {"progress_R2_mlp": {k: mlp(c0tr[:, s], c0va[:, s], Ptr, Pva) for k, s in cols.items()}, "layout_R2_linear": {k: audits.linear_r2(c0tr[:, s], Ltr, c0va[:, s], Lva) for k, s in cols.items()}}
def cam_acc(s):
    a = torch.cat([Etr[..., 0, s].reshape(-1, Etr[..., 0, s].shape[-1]), Etr[..., 1, s].reshape(-1, Etr[..., 0, s].shape[-1])]); y = torch.cat([-torch.ones(len(a) // 2), torch.ones(len(a) // 2)]).double()
    w = audits.ridge_fit(a, y[:, None]); b = torch.cat([Eva[..., 0, s].reshape(-1, a.shape[1]), Eva[..., 1, s].reshape(-1, a.shape[1])]); yb = torch.cat([-torch.ones(len(b) // 2), torch.ones(len(b) // 2)]).double()
    return float(((torch.cat([b, torch.ones(len(b), 1, dtype=b.dtype)], 1) @ w).squeeze(1).sign() == yb).float().mean())
res["direct"]["camera_acc"] = {k: cam_acc(s) for k, s in cols.items()}
d = res["direct"]; res["direct"]["progress_dissociation"] = d["progress_R2_mlp"]["z_P"] - d["progress_R2_mlp"]["z_S"]; res["direct"]["layout_dissociation"] = d["layout_R2_linear"]["z_S"] - d["layout_R2_linear"]["z_P"]
# ---------- (B) the ladder on the new embedding (E65 pipeline, seed 0)
dH = dS + dP
def rule2(ru, rv, h):
    pr = fit_rung(ru, rv, h, k=2, d_k=1); vals = pr.eigvals.double(); dd = select_block_count(vals, .1 * float(vals[0]))
    if dd == 0: dd = int(torch.argmax(vals[:32] / vals[1:33].clamp_min(1e-12))) + 1
    return fit_rung(ru, rv, h, k=2, d_k=dd), dd
a, b = Etr[..., 0, :].reshape(-1, D), Etr[..., 1, :].reshape(-1, D); lam, V = torch.linalg.eigh((a - b).T @ (a - b) / len(a)); Vinv = V[:, :dH]; res["ladder"] = {"rung1_eig_ratio_at_cut": float(lam[dH] / lam[dH - 1])}
mu = Etr.reshape(-1, D).mean(0); cont = lambda X: (X - mu) @ Vinv; wh = fit_whitener(cont(Etr.reshape(-1, D)).float(), 1e-5)
R = lambda X: wh(cont(X.reshape(-1, D)).float()).double().reshape(*X.shape[:-1], dH); c0t, c0v = R(Etr)[..., 0, :], R(Eva)[..., 0, :]
ia, ib = torch.triu_indices(nt, nt, offset=1); u2, v2 = c0t[:, ia].reshape(-1, dH), c0t[:, ib].reshape(-1, dH); sw = torch.rand(len(u2), generator=torch.Generator().manual_seed(2)) < .5; u2, v2 = torch.where(sw[:, None], v2, u2), torch.where(sw[:, None], u2, v2)
f2, d2 = rule2(u2, v2, torch.eye(dH)); H2 = f2.Q.double(); m2 = H2.shape[1]; xt, xv = c0t.reshape(-1, dH), c0v.reshape(-1, dH)
gp = torch.Generator().manual_seed(9); k1 = torch.randint(0, K, (G, nt, 40), generator=gp); k2 = (k1 + torch.randint(10, K - 9, (G, nt, 40), generator=gp)) % K
gi = torch.arange(G)[:, None, None].expand_as(k1); ti = torch.arange(nt)[None, :, None].expand_as(k1); u3, v3 = c0t[gi, ti, k1].reshape(-1, dH), c0t[gi, ti, k2].reshape(-1, dH)
pr = fit_rung(u3, v3, H2, k=3, d_k=1); e = pr.eigvals.double(); cs = e.cumsum(0) / e.sum(); d95 = int((cs < .95).sum()) + 1; f3 = fit_rung(u3, v3, H2, k=3, d_k=d95); Vb, Qc = f3.V.double(), f3.Q.double()
rm = lambda B_, Y, Yv: audits.mlp_r2((xt @ B_)[::3].float(), Y[::3].float(), (xv @ B_).float(), Yv.float(), hidden=128, steps=1500)
rl = lambda B_, Y, Yv: audits.linear_r2(xt @ B_, Y, xv @ B_, Yv)
dyn = lambda S_: (lambda X: (X - X.mean(2, keepdim=True)).reshape(-1, 6))(torch.cat([S_[:, :, :, 0:3], S_[:, :, :, 3:6]], 3)); Dtr, Dva = dyn(Str), dyn(Sva); dm, ds = Dtr.mean(0), Dtr.std(0); Dtr, Dva = (Dtr - dm) / ds, (Dva - dm) / ds
L = res["ladder"]; L.update({"rung2_d": d2, "content_after_rung2": m2, "d95": d95, "gap_ratio_at_d95": float(e[d95 - 1] / e[d95].clamp_min(1e-12)) if d95 < len(e) else None,
     "progress_R2_mlp": {"block": rm(Vb, Ptr, Pva), "core": rm(Qc, Ptr, Pva)}, "layout_R2_linear": {"block": rl(Vb, Ltr, Lva), "core": rl(Qc, Ltr, Lva)}, "dynamic_dev_R2_mlp": {"block": rm(Vb, Dtr, Dva), "core": rm(Qc, Dtr, Dva)}})
L["progress_separation"] = L["progress_R2_mlp"]["block"] - L["progress_R2_mlp"]["core"]; L["static_separation"] = L["layout_R2_linear"]["core"] - L["layout_R2_linear"]["block"]
json.dump(res, open(out, "w"), indent=1); print(json.dumps(res, indent=1))
