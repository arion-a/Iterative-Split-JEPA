"""Stage B1 (mechanism): with CORRECT (generator-made) matched pairs at each level, can the
invariant block of one split be split again?  All results are labelled "ground-truth pairs".

World: texture (fast), identity, category (slow), all Gaussian. Observations come from the paper's
coupling map with no extra observed numbers. Encoder: the mirror-style encoder trained with the
paper's objective, then frozen. Rung-k pairs: twins share the slower blocks and resample block k.
Ground truth is used only to generate data and to evaluate.
"""

from __future__ import annotations

import math
import time

import torch

from . import audits
from .encoder import EncoderConfig, encode, train_encoder
from .engine import RungFit, centering_only, fit_ladder, fit_whitener
from .worlds import BlockWorld, CouplingMap

ABLATIONS = ("none", "no_pred", "no_inv", "no_var")
CONTROLS = ("none", "shuffled_rung2", "rank1_rung2")


def run_stage_b1(cfg: dict, seed: int, ablation: str = "none", control: str = "none",
                 verbose: bool = False) -> dict:
    assert ablation in ABLATIONS and control in CONTROLS
    t0 = time.time()
    w, e, s, sig = cfg["world"], cfg["encoder"], cfg["split"], cfg["significance"]
    world = BlockWorld(list(w["block_dims"]), list(w["rhos"]), seed=seed)
    d = world.d
    observe = CouplingMap(d, w["coupling_layers"], w["coupling_strength"], w.get("obs_dim"), seed=seed)

    ecfg = EncoderConfig(in_dim=observe.obs_dim, latent_dim=d, hidden=e["hidden"], steps=e["steps"],
                         batch_size=e["batch_size"], lr=e["lr"], reg=e["reg"], var_weight=e["var_weight"], cov_weight=e.get("cov_weight", 0.0), corr_inv_weight=e.get("corr_inv_weight", 0.0), stop_grad=e.get("stop_grad", True),
                         sigreg_weight=e["sigreg_weight"], arch=e["arch"], objective=e["objective"],
                         coupling_layers=w["coupling_layers"])
    if ablation == "no_pred":
        ecfg.pred_weight = 0.0
    if ablation == "no_var":
        ecfg.sigreg_weight = 0.0
    enc, train_log = train_encoder(world, observe, ecfg, seed + 77_777, verbose)

    wh = centering_only(encode(enc, observe, world.sample(s["num_whiten"]))) if ablation == "no_var" \
        else fit_whitener(encode(enc, observe, world.sample(s["num_whiten"])), s["zca_eps"])

    max_sq_diff = {}
    budgets = s.get("num_pairs_per_rung") or [s["num_pairs"]] * len(s["d_ks"])
    nest = cfg.get("nesting_enforcement", "hard")

    def pairs_fn(k):
        if k > world.n_blocks - 1:
            return None
        u, v = world.correspondence_pairs(budgets[k - 1], k, rank=1 if (control == "rank1_rung2" and k == 2) else None)
        if control == "shuffled_rung2" and k == 2:
            v = v[torch.randperm(len(v), generator=world._g)]
        ru, rv = wh(encode(enc, observe, u)), wh(encode(enc, observe, v))
        max_sq_diff[k] = float((ru - rv).square().sum(1).max())
        return ru, rv

    gate = cfg["criteria"]["gap_ratio_min"] if cfg.get("rung_gate") else None          # Gap 2: a rung that fails the frozen gap criterion is not applied
    rungs = fit_ladder(pairs_fn, d, d_ks=list(s["d_ks"]), nesting_enforcement=nest, gate_gap_ratio=gate)
    if ablation == "no_inv":      # no spectral head: read blocks off the encoder's coordinates
        eye, off, ident, h_prev = torch.eye(d), 0, [], torch.eye(d)
        for r in rungs:
            dk = r.d_k
            ident.append(RungFit(k=r.k, d_k=dk, eigvals=r.eigvals, gap_ratio=r.gap_ratio, selected_d=None,
                                 V=eye[:, off:off + dk], Q=eye[:, off + dk:], H_prev=h_prev, n_pairs=r.n_pairs))
            h_prev, off = eye[:, off + dk:], off + dk
        rungs = ident

    # ---- evaluation on fresh latents (ground truth used only here)
    n_tr, n_te = s["probe_train"], s["probe_test"]
    z_all = world.sample(n_tr + n_te)
    r_all = wh(encode(enc, observe, z_all))
    ztr, zte, rtr, rte = z_all[:n_tr], z_all[n_tr:], r_all[:n_tr], r_all[n_tr:]
    w_glob = audits.ridge_fit(ztr, rtr)
    a_hat = w_glob[:-1].T                                  # r ≈ A z + b
    image = {k: a_hat[:, world.block_slice(k)] for k in range(1, world.n_blocks + 1)}

    def cols(ks):
        return torch.cat([torch.arange(world.block_slice(k).start, world.block_slice(k).stop) for k in ks])

    out = []
    for r in rungs:
        k = r.k
        slower = list(range(k + 1, world.n_blocks + 1))
        qm = r.Q if r.applied else r.H_prev                  # content after this rung (unchanged when the rung was not applied)
        v_tr, v_te, q_tr, q_te = rtr @ r.V, rte @ r.V, rtr @ qm, rte @ qm
        z_own, z_slow = (lambda z: z[:, world.block_slice(k)]), (lambda z: z[:, cols(slower)])
        est_v = audits.ridge_fit(ztr, v_tr)[:-1].T         # variant coords from true latents (d_k, d)
        est_q = audits.ridge_fit(ztr, q_tr)[:-1].T         # invariant-content coords (m_k, d)
        own_c, slow_c = cols([k]), cols(slower)
        a12 = est_v.index_select(1, torch.tensor([c for c in range(d) if c not in set(own_c.tolist())]))
        a21 = est_q.index_select(1, own_c)
        total = est_v.square().sum() + est_q.square().sum()
        good = est_v.index_select(1, own_c).square().sum() + est_q.index_select(1, slow_c).square().sum()
        leak = audits.leakage_matrix(
            {"own": (v_tr, v_te), "rest": (q_tr, q_te)},
            {"own": (z_own(ztr), z_own(zte)), "rest": (z_slow(ztr), z_slow(zte))},
            alpha=sig["alpha"], n_perm=sig["n_perm"], seed=seed + k)
        lam = float(r.eigvals[r.d_k - 1])
        out.append({
            "k": k, "applied": bool(r.applied), "angle_deg": audits.max_angle_deg(r.V, image[k]),
            "nesting_deg": None if k == 1 else float(audits.principal_angles_deg(r.V, torch.cat([image[j] for j in range(k, world.n_blocks + 1)], dim=1)).max()),
            "variant_r2": audits.linear_r2(v_tr, ztr[:, world.block_slice(k)], v_te, zte[:, world.block_slice(k)]),
            "invariant_content_r2": audits.linear_r2(q_tr, z_slow(ztr), q_te, z_slow(zte)),
            "gap_ratio": r.gap_ratio, "lambda_dk": lam, "eigvals": [float(x) for x in r.eigvals],
            "rank_deficient": audits.rank_deficient(torch.diag(r.eigvals[: r.d_k]), budgets[k - 1],
                                                    max_sq_diff.get(k, 1.0) ** 0.5, sig["rank_test_delta"]),
            "n_pairs": budgets[k - 1], "rank_monitor": audits.rank_monitor(r) if r.max_sq_diff is not None else None,
            "a12_fro": float(a12.norm()), "a21_fro": float(a21.norm()), "block_purity": float(good / total),
            "leak_any_significant": leak["any_significant"],
            "leak_r2": {key: v["r2"] for key, v in leak["entries"].items()},
        })
    last = rungs[-1]
    core = last.Q if last.applied else last.H_prev
    core_r2 = audits.linear_r2(rtr @ core, ztr[:, world.block_slice(world.n_blocks)], rte @ core, zte[:, world.block_slice(world.n_blocks)])
    span = torch.cat([image[j] for j in range(2, world.n_blocks + 1)], dim=1)
    nesting = float(audits.principal_angles_deg(rungs[1].V, span).max())
    u_, _, _ = torch.linalg.svd(image[1], full_matrices=True)
    h_perp = u_[:, world.block_slice(1).stop - world.block_slice(1).start:]
    extra = {"nesting_perp_deg": float(audits.principal_angles_deg(rungs[1].V, h_perp).max()),
             "inherited_span_deg": float(audits.principal_angles_deg(rungs[0].Q if rungs[0].applied else rungs[0].H_prev, span).max()),
             "inherited_perp_deg": float(audits.principal_angles_deg(rungs[0].Q if rungs[0].applied else rungs[0].H_prev, h_perp).max()),
             "pair_budgets": list(budgets), "nesting_enforcement": nest}
    blocks = [world.block_slice(k) for k in range(1, world.n_blocks + 1)]
    presence = {"linear": [audits.linear_r2(rtr, ztr[:, b], rte, zte[:, b]) for b in blocks],
                "mlp": [audits.mlp_r2(rtr, ztr[:, b], rte, zte[:, b], seed=seed) for b in blocks]}
    payoff = None
    if cfg.get("payoff"):                                  # E38: one eigendecomposition of the adjacent-frame difference moment, blocks read off in eigenvalue order
        pu, pv = world.transition_pairs(budgets[0])
        delta = (wh(encode(enc, observe, pu)) - wh(encode(enc, observe, pv))).double()
        _, vecs = torch.linalg.eigh(delta.T @ delta / len(delta))
        vecs = vecs.flip(1).float()
        db = [world.block_slice(k).stop - world.block_slice(k).start for k in (1, 2)]
        single = [audits.max_angle_deg(vecs[:, :db[0]], image[1]), audits.max_angle_deg(vecs[:, db[0]:db[0] + db[1]], image[2])]
        payoff = {"single_shot_angles_deg": single, "ladder_angles_deg": [out[0]["angle_deg"], out[1]["angle_deg"]]}
    predictive = None
    if cfg.get("predictive"):                              # E39: monograph 8.1(c), rho_k = error of predicting the kept content's future from the kept content / from the content before the rung
        predictive = []
        for r in rungs:
            h = max(1, math.ceil(-1 / math.log(world.rhos[r.k - 1])))
            zt, zf = world.lag_pairs(n_tr + n_te, h)
            rt, rf = wh(encode(enc, observe, zt)), wh(encode(enc, observe, zf))
            after = r.Q if r.applied else r.H_prev
            tgt = rf @ after
            err = []
            for basis in (r.H_prev, after):
                x = rt @ basis
                w = audits.ridge_fit(x[:n_tr], tgt[:n_tr])
                pred = torch.cat([x[n_tr:], torch.ones(len(x) - n_tr, 1)], 1).to(w.dtype) @ w
                err.append(float((pred - tgt[n_tr:].to(w.dtype)).square().mean()))
            predictive.append({"k": r.k, "h": h, "rho": err[1] / err[0]})
    return {"seed": seed, "ablation": ablation, "control": control, "label": "ground-truth pairs", "presence": presence, "payoff": payoff, "predictive": predictive,
            "rungs": out, "nesting_angle_deg": nesting, **extra, "core_invariant_r2": core_r2,
            "global_r2": audits.r2(w_glob, zte, rte), "encoder_final": train_log[-1],
            "seconds": round(time.time() - t0, 1)}


CRITERIA_KEYS = ["rung1_angle", "rung2_angle", "rung1_variant_r2", "rung2_variant_r2", "core_invariant_r2",
                 "nesting", "rung1_gap", "rung2_gap", "leakage", "rank_test"]


def criteria_keys(n_rungs: int) -> list[str]:
    """Names of the per-seed checks for a ladder of n rungs (2 rungs: CRITERIA_KEYS; deeper rungs add their own angle, variant R2, gap and nesting)."""
    ks = [f"rung{i}_angle" for i in range(1, n_rungs + 1)] + [f"rung{i}_variant_r2" for i in range(1, n_rungs + 1)] + ["core_invariant_r2", "nesting"]
    return ks + [f"nesting{i}" for i in range(3, n_rungs + 1)] + [f"rung{i}_gap" for i in range(1, n_rungs + 1)] + ["leakage", "rank_test"]


def seed_checks(r: dict, c: dict) -> dict:
    """The per-seed acceptance checks, for any number of rungs (the plan's Stage C: the same checks at every rung)."""
    rg = r["rungs"]
    out = {}
    for i, g in enumerate(rg, 1):
        out[f"rung{i}_angle"] = g["angle_deg"] < c["rung_angle_max_deg"]
        out[f"rung{i}_variant_r2"] = g["variant_r2"] > c["variant_r2_min"]
        out[f"rung{i}_gap"] = g["gap_ratio"] > c["gap_ratio_min"]
        if i >= 3:
            out[f"nesting{i}"] = g["nesting_deg"] < c["nesting_angle_max_deg"]
    out["core_invariant_r2"] = r["core_invariant_r2"] > c["core_invariant_r2_min"]
    out["nesting"] = r["nesting_angle_deg"] < c["nesting_angle_max_deg"]
    out["leakage"] = not any(g["leak_any_significant"] for g in rg)
    out["rank_test"] = not any(g["rank_deficient"] for g in rg)
    return out


def evaluate(runs: dict, cfg: dict) -> dict:
    """Verdict rule (locked): PASS if every criterion holds on every seed; PASS_WITH_LOCATED_RISK if the
    only criterion failing on any seed is rung1_variant_r2 (texture); otherwise FAIL."""
    c, ctl = cfg["criteria"], cfg["controls"]["must_fail"]
    per = [dict(seed=r["seed"], **seed_checks(r, c)) for r in runs["main"]]
    failing = {k for k in CRITERIA_KEYS if not all(p[k] for p in per)}
    verdict = "PASS" if not failing else ("PASS_WITH_LOCATED_RISK" if failing == {"rung1_variant_r2"} else "FAIL")
    mean = lambda arm, f: sum(f(r) for r in runs[arm]) / len(runs[arm])
    controls = {
        "shuffled_rung2": mean("shuffled_rung2", lambda r: r["rungs"][1]["angle_deg"]) > ctl["shuffled_rung2"]["rung2_angle_min_deg"]
                          and mean("shuffled_rung2", lambda r: r["rungs"][1]["gap_ratio"]) < ctl["shuffled_rung2"]["rung2_gap_ratio_max"],
        "rank1_rung2": mean("rank1_rung2", lambda r: r["rungs"][1]["angle_deg"]) > ctl["rank1_rung2"]["rung2_angle_min_deg"]
                       and mean("rank1_rung2", lambda r: r["rungs"][0]["angle_deg"]) < ctl["rank1_rung2"]["rung1_angle_max_deg"]}
    return {"per_seed": per, "failing_criteria": sorted(failing), "verdict": verdict, "controls": controls}
