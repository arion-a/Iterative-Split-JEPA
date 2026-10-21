"""T1-T3: representation / data / lag tests on the NUS videos. One variant per call: python experiments/run_nus_t.py S0|SH|SL|C0|CL.
Frozen criteria: configs/nus_t.yaml (rule in docs/EVIDENCE.md, T1-T3). Results are never overwritten."""
from __future__ import annotations

import hashlib, itertools, json, os, sys

import numpy as np
import torch
import yaml
from scipy.stats import spearmanr

from isj import explog, quotient_audit as qa, real_video_io as rio, temporal_ladder as tl
from isj.engine import eig_desc
from isj.pipeline import Pipeline

cfg = yaml.safe_load(open("configs/nus_t.yaml")); c = cfg["criteria"]
if hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest() != open("configs/nus_t.criteria.sha256").read().strip():
    sys.exit("criteria differ from the frozen hash")
name = sys.argv[1]; var = cfg["variants"][name]
enc_cfg = cfg["encoder_conv"] if var["arch"] == "conv" else cfg["encoder_mlp"]
lad, cert = cfg["ladder"], cfg["certificate"]; T = cfg["frames_per_segment"]
torch.set_num_threads(4)

allf = np.load("data/nus/all64.npy"); meta = json.load(open("data/nus/all_meta.json"))
kept = json.load(open("data/nus/index.json"))["kept"]
vid = np.array(meta["video"]); fr = np.array(meta["frame"])
vids = {}
for v in kept:
    m = np.where(vid == v)[0]; o = m[np.argsort(fr[m])]
    assert (fr[o] == np.arange(1, len(o) + 1)).all(), v
    vids[v] = o
n_tr = cfg["base_training_videos"]; R = len(kept); n_val, n_te = round(R * 0.1), round(R * 0.2)
assert R - n_val - n_te == n_tr
tr_v, va_v, te_v = kept[:n_tr], kept[n_tr:n_tr + n_val], kept[n_tr + n_val:]


def seg(v, j):
    return allf[vids[v][j * T:(j + 1) * T]]


segs_tr = [seg(v, 0) for v in tr_v]
if var["train"] == "half":
    segs_tr = segs_tr[::2]
elif var["train"] == "long":
    segs_tr = [seg(v, j) for v in tr_v for j in range(len(vids[v]) // T)]
size = var["size"]


def views_of(segs, seed):
    rng = np.random.default_rng(seed)
    out = []
    for s in segs:
        x = s.astype(np.float32) / 255.0
        if size == 32:
            x = x.reshape(-1, 32, 2, 32, 2).mean((2, 4)).reshape(len(x), -1)
        out.append(rio.illumination_views(x, rng, cfg["nuisance_amp"], size))
    return np.stack(out)


v_tr, v_va, v_te = views_of(segs_tr, 0), views_of([seg(v, 0) for v in va_v], 1), views_of([seg(v, 0) for v in te_v], 2)
print(name, "train releases", len(v_tr), "val", len(v_va), "test", len(v_te), "size", size, flush=True)
os.makedirs(f"results/nus_t/{name}", exist_ok=True)


def cert_of(q_tr, q_va, q_te, s):
    r = qa.certificate(q_tr, q_va, q_te, cert["horizon_K"], cert["delta_std"], cert["n_pairs"], s)
    return {k: (float(x) if isinstance(x, (float, int, np.floating, np.integer)) else x) for k, x in r.items()}


def cuts_of(run):
    return [round(float(r["gap_ratio"]), 3) for r in run["rungs"] if "gap_ratio" in r]


res, qtest = {}, {}
for s in cfg["seeds"]:
    pipe = Pipeline(v_tr, {"encoder": enc_cfg}, s)
    z = {k: pipe.latent(v) for k, v in (("tr", v_tr), ("va", v_va), ("te", v_te))}
    zw = {k: pipe.whiten(x) for k, x in z.items()}
    assert all(np.isfinite(x).all() for x in zw.values())
    out = {"seed": s, "train_releases": len(v_tr), "sets": {}}
    for ls, lags in cfg["lag_sets"].items():
        main = tl.run_ladder(zw["tr"], lags, lad["gamma_min"], lad["b2_quantile"], False, s, s1_chance_fraction=lad["s1_chance_fraction"])
        shuf = tl.run_ladder(zw["tr"], lags, lad["gamma_min"], lad["b2_quantile"], True, s, s1_chance_fraction=lad["s1_chance_fraction"])
        psi, psi_s = tl.fit_psi(zw["tr"], main["core"]), tl.fit_psi(zw["tr"], shuf["core"])
        qm = {k: tl.apply_psi(zw[k], psi) for k in zw}
        qtest[(ls, s)] = qm["te"][:, 0, :, 0].ravel()
        out["sets"][ls] = {"lags": lags, "stop": main["stop"], "core_dim": int(main["core"].shape[1]), "cut_gap_ratios": cuts_of(main),
                           "shuffled_stop": shuf["stop"], "shuffled_cut_gap_ratios": cuts_of(shuf),
                           "ladder": [{k: v for k, v in x.items() if k not in ("V", "Q", "eigvals")} for x in main["rungs"]],
                           "main": cert_of(qm["tr"], qm["va"], qm["te"], s),
                           "shuffled": cert_of(*[tl.apply_psi(zw[k], psi_s) for k in ("tr", "va", "te")], s)}
    proj = {k: (z[k] - pipe.zmean) @ pipe.flat_dir for k in z}; mu, sd = proj["tr"].mean(), proj["tr"].std()
    out["flat"] = cert_of(*[((proj[k] - mu) / sd)[..., None] for k in ("tr", "va", "te")], s)
    ru, rv = tl.lag_pairs(zw["tr"], cfg["lag_sets"]["A"][0]); dl = torch.from_numpy(ru - rv).double()
    _, vecs = eig_desc(dl.T @ dl / len(dl)); p = {k: zw[k] @ vecs[:, -1].numpy() for k in zw}
    pm, ps = p["tr"].mean(), p["tr"].std()
    out["temporal_only"] = cert_of(*[((p[k] - pm) / ps)[..., None] for k in ("tr", "va", "te")], s)
    out["per_lag_best_ratio"] = {}
    for lag in cfg["per_lag_table"]:
        r = tl.run_ladder(zw["tr"], [lag], lad["gamma_min"], lad["b2_quantile"], False, s, use_aug=False, s1_chance_fraction=lad["s1_chance_fraction"])["rungs"][0]
        out["per_lag_best_ratio"][str(lag)] = {"best_ratio": float(r["best_ratio"]), "lambda_max_over_chance": float(r["lambda_max_over_chance"]), "cut": "gap_ratio" in r}
    res[s] = out
    print(name, s, {ls: (o["stop"], o["cut_gap_ratios"], round(o["main"]["rollout_nmse"], 3), round(o["main"]["icc"], 3)) for ls, o in out["sets"].items()}, "flat icc", round(out["flat"]["icc"], 3), flush=True)
    del z, zw, pipe
for ls in cfg["lag_sets"]:
    stab = {f"{a}-{b}": abs(float(spearmanr(qtest[(ls, a)], qtest[(ls, b)])[0])) for a, b in itertools.combinations(cfg["seeds"], 2)}
    for s in cfg["seeds"]:
        res[s]["sets"][ls]["seed_agreement"] = stab
for s in cfg["seeds"]:
    path = f"results/nus_t/{name}/{s}.json"
    with open(path, "x") as f:
        json.dump(res[s], f, indent=1)
    explog.append("run", f"NUS test {name} seed {s} finished", stage="V", step="NT", how="experiments/run_nus_t.py", artifact_paths=[path],
                  outputs={ls: {"stop": o["stop"], "cuts": o["cut_gap_ratios"], "rollout": round(o["main"]["rollout_nmse"], 4), "icc": round(o["main"]["icc"], 4), "agreement_min": round(min(o["seed_agreement"].values()), 4)} for ls, o in res[s]["sets"].items()})
