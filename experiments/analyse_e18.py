"""E18 evaluation (decision rule frozen in docs/EVIDENCE.md before the run): spectral K against the silhouette K; writes results/stage_b2_e18/E18_REPORT.md."""
import glob, json, statistics as st
D = "results/stage_b2_e18"
runs = sorted((json.load(open(f)) for f in glob.glob(f"{D}/sigma_cat_*/[0-9]*.json")), key=lambda r: (r["sigma_cat"], r["seed"]))
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
rows = []
for r in runs:
    q, sp, a = r["quality"], r["quality"]["spectral"], r["arms"]
    g = sorted(sp["info"]["gaps"].values(), reverse=True); ach = a["label_pairs"]["gap_ratio"]
    sg, sp_u, sp_t, sil_u, sil_t = a["b2_spectral"]["gap_ratio"], a["b2_spectral"]["gap_ratio"], a["b2_spectral_purified"]["gap_ratio"], a["b2_kmeans"]["gap_ratio"], a["b2_kmeans_purified"]["gap_ratio"]
    rows.append([r["sigma_cat"], r["seed"], q["k_discovered"], sp["k"], f"{q['cluster_purity']:.3f}", f"{sp['purity']:.3f}", f"{1 - r['construction']['b2_kmeans']['pair_validity']:.3f}",
                 f"{1 - r['construction']['b2_spectral']['pair_validity']:.3f}", f"{g[0] / max(g[1], 1e-9):.2f}", f"{ach:.2f}", f"{sil_u:.2f} / {sil_t:.2f}", f"{sp_u:.2f} / {sp_t:.2f}",
                 ("yes" if sp_t >= 0.6 * ach else "no") if ach >= 3 else "n/a"])
by = {}
for r in runs: by.setdefault(r["sigma_cat"], []).append(r)
ks = [r["quality"]["spectral"]["k"] for r in runs]; n6 = sum(k == 6 for k in ks)
conf = len(runs) == 18 and n6 == 18
per = [[s, " / ".join(str(r["quality"]["k_discovered"]) for r in R), " / ".join(str(r["quality"]["spectral"]["k"]) for r in R), f"{sum(r['quality']['spectral']['k'] == 6 for r in R)}/{len(R)}",
        f"{sum(r['quality']['k_discovered'] == 6 for r in R)}/{len(R)}", f"{st.mean(r['quality']['cluster_purity'] for r in R):.3f}", f"{st.mean(r['quality']['spectral']['purity'] for r in R):.3f}"] for s, R in sorted(by.items())]
md = ["# E18 report: spectral (Laplacian eigengap) choice of the cluster count versus the silhouette rule\n",
      f"**Verdict:** spectral K = 6 in {n6} of {len(runs)} runs -> **E18 {'CONFIRMED' if conf else 'REFUTED'}** (rule: K = 6 in all 18 runs at σ_cat 0.1, 0.4, 0.6; selector constants fixed before the run).\n",
      "## By noise level (seeds in the order they appear in the table below)\n", tab(["σ_cat", "Silhouette K", "Spectral K", "Spectral K = 6", "Silhouette K = 6", "Purity, silhouette (mean)", "Purity, spectral (mean)"], per),
      "\n## Every run\n", tab(["σ_cat", "seed", "K silhouette", "K spectral", "Purity silhouette", "Purity spectral", "ρ silhouette", "ρ spectral", "Top eigengap / second", "Achievable gap (perfect clusters)", "Rung-2 gap: silhouette arm, untreated / Tier 1", "spectral arm, untreated / Tier 1", "Spectral + Tier 1 meets E20 criterion"], rows)]
open(f"{D}/E18_REPORT.md", "w").write("\n".join(md)); print("\n".join(md[:3])); print(tab(["σ_cat", "Silhouette K", "Spectral K", "Spectral K = 6", "Silhouette K = 6", "Purity sil", "Purity spec"], per))
