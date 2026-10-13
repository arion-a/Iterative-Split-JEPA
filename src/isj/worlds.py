"""Synthetic block worlds: latent dynamics, correspondence families, observation maps.

Convention (monograph Assumption 2.1): blocks z_1..z_L are ordered fast -> slow.
Rung k varies block k and holds every slower block (j > k) fixed; blocks faster
than k were already removed by earlier rungs, so they are resampled freely.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import torch


def _gen(seed: int) -> torch.Generator:
    return torch.Generator().manual_seed(int(seed))


@dataclass
class BlockWorld:
    """Stationary block-diagonal Gaussian AR(1): z_{t+1} = a_k z_t + eps, blockwise.

    Stationary covariance of block k is scales[k]**2 * I.
    """

    block_dims: list[int]
    rhos: list[float]
    scales: list[float] | None = None
    seed: int = 0
    _g: torch.Generator = field(init=False, repr=False)

    def __post_init__(self):
        assert len(self.block_dims) == len(self.rhos)
        if self.scales is None:
            self.scales = [1.0] * len(self.block_dims)
        self._g = _gen(self.seed)

    @property
    def d(self) -> int:
        return sum(self.block_dims)

    @property
    def n_blocks(self) -> int:
        return len(self.block_dims)

    def block_slice(self, k: int) -> slice:
        """Coordinate slice of block k (1-based)."""
        start = sum(self.block_dims[: k - 1])
        return slice(start, start + self.block_dims[k - 1])

    def _scale_vec(self) -> torch.Tensor:
        return torch.cat([torch.full((m,), s) for m, s in zip(self.block_dims, self.scales)])

    def _rho_vec(self) -> torch.Tensor:
        return torch.cat([torch.full((m,), r) for m, r in zip(self.block_dims, self.rhos)])

    def sample(self, n: int) -> torch.Tensor:
        return torch.randn(n, self.d, generator=self._g) * self._scale_vec()

    def transition_pairs(self, n: int) -> tuple[torch.Tensor, torch.Tensor]:
        """(z_t, z_{t+1}) from the stationary chain."""
        z = self.sample(n)
        rho = self._rho_vec()
        eps = torch.randn(n, self.d, generator=self._g) * self._scale_vec()
        return z, rho * z + torch.sqrt(1 - rho**2) * eps

    def correspondence_pairs(
        self, n: int, k: int, rank: int | None = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Tuples from D_k: agree on blocks j > k, vary block k.

        Blocks j < k are resampled independently (already removed content).
        `rank` restricts the variation of block k to its first `rank` coordinates
        (the rank-1 injection control: Sigma_Delta_k rank-deficient).
        """
        u = self.sample(n)
        v = u.clone()
        fresh = self.sample(n)
        for j in range(1, k + 1):
            sl = self.block_slice(j)
            if j == k and rank is not None:
                sl = slice(sl.start, sl.start + rank)
            v[:, sl] = fresh[:, sl]
        return u, v

    def shuffled_pairs(self, n: int, k: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Control: genuine D_k pairs with the partner rows permuted (correspondence destroyed)."""
        u, v = self.correspondence_pairs(n, k)
        perm = torch.randperm(n, generator=self._g)
        return u, v[perm]


def _orthogonal(m: int, n: int, g: torch.Generator) -> torch.Tensor:
    q, _ = torch.linalg.qr(torch.randn(m, n, generator=g))
    return q


class CouplingMap:
    """Alternating additive tanh couplings (volume preserving, invertible), then an optional
    fixed isometric lift to `obs_dim` dimensions.

    obs_dim=None (or == d) reproduces the authors' 8-dim observation process.
    """

    def __init__(self, d: int, layers: int = 4, strength: float = 0.5,
                 obs_dim: int | None = None, seed: int = 0):
        g = _gen(seed)
        self.d, self.half = d, d // 2
        self.right = d - self.half
        self.weights = []
        for i in range(layers):
            shape = (self.half, self.right) if i % 2 == 0 else (self.right, self.half)
            if shape[0] == shape[1]:
                w = strength * _orthogonal(*shape, g)
            else:
                w = strength * torch.randn(*shape, generator=g) / math.sqrt(shape[0])
            self.weights.append(w)
        self.lift = None
        if obs_dim is not None and obs_dim > d:
            self.lift = _orthogonal(obs_dim, d, g)  # (obs_dim, d), orthonormal columns
        self.obs_dim = obs_dim if self.lift is not None else d

    def __call__(self, z: torch.Tensor) -> torch.Tensor:
        x = z
        for i, w in enumerate(self.weights):
            left, right = x[:, : self.half], x[:, self.half:]
            if i % 2 == 0:
                right = right + torch.tanh(left @ w)
            else:
                left = left + torch.tanh(right @ w)
            x = torch.cat([left, right], dim=1)
        return x if self.lift is None else x @ self.lift.T


class LinearRepresentation:
    """The post-prediction representation r = U C^{-1/2} z (+ optional isotropic noise).

    U is the maximal freedom left by Lemma 3.1 / Remark 4.3. Used by the algebraic-core tests.
    """

    def __init__(self, world: BlockWorld, seed: int = 0, noise: float = 0.0):
        g = _gen(seed + 10_007)
        self.U = _orthogonal(world.d, world.d, g)
        self.inv_scale = 1.0 / world._scale_vec()
        self.noise = noise
        self.world = world
        self._g = _gen(seed + 20_011)

    def __call__(self, z: torch.Tensor) -> torch.Tensor:
        r = (z * self.inv_scale) @ self.U.T
        if self.noise > 0:
            r = r + self.noise * torch.randn(r.shape, generator=self._g)
        return r

    def true_block(self, k: int) -> torch.Tensor:
        """Orthonormal basis (D x d_k) of block k's image in representation space."""
        return self.U[:, self.world.block_slice(k)]


@dataclass
class MixtureBlockWorld(BlockWorld):
    """Three blocks (texture, identity, category). Texture and identity are Gaussian AR(1) as before.
    The category block is a mixture of `n_categories` clusters, each Gaussian inside itself:
    z3 = centre[label] + sigma * noise. Dynamics: the label persists with probability rho_3 (else is
    redrawn uniformly) and the within-cluster jitter follows an AR(1) with the same rho_3.
    """

    n_categories: int = 6
    sigma: float = 0.3
    centre_scale: float = 1.0
    centres: torch.Tensor = field(init=False, repr=False, default=None)

    def __post_init__(self):
        super().__post_init__()
        assert self.n_blocks == 3
        g = _gen(self.seed + 999)
        self.centres = self.centre_scale * torch.randn(self.n_categories, self.block_dims[2], generator=g)

    def _cat(self, n, labels=None):
        if labels is None:
            labels = torch.randint(0, self.n_categories, (n,), generator=self._g)
        jitter = self.sigma * torch.randn(n, self.block_dims[2], generator=self._g)
        return self.centres[labels] + jitter, labels, jitter

    def sample_with_labels(self, n, labels=None):
        d1, d2, _ = self.block_dims
        z12 = torch.randn(n, d1 + d2, generator=self._g)
        z3, labels, _ = self._cat(n, labels)
        return torch.cat([z12, z3], dim=1), labels

    def sample(self, n):
        return self.sample_with_labels(n)[0]

    def transition_pairs(self, n):
        d1, d2, _ = self.block_dims
        rho = self._rho_vec()
        z12 = torch.randn(n, d1 + d2, generator=self._g)
        z3, lab, jit = self._cat(n)
        eps12 = torch.randn(n, d1 + d2, generator=self._g)
        r3 = self.rhos[2]
        stay = torch.rand(n, generator=self._g) < r3
        lab2 = torch.where(stay, lab, torch.randint(0, self.n_categories, (n,), generator=self._g))
        jit2 = r3 * jit + math.sqrt(1 - r3**2) * self.sigma * torch.randn(n, self.block_dims[2], generator=self._g)
        z3b = self.centres[lab2] + jit2
        z12b = rho[: d1 + d2] * z12 + torch.sqrt(1 - rho[: d1 + d2] ** 2) * eps12
        return torch.cat([z12, z3], 1), torch.cat([z12b, z3b], 1)

    def correspondence_pairs(self, n, k, rank=None):
        """Generator-made twins: share every block slower than k EXACTLY (same label and jitter)."""
        assert rank is None
        u, v = self.sample(n), self.sample(n)
        for j in range(k + 1, self.n_blocks + 1):
            sl = self.block_slice(j)
            v[:, sl] = u[:, sl]
        return u, v

    def label_pairs(self, n):
        """Perfect-clustering pairs: same true category, independent jitter, identity and texture."""
        u, lab = self.sample_with_labels(n)
        v, _ = self.sample_with_labels(n, labels=lab)
        return u, v

    def random_pairs(self, n):
        return self.sample(n), self.sample(n)
