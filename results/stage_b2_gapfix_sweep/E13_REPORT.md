# E13 report: contamination model across the noise sweep (18 runs), blind E14 check, Tier 4 comparability

**Model fit:** v_cat = 3.981; log-gap R² = 0.667 (needs ≥ 0.8); median absolute relative error = 0.19 (needs ≤ 0.25) -> **DOES NOT FIT**.

**Purified above the curve:** Tier 1 gap exceeds the predicted untreated gap in 10 of 17 runs with ρ > 0.05 (needs ≥ 90%) -> **NO**.

**Blind E14:** no metric damaged in 18 of 18 runs; treated subspace no farther from the B1-arm subspace in 14 of 18 runs -> **NOT CONFIRMED in every run**.

**Tier 4 comparability:** coefficient of variation of the rung-2 gap across runs, Tier 1 1.419, Tier 1 + Tier 4 1.384 (Tier 4 keeps a case only if ≤ 75% of Tier 1's) -> **no case**.

**ρ-hat vs true ρ:** correlation -0.498; mean ρ-hat -0.005 vs mean ρ 0.325.

| σ_cat | seed | Cluster purity | K found | True ρ | Gap B1 | Gap B2 untreated | Gap predicted (model) | Gap Tier 1 | Gap Tier 1+4 | ρ-hat | No damage (E14) | Closer to B1 subspace (E14) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 0 | 0.834 | 5 | 0.170 | 28.7 | 2.7 | 2.5 | 19.2 | 17.0 | 0.159 | yes | yes |
| 0.1 | 1 | 0.835 | 5 | 0.167 | 31.0 | 2.7 | 2.7 | 22.2 | 19.5 | 0.157 | yes | yes |
| 0.1 | 2 | 0.836 | 5 | 0.165 | 22.2 | 3.9 | 2.6 | 17.6 | 19.5 | 0.147 | yes | yes |
| 0.4 | 0 | 0.967 | 6 | 0.063 | 34.7 | 4.2 | 6.1 | 4.5 | 4.6 | -0.015 | yes | yes |
| 0.4 | 1 | 0.990 | 6 | 0.019 | 40.7 | 5.7 | 15.5 | 5.8 | 5.9 | -0.027 | yes | yes |
| 0.4 | 2 | 0.834 | 5 | 0.176 | 33.9 | 3.1 | 2.5 | 3.7 | 3.7 | -0.008 | yes | yes |
| 0.6 | 0 | 0.849 | 6 | 0.240 | 45.9 | 1.4 | 1.9 | 1.6 | 1.6 | -0.033 | yes | yes |
| 0.6 | 1 | 0.835 | 6 | 0.262 | 46.4 | 1.8 | 1.8 | 1.9 | 1.9 | -0.023 | yes | yes |
| 0.6 | 2 | 0.848 | 6 | 0.207 | 40.8 | 1.7 | 2.2 | 1.8 | 1.8 | -0.034 | yes | yes |
| 0.8 | 0 | 0.769 | 11 | 0.354 | 59.1 | 1.1 | 1.3 | 1.2 | 1.2 | -0.042 | yes | yes |
| 0.8 | 1 | 0.744 | 12 | 0.366 | 55.0 | 1.1 | 1.3 | 1.1 | 1.1 | -0.039 | yes | yes |
| 0.8 | 2 | 0.747 | 9 | 0.360 | 47.5 | 1.2 | 1.3 | 1.3 | 1.3 | -0.045 | yes | yes |
| 1.0 | 0 | 0.688 | 10 | 0.474 | 74.9 | 1.0 | 1.0 | 1.1 | 1.0 | -0.045 | yes | yes |
| 1.0 | 1 | 0.653 | 10 | 0.490 | 66.2 | 1.1 | 1.0 | 1.1 | 1.1 | -0.044 | yes | yes |
| 1.0 | 2 | 0.711 | 12 | 0.424 | 60.4 | 1.0 | 1.1 | 1.1 | 1.1 | -0.050 | yes | **NO** |
| 1.5 | 0 | 0.541 | 9 | 0.641 | 139.7 | 1.0 | 0.7 | 1.0 | 1.0 | -0.050 | yes | **NO** |
| 1.5 | 1 | 0.518 | 10 | 0.644 | 132.5 | 1.0 | 0.7 | 1.1 | 1.0 | -0.049 | yes | **NO** |
| 1.5 | 2 | 0.543 | 10 | 0.626 | 110.7 | 1.0 | 0.7 | 1.1 | 1.1 | -0.055 | yes | **NO** |

## Exploratory (post hoc, NOT the registered test): a within-category floor

Pairs built from clusters share the category label but not the category jitter, so even perfectly valid cluster pairs carry energy of about 2 sigma_cat^2 in the category directions; the B1 twins share the jitter exactly, so the B1 eigenvalue understates the floor for cluster pairs. Runs with almost no invalid pairs (rho < 0.03), fifth eigenvalue of the B1 arm vs the untreated B2 arm vs 2 sigma_cat^2: sigma 0.4: 0.047 vs 0.342 vs 0.320 (rho 0.019).

Refit with a free within-category coefficient c: gap = lambda_d2 / (lambda_d2+1^B1 + c sigma_cat^2 + rho v_cat), best c = 0.4, v_cat = 3.16: log-gap R² = 0.714, median relative error 0.22. Two free parameters instead of one and fitted after seeing the data, so it is a lead, not a confirmation.


![E13](figures/E13_gap_vs_contamination.svg)
