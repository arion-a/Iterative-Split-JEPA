import numpy as np

from isj import pendulum as pd
from isj import quotient_audit as qa


def _seq(r=40, t=120, sd_release=1.0, noise=0.05, seed=0):
    rng = np.random.default_rng(seed)
    base = rng.normal(0, sd_release, (r, 1, 1, 1))
    return base + noise * rng.normal(size=(r, 2, t, 1))


def _cert(q):
    return qa.certificate(q[:12], q[12:24], q[24:], k=8, delta=0.1, n_pairs=200, seed=0)


def test_conserved_passes():
    c = _cert(_seq(r=40))
    assert c["V"] <= 0.05 and c["icc"] >= 0.9 and c["L"] <= 1.02 and c["rollout_nmse"] <= 0.35


def test_constant_caught_by_icc():
    q = _seq(sd_release=0.0, noise=0.05)
    assert qa.icc(q) < 0.2          # V alone would not catch it (a constant map has V = 0); ICC does


def test_fast_variable_fails():
    rng = np.random.default_rng(1)
    t = np.arange(120)
    ph = rng.uniform(0, 2 * np.pi, (40, 2, 1))
    q = np.sin(0.6 * t[None, None] + ph)[..., None] + 0.02 * rng.normal(size=(40, 2, 120, 1))
    c = _cert(q)
    assert c["icc"] < 0.2 and (c["rollout_nmse"] > 0.35)


def test_lipschitz_identity_is_one():
    q = _seq()
    a, _ = qa.fit_transition(q)
    assert abs(qa.lipschitz(a) - 1.0) < 0.05


def test_damped_eps_from_drift():
    """With friction the energy is only approximately conserved: eps calibrated on measured drift keeps V small."""
    rng = np.random.default_rng(0)
    s0 = pd.sample_initial(40, rng)
    e = pd.energy(pd.simulate(s0, 120, 0.05, 1e-3, gamma=0.05))[:, None, :, None]
    e = np.repeat(e, 2, axis=1)
    c = qa.certificate(e[:12], e[12:24], e[24:], k=8)
    assert c["V"] <= 0.05 and c["icc"] > 0.5


def test_anova_icc_known_values():
    from isj import handshake_eval as ev
    rng = np.random.default_rng(0)
    base = rng.normal(0, 1, (60, 1))                                   # between-group sd 1, within sd 0.5 -> ICC = 1 / (1 + 0.25) = 0.8
    vals = base + 0.5 * rng.normal(size=(60, 40))
    valid = rng.random((60, 40)) > 0.15                                # unbalanced
    assert abs(ev.anova_icc(vals, valid) - 0.8) < 0.05
    assert abs(ev.anova_icc(rng.normal(size=(60, 40)), valid)) < 0.05    # pure noise -> 0
