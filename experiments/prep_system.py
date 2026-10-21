"""Prep a Columbia system (single_pendulum / elastic_pendulum): decode clips to 32x32 gray, load phys_vars with the allowlist unpickler, recover the video grouping by the
contrast test over the divisors of the clip count (no preset period), write data/<name>_full/{frames.npy, audit.npz, grouping_check.json}."""
import io, json, os, sys, zipfile

import numpy as np
import yaml
from PIL import Image

from isj import safe_npy

name = sys.argv[1]
crit = yaml.safe_load(open("configs/gaps.yaml"))["criteria"]["systems"]
Z = zipfile.ZipFile(f"data/public/columbia_other/{name}.zip")
ph = safe_npy.load_object_npy(Z.read(f"{name}/phys_vars.npy"))
names = [n for n in Z.namelist() if n.endswith(".png")]
n_clips = 1 + max(int(n.split("/")[1]) for n in names)
frames = np.zeros((n_clips, 60, 1024), np.float32)
for n in names:
    c, f = int(n.split("/")[1]), int(n.split("/")[2][:-4])
    im = np.asarray(Image.open(io.BytesIO(Z.read(n))).convert("RGB"), np.float32) / 255.0
    frames[c, f] = im.mean(2).reshape(32, 4, 32, 4).mean((1, 3)).reshape(-1)
step = np.abs(np.diff(frames, axis=1)).mean(2)
thr = float(np.quantile(step, 0.99))
cont = np.array([np.abs(frames[i, -1] - frames[i + 1, 0]).mean() for i in range(n_clips - 1)])
pix = cont > thr
def contrast(p):
    on = np.array([(i + 1) % p == 0 for i in range(n_clips - 1)])
    return float(pix[on].mean() - pix[~on].mean())
scores = {p: contrast(p) for p in range(5, 61) if n_clips % p == 0}
k = max(scores, key=scores.get)
on = np.array([(i + 1) % k == 0 for i in range(n_clips - 1)])
check = {"system": name, "n_clips": n_clips, "best_period": int(k), "contrast_by_period": {str(p): round(s, 3) for p, s in scores.items()},
         "pixel_break_fraction_on_boundaries": float(pix[on].mean()), "pixel_break_fraction_within_videos": float(pix[~on].mean()),
         "adjacent_vs_random_distance": [float(np.median(cont)), float(np.median([np.abs(frames[i, -1] - frames[(i * 7 + 13) % n_clips, 0]).mean() for i in range(n_clips - 1)]))]}
check["ok"] = bool(scores[k] >= crit["grouping_min_contrast"] and check["pixel_break_fraction_within_videos"] <= 0.02)
check["fallback"] = None
if not check["ok"]:
    # registered fallback (EVIDENCE G1-G3 amendment): clips are not in temporal order, so videos cannot be recovered; release = clip, 60 frames each
    # (as in C1), contiguous-block split; S1 stays "not met"; the shared-video leakage risk is stated.
    check["fallback"] = "release = clip"; k = 1
out = f"data/{name}_full"; os.makedirs(out, exist_ok=True)
json.dump(check, open(f"{out}/grouping_check.json", "w"), indent=1); print(check)
nv = n_clips // k
np.save(f"{out}/frames.npy", frames.reshape(nv, k * 60, 1024))
np.savez(f"{out}/audit.npz", **{key.replace(" ", "_"): np.asarray(v).reshape(nv, k * 60) for key, v in ph.items()})
print("videos", nv, "frames per video", k * 60, "keys", list(ph))
