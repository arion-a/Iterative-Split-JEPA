"""Stage B2 (construction): build the second split's pairs from the data.

Rung 1 uses generator-made pairs (as the paper does for its single split). For rung 2 we compare four
ways of making pairs, on the SAME trained encoder:
  generator : twins share the category exactly (the B1 setting; upper bound)
  label     : two samples with the same true category (what perfect clustering would give)
  kmeans    : cluster the rung-1 invariant output, pair samples within a cluster (the real B2)
  random    : unrelated pairs (should not work)
"""

from __future__ import annotations

import time

import torch

from . import audits
from .cluster import kmeans, pairs_within_clusters, purity
from .encoder import EncoderConfig, encode, train_encoder
from .engine import fit_rung, fit_whitener
from .worlds import CouplingMap, MixtureBlockWorld


def run_stage_b2(cfg: dict, seed: int, n_categories: int, verbose: bool = False) -> dict:
    t0 = time.time()
    w, e, s = cfg["world"], cfg["encoder"], cfg["split"]
    world = MixtureBlockWorld(list(w["block_dims"]), list(w["rhos"]), seed=seed, n_categories=n_categories,
                              sigma=w["sigma"], centre_scale=w["centre_scale"],
                              isotropic_centres=w.get("isotropic_centres", True))
    d, n = world.d, s["num_pairs"]
    observe = CouplingMap(d, w["coupling_layers"], w["coupling_strength"], w.get("obs_dim"), seed=seed)
    ecfg = EncoderConfig(in_dim=observe.obs_dim, latent_dim=d, hidden=e["hidden"], steps=e["steps"],
                         batch_size=e["batch_size"], lr=e["lr"], reg=e["reg"], var_weight=e["var_weight"],
                         sigreg_weight=e["sigreg_weight"], arch=e["arch"], objective=e["objective"],
                         coupling_layers=w["coupling_layers"])
    enc, train_log = train_encoder(world, observe, ecfg, seed + 77_777, verbose)
    wh = fit_whitener(encode(enc, observe, world.sample(s["num_whiten"])), 1e-5)
    R = lambda z: wh(encode(enc, observe, z))

    # ---- rung 1 (generator pairs, as in B1)
    u, v = world.correspondence_pairs(n, 1)
    fit1 = fit_rung(R(u), R(v), torch.eye(d), k=1, d_k=4)

    # ---- ground-truth probe for evaluation
    z_all, lab_all = world.sample_with_labels(s["probe_train"] + s["probe_test"])
    r_all = R(z_all)
    ntr = s["probe_train"]
    ztr, zte, rtr, rte = z_all[:ntr], z_all[ntr:], r_all[:ntr], r_all[ntr:]
    w_glob = audits.ridge_fit(ztr, rtr)
    a_hat = w_glob[:-1].T
    image = {k: a_hat[:, world.block_slice(k)] for k in (1, 2, 3)}
    global_r2 = audits.r2(w_glob, zte, rte)

    def leakage(V, Q, k):
        """The paper's a12 / a21 / block purity for one split (raw and normalized by sqrt of block size)."""
        est_v = audits.ridge_fit(ztr, rtr @ V)[:-1].T          # variant coords from true latents (d_L, d)
        est_q = audits.ridge_fit(ztr, rtr @ Q)[:-1].T          # invariant-content coords (d_H, d)
        own = list(range(*world.block_slice(k).indices(world.d)))
        slower = list(range(world.block_slice(k).stop, world.d))
        other = [c for c in range(world.d) if c not in own]
        a12, a21 = float(est_v[:, other].norm()), float(est_q[:, own].norm())
        good = est_v[:, own].square().sum() + est_q[:, slower].square().sum()
        dH, dL = Q.shape[1], V.shape[1]
        return {"a12_fro": a12, "a21_fro": a21, "a12_norm": a12 / dH**0.5, "a21_norm": a21 / dL**0.5,
                "block_purity": float(good / (est_v.square().sum() + est_q.square().sum()))}

    def evaluate(fit2):
        v_tr, v_te, q_tr, q_te = rtr @ fit2.V, rte @ fit2.V, rtr @ fit2.Q, rte @ fit2.Q
        return {**leakage(fit2.V, fit2.Q, 2), "global_r2": global_r2,
                "invariant_r2": audits.linear_r2(q_tr, ztr[:, 8:], q_te, zte[:, 8:]),
                "eigvals": [float(x) for x in fit2.eigvals],
                "angle_deg": audits.max_angle_deg(fit2.V, image[2]),
                "variant_r2": audits.linear_r2(v_tr, ztr[:, 4:8], v_te, zte[:, 4:8]),
                "core_invariant_r2": audits.linear_r2(q_tr, ztr[:, 8:], q_te, zte[:, 8:]),
                "nesting_deg": float(audits.principal_angles_deg(fit2.V, torch.cat([image[2], image[3]], 1)).max()),
                "gap_ratio": fit2.gap_ratio, "lambda_dk": float(fit2.eigvals[3])}

    rung1 = {"angle_deg": audits.max_angle_deg(fit1.V, image[1]),
             "variant_r2": audits.linear_r2(rtr @ fit1.V, ztr[:, :4], rte @ fit1.V, zte[:, :4]),
             "gap_ratio": fit1.gap_ratio, **leakage(fit1.V, fit1.Q, 1), "global_r2": global_r2,
             "invariant_r2": audits.linear_r2(rtr @ fit1.Q, ztr[:, 4:], rte @ fit1.Q, zte[:, 4:])}

    # ---- clustering of the rung-1 invariant output
    z_c, lab_c = world.sample_with_labels(s["cluster_samples"])
    r_c = R(z_c)
    inv = r_c @ fit1.Q                                          # (N, 8): identity + category content
    km_lab, _, _ = kmeans(inv, n_categories, restarts=s["kmeans_restarts"], seed=seed)
    pur = purity(km_lab, lab_c)
    ia, ib = pairs_within_clusters(km_lab, seed)
    misgroup = float((lab_c[ia] != lab_c[ib]).float().mean())

    def latents(name):
        if name == "generator": return world.correspondence_pairs(n, 2)
        if name == "label": return world.label_pairs(n)
        if name == "kmeans": return z_c[ia], z_c[ib]
        return world.random_pairs(n)

    arms = {}
    for name in ("generator", "label", "kmeans", "random"):
        zu, zv = latents(name)
        ru, rv = (r_c[ia], r_c[ib]) if name == "kmeans" else (R(zu), R(zv))
        arms[name] = evaluate(fit_rung(ru, rv, fit1.Q, k=2, d_k=4))
        # how close the paired samples really are in category space (raw units)
        arms[name]["category_pair_distance"] = float((zu[:, 8:] - zv[:, 8:]).norm(dim=1).mean())
    arms["kmeans"]["cluster_purity"] = pur
    arms["kmeans"]["misgrouped_pair_fraction"] = misgroup
    return {"seed": seed, "n_categories": n_categories, "rung1": rung1, "arms": arms, "cluster_purity": pur,
            "misgrouped_pair_fraction": misgroup, "encoder_final": train_log[-1], "seconds": round(time.time() - t0, 1)}
