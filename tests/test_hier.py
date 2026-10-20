import numpy as np

from isj import hier


def test_world_stats_autocorrelation_matches_coefficients():
    z = hier.trajectories(n=400, t=60, seed=0)
    for k, a in enumerate(hier.A_COEF):
        blk = z[:, :, 4 * k:4 * k + 4]
        c = np.mean(blk[:, 1:] * blk[:, :-1]) / np.mean(blk[:, :-1] ** 2)
        assert abs(c - a) < 0.03, (k, c, a)
        assert abs(blk.std() - 1) < 0.05


def test_oracle_gap_arithmetic():
    g1 = hier.oracle_cut_gaps(tau=1)
    assert np.allclose(g1, [1.6, 2.0, 2.5, 2.0])
    tr = [np.log(a) for a in hier.A_COEF]
    ratios = [tr[k] / tr[k + 1] for k in range(4)]            # adjacent timescale ratios = tau-> 0 limit of the cut gap
    assert np.allclose(hier.oracle_cut_gaps(tau=1e-6), ratios, atol=1e-4)
    for tau in (1, 2, 4, 8):                                   # the gap never exceeds the timescale ratio
        assert all(g <= r + 1e-9 for g, r in zip(hier.oracle_cut_gaps(tau=tau), ratios))
