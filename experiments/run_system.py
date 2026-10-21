"""G3: the C2 protocol on another real system (single_pendulum / elastic_pendulum): video-level split, arms main / flat / shuffled / temporal-only,
naming against tracked total energy, informational correlations with the other tracked quantities. Frozen criteria: configs/gaps.yaml."""
import hashlib, itertools, json, os, sys

import numpy as np
import torch
import yaml
from scipy.stats import spearmanr

from isj import explog, handshake_eval as ev, quotient_audit as qa, real_video_io as rio, temporal_ladder as tl
from isj.engine import eig_desc
from isj.pipeline import Pipeline

name = sys.argv[1]
cfg = yaml.safe_load(open("configs/gaps.yaml")); c = cfg["criteria"]
if hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest() != open("configs/gaps.criteria.sha256").read().strip():
    sys.exit("criteria differ from the frozen hash")
cs = yaml.safe_load(open("configs/columbia_full.yaml")); lad, cert = cs["criteria"]["ladder"], cs["criteria"]["certificate"]
torch.set_num_threads(4)
d0 = f"data/{name}_full"; frames = np.load(f"{d0}/frames.npy"); au = {k: v for k, v in np.load(f"{d0}/audit.npz").items()}
nv = len(frames); f1, f2 = cfg["split_fractions"][0], cfg["split_fractions"][1]
n_tr, n_va = int(f1 * nv), int(f2 * nv)
split = np.zeros(nv, int); split[n_tr:n_tr + n_va] = 1; split[n_tr + n_va:] = 2
rng = np.random.default_rng(0)
views = np.stack([rio.illumination_views(frames[i], rng, cfg["nuisance_amp"]) for i in range(nv)])
e = au["total_energy"][:, 1:]; valid = np.isfinite(e) & ~au["reject"].astype(bool)[:, 1:]
th1, th2 = (au["theta_1"], au["theta_2"]) if "theta_1" in au else (au["theta"], au["theta"])
au["amplitude"] = ev.local_amplitude(th1, th2)
targets = {k: v for k, v in au.items() if k != "reject" and np.issubdtype(v.dtype, np.floating)}
tmask = valid.copy()
for k, v in targets.items():
    tmask &= np.isfinite(v[:, 1:])
tm = tmask[split == 2]
os.makedirs(f"results/system_{name}", exist_ok=True)
pipes, res = {}, {}
for s in cfg["seeds"]:
    pipe = Pipeline(views[split == 0], cs, s)
    z = pipe.latent(views); zw = pipe.whiten(z); d = zw.shape[-1]
    main = tl.run_ladder(zw[split == 0], lad["lags"], lad["gamma_min"], lad["b2_quantile"], False, s, s1_chance_fraction=lad["s1_chance_fraction"])
    shuf = tl.run_ladder(zw[split == 0], lad["lags"], lad["gamma_min"], lad["b2_quantile"], True, s, s1_chance_fraction=lad["s1_chance_fraction"])
    psi = tl.fit_psi(zw[split == 0], main["core"])
    q = {"main": tl.apply_psi(zw, psi), "shuffled": tl.apply_psi(zw, tl.fit_psi(zw[split == 0], shuf["core"]))}
    proj = (z - pipe.zmean) @ pipe.flat_dir; q["flat"] = ((proj - proj[split == 0].mean()) / proj[split == 0].std())[..., None]
    ru, rv = tl.lag_pairs(zw[split == 0], lad["lags"][0]); dl = torch.from_numpy(ru - rv).double()
    vals, vecs = eig_desc(dl.T @ dl / len(dl)); p = zw @ vecs[:, -1].numpy(); q["temporal_only"] = ((p - p[split == 0].mean()) / p[split == 0].std())[..., None]
    arms = {}
    for a, v in q.items():
        cr = qa.certificate(v[split == 0], v[split == 1], v[split == 2], cert["horizon_K"], cert["delta_std"], cert["n_pairs"], s)
        cr["naming_abs_spearman"] = abs(float(spearmanr(v[split == 2, 0, :, 0][tm], e[split == 2][tm])[0]))
        cr["abs_spearman_with"] = {k: abs(float(spearmanr(v[split == 2, 0, :, 0][tm], t[:, 1:][split == 2][tm])[0])) for k, t in targets.items()}
        arms[a] = cr
    res[s] = {"seed": s, "system": name, "n_videos": nv, "split_sizes": [int((split == i).sum()) for i in range(3)], "stop": main["stop"], "core_dim": int(main["core"].shape[1]),
              "ladder": [{k: v for k, v in x.items() if k not in ("V", "Q")} for x in main["rungs"]], "arms": arms, "n_test_frames": int(tm.sum()),
              "energy_between_video_icc_test": ev.anova_icc(e[split == 2], valid[split == 2])}
    pipes[s] = (pipe, psi)
    print(name, s, {a: round(r["naming_abs_spearman"], 3) for a, r in arms.items()}, main["stop"], flush=True)
cq = {s: tl.apply_psi(pipes[s][0].whiten(pipes[s][0].latent(views[split == 2])), pipes[s][1])[:, 0, :, 0].ravel() for s in cfg["seeds"]}
stab = {f"{a}-{b}": abs(float(spearmanr(cq[a], cq[b])[0])) for a, b in itertools.combinations(cfg["seeds"], 2)}
for s in cfg["seeds"]:
    res[s]["seed_agreement"] = stab
    path = f"results/system_{name}/{s}.json"
    with open(path, "x") as f:
        json.dump(res[s], f, indent=1)
    explog.append("run", f"{name} (G3) seed {s} finished", stage="V", step="G3", how="experiments/run_system.py", artifact_paths=[path],
                  outputs={"naming": {a: round(r["naming_abs_spearman"], 4) for a, r in res[s]["arms"].items()}, "stop": res[s]["stop"]})
