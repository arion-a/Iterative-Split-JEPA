# Stage V handshake report (P2-P3)

Seeds [0, 1, 2]. Criteria frozen in `configs/handshake.yaml` (sha256 in `configs/handshake.criteria.sha256`). Format: docs/REPORTING.md.

## A. Gate table
| Criterion | Plain meaning | Threshold | Measured (mean ± std over seeds) | Pass? |
|---|---|---|---|---|
| E31c′ violation rate V | matched states keep matched successors | ≤ 0.05 | 0.003 ± 0.005 | True |
| E31c′ non-degeneracy (ICC) | share of ψ variance between releases (a constant has V = 0) | ≥ 0.9 | 0.973 ± 0.003 | True |
| E31c′ stability L | Lipschitz constant of the linear latent transition | ≤ 1.02 | 0.993 ± 0.001 | True |
| E31c′ rollout closure | 8-step rollout RMSE / std ψ | ≤ 0.35 | 0.232 ± 0.008 | True |
| E31d naming | |Spearman(ψ, E)| on held-out releases (evaluator side) | ≥ 0.99 | 0.786 ± 0.074 | False |
| E31e ladder ends by S1 at the third family (lag 32) | no variation left beyond the discovered coordinate | every seed | 2/3 seeds (stops: [(3, 'S1'), (3, 'S1'), (3, None)]) | False |
| E31e reach | NMSE at horizon 32: variant block ≥ 0.5 and ψ ≤ 0.1225 | every seed | variant 0.666 ± 0.042, ψ 0.057 ± 0.006 | True |
| P-stab | min pairwise |Spearman| of ψ across seeds (common held-out frames) | ≥ 0.9 | 0.766 ± 0.058 | False |

## D. Verdict and controls
Handshake on 3 seeds: gates passed 5/8; controls behaved 3/3.

| Control | Required outcome | Observed | Behaved? |
|---|---|---|---|
| flat arm | |Spearman(ψ, E)| below 0.9 on every seed | 0.257 ± 0.293 | True |
| shuffled arm | |Spearman(ψ, E)| below 0.9 on every seed | 0.790 ± 0.085 | True |
| shuffled arm ladder | S2 (flat spectrum) at the first lag family | ['S2', 'S2', 'S2'] | True |

## Informational (not gates)

Arms (physics-free certificate + naming):
| arm | V | ICC | L | rollout | |Spearman| with E |
|---|---|---|---|---|---|
| main | 0.003 ± 0.005 | 0.973 ± 0.003 | 0.993 ± 0.001 | 0.232 ± 0.008 | 0.786 ± 0.074 |
| flat | 0.005 ± 0.007 | 0.589 ± 0.029 | 0.972 ± 0.001 | 0.826 ± 0.065 | 0.257 ± 0.293 |
| shuffled | 0.003 ± 0.005 | 0.974 ± 0.002 | 0.993 ± 0.001 | 0.238 ± 0.010 | 0.790 ± 0.085 |

Evaluator-side reference coordinates through the same checker (q_energy should pass; q_angle and q_const should fail V or ICC):
| reference | V | ICC | L | rollout |
|---|---|---|---|---|
| E | 0.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.000 ± 0.000 |
| angles | 0.000 ± 0.000 | 0.369 ± 0.274 | 1.006 ± 0.000 | 0.560 ± 0.265 |
| const | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | nan ± nan |

Ladder records (lambda_max over chance = largest eigenvalue / 2 of the family's difference moment on the remaining content):
| seed | family | content dim | d_k | lambda_max / chance | best ratio | outcome |
|---|---|---|---|---|---|---|
| 0 | aug | 64 | 0 | 0.016 | 0.0 | S1 |
| 0 | lag8 | 64 | 63 | 1.69 | 2.67 | split |
| 0 | lag32 | 1 | 0 | 0.028 | 0.0 | S1 |
| 1 | aug | 64 | 0 | 0.016 | 0.0 | S1 |
| 1 | lag8 | 64 | 63 | 1.705 | 2.1 | split |
| 1 | lag32 | 1 | 0 | 0.04 | 0.0 | S1 |
| 2 | aug | 64 | 0 | 0.016 | 0.0 | S1 |
| 2 | lag8 | 64 | 60 | 1.789 | 2.27 | split |
| 2 | lag32 | 4 | 3 | 0.153 | 2.2 | split |

Ceiling probe (REPORT-ONLY, D13): linear readout of E from the whitened latent, R²:
| seed | train | test |
|---|---|---|
| 0 | 0.929 | 0.926 |
| 1 | 0.912 | 0.907 |
| 2 | 0.905 | 0.794 |

Reach curves (NMSE vs horizon, held-out releases): see raw JSON `reach_psi`, `reach_variant_block`.

Not run: E31f (no frozen statistic). Limitations: additive-illumination nuisance only (gain, shift not tested); naming sign is arbitrary so |Spearman| is used; datasets differ per seed, P-stab compares seeds on the seed-0 test releases.
