# Encoder generality: presence first, then splitting (E25-E27; criteria `configs/layered.yaml`, D15)

## E25: is the fast (texture) block absent from the prediction-trained MLP's output at the original speeds? (5 seeds)

**E25 prediction (texture presence below 0.5 on at least 4 of 5 seeds and category presence at least 0.9 on at least 4 of 5): CONFIRMED.** (texture absent on 5 of 5; texture present on 0; category present on 5). Refuted if texture presence is at least 0.9 on at least 4 of 5.

| Block | Presence, nonlinear probe R² | Presence, linear R² | Seeds present (≥ 0.9) |
|---|---|---|---|
| texture (block 1) | -0.012 ± 0.001 | -0.001 ± 0.000 | 0 of 5 |
| identity (block 2) | 0.744 ± 0.061 | 0.559 ± 0.122 | 0 of 5 |
| category (block 3) | 0.993 ± 0.001 | 0.984 ± 0.003 | 5 of 5 |

| Rung | ABSENT | PARTIAL | PRESENT_NOT_SEPARABLE | SPLIT |
|---|---|---|---|---|
| rung 1 (texture) | 5 | 0 | 0 | 0 |
| rung 2 (identity) | 0 | 5 | 0 | 0 |

## E26: equal predictability (rhos 0.5), generic MLP + prediction recipe (5 main, 5 shuffled-control seeds)

**E26 prediction (all three blocks present on at least 4 of 5 seeds AND every B1 criterion except possibly rung-1 variant R² on at least 4 of 5 seeds AND shuffled control behaves): CONFIRMED.** All blocks present on 5 of 5; criteria rule held; shuffled control behaved.

| Block | Presence, nonlinear probe R² | Presence, linear R² | Seeds present (≥ 0.9) |
|---|---|---|---|
| texture (block 1) | 0.991 ± 0.001 | 0.986 ± 0.003 | 5 of 5 |
| identity (block 2) | 0.991 ± 0.001 | 0.986 ± 0.002 | 5 of 5 |
| category (block 3) | 0.991 ± 0.001 | 0.986 ± 0.001 | 5 of 5 |

| Rung | ABSENT | PARTIAL | PRESENT_NOT_SEPARABLE | SPLIT |
|---|---|---|---|---|
| rung 1 (texture) | 0 | 0 | 0 | 5 |
| rung 2 (identity) | 0 | 0 | 0 | 5 |

| Criterion | Seeds passing |
|---|---|
| rung1_angle | 5/5 |
| rung2_angle | 5/5 |
| rung1_variant_r2 | 5/5 |
| rung2_variant_r2 | 5/5 |
| core_invariant_r2 | 5/5 |
| nesting | 5/5 |
| rung1_gap | 5/5 |
| rung2_gap | 5/5 |
| leakage | 5/5 |
| rank_test | 5/5 |

## E27: architecture x objective at equal predictability (main arm, 5 seeds per cell)

**E27 prediction (in no cell is a present block not separable on 2 or more seeds): CONFIRMED.** Seeds with a PRESENT_NOT_SEPARABLE rung, per cell: {'mirror + paper objective': 0, 'mlp + paper objective': 0, 'mirror + prediction recipe': 0, 'mlp + prediction recipe (= E26)': 0}.

### mirror + paper objective

| Block | Presence, nonlinear probe R² | Presence, linear R² | Seeds present (≥ 0.9) |
|---|---|---|---|
| texture (block 1) | 0.997 ± 0.001 | 1.000 ± 0.000 | 5 of 5 |
| identity (block 2) | 0.996 ± 0.001 | 0.998 ± 0.002 | 5 of 5 |
| category (block 3) | 0.996 ± 0.001 | 0.999 ± 0.001 | 5 of 5 |

| Rung | ABSENT | PARTIAL | PRESENT_NOT_SEPARABLE | SPLIT |
|---|---|---|---|---|
| rung 1 (texture) | 0 | 0 | 0 | 5 |
| rung 2 (identity) | 0 | 0 | 0 | 5 |

### mlp + paper objective

| Block | Presence, nonlinear probe R² | Presence, linear R² | Seeds present (≥ 0.9) |
|---|---|---|---|
| texture (block 1) | 0.029 ± 0.004 | 0.000 ± 0.001 | 0 of 5 |
| identity (block 2) | 0.030 ± 0.007 | 0.000 ± 0.001 | 0 of 5 |
| category (block 3) | 0.029 ± 0.008 | 0.000 ± 0.001 | 0 of 5 |

| Rung | ABSENT | PARTIAL | PRESENT_NOT_SEPARABLE | SPLIT |
|---|---|---|---|---|
| rung 1 (texture) | 5 | 0 | 0 | 0 |
| rung 2 (identity) | 5 | 0 | 0 | 0 |

### mirror + prediction recipe

| Block | Presence, nonlinear probe R² | Presence, linear R² | Seeds present (≥ 0.9) |
|---|---|---|---|
| texture (block 1) | 0.994 ± 0.001 | 0.996 ± 0.001 | 5 of 5 |
| identity (block 2) | 0.994 ± 0.001 | 0.995 ± 0.002 | 5 of 5 |
| category (block 3) | 0.994 ± 0.001 | 0.995 ± 0.001 | 5 of 5 |

| Rung | ABSENT | PARTIAL | PRESENT_NOT_SEPARABLE | SPLIT |
|---|---|---|---|---|
| rung 1 (texture) | 0 | 0 | 0 | 5 |
| rung 2 (identity) | 0 | 0 | 0 | 5 |

### mlp + prediction recipe (= E26)

| Block | Presence, nonlinear probe R² | Presence, linear R² | Seeds present (≥ 0.9) |
|---|---|---|---|
| texture (block 1) | 0.991 ± 0.001 | 0.986 ± 0.003 | 5 of 5 |
| identity (block 2) | 0.991 ± 0.001 | 0.986 ± 0.002 | 5 of 5 |
| category (block 3) | 0.991 ± 0.001 | 0.986 ± 0.001 | 5 of 5 |

| Rung | ABSENT | PARTIAL | PRESENT_NOT_SEPARABLE | SPLIT |
|---|---|---|---|---|
| rung 1 (texture) | 0 | 0 | 0 | 5 |
| rung 2 (identity) | 0 | 0 | 0 | 5 |
