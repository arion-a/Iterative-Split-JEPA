# E21 Part A: B1 mechanism (all-Gaussian world, mirror encoder), fresh seeds 20-29

**Verdict (registered rule, amended leakage floor 0.01): FAIL** on 6 seeds; failing criteria: ['rank_test'] ({'rank_test': [21]}). Controls (judged on the mean): shuffled rung-2 DID NOT behave; rank-1 rung-2 DID NOT behave.

**E21 Part A prediction (PASS or PASS_WITH_LOCATED_RISK, controls behave): REFUTED.**

## Measured (main arm, mean ± std over seeds)

| Quantity | Value |
|---|---|
| Rung 1 angle (°) | 0.97 ± 0.25 |
| Rung 2 angle (°) | 1.12 ± 0.18 |
| Texture R² (rung 1) | 0.958 ± 0.006 |
| Identity R² (rung 2) | 0.982 ± 0.003 |
| Category core R² | 0.980 ± 0.003 |
| Nesting (gate definition, °) | 1.08 ± 0.19 |
| Gap ratio rung 1 / rung 2 | 52.7 ± 8.4 / 50.8 ± 4.9 |
| Largest off-diagonal |R²| (amended rule needs < 0.01) | 0.0005 ± 0.0002 |
| D13 leakage: normalized ‖A21‖, rung 1 / rung 2 (gate 0.0209) | 0.0109 ± 0.0026 / 0.0046 ± 0.0010 |
| Seeds meeting the D13 gate at both rungs | 6 of 6 |

## Per-criterion seeds passing

| Criterion | Seeds passing |
|---|---|
| rung1_angle | 6 of 6 |
| rung2_angle | 6 of 6 |
| rung1_variant_r2 | 6 of 6 |
| rung2_variant_r2 | 6 of 6 |
| core_invariant_r2 | 6 of 6 |
| nesting | 6 of 6 |
| rung1_gap | 6 of 6 |
| rung2_gap | 6 of 6 |
| leakage | 6 of 6 |
| rank_test | 5 of 6 |