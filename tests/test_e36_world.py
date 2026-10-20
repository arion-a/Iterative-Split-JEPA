"""E36 world sanity, independent of any encoder: the coupled world has unit stationary variance and its slow block is NOT closed
(closure ratio ~ (c^2 + sigma^2) / sigma^2 = 3.1), the uncoupled control is closed (ratio ~ 1)."""
import numpy as np

from isj import hier


def _ratio(c, seed=0):
    w = hier.CoupledWorld(0.1, 0.97, c, seed=seed)
    z = hier.coupled_trajectories(w, 400, 60, seed)
    x, y = z[:, :-1].reshape(-1, 8), z[:, 1:, 4:].reshape(-1, 4)
    def resid(feat):
        a = np.concatenate([feat, np.ones((len(feat), 1))], 1)
        p = a @ np.linalg.lstsq(a, y, rcond=None)[0]
        return ((y - p) ** 2).sum()
    return resid(x[:, 4:]) / resid(x), z


def test_unit_stationary_variance():
    _, z = _ratio(0.2)
    assert abs(z[:, 20:].std() - 1) < 0.05


def test_coupled_world_not_closed_and_control_closed():
    r_c, _ = _ratio(0.2)
    r_0, _ = _ratio(0.0)
    assert 2.5 < r_c < 3.8, r_c            # registered arithmetic: about 3.1
    assert 0.95 < r_0 < 1.1, r_0
