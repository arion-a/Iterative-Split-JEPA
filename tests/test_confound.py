import numpy as np

from isj import handshake_eval as ev


def test_local_amplitude_tracks_swing_size():
    t = np.arange(400)
    small = 0.3 * np.sin(0.1 * t); big = 1.5 * np.sin(0.1 * t)
    a = ev.local_amplitude(np.stack([small, big]), np.stack([small, big]))
    assert np.nanmedian(a[1]) > 3 * np.nanmedian(a[0])
    bad = np.full((1, 400), np.nan)
    assert np.isnan(ev.local_amplitude(bad, bad)).all()


def test_partial_spearman_removes_a_common_driver():
    rng = np.random.default_rng(0)
    z = rng.normal(size=4000); x = z + 0.3 * rng.normal(size=4000); y = z + 0.3 * rng.normal(size=4000)
    from scipy.stats import spearmanr
    assert spearmanr(x, y)[0] > 0.8
    assert abs(ev.partial_spearman(x, y, z)) < 0.05                    # same driver -> no partial correlation left
    w = rng.normal(size=4000)
    assert ev.partial_spearman(z + w, w, z) > 0.9                     # independent part survives
