"""Run formal Stage B2 (docs/B2.md): sigma_cat sweep x seeds; one encoder per run; all arms on that encoder.

    python experiments/run_stage_b2_spec.py --out results/B2 --seeds 0       # one process per seed
    python experiments/run_stage_b2_spec.py --smoke 300                        # code-path check, nothing saved

Raw JSON per run: results/B2/sigma_cat_<value>/<seed>.json (never overwritten). One line per run is appended to docs/STATUS.md.
"""
import argparse
import hashlib
import json
import os
import sys

import yaml

from isj import explog
from isj.stage_b2_spec import run_stage_b2_spec


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/stage_b2_spec.yaml")
    ap.add_argument("--out", default="results/B2")
    ap.add_argument("--seeds", type=int, nargs="*")
    ap.add_argument("--sigmas", type=float, nargs="*")
    ap.add_argument("--smoke", type=int)
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    if sha(cfg["targets"]) != open("configs/stage_b2_spec.targets.sha256").read().strip():
        sys.exit("B2 targets differ from the frozen hash")
    b1 = yaml.safe_load(open(cfg["gate_criteria_from"]))
    if sha(b1["criteria"]) != open("configs/stage_b1.criteria.sha256").read().strip():
        sys.exit("B1 gate criteria differ from their frozen hash")
    if a.smoke:
        cfg["encoder"]["steps"] = a.smoke
        r = run_stage_b2_spec(cfg, 0, cfg["sweep"]["clean_sigma_cat"])
        print("SMOKE purity", round(r["quality"]["cluster_purity"], 3), "K found", r["quality"]["k_discovered"], "singleton pairs", r["construction"]["c3_singleton"]["n_pairs"])
        for k, v in r["arms"].items():
            print(f"  {k:20s} angle {v['angle_deg']:.1f} var_r2 {v['variant_r2']:.3f} inv_r2 {v['invariant_r2']:.3f} gap {v['gap_ratio']:.1f} rank_def {v['rank_deficient']} validity {r['construction'][k]['pair_validity']}")
        return
    seeds = a.seeds if a.seeds else cfg["seeds"]
    sigmas = a.sigmas if a.sigmas else cfg["sweep"]["sigma_cat"]
    for sg in sigmas:
        for s in seeds:
            d = os.path.join(a.out, f"sigma_cat_{sg}")
            os.makedirs(d, exist_ok=True)
            path = os.path.join(d, f"{s}.json")
            if os.path.exists(path):
                continue
            r = run_stage_b2_spec(cfg, s, sg)
            with open(path, "x") as f:
                json.dump(r, f, indent=1)
            q, m, b = r["quality"], r["arms"]["b2_kmeans"], r["arms"]["b1_generator"]
            line = (f"| {r['seed']} | B2{cfg.get("label","")} sigma_cat={sg} | purity {q['cluster_purity']:.2f}, K found {q['k_discovered']} | "
                    f"rung-2 angle B1 {b['angle_deg']:.1f} deg, B2 {m['angle_deg']:.1f} deg | `{path}` |\n")
            with open("docs/STATUS.md", "a") as f:
                f.write(line)
            explog.append("run", f"Stage B2 sigma_cat={sg} seed={s} finished", stage="B", step="4.2", objectives=["O2"],
                          outputs={"purity": round(q["cluster_purity"], 3), "k_found": q["k_discovered"],
                                   "angle_b1": round(b["angle_deg"], 2), "angle_b2": round(m["angle_deg"], 2)}, artifact_paths=[path])
            print(sg, s, round(q["cluster_purity"], 3), q["k_discovered"], round(b["angle_deg"], 1), round(m["angle_deg"], 1), flush=True)


if __name__ == "__main__":
    main()
