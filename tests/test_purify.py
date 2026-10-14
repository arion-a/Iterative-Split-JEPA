"""D10a: Tier 1 purification drops mis-grouped pairs; Tier 4 within-H1 whitening keeps rung 2 inside H1."""
import torch

from isj.audits import max_angle_deg
from isj.engine import fit_rung, purify_pairs
from isj.worlds import BlockWorld, LinearRepresentation


def setup(frac_bad=0.2, n=30_000):
    w = BlockWorld([2, 2, 2], [0.2, 0.7, 0.95], seed=0)
    rep = LinearRepresentation(w, seed=0, noise=0.1)
    u1, v1 = w.correspondence_pairs(n, 1)
    r1 = fit_rung(rep(u1), rep(v1), torch.eye(w.d), k=1, d_k=2)
    u, v = w.correspondence_pairs(n, 2)
    bad = torch.rand(n) < frac_bad                      # mis-grouped pairs: the partner is an unrelated sample
    v = torch.where(bad[:, None], w.sample(n), v)
    return w, rep, r1, rep(u), rep(v), bad


def test_purification_removes_bad_pairs_and_raises_the_gap():
    w, rep, r1, ru, rv, bad = setup()
    raw = fit_rung(ru, rv, r1.Q, k=2, d_k=2)
    keep, iters = purify_pairs(ru, rv, r1.Q, 2)
    pur = fit_rung(ru[keep], rv[keep], r1.Q, k=2, d_k=2)
    print(f"\ngap {raw.gap_ratio:.1f} -> {pur.gap_ratio:.1f}; dropped {float((~keep)[bad].float().mean()):.2f} of bad, {float((~keep)[~bad].float().mean()):.2f} of good; {iters} iterations")
    assert pur.gap_ratio > raw.gap_ratio
    assert (~keep)[bad].float().mean() > 0.8 and (~keep)[~bad].float().mean() < 0.15


def test_purification_keeps_clean_pairs():
    w, rep, r1, ru, rv, bad = setup(frac_bad=0.0)
    keep, _ = purify_pairs(ru, rv, r1.Q, 2)
    assert keep.float().mean() > 0.9


def test_within_whitening_stays_inside_h1():
    w, rep, r1, ru, rv, bad = setup(frac_bad=0.0)
    fit = fit_rung(ru, rv, r1.Q, k=2, d_k=2, within_whitening=True)
    assert float(((torch.eye(w.d) - r1.Q @ r1.Q.T) @ fit.V).norm()) < 1e-5
    assert max_angle_deg(fit.V, torch.cat([rep.true_block(2), rep.true_block(3)], 1)) < 1.0
