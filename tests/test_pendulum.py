import json
import os

import numpy as np

from isj import pendulum as pd
from isj import pendulum_data, video_io


def _s0(n=6, seed=0):
    return pd.sample_initial(n, np.random.default_rng(seed))


def test_energy_conserved():
    s = pd.simulate(_s0(), 200, 0.05, 1e-3)                  # 10 s
    e = pd.energy(s)
    scale = np.abs(e).max()
    assert (np.abs(e - e[:, :1]).max() / scale) <= 1e-6


def test_step_halving():
    s0 = _s0(4)
    a = pd.simulate(s0, 100, 0.05, 1e-3)
    b = pd.simulate(s0, 100, 0.05, 5e-4)
    assert np.abs(a - b).max() <= 1e-8


def test_damped_decays():
    s = pd.simulate(_s0(), 200, 0.05, 1e-3, gamma=0.1)
    e = pd.energy(s)
    assert (e[:, -1] < e[:, 0]).all()
    assert (np.diff(e, axis=1).max(axis=1) <= 1e-6).all()    # monotone decrease up to integration error


def test_render_nuisance():
    s = _s0(1, 3)
    n1 = np.zeros((1, 4)); n2 = np.array([[0.1, 0.2, -0.1, 0.3]])
    a = pd.render(s, n1, noise=0); b = pd.render(s, n2, noise=0); a2 = pd.render(s, n1, noise=0)
    assert np.array_equal(a, a2)
    assert np.allclose(b - a, (n2 @ pd.illumination_basis(32)), atol=1e-5)   # nuisance is purely additive


def _cfg():
    return dict(n_releases=12, splits=[6, 3, 3], n_frames=20, dt_frame=0.05, dt_int=0.001, size=32,
                amp_range=[0.3, 3.1], omega_std=0.3, nuisance_amp=0.4, pixel_noise=0.01)


def test_splits_disjoint_and_audit_separate_file(tmp_path):
    out = str(tmp_path / "d")
    pendulum_data.build(_cfg(), 0, out)
    frames, split = video_io.load_frames(out)
    assert frames.shape == (12, 2, 20, 1024)
    assert [int((split == i).sum()) for i in range(3)] == [6, 3, 3]
    meta = json.load(open(os.path.join(out, "meta.json")))
    assert set(meta) <= {"shape", "split", "seed"}           # no physics keys in the discovery metadata
    audit = pendulum_data.load_audit(out)
    assert audit["energy"].shape == (12, 20) and os.path.exists(os.path.join(out, "audit.npz"))
