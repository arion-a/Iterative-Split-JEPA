"""The correspondence terms of the encoder objective (E40-E43): each runs, stays finite, and is refused where it would be silently ignored."""
import pytest
import torch

from isj.encoder import EncoderConfig, encode, train_encoder
from isj.worlds import BlockWorld, CouplingMap


def _train(**kw):
    world = BlockWorld([2, 2, 2], [0.2, 0.7, 0.95], seed=0)
    obs = CouplingMap(world.d, 2, 0.5, None, seed=0)
    cfg = EncoderConfig(in_dim=obs.obs_dim, latent_dim=world.d, steps=30, batch_size=64, hidden=16, reg="hinge", **kw)
    enc, log = train_encoder(world, obs, cfg, 1)
    return encode(enc, obs, world.sample(500)), log


@pytest.mark.parametrize("kw", [dict(corr_inv_weight=1.0), dict(corr_inv_weight=1.0, corr_var_weight=1.0), dict(corr_inv_weight=1.0, corr_whiten_weight=1.0)])
def test_terms_run_and_stay_finite(kw):
    h, log = _train(**kw)
    assert torch.isfinite(h).all() and all(torch.isfinite(torch.tensor(r["pred"])) for r in log)


def test_terms_refused_with_other_objective():
    with pytest.raises(AssertionError):
        _train(objective="lejepa", corr_whiten_weight=1.0)
