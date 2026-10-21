"""Evaluator side of the handshake: reads the sealed simulator table. Nothing here feeds back into discovery."""

from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr

from . import quotient_audit as qa
from .pendulum_data import load_audit


def aligned(path: str, arms: int = 2) -> dict:
    """Audit quantities aligned to descriptor time (first frame dropped) and broadcast over rendering arms: (R, A, T-1, m)."""
    a = load_audit(path)
    def bc(x):
        return np.repeat(x[:, None, 1:, None], arms, axis=1)
    return {"E": bc(a["energy"]), "angles": np.concatenate([bc(a["theta1"]), bc(a["theta2"])], axis=-1),
            "const": np.zeros_like(bc(a["energy"])), "split": a["split"]}


def naming(psi: np.ndarray, e: np.ndarray) -> float:
    """|Spearman| (the sign of a recovered direction is arbitrary), D14."""
    return abs(float(spearmanr(psi.ravel(), e.ravel())[0]))


def references(ev: dict, split: np.ndarray, k: int, delta: float, n_pairs: int, seed: int) -> dict:
    out = {}
    for name in ("E", "angles", "const"):
        q = ev[name]
        out[name] = qa.certificate(q[split == 0], q[split == 1], q[split == 2], k, delta, n_pairs, seed)
    return out


def ceiling_probe(z_white: np.ndarray, e: np.ndarray, split: np.ndarray) -> dict:
    """REPORT-ONLY (D13): linear readout of E from the whitened latent; R^2 on train and held-out test releases."""
    d = z_white.shape[-1]
    def flat(x, m):
        return x[split == m].reshape(-1, x.shape[-1])
    xtr, ytr = flat(z_white, 0), flat(e, 0)
    xa = np.concatenate([xtr, np.ones((len(xtr), 1))], 1)
    w, *_ = np.linalg.lstsq(xa, ytr, rcond=None)
    def r2(m):
        x, y = flat(z_white, m), flat(e, m)
        p = np.concatenate([x, np.ones((len(x), 1))], 1) @ w
        return float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum())
    return {"r2_train": r2(0), "r2_test": r2(2)}


def reach_curve(coords: np.ndarray, split: np.ndarray, horizons=(1, 2, 4, 8, 16, 32), ridge: float = 1e-6) -> dict:
    """Normalised held-out error of a linear K-step predictor of `coords` (R, A, T, m) from the same coordinates."""
    m = coords.shape[-1]
    out = {}
    for h in horizons:
        def pairs(s):
            c = coords[split == s]
            return c[:, :, :-h].reshape(-1, m), c[:, :, h:].reshape(-1, m)
        xtr, ytr = pairs(0)
        xa = np.concatenate([xtr, np.ones((len(xtr), 1))], 1)
        w = np.linalg.solve(xa.T @ xa + ridge * np.eye(m + 1), xa.T @ ytr)
        xte, yte = pairs(2)
        p = np.concatenate([xte, np.ones((len(xte), 1))], 1) @ w
        out[str(h)] = float(((yte - p) ** 2).sum() / ((yte - yte.mean(0)) ** 2).sum())
    return out


def anova_icc(values: np.ndarray, valid: np.ndarray) -> float:
    """One-way ANOVA ICC(1) of a (groups, frames) table with a validity mask (unbalanced groups): share of variance that is between groups.
    Evaluator side: used for the reliability (label-noise ceiling) of tracked energy."""
    g = [v[m] for v, m in zip(values, valid) if m.sum() > 1]
    n_i = np.array([len(x) for x in g], float); n = n_i.sum(); k = len(g)
    grand = np.concatenate(g).mean()
    msb = sum(len(x) * (x.mean() - grand) ** 2 for x in g) / (k - 1)
    msw = sum(((x - x.mean()) ** 2).sum() for x in g) / (n - k)
    n0 = (n - (n_i ** 2).sum() / n) / (k - 1)
    return float((msb - msw) / (msb + (n0 - 1) * msw))


def local_amplitude(theta1: np.ndarray, theta2: np.ndarray, half: int = 30, min_valid: int = 20) -> np.ndarray:
    """Local swing amplitude per frame from the tracked angles: sqrt of the summed variances of (sin t1, cos t1, sin t2, cos t2) over a centred
    window of +-`half` frames (valid samples only). Inputs (videos, frames); NaN where fewer than `min_valid` samples are valid. Evaluator side."""
    feats = np.stack([np.sin(theta1), np.cos(theta1), np.sin(theta2), np.cos(theta2)], axis=-1)        # (V, T, 4), NaN where tracking failed
    v, t, _ = feats.shape
    out = np.full((v, t), np.nan)
    for i in range(t):
        w = feats[:, max(0, i - half): i + half + 1]
        ok = np.isfinite(w).all(-1)
        for j in range(v):
            if ok[j].sum() >= min_valid:
                out[j, i] = np.sqrt(w[j][ok[j]].var(0).sum())
    return out


def partial_spearman(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    """Spearman correlation of x and y after removing the (rank) linear dependence of each on z."""
    from scipy.stats import rankdata
    rx, ry, rz = (rankdata(a) for a in (x, y, z))
    def resid(a, b):
        b1 = np.stack([b, np.ones_like(b)], 1)
        return a - b1 @ np.linalg.lstsq(b1, a, rcond=None)[0]
    return float(np.corrcoef(resid(rx, rz), resid(ry, rz))[0, 1])
