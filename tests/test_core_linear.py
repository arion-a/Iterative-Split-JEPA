"""Frozen algebraic core (monograph §12.1): five-block Gaussian world, r = U C^{-1/2} z.

Asserted (provenance: this suite is the canonical verification; earlier notebook values are
superseded): per-rung angle < 0.5 deg, own-block capture > 0.99, off-block capture < 1e-3,
destruction under shuffled correspondences, rung-localized failure under rank-1 variation,
and an n^{-1/2} noise scaling of the angle error.
"""

import math

import numpy as np
import pytest
import torch

from isj.audits import capture, max_angle_deg
from isj.engine import fit_ladder, gauge_fix
from isj.worlds import BlockWorld, LinearRepresentation

RHOS = [0.2, 0.5, 0.75, 0.9, 0.97]
D_KS = [2, 2, 2, 2]


def make(seed=0, noise=0.0, scales=None):
    world = BlockWorld([2] * 5, RHOS, scales=scales, seed=seed)
    rep = LinearRepresentation(world, seed=seed, noise=noise)
    return world, rep


def ladder(world, rep, n, mode="oracle", rank_at=None, d_ks=D_KS, gamma_min=None):
    def pairs_fn(k):
        if k >= world.n_blocks:  # no correspondence family for the invariant core
            return None
        if mode == "shuffled":
            u, v = world.shuffled_pairs(n, k)
        else:
            u, v = world.correspondence_pairs(n, k, rank=1 if k == rank_at else None)
        return rep(u), rep(v)

    return fit_ladder(pairs_fn, world.d, d_ks=d_ks, gamma_min=gamma_min)


def angles(world, rep, rungs):
    return [max_angle_deg(r.V, rep.true_block(r.k)) for r in rungs]


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_each_rung_recovers_its_block(seed):
    world, rep = make(seed, scales=[1.0, 2.0, 0.5, 1.5, 1.0])  # non-identity C exercises whitening
    # whitening is part of rep: r = U C^{-1/2} z has identity covariance
    rungs = ladder(world, rep, n=20_000)
    assert len(rungs) == 4
    for r, ang in zip(rungs, angles(world, rep, rungs)):
        own = capture(r.V, rep.true_block(r.k))
        off = sum(capture(r.V, rep.true_block(j)) for j in range(1, 6) if j != r.k)
        assert ang < 0.5
        assert own > 0.99
        assert off < 1e-3
    # filtration nests and shrinks: H_k has dimension d - sum_{j<=k} d_j
    assert [r.Q.shape[1] for r in rungs] == [8, 6, 4, 2]
    # final invariant core is block 5
    assert max_angle_deg(rungs[-1].Q, rep.true_block(5)) < 0.5


def test_gap_spectrum_is_published_and_clean():
    world, rep = make(0)
    for r in ladder(world, rep, n=20_000):
        assert r.gap_ratio > 1e3
        assert len(r.eigvals) == 10 - 2 * (r.k - 1)


def test_block_counts_from_gaps():
    world, rep = make(0)
    rungs = ladder(world, rep, n=20_000, d_ks=None, gamma_min=0.5)
    # with gap selection and no d_ks the ladder runs until content is exhausted or no gap
    assert [r.d_k for r in rungs[:4]] == [2, 2, 2, 2]
    assert [r.selected_d for r in rungs[:4]] == [2, 2, 2, 2]


def test_shuffled_correspondences_destroy_split():
    world, rep = make(0)
    rungs = ladder(world, rep, n=20_000, mode="shuffled", d_ks=[2])
    r = rungs[0]
    assert r.gap_ratio < 1.1  # flat spectrum (monograph reports 1.004)
    assert angles(world, rep, rungs)[0] > 20  # no recovery of block 1


def test_rank1_variation_fails_exactly_that_rung():
    world, rep = make(0)
    rungs = ladder(world, rep, n=20_000, rank_at=3)
    a = angles(world, rep, rungs)
    assert a[0] < 0.5 and a[1] < 0.5        # rungs above are exact
    assert a[2] > 10                       # rung 3 fails
    assert a[3] > 1                        # contamination propagates one rung down
    assert rungs[2].gap_ratio < 1e3 <= rungs[1].gap_ratio  # the gap spectrum flags it


def test_noise_scaling_is_inverse_sqrt_n():
    ns = [1_000, 10_000, 100_000, 300_000]
    errs = {1: [], 2: []}
    for n in ns:
        e = {1: [], 2: []}
        for s in range(6):
            world, rep = make(s, noise=0.15)
            rungs = ladder(world, rep, n=n, d_ks=[2, 2])
            for r, a in zip(rungs, angles(world, rep, rungs)):
                e[r.k].append(a)
        for k in e:
            errs[k].append(float(np.mean(e[k])))
    for k in errs:
        slope = np.polyfit(np.log(ns), np.log(errs[k]), 1)[0]
        assert -0.62 < slope < -0.38, (k, slope, errs[k])


def test_gauge_is_canonical_up_to_sign():
    world, rep = make(0)
    ref = torch.diag(torch.tensor([3., 1., .5, .4, .3, .2, .1, .05, .03, .01]))
    v = torch.linalg.qr(torch.randn(10, 2))[0]
    a = gauge_fix(v, ref)
    rot = torch.linalg.qr(torch.randn(2, 2))[0]
    b = gauge_fix(v @ rot, ref)
    assert torch.allclose(a, b, atol=1e-5) or torch.allclose(a, -b, atol=1e-5)
