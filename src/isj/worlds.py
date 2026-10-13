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
    isotropic_centres: bool = True      # every category direction gets equal between-cluster spread (needs K > d3)
    centres: torch.Tensor = field(init=False, repr=False, default=None)

    def __post_init__(self):
        super().__post_init__()
        assert self.n_blocks == 3
        g = _gen(self.seed + 999)
        c = torch.randn(self.n_categories, self.block_dims[2], generator=g)
        if self.isotropic_centres:
            # K centres can only spread over K-1 directions; a category block with more directions than that
            # would have directions that hold nothing but within-cluster jitter (whitening then inflates it).
            assert self.n_categories > self.block_dims[2], "need more categories than category-block directions"
            c = c - c.mean(0)
            cov = c.T @ c / self.n_categories
            vals, vecs = torch.linalg.eigh(cov)
            c = c @ (vecs * vals.rsqrt()) @ vecs.T          # empirical between-cluster covariance = identity
        self.centres = self.centre_scale * c

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


@dataclass
class HierarchicalMixtureWorld(BlockWorld):
    """The B2 world (docs/B2.md): categories contain identities, identities contain textures, every
    level a tight Gaussian cluster. 6 category centres; per category `n_identities` identity centres;
    per identity `n_textures` texture centres. A sample picks (category, identity, texture) and adds
    Gaussian jitter at each level: z3 = category centre + sigma_cat * noise, z2 = identity centre +
    sigma_id * noise, z1 = texture centre + sigma_tex * noise. Blocks: [texture, identity, category].
    Dynamics: each label persists with the block's rho (else redrawn), each jitter follows an AR(1).
    """

    n_categories: int = 6
    n_identities: int = 20
    n_textures: int = 2
    sigma_cat: float = 0.3          # within-category spread; the separation knob (unit between-category spread)
    sigma_id: float = 0.3
    sigma_tex: float = 0.3
    cat_c: torch.Tensor = field(init=False, repr=False, default=None)
    id_c: torch.Tensor = field(init=False, repr=False, default=None)
    tex_c: torch.Tensor = field(init=False, repr=False, default=None)

    def __post_init__(self):
        super().__post_init__()
        assert self.n_blocks == 3
        d1, d2, d3 = self.block_dims
        K, I, T = self.n_categories, self.n_identities, self.n_textures
        assert K > d3, "need more categories than category-block directions"
        g = _gen(self.seed + 4242)
        c = torch.randn(K, d3, generator=g)
        c = c - c.mean(0)
        vals, vecs = torch.linalg.eigh(c.T @ c / K)
        self.cat_c = c @ (vecs * vals.rsqrt()) @ vecs.T         # isotropic between-category spread
        self.id_c = torch.randn(K, I, d2, generator=g)
        self.tex_c = torch.randn(K, I, T, d1, generator=g)

    def _build(self, cat, ident, tex, j1, j2, j3):
        z1 = self.tex_c[cat, ident, tex] + self.sigma_tex * j1
        z2 = self.id_c[cat, ident] + self.sigma_id * j2
        z3 = self.cat_c[cat] + self.sigma_cat * j3
        return torch.cat([z1, z2, z3], dim=1)

    def _draw(self, n, cat=None, ident=None, tex=None):
        d1, d2, d3 = self.block_dims
        g = self._g
        cat = torch.randint(0, self.n_categories, (n,), generator=g) if cat is None else cat
        ident = torch.randint(0, self.n_identities, (n,), generator=g) if ident is None else ident
        tex = torch.randint(0, self.n_textures, (n,), generator=g) if tex is None else tex
        j = [torch.randn(n, d, generator=g) for d in (d1, d2, d3)]
        return cat, ident, tex, j

    def sample_with_labels(self, n, cat=None, ident=None, tex=None):
        cat, ident, tex, j = self._draw(n, cat, ident, tex)
        return self._build(cat, ident, tex, *j), {"cat": cat, "ident": ident, "tex": tex}

    def sample(self, n):
        return self.sample_with_labels(n)[0]

    def transition_pairs(self, n):
        cat, ident, tex, j = self._draw(n)
        z0 = self._build(cat, ident, tex, *j)
        r1, r2, r3 = self.rhos
        g = self._g
        keep3 = torch.rand(n, generator=g) < r3
        cat2 = torch.where(keep3, cat, torch.randint(0, self.n_categories, (n,), generator=g))
        keep2 = (torch.rand(n, generator=g) < r2) & (cat2 == cat)
        ident2 = torch.where(keep2, ident, torch.randint(0, self.n_identities, (n,), generator=g))
        keep1 = (torch.rand(n, generator=g) < r1) & (ident2 == ident) & (cat2 == cat)
        tex2 = torch.where(keep1, tex, torch.randint(0, self.n_textures, (n,), generator=g))
        ar = lambda x, r: r * x + math.sqrt(1 - r**2) * torch.randn(x.shape, generator=g)
        z1 = self._build(cat2, ident2, tex2, ar(j[0], r1), ar(j[1], r2), ar(j[2], r3))
        return z0, z1

    def correspondence_pairs(self, n, k, rank=None):
        """Generator twins: share every block slower than k EXACTLY (same labels and jitter)."""
        assert rank is None
        u, lab = self.sample_with_labels(n)
        if k == 1:
            v, _ = self.sample_with_labels(n, cat=lab["cat"], ident=lab["ident"])
            v[:, 4:] = u[:, 4:]
        else:
            v, _ = self.sample_with_labels(n, cat=lab["cat"])
            v[:, 8:] = u[:, 8:]
        return u, v

    def label_pairs(self, n):
        """Perfect-clustering pairs: same true category, everything else independent."""
        u, lab = self.sample_with_labels(n)
        v, _ = self.sample_with_labels(n, cat=lab["cat"])
        return u, v

    def random_pairs(self, n):
        return self.sample(n), self.sample(n)
