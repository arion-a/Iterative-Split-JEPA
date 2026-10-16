"""Recalibrated gap reference for cluster-built pairs (D14 candidate) and the corrected contamination model (erratum). Existing sweep data only.
    -> results/stage_b2_gapfix_sweep/RECALIBRATION.md"""
import glob, json, math, statistics as st
D = "results/stage_b2_gapfix_sweep"
runs = sorted((json.load(open(f)) for f in glob.glob(f"{D}/sigma_cat_*/[0-9]*.json")), key=lambda r: (r["sigma_cat"], r["seed"]))
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
FRAC, MIN_ACH = 0.6, 3.0          # D14 constants: 60% of the achievable gap (the E12 precedent); criterion applies only where the achievable gap is at least 3
sig = sorted({r["sigma_cat"] for r in runs}); by = {s: [r for r in runs if r["sigma_cat"] == s] for s in sig}
floor = []
for s in sig:
    R = by[s]; e = lambda arm, i: st.mean(r["arms"][arm]["eigvals"][i] for r in R)
    floor.append([s, f"{e('b1_generator', 4):.3f}", f"{e('b1_generator', 4) + 2 * s * s:.3f}", f"{e('label_pairs', 4):.3f}", f"{st.mean(r['arms']['label_pairs']['gap_ratio'] for r in R):.2f}"])
rows = []
for s in sig:
    for r in by[s]:
        ach = r["arms"]["label_pairs"]["gap_ratio"]; u, t = r["arms"]["b2_kmeans"]["gap_ratio"], r["arms"]["b2_kmeans_purified"]["gap_ratio"]
        app = ach >= MIN_ACH
        rows.append([s, r["seed"], f"{ach:.2f}", f"{u:.2f} ({u / ach:.2f})", f"{t:.2f} ({t / ach:.2f})", "applies" if app else "n/a (no usable cliff)",
                     ("yes" if u >= FRAC * ach else "no") if app else "", ("yes" if t >= FRAC * ach else "no") if app else ""])
summ = []
for s in sig:
    R = by[s]; ach = [r["arms"]["label_pairs"]["gap_ratio"] for r in R]
    if min(ach) < MIN_ACH and st.mean(ach) < MIN_ACH: summ.append([s, f"{st.mean(ach):.2f}", "n/a", "n/a"]); continue
    summ.append([s, f"{st.mean(ach):.2f}", f"{sum(r['arms']['b2_kmeans']['gap_ratio'] >= FRAC * r['arms']['label_pairs']['gap_ratio'] for r in R)}/3", f"{sum(r['arms']['b2_kmeans_purified']['gap_ratio'] >= FRAC * r['arms']['label_pairs']['gap_ratio'] for r in R)}/3"])
# model fits: original floor (B1 twins) vs corrected floor (measured on perfect-cluster pairs)
rho = [1 - r["construction"]["b2_kmeans"]["pair_validity"] for r in runs]; l4 = [r["arms"]["b1_generator"]["eigvals"][3] for r in runs]
gu = [r["arms"]["b2_kmeans"]["gap_ratio"] for r in runs]; gt = [r["arms"]["b2_kmeans_purified"]["gap_ratio"] for r in runs]; lg = [math.log(g) for g in gu]; m = st.mean(lg)
def fit(fl):
    sse = lambda v: sum((lg[i] - math.log(l4[i] / (fl[i] + rho[i] * v))) ** 2 for i in range(len(runs)))
    v = min([10 ** (x / 100) for x in range(-300, 300)], key=sse)
    pred = [l4[i] / (fl[i] + rho[i] * v) for i in range(len(runs))]
    mask = [i for i in range(len(runs)) if rho[i] > 0.05]
    return v, 1 - sse(v) / sum((x - m) ** 2 for x in lg), st.median([abs(pred[i] - gu[i]) / gu[i] for i in range(len(runs))]), sum(gt[i] > pred[i] for i in mask), len(mask)
f_old = [r["arms"]["b1_generator"]["eigvals"][4] for r in runs]; f_new = [r["arms"]["label_pairs"]["eigvals"][4] for r in runs]
(vo, r2o, eo, ao, no), (vn, r2n, en, an, nn) = fit(f_old), fit(f_new)
md = ["# Recalibrated gap reference for cluster-built pairs, and the corrected contamination model (existing sweep data; D14 candidate and erratum)\n",
      "## The floor under cluster-built pairs (fifth rung-2 eigenvalue, mean over 3 seeds)\n",
      "Twins (B1) share the category jitter exactly. Cluster-built pairs share only the label, so even perfect clusters carry within-category energy. 'Perfect clusters' = the label_pairs arm (pairs that share the true category).\n",
      tab(["σ_cat", "B1 twins", "Twins + 2σ_cat² (analytic)", "Perfect-cluster pairs (measured)", "Rung-2 gap, perfect clusters (the achievable gap)"], floor),
      "\nThe analytic term holds within about 5% up to σ_cat 0.4 and overstates beyond (whitening compresses the growing variance), so the erratum uses the measured floor, not 2σ_cat².\n",
      f"## Recalibrated criterion (D14 candidate): cluster-built gap ≥ {FRAC} × achievable gap, where the achievable gap is at least {MIN_ACH}\n",
      tab(["σ_cat", "Achievable gap", "B2 untreated meets it", "B2 + Tier 1 meets it"], summ), "\nPer run (ratio to the achievable gap in brackets):\n",
      tab(["σ_cat", "seed", "Achievable gap", "B2 untreated", "B2 + Tier 1", "Criterion", "Untreated meets", "Tier 1 meets"], rows),
      "\n## Contamination model, original versus corrected floor (post hoc refit on the same 18 runs, one fitted constant each)\n",
      tab(["Floor used for λ_{d2+1}^clean", "v_cat", "log-gap R²", "median relative error", "Tier 1 above the curve"], [["B1 twins (registered E13 model)", f"{vo:.3g}", f"{r2o:.3f}", f"{eo:.2f}", f"{ao} of {no}"], ["Perfect-cluster pairs (corrected)", f"{vn:.3g}", f"{r2n:.3f}", f"{en:.2f}", f"{an} of {nn}"]]),
      "\nThe corrected model meets the numeric thresholds registered for E13 (R² ≥ 0.8, error ≤ 25%), but it was fitted after seeing the data, so it is a lead and not a confirmation of E13."]
open(f"{D}/RECALIBRATION.md", "w").write("\n".join(md))
print("\n".join(md[6:9])); print(tab(["σ_cat", "Achievable gap", "B2 untreated meets it", "B2 + Tier 1 meets it"], summ)); print(f"orig R2 {r2o:.3f} above {ao}/{no}; corrected R2 {r2n:.3f} above {an}/{nn}")
