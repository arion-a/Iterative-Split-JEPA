"""Re-score the existing B1 runs under the AMENDED leakage rule (decided after seeing the data).

Amended rule (user's ruling, floor proposed by Claude): leakage counts as "at the null" if every
off-diagonal held-out R^2 is below LEAK_FLOOR, whether or not the permutation test fires. Every other
locked criterion is unchanged. The registered verdict under the original strict rule is not altered.
"""
import glob
import json
import sys

import yaml

from isj.stage_b1 import CRITERIA_KEYS, seed_checks

LEAK_FLOOR = float(sys.argv[1]) if len(sys.argv) > 1 else 0.01
cfg = yaml.safe_load(open("configs/stage_b1.yaml"))
c = cfg["criteria"]
files = sorted(glob.glob("runs/stage_b1/r1/main_seed*.json") + glob.glob("runs/stage_b1/more_seeds/main_seed*.json"))
rows, failing = [], {}
for f in files:
    r = json.load(open(f))
    chk = seed_checks(r, c)
    off = [abs(x) for rg in r["rungs"] for k, x in rg["leak_r2"].items() if k in ("rest->own", "own->rest")]
    chk["leakage"] = max(off) < LEAK_FLOOR                      # amended rule
    rows.append({"seed": r["seed"], "max_offdiag_leak_r2": max(off), **chk})
    for k in CRITERIA_KEYS:
        if not chk[k]:
            failing.setdefault(k, []).append(r["seed"])
out = {"rule": f"leakage: every off-diagonal held-out R2 below {LEAK_FLOOR}; other criteria as locked",
       "seeds": [r["seed"] for r in rows], "n_seeds": len(rows), "failing_criteria": failing,
       "max_offdiag_leak_r2_over_all_seeds": max(r["max_offdiag_leak_r2"] for r in rows),
       "reading": "ALL CRITERIA HOLD on every seed" if not failing else "some criteria fail"}
json.dump(out, open("runs/stage_b1/rescore_amended_leakage_rule.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "seeds"}, indent=1))
