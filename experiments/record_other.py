"""Mechanical outcome of H1 and R1 (verdicts H-a..H-d, R-a..R-c) into EVIDENCE, STATUS, a report and the chain. Idempotent."""
import glob, json

import numpy as np
import yaml

from isj import explog

ev = open("docs/EVIDENCE.md").read()
if "### H1/R1 outcome" in ev:
    print("already recorded"); raise SystemExit(0)
cfg = yaml.safe_load(open("configs/other_data.yaml")); ch, cr = cfg["criteria"]["hf_pendulum"], cfg["criteria"]["robot"]
hs = [json.load(open(p)) for p in sorted(glob.glob("results/hf_pendulum/[0-9].json"))]
nm = [r["arms"]["main"]["naming_abs_spearman"] for r in hs]; fl = [r["arms"]["flat"]["naming_abs_spearman"] for r in hs]
li = [r["arms"]["main"]["abs_spearman_with"]["light_angle"] for r in hs]; st = list(hs[0]["seed_agreement"].values())
ha = all(v >= ch["naming_min"] for v in nm); hb = all(a - b >= ch["main_minus_flat_min"] for a, b in zip(nm, fl)); hc = all(v < ch["nuisance_max_abs_spearman"] for v in li); hd = all(v >= ch["seed_agreement_min"] for v in st)
rs = [json.load(open(p)) for p in sorted(glob.glob("results/robot/[0-9].json"))]
g = lambda f, t: [round(r["r2"][f][t], 3) for r in rs]
ra = all(r["r2"]["core"]["cube0"] >= cr["core_cube0_r2_min"] for r in rs)
rb = all(r["r2"]["core"]["cube0"] - r["r2"]["flat_top_pcs"]["cube0"] >= cr["core_minus_flat_min"] for r in rs)
rc = all(r["r2"]["variant"]["tcp"] - r["r2"]["core"]["tcp"] >= cr["variant_minus_core_tcp_min"] for r in rs)
ver = dict(Ha=ha, Hb=hb, Hc=hc, Hd=hd, Ra=ra, Rb=rb, Rc=rc); allok = all(ver.values())
w = lambda ok: "met" if ok else "not met"
corr = {k: round(float(np.mean([r["arms"]["main"]["abs_spearman_with"][k] for r in hs])), 3) for k in hs[0]["arms"]["main"]["abs_spearman_with"]}
lines = [f"* **H1 HF controlled pendulum** (test = 40 provided val videos): H-a naming {w(ha)} {[round(v,3) for v in nm]}; H-b main minus flat {w(hb)} (flat {[round(v,3) for v in fl]}); H-c |Spearman| with the controlled light angle {w(hc)} {[round(v,3) for v in li]} (< 0.3); H-d seed agreement {w(hd)} {[round(v,3) for v in st]}. Correlations of psi with every label (mean over seeds): {corr}. Shuffled {[round(r['arms']['shuffled']['naming_abs_spearman'],3) for r in hs]}, temporal-only {[round(r['arms']['temporal_only']['naming_abs_spearman'],3) for r in hs]}; stop {[r['stop'] for r in hs]}.",
         f"* **R1 ManiSkill PickCube** (held-out test episodes; core dim {[r['core_dim'] for r in rs]}, rendering-pair family outcome {[r['ladder'][0].get('stop','split') for r in rs]}): R-a core readout of the cube's initial position R² {g('core','cube0')} {w(ra)}; R-b flat top-PC readout {g('flat_top_pcs','cube0')}, difference ≥ 0.1 {w(rb)}; R-c tcp readout from the variant block {g('variant','tcp')} vs from the core {g('core','tcp')}, difference ≥ 0.2 {w(rc)}. Informational: goal (visible in the side view only) from the core {g('core','goal')}, from the full latent {g('full','goal')}; cube over time from the core {g('core','cube_t')}; arm joints from the core {g('core','qpos')}, from the variant block {g('variant','qpos')}."]
text = f"\n### H1/R1 outcome (2026-10-21), `results/hf_pendulum`, `results/robot`: **{'CONFIRMED' if allok else 'NOT CONFIRMED (refuted as worded)'}**\n" + "\n".join(lines) + "\n"
open("docs/EVIDENCE.md", "a").write(text)
open("results/robot/REPORT.md", "w").write("# Stage V other-data report (H1, R1)\n\nCriteria frozen in `configs/other_data.yaml`; predictions in `docs/EVIDENCE.md` (H1 and R1).\n\n" + "\n".join(lines) + "\n")
open("docs/STATUS.md", "a").write(f"\n| - | **Stage V H1/R1 other data (2026-10-21)** | HF controlled pendulum and ManiSkill PickCube | {'confirmed' if allok else 'not confirmed'}: {json.dumps(ver)} | `results/robot/REPORT.md` |\n")
explog.append("result", f"H1/R1 finished: {'confirmed' if allok else 'not confirmed'}; verdicts {json.dumps(ver)}.", stage="V", step="O-outcome", how="experiments/record_other.py after the supervised runs",
              artifact_paths=["results/robot/REPORT.md"], outputs={"verdicts": ver, "hf_naming": [round(v, 3) for v in nm], "hf_flat": [round(v, 3) for v in fl], "hf_light": [round(v, 3) for v in li], "robot_core_cube0": g("core", "cube0"), "robot_flat_cube0": g("flat_top_pcs", "cube0")},
              verdict="confirmed" if allok else "not confirmed")
print("recorded", allok, ver)
