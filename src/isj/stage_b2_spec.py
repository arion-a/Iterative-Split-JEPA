"""Stage B2, formal version (docs/B2.md): can rung-2 pairs be BUILT from the rung-1 representation alone?

World: HierarchicalMixtureWorld (6 categories, 20 identities each, 2 textures each, all Gaussian inside).
Rung 1 uses generator twins (as in B1). For rung 2 we compare, on the SAME trained encoder and seed:
  b1_generator      generator twins (B1 with ground-truth pairs: the reference)
  b2_kmeans         clusters discovered from the rung-1 INVARIANT output, pairs within clusters (the real B2)
  b2_kmeans_oracleK the same with the planted count of 6 (informational)
  b2_slowk          (option cluster.slow_k, plan G4-K) count chosen in the slow subspace of the invariant output, pairs within clusters there
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
from .cluster import kmeans, pairs_within_clusters, purity, slow_subspace_k, spectral_k
from .encoder import EncoderConfig, encode, train_encoder
from .engine import fit_rung, fit_whitener, purify_pairs
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
    n1, n2 = (s["num_pairs_per_rung"] if "num_pairs_per_rung" in s else (n, n))
    n = n2
    nest = cfg.get("nesting_enforcement", "hard")
    observe = CouplingMap(d, w["coupling_layers"], w["coupling_strength"], w.get("obs_dim"), seed=seed)
    ecfg = EncoderConfig(in_dim=observe.obs_dim, latent_dim=d, hidden=e["hidden"], steps=e["steps"], batch_size=e["batch_size"],
                         lr=e["lr"], reg=e["reg"], var_weight=e["var_weight"], sigreg_weight=e["sigreg_weight"], arch=e["arch"],
                         objective=e["objective"], coupling_layers=w["coupling_layers"], horizon=e.get("horizon", 1))
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
    probe_r2 = {nm: audits.linear_r2(rtr, ztr[:, sl], rte, zte[:, sl]) for nm, sl in (("texture", slice(0, 4)), ("identity", slice(4, 8)), ("category", slice(8, 12)))}   # E15 measure: full features -> true block
    # two truths for the rung-1 invariant content H1*: span of the probe images of blocks 2,3 (gate definition),
    # and the orthogonal complement of block 1's image (what the method targets) -- informational (addition)
    # E22 (probe-image explanation, tested directly): how far the block images are from orthogonal, and the identity image taken orthogonal to the texture image
    q_tex = audits.orth(image[1])
    image2_orth = image[2] - q_tex @ (q_tex.T @ image[2])
    image_geometry = {"min_angle_texture_vs_identity_category_deg": float(audits.principal_angles_deg(image[1], torch.cat([image[2], image[3]], 1)).min()),
                      "min_angle_texture_vs_identity_deg": float(audits.principal_angles_deg(image[1], image[2]).min()),
                      "min_angle_identity_vs_category_deg": float(audits.principal_angles_deg(image[2], image[3]).min()),
                      "identity_image_energy_removed": float(1 - image2_orth.square().sum() / image[2].square().sum())}
    h_span = torch.cat([image[2], image[3]], 1)
    u_, _, _ = torch.linalg.svd(image[1], full_matrices=True)
    h_perp = u_[:, 4:]
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
    u1, v1 = world.correspondence_pairs(n1, 1)
    ru1, rv1 = R(u1), R(v1)
    fit1 = fit_rung(ru1, rv1, torch.eye(d), k=1, d_k=4, nesting_enforcement=nest)
    rung1 = {"k": 1, "angle_deg": audits.max_angle_deg(fit1.V, image[1]),
             "variant_r2": audits.linear_r2(rtr @ fit1.V, ztr[:, :4], rte @ fit1.V, zte[:, :4]),
             "invariant_r2": audits.linear_r2(rtr @ fit1.Q, ztr[:, 4:], rte @ fit1.Q, zte[:, 4:]),
             "gap_ratio": fit1.gap_ratio, "lambda_dk": float(fit1.eigvals[3]), "eigvals": [float(x) for x in fit1.eigvals],
             "rank_deficient": rank_flag(fit1, ru1, rv1), "global_r2": global_r2, **leak(fit1.V, fit1.Q, 1),
             "n_pairs": len(ru1), "rank_monitor": audits.rank_monitor(fit1),
             "inherited_span_deg": float(audits.principal_angles_deg(fit1.Q, h_span).max()),
             "inherited_perp_deg": float(audits.principal_angles_deg(fit1.Q, h_perp).max())}

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
    spec = None
    if cfg.get("cluster", {}).get("spectral_k", False):          # E18: cluster count by Laplacian eigengap instead of the silhouette
        k_spec, spec_info = spectral_k(inv, seed=seed)
        spec_lab, _, _ = kmeans(inv, k_spec, restarts=s["kmeans_restarts"], seed=seed)
        spec = {"k": int(k_spec), "info": spec_info, "purity": purity(spec_lab, cat_c)}
    slowk, slow_lab = None, None
    if cfg.get("cluster", {}).get("slow_k", False):               # G4-K: cluster count in the slow subspace of the invariant output
        gstate = world._g.get_state()                              # adjacent frames drawn without disturbing the random state the other arms use
        ta, tb = world.transition_pairs(s.get("slowk_pairs", 20000))
        world._g.set_state(gstate)
        ia, ib = R(ta) @ fit1.Q, R(tb) @ fit1.Q
        k_slow, sinfo = slow_subspace_k(inv, ia, ib, seed=seed)
        k_shuf, shinfo = slow_subspace_k(inv, ia, ib[torch.randperm(len(ib), generator=torch.Generator().manual_seed(seed + 7))], seed=seed)   # control: time order destroyed
        slowk = {"k": None if k_slow is None else int(k_slow), "abstained": k_slow is None, "d": sinfo["d"], "ratio": sinfo["ratio"],
                 "change_eigvals": sinfo["eigvals"], "control_shuffled_time": {"k": None if k_shuf is None else int(k_shuf), "abstained": shinfo["abstained"], "ratio": shinfo["ratio"], "d": shinfo["d"]}}
        if k_slow is not None:
            basis = sinfo["basis"]
            slow_lab, _, _ = kmeans(inv @ basis, k_slow, restarts=s["kmeans_restarts"], seed=seed)
            slowk["purity"] = purity(slow_lab, cat_c)
            slowk["subspace_angle_deg"] = float(audits.principal_angles_deg(fit1.Q @ basis, image[3]).max())   # evaluation only: slow subspace vs the true category image
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
    arm_opts, purify_info, noop_info = {}, None, None
    if cfg.get("purify"):                                      # decision D10a: Tier 1 (purification) and Tier 4 (within-H1 whitening)
        ru0, rv0, zu0, zv0, cu0, cv0 = pairs["b2_kmeans"]
        keep, iters = purify_pairs(ru0, rv0, fit1.Q, 4, factor=cfg["purify"]["factor"], max_iter=cfg["purify"]["max_iter"])
        sub = (ru0[keep], rv0[keep], zu0[keep], zv0[keep], cu0[keep], cv0[keep])
        pairs["b2_kmeans_purified"] = sub
        if cfg["purify"].get("tier4", False):                  # D11: Tier 4 is opt-in (demoted); historic configs set tier4: true
            pairs["b2_kmeans_purified_whitened"] = sub
            arm_opts["b2_kmeans_purified_whitened"] = {"within_whitening": True}
        if cfg.get("noop_control"):                                  # E10 no-op control: Tier 1 on B1's clean generator-twin pairs
            ru1c, rv1c, zu1c, zv1c, cu1c, cv1c = pairs["b1_generator"]
            keepc, itersc = purify_pairs(ru1c, rv1c, fit1.Q, 4, factor=cfg["purify"]["factor"], max_iter=cfg["purify"]["max_iter"])
            pairs["b1_generator_purified"] = (ru1c[keepc], rv1c[keepc], zu1c[keepc], zv1c[keepc], None, None)
            noop_info = {"n_pairs": len(keepc), "n_trimmed": int((~keepc).sum()), "trimmed_fraction": float((~keepc).float().mean()), "iterations": itersc}
        purify_info = {"iterations": iters, "kept_fraction": float(keep.float().mean()), "n_kept": int(keep.sum()),
                       "validity_before": float((cu0 == cv0).float().mean()), "validity_after": float((cu0[keep] == cv0[keep]).float().mean()),
                       "valid_kept": float(keep[cu0 == cv0].float().mean()), "invalid_dropped": float((~keep)[cu0 != cv0].float().mean()) if (cu0 != cv0).any() else None}
    if spec is not None:
        pairs["b2_spectral"] = idx_arm(*pairs_within_clusters(spec_lab, seed))
        if cfg.get("purify"):
            ru_s, rv_s, zu_s, zv_s, cu_s, cv_s = pairs["b2_spectral"]
            keep_s, _ = purify_pairs(ru_s, rv_s, fit1.Q, 4, factor=cfg["purify"]["factor"], max_iter=cfg["purify"]["max_iter"])
            pairs["b2_spectral_purified"] = (ru_s[keep_s], rv_s[keep_s], zu_s[keep_s], zv_s[keep_s], cu_s[keep_s], cv_s[keep_s])
    if slow_lab is not None:
        pairs["b2_slowk"] = idx_arm(*pairs_within_clusters(slow_lab, seed))
        if cfg.get("purify"):
            ru_k, rv_k, zu_k, zv_k, cu_k, cv_k = pairs["b2_slowk"]
            keep_k, _ = purify_pairs(ru_k, rv_k, fit1.Q, 4, factor=cfg["purify"]["factor"], max_iter=cfg["purify"]["max_iter"])
            pairs["b2_slowk_purified"] = (ru_k[keep_k], rv_k[keep_k], zu_k[keep_k], zv_k[keep_k], cu_k[keep_k], cv_k[keep_k])
    singleton_pairs = len(pairs_within_clusters(torch.arange(len(inv)))[0])        # C3: every sample alone -> zero pairs

    arms, construction = {}, {}
    for name, (ru, rv, zu, zv, cu, cv) in pairs.items():
        fit2 = fit_rung(ru, rv, fit1.Q, k=2, d_k=4, nesting_enforcement=nest, **arm_opts.get(name, {}))
        L = leak(fit2.V, fit2.Q, 2)
        arms[name] = {
            "k": 2, "angle_deg": audits.max_angle_deg(fit2.V, image[2]),
            "variant_r2": audits.linear_r2(rtr @ fit2.V, ztr[:, 4:8], rte @ fit2.V, zte[:, 4:8]),
            "invariant_r2": audits.linear_r2(rtr @ fit2.Q, ztr[:, 8:], rte @ fit2.Q, zte[:, 8:]),
            "global_r2": global_r2, "gap_ratio": fit2.gap_ratio, "lambda_dk": float(fit2.eigvals[3]),
            "eigvals": [float(x) for x in fit2.eigvals], "rank_deficient": rank_flag(fit2, ru, rv),
            "nesting_angle_deg": float(audits.principal_angles_deg(fit2.V, torch.cat([image[2], image[3]], 1)).max()),
            "V": [[float(x) for x in row] for row in fit2.V.T] if cfg.get("save_subspaces") else None,
            "angle_orth_deg": audits.max_angle_deg(fit2.V, image2_orth),
            "nesting_perp_deg": float(audits.principal_angles_deg(fit2.V, h_perp).max()),
            "rank_monitor": audits.rank_monitor(fit2), "n_pairs": len(ru), **L}
        arms[name]["core_invariant_r2"] = arms[name]["invariant_r2"]
        validity = None if cu is None else float((cu == cv).float().mean())
        construction[name] = {"n_pairs": len(ru), "pair_validity": validity,
                              "category_pair_distance": float((zu[:, 8:] - zv[:, 8:]).norm(dim=1).mean())}
    construction["b1_generator"]["pair_validity"] = 1.0
    construction["label_pairs"]["pair_validity"] = 1.0
    construction["c3_singleton"] = {"n_pairs": singleton_pairs, "pair_validity": None}
    quality = {"cluster_purity": purity(km_lab, cat_c), "cluster_purity_oracleK": purity(km6_lab, cat_c),
               "variant_cluster_purity": purity(var_lab, cat_c), "k_discovered": int(k_star), "k_true": k_true, "spectral": spec, "slowk": slowk,
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
    return {"seed": seed, "nesting_enforcement": nest, "pair_budgets": [n1, n2], "sigma_cat": sigma_cat, "rung1": rung1, "arms": arms, "construction": construction,
            "quality": quality, "full_feature_probe_r2": probe_r2, "image_geometry": image_geometry, "horizon": e.get("horizon", 1), "purify": purify_info, "noop_control": noop_info, "bound": bound, "p7": p7, "encoder_final": train_log[-1], "seconds": round(time.time() - t0, 1)}
