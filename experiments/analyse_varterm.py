"""E42: the variance term on each family's own block. Rule from configs/varterm.criteria.yaml, frozen by hash before any run.
    python experiments/analyse_varterm.py -> results/minimal/VARTERM_REPORT.md"""
import glob, hashlib, json
import yaml

C = yaml.safe_load(open("configs/varterm.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/varterm.criteria.sha256").read().strip(), "criteria changed after freezing"
T = C["thresholds"]
load = lambda folder: {r["seed"]: r for r in (json.load(open(f)) for f in glob.glob(f"{folder}/main_seed*.json"))}
X, B, I = load(C["folder"]), load(C["references"]["e40_baseline"]), load(C["references"]["e40_invariance_only"])
good = lambda r: all(p >= T["presence_min"] for p in r["presence"]["mlp"]) and all(g["angle_deg"] < T["angle_max_deg"] and g["gap_ratio"] > T["gap_min"] for g in r["rungs"])
n = sum(good(r) for r in X.values()); ni = sum(good(r) for r in I.values())
v = "INCOMPLETE" if len(X) < len(C["seeds"]) else ("CONFIRMED" if n >= C["min_seeds"] else "REFUTED")
tex = lambda D: sum(r["presence"]["mlp"][0] >= T["presence_min"] for r in D.values())
md = [f"# E42: the variance term on each family's own block; frozen criteria `configs/varterm.criteria.yaml`\n",
      f"**E42: {v}.** With the invariance term plus the variance term: all presences at least {T['presence_min']} and both rungs clean on {n} of {len(X)} seeds (needs {C['min_seeds']}); texture presence at least {T['presence_min']} on {tex(X)} of {len(X)}. Invariance term only (E40, same seeds): {ni} of {len(I)}, texture present on {tex(I)}. Baseline: texture present on {tex(B)} of {len(B)}.\n",
      "| Seed | Baseline presence | Invariance only presence | + variance term presence | + variance term angles | + variance term gaps |", "|---|---|---|---|---|---|"]
f3 = lambda r: ", ".join(f"{p:.2f}" for p in r["presence"]["mlp"])
for s in sorted(X):
    r = X[s]
    md.append(f"| {s} | {f3(B[s])} | {f3(I[s])} | {f3(r)} | " + ", ".join(f"{g['angle_deg']:.1f}" for g in r["rungs"]) + " | " + ", ".join(f"{g['gap_ratio']:.1f}" for g in r["rungs"]) + " |")
open("results/minimal/VARTERM_REPORT.md", "w").write("\n".join(md) + "\n"); print("\n".join(md[:3]))
