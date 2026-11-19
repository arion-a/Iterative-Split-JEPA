import pytest
import torch

from isj.cluster import kmeans, pairs_within_clusters, purity
from isj.worlds import MixtureBlockWorld


def world(k, **kw):
    return MixtureBlockWorld([4, 4, 4], [0.2, 0.7, 0.95], seed=0, n_categories=k, **kw)


@pytest.mark.parametrize("k", [6, 12, 24])
def test_every_category_direction_has_equal_spread(k):
    c = world(k).centres
    cov = (c - c.mean(0)).T @ (c - c.mean(0)) / k
    assert torch.allclose(cov, torch.eye(4), atol=1e-4)      # isotropic between-cluster spread


def test_too_few_categories_is_refused():
    with pytest.raises(AssertionError):
        world(3)                                              # 3 centres cannot fill a 4-direction block


def test_generator_twins_share_category_exactly_and_label_pairs_share_label():
    w = world(6)
    u, v = w.correspondence_pairs(500, 2)
    assert float((u[:, 8:] - v[:, 8:]).abs().max()) == 0.0
    u, v = w.label_pairs(2000)
    assert float((u[:, 8:] - v[:, 8:]).norm(dim=1).mean()) < 1.0   # same cluster: only jitter differs


def test_kmeans_recovers_well_separated_categories():
    w = world(6, sigma=0.05)
    z, lab = w.sample_with_labels(4000)
    km, _, _ = kmeans(z[:, 8:], 6, restarts=5)
    assert purity(km, lab) > 0.95
    i, j = pairs_within_clusters(km)
    assert float((lab[i] == lab[j]).float().mean()) > 0.95
