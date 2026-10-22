"""RL: the multi-rung ladder on ManiSkill PickCube, 64x64 RGB, conv encoder. Families in order: cross-view (base vs side camera), lag 8, lag 24.
python experiments/run_robot_ladder.py --pilot W   (label-free: 1000-step encoder, prints the rungs; chooses aug_weight, nothing is saved)
python experiments/run_robot_ladder.py             (the registered run; frozen criteria: configs/robot_ladder.yaml)
Evaluator side (simulator state) is used only for the held-out linear readouts of each block."""
from __future__ import annotations

import hashlib, json, os, sys

import numpy as np
import torch
import yaml

from isj import explog, temporal_ladder as tl
from isj.pipeline import Pipeline

cfg = yaml.safe_load(open("configs/robot_ladder.yaml")); c = cfg["criteria"]; lad = cfg["ladder"]
if hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest() != open("configs/robot_ladder.criteria.sha256").read().strip():
    sys.exit("criteria differ from the frozen hash")
torch.set_num_threads(4)
raw = np.load("data/maniskill_rgb/views.npy")                      # (R, 2, T, 12288) uint8
au = np.load("data/maniskill_rgb/audit.npz")
views = raw.astype(np.float32) / 255.0; del raw
nr, T = views.shape[0], views.shape[2]
a, b = cfg["split"][0], cfg["split"][0] + cfg["split"][1]
split = np.zeros(nr, int); split[a:b] = 1; split[b:] = 2
assert nr == cfg["episodes"] and [int((split == i).sum()) for i in range(3)] == cfg["split"]
tg = {"cube0": np.repeat(au["cube"][:, :1, :2], T - 1, 1), "goal": np.repeat(au["goal"][:, None], T - 1, 1), "cube_t": au["cube"][:, 1:, :2],
      "tcp": au["tcp"][:, 1:], "qpos": au["qpos"][:, 1:]}


def readout(x, name):
    """held-out R^2 (mean over target dims), ridge from x (R, 2, T-1, m), both cameras pooled; fit on train episodes, scored on test episodes."""
    if x.shape[-1] == 0:
        return float("nan")
    y = tg[name]

    def flat(sel):
        return x[sel].reshape(-1, x.shape[-1]), np.repeat(y[sel][:, None], 2, 1).reshape(-1, y.shape[-1])
    (xt, yt), (xe, ye) = flat(split == 0), flat(split == 2)
    xa = np.concatenate([xt, np.ones((len(xt), 1))], 1)
    w = np.linalg.solve(xa.T @ xa + 1e-3 * np.eye(xa.shape[1]), xa.T @ yt)
    p = np.concatenate([xe, np.ones((len(xe), 1))], 1) @ w
    return float(np.mean(1 - ((ye - p) ** 2).sum(0) / ((ye - ye.mean(0)) ** 2).sum(0)))


def rungs_of(run):
    return [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k in ("family", "content_dim", "d_k", "best_ratio", "gap_ratio", "lambda_max_over_chance", "stop")} for r in run["rungs"]]


if "--pilot" in sys.argv:
    w = float(sys.argv[sys.argv.index("--pilot") + 1])
    enc = dict(cfg["encoder"], steps=1000, aug_weight=w)
    pipe = Pipeline(views[split == 0], {"encoder": enc}, 0)
    zw = pipe.whiten(pipe.latent(views[split == 0]))
    run = tl.run_ladder(zw, cfg["lags"], lad["gamma_min"], lad["b2_quantile"], False, 0, s1_chance_fraction=lad["s1_chance_fraction"])
    print("PILOT aug_weight", w, rungs_of(run), flush=True)
    sys.exit(0)

assert cfg["encoder"]["aug_weight"] is not None, "aug_weight not chosen yet (pilot rule in the config)"
os.makedirs("results/robot_ladder", exist_ok=True)
for s in cfg["seeds"]:
    pipe = Pipeline(views[split == 0], {"encoder": cfg["encoder"]}, s)
    z = pipe.latent(views); zw = pipe.whiten(z); d = zw.shape[-1]
    main = tl.run_ladder(zw[split == 0], cfg["lags"], lad["gamma_min"], lad["b2_quantile"], False, s, s1_chance_fraction=lad["s1_chance_fraction"])
    shuf = tl.run_ladder(zw[split == 0], cfg["lags"], lad["gamma_min"], lad["b2_quantile"], True, s, s1_chance_fraction=lad["s1_chance_fraction"])
    cuts = [r for r in main["rungs"] if "V" in r]
    core = main["core"]; m = core.shape[1]
    pcs = np.linalg.eigh(np.cov((z - pipe.zmean).reshape(-1, d).T))[1][:, ::-1][:, :max(m, 1)]
    blocks = {f"variant_{r['family']}": zw @ r["V"] for r in cuts}
    blocks |= {"final_core": zw @ core, "flat_top_pcs": (z - pipe.zmean) @ pcs, "full": zw}
    rec = {"seed": s, "aug_weight": cfg["encoder"]["aug_weight"], "n_cuts": len(cuts), "cut_gap_ratios": [round(float(r["gap_ratio"]), 3) for r in cuts],
           "block_dims": {k: int(v.shape[-1]) for k, v in blocks.items()}, "stop": main["stop"], "ladder": rungs_of(main),
           "shuffled_n_cuts": sum("V" in r for r in shuf["rungs"]), "shuffled_ladder": rungs_of(shuf),
           "r2": {k: {t: readout(x, t) for t in tg} for k, x in blocks.items()}}
    path = f"results/robot_ladder/{s}.json"
    with open(path, "x") as f:
        json.dump(rec, f, indent=1)
    print(s, "cuts", rec["cut_gap_ratios"], "dims", rec["block_dims"], {k: {t: round(v, 2) for t, v in r.items()} for k, r in rec["r2"].items()}, flush=True)
    explog.append("run", f"Robot ladder (RL) seed {s} finished", stage="V", step="RL", how="experiments/run_robot_ladder.py", artifact_paths=[path],
                  outputs={"cuts": rec["cut_gap_ratios"], "block_dims": rec["block_dims"], "r2_full_cube0": round(rec["r2"]["full"]["cube0"], 3), "r2_final_core": {t: round(v, 3) for t, v in rec["r2"]["final_core"].items()}})
