"""Unregistered diagnostic: why does the progress rung (rung 3) fail on PickCube but work on PushCube (E60)?
    PYTHONPATH=src python diag_progress.py TASK FEAT_DIR STATE_DIR D_H OUT_JSON"""
import sys, glob, json, numpy as np, torch
from isj import audits
from isj.engine import fit_rung, fit_whitener
task, feat, st, dH, out = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
fs = sorted(glob.glob(f"{feat}/group_*.npy")); E = torch.from_numpy(np.stack([np.load(f) for f in fs])).double()
G, T, K, _, D = E.shape; g = torch.Generator().manual_seed(0); perm = torch.stack([torch.randperm(T, generator=g) for _ in range(G)]); nv = max(1, round(0.2 * T))
take = lambda X, idx: torch.stack([X[i, idx[i]] for i in range(G)]); Etr, Eva = take(E, perm[:, nv:]), take(E, perm[:, :nv]); nt = Etr.shape[1]
a, b = Etr[..., 0, :].reshape(-1, D), Etr[..., 1, :].reshape(-1, D); lam, V = torch.linalg.eigh((a - b).T @ (a - b) / len(a)); Vinv = V[:, :dH]
mu = Etr.reshape(-1, D).mean(0); cont = lambda X: (X - mu) @ Vinv; wh = fit_whitener(cont(Etr.reshape(-1, D)).float(), 1e-5)
R = lambda X: wh(cont(X.reshape(-1, D)).float()).double().reshape(*X.shape[:-1], dH); Rtr, Rva = R(Etr)[..., 0, :], R(Eva)[..., 0, :]        # (G,n,K,dH), camera 0
res = {"task": task, "d_H": dH}
# 1) is progress carried linearly? linear vs nonlinear readout from the whole content (held-out R2)
prog = torch.linspace(0, 1, K).view(1, 1, K).expand(G, nt, K).reshape(-1, 1).double(); progv = torch.linspace(0, 1, K).view(1, 1, K).expand(G, Rva.shape[1], K).reshape(-1, 1).double()
xt, xv = Rtr.reshape(-1, dH), Rva.reshape(-1, dH)
res["progress_R2_linear_full_content"] = audits.linear_r2(xt, prog, xv, progv)
res["progress_R2_mlp_full_content"] = audits.mlp_r2(xt[::3].float(), prog[::3].float(), xv.float(), progv.float(), hidden=128, steps=1500)
# 2) the progress curve: mean content per progress step (across all trajectories), how many directions does it need?
curve = Rtr.mean((0, 1)); cc = curve - curve.mean(0); sv = torch.linalg.svdvals(cc).square(); ex = (sv / sv.sum()).cumsum(0)
res["curve_dims_for_90pct"] = int((ex < .9).sum()) + 1; res["curve_dims_for_99pct"] = int((ex < .99).sum()) + 1; res["curve_first3_share"] = [float(x) for x in (sv / sv.sum())[:3]]
# progress variance vs trajectory/layout variance in the content (how much of the content's spread is progress?)
tot = xt.var(0).sum(); res["share_of_content_variance_that_is_progress_curve"] = float(cc.var(0).sum() / tot)
# 3) progress pairs (same trajectory, >=3 steps apart): spectrum of the difference moment in the content and in what rung 2 leaves
gp = torch.Generator().manual_seed(9); npair = 40; k1 = torch.randint(0, K, (G, nt, npair), generator=gp); k2 = (k1 + torch.randint(3, K - 2, (G, nt, npair), generator=gp)) % K
gi = torch.arange(G)[:, None, None].expand_as(k1); ti = torch.arange(nt)[None, :, None].expand_as(k1); u3, v3 = Rtr[gi, ti, k1].reshape(-1, dH), Rtr[gi, ti, k2].reshape(-1, dH)
M3 = (u3 - v3).T @ (u3 - v3) / len(u3); l3 = torch.linalg.eigvalsh(M3).flip(0); res["progress_pair_eig_top8"] = [float(x) for x in l3[:8]]; res["progress_pair_energy_top_d"] = {d: float(l3[:d].sum() / l3.sum()) for d in (1, 2, 4, 8, 16, 32)}
res["progress_pair_effective_rank"] = float(torch.exp(-(l3 / l3.sum() * (l3 / l3.sum()).clamp_min(1e-12).log()).sum()))
# 4) the readout the ladder cares about: progress R2 from the top-d eigen-block of progress pairs (no rung 2 removal), several d
_, vv = torch.linalg.eigh(M3); vv = vv.flip(1); res["progress_R2_from_topd_block"] = {d: audits.linear_r2(xt @ vv[:, :d], prog, xv @ vv[:, :d], progv) for d in (1, 2, 4, 8, 16, 32, 64) if d <= dH}
# 5) trajectory/layout contamination: variance of the progress-pair differences along directions that also separate trajectories (rung-2 pairs)
ia, ib = torch.triu_indices(nt, nt, offset=1); u2, v2 = Rtr[:, ia].reshape(-1, dH), Rtr[:, ib].reshape(-1, dH); M2 = (u2 - v2).T @ (u2 - v2) / len(u2); l2, V2 = torch.linalg.eigh(M2); V2 = V2.flip(1)
res["overlap_progress_top8_with_trajectory_top8"] = float((vv[:, :8].T @ V2[:, :8]).square().sum() / 8)
json.dump(res, open(out, "w"), indent=1); print(json.dumps(res, indent=1))
