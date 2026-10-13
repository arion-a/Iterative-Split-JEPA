# Run status (one line per run; newest last; see docs/REPORTING.md section F)

| Seed | Run | Construction | Headline | Raw result |
|---|---|---|---|---|
| 2 | B2 sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 11.6 deg, B2 11.7 deg | `results/B2/sigma_cat_0.1/2.json` |
| 0 | B2 sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 10.7 deg, B2 14.4 deg | `results/B2/sigma_cat_0.1/0.json` |
| 1 | B2 sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 8.8 deg, B2 8.8 deg | `results/B2/sigma_cat_0.1/1.json` |
| 2 | B2 sigma_cat=0.4 | purity 0.83, K found 5 | rung-2 angle B1 11.1 deg, B2 11.4 deg | `results/B2/sigma_cat_0.4/2.json` |
| 0 | B2 sigma_cat=0.4 | purity 0.96, K found 6 | rung-2 angle B1 10.4 deg, B2 10.7 deg | `results/B2/sigma_cat_0.4/0.json` |
| 1 | B2 sigma_cat=0.4 | purity 0.83, K found 5 | rung-2 angle B1 8.5 deg, B2 8.8 deg | `results/B2/sigma_cat_0.4/1.json` |
| 2 | B2 sigma_cat=0.6 | purity 0.81, K found 5 | rung-2 angle B1 10.8 deg, B2 12.2 deg | `results/B2/sigma_cat_0.6/2.json` |
| 0 | B2 sigma_cat=0.6 | purity 0.85, K found 6 | rung-2 angle B1 10.2 deg, B2 13.7 deg | `results/B2/sigma_cat_0.6/0.json` |
| 1 | B2 sigma_cat=0.6 | purity 0.82, K found 5 | rung-2 angle B1 8.5 deg, B2 9.3 deg | `results/B2/sigma_cat_0.6/1.json` |
| 0 | B2 sigma_cat=0.8 | purity 0.77, K found 7 | rung-2 angle B1 10.2 deg, B2 18.4 deg | `results/B2/sigma_cat_0.8/0.json` |
| 2 | B2 sigma_cat=0.8 | purity 0.78, K found 12 | rung-2 angle B1 10.7 deg, B2 34.6 deg | `results/B2/sigma_cat_0.8/2.json` |
| 1 | B2 sigma_cat=0.8 | purity 0.77, K found 6 | rung-2 angle B1 8.4 deg, B2 10.6 deg | `results/B2/sigma_cat_0.8/1.json` |
| 0 | B2 sigma_cat=1.0 | purity 0.70, K found 11 | rung-2 angle B1 10.1 deg, B2 49.3 deg | `results/B2/sigma_cat_1.0/0.json` |
| 2 | B2 sigma_cat=1.0 | purity 0.70, K found 11 | rung-2 angle B1 10.8 deg, B2 50.8 deg | `results/B2/sigma_cat_1.0/2.json` |
| 1 | B2 sigma_cat=1.0 | purity 0.68, K found 12 | rung-2 angle B1 8.3 deg, B2 82.4 deg | `results/B2/sigma_cat_1.0/1.json` |
| 0 | B2 sigma_cat=1.5 | purity 0.57, K found 12 | rung-2 angle B1 10.1 deg, B2 82.1 deg | `results/B2/sigma_cat_1.5/0.json` |
| 2 | B2 sigma_cat=1.5 | purity 0.52, K found 9 | rung-2 angle B1 10.5 deg, B2 89.6 deg | `results/B2/sigma_cat_1.5/2.json` |
| 1 | B2 sigma_cat=1.5 | purity 0.48, K found 9 | rung-2 angle B1 8.4 deg, B2 79.5 deg | `results/B2/sigma_cat_1.5/1.json` |
| - | Nesting-angle laboratory (2026-10-13) | Owner's lab: inheritance ~90-100% of nesting error, budget lever n^-1/2 (1.37 -> 0.18 deg over 5k..320k pairs), soft tested in 3 regimes. Our replication: inheritance and ideal-world slope -0.51 replicate; in the B2 world the budget lever is flat (rung-1 angle 3-4.7 deg at every budget); B2 nesting 8.5-11.5 deg is mostly the truth-definition gap (11.6-13.0 deg), orthogonal-complement nesting 2.2-3.3 deg; hard = soft at large lambda; foreign-direction regime did not replicate | DECISION: hard default, soft armed but inactive (activate only if truth is outside H_k and reachable without contamination) | `results/diagnostics/nesting/` |
| 0 | B2 [P9 nesting] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 10.7 deg, B2 14.7 deg | `results/stage_b2_nesting/sigma_cat_0.1/0.json` |
| 2 | B2 [P9 nesting] sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 11.6 deg, B2 11.6 deg | `results/stage_b2_nesting/sigma_cat_0.1/2.json` |
| 1 | B2 [P9 nesting] sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 8.6 deg, B2 8.7 deg | `results/stage_b2_nesting/sigma_cat_0.1/1.json` |
| - | **P9 outcome (2026-10-13): REFUTED as worded** | B1 nesting 1.28 -> 1.22 deg (already < 2); B2 arm 10.39 -> 10.31 deg (gate definition), 2.82 deg vs orthogonal-complement truth; B2-B1 nesting gap +0.10 deg (confirmed ~0); other gates held; rank check 3/3 before and after. Cause: rung-1 angle is an encoder-bias floor (unchanged by doubling budget) and the gate definition adds a ~12 deg truth gap. B2 in clean world only. | Follow-ups P10, P11 registered in EVIDENCE.md | `results/stage_b1_nesting/`, `results/stage_b2_nesting/` |
