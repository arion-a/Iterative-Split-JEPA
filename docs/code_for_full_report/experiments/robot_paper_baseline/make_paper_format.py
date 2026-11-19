"""Convert our robot groups (data/robot/<Task>/group_*.npz) to the layout the SplitJEPA robot code reads.
    python make_paper_format.py TASK [SRC_ROOT] [OUT_ROOT]   # TASK = PickCube or PushCube; reads SRC_ROOT/TASK (default data/robot), writes OUT_ROOT/TASK-v1_hshared100/ (default data)
Per trajectory: image_base, image_side, action (8-d). Our files store no actions, only a 9-d state (end-effector xyz, cube xyz, goal xyz), so the action is a stand-in:
the change of the end-effector position between consecutive frames (3 numbers) padded with 5 zeros to the 8 the code expects; the last frame repeats the previous action.
Split: the same 6 train / 2 validation trajectories per group as experiments/robot/run_stage_c.py (split seed 0).
Pairs: viewpoint = (episode, t) base vs side camera; cross_traj = same group, same frame index (progress-aligned), two different trajectories of the same split."""
import glob, json, os, sys, itertools
import numpy as np, torch, h5py
task = sys.argv[1]; src = f"{sys.argv[2] if len(sys.argv) > 2 else 'data/robot'}/{task}"; root = f"{sys.argv[3] if len(sys.argv) > 3 else 'data'}/{task}-v1_hshared100"; os.makedirs(f"{root}/episodes", exist_ok=True)
files = sorted(glob.glob(f"{src}/group_*.npz")); G = len(files); T = 8
g = torch.Generator().manual_seed(0); perm = torch.stack([torch.randperm(T, generator=g) for _ in range(G)]); n_val = max(1, round(0.2 * T))
ids, lens, train, val = [], [], [], []; pt = {"train": {"cross_traj": [], "viewpoint": []}, "val": {"cross_traj": [], "viewpoint": []}}
for gi, f in enumerate(files):
    d = np.load(f); img, st = d["images"], d["state"]; K = img.shape[1]
    for k in range(T):
        ep = gi * T + k; s = st[k]
        dq = s[1:, :3] - s[:-1, :3]; dq = np.concatenate([dq, dq[-1:]], 0); act = np.concatenate([dq, np.zeros((len(dq), 5))], 1).astype(np.float32)
        np.savez(f"{root}/episodes/traj_{ep:06d}.npz", image_base=img[k, :, 0], image_side=img[k, :, 1], action=act)
        ids.append(ep); lens.append(K); split = "val" if k in perm[gi, :n_val].tolist() else "train"; (val if split == "val" else train).append(ep)
        pt[split]["viewpoint"] += [[ep, t] for t in range(K)]
    for split, members in (("train", [gi * T + k for k in range(T) if gi * T + k in train]), ("val", [gi * T + k for k in range(T) if gi * T + k in val])):
        for a, b in itertools.combinations(members, 2): pt[split]["cross_traj"] += [[a, t, b, t] for t in range(K)]
    if gi % 20 == 0: print(task, gi, "/", G, flush=True)
json.dump({"episode_ids": ids, "episode_lengths": lens}, open(f"{root}/index.json", "w")); json.dump({"train": train, "val": val}, open(f"{root}/split.json", "w"))
with h5py.File(f"{root}/pairs.h5", "w") as hf:
    for split in ("train", "val"):
        for kind in ("cross_traj", "viewpoint"): hf.create_dataset(f"{split}/{kind}", data=np.array(pt[split][kind], dtype=np.int64))
print(task, "episodes", len(ids), "train", len(train), "val", len(val), {s: {k: len(v) for k, v in d.items()} for s, d in pt.items()})
