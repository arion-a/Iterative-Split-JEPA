"""Stage B maths-only core: a three-level chain (texture, identity, category) plus one planted
cross-cutting factor that varies in every correspondence family. No encoder involved."""
import numpy as np

from isj.audits import deviation_map, max_angle_deg
from isj.engine import fit_ladder
from isj.worlds import BlockWorld, LinearRepresentation

DIMS = [4, 4, 4]


def run(seed, cross, n=40_000):
    dims = DIMS + ([1] if cross else [])
    world = BlockWorld(dims, [0.2, 0.7, 0.95] + ([0.5] if cross else []), seed=seed,
                       cross_block=4 if cross else None, cross_p=0.5)
    rep = LinearRepresentation(world, seed=seed)

    def pairs_fn(k):
        if k > 2:
            return None
        u, v = world.correspondence_pairs(n, k)
        return rep(u), rep(v)

    return world, rep, fit_ladder(pairs_fn, world.d, d_ks=[4, 4])


def test_chain_world_has_no_deviation():
    world, rep, rungs = run(0, cross=False)
    dm = deviation_map(rungs)
    assert dm["T"] < 0.05
    assert all(max_angle_deg(r.V, rep.true_block(r.k)) < 0.5 for r in rungs)


def test_cross_cutting_factor_is_localized():
    world, rep, rungs = run(0, cross=True)
    # nominal rungs are still recovered despite the extra factor (plan threshold 5 deg); the residual
    # error is sampling noise, because the factor occupies part of the spectrum
    errs = [max_angle_deg(r.V, rep.true_block(r.k)) for r in rungs]
    assert all(e < 5 for e in errs)
    big = run(0, cross=True, n=160_000)
    errs_big = [max_angle_deg(r.V, big[1].true_block(r.k)) for r in big[2]]
    assert all(b < e for b, e in zip(errs_big, errs)) and all(b < 1.0 for b in errs_big)
    dm = deviation_map(rungs)
    assert dm["T"] > 1.5                                   # about 2 rungs x (2 * p * var) = 2.0
    assert max(dm["between_rung_angles_deg"]) < 3          # the same direction recurs at every rung
    truth = rep.true_block(4)
    assert all(max_angle_deg(p["direction"].unsqueeze(1), truth) < 3 for p in dm["per_rung"])


def test_detector_separates_cross_from_chain_across_seeds():
    t_null = [deviation_map(run(s, False, 20_000)[2])["T"] for s in range(5)]
    t_alt = [deviation_map(run(s, True, 20_000)[2])["T"] for s in range(5)]
    assert max(t_null) < min(t_alt) / 10
