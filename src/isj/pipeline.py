"""frames -> standardized descriptors -> frozen encoder -> whitened latent; everything fitted on the training frames only."""

from __future__ import annotations

import numpy as np
import torch

from . import video_encoder as ve
from .engine import fit_whitener


class Pipeline:
    def __init__(self, frames_train: np.ndarray, cfg: dict, seed: int):
        desc = ve.descriptors(frames_train)
        self.std = ve.Standardizer(desc)
        self.enc, self.log = ve.train_encoder(self.std(desc), cfg["encoder"], seed + 77_777)
        z = ve.encode(self.enc, self.std(desc))
        d = z.shape[-1]
        self.zmean = z.reshape(-1, d).mean(0)
        self.flat_dir = np.linalg.eigh(np.cov((z.reshape(-1, d) - self.zmean).T))[1][:, -1]
        self.wh = fit_whitener(torch.from_numpy(z.reshape(-1, d)).float(), cfg["encoder"]["zca_eps"])

    def latent(self, frames: np.ndarray) -> np.ndarray:
        return ve.encode(self.enc, self.std(ve.descriptors(frames)))

    def whiten(self, z: np.ndarray) -> np.ndarray:
        d = z.shape[-1]
        return self.wh(torch.from_numpy(z.reshape(-1, d)).float()).numpy().reshape(z.shape)
