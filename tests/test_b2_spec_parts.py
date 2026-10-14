import torch

from isj.cluster import kmeans, pairs_within_clusters
from isj.stage_b2_spec import cross_cluster_pairs, discover_k, silhouette
from isj.worlds import HierarchicalMixtureWorld


def blobs(k=5, n=600, spread=0.1, d=4, seed=0):
    g = torch.Generator().manual_seed(seed)
    c = 4 * torch.randn(k, d, generator=g)
    lab = torch.randint(0, k, (n,), generator=g)
    return c[lab] + spread * torch.randn(n, d, generator=g), lab


def test_discover_k_finds_the_planted_count():
    x, _ = blobs(5)
    k, scores = discover_k(x, subsample=600)
    assert k == 5


def test_silhouette_is_high_for_clean_clusters_and_low_for_random_labels():
    x, lab = blobs(4)
    assert silhouette(x, lab) > 0.8
    assert silhouette(x, torch.randint(0, 4, (len(x),))) < 0.1


def test_cross_cluster_pairs_never_share_a_cluster():
    lab = torch.randint(0, 6, (3000,))
    i, j = cross_cluster_pairs(lab, 2000)
    assert len(i) == 2000 and bool((lab[i] != lab[j]).all())


def test_singletons_give_no_pairs():
    assert len(pairs_within_clusters(torch.arange(500))[0]) == 0


def test_hierarchical_world_levels():
    w = HierarchicalMixtureWorld([4, 4, 4], [0.2, 0.7, 0.95], seed=0)
    z, lab = w.sample_with_labels(3000)
    assert z.shape == (3000, 12) and int(lab["ident"].max()) == 19 and int(lab["tex"].max()) == 1
    u, v = w.correspondence_pairs(500, 1)
    assert float((u[:, 4:] - v[:, 4:]).abs().max()) == 0.0 and float((u[:, :4] - v[:, :4]).abs().mean()) > 0.1
    a, b = w.transition_pairs(500)
    assert a.shape == b.shape == (500, 12)
