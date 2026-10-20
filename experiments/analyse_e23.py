"""E23 analysis (generic MLP encoder in the B1 ladder, seeds 30-34); rules frozen in docs/EVIDENCE.md before the runs.
    python experiments/analyse_e23.py  -> results/stage_b1_e23/E23_REPORT.md
Same scorer and same amended leakage floor (0.01) as E21 Part A, so the two encoders are judged by one ruler."""
import glob, json, statistics as st
import yaml
from isj.stage_b1 import CRITERIA_KEYS, seed_checks

cfg = yaml.safe_load(open("configs/stage_b1.yaml")); crit = cfg["criteria"]; ctl = cfg["controls"]["must_fail"]["shuffled_rung2"]
L = lambda pat: sorted((json.load(open(f)) for f in glob.glob(pat)), key=lambda r: r["seed"])
M, S = L("results/stage_b1_e23/main_seed*.json"), L("results/stage_b1_e23/shuffled_rung2_seed*.json")
ms = lambda v, nd=2: f"{st.mean(v):.{nd}f} ± {st.stdev(v):.{nd}f}"
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
per, n = [], len(M)
for r in M:
    chk = seed_checks(r, crit)
    chk["leakage"] = max(abs(x) for rg in r["rungs"] for k, x in rg["leak_r2"].items() if k in ("rest->own", "own->rest")) < 0.01
    per.append(chk)
passes = {k: sum(p[k] for p in per) for k in CRITERIA_KEYS}
fail_seeds = {k: n - v for k, v in passes.items()}
ctl_ok = st.mean(r["rungs"][1]["angle_deg"] for r in S) > ctl["rung2_angle_min_deg"] and st.mean(r["rungs"][1]["gap_ratio"] for r in S) < ctl["rung2_gap_ratio_max"]
need = {k: passes[k] >= 4 for k in CRITERIA_KEYS if k != "rung1_variant_r2"}
refuted = sum(1 for k in CRITERIA_KEYS if fail_seeds[k] >= 2) >= 2
verdict = "CONFIRMED" if all(need.values()) and ctl_ok else ("REFUTED" if refuted else "NOT CONFIRMED, NOT REFUTED (see table)")
md = [f"# E23: generic MLP encoder in the B1 ladder, seeds 30-34 ({n} main runs, {len(S)} shuffled-control runs)\n",
      f"**E23 prediction (every criterion except possibly rung-1 variant R² on at least 4 of 5 seeds; shuffled control behaves): {verdict}.** "
      f"Refutation rule (two or more criteria each failing on two or more seeds): {'met' if refuted else 'not met'}. Shuffled control {'behaved' if ctl_ok else 'DID NOT behave'}.\n",
      "## Per-criterion seeds passing\n", tab(["Criterion", "Seeds passing", "Needs ≥ 4 of 5"], [[k, f"{passes[k]} of {n}", "n/a (excepted)" if k == "rung1_variant_r2" else ("yes" if passes[k] >= 4 else "NO")] for k in CRITERIA_KEYS]),
      "\n## Measured (main arm, mean ± std)\n", tab(["Quantity", "Value"], [["Rung 1 angle (°)", ms([r["rungs"][0]["angle_deg"] for r in M])], ["Rung 2 angle (°)", ms([r["rungs"][1]["angle_deg"] for r in M])],
      ["Texture R² (rung 1)", ms([r["rungs"][0]["variant_r2"] for r in M], 3)], ["Identity R² (rung 2)", ms([r["rungs"][1]["variant_r2"] for r in M], 3)],
      ["Gap ratio rung 1 / rung 2", f"{ms([r['rungs'][0]['gap_ratio'] for r in M], 1)} / {ms([r['rungs'][1]['gap_ratio'] for r in M], 1)}"],
      ["Nesting (gate definition, °)", ms([r["nesting_angle_deg"] for r in M])]]),
      "\n## Shuffled-pair control\n", tab(["Rung-2 angle (°)", "Rung-2 gap ratio"], [[ms([r["rungs"][1]["angle_deg"] for r in S], 1), ms([r["rungs"][1]["gap_ratio"] for r in S], 2)]])]
open("results/stage_b1_e23/E23_REPORT.md", "w").write("\n".join(md)); print("\n".join(md))
