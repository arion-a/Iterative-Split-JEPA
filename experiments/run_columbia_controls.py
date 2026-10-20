"""Stage V C1b: control arms on Columbia (flat, shuffled, temporal-only) with the C1 pipelines retrained from the same seeds."""
import hashlib, json, os, sys

import numpy as np
import torch
import yaml
from scipy.stats import spearmanr

from isj import explog, real_video_io as rio, temporal_ladder as tl
from isj.engine import eig_desc
from isj.pipeline import Pipeline

cfg = yaml.safe_load(open("configs/columbia.yaml")); cc = yaml.safe_load(open("configs/columbia_controls.yaml"))
if hashlib.sha256(json.dumps(cc["criteria"], sort_keys=True).encode()).hexdigest() != open("configs/columbia_controls.criteria.sha256").read().strip():
    sys.exit("criteria differ from the frozen hash")
lad = cfg["criteria"]["ladder"]; torch.set_num_threads(4)
frames = np.load("data/columbia/frames.npy"); au = np.load("data/columbia/audit.npz")
rng = np.random.default_rng(0)
views = np.stack([rio.illumination_views(frames[i], rng, cfg["nuisance_amp"]) for i in range(len(frames))])
b = cfg["split_blocks"]; split = np.zeros(len(frames), int); split[b["val"][0]:b["val"][1]] = 1; split[b["test"][0]:] = 2
e = au["total_energy"][:, 1:]; valid = np.isfinite(e) & ~au["reject"][:, 1:]
tm = valid[split == 2]; et = e[split == 2][tm]
nm = lambda q: abs(float(spearmanr(q[split == 2, 0, :, 0][tm], et)[0]))
os.makedirs("results/columbia_controls", exist_ok=True)
for s in cfg["seeds"]:
    pipe = Pipeline(views[split == 0], cfg, s)
    z = pipe.latent(views); zw = pipe.whiten(z); d = zw.shape[-1]
    main = tl.run_ladder(zw[split == 0], lad["lags"], lad["gamma_min"], lad["b2_quantile"], False, s, s1_chance_fraction=lad["s1_chance_fraction"])
    shuf = tl.run_ladder(zw[split == 0], lad["lags"], lad["gamma_min"], lad["b2_quantile"], True, s, s1_chance_fraction=lad["s1_chance_fraction"])
    q_main = tl.apply_psi(zw, tl.fit_psi(zw[split == 0], main["core"])); q_shuf = tl.apply_psi(zw, tl.fit_psi(zw[split == 0], shuf["core"]))
    proj = (z - pipe.zmean) @ pipe.flat_dir; q_flat = ((proj - proj[split == 0].mean()) / proj[split == 0].std())[..., None]
    ru, rv = tl.lag_pairs(zw[split == 0], 8); dl = torch.from_numpy(ru - rv).double()
    vals, vecs = eig_desc(dl.T @ dl / len(dl)); p = zw @ vecs[:, -1].numpy(); q_t = ((p - p[split == 0].mean()) / p[split == 0].std())[..., None]
    rec = {"seed": s, "main": nm(q_main), "flat": nm(q_flat), "shuffled": nm(q_shuf), "temporal_only": nm(q_t), "c1_main": json.load(open(f"results/columbia/{s}.json"))["certificate"]["naming_abs_spearman"]}
    rec["reproduction_diff"] = abs(rec["main"] - rec["c1_main"])
    path = f"results/columbia_controls/{s}.json"
    with open(path, "x") as f:
        json.dump(rec, f, indent=1)
    print(rec, flush=True)
    explog.append("run", f"Columbia control arms seed {s} finished", stage="V", step="C1b", how="experiments/run_columbia_controls.py", artifact_paths=[path], outputs={k: round(v, 3) for k, v in rec.items() if isinstance(v, float)})
