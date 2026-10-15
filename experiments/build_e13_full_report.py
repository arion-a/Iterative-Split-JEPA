"""Full E13 report (docs/REPORTING.md format) for results/stage_b2_gapfix_sweep/: per-noise-level gate tables, paper metrics, controls, attribution, plus the E13 analysis."""
import glob, json, statistics as st, yaml
from isj.stage_b1 import seed_checks

D = "results/stage_b2_gapfix_sweep"
crit = yaml.safe_load(open("configs/stage_b1.yaml"))["criteria"]
LEAK = yaml.safe_load(open("configs/gates_v2.yaml"))["leakage_gate"]["threshold"]
runs = sorted((json.load(open(f)) for f in glob.glob(f"{D}/sigma_cat_*/[0-9]*.json")), key=lambda r: (r["sigma_cat"], r["seed"]))
sig = sorted({r["sigma_cat"] for r in runs}); by = {s: [r for r in runs if r["sigma_cat"] == s] for s in sig}
ms = lambda v, nd=2: f"{st.mean(v):.{nd}f} ± {st.stdev(v):.{nd}f}" if len(v) > 1 else f"{v[0]:.{nd}f}"
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
ARMS = [("B1 arm (generator twins)", "b1_generator"), ("B2 untreated", "b2_kmeans"), ("B2 + Tier 1", "b2_kmeans_purified"), ("B2 + Tier 1 + Tier 4", "b2_kmeans_purified_whitened")]

def view(r, arm):
    a = dict(r["arms"][arm]); a["nesting_angle_deg"] = a["nesting_perp_deg"]          # D10 reference
    return {"rungs": [r["rung1"], a], "nesting_angle_deg": a["nesting_angle_deg"], "core_invariant_r2": a["core_invariant_r2"]}

def gates_ok(r, arm):
    c = seed_checks(view(r, arm), crit)
    c["leakage"] = max(r["rung1"]["a21_norm"], r["arms"][arm]["a21_norm"]) < LEAK         # gates_v2 (D13)
    return c
KEYS = ["rung1_angle", "rung2_angle", "rung1_variant_r2", "rung2_variant_r2", "core_invariant_r2", "nesting", "rung1_gap", "rung2_gap", "leakage", "rank_test"]
NAMES = {"rung1_angle": "R1 angle <5°", "rung2_angle": "R2 angle <5°", "rung1_variant_r2": "texture R² >0.9", "rung2_variant_r2": "identity R² >0.9", "core_invariant_r2": "core R² >0.9",
         "nesting": "nesting <5° (D10)", "rung1_gap": "R1 gap >10", "rung2_gap": "R2 gap >10", "leakage": f"leakage ‖A21‖ <{LEAK}", "rank_test": "rank check"}

md = ["# E13 full report: gap-ratio fix across the noise sweep (formal B2 world, 18 runs)\n",
      "## 1. What was run\n",
      "World: formal B2 mixture world (docs/B2.md): blocks texture / identity / category of 4 numbers each, speeds 0.2 / 0.7 / 0.95, 6 categories × 20 identities × 2 textures, scrambled by the paper's 4-layer coupling map, 12 observed numbers. Noise sweep: within-category spread sigma_cat ∈ {0.1, 0.4, 0.6, 0.8, 1.0, 1.5}; seeds 0, 1, 2; 18 runs. Encoder: mirror (inverse-coupling) encoder, paper objective (alignment + SIGReg 1e-6), 10,000 steps, batch 256, lr 3e-3, then frozen; ZCA whitening on 30,000 samples. Rung 1: 60,000 generator twin pairs; rung 2: 30,000 pairs (B1 twins, or pairs inside discovered clusters from the rung-1 invariant output; k-means, K by silhouette); hard nesting; Tier 1 purification (drop pairs scoring over 4 × the median in the bottom eigendirections, up to 5 iterations); Tier 4 arm (within-H₁ whitening) kept for the comparability check. Gates: frozen B1 criteria with the D10 nesting reference and the D13 leakage gate (normalized ‖A21‖ below 0.0209). Protocol and thresholds for the E13 checks were fixed in `docs/EVIDENCE.md` before the run. Wall time about 25 minutes (3 processes, one per seed).\n",
      "## 2. Verdict\n",
      "**E13 is REFUTED as registered.** The contamination model does not fit across the sweep (log-gap R² 0.667, needs 0.8) and purified runs sit above the model curve in 10 of 17 runs (needs 90%). Tier 1 recovers the rung-2 gap only in the clean world (sigma_cat 0.1). From 0.4 up it trims 1-3% of pairs and the gap stays at 1-6. The blind E14 check is confirmed for damage (18 of 18 runs) but not for position (14 of 18). Tier 4 shows no case. Details below.\n"]

# per-noise-level summary
rows = []
for s in sig:
    R = by[s]
    rows.append([s, ms([r["quality"]["cluster_purity"] for r in R], 3), "/".join(str(r["quality"]["k_discovered"]) for r in R), ms([1 - r["construction"]["b2_kmeans"]["pair_validity"] for r in R], 3),
                 ms([r["arms"]["b1_generator"]["gap_ratio"] for r in R], 1), ms([r["arms"]["b2_kmeans"]["gap_ratio"] for r in R], 1), ms([r["arms"]["b2_kmeans_purified"]["gap_ratio"] for r in R], 1),
                 ms([r["arms"]["b2_kmeans_purified_whitened"]["gap_ratio"] for r in R], 1), ms([1 - r["purify"]["kept_fraction"] for r in R], 3),
                 ms([(1 - r["purify"]["kept_fraction"]) - r["noop_control"]["trimmed_fraction"] for r in R], 3)])
md += ["## 3. Headline by noise level (mean ± std over 3 seeds)\n", tab(["σ_cat", "Cluster purity", "K found (3 seeds)", "True mis-grouped ρ", "Rung-2 gap B1 arm", "B2 untreated", "B2 + Tier 1", "B2 + Tier 1+4", "Pairs trimmed by Tier 1", "ρ̂ (trimmed − B1 clean baseline)"], rows)]

# gate table per sigma for the Tier 1 arm + B1 arm
for title, arm in (("B2 + Tier 1 (canonical treatment)", "b2_kmeans_purified"), ("B2 untreated", "b2_kmeans"), ("B1 arm (generator twins, reference)", "b1_generator")):
    rows = []
    for s in sig:
        R = by[s]; c = [gates_ok(r, arm) for r in R]
        rows.append([s] + [f"{sum(x[k] for x in c)}/3" for k in KEYS])
    md += [f"\n## 4. Gate table by noise level: {title} (seeds passing each frozen criterion)\n", tab(["σ_cat"] + [NAMES[k] for k in KEYS], rows)]
rows = []
for k in KEYS:
    rows.append([NAMES[k]] + [f"{ms([ {'rung1_angle':v['rung1']['angle_deg'] if False else 0} for v in []] or [0]) if False else ''}" for _ in []])
md.append("")

# measured values for the Tier 1 arm in the clean world and a mid and a high noise level
def meas(r, arm):
    v = view(r, arm); a = r["arms"][arm]
    return {"R1 angle (°)": v["rungs"][0]["angle_deg"], "R2 angle (°)": a["angle_deg"], "texture R²": r["rung1"]["variant_r2"], "identity R²": a["variant_r2"], "core R²": a["core_invariant_r2"],
            "nesting D10 (°)": a["nesting_perp_deg"], "R1 gap": r["rung1"]["gap_ratio"], "R2 gap": a["gap_ratio"], "‖A21‖ norm (max of rungs)": max(r["rung1"]["a21_norm"], a["a21_norm"])}
names = list(meas(runs[0], "b2_kmeans_purified"))
rows = []
for n in names:
    rows.append([n] + [ms([meas(r, "b2_kmeans_purified")[n] for r in by[s]], 3 if "R²" in n or "norm" in n else 2) for s in sig])
md += ["\n## 5. Measured values, B2 + Tier 1 (mean ± std over seeds)\n", tab(["Metric"] + [f"σ {s}" for s in sig], rows)]

# paper metrics (rung-2 split), Tier 1 arm
rows = []
for s in sig:
    R = by[s]; a = lambda k: [r["arms"]["b2_kmeans_purified"][k] for r in R]
    rows.append([s, ms([r["arms"]["b2_kmeans_purified"]["global_r2"] for r in R], 4), ms(a("invariant_r2"), 4), ms(a("variant_r2"), 4), ms(a("a12_fro"), 4), ms(a("a21_fro"), 4), ms(a("block_purity"), 5)])
rows.append(["Paper (single split)", "0.9977", "0.9980", "0.9974", "0.0034", "0.0233", "0.99993"])
md += ["\n## 6. Paper-standard metrics, rung-2 split, B2 + Tier 1\n", tab(["σ_cat", "Global R²", "Invariant R²", "Variant R²", "a12_fro", "a21_fro", "Block purity"], rows)]

# controls
rows = []
for s in sig:
    R = by[s]; ma = lambda arm: st.mean(r["arms"][arm]["angle_deg"] for r in R)
    rows.append([s, f"{ma('c1_cross_cluster'):.1f}° / {st.mean(r['construction']['c1_cross_cluster']['pair_validity'] for r in R):.3f}", f"{ma('c2_variant_clusters'):.1f}°",
                 f"{st.mean(r['construction']['c3_singleton']['n_pairs'] for r in R):.0f}", f"{ma('c4_shuffled'):.1f}°",
                 f"{sum(r['arms']['b2_kmeans']['rank_monitor']['pass'] for r in R)}/3, {sum(r['arms']['b2_kmeans_purified']['rank_monitor']['pass'] for r in R)}/3"])
md += ["\n## 7. Controls (required: C1 angle > 10° and validity < 0.95; C2 angle > 10°; C3 zero pairs; C4 recorded) and rank monitor\n",
       tab(["σ_cat", "C1 cross-cluster: angle / validity", "C2 variant-block clusters: angle", "C3 singleton: pairs", "C4 shuffled: angle", "Rank monitor passes (B2 untreated, B2 + Tier 1)"], rows)]
c1 = all(st.mean(r["arms"]["c1_cross_cluster"]["angle_deg"] for r in by[s]) > 10 for s in sig); c2 = all(st.mean(r["arms"]["c2_variant_clusters"]["angle_deg"] for r in by[s]) > 10 for s in sig)
c3 = all(r["construction"]["c3_singleton"]["n_pairs"] == 0 for r in runs)
md.append(f"\nC1 {'failed as required' if c1 else 'DID NOT FAIL'} at every noise level; C2 {'failed as required' if c2 else 'DID NOT FAIL'}; C3 {'zero pairs everywhere' if c3 else 'NOT zero'}.")

# attribution
rows = [[r["sigma_cat"], r["seed"], f"{r['rung1']['angle_deg']:.2f}", f"{r['rung1']['inherited_span_deg']:.2f}", f"{r['rung1']['inherited_perp_deg']:.2f}", f"{r['arms']['b2_kmeans']['nesting_angle_deg']:.2f}",
         f"{r['arms']['b2_kmeans']['nesting_perp_deg']:.2f}", f"{r['arms']['b1_generator']['angle_deg']:.2f}", f"{r['arms']['b2_kmeans_purified']['angle_deg']:.2f}"] for r in runs]
md += ["\n## 8. Attribution (informational, not a gate): where the angles come from, every run\n", tab(["σ_cat", "seed", "Rung-1 angle (°)", "Inherited θ(H₁,H₁*) span truth (°)", "Inherited, complement truth (°)", "Nesting, span truth (°)", "Nesting, complement truth (°)", "Rung-2 angle B1 arm (°)", "Rung-2 angle B2 + Tier 1 (°)"], rows)]

# the E13 analysis (registered checks, per-run table, exploratory refit, figure)
md += ["\n## 9. The registered E13 checks, per-run table and figure\n", open(f"{D}/E13_REPORT.md").read().split("\n", 2)[2], ]
probe = [(sg, st.mean(r["full_feature_probe_r2"]["texture"] for r in by[sg]), st.mean(r["rung1"]["variant_r2"] for r in by[sg]), st.mean(r["rung1"]["angle_deg"] for r in by[sg]),
          st.mean(r["arms"]["b1_generator"]["angle_deg"] for r in by[sg]), st.mean(r["rung1"]["inherited_perp_deg"] for r in by[sg]), st.mean(r["rung1"]["inherited_span_deg"] for r in by[sg])) for sg in sig]
md += ["\n## 10. Observations beyond the registered checks (informational, not tests)\n",
       tab(["σ_cat", "Full-feature texture probe R² (E15 measure)", "Recovered texture block R²", "Rung-1 angle (°)", "Rung-2 angle, B1 arm (°)", "Inherited error, complement truth (°)", "Inherited error, span truth (°)"],
           [[f"{a}", f"{b:.3f}", f"{c:.3f}", f"{d:.2f}", f"{e:.2f}", f"{f:.2f}", f"{g:.2f}"] for a, b, c, d, e, f, g in probe]),
       "\n* **The texture and rung-1 'floor' is specific to the smallest noise level.** At σ_cat 0.1 the texture probe is 0.910, the texture block 0.882 and the rung-1 angle 3.78°. From σ_cat 0.4 up the rung-1 angle is 1.9° and falls to 1.1°, the texture block is 0.92-0.94 (passing), and the probe is 0.947-0.958 (at or above the E15 line of 0.95 from σ 0.6). So the encoder-side shortfall that E15 and E11 chased belongs to the world with the tightest category clusters, not to the encoder in general. Why is not tested here.",
       "* **The rung-2 angle of about 10° does not move with the noise level.** For the B1 arm (true twins) it is 9.6-10.3° at every σ_cat while the rung-1 error against the complement truth falls from 4.6° to about 1°. The inherited error against the span truth stays at 9-13°. The rung-2 angle is measured against the identity block's probe image, so this constant 10° looks like the same non-orthogonal-probe-image definition effect found for nesting (D10), not an encoder floor. This is an observation from this sweep, not a tested explanation.",
       "* **At σ_cat ≥ 0.8 the splitter is not what fails.** The B1 arm keeps rung-2 gaps of 48-140 and all gates except the 10° angle and texture-free items pass for it, while the cluster-built arms collapse (rung-2 angle 40-84°, identity R² 0.24-0.80) because the clusterer finds 9-12 clusters at purity 0.53-0.77.\n"]
md += ["\n## 11. Caveats\n",
       "* 18 runs, 3 seeds per noise level; standard deviations over 3 seeds are rough.",
       "* The E13 thresholds (R² ≥ 0.8, median error ≤ 25%, 90% above the curve, CV ratio 0.75) were mine, fixed before the run and flagged; the formula was the owner's.",
       "* The model's 'clean' floor was taken from the B1 arm (generator twins), which share their category jitter exactly; cluster-built pairs do not, so the floor is understated for them. The explanation in section 9 (within-category energy about 2 σ_cat²) is an observation from the run files, supported directly by one run (σ 0.4 seed 1, almost no invalid pairs). The refit that adds it is post hoc.",
       "* Discovered cluster counts above 6 at σ ≥ 0.8 and purity near 0.5 at σ 1.5 mean the clusterer, not the splitter, is limiting there; the B1 arm (true twins) keeps gaps of 48-140.",
       "* This sweep does not test the encoder floor, texture R² (0.88) or the rung-2 angle (about 10°), which stay open.",
       "\nFiles: `results/stage_b2_gapfix_sweep/sigma_cat_*/<seed>.json` (raw), `E13_REPORT.md` (analysis), `REPORT.md` (this file), `figures/E13_gap_vs_contamination.svg`. Protocol and outcome: `docs/EVIDENCE.md`."]
open(f"{D}/REPORT.md", "w").write("\n".join(md))
print(len(md), "sections written")
