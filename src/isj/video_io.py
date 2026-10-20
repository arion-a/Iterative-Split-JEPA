"""Discovery-side frame storage: ordered frames and a release-level split. Nothing else crosses this boundary."""

from __future__ import annotations

import json
import os

import numpy as np


def save_frames(path: str, frames: np.ndarray, split: np.ndarray, extra: dict | None = None) -> None:
    """frames (R, A, T, D) float32: release, rendering arm, time, pixels. split (R,) in {0 train, 1 val, 2 test}."""
    os.makedirs(path, exist_ok=True)
    np.save(os.path.join(path, "frames.npy"), frames)
    meta = {"shape": list(frames.shape), "split": [int(s) for s in split], **(extra or {})}
    with open(os.path.join(path, "meta.json"), "w") as f:
        json.dump(meta, f)


def load_frames(path: str) -> tuple[np.ndarray, np.ndarray]:
    frames = np.load(os.path.join(path, "frames.npy"))
    with open(os.path.join(path, "meta.json")) as f:
        meta = json.load(f)
    return frames, np.asarray(meta["split"])


def illumination_basis(size: int) -> np.ndarray:
    """(4, size*size): 1, x, y, x*y on [-1, 1]^2 (additive illumination patterns)."""
    ax = np.linspace(-1, 1, size, dtype=np.float32)
    yy, xx = np.meshgrid(ax, ax, indexing="ij")
    return np.stack([np.ones_like(xx), xx, yy, xx * yy]).reshape(4, -1)
