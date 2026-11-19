"""E54: the invertible coupling encoder with the paper objective, 4 and 5 blocks. Rules from configs/inv_paper.criteria.yaml, frozen by hash before any run.
    python experiments/analyse_inv.py -> results/minimal/INV_PAPER_REPORT.md"""
import glob, hashlib, json
import yaml

C = yaml.safe_load(open("configs/inv_paper.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/inv_paper.criteria.sha256").read().strip(), "criteria changed after freezing"
T = C["thresholds"]; need = C["min_seeds"]
load = lambda folder: sorted((json.load(open(f)) for f in glob.glob(f"{folder}/main_seed*.json")), key=lambda r: r["seed"])
ok = lambda g: g["angle_deg"] < T["angle_max_deg"] and g["gap_ratio"] > T["gap_min"]
md, all_ok, failing = [], True, []
for K, folder in C["depths"].items():
    R = load(folder); n = len(R); K = int(K); complete = n >= len(C["seeds"])
    pres = [sum(r["presence"]["mlp"][b] >= T["presence_min"] for r in R) for b in range(K)]
    rung = [sum(ok(r["rungs"][i]) for r in R) for i in range(K - 1)]
    comp = [sum(r["rungs"][i]["variant_mlp_r2"] / max(r["presence"]["mlp"][i], 1e-6) >= T["completeness_min"] for r in R) for i in range(K - 1)]
    health = sum(r["output_cov_min_eig"] >= T["health_min_eig"] for r in R)
    p = {"presence": complete and all(c >= need for c in pres), "rung": complete and all(c >= need for c in rung), "completeness": complete and all(c >= need for c in comp)}
    failing += [f"depth {K}: {k}" for k, v in p.items() if not v]; all_ok &= all(p.values())
    md += [f"## {K} blocks ({n} seeds): presence line {'met' if p['presence'] else 'NOT met'}, rung line {'met' if p['rung'] else 'NOT met'}, completeness line {'met' if p['completeness'] else 'NOT met'}",
           f"Blocks present (0.95) by block: {pres} (needs {need}); clean rungs by rung: {rung} (needs {need}); complete rungs by rung: {comp} (needs {need}); no dead direction on {health} of {n}.\n",
           "| Seed | Angles per rung | Gaps | Presence per block | Block-from-found-block / whole-embedding readout per rung |", "|---|---|---|---|---|"]
    md += [f"| {r['seed']} | " + ", ".join(f"{g['angle_deg']:.1f}" for g in r["rungs"]) + " | " + ", ".join(f"{g['gap_ratio']:.0f}" for g in r["rungs"]) + " | " + ", ".join(f"{q:.2f}" for q in r["presence"]["mlp"]) + " | " + ", ".join(f"{g['variant_mlp_r2'] / max(q, 1e-6):.2f}" for g, q in zip(r["rungs"], r["presence"]["mlp"])) + " |" for r in R] + [""]
v = "CONFIRMED" if all_ok else "REFUTED (failing: " + ", ".join(failing) + ")"
open("results/minimal/INV_PAPER_REPORT.md", "w").write("\n".join(["# E54: the invertible coupling encoder with the paper objective (E45 recipe); frozen criteria `configs/inv_paper.criteria.yaml`\n", f"**E54: {v}**\n"] + md) + "\n"); print(f"E52: {v}")
