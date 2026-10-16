# Recalibrated gap reference for cluster-built pairs, and the corrected contamination model (existing sweep data; D14 candidate and erratum)

## The floor under cluster-built pairs (fifth rung-2 eigenvalue, mean over 3 seeds)

Twins (B1) share the category jitter exactly. Cluster-built pairs share only the label, so even perfect clusters carry within-category energy. 'Perfect clusters' = the label_pairs arm (pairs that share the true category).

| σ_cat | B1 twins | Twins + 2σ_cat² (analytic) | Perfect-cluster pairs (measured) | Rung-2 gap, perfect clusters (the achievable gap) |
|---|---|---|---|---|
| 0.1 | 0.071 | 0.091 | 0.097 | 19.49 |
| 0.4 | 0.052 | 0.372 | 0.358 | 5.31 |
| 0.6 | 0.043 | 0.763 | 0.594 | 3.21 |
| 0.8 | 0.036 | 1.316 | 0.828 | 2.30 |
| 1.0 | 0.028 | 2.028 | 1.039 | 1.83 |
| 1.5 | 0.015 | 4.515 | 1.415 | 1.34 |

The analytic term holds within about 5% up to σ_cat 0.4 and overstates beyond (whitening compresses the growing variance), so the erratum uses the measured floor, not 2σ_cat².

## Recalibrated criterion (D14 candidate): cluster-built gap ≥ 0.6 × achievable gap, where the achievable gap is at least 3.0

| σ_cat | Achievable gap | B2 untreated meets it | B2 + Tier 1 meets it |
|---|---|---|---|
| 0.1 | 19.49 | 0/3 | 3/3 |
| 0.4 | 5.31 | 2/3 | 3/3 |
| 0.6 | 3.21 | 0/3 | 0/3 |
| 0.8 | 2.30 | n/a | n/a |
| 1.0 | 1.83 | n/a | n/a |
| 1.5 | 1.34 | n/a | n/a |

Per run (ratio to the achievable gap in brackets):

| σ_cat | seed | Achievable gap | B2 untreated | B2 + Tier 1 | Criterion | Untreated meets | Tier 1 meets |
|---|---|---|---|---|---|---|---|
| 0.1 | 0 | 20.18 | 2.70 (0.13) | 19.16 (0.95) | applies | no | yes |
| 0.1 | 1 | 21.03 | 2.65 (0.13) | 22.20 (1.06) | applies | no | yes |
| 0.1 | 2 | 17.26 | 3.95 (0.23) | 17.62 (1.02) | applies | no | yes |
| 0.4 | 0 | 5.16 | 4.22 (0.82) | 4.55 (0.88) | applies | yes | yes |
| 0.4 | 1 | 5.59 | 5.65 (1.01) | 5.85 (1.05) | applies | yes | yes |
| 0.4 | 2 | 5.19 | 3.10 (0.60) | 3.72 (0.72) | applies | no | yes |
| 0.6 | 0 | 3.09 | 1.45 (0.47) | 1.63 (0.53) | applies | no | no |
| 0.6 | 1 | 3.33 | 1.75 (0.53) | 1.95 (0.59) | applies | no | no |
| 0.6 | 2 | 3.20 | 1.70 (0.53) | 1.81 (0.57) | applies | no | no |
| 0.8 | 0 | 2.23 | 1.12 (0.50) | 1.18 (0.53) | n/a (no usable cliff) |  |  |
| 0.8 | 1 | 2.35 | 1.07 (0.45) | 1.10 (0.47) | n/a (no usable cliff) |  |  |
| 0.8 | 2 | 2.31 | 1.21 (0.52) | 1.26 (0.54) | n/a (no usable cliff) |  |  |
| 1.0 | 0 | 1.79 | 1.02 (0.57) | 1.06 (0.59) | n/a (no usable cliff) |  |  |
| 1.0 | 1 | 1.87 | 1.06 (0.57) | 1.10 (0.59) | n/a (no usable cliff) |  |  |
| 1.0 | 2 | 1.83 | 1.04 (0.57) | 1.07 (0.58) | n/a (no usable cliff) |  |  |
| 1.5 | 0 | 1.32 | 1.02 (0.77) | 1.04 (0.79) | n/a (no usable cliff) |  |  |
| 1.5 | 1 | 1.37 | 1.02 (0.74) | 1.06 (0.78) | n/a (no usable cliff) |  |  |
| 1.5 | 2 | 1.33 | 1.03 (0.78) | 1.07 (0.81) | n/a (no usable cliff) |  |  |

## Contamination model, original versus corrected floor (post hoc refit on the same 18 runs, one fitted constant each)

| Floor used for λ_{d2+1}^clean | v_cat | log-gap R² | median relative error | Tier 1 above the curve |
|---|---|---|---|---|
| B1 twins (registered E13 model) | 3.98 | 0.667 | 0.19 | 10 of 17 |
| Perfect-cluster pairs (corrected) | 2.14 | 0.810 | 0.12 | 14 of 17 |

The corrected model meets the numeric thresholds registered for E13 (R² ≥ 0.8, error ≤ 25%), but it was fitted after seeing the data, so it is a lead and not a confirmation of E13.