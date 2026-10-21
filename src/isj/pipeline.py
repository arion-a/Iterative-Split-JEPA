"""frames -> standardized descriptors -> frozen encoder -> whitened latent; everything fitted on the training frames only."""

from __future__ import annotations

import numpy as np
import torch

from . import video_encoder as ve
from .engine import fit_whitener


class Pipeline:
    def __init__(self, frames_train: np.ndarray, cfg: dict, seed: int):
        self.std = ve.Standardizer.from_frames(frames_train)
        xs = self._standardized(frames_train)
        self.enc, self.log = ve.train_encoder(xs, cfg["encoder"], seed + 77_777)
        z = ve.encode(self.enc, xs); del xs
        d = z.shape[-1]
        self.zmean = z.reshape(-1, d).mean(0)
        self.flat_dir = np.linalg.eigh(np.cov((z.reshape(-1, d) - self.zmean).T))[1][:, -1]
        self.wh = fit_whitener(torch.from_numpy(z.reshape(-1, d)).float(), cfg["encoder"]["zca_eps"])

    def _standardized(self, frames: np.ndarray) -> np.ndarray:
        r, a, t, d = frames.shape
        out = np.empty((r, a, t - 1, 2 * d), np.float32)               # one release at a time: no full-size float64 descriptor array
        for i in range(r):
            out[i] = self.std(ve.descriptors(frames[i:i + 1]))[0]
        return out

    def latent(self, frames: np.ndarray) -> np.ndarray:
        return np.concatenate([ve.encode(self.enc, self.std(ve.descriptors(frames[i:i + 1]))) for i in range(len(frames))])

    def whiten(self, z: np.ndarray) -> np.ndarray:
        d = z.shape[-1]
        return self.wh(torch.from_numpy(z.reshape(-1, d)).float()).numpy().reshape(z.shape)
