"""Descriptive look (Phase D of docs/PLAN_ENCODER_GENERALITY.md, retrospective, no new claim): across all E25-E28 runs, how does the
presence of the block a rung splits off relate to whether that rung split?
    python experiments/analyse_presence_vs_split.py -> results/enc_generality/PRESENCE_VS_SPLIT.md"""
import glob, json, statistics as st
import yaml
from isj.stage_b1 import seed_checks

crit = yaml.safe_load(open("configs/stage_b1.yaml"))["criteria"]
SETS = {"E25 MLP+prediction, speeds 0.2/0.7/0.95": "results/stage_b1_e25", "E26 MLP+prediction, equal speeds": "results/stage_b1_e26",
        "E27 mirror+paper": "results/stage_b1_e27/mirror_lejepa", "E27 mirror+prediction": "results/stage_b1_e27/mirror_predict",
        "E27 MLP+paper (collapsed, weight 1e-6)": "results/stage_b1_e27/mlp_lejepa", "E28 MLP+paper, weight 0.01": "results/stage_b1_e28", "E29 MLP+paper, weight 0.01, fresh seeds": "results/stage_b1_e29"}
rows = []
for lab, d in SETS.items():
    for f in sorted(glob.glob(d + "/main_seed*.json")):
        r = json.load(open(f)); c = seed_checks(r, crit)
        for k in (1, 2):
            sep = c[f"rung{k}_angle"] and c[f"rung{k}_variant_r2"] and c[f"rung{k}_gap"]
            rows.append((lab, r["seed"], k, r["presence"]["mlp"][k - 1], r["rungs"][k - 1]["gap_ratio"], r["rungs"][k - 1]["angle_deg"], sep))
split = [x for x in rows if x[6]]; nots = [x for x in rows if not x[6] and x[3] >= 0.5]
md = ["# Presence versus splitting across E25-E29 (retrospective, descriptive)\n",
      f"Rungs examined: {len(rows)} ({len(split)} split, {len(nots)} not split although the block is at least partly present (presence >= 0.5), {len(rows)-len(split)-len(nots)} absent).\n",
      f"- Lowest presence among rungs that split: **{min(x[3] for x in split):.3f}** (n = {len(split)}).",
      f"- Highest presence among rungs that did not split but are at least partly present: **{max(x[3] for x in nots):.3f}** (n = {len(nots)}).",
      "- Reading: when the first number is above the second, presence alone separates split from not split; when they overlap, it does not. The conditional rule (a rung splits when its block presence is at least the threshold AND the previous rung split) is tested below. All of this is read off the data after the fact and is not a criterion; E29 (fresh seeds) tested the unconditional 0.95 version prospectively.\n",
      "| Set | Seed | Rung | Presence of the block (nonlinear probe) | Gap ratio | Angle (deg) | Split |", "|---|---|---|---|---|---|---|"]
for x in sorted(rows, key=lambda x: (x[0], x[1], x[2])):
    if x[3] >= 0.5: md.append(f"| {x[0]} | {x[1]} | {x[2]} | {x[3]:.3f} | {x[4]:.1f} | {x[5]:.1f} | {'yes' if x[6] else 'no'} |")
# ---- conditional rule (descriptive): a rung splits iff its block presence is at least 0.95 AND the previous rung split
bysplit = {(x[0], x[1], x[2]): x for x in rows}
def predict(x, thr):
    lab, seed, k = x[0], x[1], x[2]
    return x[3] >= thr and (k == 1 or bysplit[(lab, seed, 1)][6])
for thr in (0.9, 0.95):
    ok_unc = sum((x[3] >= thr) == x[6] for x in rows); ok_con = sum(predict(x, thr) == x[6] for x in rows)
    md.insert(next(i for i, l in enumerate(md) if l.startswith("| Set")), f"- Rule at presence threshold {thr}: block presence alone explains {ok_unc} of {len(rows)} rungs; presence AND previous rung split explains {ok_con} of {len(rows)}.\n" if thr == 0.95 else f"- Rule at presence threshold {thr}: block presence alone explains {ok_unc} of {len(rows)} rungs; presence AND previous rung split explains {ok_con} of {len(rows)}.")
open("results/enc_generality/PRESENCE_VS_SPLIT.md", "w").write("\n".join(md) + "\n"); print("\n".join(md[:8]))
