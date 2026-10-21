# Stage V C2 report: Columbia full experiment (video-level)

Criteria frozen in `configs/columbia_full.yaml`; prediction text in `docs/EVIDENCE.md` (C2). Format: docs/REPORTING.md.

## A. Gate table
| Criterion | Plain meaning | Threshold | Measured (mean ± std over 3 seeds) | Pass? |
|---|---|---|---|---|
| (a) V | matched states keep matched successors | ≤ 0.05 | 0.012 ± 0.010 | True |
| (a) ICC (between videos) | share of psi variance between videos | ≥ 0.9 | 0.685 ± 0.003 | False |
| (a) L | Lipschitz constant of the linear transition | ≤ 1.02 | 0.985 ± 0.000 | True |
| (a) rollout | 8-step rollout RMSE / std psi | ≤ 0.35 | 0.297 ± 0.007 | True |
| (b) naming | |Spearman(psi, tracked total energy)|, valid test frames | ≥ 0.5 | 0.910 ± 0.004 | True |
| (c) flat control | no-split baseline stays below | < 0.5 | 0.562 ± 0.120 | False |
| (d) seed agreement | min pairwise |Spearman| of psi on the common test videos | ≥ 0.9 | 0.966 ± 0.001 | True |

## D. Verdict
C2 Columbia full: gates passed 5/7; confirmed only if all four predictions (a)-(d) hold: NOT CONFIRMED.

## Informational (not gates)

Arms:
| arm | V | ICC | L | rollout | |Spearman| with energy |
|---|---|---|---|---|---|
| main | 0.012 ± 0.010 | 0.685 ± 0.003 | 0.985 ± 0.000 | 0.297 ± 0.007 | 0.910 ± 0.004 |
| flat | 0.000 ± 0.000 | 0.389 ± 0.108 | 0.966 ± 0.002 | 0.805 ± 0.072 | 0.562 ± 0.120 |
| shuffled | 0.002 ± 0.002 | 0.750 ± 0.003 | 0.977 ± 0.001 | 0.379 ± 0.013 | 0.796 ± 0.034 |
| temporal_only | 0.012 ± 0.010 | 0.685 ± 0.003 | 0.985 ± 0.000 | 0.297 ± 0.007 | 0.910 ± 0.004 |

Ladder records:
| seed | family | content dim | d_k | lambda_max / chance | best ratio | outcome |
|---|---|---|---|---|---|---|
| 0 | aug | 64 | 0 | 0.001 | 0.0 | S1 |
| 0 | lag8 | 64 | 63 | 1.757 | 4.61 | split |
| 0 | lag32 | 1 | 0 | 0.047 | 0.0 | S1 |
| 1 | aug | 64 | 0 | 0.001 | 0.0 | S1 |
| 1 | lag8 | 64 | 63 | 1.746 | 4.93 | split |
| 1 | lag32 | 1 | 0 | 0.043 | 0.0 | S1 |
| 2 | aug | 64 | 0 | 0.001 | 0.0 | S1 |
| 2 | lag8 | 64 | 63 | 1.767 | 5.01 | split |
| 2 | lag32 | 1 | 0 | 0.045 | 0.0 | S1 |

Reach (normalised held-out error vs horizon in frames [1, 2, 4, 8, 16, 32]):
| block | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| psi | 0.035 ± 0.001 | 0.055 ± 0.003 | 0.076 ± 0.003 | 0.084 ± 0.004 | 0.096 ± 0.005 | 0.102 ± 0.005 |
| fast block | 0.292 ± 0.002 | 0.482 ± 0.001 | 0.638 ± 0.003 | 0.760 ± 0.001 | 0.839 ± 0.000 | 0.804 ± 0.005 |

Tracked-energy reliability (ANOVA share between test videos): 0.553. Report-only ceiling probe R² (D13): [0.818, 0.82, 0.819].

Comparison with C1 (clip-level, 4000 steps; its thresholds were the same): naming [0.893, 0.895, 0.88], rollout [0.431, 0.452, 0.441], ICC [0.908, 0.898, 0.903].

Not applicable to real data, not run: E35 (planted hierarchy), E36 (planted bridge).
