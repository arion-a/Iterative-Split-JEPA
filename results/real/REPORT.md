# Stage V real-video report (P5), informational

10 public real double-pendulum clips (MIT licence), 447 frames each at 30 fps, held out in TIME (first 60% train, next 15% validation, last 25% test), not in release.
No gates, no frozen predictions (DECIDE 9). The framework input is a 32×32 grayscale crop with an additive-illumination view pair; the orange-link tracker is evaluator-side and partial (one link only), so NO energy naming is claimed.

Ladder stop: S2; core dimension 7; psi ICC on fit: 1.088

Certificate on the held-out time slice:
| quantity | value |
|---|---|
| V | 0.0 |
| n_pairs_found | 200 |
| eps | 0.6182 |
| drift_q95_val | 0.2591 |
| icc | 0.9892 |
| L | 0.9886 |
| rollout_nmse | 0.1708 |

Ladder records:
| family | content dim | d_k | lambda_max / chance | best ratio | outcome |
|---|---|---|---|---|---|
| aug | 64 | 0 | 0.004 | 0.0 | S1 |
| lag8 | 64 | 57 | 1.819 | 2.81 | split |
| lag32 | 7 | 0 | 0.079 | 1.61 | S2 |

Tracker proxies (informational; ceiling probe is REPORT-ONLY, D13):
| proxy | |Spearman(psi, proxy)| test | linear probe R² test |
|---|---|---|
| speed2 | 0.112 | -0.49 |
| height | 0.309 | 0.068 |

Caveats: 10 clips; friction decays any energy-like quantity within a clip; the ICC is a statistic over 10 release means; the proxy is not the conserved energy.
