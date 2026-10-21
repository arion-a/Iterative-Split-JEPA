"""All frames of the NUS videos at 64x64 gray (uint8) for the representation / data / lag tests (configs/nus_t.yaml). Frame order is checked.
Writes data/nus/all64.npy (N, 4096) and data/nus/all_meta.json (video id and frame index per row). Needs pyarrow (PYTHONPATH=/tmp/claude-0/pa)."""
import glob, io, json
import numpy as np
import pyarrow.parquet as pq
from PIL import Image

out, vid_ids, idx = [], [], []
for path in sorted(glob.glob("data/public/nus_dp/p[0-9].parquet")):
    f = pq.ParquetFile(path)
    for g in range(f.metadata.num_row_groups):
        t = f.read_row_group(g)
        for im, tr in zip(t.column("image").to_pylist(), t.column("trajectory").to_pylist()):
            v, k = tr.rsplit("_", 1)
            out.append(np.asarray(Image.open(io.BytesIO(im["bytes"])).convert("L").resize((64, 64), Image.BOX), np.uint8).reshape(-1))
            vid_ids.append(v); idx.append(int(k))
    print(path, len(out), flush=True)
np.save("data/nus/all64.npy", np.stack(out)); json.dump({"video": vid_ids, "frame": idx}, open("data/nus/all_meta.json", "w"))
print("frames", len(out), "videos", len(set(vid_ids)))
