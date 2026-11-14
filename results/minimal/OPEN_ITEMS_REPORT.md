# The open Stage C and Stage D items (E48-E51); frozen criteria `configs/open_items.criteria.yaml`

| Item | Verdict |
|---|---|
| E48 | CONFIRMED |
| E49 | REFUTED |
| E50 | CONFIRMED |
| E51 | REFUTED |

## E48 (the 1/sqrt(n) rate with a learned encoder, against the encoder's own eigenspace): CONFIRMED
| Rung | Slope | 95% interval | Mean angle (deg) at n = 1000, 10000, 100000 |
|---|---|---|---|
| 1 | -0.48 | [-0.51, -0.44] | 0.379, 0.095, 0.042 |
| 2 | -0.48 | [-0.52, -0.45] | 0.375, 0.097, 0.041 |

## E49 (the E45 recipe on fresh seeds): REFUTED
- 4 blocks (10 seeds): clean rungs by rung [10, 6, 10] (needs 7), no dead direction 10 (needs 9), core present 10 (needs 7): NOT met
- 5 blocks (10 seeds): clean rungs by rung [10, 9, 10, 10] (needs 7), no dead direction 10 (needs 9), core present 10 (needs 7): met

## E50 (a flat one-shot split from the pooled correspondence families, equal speeds): CONFIRMED
Pooled one-shot worst angle under 5 on 5 of 5 (needs 4); its block-1 / block-2 gap under 5 on 5 of 5; the ladder's smallest rung gap over 10 on 5 of 5 (both need 5).

| Seed | Pooled angles (deg) | Pooled gaps (b1/b2, b2/core) | Ladder rung gaps |
|---|---|---|---|
| 210 | 1.6, 2.1 | 1.92, 89.1 | 180, 164 |
| 211 | 1.4, 2.2 | 1.93, 42883.4 | 91645, 73181 |
| 212 | 1.2, 1.9 | 1.91, 375.2 | 543, 638 |
| 213 | 1.8, 2.7 | 1.89, 101.0 | 216, 185 |
| 214 | 1.1, 1.9 | 1.93, 48127.7 | 75022, 91359 |

## E51 (does the invariant core pay under a nuisance shift): REFUTED
Core-only readout shifted R2 at least 0.9 on 5 of 5; beats the whole-embedding readout by at least 0.2 on 0; without the shift the two differ by under 0.05 on 5 (each needs 4).

| Seed | Whole: correlated / shifted R2 | Core only: correlated / shifted R2 |
|---|---|---|
| 210 | 0.99 / 0.95 | 0.99 / 0.99 |
| 211 | 0.99 / 0.96 | 1.00 / 1.00 |
| 212 | 0.99 / 0.96 | 1.00 / 1.00 |
| 213 | 0.99 / 0.96 | 0.99 / 0.99 |
| 214 | 0.99 / 0.96 | 1.00 / 1.00 |
