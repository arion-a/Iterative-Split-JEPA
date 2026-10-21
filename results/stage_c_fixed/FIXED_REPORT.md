# E36 (Gap 5): paper block sizes on the E24 pipeline; frozen criteria `configs/fixed_sizes.criteria.yaml`

**E36: REFUTED.** PickCube: not all hold; PushCube: not all hold.

| Task | Split seed | d1 | Rung-1 gap | P1 V1/Q1 (>=3) | P2 V2/Q2 (>=1.5) | P3 controls | Camera acc V1 / Q1 |
|---|---|---|---|---|---|---|---|
| PickCube | 0 | 64 | 1.00 | 1.46 | 1.37 | yes | 0.979 / 0.549 |
| PickCube | 1 | 64 | 1.00 | 1.51 | 1.43 | yes | 0.999 / 0.528 |
| PickCube | 2 | 64 | 1.00 | 1.43 | 1.39 | yes | 0.998 / 0.537 |
| PickCube | verdict | | | P1 NO | P2 NO | P3 yes | P4 yes |
| PushCube | 0 | 128 | 1.00 | 1.89 | 1.72 | yes | 0.980 / 0.373 |
| PushCube | 1 | 128 | 1.00 | 1.65 | 1.86 | yes | 0.993 / 0.347 |
| PushCube | 2 | 128 | 1.00 | 1.34 | 1.53 | yes | 0.988 / 0.487 |
| PushCube | verdict | | | P1 NO | P2 yes | P3 yes | P4 yes |
