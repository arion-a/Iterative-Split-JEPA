"""Certificate of a candidate coordinate q over ordered sequences (UP1 of MATHEMATICAL_PLAN): violation rate V with a
validation-calibrated tolerance, between-release variance share (non-degeneracy, D15), Lipschitz constant of a linear
latent transition (D16) and K-step rollout error. q arrays are (R, A, T, m): release, rendering arm, time, coordinate.
"""

from __future__ import annotations

import numpy as np


def standardize(q_fit: np.ndarray, *others: np.ndarray):
    flat = q_fit.reshape(-1, q_fit.shape[-1])
    mu, sd = flat.mean(0), flat.std(0) + 1e-12
    return tuple((x - mu) / sd for x in (q_fit, *others))


def icc(q: np.ndarray) -> float:
    """Share of the (1-D) coordinate's variance that is between releases. 0 for a constant."""
    v = q[..., 0]
    tot = v.var()
    if tot < 1e-18:
        return 0.0
    return float(v.mean(axis=(1, 2)).var() / tot)


def drift_q95(q: np.ndarray, k: int) -> float:
    d = np.linalg.norm(q[:, :, k:] - q[:, :, :-k], axis=-1)
    return float(np.quantile(d, 0.95))


def violation_rate(q: np.ndarray, k: int, delta: float, eps: float, n_pairs: int, seed: int = 0, pool: int = 400_000):
    """Cross-release matched pairs |q_i - q_j| <= delta whose K-step successors differ by more than eps."""
    rng = np.random.default_rng(seed)
    r, a, t, _ = q.shape
    r1, r2 = rng.integers(0, r, pool), rng.integers(0, r, pool)
    keep = r1 != r2
    r1, r2 = r1[keep], r2[keep]
    t1, t2 = rng.integers(0, t - k, len(r1)), rng.integers(0, t - k, len(r1))
    q1, q2 = q[r1, 0, t1], q[r2, 0, t2]
    ok = np.linalg.norm(q1 - q2, axis=-1) <= delta
    idx = np.flatnonzero(ok)[:n_pairs]
    if len(idx) == 0:
        return float("nan"), 0
    s1, s2 = q[r1[idx], 0, t1[idx] + k], q[r2[idx], 0, t2[idx] + k]
    return float((np.linalg.norm(s1 - s2, axis=-1) > eps).mean()), len(idx)


def fit_transition(q_train: np.ndarray):
    """Linear F-hat with intercept from one-step pairs; returns (A, b) with q' = A q + b (row convention q' = q @ A.T + b)."""
    m = q_train.shape[-1]
    x, y = q_train[:, :, :-1].reshape(-1, m), q_train[:, :, 1:].reshape(-1, m)
    xa = np.concatenate([x, np.ones((len(x), 1))], 1)
    sol, *_ = np.linalg.lstsq(xa, y, rcond=None)
    return sol[:m].T, sol[m]


def lipschitz(a: np.ndarray) -> float:
    return float(np.linalg.norm(a, 2))


def rollout_nmse(q_test: np.ndarray, a: np.ndarray, b: np.ndarray, k: int) -> float:
    """RMSE of K-step rollout of F-hat over the std of the coordinate (the 'e_norm' of the plan)."""
    m = q_test.shape[-1]
    x = q_test[:, :, :-k].reshape(-1, m)
    y = q_test[:, :, k:].reshape(-1, m)
    pred = x
    for _ in range(k):
        pred = pred @ a.T + b
    sd = np.sqrt(q_test.reshape(-1, m).var(0).sum())
    return float(np.sqrt(((pred - y) ** 2).sum(1).mean()) / sd) if sd > 1e-12 else float("nan")


def certificate(q_fit: np.ndarray, q_val: np.ndarray, q_test: np.ndarray, k: int = 8, delta: float = 0.1,
                n_pairs: int = 200, seed: int = 0, eps: float | None = None) -> dict:
    """Standardize on the fitting releases; calibrate eps on validation drift (triangle rule, DECIDE 7) unless `eps` is given
    (e.g. from a measured per-step drift for real video); evaluate everything on the held-out test releases."""
    q_fit, q_val, q_test = standardize(q_fit, q_val, q_test)
    drift = drift_q95(q_val, k)
    tol = delta + 2 * drift if eps is None else eps
    v, n = violation_rate(q_test, k, delta, tol, n_pairs, seed)
    a, b = fit_transition(q_fit)
    return {"V": v, "n_pairs_found": n, "eps": tol, "drift_q95_val": drift, "icc": icc(q_test),
            "L": lipschitz(a), "rollout_nmse": rollout_nmse(q_test, a, b, k)}
