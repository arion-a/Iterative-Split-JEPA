import numpy as np
import torch
from scipy.stats import spearmanr

from isj import engine, temporal_ladder as tl


def planted(r=60, t=120, seed=0):
    rng = np.random.default_rng(seed)
    nuis = rng.normal(0, 1, (r, 2, 1, 3)) + 0.02 * rng.normal(size=(r, 2, t, 3))      # constant per (release, rendering)
    fast = np.zeros((r, 2, t, 6)); fast[:, :, 0] = rng.normal(size=(r, 2, 6))
    for i in range(1, t):
        fast[:, :, i] = 0.5 * fast[:, :, i - 1] + np.sqrt(1 - 0.25) * rng.normal(size=(r, 2, 6))
    fast[:, 1] = fast[:, 0]                                                            # same clip in both renderings
    cons = rng.normal(0, 1, (r, 1, 1, 1)) + 0.02 * rng.normal(size=(r, 2, t, 1))
    cons[:, 1] = cons[:, 0] + 0.02 * rng.normal(size=cons[:, 1].shape)
    z = np.concatenate([np.broadcast_to(nuis, (r, 2, t, 3)), fast, np.broadcast_to(cons, (r, 2, t, 1))], axis=-1)
    q, _ = np.linalg.qr(rng.normal(size=(10, 10)))
    x = z @ q.T
    wh = engine.fit_whitener(torch.from_numpy(x.reshape(-1, 10)).float())
    xw = wh(torch.from_numpy(x.reshape(-1, 10)).float()).numpy().reshape(x.shape)
    return xw, cons[..., 0]


def test_ladder_recovers_planted():
    xw, cons = planted()
    out = tl.run_ladder(xw, [8, 32], gamma_min=2.0, b2_quantile=0.99, s1_chance_fraction=0.05)
    ks = [(r["k"], r["d_k"]) for r in out["rungs"]]
    assert ks[:2] == [(1, 3), (2, 6)], ks
    assert out["stop"] == "S1" and out["rungs"][-1]["k"] == 3 and out["core"].shape[1] == 1, (out["stop"], ks)
    psi = tl.apply_psi(xw, tl.fit_psi(xw, out["core"]))[..., 0]
    assert abs(spearmanr(psi.ravel(), cons.ravel())[0]) >= 0.99


def test_shuffled_pairs_flat():
    xw, _ = planted()
    out = tl.run_ladder(xw, [8, 32], gamma_min=2.0, b2_quantile=0.99, shuffle_temporal=True)
    assert out["rungs"][1].get("stop") == "S2"        # flat spectrum: no cut clears the gap ratio


def test_s1_skips_family_without_variation():
    xw, _ = planted()
    xw = xw.copy()
    xw[:, 1] = xw[:, 0]                                    # renderings identical: the aug family exposes nothing
    out = tl.run_ladder(xw, [8, 32], gamma_min=2.0, b2_quantile=0.99)
    assert out["rungs"][0]["stop"] == "S1" and out["rungs"][1]["d_k"] > 0
