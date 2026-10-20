"""E21 (confirmatory re-run on seeds 20-29) and E22 (probe-image explanation) analysis; rules frozen in docs/EVIDENCE.md before the runs.
    python experiments/analyse_e21_e22.py  -> results/stage_b1_e21/E21_REPORT.md, results/stage_b2_e21/E21_E22_REPORT.md"""
import glob, json, statistics as st, sys
import yaml
from isj.stage_b1 import CRITERIA_KEYS, seed_checks

cfg = yaml.safe_load(open("configs/stage_b1.yaml")); crit = cfg["criteria"]; ctl = cfg["controls"]["must_fail"]
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
ms = lambda v, nd=2: f"{st.mean(v):.{nd}f} ± {st.stdev(v):.{nd}f}" if len(v) > 1 else f"{v[0]:.{nd}f}"
L = lambda pat: sorted((json.load(open(f)) for f in glob.glob(pat)), key=lambda r: r["seed"])

# ------------------------------------------------------------------ Part A: B1 mechanism, fresh seeds
A = {arm: L(f"results/stage_b1_e21/{arm}_seed*.json") for arm in ("main", "shuffled_rung2", "rank1_rung2")}
md = ["# E21 Part A: B1 mechanism (all-Gaussian world, mirror encoder), fresh seeds 20-29\n"]
if len(A["main"]) >= 1:
    per, fails = [], {k: [] for k in CRITERIA_KEYS}
    for r in A["main"]:
        chk = seed_checks(r, crit)
        chk["leakage"] = max(abs(x) for rg in r["rungs"] for k, x in rg["leak_r2"].items() if k in ("rest->own", "own->rest")) < 0.01          # registered amended leakage rule
        per.append(chk)
        for k in CRITERIA_KEYS:
            if not chk[k]: fails[k].append(r["seed"])
    failing = {k for k, v in fails.items() if v}
    verdict = "PASS" if not failing else ("PASS_WITH_LOCATED_RISK" if failing == {"rung1_variant_r2"} else "FAIL")
    mean = lambda arm, f: st.mean(f(r) for r in A[arm]) if A[arm] else float("nan")
    ctls = {"shuffled_rung2": mean("shuffled_rung2", lambda r: r["rungs"][1]["angle_deg"]) > ctl["shuffled_rung2"]["rung2_angle_min_deg"] and mean("shuffled_rung2", lambda r: r["rungs"][1]["gap_ratio"]) < ctl["shuffled_rung2"]["rung2_gap_ratio_max"],
            "rank1_rung2": mean("rank1_rung2", lambda r: r["rungs"][1]["angle_deg"]) > ctl["rank1_rung2"]["rung2_angle_min_deg"] and mean("rank1_rung2", lambda r: r["rungs"][0]["angle_deg"]) < ctl["rank1_rung2"]["rung1_angle_max_deg"]}
    n = len(A["main"])
    md += [f"**Verdict (registered rule, amended leakage floor 0.01): {verdict}** on {n} seeds; failing criteria: {sorted(failing) or 'none'} ({ {k: v for k, v in fails.items() if v} or 'no seed fails any'}). "
           f"Controls (judged on the mean): shuffled rung-2 {'behaved' if ctls['shuffled_rung2'] else 'DID NOT behave'}; rank-1 rung-2 {'behaved' if ctls['rank1_rung2'] else 'DID NOT behave'}.\n",
           f"**E21 Part A prediction (PASS or PASS_WITH_LOCATED_RISK, controls behave): {'CONFIRMED' if verdict != 'FAIL' and all(ctls.values()) else 'REFUTED'}.**\n",
           "## Measured (main arm, mean ± std over seeds)\n",
           tab(["Quantity", "Value"], [["Rung 1 angle (°)", ms([r["rungs"][0]["angle_deg"] for r in A["main"]])], ["Rung 2 angle (°)", ms([r["rungs"][1]["angle_deg"] for r in A["main"]])],
                ["Texture R² (rung 1)", ms([r["rungs"][0]["variant_r2"] for r in A["main"]], 3)], ["Identity R² (rung 2)", ms([r["rungs"][1]["variant_r2"] for r in A["main"]], 3)],
                ["Category core R²", ms([r["core_invariant_r2"] for r in A["main"]], 3)], ["Nesting (gate definition, °)", ms([r["nesting_angle_deg"] for r in A["main"]])],
                ["Gap ratio rung 1 / rung 2", f"{ms([r['rungs'][0]['gap_ratio'] for r in A['main']], 1)} / {ms([r['rungs'][1]['gap_ratio'] for r in A['main']], 1)}"],
                ["Largest off-diagonal |R²| (amended rule needs < 0.01)", ms([max(abs(x) for rg in r["rungs"] for k, x in rg["leak_r2"].items() if k in ("rest->own", "own->rest")) for r in A["main"]], 4)],
                ["D13 leakage: normalized ‖A21‖, rung 1 / rung 2 (gate 0.0209)", f"{ms([r['rungs'][0]['a21_fro'] / 2 for r in A['main']], 4)} / {ms([r['rungs'][1]['a21_fro'] / 2 for r in A['main']], 4)}"],
                ["Seeds meeting the D13 gate at both rungs", f"{sum(max(r['rungs'][0]['a21_fro'], r['rungs'][1]['a21_fro']) / 2 < 0.0209 for r in A['main'])} of {n}"]]),
           "\n## Per-criterion seeds passing\n", tab(["Criterion", "Seeds passing"], [[k, f"{sum(p[k] for p in per)} of {n}"] for k in CRITERIA_KEYS])]
    if A["shuffled_rung2"]: md += ["\n## Controls\n", tab(["Control", "Rung-2 angle (°)", "Rung-2 gap", "Rung-1 angle (°)"], [[arm, ms([r["rungs"][1]["angle_deg"] for r in A[arm]], 1), ms([r["rungs"][1]["gap_ratio"] for r in A[arm]], 2), ms([r["rungs"][0]["angle_deg"] for r in A[arm]], 2)] for arm in ("shuffled_rung2", "rank1_rung2") if A[arm]])]
    open("results/stage_b1_e21/E21_REPORT.md", "w").write("\n".join(md))
else: md.append("No B1 runs found yet.")

# ------------------------------------------------------------------ Part B (B2 world) and E22
runs = sorted((json.load(open(f)) for f in glob.glob("results/stage_b2_e21/sigma_cat_*/[0-9]*.json")), key=lambda r: (r["sigma_cat"], r["seed"]))
by = {}
for r in runs: by.setdefault(r["sigma_cat"], []).append(r)
out = ["# E21 Part B and E22: B2 world, fresh seeds 20-29, sigma_cat 0.1 and 0.4\n"]
a = lambda r, arm, k: r["arms"][arm][k]
verd = {}
rows = []
for s, R in sorted(by.items()):
    n = len(R)
    gb1, gun, gt1 = (st.mean(a(r, arm, "gap_ratio") for r in R) for arm in ("b1_generator", "b2_kmeans", "b2_kmeans_purified"))
    rec = (gt1 - gun) / (gb1 - gun)
    over10 = sum(a(r, "b2_kmeans_purified", "gap_ratio") > 10 for r in R)
    e20 = [a(r, "b2_kmeans_purified", "gap_ratio") >= 0.6 * a(r, "label_pairs", "gap_ratio") for r in R if a(r, "label_pairs", "gap_ratio") >= 3]
    nest = all(a(r, arm, "nesting_perp_deg") < 5 for r in R for arm in ("b1_generator", "b2_kmeans", "b2_kmeans_purified"))
    METRICS = [("angle_deg", 1), ("variant_r2", -1), ("core_invariant_r2", -1), ("nesting_perp_deg", 1), ("nesting_angle_deg", 1), ("block_purity", -1), ("a12_fro", 1)]
    dmg = {k: (st.mean(a(r, "b2_kmeans_purified", k) for r in R) - st.mean(a(r, "b2_kmeans", k) for r in R)) * bad > st.stdev(a(r, "b2_kmeans", k) for r in R) for k, bad in METRICS}
    verd[s] = {"recovery": rec, "over10": over10 / n, "e20_share": (sum(e20) / len(e20)) if e20 else None, "nesting_all_below_5": nest, "damaged": [k for k, v in dmg.items() if v]}
    rows.append([s, n, f"{gb1:.1f}", f"{gun:.1f}", f"{gt1:.1f}", f"{rec:.2f}", f"{over10}/{n}", (f"{sum(e20)}/{len(e20)}" if e20 else "n/a"), "yes" if nest else "**NO**", ", ".join(verd[s]["damaged"]) or "none"])
out += ["## Part B: frozen criteria on fresh seeds\n", tab(["σ_cat", "Runs", "Gap B1 arm", "Gap B2 untreated", "Gap B2 + Tier 1", "Share of deficit recovered (needs ≥ 0.60 at σ 0.1)", "Tier 1 gap > 10", "Tier 1 meets E20 criterion (needs ≥ 90% at σ 0.4)", "D10 nesting < 5° in every run", "Metrics damaged (E14 rule)"], rows)]
if runs:
    c1 = verd.get(0.1, {}); c2 = verd.get(0.4, {})
    ok = (c1.get("recovery", 0) >= 0.6 and c1.get("over10", 0) >= 0.9, (c2.get("e20_share") or 0) >= 0.9, all(v["nesting_all_below_5"] for v in verd.values()), all(not v["damaged"] for v in verd.values()))
    out += [f"\nSub-claims: (i) σ 0.1 recovery ≥ 0.60 and gap > 10 in ≥ 90% of seeds: **{'yes' if ok[0] else 'NO'}**; (ii) σ 0.4 E20 criterion in ≥ 90% of seeds: **{'yes' if ok[1] else 'NO'}**; (iii) nesting < 5° in every run: **{'yes' if ok[2] else 'NO'}**; (iv) no metric damaged: **{'yes' if ok[3] else 'NO'}**. "
            f"Part A verdict: see `results/stage_b1_e21/E21_REPORT.md`."]
    # ---- E22
    e22 = [[r["sigma_cat"], r["seed"], f"{r['image_geometry']['min_angle_texture_vs_identity_category_deg']:.1f}", f"{r['image_geometry']['identity_image_energy_removed']:.3f}", f"{a(r, 'b1_generator', 'angle_deg'):.2f}", f"{a(r, 'b1_generator', 'angle_orth_deg'):.2f}",
            f"{a(r, 'b1_generator', 'angle_deg') - a(r, 'b1_generator', 'angle_orth_deg'):.2f}", f"{a(r, 'b2_kmeans_purified', 'angle_deg'):.2f}", f"{a(r, 'b2_kmeans_purified', 'angle_orth_deg'):.2f}"] for r in runs]
    n_ = len(runs); le5 = sum(a(r, "b1_generator", "angle_orth_deg") <= 5 for r in runs); ge3 = sum(a(r, "b1_generator", "angle_deg") - a(r, "b1_generator", "angle_orth_deg") >= 3 for r in runs)
    out += ["\n## E22: probe-image explanation, direct test (B1 arm = generator twins; raw angle = against the identity probe image, orthogonalised = against the part of it orthogonal to the texture image)\n",
            f"**Prediction (orthogonalised angle ≤ 5° in ≥ 90% of runs AND ≥ 3° below the raw angle in ≥ 90% of runs): ≤ 5° in {le5} of {n_}; ≥ 3° lower in {ge3} of {n_} -> {'CONFIRMED' if le5 >= 0.9 * n_ and ge3 >= 0.9 * n_ else 'REFUTED'}.**\n",
            f"Means over runs: raw {ms([a(r, 'b1_generator', 'angle_deg') for r in runs])}°, orthogonalised {ms([a(r, 'b1_generator', 'angle_orth_deg') for r in runs])}°; smallest angle between the texture image and the identity+category images {ms([r['image_geometry']['min_angle_texture_vs_identity_category_deg'] for r in runs], 1)}°.\n",
            tab(["σ_cat", "seed", "Min angle texture image vs identity+category images (°)", "Share of identity image removed by orthogonalising", "B1 arm rung-2 angle, raw (°)", "orthogonalised (°)", "Difference (°)", "B2 + Tier 1, raw (°)", "orthogonalised (°)"], e22)]
open("results/stage_b2_e21/E21_E22_REPORT.md", "w").write("\n".join(out)); print("\n".join(md[:3])); print("\n".join(out[:3]))
