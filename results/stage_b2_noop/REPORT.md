# E14 and no-op control: Tier 1 purification, clean world (sigma_cat 0.1), 3 seeds

Untreated and treated arms reproduce the E12 run exactly: yes.

**E14 verdict:** CONFIRMED (criterion: no metric worse than untreated by more than 1 untreated seed-std; fixed in docs/EVIDENCE.md after the E10a numbers were seen, so not blind).

**No-op control verdict:** strict reading (nothing trimmed, results identical): **FAIL**. Practical reading (≤ 2% trimmed, every metric within one seed-std of the unpurified B1 arm): **FAIL**. Which reading is the gate is the owner's call.

## E14: treated vs untreated B2 arm (means over 3 seeds)

| Treated arm | Metric | Untreated | Treated | Δ | Untreated seed-std | Direction | No damage? |
|---|---|---|---|---|---|---|---|
| b2_kmeans_purified | Rung-2 angle (°) | 11.684 ± 3.040 | 10.304 ± 1.535 | -1.3799 | 3.0399 | better | yes |
| b2_kmeans_purified | Identity R² | 0.915 ± 0.012 | 0.920 ± 0.018 | +0.0051 | 0.0124 | better | yes |
| b2_kmeans_purified | Category core R² | 0.965 ± 0.006 | 0.970 ± 0.004 | +0.0048 | 0.0058 | better | yes |
| b2_kmeans_purified | Nesting, D10 reference (°) | 2.816 ± 0.546 | 2.806 ± 0.490 | -0.0105 | 0.5461 | better | yes |
| b2_kmeans_purified | Nesting, absolute (°) (informational) | 10.313 ± 1.611 | 10.218 ± 1.574 | -0.0951 | 1.6108 | better | yes |
| b2_kmeans_purified | Block purity | 0.981 ± 0.004 | 0.987 ± 0.003 | +0.0059 | 0.0044 | better | yes |
| b2_kmeans_purified | a12_fro | 0.344 ± 0.026 | 0.305 ± 0.042 | -0.0387 | 0.0256 | better | yes |
| b2_kmeans_purified_whitened | Rung-2 angle (°) | 11.684 ± 3.040 | 10.548 ± 1.647 | -1.1353 | 3.0399 | better | yes |
| b2_kmeans_purified_whitened | Identity R² | 0.915 ± 0.012 | 0.919 ± 0.016 | +0.0037 | 0.0124 | better | yes |
| b2_kmeans_purified_whitened | Category core R² | 0.965 ± 0.006 | 0.969 ± 0.004 | +0.0039 | 0.0058 | better | yes |
| b2_kmeans_purified_whitened | Nesting, D10 reference (°) | 2.816 ± 0.546 | 2.788 ± 0.498 | -0.0280 | 0.5461 | better | yes |
| b2_kmeans_purified_whitened | Nesting, absolute (°) (informational) | 10.313 ± 1.611 | 10.273 ± 1.620 | -0.0404 | 1.6108 | better | yes |
| b2_kmeans_purified_whitened | Block purity | 0.981 ± 0.004 | 0.986 ± 0.002 | +0.0044 | 0.0044 | better | yes |
| b2_kmeans_purified_whitened | a12_fro | 0.344 ± 0.026 | 0.318 ± 0.032 | -0.0260 | 0.0256 | better | yes |

### Position: largest angle between the untreated and the treated rung-2 variant subspace (°)

| Seed | Tier 1 | Tier 1 + Tier 4 |
|---|---|---|
| 0 | 11.57 | 7.35 |
| 1 | 4.61 | 3.55 |
| 2 | 6.37 | 4.11 |

## No-op control: Tier 1 on B1's clean generator-twin pairs

| Seed | Pairs | Trimmed | Trimmed fraction | Iterations |
|---|---|---|---|---|
| 0 | 30000 | 684 | 0.0228 | 5 |
| 1 | 30000 | 739 | 0.0246 | 4 |
| 2 | 30000 | 1020 | 0.0340 | 5 |


| Metric | B1 arm, unpurified | B1 arm, Tier 1 | Largest per-seed change |
|---|---|---|---|
| Rung-2 angle (°) | 10.297 ± 1.513 | 10.294 ± 1.513 | 0.0038 |
| Gap ratio, rung 2 | 27.325 ± 4.572 | 30.151 ± 4.323 | 3.2152 |
| Identity R² | 0.922 ± 0.017 | 0.921 ± 0.017 | 0.0006 |
| Category core R² | 0.970 ± 0.004 | 0.970 ± 0.004 | 0.0000 |
| Nesting, D10 reference (°) | 2.799 ± 0.484 | 2.798 ± 0.485 | 0.0052 |
| a21_fro | 0.040 ± 0.008 | 0.039 ± 0.006 | 0.0045 |

## E14 per seed: untreated -> Tier 1, with position against the clean B1-arm subspace (°)

| Seed | Rung-2 angle (°) | Identity R² | Core R² | Nesting D10 (°) | Gap ratio | Angle to B1-arm subspace |
|---|---|---|---|---|---|---|
| 0 | 14.74 -> 10.71 | 0.919 -> 0.930 | 0.961 -> 0.970 | 3.37 -> 3.27 | 2.7 -> 19.2 | 11.85 -> 0.76 |
| 1 | 8.66 -> 8.61 | 0.926 -> 0.932 | 0.972 -> 0.973 | 2.28 -> 2.29 | 2.7 -> 22.2 | 5.17 -> 0.90 |
| 2 | 11.65 -> 11.60 | 0.902 -> 0.900 | 0.963 -> 0.966 | 2.79 -> 2.86 | 3.9 -> 17.6 | 6.97 -> 1.41 |

Treated subspace closer to the clean B1 subspace on every seed: yes.