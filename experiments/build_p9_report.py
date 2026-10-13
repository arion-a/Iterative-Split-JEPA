"""P9 report (docs/REPORTING.md format) for the nesting-enforcement confirmation run.
Reads results/stage_b1_nesting/ and results/stage_b2_nesting/ (clean world); compares with the earlier runs (runs/stage_b1/r1, results/B2).
Writes REPORT.md + figures in each results dir. Never edits run files."""
import glob, json, os, statistics as st
import yaml
from isj import svgplots as sv
from isj.stage_b1 import seed_checks

crit = yaml.safe_load(open("configs/stage_b1.yaml"))["criteria"]
clean = yaml.safe_load(open("configs/stage_b2_nesting.yaml"))["sweep"]["clean_sigma_cat"]
L = lambda pat: sorted((json.load(open(f)) for f in glob.glob(pat)), key=lambda r: r["seed"])
b1n = L("results/stage_b1_nesting/main_seed*.json")
b1ctl = {a: L(f"results/stage_b1_nesting/{a}_seed*.json") for a in ("shuffled_rung2", "rank1_rung2", "no_inv", "no_pred", "no_var")}
b2n = L(f"results/stage_b2_nesting/sigma_cat_{clean}/[0-9]*.json")
b1old = L("runs/stage_b1/r1/main_seed*.json")
b2old = L(f"results/B2/sigma_cat_{clean}/[0-9]*.json")
ms = lambda v, nd=2: f"{st.mean(v):.{nd}f} ± {st.stdev(v):.{nd}f}" if len(v) > 1 else f"{v[0]:.{nd}f}"
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
yn = lambda b: "yes" if b else "**NO**"

def b2_as_b1(r, arm):
    a = r["arms"][arm]
    return {"rungs": [r["rung1"], a], "nesting_angle_deg": a["nesting_angle_deg"], "core_invariant_r2": a["core_invariant_r2"]}

GATES = [("Rung 1 angle (texture)", "below 5°", "rung1_angle", lambda r: r["rungs"][0]["angle_deg"], 2),
         ("Rung 2 angle (identity)", "below 5°", "rung2_angle", lambda r: r["rungs"][1]["angle_deg"], 2),
         ("Texture R² (variant R², rung 1)", "above 0.9", "rung1_variant_r2", lambda r: r["rungs"][0]["variant_r2"], 3),
         ("Identity R² (variant R², rung 2)", "above 0.9", "rung2_variant_r2", lambda r: r["rungs"][1]["variant_r2"], 3),
         ("Category core R² (invariant R²)", "above 0.9", "core_invariant_r2", lambda r: r["core_invariant_r2"], 3),
         ("**Nesting angle** (gate definition: span of true identity+category images)", "below 5°", "nesting", lambda r: r["nesting_angle_deg"], 2),
         ("Gap ratio, rung 1", "above 10", "rung1_gap", lambda r: r["rungs"][0]["gap_ratio"], 1),
         ("Gap ratio, rung 2", "above 10", "rung2_gap", lambda r: r["rungs"][1]["gap_ratio"], 1),
         ("Leakage (no significant off-diagonal, B1 rule)", "none", "leakage", lambda r: float(max(x.get("max_leak_abs_r2", 0) for x in r["rungs"])), 4),
         ("Rank check (statistical test)", "passes", "rank_test", lambda r: float(not any(x["rank_deficient"] for x in r["rungs"])), 0)]

def gate_table(rs):
    rows = []
    for label, need, key, f, nd in GATES:
        ok = all(seed_checks(r, crit)[key] for r in rs)
        v = [f(r) for r in rs]
        rows.append([label, need, f"{sum(v):.0f} of {len(v)} seeds" if key == "rank_test" else ms(v, nd), yn(ok)])
    return rows

def b1_view(rs):                       # B1-shaped runs from the B1 re-run
    return rs

def b2_views(rs, arm):
    return [b2_as_b1(r, arm) for r in rs]

def six(rungs):                        # rungs: list of rung dicts (rung-2 split)
    return [ms([a["global_r2"] for a in rungs], 4) if "global_r2" in rungs[0] else "n/a", ms([a["invariant_r2"] if "invariant_r2" in a else a["invariant_content_r2"] for a in rungs], 4),
            ms([a["variant_r2"] for a in rungs], 4), ms([a["a12_fro"] for a in rungs], 4), ms([a["a21_fro"] for a in rungs], 4), ms([a["block_purity"] for a in rungs], 5)]

def rank_rows(rs, getters):
    out = []
    for name, g in getters:
        m = [g(r) for r in rs]
        out.append([name, f"{sum(x['pass'] for x in m)} of {len(m)}", ms([x["lambda_min"] for x in m], 3), ms([x["threshold"] for x in m], 3), m[0]["n_pairs"]])
    return out

def figs(outdir, e_a, e_b, labels, a_b1, a_b2, core):
    os.makedirs(f"{outdir}/figures", exist_ok=True)
    p2 = sv.log_lines([(labels[0], e_a, "--s1"), (labels[1], e_b, "--s2")], vline=4, vline_label="selected boundary: 4 | 4", ymin=1e-3, ymax=10,
                      note="Pair-difference spectrum at rung 2", annotations=[(5, f"{labels[0]} gap {e_a[3]/e_a[4]:.0f}", e_a[4] * 0.32), (5, f"{labels[1]} gap {e_b[3]/e_b[4]:.1f}", e_b[4] * 2.6)])
    p5 = sv.ladder(a_b1, a_b2, core[0], core[1], note="Ladder: nested blocks, angles")
    open(f"{outdir}/figures/P2prime.svg", "w").write(sv.standalone(p2)); open(f"{outdir}/figures/P5.svg", "w").write(sv.standalone(p5))

unit = open("results/stage_b2_nesting/unit_test_output.txt").read().strip()
nest_before_b1 = ms([r["nesting_angle_deg"] for r in b1old]); nest_after_b1 = ms([r["nesting_angle_deg"] for r in b1n])
nest_before_b2 = ms([r["arms"]["b2_kmeans"]["nesting_angle_deg"] for r in b2old]); nest_after_b2 = ms([r["arms"]["b2_kmeans"]["nesting_angle_deg"] for r in b2n])
nest_ms = lambda rs, f: [f(r) for r in rs]

# ---------------------------------------------------------------- B1 report
if b1n:
    e1 = [st.mean(r["rungs"][1]["eigvals"][i] for r in b1n) for i in range(8)]
    e1o = [st.mean(r["rungs"][1]["eigvals"][i] for r in b1old) for i in range(8)]
    figs("results/stage_b1_nesting", e1o, e1, ["before (hard, 30k)", "P9 (hard, 60k)"],
         [st.mean(r["rungs"][0]["angle_deg"] for r in b1old), st.mean(r["rungs"][1]["angle_deg"] for r in b1old)],
         [st.mean(r["rungs"][0]["angle_deg"] for r in b1n), st.mean(r["rungs"][1]["angle_deg"] for r in b1n)],
         (st.mean(r["core_invariant_r2"] for r in b1old), st.mean(r["core_invariant_r2"] for r in b1n)))
    ctl = [[a, ", ".join(f"{r['rungs'][1]['angle_deg']:.1f}°" for r in v) + " (rung-2 angle per seed)", f"rung-2 gap {ms([r['rungs'][1]['gap_ratio'] for r in v], 1)}"] for a, v in b1ctl.items() if v]
    attr = [[r["seed"], f"{r['inherited_span_deg']:.2f}", f"{r['inherited_perp_deg']:.2f}", f"{r['nesting_angle_deg']:.2f}", f"{r['nesting_perp_deg']:.2f}", f"{r['rungs'][1]['angle_deg']:.2f}"] for r in b1n]
    md = ["# P9 report: B1 re-run with hard nesting projection and rung-1 budget 60,000 (ground-truth pairs)\n",
          f"**Verdict line.** Nesting (gate definition) moved from {nest_before_b1}° to {nest_after_b1}° (mean ± std over {len(b1n)} seeds). Pairs per rung: {b1n[0]['pair_budgets']}. Enforcement: {b1n[0]['nesting_enforcement']}.\n",
          "## A. Gate table\n", tab(["Criterion", "Threshold", "Measured (mean ± std)", "Pass?"], gate_table(b1n)),
          "\n## B. Paper-standard metrics (rung-2 split)\n", tab(["Global R²", "Invariant R²", "Variant R²", "a12_fro", "a21_fro", "Block purity"], [six([{**r["rungs"][1], "global_r2": r["global_r2"], "invariant_r2": r["core_invariant_r2"]} for r in b1n])]),
          "\n## Before / after (informational, not a gate)\n", tab(["", "Earlier B1 (30k per rung)", "P9 (60k / 30k)"],
                                                   [["Nesting angle, gate definition (°)", nest_before_b1, nest_after_b1],
                                                    ["Rung-1 angle (°)", ms([r["rungs"][0]["angle_deg"] for r in b1old]), ms([r["rungs"][0]["angle_deg"] for r in b1n])],
                                                    ["Rung-2 angle (°)", ms([r["rungs"][1]["angle_deg"] for r in b1old]), ms([r["rungs"][1]["angle_deg"] for r in b1n])]]),
          "\n## Rank-completeness monitor (D9)\n", tab(["Rung", "Seeds passing", "λ_min", "Noise-floor threshold", "Pairs"], rank_rows(b1n, [("1", lambda r: r["rungs"][0]["rank_monitor"]), ("2", lambda r: r["rungs"][1]["rank_monitor"])])),
          "\n## Controls\n", tab(["Arm", "Observed", "Note"], ctl),
          "\n## Attribution (informational, not a gate): where the nesting angle comes from\n", tab(["Seed", "Inherited θ(H₁, H₁*), span truth (°)", "Inherited, orthogonal-complement truth (°)", "Nesting, span truth (°)", "Nesting, orthogonal-complement truth (°)", "Recovery θ(V₂, identity image) (°)"], attr),
          "\n## Unit test output\n```\n" + unit + "\n```\n", "\n## Figures\n![P2prime](figures/P2prime.svg)\n![P5](figures/P5.svg)\n"]
    open("results/stage_b1_nesting/REPORT.md", "w").write("\n".join(md))

# ---------------------------------------------------------------- B2 report
if b2n:
    arms = {"B1 (generator twins)": "b1_generator", "B2 (discovered clusters)": "b2_kmeans"}
    e_o = [st.mean(r["arms"]["b2_kmeans"]["eigvals"][i] for r in b2old) for i in range(8)]
    e_n = [st.mean(r["arms"]["b2_kmeans"]["eigvals"][i] for r in b2n) for i in range(8)]
    a = lambda rs, arm, k: st.mean(r["arms"][arm][k] for r in rs)
    figs("results/stage_b2_nesting", e_o, e_n, ["before (30k)", "P9 (60k / 30k)"],
         [st.mean(r["rung1"]["angle_deg"] for r in b2old), a(b2old, "b2_kmeans", "angle_deg")], [st.mean(r["rung1"]["angle_deg"] for r in b2n), a(b2n, "b2_kmeans", "angle_deg")],
         (a(b2old, "b2_kmeans", "core_invariant_r2"), a(b2n, "b2_kmeans", "core_invariant_r2")))
    six_rows = [[n] + six([r["arms"][arm] for r in b2n]) for n, arm in arms.items()]
    six_rows.append(["Paper (single split)", "0.9977", "0.9980", "0.9974", "0.0034", "0.0233", "0.99993"])
    head = []
    for label, f, nd in (("Rung-2 angle (°)", lambda x: x["angle_deg"], 2), ("Identity R²", lambda x: x["variant_r2"], 3), ("Category core R²", lambda x: x["core_invariant_r2"], 3),
                         ("Nesting, gate definition (°)", lambda x: x["nesting_angle_deg"], 2), ("Nesting, orthogonal-complement truth (°)", lambda x: x["nesting_perp_deg"], 2), ("Gap ratio, rung 2", lambda x: x["gap_ratio"], 1)):
        row = [label]
        for r in b2n:
            b1v, b2v = f(r["arms"]["b1_generator"]), f(r["arms"]["b2_kmeans"]); row.append(f"{b1v:.{nd}f} / {b2v:.{nd}f} / {b2v-b1v:+.{nd}f}")
        head.append(row)
    cr = b2n; m_a = lambda arm: st.mean(r["arms"][arm]["angle_deg"] for r in cr)
    ctl = [["C1 cross-cluster pairs", "angle above 10°, validity below 0.95", f"angle {m_a('c1_cross_cluster'):.1f}°, validity {st.mean(r['construction']['c1_cross_cluster']['pair_validity'] for r in cr):.3f}", yn(m_a("c1_cross_cluster") > 10)],
           ["C2 clusters from variant block", "angle above 10°", f"angle {m_a('c2_variant_clusters'):.1f}°", yn(m_a("c2_variant_clusters") > 10)],
           ["C3 singleton clusters", "zero valid pairs", f"{st.mean(r['construction']['c3_singleton']['n_pairs'] for r in cr):.0f} pairs", yn(all(r["construction"]["c3_singleton"]["n_pairs"] == 0 for r in cr))],
           ["C4 shuffled membership (recorded)", "none", f"angle {m_a('c4_shuffled'):.1f}°", "recorded"]]
    attr = [[r["seed"], f"{r['rung1']['inherited_span_deg']:.2f}", f"{r['rung1']['inherited_perp_deg']:.2f}", f"{r['arms']['b2_kmeans']['nesting_angle_deg']:.2f}", f"{r['arms']['b2_kmeans']['nesting_perp_deg']:.2f}", f"{r['arms']['b2_kmeans']['angle_deg']:.2f}"] for r in b2n]
    rm = rank_rows(b2n, [("1", lambda r: r["rung1"]["rank_monitor"]), ("2 (B2 clusters)", lambda r: r["arms"]["b2_kmeans"]["rank_monitor"])])
    gate_b2 = gate_table(b2_views(b2n, "b2_kmeans")); gate_b1 = gate_table(b2_views(b2n, "b1_generator"))
    md = ["# P9 report: formal B2 re-run with hard nesting projection and rung-1 budget 60,000 (clean world, sigma_cat " + str(clean) + ")\n",
          f"**Verdict line.** Nesting (gate definition), B2 arm: {nest_before_b2}° earlier → {nest_after_b2}° now (mean ± std, {len(b2n)} seeds); with the orthogonal-complement truth: {ms([r['arms']['b2_kmeans']['nesting_perp_deg'] for r in b2n])}°. Pairs per rung: {b2n[0]['pair_budgets']}.\n",
          "## A. Gate table (B2 arm)\n", tab(["Criterion", "Threshold", "Measured (mean ± std)", "Pass?"], gate_b2),
          "\nFor reference, the B1 arm (generator twins) on the same encoders:\n", tab(["Criterion", "Threshold", "Measured (mean ± std)", "Pass?"], gate_b1),
          "\n## B. Paper-standard metrics (rung-2 split)\n", tab(["Rung 2 split", "Global R²", "Invariant R²", "Variant R²", "a12_fro", "a21_fro", "Block purity"], six_rows),
          "\n## D. Headline: B1 / B2 / Δ per seed\n", tab(["Metric"] + [f"seed {r['seed']}" for r in b2n], head),
          "\n## Before / after (informational)\n", tab(["", "Earlier (30k)", "P9 (60k / 30k)"], [["Nesting, B2 arm, gate definition (°)", nest_before_b2, nest_after_b2],
              ["Nesting gap B2 − B1 (°)", ms([r["arms"]["b2_kmeans"]["nesting_angle_deg"] - r["arms"]["b1_generator"]["nesting_angle_deg"] for r in b2old]), ms([r["arms"]["b2_kmeans"]["nesting_angle_deg"] - r["arms"]["b1_generator"]["nesting_angle_deg"] for r in b2n])],
              ["Rung-1 angle (°)", ms([r["rung1"]["angle_deg"] for r in b2old]), ms([r["rung1"]["angle_deg"] for r in b2n])]]),
          "\n## Rank-completeness monitor (D9)\n", tab(["Rung", "Seeds passing", "λ_min", "Threshold", "Pairs"], rm),
          "\n## Controls\n", tab(["Control", "Required outcome", "Observed", "Result"], ctl),
          "\n## Attribution (informational, not a gate)\n", tab(["Seed", "Inherited, span truth (°)", "Inherited, orthogonal-complement truth (°)", "Nesting, span truth (°)", "Nesting, orthogonal-complement truth (°)", "Recovery θ(V₂, identity image) (°)"], attr),
          "\n## Unit test output\n```\n" + unit + "\n```\n", "\n## Figures\n![P2prime](figures/P2prime.svg)\n![P5](figures/P5.svg)\n"]
    open("results/stage_b2_nesting/REPORT.md", "w").write("\n".join(md))
print("built", len(b1n), "B1 seeds,", len(b2n), "B2 seeds")
