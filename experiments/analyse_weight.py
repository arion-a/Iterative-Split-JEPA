"""E35 (Gap 4): regulariser weight. Rules from configs/weight.criteria.yaml, frozen by hash before any run.
    python experiments/analyse_weight.py -> results/stage_b1_e35/WEIGHT_REPORT.md"""
import glob, hashlib, json
import yaml
from isj.stage_b1 import seed_checks

C = yaml.safe_load(open("configs/weight.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/weight.criteria.sha256").read().strip(), "criteria changed after freezing"
P = yaml.safe_load(open("configs/layered_v2.yaml"))["presence"]["present_min"]
crit = yaml.safe_load(open("configs/stage_b1.yaml"))["criteria"]
md, any_q = ["| Weight | Seed | Presence (b1, b2, b3) | Rung 1 split | Rung 2 split | Qualifies |", "|---|---|---|---|---|---|"], False
summ = []
for w in C["weights"]:
    R = sorted((json.load(open(f)) for f in glob.glob(f"results/stage_b1_e35/w{w}/main_seed*.json")), key=lambda r: r["seed"])
    q = 0
    for r in R:
        c, pr = seed_checks(r, crit), r["presence"]["mlp"]
        sp = [c[f"rung{k}_angle"] and c[f"rung{k}_variant_r2"] and c[f"rung{k}_gap"] for k in (1, 2)]
        ok = all(p >= P for p in pr) and all(sp); q += ok
        md.append(f"| {w} | {r['seed']} | {', '.join(f'{p:.3f}' for p in pr)} | {'yes' if sp[0] else 'no'} | {'yes' if sp[1] else 'no'} | {'yes' if ok else 'no'} |")
    good = len(R) >= len(C["seeds"]) and q >= 9; any_q |= good
    summ.append(f"weight {w}: {q} of {len(R)} seeds qualify ({'qualifies' if good else 'does not qualify'}; needs 9 of 10)")
head = [f"# E35 (Gap 4): regulariser weight; frozen criteria `configs/weight.criteria.yaml`\n", f"**E35: {'CONFIRMED' if any_q else 'REFUTED'}.** " + "; ".join(summ) + ". Reference, weight 0.01 (E28/E29): all blocks kept on 6 of 15 seeds.\n"]
open("results/stage_b1_e35/WEIGHT_REPORT.md", "w").write("\n".join(head + md) + "\n"); print("\n".join(head))
