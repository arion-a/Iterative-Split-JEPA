"""H1: the pipeline on the HF controlled pendulum videos (release = video, provided whole-video split). Frozen criteria: configs/other_data.yaml."""
import hashlib, itertools, json, os, sys

import numpy as np
import torch
import yaml
from scipy.stats import spearmanr

from isj import explog, quotient_audit as qa, real_video_io as rio, temporal_ladder as tl
from isj.engine import eig_desc
from isj.pipeline import Pipeline

cfg = yaml.safe_load(open("configs/other_data.yaml")); c = cfg["criteria"]
if hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest() != open("configs/other_data.criteria.sha256").read().strip():
    sys.exit("criteria differ from the frozen hash")
cs = yaml.safe_load(open("configs/columbia_full.yaml")); lad, cert = cs["criteria"]["ladder"], cs["criteria"]["certificate"]
torch.set_num_threads(4)
frames = np.load("data/hf_pendulum/frames.npy"); au = {k: v for k, v in np.load("data/hf_pendulum/audit.npz").items()}; split = au.pop("split")
rng = np.random.default_rng(0)
views = np.stack([rio.illumination_views(frames[i], rng, cfg["nuisance_amp"]) for i in range(len(frames))])
targets = {k: v[:, 1:] for k, v in au.items()}; tm = np.ones_like(targets["energy"], bool)[split == 2]
os.makedirs("results/hf_pendulum", exist_ok=True)
pipes, res = {}, {}
for s in cfg["seeds"]:
    pipe = Pipeline(views[split == 0], cfg, s)
    z = pipe.latent(views); zw = pipe.whiten(z)
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
        arms[a] = {**qa.certificate(v[split == 0], v[split == 1], v[split == 2], cert["horizon_K"], cert["delta_std"], cert["n_pairs"], s),
                   "abs_spearman_with": {k: abs(float(spearmanr(x, t[split == 2].ravel())[0])) for k, t in targets.items()}}
        arms[a]["naming_abs_spearman"] = arms[a]["abs_spearman_with"]["energy"]
    res[s] = {"seed": s, "split_sizes": [int((split == i).sum()) for i in range(3)], "stop": main["stop"], "core_dim": int(main["core"].shape[1]),
              "ladder": [{k: v for k, v in x.items() if k not in ("V", "Q")} for x in main["rungs"]], "arms": arms}
    pipes[s] = (pipe, psi)
    print(s, {a: round(r["naming_abs_spearman"], 3) for a, r in arms.items()}, "light", round(arms["main"]["abs_spearman_with"]["light_angle"], 3), main["stop"], flush=True)
cq = {s: tl.apply_psi(pipes[s][0].whiten(pipes[s][0].latent(views[split == 2])), pipes[s][1])[:, 0, :, 0].ravel() for s in cfg["seeds"]}
stab = {f"{a}-{b}": abs(float(spearmanr(cq[a], cq[b])[0])) for a, b in itertools.combinations(cfg["seeds"], 2)}
for s in cfg["seeds"]:
    res[s]["seed_agreement"] = stab
    path = f"results/hf_pendulum/{s}.json"
    with open(path, "x") as f:
        json.dump(res[s], f, indent=1)
    explog.append("run", f"HF pendulum (H1) seed {s} finished", stage="V", step="H1", how="experiments/run_hfpend.py", artifact_paths=[path],
                  outputs={"naming": {a: round(r["naming_abs_spearman"], 4) for a, r in res[s]["arms"].items()}, "light": round(res[s]["arms"]["main"]["abs_spearman_with"]["light_angle"], 4), "stop": res[s]["stop"]})
