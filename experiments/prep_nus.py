"""Decode the NUS real double-pendulum videos (HF MLDS-NUS/double_pendulum) for the video-level protocol (release = video).
Discovery side: 32x32 gray frames, the first FRAMES frames of every video that has at least that many. Evaluator side (sealed, image-derived, no
state labels exist in this dataset): white-pixel centre of mass, reach, motion. Writes data/nus/{frames.npy, audit.npz, index.json}.
Needs pyarrow (PYTHONPATH=/tmp/claude-0/pa)."""
import glob, io, json, os
from collections import defaultdict

import numpy as np
import pyarrow.parquet as pq
from PIL import Image

FRAMES = 660
PIVOT = (360.0, 350.0)
lo, hi = 40, 680                                                   # drop the frame border and the three edge markers
yy, xx = np.mgrid[lo:hi, lo:hi]
rows = defaultdict(dict)                                           # trajectory -> {frame index: (small, com_y, com_x, reach, area)}
n_total = defaultdict(int)
prev = {}                                                          # last frame of each video (rows are in frame order; checked below)
for path in sorted(glob.glob("data/public/nus_dp/p[0-9].parquet")):
    f = pq.ParquetFile(path)
    for g in range(f.metadata.num_row_groups):
        t = f.read_row_group(g)
        for im, tr in zip(t.column("image").to_pylist(), t.column("trajectory").to_pylist()):
            vid, k = tr.rsplit("_", 1); k = int(k); n_total[vid] += 1
            if k > FRAMES:
                continue
            g8 = Image.open(io.BytesIO(im["bytes"])).convert("L")
            small = np.asarray(g8.resize((32, 32), Image.BOX), np.float32).reshape(-1) / 255.0
            a = np.asarray(g8, np.float32)[lo:hi, lo:hi]
            m = a > 128
            area = float(m.sum())
            cy, cx = (float(yy[m].mean()), float(xx[m].mean())) if area > 0 else (np.nan, np.nan)
            reach = float(np.hypot(xx[m] - PIVOT[0], yy[m] - PIVOT[1]).mean()) if area > 0 else np.nan
            mo = float(np.abs(a - prev[vid]).mean()) if k > 1 and (vid in prev) and (k - 1) in rows[vid] else 0.0
            prev[vid] = a
            rows[vid][k] = (small, cy, cx, reach, area, mo)
    print(path, len(rows), flush=True)
keep = sorted(v for v in rows if n_total[v] >= FRAMES and sorted(rows[v]) == list(range(1, FRAMES + 1)))
print("videos", len(n_total), "kept", len(keep), "min/max length", min(n_total.values()), max(n_total.values()))
frames = np.stack([np.stack([rows[v][k][0] for k in range(1, FRAMES + 1)]) for v in keep])
au = {n: np.array([[rows[v][k][i] for k in range(1, FRAMES + 1)] for v in keep], np.float32) for i, n in ((1, "com_y"), (2, "com_x"), (3, "reach"), (4, "area"))}
motion = np.array([[rows[v][k][5] for k in range(1, FRAMES + 1)] for v in keep], np.float32)
au["height"] = -au["com_y"]                                        # gravitational potential of uniform bars is proportional to the centre-of-mass height
au["motion"] = motion
os.makedirs("data/nus", exist_ok=True)
np.save("data/nus/frames.npy", frames); np.savez("data/nus/audit.npz", **au)
json.dump({"kept": keep, "lengths": {v: n_total[v] for v in keep}, "excluded": sorted(set(n_total) - set(keep))}, open("data/nus/index.json", "w"), indent=1)
print("frames", frames.shape, "audit finite", {k: bool(np.isfinite(v).all()) for k, v in au.items()})
