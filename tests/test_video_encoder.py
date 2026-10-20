import numpy as np

from isj import video_encoder as ve


def test_no_collapse_and_shapes():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(8, 2, 60, 40)).astype(np.float32)
    cfg = dict(latent_dim=6, hidden=32, steps=300, batch_size=64, lr=3e-3, horizons=[1, 8], var_weight=1e-2, cov_weight=0.04)
    enc, log = ve.train_encoder(x, cfg, 0)
    z = ve.encode(enc, x)
    assert z.shape == (8, 2, 60, 6)
    assert z.reshape(-1, 6).std(0).min() >= 0.5, log[-1]
