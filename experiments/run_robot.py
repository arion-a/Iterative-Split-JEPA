"""R1: the pipeline on ManiSkill PickCube episodes (SplitJEPA robotics setting): cross-view pairs (base vs side camera) are the rendering-pair family.
Evaluator side: linear readouts (held-out episodes) of simulator state from the invariant core, the variant block, a flat top-PC baseline and the full latent."""
import hashlib, json, os, sys

import numpy as np
import torch
import yaml

from isj import explog, temporal_ladder as tl
from isj.pipeline import Pipeline

cfg = yaml.safe_load(open("configs/other_data.yaml")); c = cfg["criteria"]["robot"]; rb = cfg["robot"]
if hashlib.sha256(json.dumps(cfg["criteria"], sort_keys=True).encode()).hexdigest() != open("configs/other_data.criteria.sha256").read().strip():
    sys.exit("criteria differ from the frozen hash")
cs = yaml.safe_load(open("configs/columbia_full.yaml")); lad = cs["criteria"]["ladder"]
torch.set_num_threads(4)
views = np.load("data/maniskill/views.npy"); au = np.load("data/maniskill/audit.npz")
nr, T = views.shape[0], views.shape[2]
split = np.zeros(nr, int); a, b = rb["split"][0], rb["split"][0] + rb["split"][1]; split[a:b] = 1; split[b:] = 2
tg = {"cube0": np.repeat(au["cube"][:, :1], T - 1, 1), "goal": np.repeat(au["goal"][:, None], T - 1, 1), "cube_t": au["cube"][:, 1:], "tcp": au["tcp"][:, 1:], "qpos": au["qpos"][:, 1:]}


def readout(x, name):
    """held-out R^2 (mean over target dims) of a ridge readout from x (R, 2, T-1, m), both cameras pooled; fit on train episodes, scored on test episodes."""
    if x.shape[-1] == 0:
        return float("nan")
    y = tg[name]
    def flat(sel):
        xs = x[sel].reshape(-1, x.shape[-1]); ys = np.repeat(y[sel][:, None], 2, 1).reshape(-1, y.shape[-1]); return xs, ys
    xt, yt = flat(split == 0); xe, ye = flat(split == 2)
    xa = np.concatenate([xt, np.ones((len(xt), 1))], 1)
    w = np.linalg.solve(xa.T @ xa + 1e-3 * np.eye(xa.shape[1]), xa.T @ yt)
    p = np.concatenate([xe, np.ones((len(xe), 1))], 1) @ w
    return float(np.mean(1 - ((ye - p) ** 2).sum(0) / ((ye - ye.mean(0)) ** 2).sum(0)))


os.makedirs("results/robot", exist_ok=True)
for s in cfg["seeds"]:
    pipe = Pipeline(views[split == 0], {"encoder": cfg["encoder"]}, s)
    z = pipe.latent(views); zw = pipe.whiten(z); d = zw.shape[-1]
    main = tl.run_ladder(zw[split == 0], rb["lags"], lad["gamma_min"], lad["b2_quantile"], False, s, s1_chance_fraction=lad["s1_chance_fraction"])
    core = main["core"]; m = core.shape[1]
    vrec = next((x for x in main["rungs"] if x["family"] == f"lag{rb['lags'][0]}" and "V" in x), None)
    pcs = np.linalg.eigh(np.cov((z - pipe.zmean).reshape(-1, d).T))[1][:, ::-1][:, :max(m, 1)]
    feats = {"core": zw @ core, "variant": zw @ vrec["V"] if vrec is not None else zw[..., :0], "flat_top_pcs": (z - pipe.zmean) @ pcs, "full": zw}
    rec = {"seed": s, "core_dim": int(m), "stop": main["stop"], "ladder": [{k: v for k, v in x.items() if k not in ("V", "Q")} for x in main["rungs"]],
           "r2": {f: {t: readout(x, t) for t in tg} for f, x in feats.items()}}
    path = f"results/robot/{s}.json"
    with open(path, "x") as f:
        json.dump(rec, f, indent=1)
    print(s, "core dim", m, {f: {t: round(v, 3) for t, v in r.items()} for f, r in rec["r2"].items()}, flush=True)
    explog.append("run", f"Robot PickCube (R1) seed {s} finished", stage="V", step="R1", how="experiments/run_robot.py", artifact_paths=[path],
                  outputs={"core_dim": int(m), "stop": main["stop"], "r2_core": {t: round(v, 3) for t, v in rec["r2"]["core"].items()}, "r2_flat": {t: round(v, 3) for t, v in rec["r2"]["flat_top_pcs"].items()}})
