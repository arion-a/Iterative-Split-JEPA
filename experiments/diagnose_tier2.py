"""Tier 2 diagnosis (analysis only, no rebuild): why does the clusterer find 5 categories, not 6, in the clean B2 world?
Rebuilds each seed's encoder and rung-1 output exactly as run_stage_b2_spec does (same seeds, same config), then examines the
rung-1 INVARIANT output on the 60,000 clustering samples. True categories are used only to describe which categories merge
(evaluation); nothing here feeds back into cluster construction.
    python experiments/diagnose_tier2.py --seed 0   ->   results/diagnostics/tier2/seed<N>.json"""
import argparse, json, os
import torch, yaml
from isj.cluster import kmeans, purity
from isj.encoder import EncoderConfig, encode, train_encoder
from isj.engine import fit_rung, fit_whitener
from isj.stage_b2_spec import silhouette
from isj.worlds import CouplingMap, HierarchicalMixtureWorld

ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, required=True); a = ap.parse_args()
cfg = yaml.safe_load(open("configs/stage_b2_nesting.yaml")); w, e, s = cfg["world"], cfg["encoder"], cfg["split"]
seed, sg = a.seed, cfg["sweep"]["clean_sigma_cat"]
world = HierarchicalMixtureWorld(list(w["block_dims"]), list(w["rhos"]), seed=seed, n_categories=w["n_categories"], n_identities=w["n_identities"],
                                 n_textures=w["n_textures"], sigma_cat=sg, sigma_id=w["sigma_id"], sigma_tex=w["sigma_tex"])
d = world.d
observe = CouplingMap(d, w["coupling_layers"], w["coupling_strength"], w.get("obs_dim"), seed=seed)
ecfg = EncoderConfig(in_dim=observe.obs_dim, latent_dim=d, hidden=e["hidden"], steps=e["steps"], batch_size=e["batch_size"], lr=e["lr"], reg=e["reg"],
                     var_weight=e["var_weight"], sigreg_weight=e["sigreg_weight"], arch=e["arch"], objective=e["objective"], coupling_layers=w["coupling_layers"])
enc, _ = train_encoder(world, observe, ecfg, seed + 77_777, False)
wh = fit_whitener(encode(enc, observe, world.sample(s["num_whiten"])), 1e-5)
R = lambda z: wh(encode(enc, observe, z))
u1, v1 = world.correspondence_pairs(s["num_pairs_per_rung"][0], 1)
fit1 = fit_rung(R(u1), R(v1), torch.eye(d), k=1, d_k=4)
z, lab = world.sample_with_labels(s["cluster_samples"]); cat = lab["cat"]
inv = R(z) @ fit1.Q                                     # what the clusterer sees (8 dims)
K = w["n_categories"]

out = {"seed": seed}
out["category_sizes"] = torch.bincount(cat, minlength=K).tolist()
mu = torch.stack([inv[cat == c].mean(0) for c in range(K)])
within = torch.stack([(inv[cat == c] - mu[c]).norm(dim=1).mean() for c in range(K)])
dist = torch.cdist(mu, mu)
pairs = [(float(dist[i, j]), i, j) for i in range(K) for j in range(i + 1, K)]
pairs.sort()
out["centre_distances_sorted"] = [{"d": round(x, 3), "cats": [i, j]} for x, i, j in pairs]
out["mean_within_cluster_radius"] = [round(float(x), 3) for x in within]
out["closest_pair_ratio"] = round(pairs[0][0] / float(within.mean()), 3)          # centre distance / typical radius
out["distance_to_largest"] = round(pairs[-1][0] / float(within.mean()), 3)
# what K=5 k-means does (as the pipeline does: silhouette-chosen K=5, 10 restarts, seed = run seed)
lab5, _, in5 = kmeans(inv, 5, restarts=s["kmeans_restarts"], seed=seed)
tbl = torch.zeros(5, K, dtype=torch.long)
for c in range(5):
    tbl[c] = torch.bincount(cat[lab5 == c], minlength=K)
out["k5_contingency_cluster_by_category"] = tbl.tolist()
merged = [int(c) for c in range(5) if (tbl[c] > 0.2 * tbl[c].sum()).sum() >= 2]
out["k5_merged_categories"] = [int(x) for x in (tbl[merged[0]] > 0.2 * tbl[merged[0]].sum()).nonzero().flatten()] if merged else None
out["k5_inertia"], out["k5_purity"] = round(in5, 1), round(purity(lab5, cat), 4)
# K=6: init sensitivity (20 different seeds, 1 restart each, and 10 restarts)
inert, pur = [], []
for sd in range(20):
    l6, _, i6 = kmeans(inv, 6, restarts=1, seed=100 + sd)
    inert.append(round(i6, 1)); pur.append(round(purity(l6, cat), 3))
out["k6_single_init_purity"] = pur; out["k6_single_init_inertia"] = inert
l6b, _, i6b = kmeans(inv, 6, restarts=s["kmeans_restarts"], seed=seed)
out["k6_10restart_purity"], out["k6_10restart_inertia"] = round(purity(l6b, cat), 4), round(i6b, 1)
# silhouette: K=5 vs K=6 on 20 different 3000-point subsamples (the pipeline uses one) and on 12000 points
rng = torch.Generator().manual_seed(seed + 1)
diff = []
for r in range(20):
    sub = inv[torch.randperm(len(inv), generator=rng)[:3000]]
    l5s, _, _ = kmeans(sub, 5, restarts=3, iters=60, seed=r); l6s, _, _ = kmeans(sub, 6, restarts=3, iters=60, seed=r)
    diff.append(round(silhouette(sub, l6s) - silhouette(sub, l5s), 4))
out["silhouette_k6_minus_k5_over_20_subsamples"] = diff
out["silhouette_k6_wins_count"] = int(sum(x > 0 for x in diff))
sub = inv[torch.randperm(len(inv), generator=rng)[:12000]]
l5s, _, _ = kmeans(sub, 5, restarts=3, iters=60, seed=0); l6s, _, _ = kmeans(sub, 6, restarts=3, iters=60, seed=0)
out["silhouette_k5_k6_12000pts"] = [round(silhouette(sub, l5s), 4), round(silhouette(sub, l6s), 4)]
os.makedirs("results/diagnostics/tier2", exist_ok=True)
json.dump(out, open(f"results/diagnostics/tier2/seed{seed}.json", "w"), indent=1)
print("done", seed)
