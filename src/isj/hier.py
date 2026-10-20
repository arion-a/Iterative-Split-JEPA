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


class CoupledWorld(BlockWorld):
    """Two 4-d blocks (fast, slow). The slow block's one-step update is driven by the fast block: slow' = a_s slow + c fast + sigma eps,
    sigma^2 = 1 - a_s^2 - c^2 (unit stationary variance). c = 0 is the uncoupled control. The slow block alone is then not dynamically closed (E36)."""

    def __init__(self, a_fast: float, a_slow: float, c: float, seed: int = 0):
        super().__init__([4, 4], [a_fast, a_slow], seed=seed)
        self.c, self.sigma = c, float(np.sqrt(1 - a_slow**2 - c**2))

    def _step(self, z: torch.Tensor, eps: torch.Tensor) -> torch.Tensor:
        af, as_ = self.rhos
        fast = af * z[:, :4] + np.sqrt(1 - af**2) * eps[:, :4]
        slow = as_ * z[:, 4:] + self.c * z[:, :4] + self.sigma * eps[:, 4:]
        return torch.cat([fast, slow], 1)

    def transition_pairs(self, n: int):
        z = self.sample(n)
        return z, self._step(z, torch.randn(n, self.d, generator=self._g))


def coupled_trajectories(world: CoupledWorld, n: int, t: int, seed: int) -> np.ndarray:
    g = torch.Generator().manual_seed(seed)
    z = torch.randn(n, world.d, generator=g)
    out = [z]
    for _ in range(t - 1):
        z = world._step(z, torch.randn(n, world.d, generator=g))
        out.append(z)
    return torch.stack(out, 1).numpy()


def oracle_cut_gaps(a=A_COEF, tau: int = 1) -> list[float]:
    """Adjacent-cut gap (1 - a_k^tau)/(1 - a_{k+1}^tau): the difference-moment eigenvalue ratio across level k/k+1."""
    return [(1 - a[k] ** tau) / (1 - a[k + 1] ** tau) for k in range(len(a) - 1)]
