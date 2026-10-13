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
                              sigma=w["sigma"], centre_scale=w["centre_scale"])
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
    a_hat = audits.ridge_fit(ztr, rtr)[:-1].T
    image = {k: a_hat[:, world.block_slice(k)] for k in (1, 2, 3)}

    def evaluate(fit2):
        v_tr, v_te, q_tr, q_te = rtr @ fit2.V, rte @ fit2.V, rtr @ fit2.Q, rte @ fit2.Q
        return {"angle_deg": audits.max_angle_deg(fit2.V, image[2]),
                "variant_r2": audits.linear_r2(v_tr, ztr[:, 4:8], v_te, zte[:, 4:8]),
                "core_invariant_r2": audits.linear_r2(q_tr, ztr[:, 8:], q_te, zte[:, 8:]),
                "nesting_deg": float(audits.principal_angles_deg(fit2.V, torch.cat([image[2], image[3]], 1)).max()),
                "gap_ratio": fit2.gap_ratio, "lambda_dk": float(fit2.eigvals[3])}

    rung1 = {"angle_deg": audits.max_angle_deg(fit1.V, image[1]),
             "variant_r2": audits.linear_r2(rtr @ fit1.V, ztr[:, :4], rte @ fit1.V, zte[:, :4]),
             "gap_ratio": fit1.gap_ratio}

    # ---- clustering of the rung-1 invariant output
    z_c, lab_c = world.sample_with_labels(s["cluster_samples"])
    r_c = R(z_c)
    inv = r_c @ fit1.Q                                          # (N, 8): identity + category content
    km_lab, _, _ = kmeans(inv, n_categories, restarts=s["kmeans_restarts"], seed=seed)
    pur = purity(km_lab, lab_c)
    ia, ib = pairs_within_clusters(km_lab, seed)
    misgroup = float((lab_c[ia] != lab_c[ib]).float().mean())

    arms = {}
    for name, pairs in {
        "generator": lambda: tuple(map(R, world.correspondence_pairs(n, 2))),
        "label": lambda: tuple(map(R, world.label_pairs(n))),
        "kmeans": lambda: (r_c[ia], r_c[ib]),
        "random": lambda: tuple(map(R, world.random_pairs(n))),
    }.items():
        ru, rv = pairs()
        arms[name] = evaluate(fit_rung(ru, rv, fit1.Q, k=2, d_k=4))
    arms["kmeans"]["cluster_purity"] = pur
    arms["kmeans"]["misgrouped_pair_fraction"] = misgroup
    return {"seed": seed, "n_categories": n_categories, "rung1": rung1, "arms": arms, "cluster_purity": pur,
            "misgrouped_pair_fraction": misgroup, "encoder_final": train_log[-1], "seconds": round(time.time() - t0, 1)}
