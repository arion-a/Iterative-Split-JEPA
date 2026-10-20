"""Stage V E36: coupled vs uncoupled two-block world; (S) split quality and (D) closure ratio. Frozen criteria: configs/e36.yaml."""
from __future__ import annotations

import hashlib, json, os, sys

import numpy as np
import torch
import yaml

sys.path.insert(0, "experiments")
from run_hier import r2, r2_score
from isj import hier, temporal_ladder as tl
from isj.encoder import EncoderConfig, train_encoder
from isj.engine import fit_whitener
from isj.worlds import CouplingMap

cfg = yaml.safe_load(open("configs/e36.yaml")); c, w, e = cfg["criteria"], cfg["world"], cfg["encoder"]
if hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest() != open("configs/e36.criteria.sha256").read().strip():
    sys.exit("criteria differ from the frozen hash")
torch.set_num_threads(4)


def resid(x, y_next, x_fit, y_fit):
    a = np.concatenate([x_fit, np.ones((len(x_fit), 1))], 1)
    wgt = np.linalg.lstsq(a, y_fit, rcond=None)[0]
    p = np.concatenate([x, np.ones((len(x), 1))], 1) @ wgt
    return float(((y_next - p) ** 2).sum() / ((y_next - y_next.mean(0)) ** 2).sum())


os.makedirs("results/e36", exist_ok=True)
for s in cfg["seeds"]:
    for name, coup in (("coupled", w["coupling"]), ("control", 0.0)):
        world = hier.CoupledWorld(w["a_fast"], w["a_slow"], coup, seed=s)
        obs = CouplingMap(world.d, 4, 0.5, None, seed=s)
        ecfg = EncoderConfig(in_dim=obs.obs_dim, latent_dim=world.d, steps=e["steps"], batch_size=e["batch_size"], lr=e["lr"], reg="hinge",
                             var_weight=e["var_weight"], cov_weight=e["cov_weight"], arch=e["arch"], coupling_layers=e["coupling_layers"])
        enc, _ = train_encoder(world, obs, ecfg, s + 77_777)
        wh = fit_whitener(enc(obs(world.sample(w["n_whiten"]))), e["zca_eps"])

        def lat(z):
            with torch.no_grad():
                return wh(enc(obs(torch.from_numpy(z.reshape(-1, z.shape[-1])).float()))).numpy().reshape(*z.shape[:-1], -1)

        zf = hier.coupled_trajectories(world, w["n_fit"], w["t"], 1000 + s)
        zt = hier.coupled_trajectories(world, w["n_test"], w["t"], 2000 + s)
        lf, lt = lat(zf), lat(zt)
        out = tl.run_ladder(lf[:, None], c["split"]["lags"], c["split"]["gamma_min"], None, False, s, c["split"]["s1_chance_fraction"], use_aug=False)
        split = next((x for x in out["rungs"] if x["d_k"] > 0), None)
        rec = {"seed": s, "world": name, "coupling": coup, "stop": out["stop"],
               "families": [(x["family"], x["d_k"], round(x["best_ratio"], 2)) for x in out["rungs"]], "rung_found": split is not None}
        if split is not None:
            v, q = split["V"], split["Q"]
            d = lf.shape[-1]

            def side(sl_true, basis):
                fit_x, test_x = lf.reshape(-1, d) @ basis, lt.reshape(-1, d) @ basis
                return r2_score(r2(fit_x, zf.reshape(-1, 8)[:, sl_true]), test_x, zt.reshape(-1, 8)[:, sl_true])

            rec["variant_r2_fast"], rec["invariant_r2_slow"] = side(slice(0, 4), v), side(slice(4, 8), q)
            qf, qt = lf @ q, lt @ q
            xq, yq = qt[:, :-1].reshape(-1, qt.shape[-1]), qt[:, 1:].reshape(-1, qt.shape[-1])
            xqf, yqf = qf[:, :-1].reshape(-1, qf.shape[-1]), qf[:, 1:].reshape(-1, qf.shape[-1])
            xz, xzf = lt[:, :-1].reshape(-1, d), lf[:, :-1].reshape(-1, d)
            rec["resid_core_only"], rec["resid_full_latent"] = resid(xq, yq, xqf, yqf), resid(xz, yq, xzf, yqf)
            rec["closure_ratio"] = rec["resid_core_only"] / rec["resid_full_latent"]
            rec["S_pass"] = bool(rec["variant_r2_fast"] >= c["split"]["block_r2_min"] and rec["invariant_r2_slow"] >= c["split"]["block_r2_min"])
        with open(f"results/e36/{name}_{s}.json", "x") as f:
            json.dump(rec, f, indent=1)
        print(rec, flush=True)
