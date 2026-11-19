"""E18: spectral (Laplacian eigengap) cluster-count selection."""
import torch

from isj.cluster import spectral_k


def blobs(k, d=8, sep=6.0, n_per=400, noise=1.0, seed=0):
    g = torch.Generator().manual_seed(seed)
    centres = torch.randn(k, d, generator=g)
    centres = centres / centres.norm(dim=1, keepdim=True) * sep
    x = torch.cat([c + noise * torch.randn(n_per, d, generator=g) for c in centres])
    return x, torch.arange(k).repeat_interleave(n_per)


def test_finds_the_count_of_well_separated_blobs():
    for k in (3, 5, 6, 8):
        x, _ = blobs(k, seed=k)
        found, info = spectral_k(x, subsample=1500)
        assert found == k, (k, found, info["gaps"])


def test_uses_no_labels_and_is_deterministic():
    x, _ = blobs(4, seed=11)
    a, ia = spectral_k(x, subsample=1000, seed=3)
    b, ib = spectral_k(x, subsample=1000, seed=3)
    assert a == b and ia["gaps"] == ib["gaps"]


def test_single_blob_does_not_claim_many_clusters_with_a_large_gap():
    g = torch.Generator().manual_seed(5)
    x = torch.randn(1500, 8, generator=g)
    found, info = spectral_k(x, subsample=1200)
    sep, _ = blobs(6, seed=2)
    _, info_sep = spectral_k(sep, subsample=1200)
    assert max(info["gaps"].values()) < max(info_sep["gaps"].values())          # a structureless cloud has a smaller eigengap than real clusters
