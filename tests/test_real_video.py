import subprocess

import numpy as np

from isj import real_video, real_video_io


def _make_clip(path, t=30, size=64):
    frames = np.full((t, size, size, 3), 200, dtype=np.uint8)
    for i in range(t):
        x = 10 + i
        frames[i, 20:30, x:x + 8] = [255, 110, 20]                       # moving orange block
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size}x{size}", "-r", "30", "-i", "-",
                    "-pix_fmt", "yuv444p", "-crf", "1", path], input=frames.tobytes(), check=True)
    return frames


def test_decode_roundtrip_and_tracker(tmp_path):
    p = str(tmp_path / "c.mp4"); _make_clip(p)
    g = real_video_io.decode(p, (0, 0, 64, 64), 32)
    assert g.shape == (30, 1024) and 0.0 <= g.min() and g.max() <= 1.0
    rgb = real_video_io.decode(p, (0, 0, 64, 64), 64, fmt="rgb")
    tr = real_video.orange_track(rgb)
    assert np.allclose(np.diff(tr[:, 0]), 1.0, atol=0.5)                 # moves one pixel per frame
    sp = real_video.proxies(tr, 30.0)
    assert np.allclose(sp["speed2"][2:-2], 900.0, rtol=0.2)


def test_views_differ_only_by_illumination():
    rng = np.random.default_rng(0)
    f = rng.random((20, 1024)).astype(np.float32)
    v = real_video_io.illumination_views(f, rng)
    d = v[0] - v[1]
    assert np.allclose(d, d[0][None], atol=1e-5)                          # constant over time: purely the additive pattern
    assert not np.allclose(v[0], v[1])
