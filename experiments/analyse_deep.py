"""E44: more rungs with the generic MLP. Rule from configs/deep.criteria.yaml, frozen by hash before any run.
    python experiments/analyse_deep.py -> results/minimal/DEEP_REPORT.md"""
import glob, hashlib, json
import yaml

C = yaml.safe_load(open("configs/deep.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/deep.criteria.sha256").read().strip(), "criteria changed after freezing"
T = C["thresholds"]; need = 7
ok = lambda g: g["angle_deg"] < T["angle_max_deg"] and g["gap_ratio"] > T["gap_min"]
md, verdict, first_bad = [], True, None
for K, folder in C["depths"].items():
    R = sorted((json.load(open(f)) for f in glob.glob(f"{folder}/main_seed*.json")), key=lambda r: r["seed"])
    n = len(R); per = [sum(ok(r["rungs"][i]) for r in R) for i in range(K - 1)]
    both = sum(all(ok(g) for g in r["rungs"]) for r in R)
    good = n >= len(C["seeds"]) and all(c >= need for c in per)
    verdict &= good
    if not good and first_bad is None and n >= len(C["seeds"]): first_bad = (K, 1 + next(i for i, c in enumerate(per) if c < need))
    md += [f"## {K} blocks ({K-1} rungs): {'pass' if good else 'not met'}", f"Clean rungs by rung index (needs {need} of {n}): " + ", ".join(f"rung {i+1}: {c}" for i, c in enumerate(per)) + f"; every rung clean on {both} of {n} seeds.\n",
           "| Seed | Angles per rung | Gap ratios | Presence per block | Min output-covariance eigenvalue |", "|---|---|---|---|---|"]
    md += [f"| {r['seed']} | " + ", ".join(f"{g['angle_deg']:.1f}" for g in r["rungs"]) + " | " + ", ".join(f"{g['gap_ratio']:.0f}" for g in r["rungs"]) + " | " + ", ".join(f"{p:.2f}" for p in r["presence"]["mlp"]) + f" | {r.get('output_cov_min_eig', float('nan')):.3f} |" for r in R] + [""]
head = ["# E44: more rungs with the generic MLP (E43 recipe); frozen criteria `configs/deep.criteria.yaml`\n", f"**E44: {'CONFIRMED' if verdict else 'REFUTED'}**" + ("" if verdict or first_bad is None else f" (first rung below the level: depth {first_bad[0]}, rung {first_bad[1]})") + "\n"]
open("results/minimal/DEEP_REPORT.md", "w").write("\n".join(head + md) + "\n"); print("\n".join(head))
