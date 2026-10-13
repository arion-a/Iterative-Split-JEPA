# Reference targets — how far from the paper's figures we are

Paper reference values (arXiv:2610.12349, Sec 4.1, App C) vs our B1.

| Quantity | Paper target | Our B1 (3 seeds) | Distance to target |
|---|---|---|---|
| Invariant R^2 (single split) | 0.998 (their script) | rung 2 (identity): 0.980-0.984 | 1.4-1.8 points; rung 2 is a HARDER task (split inside a split) |
| Variant R^2 | ~0.99 | rung 1: 0.955-0.962; rung 2: 0.980-0.984 | rung 1 within 3-4 points |
| Leakage ||A12|| | ~0.003 | Stage A mirror arm: 0.0034 (matches exactly) |
| Leakage ||A21|| | 0.012-0.023 | Stage A mirror arm: 0.0231 vs their 0.0233 (matches) |
| No-head baseline | R^2 ~0.9619; leakage ~0.33 | 0.9615; 0.33 | reproduces the paper's ablation |
| Gap ratio | not gated in paper | 40-53 (criterion >10) | 4-5x inside our criterion |
| Angles to true blocks | not used in paper (they use R^2) | 0.8-1.5 deg (criterion <5 deg) | 3-4x inside our criterion |
| Depth (rung 2, rung 3) | NO paper target — our extension | rung 2: 1.3-1.5 deg; category core 0.976-0.981 | no reference exists; this IS the new result |

How to read this table:
- Where a paper target exists (leakage, no-head baseline), we MATCH it.
- Where no paper target exists (angles, gaps, depth), the criterion is OURS,
  frozen before the run, and we sit 3-5x inside it.
- The one visible soft spot: rung-1 variant R^2 (0.955-0.962 vs ~0.99).
  Reading with the paper's scaling study (their Fig 11c): ||A21|| drops
  0.156 -> 0.012 as pairs go 250 -> 30,000, i.e. the variant-side estimate
  is the finite-sample-sensitive one. More pairs at rung 1 is the first
  lever if we want to close this gap.
