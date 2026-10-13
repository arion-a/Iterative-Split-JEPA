"""The split engine: whitening, difference moments, spectral split, gauge, ladder.

Eigenvalues of difference moments are indexed in DESCENDING order (monograph §7.1):
the variant block of rung k is the top-d_k eigenspace, the invariant content the complement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import torch

TINY = 1e-300


@dataclass
class Whitener:
    mean: torch.Tensor      # (D,)
    matrix: torch.Tensor    # (D, D) symmetric ZCA matrix

    def __call__(self, h: torch.Tensor) -> torch.Tensor:
        return (h - self.mean) @ self.matrix


def fit_whitener(h: torch.Tensor, eps: float = 1e-5) -> Whitener:
    """ZCA: C^{-1/2} with eigenvalue floor eps."""
    h = h.double()
    mean = h.mean(0)
    c = (h - mean).T @ (h - mean) / (len(h) - 1)
    vals, vecs = torch.linalg.eigh(c)
    w = (vecs * vals.clamp_min(eps).rsqrt()) @ vecs.T
    return Whitener(mean.float(), w.float())


def centering_only(h: torch.Tensor) -> Whitener:
    """Ablation: mean-centre without whitening."""
    d = h.shape[1]
    return Whitener(h.mean(0), torch.eye(d))


def difference_moment(ru: torch.Tensor, rv: torch.Tensor,
                      basis: torch.Tensor | None = None) -> torch.Tensor:
    """M_hat = (1/n) sum Delta Delta^T (monograph eq. 4), optionally in content coordinates."""
    delta = (ru - rv).double()
    if basis is not None:
        delta = delta @ basis.double()
    return delta.T @ delta / len(delta)


def eig_desc(m: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    vals, vecs = torch.linalg.eigh(m)
    return vals.flip(0), vecs.flip(1)


def select_block_count(vals: torch.Tensor, gamma_min: float) -> int:
    """Largest d with lambda_d - lambda_{d+1} >= gamma_min (monograph §6.2); 0 if none."""
    gaps = vals[:-1] - vals[1:]
    idx = (gaps >= gamma_min).nonzero()
    return int(idx.max()) + 1 if len(idx) else 0


def gap_ratio(vals: torch.Tensor, d_k: int) -> float:
    """lambda_{d_k} / lambda_{d_k+1} (descending order). Large <=> a clean split."""
    if d_k >= len(vals):
        return float("inf")
    return float(vals[d_k - 1] / vals[d_k].clamp_min(TINY))


def gauge_fix(v_local: torch.Tensor, ref: torch.Tensor | None = None) -> torch.Tensor:
    """Canonical within-block gauge (monograph §6.3 / Remark 4.3).

    Columns are rotated to diagonalise the symmetrised reference moment `ref` restricted to the
    block (descending), then signs are fixed so each column's largest-magnitude entry is positive.
    Without a reference only the signs are fixed. Subspaces are gauge-invariant; this only makes
    coordinates reproducible. Degenerate reference spectra leave a residual rotation freedom.
    """
    v = v_local
    if ref is not None:
        g = v.T @ ref @ v
        g = (g + g.T) / 2
        _, e = eig_desc(g)
        v = v @ e
    idx = v.abs().argmax(dim=0)
    signs = torch.sign(v[idx, torch.arange(v.shape[1])])
    signs[signs == 0] = 1
    return v * signs


@dataclass
class RungFit:
    k: int
    d_k: int
    eigvals: torch.Tensor          # descending, length m_{k-1}
    gap_ratio: float
    selected_d: int | None         # d chosen by gap rule (None if gamma_min not given)
    V: torch.Tensor                # (D, d_k) variant basis, full representation coordinates
    Q: torch.Tensor                # (D, m_k) invariant basis = H_k
    H_prev: torch.Tensor           # (D, m_{k-1}) content the rung acted on
    n_pairs: int
    M: torch.Tensor = field(repr=False, default=None)
    max_sq_diff: float = 1.0            # max ||pair difference||^2 in content coordinates (enters the rank-noise floor)
    nesting_enforcement: str = "hard"



NESTING_MODES = ("hard", "soft", "none")


def _qr_keep_orientation(v: torch.Tensor) -> torch.Tensor:
    q, r = torch.linalg.qr(v)
    sign = torch.sign(torch.diagonal(r))
    sign[sign == 0] = 1
    return q * sign


def fit_rung(ru: torch.Tensor, rv: torch.Tensor, h_prev: torch.Tensor, k: int,
             d_k: int | None = None, gamma_min: float | None = None,
             gauge_ref: torch.Tensor | None = None,
             nesting_enforcement: str = "hard", soft_lambda: float = 100.0) -> RungFit:
    """One split on content H_{k-1}. ru/rv are whitened representations of D_k tuples.

    nesting_enforcement (decision D9):
      hard (default): eigendecompose the difference moment in H_{k-1} coordinates and map back, so V lies in H_{k-1} by
          construction; then V <- P V and re-orthonormalize (QR) as an explicit guard (a numerical no-op here).
      soft (INACTIVE in confirmatory runs): top eigenvectors of M - lambda (I - P) in full coordinates; approaches hard as lambda grows.
      none (ablation): top eigenvectors of the unrestricted full-coordinate moment; V may leave H_{k-1}.
    """
    if nesting_enforcement not in NESTING_MODES:
        raise ValueError(nesting_enforcement)
    hp = h_prev.double()
    delta_full = (ru - rv).double()
    m_full = delta_full.T @ delta_full / len(ru)                 # difference moment, full feature coordinates
    proj = hp @ hp.T                                              # P: projector onto H_{k-1}
    m = hp.T @ m_full @ hp                                        # the same moment seen from inside H_{k-1}
    max_sq = float((delta_full @ hp).square().sum(1).max())
    vals, vecs = eig_desc(m)
    selected = select_block_count(vals, gamma_min) if gamma_min is not None else None
    if d_k is None:
        if selected is None:
            raise ValueError("need d_k or gamma_min")
        d_k = selected
    gauge_local = None if gauge_ref is None else hp.T @ gauge_ref.double() @ hp

    if nesting_enforcement == "hard":
        v = hp @ gauge_fix(vecs[:, :d_k], gauge_local)
        v = _qr_keep_orientation(proj @ v)                        # explicit D9 guard: project onto the rung-(k-1) basis, re-orthonormalize
        q = hp @ vecs[:, d_k:]
        eig_report = vals
    elif nesting_enforcement == "soft":
        eye = torch.eye(m_full.shape[0], dtype=m_full.dtype)
        _, vs = eig_desc(m_full - soft_lambda * (eye - proj))
        v = gauge_fix(vs[:, :d_k], None)
        rest = (eye - v @ v.T) @ hp                               # content left after removing V, inside H_{k-1}
        u, _, _ = torch.linalg.svd(rest, full_matrices=False)
        q = u[:, : hp.shape[1] - d_k]
        eig_report = vals
    else:  # none
        vals_n, vs = eig_desc(m_full)
        v = gauge_fix(vs[:, :d_k], None)
        q = vs[:, d_k:]
        eig_report = vals_n
    return RungFit(k=k, d_k=d_k, eigvals=eig_report.float(), gap_ratio=gap_ratio(eig_report, d_k),
                   selected_d=selected, V=v.float(), Q=q.float(), H_prev=h_prev, n_pairs=len(ru), M=m.float(),
                   max_sq_diff=max_sq, nesting_enforcement=nesting_enforcement)


PairsFn = Callable[[int], "tuple[torch.Tensor, torch.Tensor] | None"]


def fit_ladder(pairs_fn: PairsFn, dim: int, d_ks: list[int] | None = None,
               gamma_min: float | None = None, max_rungs: int | None = None,
               gauge_ref: torch.Tensor | None = None, pair_budgets: list[int] | None = None,
               nesting_enforcement: str = "hard", soft_lambda: float = 100.0) -> list[RungFit]:
    """Iterate the engine along its own invariant output (Theorem 5.2).

    pairs_fn(k) returns whitened (ru, rv) for family D_k in full representation coordinates, or
    None when no correspondence family is available (termination relative to available
    correspondences, Remark 5.4). With `pair_budgets` (one entry per rung) it is called as pairs_fn(k, budget[k-1]),
    so each rung can have its own pair budget (decision D9).
    """
    h = torch.eye(dim)
    rungs: list[RungFit] = []
    limit = max_rungs if max_rungs is not None else (len(d_ks) if d_ks is not None else dim)
    for k in range(1, limit + 1):
        if h.shape[1] == 0:
            break
        pairs = pairs_fn(k) if pair_budgets is None else pairs_fn(k, pair_budgets[k - 1])
        if pairs is None:
            break
        fit = fit_rung(*pairs, h_prev=h, k=k,
                       d_k=None if d_ks is None else d_ks[k - 1],
                       gamma_min=gamma_min, gauge_ref=gauge_ref,
                       nesting_enforcement=nesting_enforcement, soft_lambda=soft_lambda)
        rungs.append(fit)
        h = fit.Q
    return rungs
