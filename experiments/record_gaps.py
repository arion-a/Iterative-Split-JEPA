"""Mechanical outcome of the G study (decision-rule verdicts S1-S4 per system, D1-D3) into EVIDENCE, STATUS, a report and the chain. Idempotent."""
import glob, json

import numpy as np
import yaml

from isj import explog

ev = open("docs/EVIDENCE.md").read()
if "### G outcome" in ev:
    print("already recorded"); raise SystemExit(0)
cfg = yaml.safe_load(open("configs/gaps.yaml")); c = cfg["criteria"]; cs, cd = c["systems"], c["depth"]
rows, verdicts, lines = [], {}, []
for name in cfg["systems"]:
    g = json.load(open(f"data/{name}_full/grouping_check.json")); rs = [json.load(open(p)) for p in sorted(glob.glob(f"results/system_{name}/[0-9].json"))]
    nm = [r["arms"]["main"]["naming_abs_spearman"] for r in rs]; fl = [r["arms"]["flat"]["naming_abs_spearman"] for r in rs]; st = list(rs[0]["seed_agreement"].values())
    s1 = g["contrast_by_period"][str(g["best_period"])] >= cs["grouping_min_contrast"]; s2 = all(v >= cs["naming_min"] for v in nm)
    s3 = all(a - b >= cs["main_minus_flat_min"] for a, b in zip(nm, fl)); s4 = all(v >= cs["seed_agreement_min"] for v in st)
    verdicts[name] = dict(S1=s1, S2=s2, S3=s3, S4=s4)
    corr = {k: round(float(np.mean([r["arms"]["main"]["abs_spearman_with"][k] for r in rs])), 3) for k in rs[0]["arms"]["main"]["abs_spearman_with"]}
    lines.append(f"* **{name}** (period {g['best_period']} clips per video, {rs[0]['n_videos']} videos, split {rs[0]['split_sizes']}): S1 grouping {'met' if s1 else 'not met'} (contrast {g['contrast_by_period'][str(g['best_period'])]:.2f}); S2 naming {'met' if s2 else 'not met'} {[round(v,3) for v in nm]}; S3 main minus flat {'met' if s3 else 'not met'} (flat {[round(v,3) for v in fl]}); S4 agreement {'met' if s4 else 'not met'} {[round(v,3) for v in st]}. Informational |Spearman| of psi with each tracked quantity (mean over seeds): {corr}. Shuffled arm {[round(r['arms']['shuffled']['naming_abs_spearman'],3) for r in rs]}, temporal-only {[round(r['arms']['temporal_only']['naming_abs_spearman'],3) for r in rs]}; energy reliability across test videos {rs[0]['energy_between_video_icc_test']:.3f}.")
    rows.append([name, nm, fl, st, verdicts[name]])
ds = [json.load(open(p)) for p in sorted(glob.glob("results/depth/[0-9].json"))]
lc = [r["arms"]["ladder"]["cuts"] for r in ds]; sc = [r["arms"]["single_lag"]["cuts"] for r in ds]; shc = [r["arms"]["shuffled"]["cuts"] for r in ds]
d1 = all(n == cd["expected_cuts"] and all(p["variant_r2"] >= cd["block_r2_min"] and p["invariant_r2"] >= cd["block_r2_min"] and p["best_ratio"] >= cd["best_ratio_min"] for p in r["arms"]["ladder"]["per_rung"]) for r, n in zip(ds, lc))
d2 = all(n <= cd["single_lag_max_cuts"] for n in sc); d3 = all(n == cd["shuffled_cuts"] for n in shc)
verdicts["depth"] = dict(D1=d1, D2=d2, D3=d3)
ratios = [[round(p["best_ratio"], 1) for p in r["arms"]["ladder"]["per_rung"]] for r in ds]
r2v = [[round(min(p["variant_r2"], p["invariant_r2"]), 3) for p in r["arms"]["ladder"]["per_rung"]] for r in ds]
lines.append(f"* **depth world** (a = 0.1, 0.9, 0.99, 0.999): D1 ladder cuts {lc} with best ratios {ratios} and min(variant, invariant R²) {r2v}: {'met' if d1 else 'not met'}; D2 single-lag cuts {sc} (≤ 2): {'met' if d2 else 'not met'}; D3 shuffled cuts {shc} (= 0): {'met' if d3 else 'not met'}.")
allok = all(v for d in verdicts.values() for v in d.values())
text = f"\n### G outcome (2026-10-21), `results/system_*`, `results/depth`: **{'CONFIRMED' if allok else 'NOT CONFIRMED (refuted as worded)'}**\n" + "\n".join(lines) + "\n"
open("docs/EVIDENCE.md", "a").write(text)
rep = ["# Stage V gap-closing report (G2, G3)", "", "Criteria frozen in `configs/gaps.yaml`; predictions in `docs/EVIDENCE.md` (G1-G3).", ""] + lines
open("results/depth/REPORT.md", "w").write("\n".join(rep) + "\n")
open("docs/STATUS.md", "a").write("\n| - | **Stage V gap study G2/G3 (2026-10-21)** | single and elastic pendulum (Columbia, real) and a depth world | " + ("confirmed" if allok else "not confirmed") + f": systems {json.dumps({k: v for k, v in verdicts.items() if k != 'depth'})}, depth {json.dumps(verdicts['depth'])} | `results/depth/REPORT.md` |\n")
explog.append("result", f"G study finished: {'confirmed' if allok else 'not confirmed'}; verdicts {json.dumps(verdicts)}.", stage="V", step="G-outcome", how="experiments/record_gaps.py after the supervised runs",
              artifact_paths=["results/depth/REPORT.md"], outputs={"verdicts": verdicts, "ladder_cuts": lc, "single_lag_cuts": sc, "shuffled_cuts": shc}, verdict="confirmed" if allok else "not confirmed")
print("recorded", allok, verdicts)
