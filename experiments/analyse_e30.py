"""E30: prospective test of the presence-threshold claim (2) and the previous-rung claim (3) on fresh seeds 45-54, cells A and B.
    python experiments/analyse_e30.py -> results/enc_generality/E30_REPORT.md   (rule written before the runs)"""
import glob, hashlib, json
import yaml
from isj.stage_b1 import seed_checks

L = yaml.safe_load(open("configs/layered_v2.yaml"))
assert hashlib.sha256(json.dumps(L, sort_keys=True).encode()).hexdigest() == open("configs/layered_v2.sha256").read().strip(), "layered_v2 changed after freezing"
P = L["presence"]["present_min"]
crit = yaml.safe_load(open("configs/stage_b1.yaml"))["criteria"]
rows = []
for cell in ("A", "B"):
    for f in sorted(glob.glob(f"results/stage_b1_e30/{cell}/main_seed*.json")):
        r = json.load(open(f)); c = seed_checks(r, crit)
        s = [c[f"rung{k}_angle"] and c[f"rung{k}_variant_r2"] and c[f"rung{k}_gap"] for k in (1, 2)]
        for k in (1, 2): rows.append((cell, r["seed"], k, r["presence"]["mlp"][k - 1], s[k - 1], True if k == 1 else s[0]))
hi = [x for x in rows if x[3] >= P]; lo = [x for x in rows if x[3] < P]; dist = [x for x in hi if not x[5]]
a2 = sum(x[4] for x in lo) == 0; b2 = bool(hi) and sum(x[4] for x in hi) / len(hi) >= 0.9
agree = sum(((x[3] >= P) and x[5]) == x[4] for x in rows); a3 = bool(rows) and agree / len(rows) >= 0.95; b3 = sum(x[4] for x in dist) == 0
inf2 = len(hi) >= 3 and len(lo) >= 3; inf3 = len(dist) >= 3
v2 = "NOT INFORMATIVE" if not inf2 else ("CONFIRMED" if a2 and b2 else "REFUTED")
v3 = "NOT INFORMATIVE" if not inf3 else ("CONFIRMED" if a3 and b3 else "REFUTED")
md = [f"# E30: prospective test of the presence threshold (claim 2) and the previous-rung rule (claim 3), seeds 45-54, cells A and B ({len(rows)} rungs)\n",
      f"**Claim 2 (2a: no rung below {P} splits; 2b: at least 90% of rungs at or above {P} split): {v2}.** Rungs below {P}: {len(lo)} (split: {sum(x[4] for x in lo)}); rungs at or above: {len(hi)} (split: {sum(x[4] for x in hi)}).",
      f"**Claim 3 (3a: the conditional rule agrees on at least 95% of rungs; 3b: no distinguishing rung splits): {v3}.** Agreement {agree} of {len(rows)}; distinguishing rungs (presence at least {P}, previous rung failed): {len(dist)} (split: {sum(x[4] for x in dist)}).\n",
      "| Cell | Seed | Rung | Presence | Previous rung split | Split |", "|---|---|---|---|---|---|"]
md += [f"| {x[0]} | {x[1]} | {x[2]} | {x[3]:.3f} | {'yes' if x[5] else 'no'} | {'yes' if x[4] else 'no'} |" for x in rows]
open("results/enc_generality/E30_REPORT.md", "w").write("\n".join(md) + "\n"); print("\n".join(md[:5]))
