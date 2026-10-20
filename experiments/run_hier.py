"""Stage V P4: minimal hierarchical AR world. Arms: ladder (L) and shuffled-pair control (C), 3 seeds, mirror encoder (D4).
Frozen criteria in configs/hier.yaml; results never overwritten."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import numpy as np
import torch
import yaml

from isj import explog, hier, quotient_audit as qa, temporal_ladder as tl
from isj.encoder import EncoderConfig, train_encoder
from isj.engine import fit_whitener


def criteria_hash(cfg):
    return hashlib.sha256(json.dumps(cfg["criteria"], sort_keys=True).encode()).hexdigest()


def r2(x, y, ridge=1e-6):
    xa = np.concatenate([x, np.ones((len(x), 1))], 1)
    w = np.linalg.solve(xa.T @ xa + ridge * np.eye(xa.shape[1]), xa.T @ y)
    return w


def r2_score(w, x, y):
    p = np.concatenate([x, np.ones((len(x), 1))], 1) @ w
    return float(1 - ((y - p) ** 2).sum() / ((y - y.mean(0)) ** 2).sum())


def evaluate_rungs(out, zw_fit, zw_test, z_fit, z_test, blk, crit):
    """Per found rung: variant/invariant R^2 against the true blocks, (D)/(C) ratios to the oracle-block predictor, L."""
    k_h = crit["horizon_K"]
    d = zw_fit.shape[-1]
    removed, res = set(), []
    recs = [{"rung": x["k"], "family": x["family"], "d_k": x["d_k"], "V": x["V"], "Q": x["Q"]} for x in out["rungs"] if x["d_k"] > 0]
    for r in recs:
        free = [b for b in range(5) if b not in removed]
        fit_v, test_v = zw_fit.reshape(-1, d) @ r["V"], zw_test.reshape(-1, d) @ r["V"]
        fit_q, test_q = zw_fit.reshape(-1, d) @ r["Q"], zw_test.reshape(-1, d) @ r["Q"]
        side, sc = {}, {}
        for b in free:
            yb, yb_t = z_fit.reshape(-1, 20)[:, blk(b)], z_test.reshape(-1, 20)[:, blk(b)]
            rv, rq = r2_score(r2(fit_v, yb), test_v, yb_t), r2_score(r2(fit_q, yb), test_q, yb_t)
            side[b], sc[b] = ("variant" if rv >= rq else "invariant"), (rv if rv >= rq else rq)
        var_b = [b for b in free if side[b] == "variant"]; inv_b = [b for b in free if side[b] == "invariant"]
        row = {"rung": r["rung"], "family": r["family"], "d_k": r["d_k"], "variant_blocks": [b + 1 for b in var_b], "invariant_blocks": [b + 1 for b in inv_b],
               "variant_r2": float(np.mean([sc[b] for b in var_b])) if var_b else None,
               "invariant_r2": float(np.mean([sc[b] for b in inv_b])) if inv_b else None}
        if inv_b:
            qf, qt = (zw_fit @ r["Q"]), (zw_test @ r["Q"])
            of = np.concatenate([z_fit[..., blk(b)] for b in inv_b], -1); ot = np.concatenate([z_test[..., blk(b)] for b in inv_b], -1)
            res_l, res_o = {}, {}
            for name, (a_fit, a_test) in {"learned": (qf, qt), "oracle": (of, ot)}.items():
                a_fit, a_test = a_fit[:, None], a_test[:, None]                    # (R, 1, T, m)
                A, b0 = qa.fit_transition(a_fit)
                x, y = a_test[:, :, :-1].reshape(-1, a_test.shape[-1]), a_test[:, :, 1:].reshape(-1, a_test.shape[-1])
                resid = ((y - (x @ A.T + b0)) ** 2).sum() / ((y - y.mean(0)) ** 2).sum()
                (res_l if name == "learned" else res_o).update({"D": float(resid), "C": qa.rollout_nmse(a_test, A, b0, k_h), "L": qa.lipschitz(A)})
            row.update({"D_ratio": res_l["D"] / res_o["D"], "C_ratio": res_l["C"] / res_o["C"], "L": res_l["L"], "L_oracle": res_o["L"]})
        res.append(row)
        removed |= set(var_b)
    return res


def run(cfg, seeds, out_dir, log):
    crit, lad = cfg["criteria"], cfg["criteria"]["ladder"]
    w, e = cfg["world"], cfg["encoder"]
    blk = lambda b: slice(4 * b, 4 * b + 4)
    for s in seeds:
        world, observe = hier.make_world(s, tuple(w["a"]), w["block"])
        ecfg = EncoderConfig(in_dim=observe.obs_dim, latent_dim=world.d, steps=e["steps"], batch_size=e["batch_size"], lr=e["lr"], reg="hinge",
                             var_weight=e["var_weight"], cov_weight=e["cov_weight"], arch=e["arch"], coupling_layers=e["coupling_layers"])
        enc, _ = train_encoder(world, observe, ecfg, s + 77_777)
        wh = fit_whitener(enc(observe(world.sample(w["n_whiten"]))), e["zca_eps"])
        def lat(z):
            with torch.no_grad():
                return wh(enc(observe(torch.from_numpy(z.reshape(-1, z.shape[-1])).float()))).numpy().reshape(*z.shape[:-1], -1)
        z_fit = hier.trajectories(tuple(w["a"]), w["block"], w["n_fit"], w["t"], seed=1000 + s)
        z_test = hier.trajectories(tuple(w["a"]), w["block"], w["n_test"], w["t"], seed=2000 + s)
        zw_fit, zw_test = lat(z_fit), lat(z_test)
        for arm, shuffle in (("ladder", False), ("shuffled", True)):
            out = tl.run_ladder(zw_fit[:, None], lad["lags"], lad["gamma_min"], None, shuffle, s, lad["s1_chance_fraction"], use_aug=False)
            splits = [x for x in out["rungs"] if x["d_k"] > 0]
            rec = {"seed": s, "arm": arm, "RUNGS": len(splits), "stop": out["stop"],
                   "families": [{k: v for k, v in x.items() if k not in ("V", "Q", "eigvals")} | {"eigvals": [round(v, 4) for v in x["eigvals"]]} for x in out["rungs"]],
                   "oracle_cut_gaps_lag1": hier.oracle_cut_gaps(tuple(w["a"]), 1)}
            if arm == "ladder":
                rec["per_rung"] = evaluate_rungs(out, zw_fit, zw_test, z_fit, z_test, blk, crit["per_rung"])
            path = os.path.join(out_dir, arm, f"{s}.json")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "x") as f:
                json.dump(rec, f, indent=1)
            log("run", f"Hierarchical {arm} seed {s} finished", s, {"RUNGS": rec["RUNGS"], "stop": rec["stop"]}, [path])
            print(arm, s, "RUNGS", rec["RUNGS"], "stop", rec["stop"], [(x["family"], x["d_k"], round(x["best_ratio"], 2)) for x in out["rungs"]], flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/hier.yaml"); ap.add_argument("--out", default="results/hier")
    ap.add_argument("--seeds", type=int, nargs="*"); ap.add_argument("--no-log", action="store_true")
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    if criteria_hash(cfg) != open(a.config.replace(".yaml", ".criteria.sha256")).read().strip():
        sys.exit("criteria differ from the frozen hash")
    def log(kind, what, seed, outputs, arts):
        if not a.no_log:
            explog.append(kind, what, stage="V", step="P4", how="experiments/run_hier.py", outputs=outputs, artifact_paths=arts)
    torch.set_num_threads(2)
    run(cfg, a.seeds if a.seeds else cfg["seeds"], a.out, log)
