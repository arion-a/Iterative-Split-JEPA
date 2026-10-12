"""Stage A: does the full pipeline (trained encoder, frozen) recover the planted 2-block split?

Pipeline (plan §4.1): train encoder -> freeze -> whiten (ZCA, 30k) -> fit the split on 30k matched
pairs (twin latents sharing block 2, resampling block 1, re-encoded and re-whitened) -> evaluate
on a disjoint probe set. Ground-truth latents are used only to generate data and to evaluate.
"""

from __future__ import annotations

import time

import torch

from . import audits
from .encoder import EncoderConfig, encode, train_encoder
from .engine import centering_only, fit_rung, fit_whitener, select_block_count
from .worlds import BlockWorld, CouplingMap

ABLATIONS = ("none", "no_pred", "no_inv", "no_var")
CONTROLS = ("none", "shuffled")


def run_stage_a(cfg: dict, seed: int, ablation: str = "none", control: str = "none",
                verbose: bool = False) -> dict:
    assert ablation in ABLATIONS and control in CONTROLS
    t0 = time.time()
    w, e, s = cfg["world"], cfg["encoder"], cfg["split"]
    d1, d2 = w["block_dims"]
    d = d1 + d2
    world = BlockWorld([d1, d2], [w["rho"]] * 2, seed=seed)
    observe = CouplingMap(d, w["coupling_layers"], w["coupling_strength"], w["obs_dim"], seed=seed)

    ecfg = EncoderConfig(in_dim=observe.obs_dim, latent_dim=d, hidden=e["hidden"], steps=e["steps"],
                         batch_size=e["batch_size"], lr=e["lr"], reg=e["reg"],
                         var_weight=e["var_weight"], cov_weight=e.get("cov_weight", 0.0),
                         sigreg_weight=e.get("sigreg_weight", 1e-6),
                         stop_grad=e.get("stop_grad", True))
    if ablation == "no_pred":
        ecfg.pred_weight = 0.0
    if ablation == "no_var":
        ecfg.var_weight, ecfg.cov_weight, ecfg.reg = 0.0, 0.0, "none"
    enc, train_log = train_encoder(world, observe, ecfg, seed + 77_777, verbose)

    # whitening (ZCA) on stationary samples; ablation no_var drops it (centering only)
    h_w = encode(enc, observe, world.sample(s["num_whiten"]))
    wh = centering_only(h_w) if ablation == "no_var" else fit_whitener(h_w, s["zca_eps"])

    # matched pairs: twin latents share block 2 (invariant), block 1 resampled (variant)
    zu, zv = world.correspondence_pairs(s["num_pairs"], k=1)
    if control == "shuffled":
        zv = zv[torch.randperm(len(zv), generator=world._g)]
    ru, rv = wh(encode(enc, observe, zu)), wh(encode(enc, observe, zv))
    fit = fit_rung(ru, rv, torch.eye(d), k=1, d_k=d1)
    # gap-rule block count (reported, not used for the split): threshold = frac * lambda_1
    lam = fit.eigvals
    selected = select_block_count(lam.double(), s["gamma_min_frac"] * float(lam[0]))

    if ablation == "no_inv":      # drop the invariance/correspondence step: no rotation at all
        v_basis, q_basis = torch.eye(d)[:, :d1], torch.eye(d)[:, d1:]
    else:
        v_basis, q_basis = fit.V, fit.Q

    # disjoint probe set (fresh latents)
    n_tr, n_te = s["probe_train"], s["probe_test"]
    z_all = world.sample(n_tr + n_te)
    r_all = wh(encode(enc, observe, z_all))
    ztr, zte = z_all[:n_tr], z_all[n_tr:]
    rtr, rte = r_all[:n_tr], r_all[n_tr:]
    sv, si = world.block_slice(1), world.block_slice(2)  # variant block 1, invariant block 2

    inv_tr, inv_te = rtr @ q_basis, rte @ q_basis
    var_tr, var_te = rtr @ v_basis, rte @ v_basis

    # global recovery: linear fit of the full representation from the true latents
    w_glob = audits.ridge_fit(ztr, rtr)
    global_r2 = audits.r2(w_glob, zte, rte)
    inv_r2 = audits.linear_r2(inv_tr, ztr[:, si], inv_te, zte[:, si])
    var_r2 = audits.linear_r2(var_tr, ztr[:, sv], var_te, zte[:, sv])

    # canonical angle to the probe-recovered true subspace: image of true block 2 in rep space
    a_hat = w_glob[:-1].T                       # (D, d): r ≈ A z + b
    true_inv = a_hat[:, si]
    true_var = a_hat[:, sv]
    angle_inv = audits.max_angle_deg(q_basis, true_inv)
    angle_var = audits.max_angle_deg(v_basis, true_var)

    # cross-block leakage: R^2(true_j -> est_k), permutation null + Holm (monograph §10)
    leak = audits.leakage_matrix(
        {"inv": (inv_tr, inv_te), "var": (var_tr, var_te)},
        {"inv": (ztr[:, si], zte[:, si]), "var": (ztr[:, sv], zte[:, sv])},
        alpha=cfg["significance"]["alpha"], n_perm=cfg["significance"]["n_perm"], seed=seed)
    ent = leak["entries"]
    leak_r2 = max(ent["var->inv"]["r2"], ent["inv->var"]["r2"])
    # paper-style leakage norms from the fitted linear map h ≈ A z (block-wise)
    a_blocks = _leakage_norms(rtr, ztr, q_basis, v_basis, si, sv)

    return {
        "seed": seed, "ablation": ablation, "control": control,
        "global_r2": global_r2, "invariant_r2": inv_r2, "variant_r2": var_r2,
        "angle_inv_deg": angle_inv, "angle_var_deg": angle_var,
        "gap_ratio": fit.gap_ratio, "selected_d": selected,
        "eigvals": [float(x) for x in lam],
        "leak_r2_max": leak_r2, "leak_any_significant": leak["any_significant"],
        "leak_entries": {k: {kk: vv for kk, vv in v.items()} for k, v in ent.items()},
        "leak_norms": a_blocks,
        "encoder_final": train_log[-1], "seconds": round(time.time() - t0, 1),
    }


def _leakage_norms(rtr, ztr, q, v, si, sv) -> dict:
    """||A_{inv<-var}||_F and ||A_{var<-inv}||_F of the linear map from true latents to est. blocks."""
    est = torch.cat([rtr @ q, rtr @ v], dim=1)          # [inv | var]
    w = audits.ridge_fit(ztr, est)[:-1].T               # (d, d)
    di = q.shape[1]
    # columns of A index true latents [var(sv) | inv(si)]; rows index est [inv | var]
    a_inv_from_var = w[:di, sv]
    a_var_from_inv = w[di:, si]
    return {"inv_from_var_fro": float(a_inv_from_var.norm()),
            "var_from_inv_fro": float(a_var_from_inv.norm()),
            "block_purity": float(1 - (a_inv_from_var.square().sum() + a_var_from_inv.square().sum())
                                  / w.square().sum())}
