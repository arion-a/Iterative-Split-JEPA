"""G4-K: the cluster count is selected in the slow subspace of the invariant output."""
import torch

from isj.cluster import slow_subspace_k
from isj.worlds import HierarchicalMixtureWorld


def world(rhos, seed=0, sigma_cat=0.4):
    return HierarchicalMixtureWorld([4, 4, 4], rhos, seed=seed, n_categories=6, n_identities=20, n_textures=2, sigma_cat=sigma_cat)


def data(w, n=6000, n_pairs=20000):
    x = w.sample(n)[:, 4:]                       # identity + category (the rung-1 invariant truth)
    a, b = w.transition_pairs(n_pairs)
    return x, a[:, 4:], b[:, 4:]


def test_finds_six_in_the_slow_subspace_where_the_full_space_does_not():
    from isj.cluster import spectral_k
    for seed in (0, 1):
        w = world([0.2, 0.7, 0.95], seed=seed)
        x, a, b = data(w)
        k, info = slow_subspace_k(x, a, b, seed=seed)
        assert k == 6 and info["d"] == 4 and not info["abstained"] and info["ratio"] > 2.0
        assert spectral_k(x, seed=seed)[0] != 6              # the E18 failure in the full invariant space


def test_abstains_when_speeds_are_equal_or_time_order_is_destroyed():
    w = world([0.5, 0.5, 0.5])
    x, a, b = data(w)
    assert slow_subspace_k(x, a, b)[0] is None and slow_subspace_k(x, a, b)[1]["abstained"]
    w = world([0.2, 0.7, 0.95])
    x, a, b = data(w)
    shuffled = b[torch.randperm(len(b), generator=torch.Generator().manual_seed(1))]
    assert slow_subspace_k(x, a, shuffled)[0] is None


def test_deterministic_and_basis_is_orthonormal():
    w = world([0.2, 0.7, 0.95])
    x, a, b = data(w)
    k1, i1 = slow_subspace_k(x, a, b, seed=3)
    k2, i2 = slow_subspace_k(x, a, b, seed=3)
    assert k1 == k2 and torch.allclose(i1["basis"], i2["basis"])
    assert torch.allclose(i1["basis"].T @ i1["basis"], torch.eye(i1["d"]), atol=1e-5)
