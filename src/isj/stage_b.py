"""Stage B: can the invariant output of rung 1 be split again?  (plan §4.2)

World: texture (fast), identity, category (slow) blocks plus one planted cross-cutting factor, all
Gaussian. Observations come from the paper's coupling map (no extra observed numbers); the encoder
is the mirror-style encoder trained with the paper's objective, then frozen. Matched pairs for rung k
are made the way the paper makes them: twin samples share the slower blocks and resample block k.
Ground truth is used only to generate data and to evaluate.
"""

from __future__ import annotations

import time

import torch

from . import audits
from .encoder import EncoderConfig, encode, train_encoder
from .engine import centering_only, fit_ladder, fit_whitener
from .worlds import BlockWorld, CouplingMap

ABLATIONS = ("none", "no_pred", "no_inv", "no_var")
CONTROLS = ("none", "shuffled_rung2", "rank1_rung2")


def run_stage_b(cfg: dict, seed: int, ablation: str = "none", control: str = "none",
                with_cross: bool = True, verbose: bool = False) -> dict:
    assert ablation in ABLATIONS and control in CONTROLS
    t0 = time.time()
    w, e, s = cfg["world"], cfg["encoder"], cfg["split"]
    dims = list(w["block_dims"]) if with_cross else list(w["block_dims"])[:-1]
    rhos = list(w["rhos"]) if with_cross else list(w["rhos"])[:-1]
    world = BlockWorld(dims, rhos, seed=seed, cross_block=w["cross_block"] if with_cross else None,
                       cross_p=w["cross_p"])
    d = world.d
    observe = CouplingMap(d, w["coupling_layers"], w["coupling_strength"], w.get("obs_dim"), seed=seed)

    ecfg = EncoderConfig(in_dim=observe.obs_dim, latent_dim=d, hidden=e["hidden"], steps=e["steps"],
                         batch_size=e["batch_size"], lr=e["lr"], reg=e["reg"], var_weight=e["var_weight"],
                         sigreg_weight=e["sigreg_weight"], arch=e["arch"], objective=e["objective"],
                         coupling_layers=w["coupling_layers"])
    if ablation == "no_pred":
        ecfg.pred_weight = 0.0
    if ablation == "no_var":
        ecfg.sigreg_weight = 0.0
    enc, train_log = train_encoder(world, observe, ecfg, seed + 77_777, verbose)

    h_w = encode(enc, observe, world.sample(s["num_whiten"]))
    wh = centering_only(h_w) if ablation == "no_var" else fit_whitener(h_w, s["zca_eps"])

    def pairs_fn(k):
        if k > world.n_nominal - 1:
            return None
        u, v = world.correspondence_pairs(s["num_pairs"], k, rank=1 if (control == "rank1_rung2" and k == 2) else None)
        if control == "shuffled_rung2" and k == 2:
            v = v[torch.randperm(len(v), generator=world._g)]
        return wh(encode(enc, observe, u)), wh(encode(enc, observe, v))

    rungs = fit_ladder(pairs_fn, d, d_ks=list(s["d_ks"]))
    if ablation == "no_inv":      # no spectral head: read blocks off the coordinates as they come
        from .engine import RungFit
        eye, off, rungs_id = torch.eye(d), 0, []
        h_prev = torch.eye(d)
        for k, dk in enumerate(s["d_ks"], 1):
            v_ = eye[:, off:off + dk]
            q_ = eye[:, off + dk:]
            rungs_id.append(RungFit(k=k, d_k=dk, eigvals=rungs[k - 1].eigvals, gap_ratio=rungs[k - 1].gap_ratio,
                                    selected_d=None, V=v_, Q=q_, H_prev=h_prev, n_pairs=rungs[k - 1].n_pairs))
            h_prev, off = q_, off + dk
        rungs = rungs_id

    # ---- evaluation on fresh latents
    n_tr, n_te = s["probe_train"], s["probe_test"]
    z_all = world.sample(n_tr + n_te)
    r_all = wh(encode(enc, observe, z_all))
    ztr, zte, rtr, rte = z_all[:n_tr], z_all[n_tr:], r_all[:n_tr], r_all[n_tr:]
    w_glob = audits.ridge_fit(ztr, rtr)
    a_hat = w_glob[:-1].T                                   # (d, d): r ≈ A z + b
    image = {k: a_hat[:, world.block_slice(k)] for k in range(1, world.n_blocks + 1)}
    out_rungs = []
    for r in rungs:
        k = r.k
        others = [j for j in range(1, world.n_blocks + 1) if j != k]
        v_tr, v_te = rtr @ r.V, rte @ r.V
        est = audits.ridge_fit(ztr, v_tr)[:-1].T            # (d_k, d): V-coordinates from true latents
        own = est[:, world.block_slice(k)].square().sum()
        leak = torch.cat([est[:, world.block_slice(j)] for j in others], dim=1).square().sum()
        out_rungs.append({
            "k": k, "angle_deg": audits.max_angle_deg(r.V, image[k]),
            "r2": audits.linear_r2(v_tr, ztr[:, world.block_slice(k)], v_te, zte[:, world.block_slice(k)]),
            "block_purity": float(own / (own + leak)), "leak_fro": float(leak.sqrt()),
            "gap_ratio": r.gap_ratio, "eigvals": [float(x) for x in r.eigvals],
        })
    last = rungs[-1]
    nest_span = torch.cat([image[j] for j in range(2, world.n_blocks + 1)], dim=1)
    nesting = float(audits.principal_angles_deg(rungs[1].V, nest_span).max()) if len(rungs) > 1 else 0.0
    core_r2 = audits.linear_r2(rtr @ last.Q, ztr[:, world.block_slice(3)], rte @ last.Q, zte[:, world.block_slice(3)])
    dm = audits.deviation_map(rungs)
    dev = {"T": dm["T"], "residual_eigs": [p["residual_eig"] for p in dm["per_rung"]],
           "recurrence_angles_deg": dm["between_rung_angles_deg"]}
    if with_cross:
        c_img = image[world.cross_block]
        dev["angle_to_true_factor_deg"] = [audits.max_angle_deg(p["direction"].unsqueeze(1), c_img) for p in dm["per_rung"]]

    return {"seed": seed, "ablation": ablation, "control": control, "with_cross": with_cross,
            "rungs": out_rungs, "nesting_angle_deg": nesting, "core_block3_r2": core_r2,
            "global_r2": audits.r2(w_glob, zte, rte), "deviation": dev,
            "encoder_final": train_log[-1], "seconds": round(time.time() - t0, 1)}
