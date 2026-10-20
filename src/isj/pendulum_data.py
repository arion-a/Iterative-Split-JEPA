"""Build the rendered double-pendulum dataset (generator side) and its sealed audit table.

The discovery side only ever sees `frames.npy` + `meta.json` (via video_io); `audit.npz` is read by evaluation code only.
"""

from __future__ import annotations

import os

import numpy as np

from . import pendulum as pd
from .video_io import save_frames


def build(cfg_world: dict, seed: int, out: str, gamma: float = 0.0) -> dict:
    w = cfg_world
    rng = np.random.default_rng(seed)
    n, t = w["n_releases"], w["n_frames"]
    s0 = pd.sample_initial(n, rng, tuple(w["amp_range"]), w["omega_std"])
    states = pd.simulate(s0, t - 1, w["dt_frame"], w["dt_int"], gamma)                  # (R, T, 4)
    nuis = np.stack([pd.sample_nuisance(n, rng, w["nuisance_amp"]) for _ in range(2)], axis=1)                                          # (R, 2, 4): two renderings per release
    flat = states.reshape(-1, 4)
    arms = []
    for a in range(2):
        nu = np.repeat(nuis[:, a], t, axis=0)
        arms.append(pd.render(flat, nu, w["size"], noise=w["pixel_noise"], rng=rng).reshape(n, t, -1))
    frames = np.stack(arms, axis=1)                                                       # (R, 2, T, D)
    split = np.concatenate([np.full(k, i) for i, k in enumerate(w["splits"])])
    split = split[rng.permutation(n)]
    save_frames(out, frames, split, {"seed": seed})
    np.savez(os.path.join(out, "audit.npz"), theta1=states[..., 0], theta2=states[..., 1], omega1=states[..., 2],
             omega2=states[..., 3], energy=pd.energy(states), nuisance=nuis, gamma=gamma, split=split)
    return {"frames": frames.shape, "out": out}


def load_audit(path: str) -> dict:
    z = np.load(os.path.join(path, "audit.npz"))
    return {k: z[k] for k in z.files}
