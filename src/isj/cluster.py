"""Small k-means (k-means++ init, restarts) and cluster purity, in torch."""

from __future__ import annotations

import torch


def kmeans(x: torch.Tensor, k: int, restarts: int = 10, iters: int = 100, seed: int = 0):
    g = torch.Generator().manual_seed(seed)
    best = None
    for _ in range(restarts):
        idx = torch.randint(0, len(x), (1,), generator=g)
        centres = x[idx]
        for _c in range(1, k):                                    # k-means++ seeding
            d2 = torch.cdist(x, centres).square().min(1).values
            nxt = torch.multinomial(d2 / d2.sum(), 1, generator=g)
            centres = torch.cat([centres, x[nxt]], 0)
        for _it in range(iters):
            labels = torch.cdist(x, centres).argmin(1)
            new = torch.stack([x[labels == c].mean(0) if (labels == c).any() else centres[c] for c in range(k)])
            if torch.allclose(new, centres, atol=1e-6):
                break
            centres = new
        labels = torch.cdist(x, centres).argmin(1)
        inertia = float((x - centres[labels]).square().sum())
        if best is None or inertia < best[2]:
            best = (labels, centres, inertia)
    return best


def purity(pred: torch.Tensor, true: torch.Tensor) -> float:
    """Share of samples that belong to the majority true category of their cluster."""
    total = 0
    for c in pred.unique():
        total += int(torch.bincount(true[pred == c]).max())
    return total / len(true)


def pairs_within_clusters(labels: torch.Tensor, seed: int = 0) -> tuple[torch.Tensor, torch.Tensor]:
    """Index pairs of samples in the same cluster (each sample used at most once)."""
    g = torch.Generator().manual_seed(seed)
    a, b = [], []
    for c in labels.unique():
        idx = (labels == c).nonzero().flatten()
        idx = idx[torch.randperm(len(idx), generator=g)]
        m = len(idx) // 2 * 2
        a.append(idx[0:m:2]); b.append(idx[1:m:2])
    return torch.cat(a), torch.cat(b)
