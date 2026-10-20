"""Columbia double-pendulum prep: decode the 1100 clips to 32x32 gray (discovery side), load phys_vars safely (evaluator side) and verify that clip id i
matches phys_vars row i by correlating an image feature with a tracked angle. Writes data/columbia/{frames.npy,audit.npz,mapping_check.json}."""
import io, json, os, re, zipfile

import numpy as np
from PIL import Image

from isj import safe_npy

Z = zipfile.ZipFile("data/public/columbia/double_pendulum.zip")
raw = Z.read("double_pendulum/phys_vars.npy")
phys = safe_npy.load_object_npy(raw)
names = [n for n in Z.namelist() if n.endswith(".png")]
ids = sorted({int(n.split("/")[1]) for n in names})
assert ids == list(range(1100)), ids[:5]
frames = np.zeros((1100, 60, 1024), np.float32)
blue = np.zeros((1100, 60, 2), np.float32)                      # evaluator-side image feature for the mapping check
for n in names:
    c, f = int(n.split("/")[1]), int(n.split("/")[2][:-4])
    im = np.asarray(Image.open(io.BytesIO(Z.read(n))).convert("RGB"), np.float32) / 255.0
    g = im.mean(2)
    frames[c, f] = g.reshape(32, 4, 32, 4).mean((1, 3)).reshape(-1)
    m = (im[..., 2] > 0.55) & (im[..., 0] < 0.35)
    if m.sum() > 3:
        ys, xs = np.nonzero(m); blue[c, f] = [xs.mean() / 128 - 0.5, ys.mean() / 128 - 0.5]
    else:
        blue[c, f] = np.nan
os.makedirs("data/columbia", exist_ok=True)
np.save("data/columbia/frames.npy", frames)
keys = ["total energy", "kinetic energy", "potential energy", "theta_1", "theta_2", "vel_theta_1", "vel_theta_2", "reject"]
np.savez("data/columbia/audit.npz", **{k.replace(" ", "_"): phys[k] for k in keys})


def best_corr(rows):
    """max |corr| between the blue-arm centroid and sin/cos of either tracked angle, using phys row = rows[clip]."""
    ok = np.isfinite(blue[..., 0]) & ~phys["reject"][rows] & np.isfinite(phys["theta_2"][rows])
    out = 0.0
    for th in ("theta_1", "theta_2"):
        for fn in (np.sin, np.cos):
            for ax in (0, 1):
                a, b = blue[..., ax][ok], fn(phys[th][rows])[ok]
                out = max(out, abs(float(np.corrcoef(a, b)[0, 1])))
    return out


right = best_corr(np.arange(1100))
shifted = [best_corr(np.roll(np.arange(1100), k)) for k in (1, 7, 100, 551)]
res = {"corr_identity_mapping": right, "corr_shifted_mappings": shifted, "valid_energy_fraction": float(np.mean(np.isfinite(phys["total energy"]) & ~phys["reject"]))}
json.dump(res, open("data/columbia/mapping_check.json", "w"), indent=1); print(res)
