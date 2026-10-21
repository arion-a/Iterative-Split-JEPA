"""C3: correlation of the Columbia coordinate with total / kinetic / potential energy and amplitude (evaluator side). Same pipelines as C2, retrained from the same seeds."""
import hashlib, json, os, sys

import numpy as np
import torch
import yaml
from scipy.stats import spearmanr

from isj import explog, handshake_eval as ev, real_video_io as rio, temporal_ladder as tl
from isj.pipeline import Pipeline

cfg = yaml.safe_load(open("configs/columbia_full.yaml")); cc = yaml.safe_load(open("configs/columbia_confound.yaml")); lad = cfg["criteria"]["ladder"]
if hashlib.sha256(json.dumps(cc["criteria"], sort_keys=True).encode()).hexdigest() != open("configs/columbia_confound.criteria.sha256").read().strip():
    sys.exit("criteria differ from the frozen hash")
torch.set_num_threads(4)
frames = np.load("data/columbia_full/frames.npy"); fa = np.load("data/columbia_full/audit.npz"); ca = np.load("data/columbia/audit.npz")
nv, tv = frames.shape[:2]
phys = {k: ca[k].reshape(nv, tv) for k in ("total_energy", "kinetic_energy", "potential_energy", "reject")}
rng = np.random.default_rng(0)
views = np.stack([rio.illumination_views(frames[i], rng, cfg["nuisance_amp"]) for i in range(nv)])
sv = cfg["split_videos"]; split = np.zeros(nv, int); split[sv["val"][0]:sv["val"][1]] = 1; split[sv["test"][0]:sv["test"][1]] = 2
amp = ev.local_amplitude(fa["theta_1"], fa["theta_2"], cc["amplitude"]["half_window_frames"], cc["amplitude"]["min_valid"])
ok = ~phys["reject"]
targets = {"total_energy": phys["total_energy"], "kinetic_energy": phys["kinetic_energy"], "potential_energy": phys["potential_energy"], "amplitude": amp}
os.makedirs("results/columbia_confound", exist_ok=True)
for s in cfg["seeds"]:
    pipe = Pipeline(views[split == 0], cfg, s)
    z = pipe.latent(views); zw = pipe.whiten(z)
    main = tl.run_ladder(zw[split == 0], lad["lags"], lad["gamma_min"], lad["b2_quantile"], False, s, s1_chance_fraction=lad["s1_chance_fraction"])
    q = {"main": tl.apply_psi(zw, tl.fit_psi(zw[split == 0], main["core"]))[:, 0, :, 0]}
    proj = (z - pipe.zmean) @ pipe.flat_dir; q["flat"] = ((proj - proj[split == 0].mean()) / proj[split == 0].std())[:, 0]
    mask = np.isfinite(targets["total_energy"][:, 1:]) & ok[:, 1:]
    for k in ("kinetic_energy", "potential_energy", "amplitude"):
        mask &= np.isfinite(targets[k][:, 1:])
    tm = mask[split == 2]
    rec = {"seed": s, "n_frames": int(tm.sum()), "abs_spearman": {}, "partial": {}}
    for arm, series in q.items():
        x = series[split == 2][tm]
        rec["abs_spearman"][arm] = {k: abs(float(spearmanr(x, v[:, 1:][split == 2][tm])[0])) for k, v in targets.items()}
    x = q["main"][split == 2][tm]; E_ = targets["total_energy"][:, 1:][split == 2][tm]; A_ = amp[:, 1:][split == 2][tm]
    rec["partial"] = {"psi_energy_given_amplitude": ev.partial_spearman(x, E_, A_), "psi_amplitude_given_energy": ev.partial_spearman(x, A_, E_),
                      "energy_amplitude_abs_spearman": abs(float(spearmanr(E_, A_)[0]))}
    c2 = json.load(open(f"results/columbia_full/{s}.json"))["arms"]["main"]["naming_abs_spearman"]
    rec["c2_main_naming"] = c2; rec["reproduction_diff"] = abs(rec["abs_spearman"]["main"]["total_energy"] - c2)
    path = f"results/columbia_confound/{s}.json"
    with open(path, "x") as f:
        json.dump(rec, f, indent=1)
    print(json.dumps(rec), flush=True)
    explog.append("run", f"Columbia confound check seed {s} finished", stage="V", step="C3", how="experiments/run_columbia_confound.py", artifact_paths=[path],
                  outputs={"main": {k: round(v, 3) for k, v in rec["abs_spearman"]["main"].items()}, "reproduction_diff": round(rec["reproduction_diff"], 4)})
