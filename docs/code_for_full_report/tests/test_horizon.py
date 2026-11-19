"""E11a: lag-k chains from the hierarchical world and the multi-step alignment option."""
import pytest
import torch

from isj.encoder import EncoderConfig, train_encoder
from isj.worlds import CouplingMap, HierarchicalMixtureWorld


def world(seed=0):
    return HierarchicalMixtureWorld([4, 4, 4], [0.2, 0.7, 0.95], seed=seed, n_categories=6, n_identities=20, n_textures=2, sigma_cat=0.1)


def test_horizon_one_is_the_original_pair_sampler():
    a, b = world().transition_pairs(300)
    c = world().transition_chain(300, 1)
    assert torch.equal(a, c[0]) and torch.equal(b, c[1])


def test_chain_length_and_persistence_decays_with_lag():
    w = world()
    ch = w.transition_chain(20_000, 3)
    assert len(ch) == 4 and all(x.shape == (20_000, 12) for x in ch)
    corr = lambda x, y: float(((x - x.mean(0)) * (y - y.mean(0))).mean() / (x.std() * y.std()))
    cat = [corr(ch[0][:, 8:], ch[k][:, 8:]) for k in (1, 2, 3)]          # slow block: persists
    tex = [corr(ch[0][:, :4], ch[k][:, :4]) for k in (1, 2, 3)]          # fast block: gone after a step or two
    assert cat[0] > cat[1] > cat[2] > 0.5
    assert tex[2] < 0.5 * tex[0]                                          # fast block: lag-3 correlation under half of lag-1


def test_multistep_training_runs_and_guards():
    w = world()
    obs = CouplingMap(12, 4, 0.5, None, seed=0)
    cfg = EncoderConfig(in_dim=12, latent_dim=12, steps=30, batch_size=64, reg="sigreg", var_weight=0.0, arch="inverse_coupling", objective="lejepa", horizon=3, log_every=10)
    enc, log = train_encoder(w, obs, cfg, 1, False)
    assert all(torch.isfinite(torch.tensor(r["pred"])) for r in log)
    bad = EncoderConfig(in_dim=12, latent_dim=12, steps=3, batch_size=16, objective="predict", horizon=2)
    with pytest.raises(AssertionError):
        train_encoder(w, obs, bad, 1, False)
