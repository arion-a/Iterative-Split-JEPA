"""E74: pack the images the borrowed networks will embed: the probe set and the first N pairs of each rung of the E62 data (default N = 3000).
    python make_e74_images.py [N] -> data/e62/e74_images.npz"""
import sys, numpy as np
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000; out = {"probe": np.load("data/e62/probe.npz")["x"]}
for k in range(1, 9):
    d = np.load(f"data/e62/pairs_k{k}.npz"); out[f"u{k}"], out[f"v{k}"] = d["u"][:N], d["v"][:N]
np.savez("data/e62/e74_images.npz", **out); print({k: v.shape for k, v in out.items()})
