"""Stage C: the iterated spectral ladder on frozen ResNet-50 features of ManiSkill3 robot frames (design: docs/stage_c_design.md; prediction: E24).
    python experiments/robot/run_stage_c.py --task PickCube --split-seed 0 --out results/stage_c
Rung 1 = viewpoint pairs (base vs side camera, same state); rung 2 = trajectory pairs (same group, same progress, same camera), inside the rung-1 invariant content.
Block sizes by the engine's absolute-gap rule with gamma = 0.1 x lambda_1 (as in Stage A). Ground truth (camera id, layout, progress) is used for evaluation only."""
import argparse, glob, json, os, time
import numpy as np, torch
from isj import audits
from isj.engine import fit_rung, fit_whitener, select_block_count

ap = argparse.ArgumentParser()
ap.add_argument("--task", required=True); ap.add_argument("--split-seed", type=int, default=0); ap.add_argument("--out", default="results/stage_c")
ap.add_argument("--data", default="data/robot"); ap.add_argument("--pca", type=int, default=128); ap.add_argument("--max-groups", type=int, default=None)
ap.add_argument("--encoder", choices=["pca", "head"], default="head", help="pca = frozen features only; head = JEPA-trained MLP head on the frozen features (E24 main arm)")
ap.add_argument("--fixed-d1", type=int, default=None, help="paper Appendix D: fix the rung-1 variant block to d_H dims (use --pca 2*d_H) instead of the gap rule; off by default")
ap.add_argument("--head-steps", type=int, default=4000); ap.add_argument("--head-hidden", type=int, default=512)
a = ap.parse_args()
t0 = time.time(); torch.manual_seed(a.split_seed)

files = sorted(glob.glob(f"{a.data}/feat/{a.task}/group_*.npy"))
if a.max_groups: files = files[: a.max_groups]
F = torch.from_numpy(np.stack([np.load(f).astype(np.float32) for f in files]))                       # (G, 8, K, 2, 2048)
S = torch.from_numpy(np.stack([np.load(f.replace("/feat/", "/").replace(".npy", ".npz"))["state"] for f in files]).astype(np.float32))   # (G, 8, K, 9)
G, T, K = F.shape[:3]; n_val = max(1, round(0.2 * T))
g = torch.Generator().manual_seed(a.split_seed)
perm = torch.stack([torch.randperm(T, generator=g) for _ in range(G)]); val_idx, tr_idx = perm[:, :n_val], perm[:, n_val:]
take = lambda X, idx: torch.stack([X[i, idx[i]] for i in range(G)])
Ftr, Fva = take(F, tr_idx), take(F, val_idx); Str, Sva = take(S, tr_idx), take(S, val_idx)
# ---- representation: either PCA of the frozen features, or a JEPA-trained MLP head on them (adjacent-frame prediction + variance/covariance regulariser; Stage A recipe; no viewpoint-invariance training)
flat = Ftr.reshape(-1, F.shape[-1]).double(); mu = flat.mean(0)
if a.encoder == "pca":
    cov = (flat - mu).T @ (flat - mu) / (len(flat) - 1); ev, evec = torch.linalg.eigh(cov); U = evec[:, -a.pca:].flip(1)
    proj = lambda X: ((X.double() - mu) @ U).float(); head_log = None
else:
    from isj.encoder import mlp, variance_hinge, covariance_penalty
    sd = flat.std(0).clamp_min(1e-6); stdz = lambda X: ((X.double() - mu) / sd).float()
    enc = mlp(F.shape[-1], a.head_hidden, a.pca); pred = mlp(a.pca, a.pca, a.pca)
    opt = torch.optim.AdamW(list(enc.parameters()) + list(pred.parameters()), lr=1e-3, weight_decay=1e-4)
    Xtr = stdz(Ftr)                                                    # (G, nt, K, 2, 2048)
    gi = torch.Generator().manual_seed(100 + a.split_seed); head_log = []
    for step in range(a.head_steps):
        gg = torch.randint(0, G, (512,), generator=gi); tt = torch.randint(0, Xtr.shape[1], (512,), generator=gi)
        kk = torch.randint(0, K - 1, (512,), generator=gi); cc = torch.randint(0, 2, (512,), generator=gi)          # same camera, adjacent frames
        h0, h1 = enc(Xtr[gg, tt, kk, cc]), enc(Xtr[gg, tt, kk + 1, cc])
        l_pred = (pred(h0) - h1.detach()).square().mean(); h = torch.cat([h0, h1])
        loss = l_pred + 1e-2 * variance_hinge(h) + 0.04 * covariance_penalty(h)
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0 or step == a.head_steps - 1: head_log.append({"step": step, "pred": float(l_pred), "min_std": float(h.std(0).min())})
    enc.eval()
    proj = lambda X: enc(stdz(X)).detach()
Ztr, Zva = proj(Ftr), proj(Fva)
wh = fit_whitener(Ztr.reshape(-1, a.pca), 1e-5); R_tr, R_va = wh(Ztr.reshape(-1, a.pca)).reshape(Ztr.shape), wh(Zva.reshape(-1, a.pca)).reshape(Zva.shape)   # (G, nt, K, 2, D)
D = a.pca

def fit_two_pass(ru, rv, h_prev, k):
    if k == 1 and a.fixed_d1:
        fit = fit_rung(ru, rv, h_prev, k=k, d_k=a.fixed_d1)
        return fit, {"d": a.fixed_d1, "fixed": True, "no_cliff_fallback": False, "gap_ratio": fit.gap_ratio, "top_eigvals": [float(x) for x in fit.eigvals[:10]], "eigvals_full": [float(x) for x in fit.eigvals], "rank_monitor": audits.rank_monitor(fit)}
    """Engine rung with the block size chosen by the absolute-gap rule gamma = 0.1 lambda_1 (Stage A); falls back to the largest gap ratio (flagged) if no gap qualifies."""
    probe = fit_rung(ru, rv, h_prev, k=k, d_k=1); vals = probe.eigvals.double()
    d = select_block_count(vals, 0.1 * float(vals[0])); flagged = False
    if d == 0:
        d = int(torch.argmax(vals[:32] / vals[1:33].clamp_min(1e-12))) + 1; flagged = True
    fit = fit_rung(ru, rv, h_prev, k=k, d_k=d)
    return fit, {"d": d, "no_cliff_fallback": flagged, "gap_ratio": fit.gap_ratio, "top_eigvals": [float(x) for x in fit.eigvals[:10]], "eigvals_full": [float(x) for x in fit.eigvals], "rank_monitor": audits.rank_monitor(fit)}

def swap(ru, rv, seed):
    m = torch.rand(len(ru), generator=torch.Generator().manual_seed(seed)) < 0.5
    return torch.where(m[:, None], rv, ru), torch.where(m[:, None], ru, rv)

# ---- rung 1: viewpoint pairs (same frame, base vs side camera)
u1, v1 = swap(R_tr[..., 0, :].reshape(-1, D), R_tr[..., 1, :].reshape(-1, D), 1)
fit1, info1 = fit_two_pass(u1, v1, torch.eye(D), 1)
# ---- rung 2: trajectory pairs inside each group (all train trajectory pairs, same progress, same camera), in the rung-1 invariant content
ia, ib = torch.triu_indices(R_tr.shape[1], R_tr.shape[1], offset=1)
u2 = R_tr[:, ia].reshape(-1, D); v2 = R_tr[:, ib].reshape(-1, D); u2, v2 = swap(u2, v2, 2)
fit2, info2 = fit_two_pass(u2, v2, fit1.Q, 2)
V1, Q1, V2, Q2 = fit1.V, fit1.Q, fit2.V, fit2.Q

def resp(B, u, v):                 # normalized response of block B to pairs: 1 = as far apart as random frames, 0 = identical
    bu, bv = u @ B, v @ B; allb = torch.cat([bu, bv]); rms = (allb - allb.mean(0)).square().sum(1).mean().sqrt()
    return float((bu - bv).square().sum(1).mean().sqrt() / (2 ** 0.5 * rms))

view_u, view_v = R_va[..., 0, :].reshape(-1, D), R_va[..., 1, :].reshape(-1, D)                    # validation viewpoint pairs
tj_u, tj_v = R_va[:, 0].reshape(-1, D), R_va[:, 1].reshape(-1, D)                                   # validation trajectory pairs (the held-out pair of each group)
VL = torch.cat([V1, V2], 1)                                                                          # all variant directions
res = {"encoder": a.encoder, "head_log": head_log, "split_seed": a.split_seed, "task": a.task, "groups": G, "train_traj_per_group": int(tr_idx.shape[1]), "val_traj_per_group": int(n_val), "pca": D,
       "rung1": info1, "rung2": info2, "n_pairs": {"rung1": len(u1), "rung2": len(u2), "val_view": len(view_u), "val_traj": len(tj_u)}}
res["response"] = {"view": {"V1": resp(V1, view_u, view_v), "Q1": resp(Q1, view_u, view_v), "V2": resp(V2, view_u, view_v), "Q2": resp(Q2, view_u, view_v), "V1V2": resp(VL, view_u, view_v)},
                   "traj": {"V1": resp(V1, tj_u, tj_v), "Q1": resp(Q1, tj_u, tj_v), "V2": resp(V2, tj_u, tj_v), "Q2": resp(Q2, tj_u, tj_v), "V1V2": resp(VL, tj_u, tj_v)}}
rr = res["response"]
res["ratios"] = {"P1_view_V1_over_Q1": rr["view"]["V1"] / rr["view"]["Q1"], "P2_traj_V2_over_Q2": rr["traj"]["V2"] / rr["traj"]["Q2"],
                 "paper_analogue_view_(V1+V2)_over_Q2": rr["view"]["V1V2"] / rr["view"]["Q2"], "paper_analogue_traj_(V1+V2)_over_Q2": rr["traj"]["V1V2"] / rr["traj"]["Q2"]}
# ---- controls: random orthonormal splits of the same sizes; shuffled-pair rung 1
Qr, _ = torch.linalg.qr(torch.randn(D, D, generator=torch.Generator().manual_seed(7)))
r1, r2 = Qr[:, : info1["d"]], Qr[:, info1["d"]:]
rd = Qr[:, : info2["d"]]; rrest = Qr[:, info2["d"]: D - info1["d"]]
res["controls"] = {"random_split_view_ratio": resp(r1, view_u, view_v) / resp(r2, view_u, view_v), "random_split_traj_ratio": resp(rd, tj_u, tj_v) / resp(rrest, tj_u, tj_v)}
perm_idx = torch.randperm(len(u1), generator=torch.Generator().manual_seed(11))
shuf = fit_rung(u1, v1[perm_idx], torch.eye(D), k=1, d_k=1)
res["controls"]["shuffled_pairs_rung1"] = {"gap_ratio_at_d1": shuf.gap_ratio, "top_eigvals": [float(x) for x in shuf.eigvals[:5]], "d_by_gap_rule": select_block_count(shuf.eigvals.double(), 0.1 * float(shuf.eigvals[0]))}
# ---- probes (train -> validation); ground truth in the simulator, evaluation only
def acc_cam(B):
    xtr = torch.cat([R_tr[..., 0, :], R_tr[..., 1, :]]).reshape(-1, D) @ B; ytr = torch.cat([-torch.ones(R_tr[..., 0, :].reshape(-1, D).shape[0]), torch.ones(R_tr[..., 1, :].reshape(-1, D).shape[0])])
    xva = torch.cat([R_va[..., 0, :], R_va[..., 1, :]]).reshape(-1, D) @ B; yva = torch.cat([-torch.ones(view_u.shape[0]), torch.ones(view_v.shape[0])])
    w = audits.ridge_fit(xtr, ytr[:, None]); pred = (torch.cat([xva, torch.ones(len(xva), 1)], 1).double() @ w).squeeze(1)
    return float(((pred > 0).float() * 2 - 1 == yva).float().mean())
res["probes"] = {"camera_acc_from_V1": acc_cam(V1), "camera_acc_from_Q1": acc_cam(Q1)}
def r2_from(B, tgt_tr, tgt_va, cams_tr=0, cams_va=0):
    xtr = R_tr[..., 0, :].reshape(-1, D) @ B; xva = R_va[..., 0, :].reshape(-1, D) @ B
    return audits.linear_r2(xtr, tgt_tr, xva, tgt_va)
lay = lambda S_: torch.cat([S_[:, :, 0, 3:5].unsqueeze(2).expand(-1, -1, K, -1), S_[:, :, :, 6:9]], 3).reshape(-1, 5)        # initial cube xy + goal xyz
prog = lambda S_: torch.linspace(0, 1, K).view(1, 1, K).expand(S_.shape[0], S_.shape[1], K).reshape(-1, 1)
cur = lambda S_: S_[:, :, :, 3:6].reshape(-1, 3)                                                                                # current cube position
res["probes"].update({"layout_r2_from_core_Q2": r2_from(Q2, lay(Str), lay(Sva)), "layout_r2_from_V1": r2_from(V1, lay(Str), lay(Sva)), "layout_r2_from_V2": r2_from(V2, lay(Str), lay(Sva)),
                      "progress_r2_from_core_Q2": r2_from(Q2, prog(Str), prog(Sva)), "progress_r2_from_V2": r2_from(V2, prog(Str), prog(Sva)),
                      "cube_pos_r2_from_core_Q2": r2_from(Q2, cur(Str), cur(Sva)), "layout_r2_from_all_features": r2_from(torch.eye(D), lay(Str), lay(Sva))})
res["seconds"] = round(time.time() - t0, 1)
os.makedirs(f"{a.out}/{a.task}", exist_ok=True)
json.dump(res, open(f"{a.out}/{a.task}/split{a.split_seed}.json", "w"), indent=1)
print(json.dumps({k: res[k] for k in ("groups", "rung1", "rung2", "ratios", "controls", "probes")}, indent=1, default=float)[:3500])
