"""E43: whitening constraint enforced + longer training. Rule from configs/whiten.criteria.yaml, frozen by hash before any run.
    python experiments/analyse_whiten.py -> results/minimal/WHITEN_REPORT.md"""
import glob, hashlib, json
import yaml

C = yaml.safe_load(open("configs/whiten.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/whiten.criteria.sha256").read().strip(), "criteria changed after freezing"
T = C["thresholds"]
load = lambda folder: {r["seed"]: r for r in (json.load(open(f)) for f in glob.glob(f"{folder}/main_seed*.json"))}
X = load(C["folder"]); R = {k: load(v) for k, v in C["references"].items()}
good = lambda r: all(p >= T["presence_min"] for p in r["presence"]["mlp"]) and all(g["angle_deg"] < T["angle_max_deg"] and g["gap_ratio"] > T["gap_min"] for g in r["rungs"])
n = sum(good(r) for r in X.values())
v = "INCOMPLETE" if len(X) < len(C["seeds"]) else ("CONFIRMED" if n >= C["min_seeds"] else "REFUTED")
tex = lambda D: sum(r["presence"]["mlp"][0] >= T["presence_min"] for r in D.values())
f3 = lambda r: ", ".join(f"{p:.2f}" for p in r["presence"]["mlp"])
md = ["# E43: whitening constraint enforced, 30,000 steps; frozen criteria `configs/whiten.criteria.yaml`\n",
      f"**E43: {v}.** All presences at least {T['presence_min']} and both rungs clean on {n} of {len(X)} seeds (needs {C['min_seeds']}); texture presence at least {T['presence_min']} on {tex(X)} of {len(X)}. References (same seeds): baseline {tex(R['e40_baseline'])}, invariance only {tex(R['e40_invariance_only'])}, variance hinge {tex(R['e42_variance_hinge'])} of 10 with texture present.\n",
      "| Seed | Baseline | Invariance only | Variance hinge (E42) | E43 presence | E43 angles | E43 gaps |", "|---|---|---|---|---|---|---|"]
for s in sorted(X):
    r = X[s]
    md.append(f"| {s} | {f3(R['e40_baseline'][s])} | {f3(R['e40_invariance_only'][s])} | {f3(R['e42_variance_hinge'][s])} | {f3(r)} | " + ", ".join(f"{g['angle_deg']:.1f}" for g in r["rungs"]) + " | " + ", ".join(f"{g['gap_ratio']:.1f}" for g in r["rungs"]) + " |")
open("results/minimal/WHITEN_REPORT.md", "w").write("\n".join(md) + "\n"); print("\n".join(md[:3]))
