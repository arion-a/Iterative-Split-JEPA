"""E11 verdict for a variant directory: the three registered floor-lowering criteria against the E12-run baseline.
    python experiments/build_e11_summary.py results/stage_b2_e11a E11a   (appends a section to <dir>/REPORT.md)"""
import glob, json, statistics as st, sys
D, NAME = sys.argv[1], sys.argv[2]
runs = sorted((json.load(open(f)) for f in glob.glob(f"{D}/sigma_cat_0.1/[0-9]*.json")), key=lambda r: r["seed"])
base = sorted((json.load(open(f)) for f in glob.glob("results/stage_b2_noop/sigma_cat_0.1/[0-9]*.json")), key=lambda r: r["seed"])
e15 = [json.load(open(f"results/diagnostics/e15/seed{s}.json")) for s in range(3)]
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
probe = [r["full_feature_probe_r2"]["texture"] for r in runs]; probe0 = [d["full_feature_probe_r2"]["texture"] for d in e15]
a1 = [r["rung1"]["angle_deg"] for r in runs]; a10 = [r["rung1"]["angle_deg"] for r in base]
a2 = [r["arms"]["b1_generator"]["angle_deg"] for r in runs]; a20 = [r["arms"]["b1_generator"]["angle_deg"] for r in base]
c1, c2, c3 = all(p >= 0.95 for p in probe), st.mean(a1) <= 2.8, st.mean(a2) <= 7.7
rows = [["(i) full-feature texture probe R², at least 0.95 on every seed", " / ".join(f"{x:.3f}" for x in probe0), " / ".join(f"{x:.3f}" for x in probe), "yes" if c1 else "**NO**"],
        ["(ii) mean rung-1 angle at most 2.8°", f"{st.mean(a10):.2f}", f"{st.mean(a1):.2f}", "yes" if c2 else "**NO**"],
        ["(iii) mean rung-2 angle, B1 arm, at most 7.7°", f"{st.mean(a20):.2f}", f"{st.mean(a2):.2f}", "yes" if c3 else "**NO**"]]
more = [["Recovered texture block R² (rung 1)", " / ".join(f"{r['rung1']['variant_r2']:.3f}" for r in base), " / ".join(f"{r['rung1']['variant_r2']:.3f}" for r in runs)],
        ["Global R²", " / ".join(f"{r['arms']['b1_generator']['global_r2']:.3f}" for r in base), " / ".join(f"{r['arms']['b1_generator']['global_r2']:.3f}" for r in runs)],
        ["Identity / category probe R²", " / ".join(f"{r['full_feature_probe_r2']['identity']:.3f}, {r['full_feature_probe_r2']['category']:.3f}" for r in [json.loads(json.dumps(d)) for d in e15]), " / ".join(f"{r['full_feature_probe_r2']['identity']:.3f}, {r['full_feature_probe_r2']['category']:.3f}" for r in runs)],
        ["Rung-1 angle per seed (°)", " / ".join(f"{x:.2f}" for x in a10), " / ".join(f"{x:.2f}" for x in a1)],
        ["Rung-2 angle, B1 arm, per seed (°)", " / ".join(f"{x:.2f}" for x in a20), " / ".join(f"{x:.2f}" for x in a2)],
        ["Rung-2 gap ratio, B2 + Tier 1", " / ".join(f"{r['arms']['b2_kmeans_purified']['gap_ratio']:.1f}" for r in base), " / ".join(f"{r['arms']['b2_kmeans_purified']['gap_ratio']:.1f}" for r in runs)],
        ["Cluster purity, discovered K", " / ".join(f"{r['quality']['cluster_purity']:.3f}, K={r['quality']['k_discovered']}" for r in base), " / ".join(f"{r['quality']['cluster_purity']:.3f}, K={r['quality']['k_discovered']}" for r in runs)]]
verdict = "CONFIRMED" if (c1 and c2 and c3) else "REFUTED"
md = [f"\n## {NAME} verdict on the registered floor-lowering prediction: **{verdict}**\n", tab(["Criterion", "Baseline (E12 run / E15)", f"{NAME}", "Met?"], rows),
      "\n### Other numbers, baseline vs " + NAME + " (per seed, 0 / 1 / 2)\n", tab(["Quantity", "Baseline", NAME], more)]
open(f"{D}/REPORT.md", "a").write("\n".join(md))
print(verdict, "| probe", [round(x, 3) for x in probe], "| rung1", round(st.mean(a1), 2), "| rung2 B1", round(st.mean(a2), 2))
