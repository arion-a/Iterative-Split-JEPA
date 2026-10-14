# Analyses on existing data (no new runs), clean B2 world, 3 seeds

## 1. Trimmed fraction: B2 treated runs next to the B1 clean baseline

| Seed | B2 pairs trimmed | B1 clean pairs trimmed | Excess (rho-hat) | True mis-grouped fraction (evaluation only) | Invalid pairs dropped | Valid pairs dropped |
|---|---|---|---|---|---|---|
| 0 | 0.1814 | 0.0228 | 0.1586 | 0.1696 | 1.000 | 0.0142 |
| 1 | 0.1815 | 0.0246 | 0.1568 | 0.1670 | 1.000 | 0.0174 |
| 2 | 0.1808 | 0.0340 | 0.1468 | 0.1654 | 0.985 | 0.0214 |

B1 clean baseline mean 0.0271. The excess is the empirical contamination catch rho-hat that E13 needs. It tracks the true mis-grouped fraction (excess 0.154 against true 0.167) and is a little below it. Both treated-run directories (`stage_b2_purify`, `stage_b2_noop`) give identical values.

## 2. Does the movement under purification go toward the TRUE identity subspace?

| Seed | Angle to true identity subspace, untreated (°) | treated (°) | B1 arm (°) | Subspace movement untreated -> treated (°) | Treated to B1-arm subspace (°) |
|---|---|---|---|---|---|
| 0 | 14.74 | 10.71 | 10.68 | 11.57 | 0.76 |
| 1 | 8.66 | 8.61 | 8.63 | 4.61 | 0.90 |
| 2 | 11.65 | 11.60 | 11.58 | 6.37 | 1.41 |

Angle to the true identity subspace = largest principal angle to the identity block's probe image (the rung-2 angle gate). Seed 0: the subspace moves 11.6° and its angle to the truth falls by 4.0° (toward truth, onto the B1 reference). Seeds 1 and 2: it moves 4.6° and 6.4° but its angle to the truth changes by under 0.06°. The movement is onto the B1-arm subspace (0.8-1.4° away), and the B1 arm itself sits 8.6-11.6° from the true identity image, so what remains of the angle is the shared encoder/probe-image offset, not contamination.

## 3. Corrected no-op criterion (candidate D12) applied to the existing control (retrospective)

Trimmed fraction on clean pairs: 0.0228, 0.0246, 0.0340 (limit 0.05): pass.

| Metric | Harm per seed, in untreated seed-stds (positive = worse) | Within criterion? | Note |
|---|---|---|---|
| Rung-2 angle (°) | +0.000 / -0.002 / -0.002 | yes |  |
| Gap ratio | -0.520 / -0.631 / -0.703 | yes |  |
| Identity R² | +0.018 / +0.016 / +0.035 | yes | worse on all seeds, tiny |
| Core R² | +0.004 / +0.002 / +0.007 | yes | worse on all seeds, tiny |
| Nesting D10 (°) | +0.004 / -0.001 / -0.011 | yes |  |
| a12_fro | +0.054 / +0.063 / +0.119 | yes | worse on all seeds, tiny |
| a21_fro | +0.136 / -0.054 / -0.578 | yes |  |
| Block purity | +0.065 / +0.066 / +0.140 | yes | worse on all seeds, tiny |
| Largest |leak R²| | +0.047 / +0.038 / +0.108 | yes | worse on all seeds, tiny |

Overall: **PASS** under the corrected criterion.