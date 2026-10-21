"""Re-check, from the raw run files, the three claims in docs/ENCODER_GENERALITY_REPORT.md (criteria section):
  1. presence of each true block is measured before judging splitting;
  2. no rung with block presence below 0.95 split, and almost all at or above 0.95 did;
  3. a rung splits when its block presence is at least 0.95 AND the previous rung split.
Counts are recomputed here from the stored presence values and the frozen B1 criteria; also with the linear probe instead of the nonlinear one.
    python experiments/verify_claims.py -> results/enc_generality/VERIFY_CLAIMS.md"""
import glob, json
import yaml
from isj.stage_b1 import seed_checks

crit = yaml.safe_load(open("configs/stage_b1.yaml"))["criteria"]
DIRS = ["results/stage_b1_e25", "results/stage_b1_e26", "results/stage_b1_e27/mirror_lejepa", "results/stage_b1_e27/mirror_predict",
        "results/stage_b1_e27/mlp_lejepa", "results/stage_b1_e28", "results/stage_b1_e29", "results/stage_b1_e30/A", "results/stage_b1_e30/B"]
runs = [json.load(open(f)) for d in DIRS for f in sorted(glob.glob(d + "/main_seed*.json"))]
md = [f"# Re-check of the criteria claims (E25-E30 run files, {len(runs)} runs)\n"]
missing = [r["seed"] for r in runs if "presence" not in r]
md.append(f"**Claim 1 (presence is measured):** {len(runs) - len(missing)} of {len(runs)} run files carry a `presence` field (nonlinear and linear probe, three blocks each).\n")
for probe in ("mlp", "linear"):
    rows = []
    for r in runs:
        c = seed_checks(r, crit)
        s = [c[f"rung{k}_angle"] and c[f"rung{k}_variant_r2"] and c[f"rung{k}_gap"] for k in (1, 2)]
        rows += [(r["presence"][probe][k], s[k], s[0] if k == 1 else True, k) for k in (0, 1)]
    ge = [x for x in rows if x[0] >= 0.95]; lt = [x for x in rows if x[0] < 0.95]
    cond = sum(((x[0] >= 0.95) and x[2]) == x[1] for x in rows); unc = sum((x[0] >= 0.95) == x[1] for x in rows)
    md += [f"## Probe: {'nonlinear (two-layer network)' if probe == 'mlp' else 'linear'}\n",
           f"- **Claim 2:** rungs below 0.95 that split: **{sum(x[1] for x in lt)} of {len(lt)}**; rungs at or above 0.95 that split: **{sum(x[1] for x in ge)} of {len(ge)}**.",
           f"- **Claim 3:** rule 'presence at least 0.95 and previous rung split' agrees with the outcome on **{cond} of {len(rows)}** rungs; presence alone agrees on {unc} of {len(rows)}.",
           f"- Rungs at or above 0.95 whose previous rung had failed: {sum(1 for x in ge if not x[2])}; of these, split: {sum(1 for x in ge if not x[2] and x[1])}.",
           f"- Rungs at or above 0.95 whose previous rung split (or rung 1): {sum(1 for x in ge if x[2])}; of these, split: {sum(1 for x in ge if x[2] and x[1])}.\n"]
open("results/enc_generality/VERIFY_CLAIMS.md", "w").write("\n".join(md)); print("\n".join(md))
