"""E20 blind check (criteria frozen in docs/EVIDENCE.md before the run): recalibrated gap criterion on fresh seeds + informational test of the corrected contamination model."""
import glob, json, statistics as st
D = "results/stage_b2_e20_blind"
runs = sorted((json.load(open(f)) for f in glob.glob(f"{D}/sigma_cat_*/[0-9]*.json")), key=lambda r: (r["sigma_cat"], r["seed"]))
FRAC, MIN_ACH, V_CAT, ERR = 0.6, 3.0, 2.14, 0.25
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
rows, hit_t, hit_u, errs = [], [], [], []
for r in runs:
    a = r["arms"]; ach = a["label_pairs"]["gap_ratio"]; u, t = a["b2_kmeans"]["gap_ratio"], a["b2_kmeans_purified"]["gap_ratio"]
    app = ach >= MIN_ACH; rho = 1 - r["construction"]["b2_kmeans"]["pair_validity"]
    pred = a["b1_generator"]["eigvals"][3] / (a["label_pairs"]["eigvals"][4] + rho * V_CAT); err = abs(pred - u) / u; errs.append(err)
    if app: hit_t.append(t >= FRAC * ach); hit_u.append(u >= FRAC * ach)
    rows.append([r["sigma_cat"], r["seed"], f"{r['quality']['cluster_purity']:.3f}", r["quality"]["k_discovered"], f"{rho:.3f}", f"{a['b1_generator']['gap_ratio']:.1f}", f"{ach:.2f}",
                 f"{u:.2f} ({u / ach:.2f})", f"{t:.2f} ({t / ach:.2f})", ("yes" if u >= FRAC * ach else "no") if app else "n/a", ("yes" if t >= FRAC * ach else "no") if app else "n/a", f"{pred:.2f}", f"{err:.2f}"])
by = {}
for r, row in zip(runs, rows): by.setdefault(r["sigma_cat"], []).append(row)
lv = lambda s, col: f"{sum(x[col] == 'yes' for x in by[s])}/{len(by[s])}"
pred_ok = all(lv(s, 10) == f"{len(by[s])}/{len(by[s])}" for s in by) and len(hit_t) == len(runs)
medE = st.median(errs)
md = ["# E20 blind check: recalibrated gap criterion on fresh seeds 3-5 (σ_cat 0.4 and 0.6)\n",
      f"**Owner's prediction** (cluster-built gap clears 0.6 × the perfect-cluster gap on every seed at both noise levels, B2 + Tier 1): **{'CONFIRMED' if pred_ok else 'NOT confirmed'}**. "
      + "; ".join(f"σ {s}: B2 + Tier 1 meets it on {lv(s, 10)}, untreated on {lv(s, 9)}" for s in sorted(by)) + ".\n",
      f"**Corrected contamination model (informational, v_cat frozen at {V_CAT}):** median relative error {medE:.2f} (limit {ERR}) -> **{'PASSES' if medE <= ERR else 'FAILS'}**.\n",
      tab(["σ_cat", "seed", "Cluster purity", "K found", "True ρ", "Gap B1 twins", "Achievable gap (perfect clusters)", "Gap B2 untreated (ratio)", "Gap B2 + Tier 1 (ratio)", "Untreated meets", "Tier 1 meets", "Model-predicted untreated gap", "Model relative error"], rows)]
open(f"{D}/E20_REPORT.md", "w").write("\n".join(md)); print("\n".join(md[2:5]))
