# E21 Part B and E22: B2 world, fresh seeds 20-29, sigma_cat 0.1 and 0.4

## Part B: frozen criteria on fresh seeds

| σ_cat | Runs | Gap B1 arm | Gap B2 untreated | Gap B2 + Tier 1 | Share of deficit recovered (needs ≥ 0.60 at σ 0.1) | Tier 1 gap > 10 | Tier 1 meets E20 criterion (needs ≥ 90% at σ 0.4) | D10 nesting < 5° in every run | Metrics damaged (E14 rule) |
|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 9 | 26.1 | 5.3 | 19.6 | 0.69 | 9/9 | 9/9 | yes | none |

Sub-claims: (i) σ 0.1 recovery ≥ 0.60 and gap > 10 in ≥ 90% of seeds: **yes**; (ii) σ 0.4 E20 criterion in ≥ 90% of seeds: **NO**; (iii) nesting < 5° in every run: **yes**; (iv) no metric damaged: **yes**. Part A verdict: see `results/stage_b1_e21/E21_REPORT.md`.

## E22: probe-image explanation, direct test (B1 arm = generator twins; raw angle = against the identity probe image, orthogonalised = against the part of it orthogonal to the texture image)

**Prediction (orthogonalised angle ≤ 5° in ≥ 90% of runs AND ≥ 3° below the raw angle in ≥ 90% of runs): ≤ 5° in 9 of 9; ≥ 3° lower in 9 of 9 -> CONFIRMED.**

Means over runs: raw 10.32 ± 1.69°, orthogonalised 3.28 ± 0.89°; smallest angle between the texture image and the identity+category images 77.1 ± 1.6°.

| σ_cat | seed | Min angle texture image vs identity+category images (°) | Share of identity image removed by orthogonalising | B1 arm rung-2 angle, raw (°) | orthogonalised (°) | Difference (°) | B2 + Tier 1, raw (°) | orthogonalised (°) |
|---|---|---|---|---|---|---|---|---|
| 0.1 | 20 | 76.5 | 0.014 | 11.41 | 2.74 | 8.67 | 11.41 | 2.90 |
| 0.1 | 21 | 77.6 | 0.010 | 9.92 | 3.42 | 6.50 | 9.95 | 3.99 |
| 0.1 | 22 | 78.7 | 0.009 | 9.54 | 3.09 | 6.44 | 9.56 | 3.05 |
| 0.1 | 23 | 79.9 | 0.007 | 7.04 | 2.66 | 4.38 | 7.14 | 3.27 |
| 0.1 | 24 | 75.3 | 0.015 | 9.38 | 4.00 | 5.38 | 9.42 | 4.28 |
| 0.1 | 25 | 77.6 | 0.013 | 13.14 | 4.85 | 8.29 | 13.21 | 5.18 |
| 0.1 | 26 | 77.0 | 0.011 | 10.17 | 3.23 | 6.94 | 10.17 | 3.46 |
| 0.1 | 27 | 75.2 | 0.014 | 11.18 | 3.80 | 7.38 | 11.14 | 3.92 |
| 0.1 | 28 | 76.0 | 0.012 | 11.07 | 1.73 | 9.34 | 11.06 | 1.87 |