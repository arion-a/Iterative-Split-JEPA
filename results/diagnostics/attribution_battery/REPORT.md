# Attribution battery: E15, E16, E17 (clean B2 world, 3 seeds; decomposition numbers informational)

## E15: linear probe from the FULL encoder features to the true texture block, before any split

The recovered texture block reproduces the pipeline run exactly (same variant R² on every seed). Decision rule: probe ≥ 0.95 -> split loses texture; probe < 0.9 -> encoder never encoded texture; 0.9-0.95 not covered.

| Seed | Full-feature texture probe R² | Recovered texture block R² | Lost by the split (probe − block) | Lost before the split (1 − probe) | Rule says | Probe R² per texture dimension | Probe R² identity / category |
|---|---|---|---|---|---|---|---|
| 0 | 0.8938 | 0.8623 | 0.0315 | 0.1062 | encoder (<0.9) | 0.94 / 0.81 / 0.92 / 0.91 | 0.950 / 0.971 |
| 1 | 0.9073 | 0.8871 | 0.0202 | 0.0927 | not covered by the rule (0.9-0.95) | 0.96 / 0.92 / 0.87 / 0.87 | 0.950 / 0.974 |
| 2 | 0.9303 | 0.8965 | 0.0338 | 0.0697 | not covered by the rule (0.9-0.95) | 0.94 / 0.91 / 0.95 / 0.92 | 0.931 / 0.966 |

Means: probe 0.910, recovered block 0.882. Of the 0.118 shortfall from 1.0, 0.090 (76%) is already present in the full-feature probe (the encoder side) and 0.028 (24%) is lost by taking the 4-direction block. The prediction (probe at about 0.88-0.93, below 0.95 on every seed) holds. Texture is the weakest block in the probe (identity 0.93-0.95, category 0.97).

## E16: is the texture discrete-valued per identity?

No. Two centres per identity, each a random 4-D vector, plus Gaussian jitter in all four dimensions; across the 240 centres all four directions vary (covariance eigenvalues 1.21 / 1.13 / 1.07 / 1.00). The world is not the cause of a one-direction texture block; no regeneration was run (see `docs/EVIDENCE.md`, E16).

## E17: leakage gate re-referenced (frozen in `configs/gates_v2.yaml`, threshold 0.0209 on normalized ||A21||_F)

Retrospective, on existing runs only (the gate applies from the next run on):

| Arm (rung 2) | seed 0 | seed 1 | seed 2 | Gate 0.0209 |
|---|---|---|---|---|
| B1 arm (generator twins) | 0.0157 | 0.0225 | 0.0223 | met on 1 of 3 |
| B2 untreated | 0.1072 | 0.0617 | 0.0496 | met on 0 of 3 |
| B2 + Tier 1 | 0.0211 | 0.0264 | 0.0281 | met on 0 of 3 |
| Rung 1 (same encoders) | 0.0461 | 0.0385 | 0.0319 | met on 0 of 3 |

For reference, the retired post-hoc gate's quantity (largest off-diagonal |R²|, old limit 0.01), now informational:

| Arm (rung 2) | seed 0 | seed 1 | seed 2 |
|---|---|---|---|
| B1 arm (generator twins) | 0.0215 | 0.0180 | 0.0324 |
| B2 untreated | 0.0362 | 0.0276 | 0.0333 |
| B2 + Tier 1 | 0.0218 | 0.0197 | 0.0344 |

## Decomposition (informational): where the angles come from, per seed

| Seed | Inherited θ(H₁, H₁*), span truth (°) | Inherited, complement truth (°) | Nesting, span truth (°) | Nesting, complement truth (°) | Rung 2's own error given the true H₁* (°) | Rung-2 angle, B1 arm (°) | Rung-2 angle, B2 + Tier 1 (°) |
|---|---|---|---|---|---|---|---|
| 0 | 12.86 | 4.59 | 10.99 | 3.37 | 1.42 | 10.68 | 10.71 |
| 1 | 10.69 | 3.62 | 8.48 | 2.28 | 2.08 | 8.63 | 8.61 |
| 2 | 13.61 | 3.12 | 11.48 | 2.79 | 1.95 | 11.58 | 11.60 |

(Rung 2's own error is from the nesting diagnostics, `results/diagnostics/nesting/`, same seeds and encoders.)