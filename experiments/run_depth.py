"""G2: a world with depth (timescale ratios ~10). Arms: ladder (lags 1,4,16), single-lag (lag 1 on every rung), shuffled. Frozen criteria: configs/gaps.yaml."""
import hashlib, json, os, sys

import numpy as np
import torch
import yaml

from isj import explog, hier, temporal_ladder as tl
from isj.encoder import EncoderConfig, train_encoder
from isj.engine import fit_whitener

cfg = yaml.safe_load(open("configs/gaps.yaml")); c = cfg["criteria"]["depth"]; w = cfg["depth_world"]; e = w["encoder"]
if hashlib.sha256(json.dumps(cfg["criteria"], sort_keys=True).encode()).hexdigest() != open("configs/gaps.criteria.sha256").read().strip():
    sys.exit("criteria differ from the frozen hash")
torch.set_num_threads(4)
nb = len(w["a"]); blk = lambda b: slice(w["block"] * b, w["block"] * (b + 1)); D = nb * w["block"]


def r2(x, y, ridge=1e-6):
    xa = np.concatenate([x, np.ones((len(x), 1))], 1)
    return np.linalg.solve(xa.T @ xa + ridge * np.eye(xa.shape[1]), xa.T @ y)


def r2s(wgt, x, y):
    p = np.concatenate([x, np.ones((len(x), 1))], 1) @ wgt
    return float(1 - ((y - p) ** 2).sum() / ((y - y.mean(0)) ** 2).sum())


def per_rung(out, zf, zt, lf, lt):
    removed, rows = set(), []
    for x in [x for x in out["rungs"] if x["d_k"] > 0]:
        free = [b for b in range(nb) if b not in removed]
        side, sc = {}, {}
        for b in free:
            yf, yt = zf.reshape(-1, D)[:, blk(b)], zt.reshape(-1, D)[:, blk(b)]
            rv_ = r2s(r2(lf.reshape(-1, D) @ x["V"], yf), lt.reshape(-1, D) @ x["V"], yt)
            rq_ = r2s(r2(lf.reshape(-1, D) @ x["Q"], yf), lt.reshape(-1, D) @ x["Q"], yt)
            side[b], sc[b] = ("variant" if rv_ >= rq_ else "invariant"), max(rv_, rq_)
        var = [b for b in free if side[b] == "variant"]; inv = [b for b in free if side[b] == "invariant"]
        rows.append({"family": x["family"], "best_ratio": x["best_ratio"], "variant_blocks": [b + 1 for b in var], "invariant_blocks": [b + 1 for b in inv],
                     "variant_r2": float(np.mean([sc[b] for b in var])) if var else None, "invariant_r2": float(np.mean([sc[b] for b in inv])) if inv else None})
        removed |= set(var)
    return rows


os.makedirs("results/depth", exist_ok=True)
for s in cfg["seeds"]:
    world, obs = hier.make_world(s, tuple(w["a"]), w["block"])
    ecfg = EncoderConfig(in_dim=obs.obs_dim, latent_dim=world.d, steps=e["steps"], batch_size=e["batch_size"], lr=e["lr"], reg="hinge", var_weight=e["var_weight"],
                         cov_weight=e["cov_weight"], arch=e["arch"], coupling_layers=e["coupling_layers"])
    enc, _ = train_encoder(world, obs, ecfg, s + 77_777)
    wh = fit_whitener(enc(obs(world.sample(w["n_whiten"]))), e["zca_eps"])
    def lat(z):
        with torch.no_grad():
            return wh(enc(obs(torch.from_numpy(z.reshape(-1, z.shape[-1])).float()))).numpy().reshape(*z.shape[:-1], -1)
    zf = hier.trajectories(tuple(w["a"]), w["block"], w["n_fit"], w["t"], seed=1000 + s); zt = hier.trajectories(tuple(w["a"]), w["block"], w["n_test"], w["t"], seed=2000 + s)
    lf, lt = lat(zf), lat(zt)
    arms = {}
    for arm, lags, shuffle in (("ladder", c["lags"], False), ("single_lag", [c["lags"][0]] * len(c["lags"]), False), ("shuffled", c["lags"], True)):
        out = tl.run_ladder(lf[:, None], lags, c["gamma_min"], None, shuffle, s, c["s1_chance_fraction"], use_aug=False)
        cuts = [x for x in out["rungs"] if x["d_k"] > 0]
        arms[arm] = {"cuts": len(cuts), "stop": out["stop"], "families": [(x["family"], x["d_k"], round(x["best_ratio"], 2), x.get("stop", "split"), round(x["lambda_max_over_chance"], 3)) for x in out["rungs"]],
                     "per_rung": per_rung(out, zf, zt, lf, lt)}
    path = f"results/depth/{s}.json"
    with open(path, "x") as f:
        json.dump({"seed": s, "arms": arms}, f, indent=1)
    print(s, {a: (r["cuts"], r["stop"]) for a, r in arms.items()}, flush=True)
    explog.append("run", f"Depth world (G2) seed {s} finished", stage="V", step="G2", how="experiments/run_depth.py", artifact_paths=[path], outputs={a: r["cuts"] for a, r in arms.items()})
