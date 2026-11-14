# Stage R: the robot head with the theory's terms; frozen criteria `configs/stage_r.criteria.yaml`

| Item | Verdict |
|---|---|
| E46 diagnostic | CONFIRMED |
| E47 PickCube | REFUTED |
| E47 PushCube | REFUTED |

## E46 (does the baseline robot head have dead output directions): CONFIRMED
Dead direction (eigenvalue under 1% of the mean) on 6 of 6 baseline runs (prediction: at least 4 of 6).

| Task | Seed | Min eigenvalue | Effective rank (of embedding size) | Dead | P1 ratio | Rung-1 gap |
|---|---|---|---|---|---|---|
| PickCube | 0 | 0.01132 | 89.3 of 128 | yes | 1.65 | 1.01 |
| PickCube | 1 | 0.005544 | 87.3 of 128 | yes | 1.50 | 1.00 |
| PickCube | 2 | 0.002892 | 86.1 of 128 | yes | 1.47 | 1.00 |
| PushCube | 0 | 0.002341 | 129.9 of 256 | yes | 2.09 | 1.00 |
| PushCube | 1 | 0.002374 | 138.1 of 256 | yes | 1.92 | 1.00 |
| PushCube | 2 | 0.001031 | 120.9 of 256 | yes | 1.92 | 1.00 |

## E47 (invariance and whitening terms on the robot head)
| Task | Arm | Seed | P1 | P2 | P3 | P4 | P1 ratio | Rung-1 gap | Held-out P1 | Held-out layout R2 (core / all) | Held-out progress R2 (core / all) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PickCube | baseline | 0 | no | no | yes | yes | 1.65 | 1.01 | 1.44 | 0.14 / 0.11 | 0.47 / 0.55 |
| PickCube | baseline | 1 | no | no | yes | yes | 1.50 | 1.00 | 1.39 | 0.14 / 0.14 | 0.40 / 0.45 |
| PickCube | baseline | 2 | no | no | yes | yes | 1.47 | 1.00 | 1.31 | 0.11 / 0.08 | 0.43 / 0.44 |
| PickCube | treated | 0 | no | no | yes | no | 1.09 | 1.00 | 1.04 | -0.04 / -0.03 | 0.07 / 0.08 |
| PickCube | treated | 1 | no | no | yes | no | 1.10 | 1.00 | 1.05 | -0.06 / -0.05 | 0.05 / 0.15 |
| PickCube | treated | 2 | no | no | yes | no | 1.10 | 1.00 | 1.05 | -0.02 / -0.00 | 0.07 / 0.11 |
| PushCube | baseline | 0 | no | yes | yes | yes | 2.09 | 1.00 | 1.14 | 0.65 / 0.84 | 0.70 / 0.75 |
| PushCube | baseline | 1 | no | yes | yes | yes | 1.92 | 1.00 | 1.13 | 0.65 / 0.79 | 0.52 / 0.68 |
| PushCube | baseline | 2 | no | yes | yes | yes | 1.92 | 1.00 | 1.16 | 0.65 / 0.80 | 0.70 / 0.77 |
| PushCube | treated | 0 | no | no | yes | yes | 1.25 | 1.00 | 1.16 | 0.69 / 0.75 | 0.79 / 0.84 |
| PushCube | treated | 1 | no | no | yes | no | 1.23 | 1.00 | 1.15 | 0.61 / 0.70 | 0.75 / 0.83 |
| PushCube | treated | 2 | no | no | yes | no | 1.18 | 1.00 | 1.11 | 0.40 / 0.58 | 0.54 / 0.69 |
