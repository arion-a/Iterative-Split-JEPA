"""Sequential ladder over correspondence families: rung 1 pairs two renderings of the same frame (nuisance split),
rung k >= 2 pairs frames (t, t + tau_k) of one clip (temporal split) inside the previous rung's invariant content (D17).
Block size per rung = largest gap ratio among cuts whose top eigenvalue exceeds the S1 level (DECIDE 4, amended 13; c(n) is reported only); S1 = the family agrees with itself to within
`s1_chance_fraction` of an unmatched pair on every remaining direction (DECIDE 5, amended 11); S2 = best gap ratio < gamma_min.
Everything here reads whitened latents only.
"""

from __future__ import annotations

import math

import numpy as np
import torch

from . import engine


def aug_pairs(z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """z (R, A, T, d): the two renderings of the same frame."""
    d = z.shape[-1]
    return z[:, 0].reshape(-1, d), z[:, 1].reshape(-1, d)


def lag_pairs(z: np.ndarray, tau: int, shuffle: bool = False, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    d = z.shape[-1]
    ru, rv = z[:, :, :-tau].reshape(-1, d), z[:, :, tau:].reshape(-1, d)
    if shuffle:
        rv = rv[np.random.default_rng(seed).permutation(len(rv))]
    return ru, rv


def noise_floor(delta: torch.Tensor, quantile: float | None, conf: float = 0.01) -> tuple[float, float]:
    """c(n) = B^2 sqrt(2 log(1/conf)/n); B^2 = max squared pair-difference norm (monograph §10, as in the rank-completeness monitor),
    or its `quantile` when given. Returns (floor, B^2)."""
    sq = delta.square().sum(1)
    b2 = float(sq.max()) if quantile is None else float(torch.quantile(sq, quantile))
    return b2 * math.sqrt(2 * math.log(1 / conf) / len(delta)), b2


def choose_block(vals: torch.Tensor, floor: float, gamma_min: float) -> tuple[int, float, int]:
    """(d, ratio, n_above). Candidate cuts are the d whose top eigenvalue exceeds `floor`; d = 0 when none does or the best ratio is below gamma_min."""
    n_above = int((vals > floor).sum())
    if n_above == 0:
        return 0, 0.0, 0
    top = min(n_above, len(vals) - 1)
    if top == 0:
        return 0, 0.0, n_above
    ratios = vals[:top] / vals[1:top + 1].clamp_min(1e-12)
    j = int(ratios.argmax())
    return (j + 1 if float(ratios[j]) >= gamma_min else 0), float(ratios[j]), n_above


def run_ladder(z_white: np.ndarray, lags: list[int], gamma_min: float = 2.0, b2_quantile: float | None = None,
               shuffle_temporal: bool = False, seed: int = 0, s1_chance_fraction: float = 0.05, use_aug: bool = True) -> dict:
    """z_white (R, A, T, d) whitened latents of the fitting releases. Families are tried in order (aug, then each lag).
    A family that exposes no variation (S1) is skipped; the ladder ends by S1 only when the last family is exhausted, by S2 when a
    family has variation but no clean cut (STOP_CRITERIA S1/S2). Returns rung records, the invariant core and the stop reason."""
    d = z_white.shape[-1]
    h = torch.eye(d)
    rungs, stop = [], "no_family"
    families = (["aug"] if use_aug else []) + [f"lag{l}" for l in lags]
    for idx, family in enumerate(families, start=1):
        if h.shape[1] == 0:
            stop = "exhausted"
            break
        ru, rv = aug_pairs(z_white) if family == "aug" else lag_pairs(z_white, int(family[3:]), shuffle_temporal, seed)
        ru, rv = torch.from_numpy(ru), torch.from_numpy(rv)
        delta = (ru - rv).double() @ h.double()
        vals, _ = engine.eig_desc(delta.T @ delta / len(delta))
        floor, b2 = noise_floor(delta, b2_quantile)
        chance = 2.0                                       # whitened unit-variance coordinates: an unmatched pair differs by 2 per dimension
        s1 = float(vals[0]) <= s1_chance_fraction * chance
        dk, ratio, n_above = (0, 0.0, 0) if s1 else choose_block(vals, s1_chance_fraction * chance, gamma_min)
        rec = {"k": idx, "family": family, "eigvals": [float(v) for v in vals], "floor": floor, "b2": b2,
               "n_above_floor": n_above, "best_ratio": ratio, "d_k": dk, "content_dim": int(h.shape[1]),
               "lambda_max_over_chance": float(vals[0]) / chance}
        if dk == 0:
            rec["stop"] = "S1" if s1 else "S2"
            rungs.append(rec)
            stop = rec["stop"]
            if s1:
                continue                                   # nothing varies under this family: try the next one
            break
        fit = engine.fit_rung(ru, rv, h, idx, d_k=dk)
        rec["gap_ratio"] = fit.gap_ratio
        rec["V"] = fit.V.numpy()
        rec["Q"] = fit.Q.numpy()
        rungs.append(rec)
        h = fit.Q
        stop = "split"
    return {"rungs": rungs, "core": h.numpy(), "stop": stop}


def fit_psi(z_white: np.ndarray, core: np.ndarray) -> dict:
    """Max-ICC direction in the core: generalised eigenproblem between-release vs total covariance. psi is standardized on the fit set."""
    r, a, t, d = z_white.shape
    c = z_white.reshape(-1, d) @ core                                  # (N, m)
    g = np.repeat(np.arange(r), a * t)
    total = np.cov(c.T, ddof=0).reshape(c.shape[1], c.shape[1])
    means = np.stack([c[g == i].mean(0) for i in range(r)])
    between = np.cov(means.T, ddof=0).reshape(c.shape[1], c.shape[1])
    ev, evec = np.linalg.eigh(total)
    inv_half = evec @ np.diag(1 / np.sqrt(np.maximum(ev, 1e-12))) @ evec.T
    lam, u = np.linalg.eigh(inv_half @ between @ inv_half)
    w = inv_half @ u[:, -1]
    proj = c @ w
    return {"core": core, "w": w, "mean": float(proj.mean()), "std": float(proj.std()), "icc_fit": float(lam[-1])}


def apply_psi(z_white: np.ndarray, psi: dict) -> np.ndarray:
    """(R, A, T, d) -> (R, A, T, 1) standardized coordinate."""
    return (((z_white @ psi["core"]) @ psi["w"] - psi["mean"]) / psi["std"])[..., None]
