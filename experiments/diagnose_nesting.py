"""Nesting-angle diagnostics (decision D9 follow-up). Diagnose first; fixes are decided from these numbers.

  python experiments/diagnose_nesting.py ideal                 # ideal linear 3-block world, no encoder (fast)
  python experiments/diagnose_nesting.py b2world --seed 0       # the real B2 world with a trained encoder (one encoder per seed)

Quantities (all angles are maximum principal angles, degrees):
  inherited  theta(H1_hat, H1*)      rung 1's own subspace error, H1* = true span of blocks 2 and 3
  nesting    theta(V2_hat, H1*)      how far the rung-2 block lies outside the true rung-1 invariant space
  recovery   theta(V2_hat, true identity block)
  intrinsic  recovery when rung 2 is given the TRUE H1* instead of the estimate (clean-input control)
"""
import argparse
import json
import math
import os
import sys

import torch
import yaml

from isj import audits
from isj.engine import fit_rung
from isj.worlds import BlockWorld, LinearRepresentation

ang = audits.max_angle_deg
OUT = "results/diagnostics/nesting"


def slope(ns, ys):
    xs = [math.log(n) for n in ns]; ls = [math.log(max(y, 1e-9)) for y in ys]
    mx, my = sum(xs) / len(xs), sum(ls) / len(ls)
    return sum((x - mx) * (l - my) for x, l in zip(xs, ls)) / sum((x - mx) ** 2 for x in xs)


# ------------------------------------------------------------------ ideal linear world
def ideal():
    res = {"inheritance": [], "budget": [], "soft_vs_hard": {}, "regimes": {}}
    d = 12
    def setup(seed, noise):
        w = BlockWorld([4, 4, 4], [0.2, 0.7, 0.95], seed=seed)
        rep = LinearRepresentation(w, seed=seed, noise=noise)
        return w, rep, torch.cat([rep.true_block(2), rep.true_block(3)], 1)

    def rung1(w, rep, n):
        u, v = w.correspondence_pairs(n, 1)
        return fit_rung(rep(u), rep(v), torch.eye(d), k=1, d_k=4)

    def rung2(w, rep, h, n, mode="hard", lam=100.0):
        u, v = w.correspondence_pairs(n, 2)
        return fit_rung(rep(u), rep(v), h, k=2, d_k=4, nesting_enforcement=mode, soft_lambda=lam)

    # 1. inheritance + clean-input control, across encoder-noise levels
    for noise in (0.05, 0.1, 0.2):
        rows = []
        for seed in range(3):
            w, rep, hstar = setup(seed, noise); f1 = rung1(w, rep, 30_000); f2 = rung2(w, rep, f1.Q, 30_000)
            clean = rung2(w, rep, hstar, 30_000)
            rows.append({"inherited": ang(f1.Q, hstar), "nesting": ang(f2.V, hstar), "recovery": ang(f2.V, rep.true_block(2)),
                         "intrinsic": ang(clean.V, rep.true_block(2))})
        res["inheritance"].append({"noise": noise, **{k: sum(r[k] for r in rows) / 3 for k in rows[0]}})
    # 2. budget lever: inherited error and nesting against the rung-1 budget
    ns = [5_000, 20_000, 80_000, 320_000]
    for n in ns:
        rows = []
        for seed in range(3):
            w, rep, hstar = setup(seed, 0.1); f1 = rung1(w, rep, n); f2 = rung2(w, rep, f1.Q, 30_000)
            rows.append((ang(f1.Q, hstar), ang(f2.V, hstar)))
        res["budget"].append({"n1": n, "inherited": sum(r[0] for r in rows) / 3, "nesting": sum(r[1] for r in rows) / 3})
    res["budget_slope_inherited"] = slope(ns, [b["inherited"] for b in res["budget"]])
    # 3. soft vs hard, three regimes
    lams = [0.1, 0.3, 1, 3, 10, 30, 1000]
    def regime(make_h):
        out = {"hard": [], "soft": {str(l): [] for l in lams}, "none": []}
        for seed in range(3):
            w, rep, hstar = setup(seed, 0.1); h = make_h(w, rep, hstar)
            ident = rep.true_block(2)
            out["hard"].append((ang(rung2(w, rep, h, 30_000).V, hstar), ang(rung2(w, rep, h, 30_000).V, ident)))
            for l in lams:
                f = rung2(w, rep, h, 30_000, "soft", l); out["soft"][str(l)].append((ang(f.V, hstar), ang(f.V, ident)))
            f = rung2(w, rep, h, 30_000, "none"); out["none"].append((ang(f.V, hstar), ang(f.V, ident)))
        m = lambda xs: [sum(x[i] for x in xs) / len(xs) for i in (0, 1)]
        return {"hard (nesting, recovery)": m(out["hard"]), "none": m(out["none"]),
                **{f"soft lambda={l}": m(out["soft"][str(l)]) for l in lams}}
    def isotropic(w, rep, hstar): return rung1(w, rep, 30_000).Q                       # natural finite-sample imperfection
    def contamination(w, rep, hstar):                                                   # a foreign (texture) direction inside H1
        return audits.orth(torch.cat([hstar, rep.true_block(1)[:, :1]], 1)).float()
    def recall_loss(w, rep, hstar):                                                     # one true identity direction missing, a texture direction in its place
        ident = rep.true_block(2)
        return audits.orth(torch.cat([ident[:, 1:], rep.true_block(3), rep.true_block(1)[:, :1]], 1)).float()
    res["regimes"] = {"isotropic imperfection": regime(isotropic), "foreign direction inside H1": regime(contamination), "recall loss (true identity direction outside H1)": regime(recall_loss)}
    json.dump(res, open(f"{OUT}/ideal_world.json", "x" if not os.path.exists(f"{OUT}/ideal_world.json") else "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items()}, indent=1))


# ------------------------------------------------------------------ the real B2 world
def b2world(seed, sigma=0.1):
    from isj.encoder import EncoderConfig, encode, train_encoder
    from isj.engine import fit_whitener
    from isj.worlds import CouplingMap, HierarchicalMixtureWorld
    cfg = yaml.safe_load(open("configs/stage_b2_spec.yaml")); w_, e = cfg["world"], cfg["encoder"]
    world = HierarchicalMixtureWorld(list(w_["block_dims"]), list(w_["rhos"]), seed=seed, n_categories=w_["n_categories"], n_identities=w_["n_identities"],
                                     n_textures=w_["n_textures"], sigma_cat=sigma, sigma_id=w_["sigma_id"], sigma_tex=w_["sigma_tex"])
    d = world.d
    obs = CouplingMap(d, w_["coupling_layers"], w_["coupling_strength"], None, seed=seed)
    ecfg = EncoderConfig(in_dim=d, latent_dim=d, hidden=e["hidden"], steps=e["steps"], batch_size=e["batch_size"], lr=e["lr"], reg=e["reg"],
                         var_weight=e["var_weight"], sigreg_weight=e["sigreg_weight"], arch=e["arch"], objective=e["objective"], coupling_layers=w_["coupling_layers"])
    enc, _ = train_encoder(world, obs, ecfg, seed + 77_777)
    wh = fit_whitener(encode(enc, obs, world.sample(30_000)), 1e-5)
    R = lambda z: wh(encode(enc, obs, z))
    z_all = world.sample(20_000); r_all = R(z_all)
    a_hat = audits.ridge_fit(z_all[:15_000], r_all[:15_000])[:-1].T
    img = {k: a_hat[:, world.block_slice(k)] for k in (1, 2, 3)}
    h_span = audits.orth(torch.cat([img[2], img[3]], 1)).float()                        # H1* as the span of the probe images of blocks 2, 3
    h_perp = torch.linalg.svd(audits.orth(img[1]).float(), full_matrices=True)[0][:, 4:]  # H1* as the orthogonal complement of block 1's image
    res = {"seed": seed, "sigma_cat": sigma, "global_r2": audits.r2(audits.ridge_fit(z_all[:15_000], r_all[:15_000]), z_all[15_000:], r_all[15_000:]),
           "truth_definition_gap_deg": ang(h_span, h_perp), "budget": [], "soft": {}}
    def fit2(h, n2=30_000, mode="hard", lam=100.0):
        u, v = world.correspondence_pairs(n2, 2); return fit_rung(R(u), R(v), h, k=2, d_k=4, nesting_enforcement=mode, soft_lambda=lam)
    clean = fit2(h_span)
    res["intrinsic_recovery_deg"] = ang(clean.V, img[2])
    for n1 in (7_500, 30_000, 120_000, 480_000):
        u, v = world.correspondence_pairs(n1, 1)
        f1 = fit_rung(R(u), R(v), torch.eye(d), k=1, d_k=4); f2 = fit2(f1.Q)
        res["budget"].append({"n1": n1, "rung1_angle_vs_image": ang(f1.V, img[1]), "inherited_span": ang(f1.Q, h_span), "inherited_perp": ang(f1.Q, h_perp),
                              "nesting_span": ang(f2.V, h_span), "nesting_perp": ang(f2.V, h_perp), "recovery": ang(f2.V, img[2])})
        if n1 == 30_000:
            for lam in (0.3, 1, 3, 10, 100):
                fs = fit2(f1.Q, mode="soft", lam=lam); res["soft"][str(lam)] = {"nesting_span": ang(fs.V, h_span), "recovery": ang(fs.V, img[2])}
            fn = fit2(f1.Q, mode="none"); res["none"] = {"nesting_span": ang(fn.V, h_span), "recovery": ang(fn.V, img[2])}
    p = f"{OUT}/b2world_seed{seed}.json"
    with open(p, "w") as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("part", choices=["ideal", "b2world"]); ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    ideal() if a.part == "ideal" else b2world(a.seed)
