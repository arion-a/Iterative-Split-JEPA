"""Discovery-side handling of real video: decode, fixed crop, grayscale downsample, additive-illumination views.
No tracker and no ground-truth quantity lives here (see real_video.py for the evaluator side)."""

from __future__ import annotations

import subprocess

import numpy as np

from .video_io import illumination_basis


def decode(path: str, crop: tuple[int, int, int, int], size: int = 32, fmt: str = "gray") -> np.ndarray:
    """crop = (x, y, w, h) in source pixels (a fixed, documented preprocessing choice). Returns (T, size*size) float32 in [0, 1] for gray,
    (T, size, size, 3) uint8 for rgb."""
    x, y, w, h = crop
    ch = 1 if fmt == "gray" else 3
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"crop={w}:{h}:{x}:{y},scale={size}:{size}:flags=area",
           "-f", "rawvideo", "-pix_fmt", "gray" if fmt == "gray" else "rgb24", "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    arr = np.frombuffer(raw, dtype=np.uint8).reshape(-1, size, size, ch)
    return (arr.reshape(len(arr), -1).astype(np.float32) / 255.0) if fmt == "gray" else arr


def illumination_views(frames: np.ndarray, rng: np.random.Generator, amp: float = 0.4, size: int = 32) -> np.ndarray:
    """(T, D) -> (2, T, D): two views of the same clip, each with its own constant additive illumination pattern (the correspondence)."""
    basis = illumination_basis(size)
    return np.stack([frames + (rng.uniform(-amp, amp, 4) @ basis)[None] for _ in range(2)])
