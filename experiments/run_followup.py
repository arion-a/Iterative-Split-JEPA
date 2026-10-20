"""Stage V F1: main arm vs release-free temporal-only arm on retrained handshake encoders. Frozen criteria: configs/followup.yaml."""
from __future__ import annotations

import hashlib, json, os, sys

import numpy as np
import torch
import yaml

from isj import explog, handshake_eval as ev, quotient_audit as qa, temporal_ladder as tl
from isj.engine import eig_desc
from isj.pipeline import Pipeline
from isj.video_io import load_frames

cfg = yaml.safe_load(open("configs/handshake.yaml")); fu = yaml.safe_load(open("configs/followup.yaml"))
if hashlib.sha256(json.dumps(fu["criteria"], sort_keys=True).encode()).hexdigest() != open("configs/followup.criteria.sha256").read().strip():
    sys.exit("criteria differ from the frozen hash")
lad, lag = cfg["criteria"]["ladder"], fu["criteria"]["f1"]["temporal_lag"]
torch.set_num_threads(4)
os.makedirs("results/followup", exist_ok=True)
for s in fu["seeds"]:
    frames, split = load_frames(f"data/handshake/seed{s}")
    e = ev.aligned(f"data/handshake/seed{s}")["E"]
    pipe = Pipeline(frames[split == 0], cfg, s)
    zw = pipe.whiten(pipe.latent(frames)); d = zw.shape[-1]
    main = tl.run_ladder(zw[split == 0], lad["lags"], lad["gamma_min"], lad["b2_quantile"], False, s, s1_chance_fraction=lad["s1_chance_fraction"])
    q_main = tl.apply_psi(zw, tl.fit_psi(zw[split == 0], main["core"]))
    ru, rv = tl.lag_pairs(zw[split == 0], lag)
    delta = torch.from_numpy(ru - rv).double()
    vals, vecs = eig_desc(delta.T @ delta / len(delta))
    w = vecs[:, -1].numpy()                                         # slowest direction, no release information
    proj = zw @ w; tr = proj[split == 0]
    q_t = ((proj - tr.mean()) / tr.std())[..., None]
    rec = {"seed": s, "main_abs_spearman": ev.naming(q_main[split == 2], e[split == 2]), "temporal_only_abs_spearman": ev.naming(q_t[split == 2], e[split == 2]),
           "main_icc_test": qa.icc(q_main[split == 2]), "temporal_only_icc_test": qa.icc(q_t[split == 2]), "temporal_only_lambda_min_over_chance": float(vals[-1]) / 2.0,
           "handshake_main_abs_spearman": json.load(open(f"results/handshake/main/{s}.json"))["arms"]["main"]["naming_abs_spearman"]}
    rec["gap"] = rec["main_abs_spearman"] - rec["temporal_only_abs_spearman"]
    with open(f"results/followup/{s}.json", "x") as f:
        json.dump(rec, f, indent=1)
    print(rec, flush=True)
