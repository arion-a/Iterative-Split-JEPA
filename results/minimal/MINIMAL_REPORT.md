# Minimal claims (E38-E41); frozen criteria `configs/minimal.criteria.yaml`

| Claim | Verdict |
|---|---|
| E38 | CONFIRMED |
| E39 | CONFIRMED |
| E40 | REFUTED |
| E41 | REFUTED |

## E38 (equal speeds, correspondence against speed): CONFIRMED
Ladder worst angle under 5 on 5 of 5 seeds; single-shot worst angle 5 or more on 5 of 5.

| Seed | Ladder worst angle (deg) | Single-shot worst angle (deg) |
|---|---|---|
| 120 | 1.1 | 88.1 |
| 121 | 1.0 | 84.4 |
| 122 | 0.7 | 80.1 |
| 123 | 1.1 | 88.5 |
| 124 | 0.9 | 86.7 |

Separated-speed cell (E37, seeds 120, 121, 122, 123, 124): ladder 1.6, 1.2, 0.9, 1.7, 1.5; single-shot 3.2, 2.2, 1.5, 2.9, 2.5

## E39 (depth 5, predictively sufficient): CONFIRMED
Seeds passing each check at every rung (needs 4 of 5): angle 5, gap 5, presence 5, rho 5. Control (shuffled rung 2, 5 seeds): rung-2 gap under 2 on 5, rho_2 over 1.05 on 0; **rho_k not informative (control did not exceed the line), dropped from the verdict**.

| Seed | Angles per rung | Gap ratios | rho_k per rung |
|---|---|---|---|
| 130 | 0.7, 1.5, 1.6, 1.6 | 60, 51, 55, 61 | 1.000, 1.000, 0.999, 1.000 |
| 131 | 0.8, 1.2, 1.2, 1.9 | 62, 56, 54, 53 | 1.000, 1.000, 1.000, 1.000 |
| 132 | 0.8, 1.3, 1.3, 1.6 | 64, 56, 51, 52 | 1.000, 0.999, 1.000, 1.000 |
| 133 | 0.6, 1.1, 1.6, 1.6 | 68, 61, 58, 56 | 1.000, 1.000, 1.000, 1.000 |
| 134 | 0.8, 1.2, 1.3, 1.6 | 59, 58, 54, 52 | 1.000, 1.000, 1.000, 1.000 |

Control rho_2: 1.000, 1.000, 1.000, 1.000, 1.000

## E40 (the theory's invariance term, generic MLP): REFUTED
Treated: all presences at least 0.95 and both rungs clean with gap over 10 on 0 of 10 seeds (needs 9). Baseline: texture presence under 0.5 on 10 of 10 (needs 9).

| Arm | Seed | Presence (b1, b2, b3) | Angles | Gap ratios |
|---|---|---|---|---|
| baseline | 140 | -0.01, 0.64, 0.99 | 85.8, 63.9 | 1.2, 1.3 |
| baseline | 141 | -0.01, 0.54, 0.99 | 86.0, 84.6 | 1.1, 1.0 |
| baseline | 142 | -0.01, 0.94, 0.99 | 82.2, 6.1 | 1.3, 4.8 |
| baseline | 143 | -0.01, 0.55, 0.99 | 84.3, 74.5 | 1.0, 1.3 |
| baseline | 144 | -0.01, 0.99, 0.99 | 85.8, 1.1 | 1.3, 6.1 |
| baseline | 145 | -0.01, 0.74, 0.99 | 87.7, 37.4 | 1.0, 2.3 |
| baseline | 146 | -0.00, 0.42, 0.99 | 77.3, 73.8 | 1.2, 1.2 |
| baseline | 147 | -0.01, 0.99, 0.99 | 76.0, 1.5 | 1.0, 12.6 |
| baseline | 148 | -0.01, 0.70, 0.99 | 85.4, 71.0 | 1.1, 1.3 |
| baseline | 149 | -0.01, 0.99, 0.99 | 66.5, 1.9 | 1.4, 4.7 |
| treated | 140 | -0.00, 0.99, 1.00 | 73.2, 7.3 | 2.1, 1.2 |
| treated | 141 | 0.01, 0.99, 1.00 | 85.3, 2.0 | 1.6, 2.3 |
| treated | 142 | -0.00, 0.99, 1.00 | 70.2, 5.5 | 1.1, 1.6 |
| treated | 143 | 0.00, 0.99, 1.00 | 58.4, 9.1 | 1.2, 1.4 |
| treated | 144 | 0.00, 0.99, 1.00 | 82.7, 3.8 | 1.5, 1.5 |
| treated | 145 | -0.00, 0.99, 1.00 | 84.8, 7.4 | 3.0, 1.5 |
| treated | 146 | 0.02, 0.99, 1.00 | 80.1, 1.6 | 1.3, 2.3 |
| treated | 147 | 0.01, 0.99, 1.00 | 81.0, 5.0 | 1.1, 1.2 |
| treated | 148 | 0.04, 0.99, 1.00 | 88.8, 18.8 | 1.4, 1.1 |
| treated | 149 | 0.02, 0.99, 1.00 | 78.6, 12.1 | 1.7, 1.1 |

## E41 (a violated hypothesis shows in the gap): REFUTED
Rungs with gap over 10 and block present: 31 of 31 clean (100%; needs 95%). Rungs with gap 10 or less: 5 of 39 clean (13%; at most 10%). All main-arm runs of E38-E40 (70 rungs).

