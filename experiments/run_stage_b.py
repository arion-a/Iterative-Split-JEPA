"""Run Stage B (plan §4.2): 3 seeds x {main, shuffled rung-2 pairs, rank-1 rung 2, 3 ablations} plus a
factor-free null world; evaluate the frozen criteria.

    python experiments/run_stage_b.py --out runs/stage_b/<tag> --seeds 0

Run seeds in parallel processes; the last worker to finish writes the report and the log row.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import statistics as st
import sys

import yaml

from isj import explog
from isj.stage_b import run_stage_b

ARMS = [("main", dict()), ("null", dict(with_cross=False)),
        ("shuffled_rung2", dict(control="shuffled_rung2")), ("rank1_rung2", dict(control="rank1_rung2")),
        ("no_pred", dict(ablation="no_pred")), ("no_inv", dict(ablation="no_inv")), ("no_var", dict(ablation="no_var"))]


def write_once(path, obj):
    with open(path, "x", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)


def evaluate(runs: dict, cfg: dict) -> dict:
    c, ctl = cfg["criteria"], cfg["controls"]
    t_null = max(r["deviation"]["T"] for r in runs["null"])
    per = []
    for r in runs["main"]:
        a1, a2 = r["rungs"][0]["angle_deg"], r["rungs"][1]["angle_deg"]
        dv = r["deviation"]
        per.append({"seed": r["seed"],
                    "gate_G1": a1 < c["gate_G1_rung1_angle_max_deg"],
                    "rung_angles": max(a1, a2) < c["rung_angle_max_deg"],
                    "nesting": r["nesting_angle_deg"] < c["nesting_angle_max_deg"],
                    "factor_direction": max(dv["angle_to_true_factor_deg"]) < c["deviation_direction_angle_max_deg"],
                    "factor_recurs": max(dv["recurrence_angles_deg"]) < c["deviation_recurrence_angle_max_deg"],
                    "T_large_enough": dv["T"] >= c["deviation_T_min"],
                    "T_over_null": dv["T"] >= c["deviation_T_over_null_max"] * t_null})
    keys = [k for k in per[0] if k != "seed"]
    crit = {k: all(p[k] for p in per) for k in keys}
    crit["PASS"] = all(crit.values())

    def mean(arm, f): return st.mean(f(r) for r in runs[arm])
    controls = {
        "shuffled_rung2": mean("shuffled_rung2", lambda r: r["rungs"][1]["angle_deg"]) > ctl["shuffled_rung2"]["rung2_angle_min_deg"]
                          and mean("shuffled_rung2", lambda r: r["rungs"][1]["gap_ratio"]) < ctl["shuffled_rung2"]["rung2_gap_ratio_max"],
        "rank1_rung2": mean("rank1_rung2", lambda r: r["rungs"][1]["angle_deg"]) > ctl["rank1_rung2"]["rung2_angle_min_deg"]
                       and mean("rank1_rung2", lambda r: r["rungs"][0]["angle_deg"]) < ctl["rank1_rung2"]["rung1_angle_max_deg"],
        "no_pred": mean("no_pred", lambda r: r["rungs"][0]["angle_deg"]) > ctl["no_pred"]["rung1_angle_min_deg"],
        "no_inv": mean("no_inv", lambda r: r["rungs"][0]["angle_deg"]) > ctl["no_inv"]["rung1_angle_min_deg"],
    }
    return {"per_seed": per, "criteria": crit, "controls": controls, "T_null_max": t_null}


def lines(runs, report):
    def ms(arm, f, nd=2):
        v = [f(r) for r in runs[arm]]
        return f"{st.mean(v):.{nd}f} ± {st.stdev(v):.{nd}f}" if len(v) > 1 else f"{v[0]:.{nd}f}"
    m = "main"
    return [f"Rung 1 (split off texture): angle {ms(m, lambda r: r['rungs'][0]['angle_deg'])} degrees (needs below 5); R² of true block {ms(m, lambda r: r['rungs'][0]['r2'], 3)}; block_purity {ms(m, lambda r: r['rungs'][0]['block_purity'], 4)}",
            f"Rung 2 (split off identity, inside the rung-1 invariant block): angle {ms(m, lambda r: r['rungs'][1]['angle_deg'])} degrees (needs below 5); R² {ms(m, lambda r: r['rungs'][1]['r2'], 3)}; block_purity {ms(m, lambda r: r['rungs'][1]['block_purity'], 4)}",
            f"Nesting: rung-2 block vs true span of the remaining blocks {ms(m, lambda r: r['nesting_angle_deg'])} degrees (needs below 5)",
            f"Core left after both splits: R² of the category block {ms(m, lambda r: r['core_block3_r2'], 3)}",
            f"Cross-cutting factor: detector total T {ms(m, lambda r: r['deviation']['T'])} (factor-free worlds: at most {report['T_null_max']:.3f}); leftover direction within {ms(m, lambda r: max(r['deviation']['angle_to_true_factor_deg']))} degrees of the true factor; recurs across rungs within {ms(m, lambda r: max(r['deviation']['recurrence_angles_deg']))} degrees",
            "Criteria: " + ", ".join(f"{k} {'ok' if v else 'FAILED'}" for k, v in report["criteria"].items() if k != "PASS"),
            "Controls (must fail as stated): " + ", ".join(f"{k} {'behaved' if v else 'DID NOT behave'}" for k, v in report["controls"].items()),
            f"Controls detail (rung-2 angle, mean): shuffled {ms('shuffled_rung2', lambda r: r['rungs'][1]['angle_deg'], 1)}, rank-1 {ms('rank1_rung2', lambda r: r['rungs'][1]['angle_deg'], 1)}; rung-1 angle without prediction {ms('no_pred', lambda r: r['rungs'][0]['angle_deg'], 1)}, without spectral head {ms('no_inv', lambda r: r['rungs'][0]['angle_deg'], 1)}"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/stage_b.yaml")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", type=int, nargs="*")
    ap.add_argument("--arms", nargs="*")
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    expected = open(a.config.replace(".yaml", ".criteria.sha256")).read().strip()
    if hashlib.sha256(json.dumps(cfg["criteria"], sort_keys=True).encode()).hexdigest() != expected:
        sys.exit("criteria differ from the frozen hash; amend the plan first")
    seeds = a.seeds if a.seeds else cfg["seeds"]
    os.makedirs(a.out, exist_ok=True)
    arms = [t for t in ARMS if not a.arms or t[0] in a.arms]
    explog.append("run", f"Stage B run started: seeds {seeds}, arms {[n for n, _ in arms]}", stage="B", step="4.2", objectives=["O2"],
                  outputs={"criteria_sha256": expected, "seeds": seeds}, artifact_paths=[a.config])
    for name, kw in arms:
        for s in seeds:
            path = os.path.join(a.out, f"{name}_seed{s}.json")
            if os.path.exists(path):
                continue
            r = run_stage_b(cfg, s, **kw)
            write_once(path, r)
            explog.append("run", f"Stage B arm={name} seed={s} finished", stage="B", step="4.2", objectives=["O2"],
                          outputs={"rung_angles_deg": [round(x["angle_deg"], 2) for x in r["rungs"]], "nesting_deg": round(r["nesting_angle_deg"], 2),
                                   "T": round(r["deviation"]["T"], 3), "seconds": r["seconds"]}, artifact_paths=[path])
            print(name, s, [round(x["angle_deg"], 2) for x in r["rungs"]], flush=True)
    # the last worker to finish writes the report
    needed = [(n, s) for n, _ in ARMS for s in (cfg["seeds"] if n != "null" else cfg["null_seeds"])]
    if all(os.path.exists(os.path.join(a.out, f"{n}_seed{s}.json")) for n, s in needed):
        try:
            marker = open(os.path.join(a.out, ".reported"), "x"); marker.close()
        except FileExistsError:
            return
        runs = {n: [json.load(open(os.path.join(a.out, f"{n}_seed{s}.json"))) for s in (cfg["seeds"] if n != "null" else cfg["null_seeds"])] for n, _ in ARMS}
        report = evaluate(runs, cfg)
        path = os.path.join(a.out, f"report_{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%S%f}.json")
        write_once(path, report)
        verdict = "PASS" if report["criteria"]["PASS"] else "FAIL"
        out = lines(runs, report)
        explog.append("result", f"Stage B aggregate: {verdict}", stage="B", step="4.2", objectives=["O2", "OP"],
                      outputs={"criteria": report["criteria"], "controls": report["controls"]}, artifact_paths=[path], verdict=verdict,
                      plain={"title": f"Stage B result: {verdict}", "stage": "B", "verdict": verdict.lower(),
                             "did": "Ran the full Stage B experiment (3 seeds): both splits with the trained mirror encoder, the factor-free comparison worlds, and the controls.",
                             "output": out,
                             "relevance": "This is the project's core claim. PASS means the 'stays the same' part of one split was split again, correctly and in the right nesting, and the hidden cross-cutting factor was flagged. FAIL means the claim does not hold under these conditions, and the numbers show where."})
        print(json.dumps(report["criteria"], indent=1)); print(json.dumps(report["controls"], indent=1))


if __name__ == "__main__":
    main()
