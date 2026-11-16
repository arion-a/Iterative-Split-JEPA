"""E61: iterated splitting to 8 and 10 rungs (9 and 11 layers of 4 numbers). Registered in docs/EVIDENCE.md.
    python experiments/deep_ladder.py -> results/deep_ladder.json"""
import json, sys, time, torch, numpy as np
from isj import audits
from isj.engine import fit_ladder, fit_whitener
from isj.worlds import BlockWorld, CouplingMap
out = []
for rungs_n, seeds in ((8, range(260, 265)), (10, range(270, 275))):
    L = rungs_n + 1; rhos = [float(1 - x) for x in np.logspace(np.log10(0.8), np.log10(0.04), L)]
    for seed in seeds:
        t0 = time.time(); world = BlockWorld([4] * L, rhos, seed=seed); d = world.d
        obs = CouplingMap(d, 4, 0.5, None, seed=seed)
        wh = fit_whitener(obs(world.sample(30000)), 1e-5); R = lambda z: wh(obs(z))
        pairs = lambda k: tuple(R(t) for t in world.correspondence_pairs(30000, k)) if k <= rungs_n else None
        rungs = fit_ladder(pairs, d, d_ks=[4] * rungs_n, nesting_enforcement="hard")
        z = world.sample(20000); r = R(z); a = audits.ridge_fit(z[:15000], r[:15000])[:-1].T
        rec = {"rungs": rungs_n, "seed": seed, "rhos": rhos, "angle": [audits.max_angle_deg(g.V, a[:, world.block_slice(g.k)]) for g in rungs], "gap": [g.gap_ratio for g in rungs], "applied": [bool(g.applied) for g in rungs]}
        out.append(rec); print(rungs_n, seed, [round(x, 1) for x in rec["angle"]], [round(x) for x in rec["gap"]], round(time.time() - t0), "s", flush=True)
        json.dump(out, open("results/deep_ladder.json", "w"))
