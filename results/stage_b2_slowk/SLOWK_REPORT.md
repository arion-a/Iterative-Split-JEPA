# G4-K: cluster count in the slow subspace (E31) and its boundary (E32); frozen criteria `configs/slowk.criteria.yaml`

## E31: **REFUTED** (a: K = 6 in at least 9 of 10 runs at each sigma_cat; b: purity at least 0.9 in at least 9 of 10 at sigma_cat [0.1, 0.4]; c: shuffled-time control K = 6 in at most 3 of 10; d: equal-speed control abstains in at least 9 of 10)

| sigma_cat | runs | K = 6, slow-subspace (a) | K = 6, E18 spectral (full space) | K = 6, silhouette | purity condition (b) | control K = 6 (c) | median subspace angle to category (deg) | D14 criterion met after Tier 1: slow / silhouette / E18 spectral | (a) held |
|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 10 | 10/10 | 1/10 | 3/10 | yes (mean purity 1.000) | 0/10 | 16.3 | 10/10 / 10/10 / 9/10 | yes |
| 0.4 | 10 | 9/10 | 2/10 | 2/10 | yes (mean purity 0.974) | 0/10 | 15.2 | 10/10 / 10/10 / 3/10 | yes |
| 0.6 | 10 | 6/10 | 0/10 | 2/10 | n/a (mean purity 0.901) | 0/10 | 13.9 | 9/9 / 7/9 / 1/9 | NO |

**Control d, equal speeds (sigma_cat 0.4):** the selector abstained in 10 of 10 runs (held).

## E32: **REFUTED** (K = 6 in at least 8 of 10 at sigma_cat 0.8 and 5 of 10 at 1.0; purity never above the ceiling plus 0.02)

| sigma_cat | runs | K = 6 | mean purity, slow-subspace clusters | abstained |
|---|---|---|---|---|
| 0.1 | 10 | 10/10 | 1.000 | 0/10 |
| 0.4 | 10 | 9/10 | 0.974 | 0/10 |
| 0.6 | 10 | 6/10 | 0.901 | 0/10 |
| 0.8 | 10 | 3/10 | 0.803 | 0/10 |
| 1.0 | 10 | 0/10 | 0.702 | 0/10 |

**Located boundary (largest sigma with K = 6 in at least 8 of 10 runs):** sigma_cat = 0.4.
