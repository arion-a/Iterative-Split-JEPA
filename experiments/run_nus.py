"""N: the C2 protocol on the NUS real double-pendulum videos (release = video, no state labels). Frozen criteria: configs/nus.yaml.
Arms: main, flat, shuffled, temporal-only. Evaluator side (image-derived height, reach, motion) is used only for the report-only correlations.
Results are never overwritten."""
from __future__ import annotations

import hashlib, itertools, json, os, sys

import numpy as np
import torch
import yaml
from scipy.stats import spearmanr

from isj import explog, quotient_audit as qa, real_video_io as rio, temporal_ladder as tl
from isj.engine import eig_desc
from isj.pipeline import Pipeline

cfg = yaml.safe_load(open("configs/nus.yaml")); c = cfg["criteria"]; lad, cert = c["ladder"], c["certificate"]
if hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest() != open("configs/nus.criteria.sha256").read().strip():
    sys.exit("criteria differ from the frozen hash")
torch.set_num_threads(4)
frames = np.load("data/nus/frames.npy"); au = np.load("data/nus/audit.npz")
assert frames.shape[1] == cfg["frames_per_video"]
rng = np.random.default_rng(0)
views = np.stack([rio.illumination_views(frames[i], rng, cfg["nuisance_amp"]) for i in range(len(frames))])   # (R, 2, T, D)
R = len(frames); n_val, n_test = round(R * cfg["split_videos_fraction"]["val"]), round(R * cfg["split_videos_fraction"]["test"])
split = np.zeros(R, int); split[R - n_test - n_val:R - n_test] = 1; split[R - n_test:] = 2
print("videos", R, "split", [int((split == i).sum()) for i in range(3)], flush=True)
targets = {k: au[k][:, 1:] for k in ("height", "reach", "motion")}
os.makedirs("results/nus", exist_ok=True)


def cert_of(q, s):
    return qa.certificate(q[split == 0], q[split == 1], q[split == 2], cert["horizon_K"], cert["delta_std"], cert["n_pairs"], s)


pipes, res = {}, {}
for s in cfg["seeds"]:
    pipe = Pipeline(views[split == 0], cfg, s)
    z = pipe.latent(views); zw = pipe.whiten(z)
    assert np.isfinite(zw).all()
    main = tl.run_ladder(zw[split == 0], lad["lags"], lad["gamma_min"], lad["b2_quantile"], False, s, s1_chance_fraction=lad["s1_chance_fraction"])
    shuf = tl.run_ladder(zw[split == 0], lad["lags"], lad["gamma_min"], lad["b2_quantile"], True, s, s1_chance_fraction=lad["s1_chance_fraction"])
    psi = tl.fit_psi(zw[split == 0], main["core"])
    q = {"main": tl.apply_psi(zw, psi), "shuffled": tl.apply_psi(zw, tl.fit_psi(zw[split == 0], shuf["core"]))}
    proj = (z - pipe.zmean) @ pipe.flat_dir; q["flat"] = ((proj - proj[split == 0].mean()) / proj[split == 0].std())[..., None]
    ru, rv = tl.lag_pairs(zw[split == 0], lad["lags"][0]); dl = torch.from_numpy(ru - rv).double()
    vals, vecs = eig_desc(dl.T @ dl / len(dl)); p = zw @ vecs[:, -1].numpy(); q["temporal_only"] = ((p - p[split == 0].mean()) / p[split == 0].std())[..., None]
    arms = {}
    for a, v in q.items():
        x = v[split == 2, 0, :, 0].ravel()
        arms[a] = {**cert_of(v, s), "abs_spearman_with": {k: abs(float(spearmanr(x, t[split == 2].ravel())[0])) for k, t in targets.items()}}
    res[s] = {"seed": s, "split_sizes": [int((split == i).sum()) for i in range(3)], "stop": main["stop"], "core_dim": int(main["core"].shape[1]), "shuffled_stop": shuf["stop"],
              "ladder": [{k: v for k, v in x.items() if k not in ("V", "Q")} for x in main["rungs"]], "arms": arms}
    pipes[s] = (pipe, psi)
    print(s, main["stop"], {a: {k: round(v, 3) for k, v in r.items() if k in ("V", "icc", "L", "rollout_nmse")} | {"sp": {k: round(v, 2) for k, v in r["abs_spearman_with"].items()}} for a, r in arms.items()}, flush=True)
cq = {s: tl.apply_psi(pipes[s][0].whiten(pipes[s][0].latent(views[split == 2])), pipes[s][1])[:, 0, :, 0].ravel() for s in cfg["seeds"]}
stab = {f"{a}-{b}": abs(float(spearmanr(cq[a], cq[b])[0])) for a, b in itertools.combinations(cfg["seeds"], 2)}
for s in cfg["seeds"]:
    res[s]["seed_agreement"] = stab
    path = f"results/nus/{s}.json"
    with open(path, "x") as f:
        json.dump(res[s], f, indent=1)
    explog.append("run", f"NUS (N) seed {s} finished", stage="V", step="N", how="experiments/run_nus.py", artifact_paths=[path],
                  outputs={"stop": res[s]["stop"], "main": {k: round(v, 4) for k, v in res[s]["arms"]["main"].items() if isinstance(v, float)}, "flat_icc": round(res[s]["arms"]["flat"]["icc"], 4)})
