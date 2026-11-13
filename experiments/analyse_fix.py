"""E45: whitening scale fixed, 4 and 5 blocks. Rules from configs/fix.criteria.yaml, frozen by hash before any run.
    python experiments/analyse_fix.py -> results/minimal/FIX_REPORT.md"""
import glob, hashlib, json
import yaml

C = yaml.safe_load(open("configs/fix.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/fix.criteria.sha256").read().strip(), "criteria changed after freezing"
T = C["thresholds"]
ok = lambda g: g["angle_deg"] < T["angle_max_deg"] and g["gap_ratio"] > T["gap_min"]
load = lambda folder: sorted((json.load(open(f)) for f in glob.glob(f"{folder}/main_seed*.json")), key=lambda r: r["seed"])
md, lines_ok, failing = [], True, []
for K, folder in C["depths"].items():
    R = load(folder); B = load(f"{C['references']['e44_before_fix']}/d{K}"); n = len(R)
    complete = n >= len(C["seeds"])
    rung = [sum(ok(r["rungs"][i]) for r in R) for i in range(K - 1)]
    health = sum(r["output_cov_min_eig"] >= T["health_min_eig"] for r in R)
    core = sum(r["presence"]["mlp"][-1] >= T["presence_min"] for r in R)
    h_b = sum(r["output_cov_min_eig"] >= T["health_min_eig"] for r in B); c_b = sum(r["presence"]["mlp"][-1] >= T["presence_min"] for r in B)
    r_b = [sum(ok(r["rungs"][i]) for r in B) for i in range(K - 1)]
    p = {"rung": complete and all(c >= 7 for c in rung), "health": complete and health >= 9, "core": complete and core >= 7}
    for k, v in p.items():
        if not v: failing.append(f"depth {K}: {k}")
    lines_ok &= all(p.values())
    md += [f"## {K} blocks: rung line {'met' if p['rung'] else 'NOT met'}, health line {'met' if p['health'] else 'NOT met'}, core line {'met' if p['core'] else 'NOT met'}",
           f"After the fix ({n} seeds): clean rungs by rung index {rung} (needs 7); output covariance healthy (min eigenvalue at least {T['health_min_eig']}) on {health} (needs 9); last-block presence at least {T['presence_min']} on {core} (needs 7). Before the fix (E44, same seeds): clean rungs {r_b}; healthy on {h_b}; core present on {c_b}.\n",
           "| Seed | Angles per rung | Gap ratios | Presence per block | Min output-covariance eigenvalue |", "|---|---|---|---|---|"]
    md += [f"| {r['seed']} | " + ", ".join(f"{g['angle_deg']:.1f}" for g in r["rungs"]) + " | " + ", ".join(f"{g['gap_ratio']:.0f}" for g in r["rungs"]) + " | " + ", ".join(f"{q:.2f}" for q in r["presence"]["mlp"]) + f" | {r['output_cov_min_eig']:.3f} |" for r in R] + [""]
v = "CONFIRMED" if lines_ok else "REFUTED" + (f" (failing: {', '.join(failing)})" if failing else "")
head = ["# E45: whitening scale fixed (plain sums), 4 and 5 blocks; frozen criteria `configs/fix.criteria.yaml`\n", f"**E45: {v}**\n"]
open("results/minimal/FIX_REPORT.md", "w").write("\n".join(head + md) + "\n"); print("\n".join(head))
