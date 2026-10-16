"""Why the clusterer's purity falls at large sigma_cat, from data already saved (no new training).
Uses the 2,500 stored (cluster id, true category) points per run, the stored oracle-K purity, and a Monte Carlo ceiling from the generator.
True categories are used for evaluation only. Writes results/stage_b2_gapfix_sweep/CLUSTER_LIMITS.md."""
import glob, json, statistics as st, torch
from isj.worlds import HierarchicalMixtureWorld
D = "results/stage_b2_gapfix_sweep"
runs = sorted((json.load(open(f)) for f in glob.glob(f"{D}/sigma_cat_*/[0-9]*.json")), key=lambda r: (r["sigma_cat"], r["seed"]))
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
rows, example = [], []
for r in runs:
    cl, ct = torch.tensor(r["p7"]["cluster"]), torch.tensor(r["p7"]["true_cat"])
    Ks = cl.unique(); M = torch.stack([torch.bincount(ct[cl == k], minlength=6) for k in Ks])        # clusters x categories
    n = M.sum(1); pur = M.max(1).values / n
    imp, mid = int((pur < 0.7).sum()), int(((pur >= 0.7) & (pur < 0.9)).sum())
    mixed = int(((M > 0.2 * n[:, None]).sum(1) >= 2).sum()); split = int((((M.float() / M.sum(0, keepdim=True)) > 0.2).sum(0) >= 2).sum())
    q = r["quality"]; sil = q["silhouette_by_k"]
    rows.append([r["sigma_cat"], r["seed"], len(Ks), f"{float((M.max(1).values.sum() / n.sum())):.3f}", f"{q['cluster_purity_oracleK']:.3f}", imp, mid, len(Ks) - imp - mid, mixed, split])
    if r["seed"] == 0 and r["sigma_cat"] in (0.8, 1.0, 1.5):
        order = pur.argsort()
        example.append((r["sigma_cat"], [(int(Ks[i]), int(n[i]), float(pur[i]), {int(c): round(float(M[i, c] / n[i]), 2) for c in range(6) if M[i, c] > 0.15 * n[i]}) for i in order]))
ceil = []
for s in sorted({r["sigma_cat"] for r in runs}):
    acc = []
    for seed in range(3):
        w = HierarchicalMixtureWorld([4, 4, 4], [0.2, 0.7, 0.95], seed=seed, n_categories=6, n_identities=20, n_textures=2, sigma_cat=s)
        z, lab = w.sample_with_labels(60000)
        acc.append(float((torch.cdist(z[:, 8:], w.cat_c).argmin(1) == lab["cat"]).float().mean()))
    got = [r["quality"]["cluster_purity"] for r in runs if r["sigma_cat"] == s]; orc = [r["quality"]["cluster_purity_oracleK"] for r in runs if r["sigma_cat"] == s]
    ceil.append([s, f"{st.mean(acc):.3f}", f"{st.mean(got):.3f}", f"{st.mean(orc):.3f}", f"{st.mean(acc) - st.mean(got):+.3f}"])
md = ["# Why cluster purity falls at large sigma_cat (analysis of saved data; evaluation labels only)\n",
      "## Ceiling versus achieved purity (means over 3 seeds)\n",
      "Ceiling = purity of the best possible rule that sees only the true category block and knows the true category centres (nearest centre), by Monte Carlo from the generator. No clusterer working from the observations can exceed it. Purity grows trivially with the number of clusters, so purities with K = 9-12 are flattered relative to K = 6.\n",
      tab(["σ_cat", "Ceiling purity", "Achieved, discovered K", "Achieved, K = 6 (oracle count)", "Ceiling − achieved"], ceil),
      "\n## Impure clusters per run (from the 2,500 stored points per run)\n",
      tab(["σ_cat", "seed", "K found", "Sample purity", "Oracle-K (6) purity", "Clusters purity < 0.7", "0.7-0.9", "≥ 0.9", "Clusters mixing ≥ 2 categories (each > 20%)", "Categories split over ≥ 2 clusters"], rows),
      "\n## Example cluster compositions, seed 0 (cluster id, share of points, purity, categories above 15% with their share), lowest purity first\n"]
for s, cl in example:
    md.append(f"\n**σ_cat {s}** (K = {len(cl)})\n")
    md.append(tab(["Cluster", "Share of points", "Purity", "Categories (share)"], [[c, f"{n / sum(x[1] for x in cl):.3f}", f"{p:.2f}", ", ".join(f"cat {k}: {v}" for k, v in comp.items())] for c, n, p, comp in cl]))
open(f"{D}/CLUSTER_LIMITS.md", "w").write("\n".join(md))
print("\n".join(md[2:5]))
