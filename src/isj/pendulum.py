"""Double-pendulum generator and frame renderer (generator side: physics variables live here and in the audit table only).

Unit masses and lengths, planar, optional viscous damping gamma. State s = (theta1, theta2, omega1, omega2).
Rendering draws the two bobs and rods as Gaussian splats on a small grayscale grid; the nuisance (gain, offset,
sub-pixel shift) is constant within one rendering of a release.
"""

from __future__ import annotations

import numpy as np

from .video_io import illumination_basis

G = 9.81


def deriv(s: np.ndarray, gamma: float = 0.0) -> np.ndarray:
    t1, t2, w1, w2 = s[..., 0], s[..., 1], s[..., 2], s[..., 3]
    d = t1 - t2
    den = 3.0 - np.cos(2 * d)
    a1 = (-G * 3 * np.sin(t1) - G * np.sin(t1 - 2 * t2) - 2 * np.sin(d) * (w2**2 + w1**2 * np.cos(d))) / den
    a2 = (2 * np.sin(d) * (2 * w1**2 + 2 * G * np.cos(t1) + w2**2 * np.cos(d))) / den
    return np.stack([w1, w2, a1 - gamma * w1, a2 - gamma * w2], axis=-1)


def rk4_step(s: np.ndarray, h: float, gamma: float = 0.0) -> np.ndarray:
    k1 = deriv(s, gamma)
    k2 = deriv(s + 0.5 * h * k1, gamma)
    k3 = deriv(s + 0.5 * h * k2, gamma)
    k4 = deriv(s + h * k3, gamma)
    return s + h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate(s0: np.ndarray, n_frames: int, dt_frame: float = 0.05, dt_int: float = 1e-3,
             gamma: float = 0.0) -> np.ndarray:
    """(R, 4) initial states -> (R, n_frames + 1, 4) states sampled every dt_frame."""
    sub = int(round(dt_frame / dt_int))
    h = dt_frame / sub
    out = [s0.astype(np.float64)]
    s = out[0]
    for _ in range(n_frames):
        for _ in range(sub):
            s = rk4_step(s, h, gamma)
        out.append(s)
    return np.stack(out, axis=1)


def energy(s: np.ndarray) -> np.ndarray:
    t1, t2, w1, w2 = s[..., 0], s[..., 1], s[..., 2], s[..., 3]
    kin = 0.5 * w1**2 + 0.5 * (w1**2 + w2**2 + 2 * w1 * w2 * np.cos(t1 - t2))
    pot = -2 * G * np.cos(t1) - G * np.cos(t2)
    return kin + pot


def sample_initial(n: int, rng: np.random.Generator, amp_range=(0.3, np.pi), omega_std: float = 0.3) -> np.ndarray:
    amp = rng.uniform(*amp_range, size=(n, 1))
    theta = amp * rng.uniform(-1, 1, size=(n, 2))
    return np.concatenate([theta, rng.normal(0, omega_std, size=(n, 2))], axis=1)


def sample_nuisance(n: int, rng: np.random.Generator, amp: float = 0.4) -> np.ndarray:
    """(n, 4) coefficients of an additive illumination pattern (brightness, x-gradient, y-gradient, saddle), constant per rendering."""
    return rng.uniform(-amp, amp, size=(n, 4))


def render(states: np.ndarray, nuis: np.ndarray, size: int = 32, scale: float = 7.0, noise: float = 0.01,
           rng: np.random.Generator | None = None, chunk: int = 1000) -> np.ndarray:
    """states (N, 4) with per-row nuisance (N, 4) -> frames (N, size*size) float32 = splats + additive illumination + noise."""
    n = len(states)
    t1, t2 = states[:, 0], states[:, 1]
    b1 = np.stack([np.sin(t1), -np.cos(t1)], 1)
    b2 = b1 + np.stack([np.sin(t2), -np.cos(t2)], 1)
    frac = np.linspace(0.1, 0.9, 9)[None, :, None]
    rod1 = b1[:, None, :] * frac
    rod2 = b1[:, None, :] + (b2 - b1)[:, None, :] * frac
    pts = np.concatenate([b1[:, None], b2[:, None], rod1, rod2], axis=1)       # (n, 20, 2) in world units
    wts = np.array([2.0, 1.5] + [0.35] * 18)[None, :]
    sig = np.array([1.5, 1.5] + [0.9] * 18)[None, :]
    px = size / 2 + scale * pts[..., 0]
    py = size / 2 - scale * pts[..., 1]
    ax = np.arange(size, dtype=np.float32)
    basis = illumination_basis(size)
    out = np.empty((n, size * size), dtype=np.float32)
    for i in range(0, n, chunk):
        sl = slice(i, i + chunk)
        gx = np.exp(-((ax[None, None, :] - px[sl, :, None]) ** 2) / (2 * sig[:, :, None] ** 2))      # (c, P, W)
        gy = np.exp(-((ax[None, None, :] - py[sl, :, None]) ** 2) / (2 * sig[:, :, None] ** 2))      # (c, P, H)
        img = np.einsum("cp,cph,cpw->chw", np.broadcast_to(wts, gx.shape[:2]), gy, gx)
        out[sl] = (img.reshape(len(img), -1) + nuis[sl] @ basis).astype(np.float32)
    if noise > 0:
        r = rng if rng is not None else np.random.default_rng(0)
        out += (noise * r.standard_normal(out.shape)).astype(np.float32)
    return out
