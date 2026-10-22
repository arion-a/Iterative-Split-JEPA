"""Frame-descriptor encoder trained by multi-horizon latent prediction + collapse regulariser (no decoder), plus an optional consistency term
between two renderings of the same frame (LIVE_DATA_PLAN §2) when `aug_weight` > 0.

Descriptor of frame t: [x_t ; x_t - x_{t-1}]. The prediction target is a stop-gradient latent of the same clip at t+h.
Recipe follows the validated synthetic encoder (hinge + covariance penalty); see docs/IMPLEMENTATION_PLAN.md DECIDE 2-3.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn.functional as F

from .encoder import covariance_penalty, mlp, variance_hinge


class ConvEncoder(torch.nn.Module):
    """Small conv encoder over the descriptor [x_t ; x_t - x_{t-1}] viewed as 2 channels of size x size (for size 64: 4 stride-2 convs -> 4x4x64); `channels` = 3 for RGB."""

    def __init__(self, i_dim: int, hidden: int, out: int, channels: int = 1):
        super().__init__()
        self.channels = channels
        self.size = int(round((i_dim / (2 * channels)) ** 0.5))     # descriptor = [x_t (C, S, S) ; x_t - x_{t-1} (C, S, S)], channel-major
        nn = torch.nn
        self.conv = nn.Sequential(nn.Conv2d(2 * channels, 16, 5, 2, 2), nn.GELU(), nn.Conv2d(16, 32, 3, 2, 1), nn.GELU(), nn.Conv2d(32, 64, 3, 2, 1), nn.GELU(),
                                  nn.Conv2d(64, 64, 3, 2, 1), nn.GELU(), nn.Flatten())
        self.head = nn.Sequential(nn.Linear(64 * (self.size // 16) ** 2, hidden), nn.GELU(), nn.Linear(hidden, out))

    def forward(self, x):
        return self.head(self.conv(x.reshape(-1, 2 * self.channels, self.size, self.size)))


def descriptors(frames: np.ndarray) -> np.ndarray:
    """(R, A, T, D) -> (R, A, T-1, 2D)."""
    x = frames[:, :, 1:]
    return np.concatenate([x, x - frames[:, :, :-1]], axis=-1)


class Standardizer:
    def __init__(self, desc_train: np.ndarray):
        flat = desc_train.reshape(-1, desc_train.shape[-1])
        self.mean = flat.mean(0)
        half = flat.shape[1] // 2
        self.scale = np.concatenate([np.full(half, flat[:, :half].std()), np.full(half, flat[:, half:].std() + 1e-6)])

    @classmethod
    def from_frames(cls, frames: np.ndarray) -> "Standardizer":
        """Same statistics as Standardizer(descriptors(frames)), accumulated one release at a time (float64 sums) so no full descriptor array is built."""
        n, s, q = 0, 0.0, 0.0
        s_vec = None
        for i in range(len(frames)):
            d = descriptors(frames[i:i + 1]).reshape(-1, 2 * frames.shape[-1]).astype(np.float64)
            half = d.shape[1] // 2
            n += len(d); s_vec = d.sum(0) if s_vec is None else s_vec + d.sum(0)
            q = q + np.array([(d[:, :half] ** 2).sum(), (d[:, half:] ** 2).sum()])
        half = len(s_vec) // 2
        m1, m2 = s_vec[:half].sum() / (n * half), s_vec[half:].sum() / (n * half)
        obj = cls.__new__(cls)
        obj.mean = (s_vec / n).astype(frames.dtype)
        obj.scale = np.concatenate([np.full(half, np.sqrt(q[0] / (n * half) - m1 ** 2)), np.full(half, np.sqrt(q[1] / (n * half) - m2 ** 2) + 1e-6)])
        return obj

    def __call__(self, desc: np.ndarray) -> np.ndarray:
        out = np.empty(desc.shape, np.float32)                  # chunked over the leading axis: same values, no full-size temporaries
        for i in range(len(desc)):
            out[i] = (desc[i] - self.mean) / self.scale
        return out


def train_encoder(desc_train: np.ndarray, cfg: dict, seed: int, verbose: bool = False):
    """desc_train: standardized (R, A, T', I) float32. Returns the frozen encoder and a short log."""
    torch.manual_seed(seed)
    gen = np.random.default_rng(seed)
    x = torch.from_numpy(desc_train)
    r_n, a_n, t_n, i_dim = x.shape
    hs = list(cfg["horizons"])
    d, hid = cfg["latent_dim"], cfg["hidden"]
    enc = ConvEncoder(i_dim, hid, d, cfg.get("channels", 1)) if cfg.get("arch") == "conv" else mlp(i_dim, hid, d)
    preds = torch.nn.ModuleList([mlp(d, 128, d) for _ in hs])
    opt = torch.optim.AdamW(list(enc.parameters()) + list(preds.parameters()), lr=cfg["lr"])
    steps, bs = cfg["steps"], cfg["batch_size"]
    half = steps // 2
    log = []
    for step in range(steps):
        lr = cfg["lr"] if step < half else cfg["lr"] * (1 + np.cos(np.pi * (step - half) / (steps - half))) / 2
        for g in opt.param_groups:
            g["lr"] = lr
        r = torch.from_numpy(gen.integers(0, r_n, bs)); a = torch.from_numpy(gen.integers(0, a_n, bs))
        t = torch.from_numpy(gen.integers(0, t_n - max(hs), bs))
        z = enc(x[r, a, t])
        l_aug = F.mse_loss(z, enc(x[r, 1 - a, t])) if cfg.get("aug_weight", 0.0) > 0 else torch.zeros(())
        l_pred = sum(F.mse_loss(p(z), enc(x[r, a, t + h]).detach()) for p, h in zip(preds, hs)) / len(hs)
        l_reg = cfg["var_weight"] * variance_hinge(z) + cfg["cov_weight"] * covariance_penalty(z)
        loss = l_pred + l_reg + cfg.get("aug_weight", 0.0) * l_aug
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 1000 == 0 or step == steps - 1:
            rec = {"step": step, "pred": float(l_pred.detach()), "reg": float(l_reg.detach()), "min_std": float(z.detach().std(0).min())}
            log.append(rec)
            if verbose:
                print(rec, flush=True)
    enc.eval()
    for p in enc.parameters():
        p.requires_grad_(False)
    return enc, log


@torch.no_grad()
def encode(enc, desc: np.ndarray, chunk: int = 4000) -> np.ndarray:
    flat = torch.from_numpy(desc.reshape(-1, desc.shape[-1]))
    out = torch.cat([enc(flat[i:i + chunk]) for i in range(0, len(flat), chunk)])
    return out.numpy().reshape(*desc.shape[:-1], -1)
