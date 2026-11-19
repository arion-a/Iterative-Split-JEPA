"""The one question: how does iterated splitting do over 6 rungs (7 layers of 4 numbers)? Exact pairs, mild bend, encoder left untrained.
    python experiments/simple_depth.py -> results/simple_depth.json"""
import json, torch
from isj import audits
from isj.engine import fit_ladder, fit_whitener
from isj.worlds import BlockWorld, CouplingMap
rhos = [0.2, 0.4, 0.55, 0.7, 0.8, 0.9, 0.95]; out = []
for seed in range(250, 255):
    world = BlockWorld([4] * 7, rhos, seed=seed); d = world.d
    obs = CouplingMap(d, 4, 0.5, None, seed=seed)
    wh = fit_whitener(obs(world.sample(30000)), 1e-5); R = lambda z: wh(obs(z))
    pairs = lambda k: tuple(R(t) for t in world.correspondence_pairs(30000, k)) if k <= 6 else None
    rungs = fit_ladder(pairs, d, d_ks=[4] * 6, nesting_enforcement="hard")
    z = world.sample(20000); r = R(z); a = audits.ridge_fit(z[:15000], r[:15000])[:-1].T
    out.append({"seed": seed, "angle": [audits.max_angle_deg(g.V, a[:, world.block_slice(g.k)]) for g in rungs], "gap": [g.gap_ratio for g in rungs]})
    print(seed, [round(x, 1) for x in out[-1]["angle"]], [round(x) for x in out[-1]["gap"]])
json.dump(out, open("results/simple_depth.json", "w"))
