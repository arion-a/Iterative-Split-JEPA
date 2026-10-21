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
# than 99% of within-clip consecutive-frame steps. The grouping 'video = clip // k' is accepted if k is the best period among the divisors of the clip
# count, breaks are common on its boundaries (>= 70%) and rare within videos (<= 2%, the threshold alone yields ~1%).
step = np.abs(np.diff(f, axis=1)).mean(2)
thr = float(np.quantile(step, 0.99))
cont = np.array([np.abs(f[i, -1] - f[i + 1, 0]).mean() for i in range(n_clips - 1)])
pix = cont > thr                                                  # a "break" between clip i and i+1; by construction ~1% of within-video joins also exceed the 99th-percentile threshold


def contrast(period):
    """fraction of break flags at joins that sit on a multiple of `period`, minus the fraction elsewhere (physics-free)."""
    on = np.array([(i + 1) % period == 0 for i in range(n_clips - 1)])
    return float(pix[on].mean() - pix[~on].mean())


divisors = [p for p in range(5, 61) if n_clips % p == 0]
scores = {p: contrast(p) for p in divisors}
best = max(scores, key=scores.get)
on_k = np.array([(i + 1) % k == 0 for i in range(n_clips - 1)])
# independent evaluator-side verification with the tracked angles (reported, not used to define the grouping)
def jump(i):
    """largest wrapped jump of either tracked angle between the last tracked frame of clip i and the first of clip i+1."""
    out = []
    for th in (au["theta_1"], au["theta_2"]):
        l, g = th[i][np.isfinite(th[i])], th[i + 1][np.isfinite(th[i + 1])]
        if len(l) and len(g):
            out.append(abs((g[0] - l[-1] + np.pi) % (2 * np.pi) - np.pi))
    return max(out) if out else np.nan
dj = np.array([jump(i) for i in range(n_clips - 1)])
check = {"clips_per_video": k, "threshold": thr, "pixel_break_fraction_on_boundaries": float(pix[on_k].mean()), "pixel_break_fraction_within_videos": float(pix[~on_k].mean()),
         "contrast_by_period": {str(p): round(s, 3) for p, s in scores.items()}, "best_period": int(best),
         "angle_discontinuous_fraction_on_boundaries": float(np.nanmean(dj[on_k] > 0.3)), "angle_discontinuous_fraction_within_videos": float(np.nanmean(dj[~on_k] > 0.3)),
         "adjacent_vs_random_distance": [float(np.median(cont)), float(np.median([np.abs(f[i, -1] - f[(i * 7 + 13) % n_clips, 0]).mean() for i in range(n_clips - 1)]))]}
check["ok"] = bool(best == k and check["pixel_break_fraction_on_boundaries"] >= 0.7 and check["pixel_break_fraction_within_videos"] <= 0.02
                   and check["angle_discontinuous_fraction_on_boundaries"] >= 0.9
                   and check["angle_discontinuous_fraction_on_boundaries"] - check["angle_discontinuous_fraction_within_videos"] >= 0.5)
os.makedirs("data/columbia_full", exist_ok=True)
json.dump(check, open("data/columbia_full/grouping_check.json", "w"), indent=1)
print(check)
assert check["ok"], "grouping rule failed"
# --- video-level sequences
nv = n_clips // k
frames = f.reshape(nv, k * t_clip, d)
def seq(key):
    return au[key].reshape(nv, k * t_clip)
np.save("data/columbia_full/frames.npy", frames)
np.savez("data/columbia_full/audit.npz", total_energy=seq("total_energy"), reject=seq("reject"), theta_1=seq("theta_1"), theta_2=seq("theta_2"))
print("videos", nv, "frames per video", k * t_clip)
