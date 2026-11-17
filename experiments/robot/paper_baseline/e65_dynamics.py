"""E65 (registered in docs/EVIDENCE.md): as E64 with the dynamic label = state minus its trajectory mean; split seeds 6, 7, 8.
    PYTHONPATH=src python e63_rung3.py TASK FEAT_DIR STATE_DIR D_H OUT_JSON"""
import sys, glob, json, numpy as np, torch
from isj import audits
from isj.engine import fit_rung, fit_whitener, select_block_count
task, feat, st, dH, out = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
fs = sorted(glob.glob(f"{feat}/group_*.npy")); E = torch.from_numpy(np.stack([np.load(f) for f in fs])).double()
S = torch.from_numpy(np.stack([np.load(f"{st}/{f.split('/')[-1][:-4]}.npz")["state"] for f in fs])).double(); G, T, K, _, D = E.shape
def rule2(ru, rv, h):                                                         # the E60 rule for rung 2 (unchanged)
    pr = fit_rung(ru, rv, h, k=2, d_k=1); vals = pr.eigvals.double(); d = select_block_count(vals, .1 * float(vals[0]))
    if d == 0: d = int(torch.argmax(vals[:32] / vals[1:33].clamp_min(1e-12))) + 1
    return fit_rung(ru, rv, h, k=2, d_k=d), d
res = {"task": task, "D": D, "d_H": dH, "runs": []}
for seed in (6, 7, 8):
    g = torch.Generator().manual_seed(seed); perm = torch.stack([torch.randperm(T, generator=g) for _ in range(G)]); nv = 2
    take = lambda X, idx: torch.stack([X[i, idx[i]] for i in range(G)]); Etr, Eva = take(E, perm[:, nv:]), take(E, perm[:, :nv]); Str, Sva = take(S, perm[:, nv:]), take(S, perm[:, :nv]); nt = Etr.shape[1]
    a, b = Etr[..., 0, :].reshape(-1, D), Etr[..., 1, :].reshape(-1, D); lam, V = torch.linalg.eigh((a - b).T @ (a - b) / len(a)); Vinv = V[:, :dH]
    mu = Etr.reshape(-1, D).mean(0); cont = lambda X: (X - mu) @ Vinv; wh = fit_whitener(cont(Etr.reshape(-1, D)).float(), 1e-5)
    R = lambda X: wh(cont(X.reshape(-1, D)).float()).double().reshape(*X.shape[:-1], dH); c0tr, c0va = R(Etr)[..., 0, :], R(Eva)[..., 0, :]
    ia, ib = torch.triu_indices(nt, nt, offset=1); u2, v2 = c0tr[:, ia].reshape(-1, dH), c0tr[:, ib].reshape(-1, dH); sw = torch.rand(len(u2), generator=torch.Generator().manual_seed(2)) < .5; u2, v2 = torch.where(sw[:, None], v2, u2), torch.where(sw[:, None], u2, v2)
    f2, d2 = rule2(u2, v2, torch.eye(dH)); H2 = f2.Q.double(); m2 = H2.shape[1]
    lay = lambda S_: torch.cat([S_[:, :, 0, 3:5].unsqueeze(2).expand(-1, -1, K, -1), S_[:, :, :, 6:9]], 3).reshape(-1, 5)
    Ltr, Lva = lay(Str), lay(Sva); prog = lambda n: torch.linspace(0, 1, K).view(1, 1, K).expand(G, n, K).reshape(-1, 1).double(); Ptr, Pva = prog(nt), prog(nv)
    xt, xv = c0tr.reshape(-1, dH), c0va.reshape(-1, dH)
    dyn = lambda S_: (lambda X: (X - X.mean(2, keepdim=True)).reshape(-1, 6))(torch.cat([S_[:, :, :, 0:3], S_[:, :, :, 3:6]], 3)); Dtr, Dva = dyn(Str), dyn(Sva); dm, ds = Dtr.mean(0), Dtr.std(0); Dtr, Dva = (Dtr - dm) / ds, (Dva - dm) / ds
    minlag = 10; gp = torch.Generator().manual_seed(9); k1 = torch.randint(0, K, (G, nt, 40), generator=gp); k2 = (k1 + torch.randint(minlag, K - minlag + 1, (G, nt, 40), generator=gp)) % K
    gi = torch.arange(G)[:, None, None].expand_as(k1); ti = torch.arange(nt)[None, :, None].expand_as(k1); u3, v3 = c0tr[gi, ti, k1].reshape(-1, dH), c0tr[gi, ti, k2].reshape(-1, dH)
    pr = fit_rung(u3, v3, H2, k=3, d_k=1); e = pr.eigvals.double(); cs = e.cumsum(0) / e.sum(); d95 = int((cs < .95).sum()) + 1
    f3 = fit_rung(u3, v3, H2, k=3, d_k=d95); Vb, Qc = f3.V.double(), f3.Q.double()
    Qr, _ = torch.linalg.qr(torch.randn(m2, m2, generator=torch.Generator().manual_seed(7)).double()); Rb, Rc = H2 @ Qr[:, :d95], H2 @ Qr[:, d95:]
    mlp = lambda B_, Y_tr, Y_va: audits.mlp_r2((xt @ B_)[::3].float(), Y_tr[::3].float(), (xv @ B_).float(), Y_va.float(), hidden=128, steps=1500)
    lin = lambda B_, Y_tr, Y_va: audits.linear_r2(xt @ B_, Y_tr, xv @ B_, Y_va)
    run = {"seed": seed, "rung2_d": d2, "content_after_rung2": m2, "d95": d95, "gap_ratio_at_d95": float(e[d95 - 1] / e[d95].clamp_min(1e-12)) if d95 < len(e) else None,
           "dynamic_R2_mlp": {"block": mlp(Vb, Dtr, Dva), "core": mlp(Qc, Dtr, Dva), "random_block": mlp(Rb, Dtr, Dva), "random_rest": mlp(Rc, Dtr, Dva)},
           "layout_R2_linear": {"block": lin(Vb, Ltr, Lva), "core": lin(Qc, Ltr, Lva), "random_block": lin(Rb, Ltr, Lva), "random_rest": lin(Rc, Ltr, Lva)},
           "progress_R2_mlp": {"block": audits.mlp_r2((xt @ Vb)[::3].float(), Ptr[::3].float(), (xv @ Vb).float(), Pva.float(), hidden=128, steps=1500), "core": audits.mlp_r2((xt @ Qc)[::3].float(), Ptr[::3].float(), (xv @ Qc).float(), Pva.float(), hidden=128, steps=1500)}}
    run["dynamic_separation"] = run["dynamic_R2_mlp"]["block"] - run["dynamic_R2_mlp"]["core"]; run["static_separation"] = run["layout_R2_linear"]["core"] - run["layout_R2_linear"]["block"]
    run["control_dynamic_sep"] = run["dynamic_R2_mlp"]["random_block"] - run["dynamic_R2_mlp"]["random_rest"]; run["control_static_sep"] = run["layout_R2_linear"]["random_rest"] - run["layout_R2_linear"]["random_block"]
    res["runs"].append(run); print(task, seed, "d95", d95, "of", m2, "dyn sep", round(run["dynamic_separation"], 2), "static sep", round(run["static_separation"], 2), "| control", round(run["control_dynamic_sep"], 2), round(run["control_static_sep"], 2), "| layout core/block", round(run["layout_R2_linear"]["core"], 2), round(run["layout_R2_linear"]["block"], 2), flush=True)
json.dump(res, open(out, "w"), indent=1)
