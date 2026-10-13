"""Run Stage B1 (ground-truth pairs): 3 seeds x {main, shuffled_rung2, rank1_rung2, no_inv, no_pred, no_var}.

    python experiments/run_stage_b1.py --out runs/stage_b1/<tag> --seeds 0     # one process per seed

Criteria are hash-frozen. The last worker to finish writes the report and the plain-language log row.
Pass --smoke N for a code-path check with N training steps: nothing is saved or logged.
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
from isj.stage_b1 import evaluate, run_stage_b1

ARMS = [("main", {}), ("shuffled_rung2", dict(control="shuffled_rung2")), ("rank1_rung2", dict(control="rank1_rung2")),
        ("no_inv", dict(ablation="no_inv")), ("no_pred", dict(ablation="no_pred")), ("no_var", dict(ablation="no_var"))]


def write_once(path, obj):
    with open(path, "x", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)


def lines(runs, report):
    def ms(arm, f, nd=2):
        v = [f(r) for r in runs[arm]]
        return f"{st.mean(v):.{nd}f} ± {st.stdev(v):.{nd}f}" if len(v) > 1 else f"{v[0]:.{nd}f}"
    m = "main"
    out = ["All results use ground-truth pairs (the generator builds the twins at each level).",
           f"Rung 1, texture split off: angle {ms(m, lambda r: r['rungs'][0]['angle_deg'])} degrees (needs below 5); variant_r2 {ms(m, lambda r: r['rungs'][0]['variant_r2'], 3)} (needs above 0.9); gap ratio {ms(m, lambda r: r['rungs'][0]['gap_ratio'], 0)}",
           f"Rung 2, identity split off inside what rung 1 left: angle {ms(m, lambda r: r['rungs'][1]['angle_deg'])} degrees; variant_r2 {ms(m, lambda r: r['rungs'][1]['variant_r2'], 3)}; gap ratio {ms(m, lambda r: r['rungs'][1]['gap_ratio'], 0)}",
           f"Category core (last 4 directions): invariant_r2 {ms(m, lambda r: r['core_invariant_r2'], 3)} (needs above 0.9)",
           f"Nesting: rung-2 block vs true span of identity + category {ms(m, lambda r: r['nesting_angle_deg'])} degrees (needs below 5)",
           f"Leakage, paper's names: a12_fro {ms(m, lambda r: max(x['a12_fro'] for x in r['rungs']), 4)}, a21_fro {ms(m, lambda r: max(x['a21_fro'] for x in r['rungs']), 4)}, block_purity {ms(m, lambda r: min(x['block_purity'] for x in r['rungs']), 5)} (paper, one split: 0.003, 0.024, 0.99993)",
           f"Rank check: smallest variant eigenvalue per rung {ms(m, lambda r: r['rungs'][0]['lambda_dk'])} and {ms(m, lambda r: r['rungs'][1]['lambda_dk'])} (about 2 expected for unit-variance blocks)",
           f"Verdict: {report['verdict']}; criteria failing on any seed: {report['failing_criteria'] or 'none'}",
           "Controls that must fail: " + ", ".join(f"{k} {'behaved' if v else 'DID NOT behave'}" for k, v in report["controls"].items()),
           f"Recorded without expectation (rung-1 angle / rung-2 angle): no spectral head {ms('no_inv', lambda r: r['rungs'][0]['angle_deg'], 1)} / {ms('no_inv', lambda r: r['rungs'][1]['angle_deg'], 1)}; no prediction {ms('no_pred', lambda r: r['rungs'][0]['angle_deg'], 1)} / {ms('no_pred', lambda r: r['rungs'][1]['angle_deg'], 1)}; no regularizer or whitening {ms('no_var', lambda r: r['rungs'][0]['angle_deg'], 1)} / {ms('no_var', lambda r: r['rungs'][1]['angle_deg'], 1)}"]
    if report["verdict"] == "PASS_WITH_LOCATED_RISK":
        out.append("LOCATED RISK: only texture's variant_r2 failed. Separate speeds plus the paper's alignment objective squash the fast block; this is logged as the located risk, not a B1 failure.")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/stage_b1.yaml")
    ap.add_argument("--out")
    ap.add_argument("--seeds", type=int, nargs="*")
    ap.add_argument("--arms", nargs="*")
    ap.add_argument("--criteria-sha", default=None)
    ap.add_argument("--smoke", type=int, help="code-path check with this many steps; saves and logs nothing")
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    expected = open(a.criteria_sha or a.config.replace(".yaml", ".criteria.sha256")).read().strip()
    if hashlib.sha256(json.dumps(cfg["criteria"], sort_keys=True).encode()).hexdigest() != expected:
        sys.exit("criteria differ from the frozen hash; amend the plan first")
    if a.smoke:
        cfg["encoder"]["steps"] = a.smoke
        cfg["significance"]["n_perm"] = 50
        for name, kw in ARMS:
            if a.arms and name not in a.arms:
                continue
            r = run_stage_b1(cfg, 0, **kw)
            print("SMOKE", name, [round(x["angle_deg"], 1) for x in r["rungs"]], round(r["core_invariant_r2"], 3), r["seconds"], "s")
        return
    seeds = a.seeds if a.seeds else cfg["seeds"]
    os.makedirs(a.out, exist_ok=True)
    arms = [t for t in ARMS if not a.arms or t[0] in a.arms]
    explog.append("run", f"Stage B1 run started: seeds {seeds}, arms {[n for n, _ in arms]}", stage="B", step="4.2", objectives=["O2"],
                  outputs={"criteria_sha256": expected, "seeds": seeds, "label": "ground-truth pairs"}, artifact_paths=[a.config])
    for name, kw in arms:
        for s in seeds:
            path = os.path.join(a.out, f"{name}_seed{s}.json")
            if os.path.exists(path):
                continue
            r = run_stage_b1(cfg, s, **kw)
            write_once(path, r)
            explog.append("run", f"Stage B1 arm={name} seed={s} finished", stage="B", step="4.2", objectives=["O2"],
                          outputs={"rung_angles_deg": [round(x["angle_deg"], 2) for x in r["rungs"]],
                                   "variant_r2": [round(x["variant_r2"], 3) for x in r["rungs"]],
                                   "core_invariant_r2": round(r["core_invariant_r2"], 3), "seconds": r["seconds"]},
                          artifact_paths=[path])
            print(name, s, [round(x["angle_deg"], 2) for x in r["rungs"]], flush=True)
    needed = [(n, s) for n, _ in ARMS for s in cfg["seeds"]]
    if all(os.path.exists(os.path.join(a.out, f"{n}_seed{s}.json")) for n, s in needed):
        try:
            open(os.path.join(a.out, ".reported"), "x").close()
        except FileExistsError:
            return
        runs = {n: [json.load(open(os.path.join(a.out, f"{n}_seed{s}.json"))) for s in cfg["seeds"]] for n, _ in ARMS}
        report = evaluate(runs, cfg)
        path = os.path.join(a.out, f"report_{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%S%f}.json")
        write_once(path, report)
        v = report["verdict"]
        explog.append("result", f"Stage B1 aggregate: {v}", stage="B", step="4.2", objectives=["O2", "OP"],
                      outputs={"verdict": v, "failing_criteria": report["failing_criteria"], "controls": report["controls"]},
                      artifact_paths=[path], verdict=v,
                      plain={"title": f"Stage B1 result: {v.replace('_', ' ').lower()} (ground-truth pairs)", "stage": "B",
                             "verdict": "pass" if v.startswith("PASS") else "fail",
                             "did": "Ran the full B1 experiment on 3 seeds: both splits with the trained mirror encoder, the controls, and the recorded ablations.",
                             "output": lines(runs, report),
                             "relevance": "This is the mechanism test of the project's core claim. A pass means: given correct pairs at each level, the invariant block of one split can be split again, each split recovers its own block, they nest properly, and the category core is recovered. It does not show the pairs can be built from the data; that is B2."})
        print(v, report["failing_criteria"])


if __name__ == "__main__":
    main()
