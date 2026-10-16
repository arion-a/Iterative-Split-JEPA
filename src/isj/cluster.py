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


def spectral_k(x: torch.Tensor, k_range=range(2, 13), subsample: int = 3000, n_neighbors: int = 15, scale_neighbor: int = 7, seed: int = 0):
    """Choose the cluster count by the eigengap of the normalized graph Laplacian (decision E18; unsupervised, uses no labels).

    Graph: symmetrized k-nearest-neighbour affinity with self-tuning local scales (Zelnik-Manor and Perona: sigma_i = distance to the
    `scale_neighbor`-th neighbour, W_ij = exp(-d_ij^2 / (sigma_i sigma_j))). With L = I - D^-1/2 W D^-1/2 and eigenvalues in ascending order
    l_1 <= l_2 <= ..., k well-separated clusters give k eigenvalues near zero, so K = argmax over k in k_range of (l_{k+1} - l_k).
    Constants are standard defaults fixed before any use on the B2 world. Returns (K, info) with the eigenvalues and the gaps per k."""
    g = torch.Generator().manual_seed(seed)
    sub = x[torch.randperm(len(x), generator=g)[:subsample]].double()
    n = len(sub)
    d = torch.cdist(sub, sub)
    sigma = d.topk(scale_neighbor + 1, largest=False).values[:, -1].clamp_min(1e-12)       # index 0 is the point itself
    nn_idx = d.topk(n_neighbors + 1, largest=False).indices[:, 1:]
    w = torch.zeros(n, n, dtype=torch.float64)
    rows = torch.arange(n)[:, None].expand_as(nn_idx)
    w[rows, nn_idx] = torch.exp(-d[rows, nn_idx].square() / (sigma[rows] * sigma[nn_idx]))
    w = torch.maximum(w, w.T)
    inv_sqrt_deg = w.sum(1).clamp_min(1e-12).rsqrt()
    lap = torch.eye(n, dtype=torch.float64) - inv_sqrt_deg[:, None] * w * inv_sqrt_deg[None, :]
    kmax = max(k_range)
    ev = torch.linalg.eigvalsh(lap)[: kmax + 2]
    gaps = {int(k): float(ev[k] - ev[k - 1]) for k in k_range}                           # gap after the k-th eigenvalue
    k_star = max(gaps, key=gaps.get)
    return k_star, {"eigenvalues": [float(v) for v in ev], "gaps": gaps}
