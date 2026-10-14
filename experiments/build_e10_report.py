"""E10 / E10a report (docs/REPORTING.md format) from results/stage_b2_purify/. Nesting gate = D10 (orthogonal-complement reference)."""
import glob, json, os, statistics as st, sys
import yaml
from isj import svgplots as sv
from isj.stage_b1 import seed_checks

OUT = sys.argv[1] if len(sys.argv) > 1 else "results/stage_b2_purify"
LABEL = sys.argv[2] if len(sys.argv) > 2 else "E10 / E12"
NEWGATE = len(sys.argv) > 3 and sys.argv[3] == "gates_v2"   # leakage gate of configs/gates_v2.yaml (D13), effective from the first run after the E17 freeze
LEAK_T = yaml.safe_load(open("configs/gates_v2.yaml"))["leakage_gate"]["threshold"]
crit = yaml.safe_load(open("configs/stage_b1.yaml"))["criteria"]
runs = sorted((json.load(open(f)) for f in glob.glob(f"{OUT}/sigma_cat_0.1/[0-9]*.json")), key=lambda r: r["seed"])
old = sorted((json.load(open(f)) for f in glob.glob("results/stage_b2_nesting/sigma_cat_0.1/[0-9]*.json")), key=lambda r: r["seed"])
ms = lambda v, nd=2: f"{st.mean(v):.{nd}f} ± {st.stdev(v):.{nd}f}" if len(v) > 1 else f"{v[0]:.{nd}f}"
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
yn = lambda b: "yes" if b else "**NO**"
ARMS = [("B1 (generator twins)", "b1_generator"), ("B2 (discovered clusters)", "b2_kmeans"),
        ("B2 + Tier 1 purification", "b2_kmeans_purified"), ("B2 + Tier 1 + Tier 4 (registered treatment)", "b2_kmeans_purified_whitened")]

def view(r, arm, definition="complement"):
    a = dict(r["arms"][arm])
    if definition == "complement":
        a["nesting_angle_deg"] = a["nesting_perp_deg"]
    return {"rungs": [r["rung1"], a], "nesting_angle_deg": a["nesting_angle_deg"], "core_invariant_r2": a["core_invariant_r2"]}

GATES = [("Rung 1 angle (texture)", "below 5°", "rung1_angle", lambda v: v["rungs"][0]["angle_deg"], 2),
         ("Rung 2 angle (identity)", "below 5°", "rung2_angle", lambda v: v["rungs"][1]["angle_deg"], 2),
         ("Texture R² (variant R², rung 1)", "above 0.9", "rung1_variant_r2", lambda v: v["rungs"][0]["variant_r2"], 3),
         ("Identity R² (variant R², rung 2)", "above 0.9", "rung2_variant_r2", lambda v: v["rungs"][1]["variant_r2"], 3),
         ("Category core R² (invariant R²)", "above 0.9", "core_invariant_r2", lambda v: v["core_invariant_r2"], 3),
         ("Nesting angle, D10 definition (orthogonal-complement reference)", "below 5°", "nesting", lambda v: v["nesting_angle_deg"], 2),
         ("Gap ratio, rung 1", "above 10", "rung1_gap", lambda v: v["rungs"][0]["gap_ratio"], 1),
         ("Gap ratio, rung 2", "above 10", "rung2_gap", lambda v: v["rungs"][1]["gap_ratio"], 1),
         ("Leakage, normalized ||A21|| at both rungs (gates_v2, D13)" if NEWGATE else "Leakage, largest off-diagonal |R²| (B1 amended rule)", f"below {LEAK_T}" if NEWGATE else "below 0.01", "leakage", (lambda v: max(x["a21_norm"] for x in v["rungs"])) if NEWGATE else (lambda v: max(x["max_leak_abs_r2"] for x in v["rungs"])), 4),
         ("Rank check (statistical test)", "passes", "rank_test", lambda v: float(not any(x["rank_deficient"] for x in v["rungs"])), 0)]

def gate_table(arm):
    vs = [view(r, arm) for r in runs]; rows = []
    for label, need, key, f, nd in GATES:
        vals = [f(v) for v in vs]
        rows.append([label, need, f"{sum(vals):.0f} of {len(vals)} seeds" if key == "rank_test" else ms(vals, nd), yn(all(seed_checks(v, crit)[key] for v in vs))])
    return rows

a = lambda arm, k: [r["arms"][arm][k] for r in runs]
gap_b1, gap_b2, gap_t1, gap_t14 = (st.mean(a(x, "gap_ratio")) for x in ("b1_generator", "b2_kmeans", "b2_kmeans_purified", "b2_kmeans_purified_whitened"))
rec = lambda g: (g - gap_b2) / (gap_b1 - gap_b2)
e10a = rec(gap_t14) >= 0.60
nest_ok = all(r["arms"]["b2_kmeans"]["nesting_perp_deg"] < crit["nesting_angle_max_deg"] for r in runs)

six = [[n] + [ms(a(arm, "global_r2"), 4), ms(a(arm, "invariant_r2"), 4), ms(a(arm, "variant_r2"), 4), ms(a(arm, "a12_fro"), 4), ms(a(arm, "a21_fro"), 4), ms(a(arm, "block_purity"), 5)] for n, arm in ARMS]
six.append(["Paper (single split)", "0.9977", "0.9980", "0.9974", "0.0034", "0.0233", "0.99993"])
head = []
for label, k, nd in (("Rung-2 angle (°)", "angle_deg", 2), ("Identity R²", "variant_r2", 3), ("Category core R²", "core_invariant_r2", 3), ("Gap ratio, rung 2", "gap_ratio", 1), ("Nesting, D10 definition (°)", "nesting_perp_deg", 2)):
    head.append([label] + [ms(a(arm, k), nd) for _, arm in ARMS])
info = [["Nesting, absolute (span truth) (°) - informational diagnostic"] + [ms(a(arm, "nesting_angle_deg")) for _, arm in ARMS]]
pur = [[r["seed"], f"{r['purify']['validity_before']:.3f}", f"{r['purify']['validity_after']:.3f}", f"{r['purify']['kept_fraction']:.3f}", f"{r['purify']['valid_kept']:.3f}",
        f"{r['purify']['invalid_dropped']:.3f}" if r["purify"]["invalid_dropped"] is not None else "n/a", r["purify"]["iterations"], f"{r['quality']['cluster_purity']:.3f}"] for r in runs]
cr = runs; m_a = lambda arm: st.mean(a(arm, "angle_deg"))
ctl = [["C1 cross-cluster pairs", "angle above 10°, validity below 0.95", f"angle {m_a('c1_cross_cluster'):.1f}°", yn(m_a("c1_cross_cluster") > 10)],
       ["C2 clusters from variant block", "angle above 10°", f"angle {m_a('c2_variant_clusters'):.1f}°", yn(m_a("c2_variant_clusters") > 10)],
       ["C3 singleton clusters", "zero valid pairs", f"{st.mean(r['construction']['c3_singleton']['n_pairs'] for r in cr):.0f} pairs", yn(all(r["construction"]["c3_singleton"]["n_pairs"] == 0 for r in cr))],
       ["C4 shuffled membership (recorded)", "none", f"angle {m_a('c4_shuffled'):.1f}°", "recorded"]]
attr = [[r["seed"], f"{r['rung1']['inherited_span_deg']:.2f}", f"{r['rung1']['inherited_perp_deg']:.2f}", f"{r['arms']['b2_kmeans']['nesting_angle_deg']:.2f}", f"{r['arms']['b2_kmeans']['nesting_perp_deg']:.2f}", f"{r['arms']['b2_kmeans']['angle_deg']:.2f}"] for r in runs]
rm = [[n, f"{sum(r['arms'][arm]['rank_monitor']['pass'] for r in runs)} of {len(runs)}"] for n, arm in ARMS]

os.makedirs(f"{OUT}/figures", exist_ok=True)
e = lambda arm: [st.mean(r["arms"][arm]["eigvals"][i] for r in runs) for i in range(8)]
e_b2, e_t = e("b2_kmeans"), e("b2_kmeans_purified_whitened")
open(f"{OUT}/figures/P2prime.svg", "w").write(sv.standalone(sv.log_lines([("B2 untreated", e_b2, "--s1"), ("B2 + Tier 1 + Tier 4", e_t, "--s2")], vline=4, vline_label="selected boundary: 4 | 4", ymin=1e-3, ymax=10,
    note="Pair-difference spectrum at rung 2", annotations=[(5, f"untreated gap {e_b2[3]/e_b2[4]:.1f}", e_b2[4] * 0.32), (5, f"treated gap {e_t[3]/e_t[4]:.1f}", e_t[4] * 2.6)])))
open(f"{OUT}/figures/P5.svg", "w").write(sv.standalone(sv.ladder([st.mean(r["rung1"]["angle_deg"] for r in runs), st.mean(a("b1_generator", "angle_deg"))],
    [st.mean(r["rung1"]["angle_deg"] for r in runs), st.mean(a("b2_kmeans_purified_whitened", "angle_deg"))], st.mean(a("b1_generator", "core_invariant_r2")), st.mean(a("b2_kmeans_purified_whitened", "core_invariant_r2")), note="Ladder: B1 vs treated B2")))
unit = open("results/stage_b2_purify/unit_test_output.txt").read().strip()
md = [f"# {LABEL} report: formal B2, clean world (sigma_cat 0.1), {len(runs)} seeds, hard nesting, pairs 60,000 / 30,000\n",
      f"**Verdict.** E10 (nesting gate on the D10 reference): B2 arm nesting {ms(a('b2_kmeans','nesting_perp_deg'))}°, {'inside' if nest_ok else 'NOT inside'} the 5° gate on every seed; the absolute angle is {ms(a('b2_kmeans','nesting_angle_deg'))}° and is now informational. "
      f"E12: rung-2 gap ratio B1 {gap_b1:.1f}, B2 untreated {gap_b2:.1f}, Tier 1 {gap_t1:.1f}, Tier 1 + Tier 4 {gap_t14:.1f}; recovered fraction of the B1-B2 deficit: Tier 1 {rec(gap_t1):.2f}, Tier 1 + Tier 4 {rec(gap_t14):.2f} (registered treatment; needs ≥ 0.60) -> **{'CONFIRMED' if e10a else 'REFUTED'}**.\n",
      "## A. Gate table (registered treatment: B2 + Tier 1 + Tier 4)\n", tab(["Criterion", "Threshold", "Measured (mean ± std)", "Pass?"], gate_table("b2_kmeans_purified_whitened")),
      "\nSame gates, B2 untreated:\n", tab(["Criterion", "Threshold", "Measured (mean ± std)", "Pass?"], gate_table("b2_kmeans")),
      "\nSame gates, B1 arm (generator twins) on the same encoders:\n", tab(["Criterion", "Threshold", "Measured (mean ± std)", "Pass?"], gate_table("b1_generator")),
      "\n## B. Paper-standard metrics (rung-2 split)\n", tab(["Rung 2 split", "Global R²", "Invariant R²", "Variant R²", "a12_fro", "a21_fro", "Block purity"], six),
      "\n## C. Headline across arms (mean ± std over seeds)\n", tab(["Metric"] + [n for n, _ in ARMS], head + info),
      "\n## Purification (Tier 1) bookkeeping\n", tab(["Seed", "Pair validity before", "after", "Fraction of pairs kept", "Valid pairs kept", "Invalid pairs dropped", "Iterations", "Cluster purity"], pur),
      "\n## Rank-completeness monitor, rung 2\n", tab(["Arm", "Seeds passing"], rm),
      "\n## Controls\n", tab(["Control", "Required outcome", "Observed", "Result"], ctl),
      "\n## Attribution (informational, not a gate)\n", tab(["Seed", "Inherited, span truth (°)", "Inherited, complement truth (°)", "Nesting, span truth (°)", "Nesting, complement truth (°)", "Recovery θ(V₂, identity image) (°)"], attr),
      "\n## Unit-test output (D9)\n```\n" + unit + "\n```\n", "\n## Figures\n![P2prime](figures/P2prime.svg)\n![P5](figures/P5.svg)\n"]
open(f"{OUT}/REPORT.md", "w").write("\n".join(md))
print("built", len(runs), "seeds; recovered T1", round(rec(gap_t1), 2), "T1+T4", round(rec(gap_t14), 2))
