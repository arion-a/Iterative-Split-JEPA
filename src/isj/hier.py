"""Hierarchical AR world (MATHEMATICAL_PLAN §2.1, minimal): five 4-d blocks, per-step AR(1) coefficients a_k, unit stationary variance,
scrambled by the existing coupling map. Depth (blocks, timescales) is planted; state counts are not (D17-5)."""

from __future__ import annotations

import numpy as np
import torch

from .worlds import BlockWorld, CouplingMap

A_COEF = (0.20, 0.50, 0.75, 0.90, 0.95)


def make_world(seed: int, a=A_COEF, block=4):
    world = BlockWorld([block] * len(a), list(a), seed=seed)
    return world, CouplingMap(world.d, 4, 0.5, None, seed=seed)


def trajectories(a=A_COEF, block=4, n: int = 100, t: int = 100, seed: int = 0) -> np.ndarray:
    """(n, t, 5*block) stationary AR(1) paths."""
    g = torch.Generator().manual_seed(seed)
    rho = torch.cat([torch.full((block,), r) for r in a])
    z = torch.randn(n, len(a) * block, generator=g)
    out = [z]
    for _ in range(t - 1):
        z = rho * z + torch.sqrt(1 - rho**2) * torch.randn_like(z)
        out.append(z)
    return torch.stack(out, 1).numpy()


def oracle_cut_gaps(a=A_COEF, tau: int = 1) -> list[float]:
    """Adjacent-cut gap (1 - a_k^tau)/(1 - a_{k+1}^tau): the difference-moment eigenvalue ratio across level k/k+1."""
    return [(1 - a[k] ** tau) / (1 - a[k + 1] ** tau) for k in range(len(a) - 1)]
