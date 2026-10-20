"""Stage V C1: handshake pipeline on the Columbia real double-pendulum clips. Frozen criteria: configs/columbia.yaml. Results never overwritten."""
from __future__ import annotations

import hashlib, itertools, json, os, sys

import numpy as np
import torch
import yaml
from scipy.stats import spearmanr

from isj import explog, quotient_audit as qa, real_video_io as rio, temporal_ladder as tl
from isj.pipeline import Pipeline

cfg = yaml.safe_load(open("configs/columbia.yaml")); c = cfg["criteria"]; lad, cert = c["ladder"], c["certificate"]
if hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest() != open("configs/columbia.criteria.sha256").read().strip():
    sys.exit("criteria differ from the frozen hash")
torch.set_num_threads(4)
frames = np.load("data/columbia/frames.npy"); au = np.load("data/columbia/audit.npz")
rng = np.random.default_rng(0)
views = np.stack([rio.illumination_views(frames[i], rng, cfg["nuisance_amp"]) for i in range(len(frames))])        # (R, 2, T, D)
b = cfg["split_blocks"]; split = np.zeros(len(frames), int); split[b["val"][0]:b["val"][1]] = 1; split[b["test"][0]:] = 2
e = au["total_energy"][:, 1:]; valid = np.isfinite(e) & ~au["reject"][:, 1:]
os.makedirs("results/columbia", exist_ok=True)
pipes, res, cq = {}, {}, {}
for s in cfg["seeds"]:
    pipe = Pipeline(views[split == 0], cfg, s)
    zw = pipe.whiten(pipe.latent(views))
    out = tl.run_ladder(zw[split == 0], lad["lags"], lad["gamma_min"], lad["b2_quantile"], False, s, s1_chance_fraction=lad["s1_chance_fraction"])
    psi = tl.fit_psi(zw[split == 0], out["core"]); q = tl.apply_psi(zw, psi)
    cr = qa.certificate(q[split == 0], q[split == 1], q[split == 2], cert["horizon_K"], cert["delta_std"], cert["n_pairs"], s)
    tm = valid[split == 2]; qt = q[split == 2, 0, :, 0]
    cr["naming_abs_spearman"] = abs(float(spearmanr(qt[tm], e[split == 2][tm])[0]))
    et = np.where(valid[split == 2], e[split == 2], np.nan); cm = np.nanmean(et, 1)
    ceiling = float(np.nanvar(cm) / np.nanvar(et))                       # share of tracked-energy variance that is between clips (label-noise ceiling)
    xa = np.concatenate([zw[split == 0, 0].reshape(-1, zw.shape[-1]), np.ones((int((split == 0).sum()) * zw.shape[2], 1))], 1)
    ytr = e[split == 0].reshape(-1); vm = valid[split == 0].reshape(-1)
    w = np.linalg.lstsq(xa[vm], ytr[vm], rcond=None)[0]
    xt = np.concatenate([zw[split == 2, 0].reshape(-1, zw.shape[-1]), np.ones((int((split == 2).sum()) * zw.shape[2], 1))], 1)[tm.reshape(-1)]
    yt = e[split == 2].reshape(-1)[tm.reshape(-1)]
    r2 = float(1 - ((yt - xt @ w) ** 2).sum() / ((yt - yt.mean()) ** 2).sum())
    pipes[s] = (pipe, psi)
    res[s] = {"seed": s, "stop": out["stop"], "core_dim": int(out["core"].shape[1]), "ladder": [{k: v for k, v in x.items() if k not in ("V", "Q")} for x in out["rungs"]],
              "certificate": cr, "tracked_energy_between_clip_share_test": ceiling, "ceiling_probe_report_only_r2_test": r2}
    print(s, {k: round(v, 3) for k, v in cr.items() if isinstance(v, float)}, out["stop"], flush=True)
for s in cfg["seeds"]:                                                      # seed agreement on the common test clips (informational)
    pipe, psi = pipes[s]; cq[s] = tl.apply_psi(pipe.whiten(pipe.latent(views[split == 2])), psi)[:, 0, :, 0].ravel()
stab = {f"{a}-{b_}": abs(float(spearmanr(cq[a], cq[b_])[0])) for a, b_ in itertools.combinations(cfg["seeds"], 2)}
for s in cfg["seeds"]:
    res[s]["seed_agreement"] = stab
    path = f"results/columbia/{s}.json"
    with open(path, "x") as f:
        json.dump(res[s], f, indent=1)
    explog.append("run", f"Columbia real clips seed {s} finished", stage="V", step="C1", how="experiments/run_columbia.py", artifact_paths=[path],
                  outputs={"stop": res[s]["stop"], "certificate": {k: round(v, 4) for k, v in res[s]["certificate"].items() if isinstance(v, float)}})
