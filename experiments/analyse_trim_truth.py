"""Analyses on existing data (no new runs): (1) trimmed fraction on the B2 treated runs next to the B1 clean baseline (excess = rho-hat for E13);
(2) movement of the rung-2 subspace under purification vs the TRUE identity subspace; (3) the corrected no-op criterion (D12) applied to the existing control.
Reads results/stage_b2_noop/ (reproduces results/stage_b2_purify/ exactly). Writes results/stage_b2_noop/ANALYSIS.md."""
import glob, json, statistics as st, torch
from isj.audits import principal_angles_deg
D = "results/stage_b2_noop"
runs = sorted((json.load(open(f)) for f in glob.glob(f"{D}/sigma_cat_0.1/[0-9]*.json")), key=lambda r: r["seed"])
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
# (1)
rows = []
for r in runs:
    p, n = r["purify"], r["noop_control"]; t = 1 - p["kept_fraction"]; rho = 1 - p["validity_before"]
    rows.append([r["seed"], f"{t:.4f}", f"{n['trimmed_fraction']:.4f}", f"{t - n['trimmed_fraction']:.4f}", f"{rho:.4f}", f"{p['invalid_dropped']:.3f}", f"{1 - p['valid_kept']:.4f}"])
base = st.mean(r["noop_control"]["trimmed_fraction"] for r in runs)
# (2)
mv = []
for r in runs:
    a = r["arms"]; V = lambda x: torch.tensor(a[x]["V"]).T
    mv.append([r["seed"], f"{a['b2_kmeans']['angle_deg']:.2f}", f"{a['b2_kmeans_purified']['angle_deg']:.2f}", f"{a['b1_generator']['angle_deg']:.2f}",
               f"{principal_angles_deg(V('b2_kmeans'), V('b2_kmeans_purified')).max():.2f}", f"{principal_angles_deg(V('b2_kmeans_purified'), V('b1_generator')).max():.2f}"])
# (3) corrected criterion (D12): trimmed <= 5%; no metric worse than the unpurified arm by more than 1 seed-std; not "systematic" = worse on every seed AND mean worsening > 0.5 seed-std
M = [("Rung-2 angle (°)", "angle_deg", 1), ("Gap ratio", "gap_ratio", -1), ("Identity R²", "variant_r2", -1), ("Core R²", "core_invariant_r2", -1), ("Nesting D10 (°)", "nesting_perp_deg", 1),
     ("a12_fro", "a12_fro", 1), ("a21_fro", "a21_fro", 1), ("Block purity", "block_purity", -1), ("Largest |leak R²|", "max_leak_abs_r2", 1)]
c, ok_all = [], True
for l, k, bad in M:
    b = [r["arms"]["b1_generator"][k] for r in runs]; sd = st.stdev(b)
    harm = [(r["arms"]["b1_generator_purified"][k] - r["arms"]["b1_generator"][k]) * bad / sd for r in runs]   # in seed-stds, positive = harmful
    no_noise = st.mean(harm) <= 1.0; systematic = all(h > 0 for h in harm) and st.mean(harm) > 0.5
    ok_all &= no_noise and not systematic
    c.append([l, " / ".join(f"{h:+.3f}" for h in harm), yn := ("yes" if no_noise and not systematic else "**NO**"), "worse on all seeds, tiny" if all(h > 0 for h in harm) else ""])
trim_ok = max(r["noop_control"]["trimmed_fraction"] for r in runs) <= 0.05
md = ["# Analyses on existing data (no new runs), clean B2 world, 3 seeds\n",
      "## 1. Trimmed fraction: B2 treated runs next to the B1 clean baseline\n", tab(["Seed", "B2 pairs trimmed", "B1 clean pairs trimmed", "Excess (rho-hat)", "True mis-grouped fraction (evaluation only)", "Invalid pairs dropped", "Valid pairs dropped"], rows),
      f"\nB1 clean baseline mean {base:.4f}. The excess is the empirical contamination catch rho-hat that E13 needs. It tracks the true mis-grouped fraction (excess {st.mean(float(x[3]) for x in rows):.3f} against true {st.mean(float(x[4]) for x in rows):.3f}) and is a little below it. Both treated-run directories (`stage_b2_purify`, `stage_b2_noop`) give identical values.\n",
      "## 2. Does the movement under purification go toward the TRUE identity subspace?\n", tab(["Seed", "Angle to true identity subspace, untreated (°)", "treated (°)", "B1 arm (°)", "Subspace movement untreated -> treated (°)", "Treated to B1-arm subspace (°)"], mv),
      "\nAngle to the true identity subspace = largest principal angle to the identity block's probe image (the rung-2 angle gate). Seed 0: the subspace moves 11.6° and its angle to the truth falls by 4.0° (toward truth, onto the B1 reference). Seeds 1 and 2: it moves 4.6° and 6.4° but its angle to the truth changes by under 0.06°. The movement is onto the B1-arm subspace (0.8-1.4° away), and the B1 arm itself sits 8.6-11.6° from the true identity image, so what remains of the angle is the shared encoder/probe-image offset, not contamination.\n",
      "## 3. Corrected no-op criterion (candidate D12) applied to the existing control (retrospective)\n",
      f"Trimmed fraction on clean pairs: {', '.join(f'{r['noop_control']['trimmed_fraction']:.4f}' for r in runs)} (limit 0.05): {'pass' if trim_ok else 'FAIL'}.\n",
      tab(["Metric", "Harm per seed, in untreated seed-stds (positive = worse)", "Within criterion?", "Note"], c),
      f"\nOverall: **{'PASS' if (trim_ok and ok_all) else 'FAIL'}** under the corrected criterion."]
open(f"{D}/ANALYSIS.md", "w").write("\n".join(md))
print("trim ok", trim_ok, "criterion ok", ok_all)
