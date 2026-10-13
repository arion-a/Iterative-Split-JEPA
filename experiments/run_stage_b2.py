"""Run Stage B2: for each number of categories and seed, train one encoder and compare four ways of
building the second split's pairs. One process per seed; finished runs are skipped on restart.

    python experiments/run_stage_b2.py --out runs/stage_b2/r1 --seeds 0
    python experiments/run_stage_b2.py --smoke 300      # code-path check, nothing saved
"""
import argparse
import json
import os

import yaml

from isj import explog
from isj.stage_b2 import run_stage_b2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/stage_b2.yaml")
    ap.add_argument("--out")
    ap.add_argument("--seeds", type=int, nargs="*")
    ap.add_argument("--categories", type=int, nargs="*")
    ap.add_argument("--smoke", type=int)
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    if a.smoke:
        cfg["encoder"]["steps"] = a.smoke
        r = run_stage_b2(cfg, 0, 6)
        print("SMOKE", json.dumps({k: {m: round(x, 3) for m, x in v.items()} for k, v in r["arms"].items()}), r["cluster_purity"], r["seconds"])
        return
    os.makedirs(a.out, exist_ok=True)
    seeds = a.seeds if a.seeds else cfg["seeds"]
    cats = a.categories if a.categories else cfg["sweep"]["n_categories"]
    for K in cats:
        for s in seeds:
            path = os.path.join(a.out, f"K{K}_seed{s}.json")
            if os.path.exists(path):
                continue
            r = run_stage_b2(cfg, s, K)
            with open(path, "x") as f:
                json.dump(r, f, indent=1)
            explog.append("run", f"Stage B2 K={K} seed={s} finished", stage="B", step="4.2", objectives=["O2"],
                          outputs={"cluster_purity": round(r["cluster_purity"], 3),
                                   **{f"{n}_angle": round(x["angle_deg"], 2) for n, x in r["arms"].items()}},
                          artifact_paths=[path])
            print(K, s, round(r["cluster_purity"], 3), {n: round(x["angle_deg"], 1) for n, x in r["arms"].items()}, flush=True)


if __name__ == "__main__":
    main()
