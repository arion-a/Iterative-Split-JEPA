"""E29 analysis: prospective test of the presence threshold 0.95 (D15a candidate) on fresh seeds 35-44 of the E28 cell.
    python experiments/analyse_e29.py -> results/enc_generality/E29_REPORT.md   (rule written before the runs)"""
import glob, hashlib, json
import yaml
from isj.stage_b1 import seed_checks

L = yaml.safe_load(open("configs/layered_v2.yaml"))
assert hashlib.sha256(json.dumps(L, sort_keys=True).encode()).hexdigest() == open("configs/layered_v2.sha256").read().strip(), "layered_v2 changed after freezing"
P, A = L["presence"]["present_min"], L["presence"]["absent_max"]
crit = yaml.safe_load(open("configs/stage_b1.yaml"))["criteria"]
R = sorted((json.load(open(f)) for f in glob.glob("results/stage_b1_e29/main_seed*.json")), key=lambda r: r["seed"])
rows = []
for r in R:
    c = seed_checks(r, crit)
    for k in (1, 2):
        rows.append((r["seed"], k, r["presence"]["mlp"][k - 1], r["rungs"][k - 1]["gap_ratio"], r["rungs"][k - 1]["angle_deg"], c[f"rung{k}_angle"] and c[f"rung{k}_variant_r2"] and c[f"rung{k}_gap"]))
hi = [x for x in rows if x[2] >= P]; mid = [x for x in rows if A <= x[2] < P]
v1 = [x for x in hi if not x[5]]; v2 = [x for x in mid if x[5]]
informative = len(hi) >= 3 and len(mid) >= 3
verdict = "REFUTED" if (v1 or v2) else ("CONFIRMED" if informative else "NOT INFORMATIVE FOR ONE SIDE (no violation)")
md = ["# E29: prospective test of the presence threshold 0.95 (D15a candidate), fresh seeds 35-44, MLP + paper objective, weight 0.01\n",
      f"**E29 prediction ((i) every rung with presence at least {P} is SPLIT; (ii) no rung with presence in [{A}, {P}) is SPLIT): {verdict}.** "
      f"Rungs at or above {P}: {len(hi)} (not split: {len(v1)}); rungs in [{A}, {P}): {len(mid)} (split: {len(v2)}); runs: {len(R)}.\n",
      "| Seed | Rung | Presence | Gap ratio | Angle (deg) | Split |", "|---|---|---|---|---|---|"]
md += [f"| {x[0]} | {x[1]} | {x[2]:.3f} | {x[3]:.1f} | {x[4]:.1f} | {'yes' if x[5] else 'no'} |" for x in rows]
open("results/enc_generality/E29_REPORT.md", "w").write("\n".join(md) + "\n"); print("\n".join(md[:3]))
