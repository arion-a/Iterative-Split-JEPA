"""Append the mechanical C2 outcome (decision-rule verdicts per prediction (a)-(d)) to docs/EVIDENCE.md, docs/STATUS.md and the chain. Idempotent."""
import glob, json

import yaml

from isj import explog

ev = open("docs/EVIDENCE.md").read()
if "### C2 outcome" in ev:
    print("already recorded"); raise SystemExit(0)
c = yaml.safe_load(open("configs/columbia_full.yaml"))["criteria"]; cert = c["certificate"]
runs = [json.load(open(p)) for p in sorted(glob.glob("results/columbia_full/[0-9].json"))]
m = lambda k, a="main": [round(r["arms"][a][k], 3) for r in runs]
stab = [round(v, 3) for v in runs[0]["seed_agreement"].values()]
a_ok = all(v <= cert["V_max"] for v in m("V")) and all(v >= cert["icc_min"] for v in m("icc")) and all(v <= cert["L_max"] for v in m("L")) and all(v <= cert["rollout_nmse_max"] for v in m("rollout_nmse"))
b_ok = all(v >= c["naming"]["spearman_min"] for v in m("naming_abs_spearman"))
c_ok = all(v < c["controls"]["flat_max_abs_spearman"] for v in m("naming_abs_spearman", "flat"))
d_ok = all(v >= c["stability"]["min_abs_spearman"] for v in stab)
word = lambda ok: "met" if ok else "not met"
allok = a_ok and b_ok and c_ok and d_ok
text = f"""
### C2 outcome (2026-10-21), `results/columbia_full/*.json`, report `results/columbia_full/REPORT.md`: **{'CONFIRMED' if allok else 'NOT CONFIRMED (refuted as worded)'}**
(a) certificate {word(a_ok)}: V {m('V')}, ICC {m('icc')}, L {m('L')}, rollout {m('rollout_nmse')}. (b) naming {word(b_ok)}: {m('naming_abs_spearman')} (≥ 0.5). (c) flat control {word(c_ok)}: {m('naming_abs_spearman','flat')} (< 0.5). (d) seed agreement {word(d_ok)}: {stab} (≥ 0.9).
Informational: shuffled-pair arm {m('naming_abs_spearman','shuffled')}, temporal-only arm {m('naming_abs_spearman','temporal_only')}; tracked-energy reliability across test videos {runs[0]['tracked_energy_between_video_icc_test']:.3f}; ceiling probe R² (report-only) {[round(r['ceiling_probe_report_only_r2_test'], 3) for r in runs]}.
"""
open("docs/EVIDENCE.md", "a").write(text)
open("docs/STATUS.md", "a").write(f"\n| - | **Stage V C2 Columbia full (2026-10-21)** | 100 videos, video-level split 70/10/20, 3 seeds, 8000 steps | {'confirmed' if allok else 'not confirmed'}: (a) {word(a_ok)}, (b) naming {m('naming_abs_spearman')}, (c) flat {m('naming_abs_spearman','flat')}, (d) agreement {stab} | `results/columbia_full/REPORT.md` |\n")
explog.append("result", f"C2 Columbia full experiment finished: {'confirmed' if allok else 'not confirmed'} ((a) {word(a_ok)}, (b) {word(b_ok)}, (c) {word(c_ok)}, (d) {word(d_ok)}).", stage="V", step="S3.2",
              how="experiments/run_columbia_full.py via the supervisor; report experiments/build_report.py columbia_full", artifact_paths=["results/columbia_full/REPORT.md"],
              outputs={"a":a_ok,"b":b_ok,"c":c_ok,"d":d_ok,"naming":m("naming_abs_spearman"),"flat":m("naming_abs_spearman","flat"),"seed_agreement":stab}, verdict="confirmed" if allok else "not confirmed")
print("recorded", allok)
