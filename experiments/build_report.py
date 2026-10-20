"""Render results/<stage>/REPORT.md in the docs/REPORTING.md format (gate table, controls, informational) from the raw JSON files.

    python experiments/build_report.py handshake | hier | real
"""
from __future__ import annotations

import glob
import json
import sys

import numpy as np
import yaml


def ms(v):
    v = np.asarray(v, float)
    return f"{v.mean():.3f} ± {v.std():.3f}" if len(v) > 1 else f"{v[0]:.3f}"


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def handshake():
    cfg = yaml.safe_load(open("configs/handshake.yaml")); c = cfg["criteria"]
    runs = [json.load(open(p)) for p in sorted(glob.glob("results/handshake/main/*.json"))]
    seeds = [r["seed"] for r in runs]
    m = lambda k, arm="main": [r["arms"][arm][k] for r in runs]
    cert = c["certificate"]
    last = [r["ladder_main"][-1] for r in runs]
    s1_ok = [(x["k"] == c["ladder"]["s1_rung"] and x.get("stop") == "S1") for x in last]
    reach_v = [r.get("reach_variant_block", {}).get("32") for r in runs]; reach_p = [r["reach_psi"]["32"] for r in runs]
    stab = list(runs[0]["pilot_stability_pairs"].values())
    gate = [
        ["E31c′ violation rate V", "matched states keep matched successors", f"≤ {cert['V_max']}", ms(m("V")), all(v <= cert["V_max"] for v in m("V"))],
        ["E31c′ non-degeneracy (ICC)", "share of ψ variance between releases (a constant has V = 0)", f"≥ {cert['icc_min']}", ms(m("icc")), all(v >= cert["icc_min"] for v in m("icc"))],
        ["E31c′ stability L", "Lipschitz constant of the linear latent transition", f"≤ {cert['L_max']}", ms(m("L")), all(v <= cert["L_max"] for v in m("L"))],
        ["E31c′ rollout closure", f"{cert['horizon_K']}-step rollout RMSE / std ψ", f"≤ {cert['rollout_nmse_max']}", ms(m("rollout_nmse")), all(v <= cert["rollout_nmse_max"] for v in m("rollout_nmse"))],
        ["E31d naming", "|Spearman(ψ, E)| on held-out releases (evaluator side)", f"≥ {c['naming']['spearman_min']}", ms(m("naming_abs_spearman")), all(v >= c["naming"]["spearman_min"] for v in m("naming_abs_spearman"))],
        ["E31e ladder ends by S1 at the third family (lag 32)", "no variation left beyond the discovered coordinate", "every seed", f"{sum(s1_ok)}/{len(s1_ok)} seeds (stops: {[ (x['k'], x.get('stop')) for x in last]})", all(s1_ok)],
        ["E31e reach", "NMSE at horizon 32: variant block ≥ 0.5 and ψ ≤ 0.1225", "every seed", f"variant {ms([v for v in reach_v if v is not None]) if any(v is not None for v in reach_v) else 'n/a'}, ψ {ms(reach_p)}", all(v is not None and v >= 0.5 for v in reach_v) and all(v <= 0.1225 for v in reach_p)],
        ["P-stab", "min pairwise |Spearman| of ψ across seeds (common held-out frames)", f"≥ {c['pilot']['stability_min_abs_spearman']}", ms(stab), all(v >= c["pilot"]["stability_min_abs_spearman"] for v in stab)],
    ]
    ctrl = []
    for arm in ("flat", "shuffled"):
        v = m("naming_abs_spearman", arm)
        ctrl.append([f"{arm} arm", "|Spearman(ψ, E)| below 0.9 on every seed" , ms(v), all(x < c["pilot"]["control_max_abs_spearman_E"] for x in v)])
    ctrl.append(["shuffled arm ladder", "S2 (flat spectrum) at the first lag family", str([r["ladder_shuffled_stop"] for r in runs]), all(r["ladder_shuffled_stop"] == "S2" for r in runs)])
    refs = [[k] + [ms([r["references"][k][x] for r in runs]) for x in ("V", "icc", "L", "rollout_nmse")] for k in ("E", "angles", "const")]
    arms = [[a] + [ms(m(x, a)) for x in ("V", "icc", "L", "rollout_nmse", "naming_abs_spearman")] for a in ("main", "flat", "shuffled")]
    rungs = []
    for r in runs:
        for x in r["ladder_main"]:
            rungs.append([r["seed"], x["family"], x["content_dim"], x["d_k"], round(x["lambda_max_over_chance"], 3), round(x["best_ratio"], 2), x.get("stop", "split")])
    ceil = [[r["seed"], round(r["ceiling_probe_report_only"]["r2_train"], 3), round(r["ceiling_probe_report_only"]["r2_test"], 3)] for r in runs]
    verdict = f"Handshake on {len(runs)} seeds: gates passed {sum(g[-1] for g in gate)}/{len(gate)}; controls behaved {sum(x[-1] for x in ctrl)}/{len(ctrl)}."
    txt = ["# Stage V handshake report (P2-P3)", "", f"Seeds {seeds}. Criteria frozen in `configs/handshake.yaml` (sha256 in `configs/handshake.criteria.sha256`). Format: docs/REPORTING.md.", "",
           "## A. Gate table", table(["Criterion", "Plain meaning", "Threshold", "Measured (mean ± std over seeds)", "Pass?"], gate), "",
           "## D. Verdict and controls", verdict, "", table(["Control", "Required outcome", "Observed", "Behaved?"], ctrl), "",
           "## Informational (not gates)", "", "Arms (physics-free certificate + naming):", table(["arm", "V", "ICC", "L", "rollout", "|Spearman| with E"], arms), "",
           "Evaluator-side reference coordinates through the same checker (q_energy should pass; q_angle and q_const should fail V or ICC):", table(["reference", "V", "ICC", "L", "rollout"], refs), "",
           "Ladder records (lambda_max over chance = largest eigenvalue / 2 of the family's difference moment on the remaining content):", table(["seed", "family", "content dim", "d_k", "lambda_max / chance", "best ratio", "outcome"], rungs), "",
           "Ceiling probe (REPORT-ONLY, D13): linear readout of E from the whitened latent, R²:", table(["seed", "train", "test"], ceil), "",
           "Reach curves (NMSE vs horizon, held-out releases): see raw JSON `reach_psi`, `reach_variant_block`.", "",
           "Not run: E31f (no frozen statistic). Limitations: additive-illumination nuisance only (gain, shift not tested); naming sign is arbitrary so |Spearman| is used; datasets differ per seed, P-stab compares seeds on the seed-0 test releases."]
    open("results/handshake/REPORT.md", "w").write("\n".join(txt) + "\n")
    return verdict, gate, ctrl


def hier():
    cfg = yaml.safe_load(open("configs/hier.yaml")); c = cfg["criteria"]
    lad = [json.load(open(p)) for p in sorted(glob.glob("results/hier/ladder/*.json"))]
    shf = [json.load(open(p)) for p in sorted(glob.glob("results/hier/shuffled/*.json"))]
    rungs = [r["RUNGS"] for r in lad]
    gate = [["E35 RUNGS", "cuts found by the lag ladder (registered: 4)", f"= {c['e35']['expected_rungs']}", ms(rungs) + f" ({rungs})", all(x == c["e35"]["expected_rungs"] for x in rungs)]]
    per = [p for r in lad for p in r.get("per_rung", [])]
    if per:
        gate += [["per-rung variant R²", "linear readout of the removed blocks from the rung's variant block", f"≥ {c['per_rung']['block_r2_min']}", ms([p["variant_r2"] for p in per if p["variant_r2"] is not None]), all(p["variant_r2"] is None or p["variant_r2"] >= c["per_rung"]["block_r2_min"] for p in per)],
                 ["per-rung invariant R²", "readout of the remaining blocks from the rung's invariant core", f"≥ {c['per_rung']['block_r2_min']}", ms([p["invariant_r2"] for p in per if p["invariant_r2"] is not None]), all(p["invariant_r2"] is None or p["invariant_r2"] >= c["per_rung"]["block_r2_min"] for p in per)],
                 ["(D) residual ratio", "learned vs oracle-block one-step residual", f"≤ {c['per_rung']['dc_ratio_max']}", ms([p["D_ratio"] for p in per if "D_ratio" in p]), all(p.get("D_ratio", 0) <= c["per_rung"]["dc_ratio_max"] for p in per)],
                 ["(C) rollout ratio", f"learned vs oracle {c['per_rung']['horizon_K']}-step rollout error", f"≤ {c['per_rung']['dc_ratio_max']}", ms([p["C_ratio"] for p in per if "C_ratio" in p]), all(p.get("C_ratio", 0) <= c["per_rung"]["dc_ratio_max"] for p in per)],
                 ["L per rung", "Lipschitz constant of the learned linear transition", f"≤ {c['per_rung']['L_max']}", ms([p["L"] for p in per if "L" in p]), all(p.get("L", 0) <= c["per_rung"]["L_max"] for p in per)]]
    ctrl = [["shuffled pairs", f"RUNGS = {c['e35']['control_rungs']}", str([r["RUNGS"] for r in shf]), all(r["RUNGS"] == c["e35"]["control_rungs"] for r in shf)]]
    fam = [[r["seed"], x["family"], x["content_dim"], x["d_k"], round(x["best_ratio"], 2), x.get("stop", "split"), [round(v, 2) for v in x["eigvals"]]] for r in lad for x in r["families"]]
    perrows = [[r["seed"], p["rung"], p["family"], p["variant_blocks"], p["invariant_blocks"], p["variant_r2"], p["invariant_r2"], p.get("D_ratio"), p.get("C_ratio"), p.get("L")] for r in lad for p in r.get("per_rung", [])]
    oracle = lad[0]["oracle_cut_gaps_lag1"]
    verdict = f"Hierarchical: RUNGS {rungs} against the registered 4; gates passed {sum(g[-1] for g in gate)}/{len(gate)}; control {'behaved' if ctrl[0][-1] else 'did not behave'}."
    txt = ["# Stage V hierarchical report (P4)", "", "Criteria frozen in `configs/hier.yaml`. Format: docs/REPORTING.md.", "", "## A. Gate table", table(["Criterion", "Plain meaning", "Threshold", "Measured", "Pass?"], gate), "",
           "## D. Verdict and controls", verdict, "", table(["Control", "Required outcome", "Observed", "Behaved?"], ctrl), "", "## Informational (not gates)", "",
           f"Oracle cut gaps at lag 1 (arithmetic, 2(1−a) ratios): {[round(x, 2) for x in oracle]}; a cut needs ratio ≥ 2.", "",
           "Family records:", table(["seed", "family", "content dim", "d_k", "best ratio", "outcome", "eigenvalues"], fam), "",
           "Per-rung evaluation (blocks are 1 = fastest … 5 = slowest):", table(["seed", "rung", "family", "variant blocks", "invariant blocks", "variant R²", "invariant R²", "D ratio", "C ratio", "L"], perrows), "",
           "Not run: ARM-S (equals rung 1 of the ladder), ARM-H/F, E36-E38 (need a constructed bridge-failure world)."]
    open("results/hier/REPORT.md", "w").write("\n".join(txt) + "\n")
    return verdict, gate, ctrl


def real():
    r = json.load(open("results/real/morpheus.json"))
    cert = r["certificate"]
    rows = [[k, round(v, 4) if isinstance(v, float) else v] for k, v in cert.items()]
    rungs = [[x["family"], x["content_dim"], x["d_k"], round(x["lambda_max_over_chance"], 3), round(x["best_ratio"], 2), x.get("stop", "split")] for x in r["ladder"]]
    inf = [[k, round(v["abs_spearman_psi_test"], 3), round(v["ceiling_probe_r2_test_report_only"], 3)] for k, v in r["informational"].items()]
    txt = ["# Stage V real-video report (P5), informational", "", f"{r['n_videos']} public real double-pendulum clips (MIT licence), {r['frames_per_video']} frames each at {r['fps']} fps, held out in TIME (first 60% train, next 15% validation, last 25% test), not in release.",
           "No gates, no frozen predictions (DECIDE 9). The framework input is a 32×32 grayscale crop with an additive-illumination view pair; the orange-link tracker is evaluator-side and partial (one link only), so NO energy naming is claimed.", "",
           f"Ladder stop: {r['stop']}; core dimension {r['core_dim']}; psi ICC on fit: {r['psi_icc_fit']:.3f}", "", "Certificate on the held-out time slice:", table(["quantity", "value"], rows), "",
           "Ladder records:", table(["family", "content dim", "d_k", "lambda_max / chance", "best ratio", "outcome"], rungs), "",
           "Tracker proxies (informational; ceiling probe is REPORT-ONLY, D13):", table(["proxy", "|Spearman(psi, proxy)| test", "linear probe R² test"], inf), "",
           "Caveats: 10 clips; friction decays any energy-like quantity within a clip; the ICC is a statistic over 10 release means; the proxy is not the conserved energy."]
    open("results/real/REPORT.md", "w").write("\n".join(txt) + "\n")
    return "real report written", [], []


if __name__ == "__main__":
    print(dict(handshake=handshake, hier=hier, real=real)[sys.argv[1]]()[0])
