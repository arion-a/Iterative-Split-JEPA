"""Exploratory integrity controls (not registered): the E54 pipeline with (a) an untrained invertible encoder (lr = 0: the identity) and (b) shuffled rung-2 pairs.
    python experiments/diag_controls.py untrained|shuffled DEPTH SEED"""
import sys, json, yaml
from isj.stage_b1 import run_stage_b1
mode, K, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
c = yaml.safe_load(open(f"configs/inv_paper_d{K}.yaml"))
if mode == "untrained":
    c["encoder"]["steps"], c["encoder"]["lr"] = 1, 0.0
r = run_stage_b1(c, seed, control="shuffled_rung2" if mode == "shuffled" else "none")
print(json.dumps({"mode": mode, "K": K, "seed": seed, "angles": [round(g["angle_deg"], 1) for g in r["rungs"]], "gaps": [round(g["gap_ratio"], 1) for g in r["rungs"]],
                  "presence": [round(p, 3) for p in r["presence"]["mlp"]], "completeness": [round(g["variant_mlp_r2"] / max(q, 1e-6), 2) for g, q in zip(r["rungs"], r["presence"]["mlp"])]}))
