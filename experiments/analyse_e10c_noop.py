"""E10c (no collateral damage) and the Tier 1 no-op control, from results/stage_b2_noop/ (+ cross-check against results/stage_b2_purify/).
Criteria are the ones registered in docs/EVIDENCE.md before the run. Writes results/stage_b2_noop/REPORT.md."""
import glob, json, math, statistics as st, torch
from isj.audits import principal_angles_deg

D = "results/stage_b2_noop"
runs = sorted((json.load(open(f)) for f in glob.glob(f"{D}/sigma_cat_0.1/[0-9]*.json")), key=lambda r: r["seed"])
prev = {r["seed"]: r for r in (json.load(open(f)) for f in glob.glob("results/stage_b2_purify/sigma_cat_0.1/[0-9]*.json"))}
ms = lambda v, nd=3: f"{st.mean(v):.{nd}f} ± {st.stdev(v):.{nd}f}"
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
yn = lambda b: "yes" if b else "**NO**"

# reproducibility: untreated arms must equal the E10a run
repro = all(abs(r["arms"][a][k] - prev[r["seed"]]["arms"][a][k]) < 1e-6 for r in runs for a in ("b1_generator", "b2_kmeans", "b2_kmeans_purified", "b2_kmeans_purified_whitened")
            for k in ("angle_deg", "gap_ratio", "variant_r2", "nesting_angle_deg"))

# ---- E10c: worse-than-untreated by more than 1 untreated std = damage (lower is better: True)
METRICS = [("Rung-2 angle (°)", "angle_deg", True), ("Identity R²", "variant_r2", False), ("Category core R²", "core_invariant_r2", False),
           ("Nesting, D10 reference (°)", "nesting_perp_deg", True), ("Nesting, absolute (°) (informational)", "nesting_angle_deg", True),
           ("Block purity", "block_purity", False), ("a12_fro", "a12_fro", True)]
rows, ok_all = [], True
for treated in ("b2_kmeans_purified", "b2_kmeans_purified_whitened"):
    for label, k, lower_better in METRICS:
        u, t = [r["arms"]["b2_kmeans"][k] for r in runs], [r["arms"][treated][k] for r in runs]
        delta = st.mean(t) - st.mean(u)
        worse = delta if lower_better else -delta
        ok = worse <= st.stdev(u)
        if "informational" not in label: ok_all &= ok
        rows.append([treated, label, ms(u), ms(t), f"{delta:+.4f}", f"{st.stdev(u):.4f}", "better" if worse < 0 else "worse", yn(ok)])
pos = []
for r in runs:
    a, b, c = (torch.tensor(r["arms"][x]["V"]).T for x in ("b2_kmeans", "b2_kmeans_purified", "b2_kmeans_purified_whitened"))
    pos.append([r["seed"], f"{principal_angles_deg(a, b).max():.2f}", f"{principal_angles_deg(a, c).max():.2f}"])

# ---- no-op control
nc = [r["noop_control"] for r in runs]
base, pur = "b1_generator", "b1_generator_purified"
CM = [("Rung-2 angle (°)", "angle_deg"), ("Gap ratio, rung 2", "gap_ratio"), ("Identity R²", "variant_r2"), ("Category core R²", "core_invariant_r2"),
      ("Nesting, D10 reference (°)", "nesting_perp_deg"), ("a21_fro", "a21_fro")]
ctl_rows = [[l, ms([r["arms"][base][k] for r in runs]), ms([r["arms"][pur][k] for r in runs]),
             f"{max(abs(r['arms'][pur][k] - r['arms'][base][k]) for r in runs):.4f}"] for l, k in CM]
strict = all(n["n_trimmed"] == 0 for n in nc) and all(r["arms"][pur][k] == r["arms"][base][k] for r in runs for _, k in CM)
frac = max(n["trimmed_fraction"] for n in nc)
practical = frac <= 0.02 and all(abs(r["arms"][pur][k] - r["arms"][base][k]) <= (st.stdev([x["arms"][base][k] for x in runs])) for r in runs for _, k in CM)

md = ["# E10c and no-op control: Tier 1 purification, clean world (sigma_cat 0.1), 3 seeds\n",
      f"Untreated and treated arms reproduce the E10a run exactly: {'yes' if repro else '**NO**'}.\n",
      f"**E10c verdict:** {'CONFIRMED' if ok_all else 'REFUTED'} (criterion: no metric worse than untreated by more than 1 untreated seed-std; fixed in docs/EVIDENCE.md after the E10a numbers were seen, so not blind).\n",
      f"**No-op control verdict:** strict reading (nothing trimmed, results identical): **{'PASS' if strict else 'FAIL'}**. Practical reading (≤ 2% trimmed, every metric within one seed-std of the unpurified B1 arm): **{'PASS' if practical else 'FAIL'}**. Which reading is the gate is the owner's call.\n",
      "## E10c: treated vs untreated B2 arm (means over 3 seeds)\n", tab(["Treated arm", "Metric", "Untreated", "Treated", "Δ", "Untreated seed-std", "Direction", "No damage?"], rows),
      "\n### Position: largest angle between the untreated and the treated rung-2 variant subspace (°)\n", tab(["Seed", "Tier 1", "Tier 1 + Tier 4"], pos),
      "\n## No-op control: Tier 1 on B1's clean generator-twin pairs\n", tab(["Seed", "Pairs", "Trimmed", "Trimmed fraction", "Iterations"], [[r["seed"], n["n_pairs"], n["n_trimmed"], f"{n['trimmed_fraction']:.4f}", n["iterations"]] for r, n in zip(runs, nc)]),
      "\n", tab(["Metric", "B1 arm, unpurified", "B1 arm, Tier 1", "Largest per-seed change"], ctl_rows)]
open(f"{D}/REPORT.md", "w").write("\n".join(md))
print("repro", repro, "E10c", ok_all, "noop strict", strict, "practical", practical, "trim frac max", round(frac, 4))
