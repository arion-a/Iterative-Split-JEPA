"""Run Stage A (plan §4.1): 5 seeds x {main, shuffled control, 3 ablations}; evaluate frozen criteria.

    python experiments/run_stage_a.py --config configs/stage_a.yaml --out runs/stage_a/<tag>

Per-run artifacts are immutable (written with exclusive-create). The criteria block of the config
is hashed and must match `criteria_sha256` recorded in the config's sibling file
`configs/stage_a.criteria.sha256`; edit the plan first, never the threshold alone.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys

import yaml

from isj.stage_a import run_stage_a


def criteria_hash(cfg) -> str:
    return hashlib.sha256(json.dumps(cfg["criteria"], sort_keys=True).encode()).hexdigest()


def git_rev() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def write_once(path: str, obj: dict):
    with open(path, "x", encoding="utf-8") as f:   # 'x': refuse to overwrite an existing artifact
        json.dump(obj, f, indent=1)


def evaluate(main: list[dict], crit: dict) -> dict:
    """Per-seed, per-criterion pass/fail. A criterion passes only if it passes on every seed."""
    per = []
    for r in main:
        leak_ok = (not r["leak_any_significant"]) or r["leak_r2_max"] < crit["leakage_r2_floor"]
        per.append({
            "seed": r["seed"],
            "invariant_r2": r["invariant_r2"] > crit["invariant_r2_min"],
            "angle": max(r["angle_inv_deg"], r["angle_var_deg"]) < crit["angle_max_deg"],
            "gap_ratio": r["gap_ratio"] > crit["gap_ratio_min"],
            "leakage": leak_ok,
            "leakage_strict_null": not r["leak_any_significant"],   # reported, not gating
        })
    gating = ["invariant_r2", "angle", "gap_ratio", "leakage"]
    summary = {k: all(p[k] for p in per) for k in gating}
    summary["PASS"] = all(summary.values())
    return {"per_seed": per, "criteria": summary}


def check_controls(runs: dict, ctl: dict) -> dict:
    out = {}
    sh = runs.get("shuffled", [])
    if sh:
        out["shuffled"] = all(r["gap_ratio"] < ctl["shuffled"]["gap_ratio_max"]
                              and r["angle_inv_deg"] > ctl["shuffled"]["angle_min_deg"] for r in sh)
    for name in ("no_pred", "no_inv"):
        rs = runs.get(name, [])
        if rs:
            out[name] = all(r["invariant_r2"] < ctl["ablations"][name]["invariant_r2_max"] for r in rs)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/stage_a.yaml")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", type=int, nargs="*")
    ap.add_argument("--only", choices=["main", "controls"], default=None)
    ap.add_argument("--set", nargs="*", default=[], help="override, e.g. world.coupling_strength=1.0")
    a = ap.parse_args()

    cfg = yaml.safe_load(open(a.config))
    expected = open(a.config.replace(".yaml", ".criteria.sha256")).read().strip()
    if criteria_hash(cfg) != expected:
        sys.exit("criteria differ from the frozen hash; amend the plan first")
    for kv in a.set:
        k, v = kv.split("=", 1)
        sec, key = k.split(".")
        cfg[sec][key] = yaml.safe_load(v)
    seeds = a.seeds if a.seeds is not None and len(a.seeds) else cfg["seeds"]
    os.makedirs(a.out, exist_ok=True)
    meta = {"git": git_rev(), "criteria_sha256": expected, "config": cfg}
    try:
        write_once(os.path.join(a.out, "config.json"), meta)
    except FileExistsError:
        pass   # another seed-worker wrote it first

    arms = []
    if a.only in (None, "main"):
        arms.append(("main", "none", "none"))
    if a.only in (None, "controls"):
        arms += [("shuffled", "none", "shuffled"), ("no_pred", "no_pred", "none"),
                 ("no_inv", "no_inv", "none"), ("no_var", "no_var", "none")]
    runs: dict[str, list] = {}
    for name, abl, ctl in arms:
        for s in seeds:
            path = os.path.join(a.out, f"{name}_seed{s}.json")
            if os.path.exists(path):
                runs.setdefault(name, []).append(json.load(open(path)))
                continue
            r = run_stage_a(cfg, s, ablation=abl, control=ctl)
            write_once(path, r)
            runs.setdefault(name, []).append(r)
            print(f"{name:9s} seed={s} inv_r2={r['invariant_r2']:.3f} angle={r['angle_inv_deg']:.2f} "
                  f"gap={r['gap_ratio']:.1f} leak_r2={r['leak_r2_max']:.4f} ({r['seconds']}s)", flush=True)
    report = {"git": meta["git"]}
    if "main" in runs:
        report["main"] = evaluate(runs["main"], cfg["criteria"])
    report["controls"] = check_controls(runs, cfg["controls"])
    with open(os.path.join(a.out, "report.json"), "w") as f:
        json.dump(report, f, indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != "main"} |
                     ({"main_criteria": report["main"]["criteria"]} if "main" in report else {}), indent=1))


if __name__ == "__main__":
    main()
