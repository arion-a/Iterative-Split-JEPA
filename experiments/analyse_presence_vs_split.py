"""Descriptive look (Phase D of docs/PLAN_ENCODER_GENERALITY.md, retrospective, no new claim): across all E25-E28 runs, how does the
presence of the block a rung splits off relate to whether that rung split?
    python experiments/analyse_presence_vs_split.py -> results/enc_generality/PRESENCE_VS_SPLIT.md"""
import glob, json, statistics as st
import yaml
from isj.stage_b1 import seed_checks

crit = yaml.safe_load(open("configs/stage_b1.yaml"))["criteria"]
SETS = {"E25 MLP+prediction, speeds 0.2/0.7/0.95": "results/stage_b1_e25", "E26 MLP+prediction, equal speeds": "results/stage_b1_e26",
        "E27 mirror+paper": "results/stage_b1_e27/mirror_lejepa", "E27 mirror+prediction": "results/stage_b1_e27/mirror_predict",
        "E27 MLP+paper (collapsed, weight 1e-6)": "results/stage_b1_e27/mlp_lejepa", "E28 MLP+paper, weight 0.01": "results/stage_b1_e28"}
rows = []
for lab, d in SETS.items():
    for f in sorted(glob.glob(d + "/main_seed*.json")):
        r = json.load(open(f)); c = seed_checks(r, crit)
        for k in (1, 2):
            sep = c[f"rung{k}_angle"] and c[f"rung{k}_variant_r2"] and c[f"rung{k}_gap"]
            rows.append((lab, r["seed"], k, r["presence"]["mlp"][k - 1], r["rungs"][k - 1]["gap_ratio"], r["rungs"][k - 1]["angle_deg"], sep))
split = [x for x in rows if x[6]]; nots = [x for x in rows if not x[6] and x[3] >= 0.5]
md = ["# Presence versus splitting across E25-E28 (retrospective, descriptive)\n",
      f"Rungs examined: {len(rows)} ({len(split)} split, {len(nots)} not split although the block is at least partly present (presence >= 0.5), {len(rows)-len(split)-len(nots)} absent).\n",
      f"- Lowest presence among rungs that split: **{min(x[3] for x in split):.3f}** (n = {len(split)}).",
      f"- Highest presence among rungs that did not split but are at least partly present: **{max(x[3] for x in nots):.3f}** (n = {len(nots)}).",
      "- Reading: if the first number is above the second, a presence level separates them in these runs. The registered presence threshold (0.9, D15) lies below that level, so a block at 0.90-0.95 can be 'present' and still not split. This is read off the data after the fact and is not a new criterion; see the plan's 'Noted, not started'.\n",
      "| Set | Seed | Rung | Presence of the block (nonlinear probe) | Gap ratio | Angle (deg) | Split |", "|---|---|---|---|---|---|---|"]
for x in sorted(rows, key=lambda x: (x[0], x[1], x[2])):
    if x[3] >= 0.5: md.append(f"| {x[0]} | {x[1]} | {x[2]} | {x[3]:.3f} | {x[4]:.1f} | {x[5]:.1f} | {'yes' if x[6] else 'no'} |")
open("results/enc_generality/PRESENCE_VS_SPLIT.md", "w").write("\n".join(md) + "\n"); print("\n".join(md[:8]))
