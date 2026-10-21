"""C2 data prep: group the 1100 Columbia clips into 100 videos of 11 consecutive clips, verify the grouping rule against pixel continuity,
build video-level sequences (discovery side) and the aligned evaluator table. Reads data/columbia/{frames.npy,audit.npz} (made by prep_columbia.py).
Writes data/columbia_full/{frames.npy (100, 660, 1024), audit.npz, grouping_check.json}."""
import json
import os

import numpy as np
import yaml

cfg = yaml.safe_load(open("configs/columbia_full.yaml"))
k = cfg["grouping"]["clips_per_video"]
f = np.load("data/columbia/frames.npy"); au = np.load("data/columbia/audit.npz")
n_clips, t_clip, d = f.shape
assert n_clips % k == 0, n_clips
# --- grouping rule check (physics-free): a pixel-continuity break is where the last frame of clip i is farther from the first frame of clip i+1
# than 99% of within-clip consecutive-frame steps; every such break must be a multiple-of-k clip boundary.
step = np.abs(np.diff(f, axis=1)).mean(2)
thr = float(np.quantile(step, 0.99))
cont = np.array([np.abs(f[i, -1] - f[i + 1, 0]).mean() for i in range(n_clips - 1)])
breaks = np.flatnonzero(cont > thr)                              # break between clip i and i+1
on_boundary = [(int(i) + 1) % k == 0 for i in breaks]
check = {"clips_per_video": k, "n_breaks": int(len(breaks)), "fraction_on_k_boundary": float(np.mean(on_boundary)) if len(breaks) else 1.0,
         "threshold": thr, "adjacent_vs_random_distance": [float(np.median(cont)), float(np.median([np.abs(f[i, -1] - f[(i * 7 + 13) % n_clips, 0]).mean() for i in range(n_clips - 1)]))]}
check["ok"] = check["fraction_on_k_boundary"] >= 0.98
os.makedirs("data/columbia_full", exist_ok=True)
json.dump(check, open("data/columbia_full/grouping_check.json", "w"), indent=1)
print(check)
assert check["ok"], "grouping rule failed: breaks off the multiple-of-k boundaries"
# --- video-level sequences
nv = n_clips // k
frames = f.reshape(nv, k * t_clip, d)
def seq(key):
    return au[key].reshape(nv, k * t_clip)
np.save("data/columbia_full/frames.npy", frames)
np.savez("data/columbia_full/audit.npz", total_energy=seq("total_energy"), reject=seq("reject"), theta_1=seq("theta_1"), theta_2=seq("theta_2"))
print("videos", nv, "frames per video", k * t_clip)
