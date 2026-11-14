"""E53: the invertible encoder at 3x the steps on the four failing E52 seeds. Rule from configs/inv_long.criteria.yaml, frozen by hash before the runs.
    python experiments/analyse_inv_long.py -> results/minimal/INV_LONG_REPORT.md"""
import glob, hashlib, json
import yaml

C = yaml.safe_load(open("configs/inv_long.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/inv_long.criteria.sha256").read().strip(), "criteria changed after freezing"
T = C["thresholds"]; ok = lambda g: g["angle_deg"] < T["angle_max_deg"] and g["gap_ratio"] > T["gap_min"]
load = lambda folder: {r["seed"]: r for r in (json.load(open(f)) for f in glob.glob(f"{folder}/main_seed*.json"))}
L, S = load(C["folder"]), load("results/minimal/e52/d4")
n = sum(all(ok(g) for g in L[s]["rungs"]) for s in C["seeds"] if s in L)
v = "INCOMPLETE" if len(L) < len(C["seeds"]) else ("CONFIRMED (too few steps was the cause)" if n >= C["min_seeds"] else "REFUTED (more steps did not fix it)")
f = lambda r: "angles " + ", ".join(f"{g['angle_deg']:.1f}" for g in r["rungs"]) + "; gaps " + ", ".join(f"{g['gap_ratio']:.0f}" for g in r["rungs"])
md = [f"# E53: the invertible encoder at 90,000 steps (E52 failing seeds); frozen criteria `configs/inv_long.criteria.yaml`\n", f"**E53: {v}.** Every rung clean on {n} of {len(L)} seeds (needs {C['min_seeds']}; at 30,000 steps: 0 of 4).\n", "| Seed | 30,000 steps (E52) | 90,000 steps |", "|---|---|---|"]
md += [f"| {s} | {f(S[s])} | {f(L[s])} |" for s in C["seeds"] if s in L]
open("results/minimal/INV_LONG_REPORT.md", "w").write("\n".join(md) + "\n"); print(f"E53: {v}")
