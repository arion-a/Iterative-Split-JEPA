"""Stage B2, formal version (docs/B2.md): can rung-2 pairs be BUILT from the rung-1 representation alone?

World: HierarchicalMixtureWorld (6 categories, 20 identities each, 2 textures each, all Gaussian inside).
Rung 1 uses generator twins (as in B1). For rung 2 we compare, on the SAME trained encoder and seed:
  b1_generator      generator twins (B1 with ground-truth pairs: the reference)
  b2_kmeans         clusters discovered from the rung-1 INVARIANT output, pairs within clusters (the real B2)
  b2_kmeans_oracleK the same with the planted count of 6 (informational)
  label_pairs       pairs sharing the true category (what perfect clustering would give; informational)
  c1_cross_cluster  pairs drawn from DIFFERENT discovered clusters
  c2_variant_clusters  clusters built from the rung-1 VARIANT (texture) output instead
  c3_singleton      every sample its own cluster: no valid pair exists
  c4_shuffled       cluster membership shuffled among samples, then paired within clusters (recorded only)
Ground truth is used only to generate data and to evaluate.
"""

from __future__ import annotations

import math
import time

import torch

from . import audits
from .cluster import kmeans, pairs_within_clusters, purity
from .encoder import EncoderConfig, encode, train_encoder
from .engine import fit_rung, fit_whitener
from .worlds import CouplingMap, HierarchicalMixtureWorld

ARMS_FIT = ["b1_generator", "b2_kmeans", "b2_kmeans_oracleK", "label_pairs", "c1_cross_cluster",
            "c2_variant_clusters", "c4_shuffled"]


def silhouette(x: torch.Tensor, labels: torch.Tensor) -> float:
    n = len(x)
    ks = labels.unique()
    if len(ks) < 2:
        return -1.0
    d = torch.cdist(x, x)
    onehot = torch.zeros(n, len(ks)); onehot[torch.arange(n), torch.searchsorted(ks, labels)] = 1
    sums, counts = d @ onehot, onehot.sum(0)
    own = torch.searchsorted(ks, labels)
    a = sums[torch.arange(n), own] / (counts[own] - 1).clamp_min(1)
    mean_other = sums / counts
    mean_other[torch.arange(n), own] = float("inf")
    b = mean_other.min(1).values
    s = (b - a) / torch.maximum(a, b)
    s[counts[own] <= 1] = 0
    return float(s.mean())


def discover_k(x: torch.Tensor, k_range=range(2, 13), subsample=3000, seed=0):
    g = torch.Generator().manual_seed(seed)
    sub = x[torch.randperm(len(x), generator=g)[:subsample]]
    scores = {}
    for k in k_range:
        lab, _, _ = kmeans(sub, k, restarts=3, iters=60, seed=seed)
        scores[k] = silhouette(sub, lab)
    return max(scores, key=scores.get), scores


def cross_cluster_pairs(labels: torch.Tensor, n: int, seed=0):
    g = torch.Generator().manual_seed(seed)
    i = torch.randint(0, len(labels), (3 * n,), generator=g)
    j = torch.randint(0, len(labels), (3 * n,), generator=g)
    ok = labels[i] != labels[j]
    return i[ok][:n], j[ok][:n]


def run_stage_b2_spec(cfg: dict, seed: int, sigma_cat: float, verbose: bool = False) -> dict:
    t0 = time.time()
    w, e, s = cfg["world"], cfg["encoder"], cfg["split"]
    floor = cfg["leak_floor"]
    world = HierarchicalMixtureWorld(list(w["block_dims"]), list(w["rhos"]), seed=seed, n_categories=w["n_categories"],
                                     n_identities=w["n_identities"], n_textures=w["n_textures"], sigma_cat=sigma_cat,
                                     sigma_id=w["sigma_id"], sigma_tex=w["sigma_tex"])
    d, n = world.d, s["num_pairs"]
    observe = CouplingMap(d, w["coupling_layers"], w["coupling_strength"], w.get("obs_dim"), seed=seed)
    ecfg = EncoderConfig(in_dim=observe.obs_dim, latent_dim=d, hidden=e["hidden"], steps=e["steps"], batch_size=e["batch_size"],
                         lr=e["lr"], reg=e["reg"], var_weight=e["var_weight"], sigreg_weight=e["sigreg_weight"], arch=e["arch"],
                         objective=e["objective"], coupling_layers=w["coupling_layers"])
    enc, train_log = train_encoder(world, observe, ecfg, seed + 77_777, verbose)
    wh = fit_whitener(encode(enc, observe, world.sample(s["num_whiten"])), 1e-5)
    R = lambda z: wh(encode(enc, observe, z))

    # ---- evaluation set (ground truth enters only here)
    ntr = s["probe_train"]
    z_all, _ = world.sample_with_labels(ntr + s["probe_test"])
    r_all = R(z_all)
    ztr, zte, rtr, rte = z_all[:ntr], z_all[ntr:], r_all[:ntr], r_all[ntr:]
    w_glob = audits.ridge_fit(ztr, rtr)
    a_hat = w_glob[:-1].T
    image = {k: a_hat[:, world.block_slice(k)] for k in (1, 2, 3)}
    global_r2 = audits.r2(w_glob, zte, rte)
    cols = lambda k: list(range(*world.block_slice(k).indices(d)))
    rank_delta = cfg["rank_test_delta"]

    def leak(V, Q, k):
        own, slower = cols(k), list(range(world.block_slice(k).stop, d))
        other = [c for c in range(d) if c not in own]
        est_v = audits.ridge_fit(ztr, rtr @ V)[:-1].T
        est_q = audits.ridge_fit(ztr, rtr @ Q)[:-1].T
        a12, a21 = float(est_v[:, other].norm()), float(est_q[:, own].norm())
        good = est_v[:, own].square().sum() + est_q[:, slower].square().sum()
        r_rest_own = audits.leakage_test(ztr[:, slower], rtr @ V, zte[:, slower], rte @ V, n_perm=1)["r2"]
        r_own_rest = audits.leakage_test(ztr[:, own], rtr @ Q, zte[:, own], rte @ Q, n_perm=1)["r2"]
        mx = max(abs(r_rest_own), abs(r_own_rest))
        return {"a12_fro": a12, "a21_fro": a21, "a12_norm": a12 / Q.shape[1] ** 0.5, "a21_norm": a21 / V.shape[1] ** 0.5,
                "block_purity": float(good / (est_v.square().sum() + est_q.square().sum())),
                "leak_r2": {"rest->own": r_rest_own, "own->rest": r_own_rest}, "max_leak_abs_r2": mx,
                "leak_any_significant": mx >= floor}

    def rank_flag(fit, ru, rv):
        b = float((ru - rv).square().sum(1).max()) ** 0.5
        return audits.rank_deficient(torch.diag(fit.eigvals[: fit.d_k]), len(ru), b, rank_delta)

    # ---- rung 1: generator twins (as in B1)
    u1, v1 = world.correspondence_pairs(n, 1)
    ru1, rv1 = R(u1), R(v1)
    fit1 = fit_rung(ru1, rv1, torch.eye(d), k=1, d_k=4)
    rung1 = {"k": 1, "angle_deg": audits.max_angle_deg(fit1.V, image[1]),
             "variant_r2": audits.linear_r2(rtr @ fit1.V, ztr[:, :4], rte @ fit1.V, zte[:, :4]),
             "invariant_r2": audits.linear_r2(rtr @ fit1.Q, ztr[:, 4:], rte @ fit1.Q, zte[:, 4:]),
             "gap_ratio": fit1.gap_ratio, "lambda_dk": float(fit1.eigvals[3]), "eigvals": [float(x) for x in fit1.eigvals],
             "rank_deficient": rank_flag(fit1, ru1, rv1), "global_r2": global_r2, **leak(fit1.V, fit1.Q, 1)}

    # ---- the clustering set: rung-1 invariant and variant outputs of N unlabelled samples
    z_c, lab_c = world.sample_with_labels(s["cluster_samples"])
    cat_c = lab_c["cat"]
    r_c = R(z_c)
    inv, var = r_c @ fit1.Q, r_c @ fit1.V
    k_true = w["n_categories"]
    k_star, sil = discover_k(inv, seed=seed)
    km_lab, _, _ = kmeans(inv, k_star, restarts=s["kmeans_restarts"], seed=seed)
    km6_lab, _, _ = kmeans(inv, k_true, restarts=s["kmeans_restarts"], seed=seed)
    var_lab, _, _ = kmeans(var, k_star, restarts=s["kmeans_restarts"], seed=seed)
    shuffled_lab = km_lab[torch.randperm(len(km_lab), generator=torch.Generator().manual_seed(seed + 5))]

    # ---- pairs for each arm: (representation u, representation v, true latents u, true latents v)
    def idx_arm(ia, ib):
        return r_c[ia], r_c[ib], z_c[ia], z_c[ib], cat_c[ia], cat_c[ib]

    def gen_arm(fn):
        zu, zv = fn(n)
        return R(zu), R(zv), zu, zv, None, None

    pairs = {"b1_generator": gen_arm(lambda m: world.correspondence_pairs(m, 2)),
             "label_pairs": gen_arm(world.label_pairs),
             "b2_kmeans": idx_arm(*pairs_within_clusters(km_lab, seed)),
             "b2_kmeans_oracleK": idx_arm(*pairs_within_clusters(km6_lab, seed)),
             "c1_cross_cluster": idx_arm(*cross_cluster_pairs(km_lab, n, seed)),
             "c2_variant_clusters": idx_arm(*pairs_within_clusters(var_lab, seed)),
             "c4_shuffled": idx_arm(*pairs_within_clusters(shuffled_lab, seed))}
    singleton_pairs = len(pairs_within_clusters(torch.arange(len(inv)))[0])        # C3: every sample alone -> zero pairs

    arms, construction = {}, {}
    for name, (ru, rv, zu, zv, cu, cv) in pairs.items():
        fit2 = fit_rung(ru, rv, fit1.Q, k=2, d_k=4)
        L = leak(fit2.V, fit2.Q, 2)
        arms[name] = {
            "k": 2, "angle_deg": audits.max_angle_deg(fit2.V, image[2]),
            "variant_r2": audits.linear_r2(rtr @ fit2.V, ztr[:, 4:8], rte @ fit2.V, zte[:, 4:8]),
            "invariant_r2": audits.linear_r2(rtr @ fit2.Q, ztr[:, 8:], rte @ fit2.Q, zte[:, 8:]),
            "global_r2": global_r2, "gap_ratio": fit2.gap_ratio, "lambda_dk": float(fit2.eigvals[3]),
            "eigvals": [float(x) for x in fit2.eigvals], "rank_deficient": rank_flag(fit2, ru, rv),
            "nesting_angle_deg": float(audits.principal_angles_deg(fit2.V, torch.cat([image[2], image[3]], 1)).max()),
            "n_pairs": len(ru), **L}
        arms[name]["core_invariant_r2"] = arms[name]["invariant_r2"]
        validity = None if cu is None else float((cu == cv).float().mean())
        construction[name] = {"n_pairs": len(ru), "pair_validity": validity,
                              "category_pair_distance": float((zu[:, 8:] - zv[:, 8:]).norm(dim=1).mean())}
    construction["b1_generator"]["pair_validity"] = 1.0
    construction["label_pairs"]["pair_validity"] = 1.0
    construction["c3_singleton"] = {"n_pairs": singleton_pairs, "pair_validity": None}
    quality = {"cluster_purity": purity(km_lab, cat_c), "cluster_purity_oracleK": purity(km6_lab, cat_c),
               "variant_cluster_purity": purity(var_lab, cat_c), "k_discovered": int(k_star), "k_true": k_true,
               "silhouette_by_k": {str(k): v for k, v in sil.items()},
               "misgroup_rate": 1 - purity(km_lab, cat_c)}

    # ---- P7: 2-D picture of the rung-1 invariant content (projection uses true categories: evaluation/picture only)
    g = torch.Generator().manual_seed(seed + 9)
    sub = torch.randperm(len(inv), generator=g)[:2500]
    means = torch.stack([inv[cat_c == c].mean(0) for c in cat_c.unique()])
    sb = (means - inv.mean(0)).T @ (means - inv.mean(0))
    vecs = torch.linalg.eigh(sb)[1][:, -2:]
    xy = (inv[sub] - inv.mean(0)) @ vecs
    p7 = {"x": [round(float(v), 3) for v in xy[:, 0]], "y": [round(float(v), 3) for v in xy[:, 1]],
          "true_cat": [int(v) for v in cat_c[sub]], "cluster": [int(v) for v in km_lab[sub]]}

    bound = {"misgroup_rate": quality["misgroup_rate"], "a21_rung1": rung1["a21_fro"],
             "a21_generator_rung2": arms["b1_generator"]["a21_fro"], "a21_kmeans_rung2": arms["b2_kmeans"]["a21_fro"],
             "bound_norm": rung1["a21_fro"] * (1 + 2 * quality["misgroup_rate"]),
             "bound_sqrt": rung1["a21_fro"] * math.sqrt(1 + 2 * quality["misgroup_rate"])}
    return {"seed": seed, "sigma_cat": sigma_cat, "rung1": rung1, "arms": arms, "construction": construction,
            "quality": quality, "bound": bound, "p7": p7, "encoder_final": train_log[-1], "seconds": round(time.time() - t0, 1)}
