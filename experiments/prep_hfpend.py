"""Decode the Hugging Face pendulum videos to 32x32 gray (discovery side) and the label CSVs (evaluator side). Split: provided val -> test (40),
last 20 of the provided train -> val, first 140 -> train. Writes data/hf_pendulum/{frames.npy, audit.npz}."""
import csv, os, subprocess

import numpy as np

root = "data/public/hf_pendulum"
rows = list(csv.DictReader(open(f"{root}/index.csv")))
frames, aud = [], {k: [] for k in ("energy", "theta", "omega", "light_angle")}
split = np.zeros(len(rows), int)
tr_ids = [i for i, r in enumerate(rows) if r["split"] == "train"]
for i, r in enumerate(rows):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{root}/videos/{r['video_id']}.mp4", "-vf", "scale=32:32:flags=area", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         check=True, capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, 1024).astype(np.float32) / 255.0
    assert len(f) == int(r["frames"]) == 72, (r["video_id"], len(f))
    frames.append(f)
    lab = list(csv.DictReader(open(f"{root}/timeseries/{r['video_id']}.csv")))
    assert len(lab) == 72
    for key, col in (("energy", "energy_j_per_kg"), ("theta", "theta_rad"), ("omega", "omega_rad_s"), ("light_angle", "light_angle_deg")):
        aud[key].append([float(x[col]) for x in lab])
    split[i] = 2 if r["split"] == "val" else 0
for j in tr_ids[140:]:
    split[j] = 1
os.makedirs("data/hf_pendulum", exist_ok=True)
np.save("data/hf_pendulum/frames.npy", np.stack(frames))
a = {k: np.array(v) for k, v in aud.items()}
a["kinetic"] = 0.5 * a["omega"] ** 2; a["potential"] = a["energy"] - a["kinetic"]; a["split"] = split
np.savez("data/hf_pendulum/audit.npz", **a)
print("videos", len(rows), "split sizes", [int((split == s).sum()) for s in range(3)], "energy range", float(a["energy"].min()), float(a["energy"].max()))
