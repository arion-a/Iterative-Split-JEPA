"""Descriptive diagnostic (no pass/fail): what the NUS ladder's invariant core and variant block actually contain. One variant, seed 0:
python experiments/diag_nus.py S0|CL. Reuses the data and pipeline setup of run_nus_t.py. Writes results/nus_diag/<variant>.json."""
import json, sys
src = open("experiments/run_nus_t.py").read().split("res, qtest = {}, {}")[0]
exec(compile(src, "run_nus_t_setup", "exec"))                       # cfg, var, enc_cfg, lad, kept, vids, tr_v/va_v/te_v, v_tr/v_va/v_te, seg, ...
from scipy.stats import spearmanr
au = np.load("data/nus/audit.npz"); prox_all = {k: au[k][:, 1:] for k in ("height", "reach", "motion")}   # (93, 659), kept order
kept_idx = {v: i for i, v in enumerate(kept)}

# which training releases are the first 660-frame segment of a video (the only ones with image-derived proxies)
rel = [(v, 0) for v in tr_v]
if var["train"] == "half":
    rel = rel[::2]
elif var["train"] == "long":
    rel = [(v, j) for v in tr_v for j in range(len(vids[v]) // T)]
first_tr = [i for i, (v, j) in enumerate(rel) if j == 0]
rng_c = np.random.default_rng(0); c_tr = np.array([[rng_c.uniform(-cfg["nuisance_amp"], cfg["nuisance_amp"], 4) for _ in range(2)] for _ in rel])   # same draws as views_of(…, 0)
rng_c = np.random.default_rng(2); c_te = np.array([[rng_c.uniform(-cfg["nuisance_amp"], cfg["nuisance_amp"], 4) for _ in range(2)] for _ in te_v])

pipe = Pipeline(v_tr, {"encoder": enc_cfg}, 0)
zw = {k: pipe.whiten(pipe.latent(v)) for k, v in (("tr", v_tr), ("te", v_te))}
main = tl.run_ladder(zw["tr"], cfg["lag_sets"]["A"], lad["gamma_min"], lad["b2_quantile"], False, 0, s1_chance_fraction=lad["s1_chance_fraction"])
C = main["core"]; m = C.shape[1]
out = {"variant": name, "core_dim": int(m), "core_orthonormal_err": float(np.abs(C.T @ C - np.eye(m)).max()), "rungs": []}
for r in main["rungs"]:
    out["rungs"].append({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k in ("family", "content_dim", "d_k", "best_ratio", "lambda_max_over_chance", "stop", "gap_ratio")}
                        | ({"eig_top5": [round(x, 3) for x in r["eigvals"][:5]], "eig_bottom3": [round(x, 3) for x in r["eigvals"][-3:]]} if "eigvals" in r else {}))
parts = {"full": lambda z: z, "core": lambda z: z @ C, "variant": lambda z: z - (z @ C) @ C.T}


def ridge_r2(xtr, ytr, xte, yte, lam=1e-2):
    mu, sd = xtr.mean(0), xtr.std(0) + 1e-8; a, b = (xtr - mu) / sd, (xte - mu) / sd
    w = np.linalg.solve(a.T @ a + lam * len(a) * np.eye(a.shape[1]), a.T @ (ytr - ytr.mean(0)))
    p = b @ w + ytr.mean(0)
    return float(1 - ((yte - p) ** 2).sum() / ((yte - yte.mean(0)) ** 2).sum())


def flat(x):
    return x.reshape(-1, x.shape[-1])


zt = zw["te"]                                                       # (19, 2, 659, 64)
# 1) invariance: normalised squared difference between the two lighting views of the same frame, and between frames 8 apart (0 = unchanged, 1 = unrelated)
out["invariance_pair_diff"] = {}
for pn, f in parts.items():
    x = f(zt); var_ = flat(x[:, 0]).var(0) + 1e-12
    out["invariance_pair_diff"][pn] = {"lighting_views": float((((x[:, 0] - x[:, 1]) ** 2).reshape(-1, x.shape[-1]).mean(0) / (2 * var_)).mean()),
                                       "lag8": float((((x[:, 0, 8:] - x[:, 0, :-8]) ** 2).reshape(-1, x.shape[-1]).mean(0) / (2 * var_)).mean()),
                                       "lag32": float((((x[:, 0, 32:] - x[:, 0, :-32]) ** 2).reshape(-1, x.shape[-1]).mean(0) / (2 * var_)).mean())}
# 2) can the lighting coefficients (4, constant per video and view) be read out? held-out videos, R2
out["lighting_readout_r2"], out["content_readout_r2"] = {}, {}
for pn, f in parts.items():
    xtr, xte = f(zw["tr"]), f(zt)
    ytr = np.repeat(c_tr.reshape(len(rel), 2, 1, 4), xtr.shape[2], 2)           # (R, 2, T, 4)
    yte = np.repeat(c_te.reshape(len(te_v), 2, 1, 4), xte.shape[2], 2)
    out["lighting_readout_r2"][pn] = ridge_r2(flat(xtr[:, 0]), flat(ytr[:, 0]), flat(xte[:, 0]), flat(yte[:, 0]))
    # 3) can the image-derived content (centre-of-mass height, reach, motion) be read out?  first-segment training releases only
    out["content_readout_r2"][pn] = {}
    for k, p in prox_all.items():
        ytr_k = np.stack([p[kept_idx[rel[i][0]]] for i in first_tr]); yte_k = np.stack([p[kept_idx[v]] for v in te_v])
        out["content_readout_r2"][pn][k] = ridge_r2(flat(xtr[first_tr][:, 0]), ytr_k.reshape(-1, 1), flat(xte[:, 0]), yte_k.reshape(-1, 1))
# 4) the core coordinate itself: persistence within a video, and which (fast or slow) image-derived quantities it follows
psi = tl.fit_psi(zw["tr"], C); q = tl.apply_psi(zt, psi)[:, 0, :, 0]       # (19, 659)
ac = lambda x, l: float(np.mean([np.corrcoef(r[:-l], r[l:])[0, 1] for r in x]))
out["psi"] = {"autocorr_lag1": ac(q, 1), "autocorr_lag8": ac(q, 8), "autocorr_lag32": ac(q, 32), "autocorr_lag128": ac(q, 128)}
out["psi"]["abs_spearman_instantaneous"] = {k: abs(float(spearmanr(q.ravel(), np.stack([p[kept_idx[v]] for v in te_v]).ravel())[0])) for k, p in prox_all.items()}
win = lambda x, w: np.stack([np.convolve(r, np.ones(w) / w, "same") for r in x])
env = {"motion_mean_w60": win(np.stack([prox_all["motion"][kept_idx[v]] for v in te_v]), 60),
       "height_std_w60": np.sqrt(np.maximum(win(np.stack([prox_all["height"][kept_idx[v]] for v in te_v]) ** 2, 60) - win(np.stack([prox_all["height"][kept_idx[v]] for v in te_v]), 60) ** 2, 0)),
       "reach_mean_w60": win(np.stack([prox_all["reach"][kept_idx[v]] for v in te_v]), 60)}
out["psi"]["abs_spearman_slow_envelope_w60"] = {k: abs(float(spearmanr(q[:, 30:-30].ravel(), e[:, 30:-30].ravel())[0])) for k, e in env.items()}
out["psi"]["between_video_icc_test"] = float(qa.icc(q[:, None, :, None]))
import os
os.makedirs("results/nus_diag", exist_ok=True)
json.dump(out, open(f"results/nus_diag/{name}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
