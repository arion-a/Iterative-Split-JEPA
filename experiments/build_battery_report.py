"""Attribution battery report (E15, E16, E17) from existing data and results/diagnostics/e15/. Decomposition numbers are informational."""
import glob, json, statistics as st
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
ms = lambda v, nd=3: f"{st.mean(v):.{nd}f} ± {st.stdev(v):.{nd}f}"
e15 = [json.load(open(f"results/diagnostics/e15/seed{s}.json")) for s in range(3)]
runs = [json.load(open(f"results/stage_b2_noop/sigma_cat_0.1/{s}.json")) for s in range(3)]
diag = [json.load(open(f"results/diagnostics/nesting/b2world_seed{s}.json")) for s in range(3)]
GATE = 0.0209
def branch(p): return "encoder (<0.9)" if p < 0.9 else ("split (>=0.95)" if p >= 0.95 else "not covered by the rule (0.9-0.95)")
rows = [[d["seed"], f"{d['full_feature_probe_r2']['texture']:.4f}", f"{d['recovered_texture_block_r2']:.4f}", f"{d['full_feature_probe_r2']['texture'] - d['recovered_texture_block_r2']:.4f}",
         f"{1 - d['full_feature_probe_r2']['texture']:.4f}", branch(d["full_feature_probe_r2"]["texture"]),
         " / ".join(f"{x:.2f}" for x in d["full_feature_probe_r2_per_texture_dim"]), f"{d['full_feature_probe_r2']['identity']:.3f} / {d['full_feature_probe_r2']['category']:.3f}"] for d in e15]
mp = st.mean(d["full_feature_probe_r2"]["texture"] for d in e15); mr = st.mean(d["recovered_texture_block_r2"] for d in e15)
dec = [[r["seed"], f"{r['rung1']['inherited_span_deg']:.2f}", f"{r['rung1']['inherited_perp_deg']:.2f}", f"{r['arms']['b2_kmeans']['nesting_angle_deg']:.2f}", f"{r['arms']['b2_kmeans']['nesting_perp_deg']:.2f}",
        f"{dg['intrinsic_recovery_deg']:.2f}", f"{r['arms']['b1_generator']['angle_deg']:.2f}", f"{r['arms']['b2_kmeans_purified']['angle_deg']:.2f}"] for r, dg in zip(runs, diag)]
arms = [("B1 arm (generator twins)", "b1_generator"), ("B2 untreated", "b2_kmeans"), ("B2 + Tier 1", "b2_kmeans_purified")]
lk = [[n] + [f"{r['arms'][a]['a21_norm']:.4f}" for r in runs] + [("met on " + str(sum(r['arms'][a]['a21_norm'] < GATE for r in runs)) + " of 3")] for n, a in arms]
lk.append(["Rung 1 (same encoders)"] + [f"{r['rung1']['a21_norm']:.4f}" for r in runs] + ["met on " + str(sum(r['rung1']['a21_norm'] < GATE for r in runs)) + " of 3"])
old = [[n] + [f"{r['arms'][a]['max_leak_abs_r2']:.4f}" for r in runs] for n, a in arms]
md = ["# Attribution battery: E15, E16, E17 (clean B2 world, 3 seeds; decomposition numbers informational)\n",
      "## E15: linear probe from the FULL encoder features to the true texture block, before any split\n",
      f"The recovered texture block reproduces the pipeline run exactly (same variant R² on every seed). Decision rule: probe ≥ 0.95 -> split loses texture; probe < 0.9 -> encoder never encoded texture; 0.9-0.95 not covered.\n",
      tab(["Seed", "Full-feature texture probe R²", "Recovered texture block R²", "Lost by the split (probe − block)", "Lost before the split (1 − probe)", "Rule says", "Probe R² per texture dimension", "Probe R² identity / category"], rows),
      f"\nMeans: probe {mp:.3f}, recovered block {mr:.3f}. Of the {1 - mr:.3f} shortfall from 1.0, {1 - mp:.3f} ({(1 - mp) / (1 - mr):.0%}) is already present in the full-feature probe (the encoder side) and {mp - mr:.3f} ({(mp - mr) / (1 - mr):.0%}) is lost by taking the 4-direction block. The prediction (probe at about 0.88-0.93, below 0.95 on every seed) holds. Texture is the weakest block in the probe (identity 0.93-0.95, category 0.97).\n",
      "## E16: is the texture discrete-valued per identity?\n",
      "No. Two centres per identity, each a random 4-D vector, plus Gaussian jitter in all four dimensions; across the 240 centres all four directions vary (covariance eigenvalues 1.21 / 1.13 / 1.07 / 1.00). The world is not the cause of a one-direction texture block; no regeneration was run (see `docs/EVIDENCE.md`, E16).\n",
      "## E17: leakage gate re-referenced (frozen in `configs/gates_v2.yaml`, threshold 0.0209 on normalized ||A21||_F)\n",
      "Retrospective, on existing runs only (the gate applies from the next run on):\n", tab(["Arm (rung 2)", "seed 0", "seed 1", "seed 2", "Gate 0.0209"], lk),
      "\nFor reference, the retired post-hoc gate's quantity (largest off-diagonal |R²|, old limit 0.01), now informational:\n", tab(["Arm (rung 2)", "seed 0", "seed 1", "seed 2"], old),
      "\n## Decomposition (informational): where the angles come from, per seed\n",
      tab(["Seed", "Inherited θ(H₁, H₁*), span truth (°)", "Inherited, complement truth (°)", "Nesting, span truth (°)", "Nesting, complement truth (°)", "Rung 2's own error given the true H₁* (°)", "Rung-2 angle, B1 arm (°)", "Rung-2 angle, B2 + Tier 1 (°)"], dec),
      "\n(Rung 2's own error is from the nesting diagnostics, `results/diagnostics/nesting/`, same seeds and encoders.)"]
import os; os.makedirs("results/diagnostics/attribution_battery", exist_ok=True)
open("results/diagnostics/attribution_battery/REPORT.md", "w").write("\n".join(md))
print("\n".join(md[2:6]))
