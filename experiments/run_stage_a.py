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

from isj import explog
from isj.stage_a import run_stage_a

ARM_MEANING = {
    "main": "Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.",
    "shuffled": "Control for O1 (plan §2.6 ii): destroying correspondences must flatten the gap; if it did not, the main-arm split would not be attributable to the correspondences.",
    "no_pred": "Ablation for O1: without predictive training the representation should not recover the latents.",
    "no_inv": "Ablation for O1: without the correspondence-driven rotation, prediction alone leaves the blocks mixed (Lemma 3.1).",
    "no_var": "Ablation for O1: without variance reg + ZCA the difference spectrum is not interpretable.",
}


def paper_lines(rs: list[dict]) -> list[str]:
    """Mean +/- std over seeds, under the paper's metric names."""
    import statistics as st

    def ms(f, nd):
        v = [f(r) for r in rs]
        return f"{st.mean(v):.{nd}f} ± {st.stdev(v):.{nd}f}" if len(v) > 1 else f"{v[0]:.{nd}f}"

    return [f"invariant_r2 {ms(lambda r: r['invariant_r2'], 3)}  (paper about 0.998)",
            f"variant_r2 {ms(lambda r: r['variant_r2'], 3)}  (paper about 0.997)",
            f"global_r2 {ms(lambda r: r['global_r2'], 3)}  (paper about 0.998)",
            f"a12_fro {ms(lambda r: r['leak_norms']['inv_from_var_fro'], 4)}  (paper 0.003)",
            f"a21_fro {ms(lambda r: r['leak_norms']['var_from_inv_fro'], 4)}  (paper 0.024)",
            f"block_purity {ms(lambda r: r['leak_norms']['block_purity'], 5)}  (paper about 0.99993)",
            f"Also: angle {ms(lambda r: r['angle_inv_deg'], 2)} degrees, gap ratio {ms(lambda r: r['gap_ratio'], 0)}."]


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
    ap.add_argument("--arms", nargs="*", help="explicit arm names to run, e.g. main no_inv")
    ap.add_argument("--no-plain", action="store_true", help="log to the chain but add no plain-language rows")
    ap.add_argument("--no-log", action="store_true", help="do not append to explog/chain.jsonl")
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

    def log(*args, **kw):
        if a.no_plain:
            kw.pop("plain", None)
        if not a.no_log:
            explog.append(*args, **kw)

    log("run", f"Stage A run set started: {a.out}, seeds {seeds}, overrides {a.set or 'none'}",
        stage="A", step="4.1", objectives=["O1", "OP"],
        how="experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, "
            "difference-moment split on 30k matched pairs, probe on disjoint latents)",
        outputs={"criteria_sha256": expected, "seeds": seeds, "overrides": a.set,
                 "coupling": cfg["world"]["coupling_strength"], "obs_dim": cfg["world"]["obs_dim"]},
        artifact_paths=[a.config],
        interpretation="Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).",
        plain={"title": f"Stage A run started ({a.out})", "stage": "A", "verdict": "info",
               "did": f"Started a Stage A run on seeds {seeds}" + (f" with changes {a.set}" if a.set else "") + ". The pass numbers were checked against their locked fingerprint first.",
               "output": ["Running. Results appear in the next row."],
               "relevance": "Part of testing whether the paper's single split works in our code (Stage A)."})

    arms = []
    if a.only in (None, "main"):
        arms.append(("main", "none", "none"))
    if a.only in (None, "controls"):
        arms += [("shuffled", "none", "shuffled"), ("no_pred", "no_pred", "none"),
                 ("no_inv", "no_inv", "none"), ("no_var", "no_var", "none")]
    if a.arms:
        every = [("main", "none", "none"), ("shuffled", "none", "shuffled"), ("no_pred", "no_pred", "none"),
                 ("no_inv", "no_inv", "none"), ("no_var", "no_var", "none")]
        arms = [t for t in every if t[0] in a.arms]
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
            log("run", f"Stage A arm={name} seed={s} finished",
                stage="A", step="4.1", objectives=["O1"],
                outputs={k: (round(r[k], 5) if isinstance(r[k], float) else r[k]) for k in
                         ("invariant_r2", "variant_r2", "global_r2", "angle_inv_deg", "angle_var_deg",
                          "gap_ratio", "selected_d", "leak_r2_max", "leak_any_significant", "seconds")},
                artifact_paths=[path], interpretation=ARM_MEANING[name])
            print(f"{name:9s} seed={s} inv_r2={r['invariant_r2']:.3f} angle={r['angle_inv_deg']:.2f} "
                  f"gap={r['gap_ratio']:.1f} leak_r2={r['leak_r2_max']:.4f} ({r['seconds']}s)", flush=True)
    report = {"git": meta["git"]}
    if "main" in runs:
        report["main"] = evaluate(runs["main"], cfg["criteria"])
    report["controls"] = check_controls(runs, cfg["controls"])
    import datetime as _dt
    report_path = os.path.join(a.out, f"report_{_dt.datetime.now(_dt.timezone.utc):%Y%m%dT%H%M%S%f}.json")
    write_once(report_path, report)   # unique name: parallel seed-workers must not overwrite each other
    if "main" in report:
        verdict = "PASS" if report["main"]["criteria"]["PASS"] else "FAIL"
        log("result", f"Stage A aggregate over seeds {seeds}: main arm {verdict}; controls {report['controls']}",
            stage="A", step="4.1", objectives=["O1", "OP"],
            outputs={"criteria": report["main"]["criteria"], "controls": report["controls"]},
            artifact_paths=[report_path],
            interpretation=("Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. "
                            "FAIL -> debug round (max 3) then halt and publish the negative." ),
            verdict=verdict,
            plain={"title": f"Stage A result: {verdict}", "stage": "A", "verdict": verdict.lower(),
                   "did": f"Finished the Stage A run on seeds {seeds} and scored it with the paper's metrics.",
                   "output": paper_lines(runs["main"]) + [f"Controls (should fail): {'all behaved' if all(report['controls'].values()) else 'SOME DID NOT behave: ' + str(report['controls'])}."],
                   "relevance": "A pass means the paper's single split works in our code, so Stage B (splitting a second time) can start. A fail means debugging, up to the plan's three-round limit."})
    print(json.dumps({k: v for k, v in report.items() if k != "main"} |
                     ({"main_criteria": report["main"]["criteria"]} if "main" in report else {}), indent=1))


if __name__ == "__main__":
    main()
