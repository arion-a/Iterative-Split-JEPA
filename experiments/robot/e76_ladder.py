"""E76 analysis (registered in docs/EVIDENCE.md): the iterated splitting (rungs 1 to 3) on a stored embedding of the robot frames, with the Stage C / E60 pairs and read-outs.
    PYTHONPATH=src python e76_ladder.py EMB_NPY DATA_DIR OUT_JSON        EMB_NPY (G, 8, 30, 2, D) from train_jepa_robot.py; DATA_DIR = data/robot/PickCube (state arrays)
rung 1 = viewpoint pairs (base vs side camera, same frame), rung 2 = trajectory pairs (same group, same progress, same camera), rung 3 = progress pairs (same trajectory, same camera, >= 3 steps apart);
whitening fitted on the train frames; block sizes by the absolute-gap rule gamma = 0.1 lambda_1 (fallback: largest ratio, flagged). Same seed-0 split as run_stage_c.py."""
import sys, glob, json, numpy as np, torch
from isj import audits
from isj.engine import fit_rung, fit_whitener, select_block_count
emb, ddir, out = sys.argv[1], sys.argv[2], sys.argv[3]; torch.set_num_threads(4)
E = torch.from_numpy(np.load(emb)).double(); files = sorted(glob.glob(f"{ddir}/group_*.npz")); S = torch.from_numpy(np.stack([np.load(f)["state"] for f in files])).double()
G, TT, K, _, D = E.shape; n_val = max(1, round(0.2 * TT)); g0 = torch.Generator().manual_seed(0)
perm = torch.stack([torch.randperm(TT, generator=g0) for _ in range(G)]); take = lambda X, idx: torch.stack([X[i, idx[i]] for i in range(G)])
Etr, Eva, Str, Sva = take(E, perm[:, n_val:]), take(E, perm[:, :n_val]), take(S, perm[:, n_val:]), take(S, perm[:, :n_val]); nt = Etr.shape[1]
wh = fit_whitener(Etr.reshape(-1, D).float(), 1e-5); R_tr, R_va = wh(Etr.reshape(-1, D).float()).double().reshape(Etr.shape), wh(Eva.reshape(-1, D).float()).double().reshape(Eva.shape)
def swap(ru, rv, seed):
    m = torch.rand(len(ru), generator=torch.Generator().manual_seed(seed)) < 0.5; return torch.where(m[:, None], rv, ru), torch.where(m[:, None], ru, rv)
def fit_rule(ru, rv, h_prev, k):
    probe = fit_rung(ru, rv, h_prev, k=k, d_k=1); vals = probe.eigvals.double(); d = select_block_count(vals, 0.1 * float(vals[0])); fb = False
    if d == 0: d = int(torch.argmax(vals[:32] / vals[1:33].clamp_min(1e-12))) + 1; fb = True
    f = fit_rung(ru, rv, h_prev, k=k, d_k=d); return f, {"d": d, "gap_ratio": f.gap_ratio, "no_cliff_fallback": fb, "top_eigvals": [float(x) for x in f.eigvals[:8]]}
u1, v1 = swap(R_tr[..., 0, :].reshape(-1, D), R_tr[..., 1, :].reshape(-1, D), 1); f1, i1 = fit_rule(u1, v1, torch.eye(D, dtype=torch.double), 1)
ia, ib = torch.triu_indices(nt, nt, offset=1); u2, v2 = swap(R_tr[:, ia, :, 0].reshape(-1, D), R_tr[:, ib, :, 0].reshape(-1, D), 2); f2, i2 = fit_rule(u2, v2, f1.Q, 2)
gp = torch.Generator().manual_seed(9); npair = 40; k1 = torch.randint(0, K, (G, nt, npair), generator=gp); k2 = (k1 + torch.randint(3, K - 2, (G, nt, npair), generator=gp)) % K
gi = torch.arange(G)[:, None, None].expand_as(k1); ti = torch.arange(nt)[None, :, None].expand_as(k1)
u3, v3 = swap(R_tr[gi, ti, k1, 0].reshape(-1, D), R_tr[gi, ti, k2, 0].reshape(-1, D), 3); f3, i3 = fit_rule(u3, v3, f2.Q, 3)
V1, Q1, V2, Q2, V3, Q3 = f1.V.double(), f1.Q.double(), f2.V.double(), f2.Q.double(), f3.V.double(), f3.Q.double()
def resp(B, u, v):
    bu, bv = u @ B, v @ B; allb = torch.cat([bu, bv]); rms = (allb - allb.mean(0)).square().sum(1).mean().sqrt(); return float((bu - bv).square().sum(1).mean().sqrt() / (2 ** 0.5 * rms))
vu, vv = R_va[..., 0, :].reshape(-1, D), R_va[..., 1, :].reshape(-1, D)
def acc_cam(B):
    xa = torch.cat([R_tr[..., 0, :].reshape(-1, D), R_tr[..., 1, :].reshape(-1, D)]) @ B; ya = torch.cat([-torch.ones(len(xa) // 2), torch.ones(len(xa) // 2)]).double()
    w = audits.ridge_fit(xa, ya[:, None]); xb = torch.cat([vu, vv]) @ B; yb = torch.cat([-torch.ones(len(xb) // 2), torch.ones(len(xb) // 2)]).double()
    return float(((torch.cat([xb, torch.ones(len(xb), 1, dtype=xb.dtype)], 1) @ w).squeeze(1).sign() == yb).float().mean())
lay = lambda S_: torch.cat([S_[:, :, 0, 3:5].unsqueeze(2).expand(-1, -1, K, -1), S_[:, :, :, 6:9]], 3).reshape(-1, 5)
prog = lambda S_: torch.linspace(0, 1, K).view(1, 1, K).expand(S_.shape[0], S_.shape[1], K).reshape(-1, 1).double()
xt, xv = R_tr[..., 0, :].reshape(-1, D), R_va[..., 0, :].reshape(-1, D); r2 = lambda B, ytr, yva: audits.linear_r2(xt @ B, ytr, xv @ B, yva)
res = {"D": D, "groups": G, "rung1": i1, "rung2": i2, "rung3": i3,
       "response_view": {"V1": resp(V1, vu, vv), "Q1": resp(Q1, vu, vv)}, "camera_acc": {"from_V1": acc_cam(V1), "from_Q1": acc_cam(Q1)},
       "layout_R2": {"full": r2(torch.eye(D, dtype=torch.double), lay(Str), lay(Sva)), "core_Q2": r2(Q2, lay(Str), lay(Sva)), "core_Q3": r2(Q3, lay(Str), lay(Sva)), "V1": r2(V1, lay(Str), lay(Sva)), "V2": r2(V2, lay(Str), lay(Sva))},
       "progress_R2": {"V3": r2(V3, prog(Str), prog(Sva)), "core_Q3": r2(Q3, prog(Str), prog(Sva)), "V2": r2(V2, prog(Str), prog(Sva)), "full": r2(torch.eye(D, dtype=torch.double), prog(Str), prog(Sva))}}
res["viewpoint_ratio_V1_over_Q1"] = res["response_view"]["V1"] / res["response_view"]["Q1"]
json.dump(res, open(out, "w"), indent=1); print(json.dumps({k: res[k] for k in ("rung1", "rung2", "rung3", "camera_acc", "viewpoint_ratio_V1_over_Q1", "layout_R2", "progress_R2")}, indent=1, default=float)[:2500])
