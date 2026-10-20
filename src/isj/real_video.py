"""Evaluator side for real video: colour tracker for the orange link. Never feeds discovery."""

from __future__ import annotations

import numpy as np


def orange_track(rgb: np.ndarray, min_pixels: int = 3) -> np.ndarray:
    """rgb (T, H, W, 3) uint8 -> (T, 2) centroid (x, y) of orange pixels in image coordinates; gaps interpolated."""
    r, g, b = rgb[..., 0].astype(int), rgb[..., 1].astype(int), rgb[..., 2].astype(int)
    mask = (r > 170) & (r - b > 90) & (r - g > 40) & (g > b)
    out = np.full((len(rgb), 2), np.nan)
    ys, xs = np.mgrid[: rgb.shape[1], : rgb.shape[2]]
    for i, m in enumerate(mask):
        if m.sum() >= min_pixels:
            out[i] = [xs[m].mean(), ys[m].mean()]
    idx = np.arange(len(out))
    ok = ~np.isnan(out[:, 0])
    if ok.sum() >= 2:
        for c in range(2):
            out[:, c] = np.interp(idx, idx[ok], out[ok, c])
    return out


def proxies(track: np.ndarray, fps: float) -> dict:
    """Tracker-derived quantities (partial: one link only, pixel units): speed^2 from central differences, and height (up = positive)."""
    v = np.gradient(track, axis=0) * fps
    return {"speed2": (v ** 2).sum(1), "height": -track[:, 1]}
