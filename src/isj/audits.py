"""Measurements against ground truth and the per-rung audits (monograph §8.1, §10)."""

from __future__ import annotations

import math

import torch

from .engine import RungFit


# ---------------------------------------------------------------- subspaces
def orth(a: torch.Tensor) -> torch.Tensor:
    q, _ = torch.linalg.qr(a.double())
    return q


def principal_angles_deg(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Canonical angles (degrees, ascending cosines -> descending angles) between col-spaces."""
    qa, qb = orth(a), orth(b)
    s = torch.linalg.svdvals(qa.T @ qb).clamp(0.0, 1.0)
    return torch.rad2deg(torch.acos(s))


def max_angle_deg(a: torch.Tensor, b: torch.Tensor) -> float:
    return float(principal_angles_deg(a, b).max())


def capture(basis: torch.Tensor, target: torch.Tensor) -> float:
    """Fraction of `basis` energy lying in span(target): ||target^T basis||_F^2 / dim(basis)."""
    q = orth(target)
    b = orth(basis)
    return float((q.T @ b).square().sum() / b.shape[1])


# ---------------------------------------------------------------- regression probes
def _with_intercept(x: torch.Tensor) -> torch.Tensor:
    return torch.cat([x, torch.ones(len(x), 1, dtype=x.dtype)], dim=1)


def ridge_fit(x: torch.Tensor, y: torch.Tensor, ridge: float = 1e-6) -> torch.Tensor:
    xa = _with_intercept(x.double())
    reg = ridge * len(xa) * torch.eye(xa.shape[1], dtype=xa.dtype)
    reg[-1, -1] = 0
    return torch.linalg.solve(xa.T @ xa + reg, xa.T @ y.double())


def r2(w: torch.Tensor, x: torch.Tensor, y: torch.Tensor) -> float:
    pred = _with_intercept(x.double()) @ w
    y = y.double()
    return float(1 - (y - pred).square().sum() / (y - y.mean(0)).square().sum())


def linear_r2(x_tr, y_tr, x_te, y_te, ridge: float = 1e-6) -> float:
    return r2(ridge_fit(x_tr, y_tr, ridge), x_te, y_te)


# ---------------------------------------------------------------- permutation tests
def holm(pvals: list[float], alpha: float) -> list[bool]:
    """Holm step-down: True where the null is rejected."""
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    reject = [False] * len(pvals)
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (len(pvals) - rank):
            reject[i] = True
        else:
            break
    return reject


def leakage_test(z_src_tr, y_tr, z_src_te, y_te, n_perm: int = 1000, ridge: float = 1e-6,
                 seed: int = 0) -> dict:
    """L_{j->k} = held-out R^2(z_j -> g_k) with a permutation null (monograph §10).

    Null: the test-set pairing between z_j and g_k is shuffled.
    """
    w = ridge_fit(z_src_tr, y_tr, ridge)
    obs = r2(w, z_src_te, y_te)
    g = torch.Generator().manual_seed(seed)
    n = len(z_src_te)
    pred = _with_intercept(z_src_te.double()) @ w
    y = y_te.double()
    sst = (y - y.mean(0)).square().sum()
    null = []
    for _ in range(n_perm):
        yp = y[torch.randperm(n, generator=g)]
        null.append(float(1 - (yp - pred).square().sum() / sst))
    p = (1 + sum(v >= obs for v in null)) / (1 + n_perm)
    return {"r2": obs, "p": p, "null_max": max(null), "null_mean": sum(null) / len(null)}


def leakage_matrix(blocks_est: dict[str, tuple[torch.Tensor, torch.Tensor]],
                   blocks_true: dict[str, tuple[torch.Tensor, torch.Tensor]],
                   alpha: float = 0.01, n_perm: int = 1000, seed: int = 0) -> dict:
    """Full R^2(true_j -> est_k) matrix with Holm-corrected permutation tests on off-diagonals.

    Each dict maps a name to (train, test) arrays. Diagonal entries (matching names) are the
    own-block recovery and are reported but not tested.
    """
    out, tests, keys = {}, [], []
    for kn, (e_tr, e_te) in blocks_est.items():
        for jn, (t_tr, t_te) in blocks_true.items():
            res = leakage_test(t_tr, e_tr, t_te, e_te, n_perm=n_perm, seed=seed)
            out[f"{jn}->{kn}"] = res
            if jn != kn:
                keys.append(f"{jn}->{kn}")
                tests.append(res["p"])
    rej = holm(tests, alpha) if tests else []
    for key, r in zip(keys, rej):
        out[key]["significant"] = bool(r)
    return {"entries": out, "any_significant": any(rej), "alpha": alpha}


# ---------------------------------------------------------------- rung-acceptance criteria
def gaussian_entropy_bits(cov: torch.Tensor) -> float:
    """H = 0.5 log2((2 pi e)^d det Sigma)."""
    d = cov.shape[0]
    sign, logdet = torch.linalg.slogdet(cov.double())
    return float(0.5 * (d * math.log2(2 * math.pi * math.e) + logdet / math.log(2)))


def compression_ok(content_prev: torch.Tensor, content_new: torch.Tensor) -> tuple[bool, float, float]:
    """(b): strictly fewer bits than the rung below (Gaussian entropy of the content)."""
    def bits(c):
        c = c.double() - c.double().mean(0)
        cov = c.T @ c / (len(c) - 1) if c.shape[1] else torch.zeros(0, 0)
        return gaussian_entropy_bits(cov) if c.shape[1] else 0.0
    b_prev, b_new = bits(content_prev), bits(content_new)
    return b_new < b_prev, b_prev, b_new


def predictive_loss(r_t: torch.Tensor, r_t1: torch.Tensor, ridge: float = 1e-6) -> float:
    """Equal-capacity linear predictor loss E||F r_t - r_{t+1}||^2 (held-in; use held-out splits)."""
    w = ridge_fit(r_t, r_t1, ridge)
    pred = _with_intercept(r_t.double()) @ w
    return float((pred - r_t1.double()).square().sum(1).mean())


def sufficiency(rt_prev, rt1_prev, rt_new, rt1_new, delta_s: float = 0.05) -> tuple[bool, float]:
    """(c): rho_k = L_pred(H_k)/L_pred(H_{k-1}) <= 1 + delta_s."""
    rho = predictive_loss(rt_new, rt1_new) / predictive_loss(rt_prev, rt1_prev)
    return rho <= 1 + delta_s, rho


def nesting_angle_deg(prev: RungFit | None, fit: RungFit) -> float:
    """(d), audit side: how far the new variant directions lie outside H_{k-1}.

    Holds by construction (V ⊂ H_{k-1}); the audit value should be ~0 up to float error.
    """
    if prev is None:
        return 0.0
    resid = fit.V - orth(prev.Q) @ (orth(prev.Q).T @ fit.V)
    return float(torch.rad2deg(torch.asin(resid.norm(dim=0).clamp(max=1.0).max())))


def rank_deficient(m: torch.Tensor, n: int, bound: float, delta: float = 0.01) -> bool:
    """Termination test (§10): lambda_min <= B^2 sqrt(2 log(1/delta)/n)."""
    lam_min = float(torch.linalg.eigvalsh(m.double()).min())
    return lam_min <= bound**2 * math.sqrt(2 * math.log(1 / delta) / n)

