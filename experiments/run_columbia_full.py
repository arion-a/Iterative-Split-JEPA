"""C2: the full handshake protocol on the Columbia real clips at video level (release = video). Frozen criteria: configs/columbia_full.yaml.
Arms: main (ladder + max-ICC selector), flat (top principal component), shuffled (lag partners permuted), temporal-only (release-free slowest direction).
Evaluator side (tracked energy) is used only for naming, controls and the report-only ceiling probe. Results are never overwritten."""
from __future__ import annotations

import hashlib, itertools, json, os, sys

import numpy as np
import torch
import yaml
from scipy.stats import spearmanr

from isj import explog, handshake_eval as ev, quotient_audit as qa, real_video_io as rio, temporal_ladder as tl
from isj.engine import eig_desc
from isj.pipeline import Pipeline

cfg = yaml.safe_load(open("configs/columbia_full.yaml")); c = cfg["criteria"]; lad, cert = c["ladder"], c["certificate"]
if hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest() != open("configs/columbia_full.criteria.sha256").read().strip():
    sys.exit("criteria differ from the frozen hash")
torch.set_num_threads(4)
frames = np.load("data/columbia_full/frames.npy"); au = np.load("data/columbia_full/audit.npz")           # (100, 660, D); evaluator table
rng = np.random.default_rng(0)
views = np.stack([rio.illumination_views(frames[i], rng, cfg["nuisance_amp"]) for i in range(len(frames))])   # (R, 2, T, D)
sv = cfg["split_videos"]; split = np.zeros(len(frames), int); split[sv["val"][0]:sv["val"][1]] = 1; split[sv["test"][0]:sv["test"][1]] = 2
assert [int((split == i).sum()) for i in range(3)] == [70, 10, 20]
e = au["total_energy"][:, 1:]; valid = np.isfinite(e) & ~au["reject"][:, 1:]
tm = valid[split == 2]; et = e[split == 2][tm]
label_icc = ev.anova_icc(e[split == 2], valid[split == 2])
os.makedirs("results/columbia_full", exist_ok=True)


def nm(q):
    return abs(float(spearmanr(q[split == 2, 0, :, 0][tm], et)[0]))


def cert_of(q, s):
    return qa.certificate(q[split == 0], q[split == 1], q[split == 2], cert["horizon_K"], cert["delta_std"], cert["n_pairs"], s)


pipes, res = {}, {}
for s in cfg["seeds"]:
    pipe = Pipeline(views[split == 0], cfg, s)
    z = pipe.latent(views); zw = pipe.whiten(z); d = zw.shape[-1]
    assert np.isfinite(zw).all()
    main = tl.run_ladder(zw[split == 0], lad["lags"], lad["gamma_min"], lad["b2_quantile"], False, s, s1_chance_fraction=lad["s1_chance_fraction"])
    shuf = tl.run_ladder(zw[split == 0], lad["lags"], lad["gamma_min"], lad["b2_quantile"], True, s, s1_chance_fraction=lad["s1_chance_fraction"])
    psi = tl.fit_psi(zw[split == 0], main["core"])
    q = {"main": tl.apply_psi(zw, psi), "shuffled": tl.apply_psi(zw, tl.fit_psi(zw[split == 0], shuf["core"]))}
    proj = (z - pipe.zmean) @ pipe.flat_dir; q["flat"] = ((proj - proj[split == 0].mean()) / proj[split == 0].std())[..., None]
    ru, rv = tl.lag_pairs(zw[split == 0], lad["lags"][0]); dl = torch.from_numpy(ru - rv).double()
    vals, vecs = eig_desc(dl.T @ dl / len(dl)); p = zw @ vecs[:, -1].numpy(); q["temporal_only"] = ((p - p[split == 0].mean()) / p[split == 0].std())[..., None]
    arms = {a: {**cert_of(v, s), "naming_abs_spearman": nm(v)} for a, v in q.items()}
    xa = np.concatenate([zw[split == 0, 0].reshape(-1, d), np.ones((int((split == 0).sum()) * zw.shape[2], 1))], 1)
    vm = valid[split == 0].reshape(-1); w = np.linalg.lstsq(xa[vm], e[split == 0].reshape(-1)[vm], rcond=None)[0]
    xt = np.concatenate([zw[split == 2, 0].reshape(-1, d), np.ones((int((split == 2).sum()) * zw.shape[2], 1))], 1)[tm.reshape(-1)]
    yt = e[split == 2].reshape(-1)[tm.reshape(-1)]
    v_lag = next((x["V"] for x in main["rungs"] if x["family"] == f"lag{lad['lags'][0]}" and "V" in x), None)
    res[s] = {"seed": s, "stop": main["stop"], "core_dim": int(main["core"].shape[1]), "shuffled_stop": shuf["stop"],
              "ladder": [{k: v for k, v in x.items() if k not in ("V", "Q")} for x in main["rungs"]], "arms": arms,
              "reach_psi": ev.reach_curve(q["main"], split), "reach_variant_block": ev.reach_curve(zw @ v_lag, split) if v_lag is not None else None,
              "tracked_energy_between_video_icc_test": label_icc,
              "ceiling_probe_report_only_r2_test": float(1 - ((yt - xt @ w) ** 2).sum() / ((yt - yt.mean()) ** 2).sum())}
    pipes[s] = (pipe, psi)
    print(s, {a: {k: round(v, 3) for k, v in r.items() if k in ("V", "icc", "L", "rollout_nmse", "naming_abs_spearman")} for a, r in arms.items()}, main["stop"], flush=True)
cq = {s: tl.apply_psi(pipes[s][0].whiten(pipes[s][0].latent(views[split == 2])), pipes[s][1])[:, 0, :, 0].ravel() for s in cfg["seeds"]}
stab = {f"{a}-{b}": abs(float(spearmanr(cq[a], cq[b])[0])) for a, b in itertools.combinations(cfg["seeds"], 2)}
for s in cfg["seeds"]:
    res[s]["seed_agreement"] = stab
    path = f"results/columbia_full/{s}.json"
    with open(path, "x") as f:
        json.dump(res[s], f, indent=1)
    explog.append("run", f"Columbia full (C2) seed {s} finished", stage="V", step="C2", how="experiments/run_columbia_full.py", artifact_paths=[path],
                  outputs={"stop": res[s]["stop"], "main": {k: round(v, 4) for k, v in res[s]["arms"]["main"].items() if isinstance(v, float)}, "flat_naming": round(res[s]["arms"]["flat"]["naming_abs_spearman"], 4)})
