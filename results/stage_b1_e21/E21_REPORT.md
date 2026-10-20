# E21 Part A: B1 mechanism (all-Gaussian world, mirror encoder), fresh seeds 20-29

**Verdict (registered rule, amended leakage floor 0.01): FAIL** on 10 seeds; failing criteria: ['rank_test'] ({'rank_test': [21]}). Controls (judged on the mean): shuffled rung-2 behaved; rank-1 rung-2 behaved.

**E21 Part A prediction (PASS or PASS_WITH_LOCATED_RISK, controls behave): REFUTED.**

## Measured (main arm, mean ± std over seeds)

| Quantity | Value |
|---|---|
| Rung 1 angle (°) | 0.98 ± 0.25 |
| Rung 2 angle (°) | 1.18 ± 0.24 |
| Texture R² (rung 1) | 0.958 ± 0.005 |
| Identity R² (rung 2) | 0.983 ± 0.003 |
| Category core R² | 0.980 ± 0.002 |
| Nesting (gate definition, °) | 1.13 ± 0.25 |
| Gap ratio rung 1 / rung 2 | 51.9 ± 8.0 / 49.5 ± 6.5 |
| Largest off-diagonal |R²| (amended rule needs < 0.01) | 0.0006 ± 0.0002 |
| D13 leakage: normalized ‖A21‖, rung 1 / rung 2 (gate 0.0209) | 0.0111 ± 0.0029 / 0.0048 ± 0.0013 |
| Seeds meeting the D13 gate at both rungs | 10 of 10 |

## Per-criterion seeds passing

| Criterion | Seeds passing |
|---|---|
| rung1_angle | 10 of 10 |
| rung2_angle | 10 of 10 |
| rung1_variant_r2 | 10 of 10 |
| rung2_variant_r2 | 10 of 10 |
| core_invariant_r2 | 10 of 10 |
| nesting | 10 of 10 |
| rung1_gap | 10 of 10 |
| rung2_gap | 10 of 10 |
| leakage | 10 of 10 |
| rank_test | 9 of 10 |

## Controls

| Control | Rung-2 angle (°) | Rung-2 gap | Rung-1 angle (°) |
|---|---|---|---|
| shuffled_rung2 | 78.7 ± 16.0 | 1.01 ± 0.00 | 0.93 ± 0.25 |
| rank1_rung2 | 79.7 ± 7.5 | 1.16 ± 0.13 | 0.98 ± 0.25 |