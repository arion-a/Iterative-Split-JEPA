"""E63 (registered in docs/EVIDENCE.md): robot rung 3 with the block size at the spectrum's cliff, an MLP progress readout, two lag settings, three split seeds.
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
for seed in (0, 1, 2):
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
    for minlag in (3, 10):
        gp = torch.Generator().manual_seed(9); k1 = torch.randint(0, K, (G, nt, 40), generator=gp); k2 = (k1 + torch.randint(minlag, K - minlag + 1, (G, nt, 40), generator=gp)) % K
        gi = torch.arange(G)[:, None, None].expand_as(k1); ti = torch.arange(nt)[None, :, None].expand_as(k1); u3, v3 = c0tr[gi, ti, k1].reshape(-1, dH), c0tr[gi, ti, k2].reshape(-1, dH)
        pr = fit_rung(u3, v3, H2, k=3, d_k=1); e = pr.eigvals.double(); ratio = e[:-1] / e[1:].clamp_min(1e-12); dstar = int(torch.argmax(ratio)) + 1
        f3 = fit_rung(u3, v3, H2, k=3, d_k=dstar); sh = fit_rung(u3, v3[torch.randperm(len(v3), generator=torch.Generator().manual_seed(3))], H2, k=3, d_k=dstar)
        Vb, Qc = f3.V.double(), f3.Q.double(); Qr, _ = torch.linalg.qr(torch.randn(m2, dstar, generator=torch.Generator().manual_seed(7)).double()); Rb = H2 @ Qr
        def rd(B_):
            lin = audits.linear_r2(xt @ B_, Ptr, xv @ B_, Pva); mlp = audits.mlp_r2((xt @ B_)[::3].float(), Ptr[::3].float(), (xv @ B_).float(), Pva.float(), hidden=128, steps=1500)
            return {"linear": lin, "mlp": mlp}
        run = {"seed": seed, "min_lag": minlag, "rung2_d": d2, "content_after_rung2": m2, "d_star": dstar, "gap_at_d_star": float(ratio[dstar - 1]), "gap_registered_rule_d1": float(ratio[0]), "shuffled_gap_at_d_star": float(sh.gap_ratio),
               "top_ratios": [(int(i) + 1, round(float(ratio[i]), 2)) for i in torch.argsort(ratio, descending=True)[:3]], "progress_R2": {"block": rd(Vb), "core": rd(Qc) if Qc.shape[1] > 0 else None, "random_block_same_size": rd(Rb)},
               "layout_R2_linear_from_core": audits.linear_r2(xt @ Qc, Ltr, xv @ Qc, Lva) if Qc.shape[1] > 0 else None}
        res["runs"].append(run); print(task, seed, minlag, "d*", dstar, "gap", round(run["gap_at_d_star"], 2), "prog mlp block/core/rand", round(run["progress_R2"]["block"]["mlp"], 2), round(run["progress_R2"]["core"]["mlp"], 2) if run["progress_R2"]["core"] else None, round(run["progress_R2"]["random_block_same_size"]["mlp"], 2), "layout core", None if run["layout_R2_linear_from_core"] is None else round(run["layout_R2_linear_from_core"], 2), flush=True)
json.dump(res, open(out, "w"), indent=1)
