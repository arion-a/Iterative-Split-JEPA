# Stage V hierarchical report (P4)

Criteria frozen in `configs/hier.yaml`. Format: docs/REPORTING.md.

## A. Gate table
| Criterion | Plain meaning | Threshold | Measured | Pass? |
|---|---|---|---|---|
| E35 RUNGS | cuts found by the lag ladder (registered: 4) | = 4 | 1.000 ± 0.000 ([1, 1, 1]) | False |
| per-rung variant R² | linear readout of the removed blocks from the rung's variant block | ≥ 0.9 | 0.959 ± 0.011 | True |
| per-rung invariant R² | readout of the remaining blocks from the rung's invariant core | ≥ 0.9 | 0.989 ± 0.003 | True |
| (D) residual ratio | learned vs oracle-block one-step residual | ≤ 1.25 | 1.074 ± 0.017 | True |
| (C) rollout ratio | learned vs oracle 8-step rollout error | ≤ 1.25 | 1.005 ± 0.001 | True |
| L per rung | Lipschitz constant of the learned linear transition | ≤ 1.02 | 0.949 ± 0.002 | True |

## D. Verdict and controls
Hierarchical: RUNGS [1, 1, 1] against the registered 4; gates passed 5/6; control behaved.

| Control | Required outcome | Observed | Behaved? |
|---|---|---|---|
| shuffled pairs | RUNGS = 0 | [0, 0, 0] | True |

## Informational (not gates)

Oracle cut gaps at lag 1 (arithmetic, 2(1−a) ratios): [1.6, 2.0, 2.5, 2.0]; a cut needs ratio ≥ 2.

Family records:
| seed | family | content dim | d_k | best ratio | outcome | eigenvalues |
|---|---|---|---|---|---|---|
| 0 | lag1 | 20 | 12 | 2.23 | split | [1.58, 1.51, 1.47, 1.41, 1.01, 1.0, 0.97, 0.96, 0.52, 0.51, 0.5, 0.49, 0.22, 0.22, 0.21, 0.21, 0.12, 0.11, 0.11, 0.11] |
| 0 | lag2 | 8 | 0 | 1.75 | S2 | [0.41, 0.4, 0.39, 0.38, 0.22, 0.21, 0.21, 0.2] |
| 1 | lag1 | 20 | 12 | 2.26 | split | [1.6, 1.57, 1.55, 1.51, 1.01, 1.0, 0.98, 0.96, 0.53, 0.51, 0.51, 0.5, 0.22, 0.21, 0.21, 0.21, 0.12, 0.11, 0.11, 0.11] |
| 1 | lag2 | 8 | 0 | 1.77 | S2 | [0.41, 0.4, 0.4, 0.39, 0.22, 0.21, 0.21, 0.2] |
| 2 | lag1 | 20 | 12 | 2.31 | split | [1.61, 1.57, 1.55, 1.52, 1.03, 1.01, 0.98, 0.97, 0.52, 0.52, 0.5, 0.49, 0.21, 0.21, 0.21, 0.21, 0.11, 0.11, 0.11, 0.1] |
| 2 | lag2 | 8 | 0 | 1.81 | S2 | [0.4, 0.39, 0.39, 0.38, 0.21, 0.21, 0.21, 0.2] |

Per-rung evaluation (blocks are 1 = fastest … 5 = slowest):
| seed | rung | family | variant blocks | invariant blocks | variant R² | invariant R² | D ratio | C ratio | L |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 1 | lag1 | [1, 2, 3] | [4, 5] | 0.9461281469199214 | 0.984623115788954 | 1.094641798441666 | 1.0060533880872649 | 0.9480270385810032 |
| 1 | 1 | lag1 | [1, 2, 3] | [4, 5] | 0.9585727398295139 | 0.9893337132336835 | 1.0747371526771285 | 1.0052460801559804 | 0.9480334952928199 |
| 2 | 1 | lag1 | [1, 2, 3] | [4, 5] | 0.9723183456487109 | 0.9916859428692095 | 1.054087993512906 | 1.0029044313591708 | 0.952295487700139 |

Not run: ARM-S (equals rung 1 of the ladder), ARM-H/F, E36-E38 (need a constructed bridge-failure world).
