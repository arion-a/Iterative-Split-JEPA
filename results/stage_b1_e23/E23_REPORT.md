# E23: generic MLP encoder in the B1 ladder, seeds 30-34 (5 main runs, 5 shuffled-control runs)

**E23 prediction (every criterion except possibly rung-1 variant R² on at least 4 of 5 seeds; shuffled control behaves): REFUTED.** Refutation rule (two or more criteria each failing on two or more seeds): met. Shuffled control behaved.

## Per-criterion seeds passing

| Criterion | Seeds passing | Needs ≥ 4 of 5 |
|---|---|---|
| rung1_angle | 0 of 5 | NO |
| rung2_angle | 0 of 5 | NO |
| rung1_variant_r2 | 0 of 5 | n/a (excepted) |
| rung2_variant_r2 | 0 of 5 | NO |
| core_invariant_r2 | 5 of 5 | yes |
| nesting | 0 of 5 | NO |
| rung1_gap | 0 of 5 | NO |
| rung2_gap | 0 of 5 | NO |
| leakage | 0 of 5 | NO |
| rank_test | 0 of 5 | NO |

## Measured (main arm, mean ± std)

| Quantity | Value |
|---|---|
| Rung 1 angle (°) | 82.09 ± 7.63 |
| Rung 2 angle (°) | 81.08 ± 9.06 |
| Texture R² (rung 1) | -0.001 ± 0.000 |
| Identity R² (rung 2) | 0.505 ± 0.135 |
| Gap ratio rung 1 / rung 2 | 1.1 ± 0.1 / 2.2 ± 1.3 |
| Nesting (gate definition, °) | 74.42 ± 6.46 |

## Shuffled-pair control

| Rung-2 angle (°) | Rung-2 gap ratio |
|---|---|
| 85.9 ± 2.7 | 1.01 ± 0.00 |