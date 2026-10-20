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
| - | **E9 outcome (2026-10-13): REFUTED as worded** | B1 nesting 1.28 -> 1.22 deg (already < 2); B2 arm 10.39 -> 10.31 deg (gate definition), 2.82 deg vs orthogonal-complement truth; B2-B1 nesting gap +0.10 deg (confirmed ~0); other gates held; rank check 3/3 before and after. Cause: rung-1 angle is an encoder-bias floor (unchanged by doubling budget) and the gate definition adds a ~12 deg truth gap. B2 in clean world only. | Follow-ups E10, E11 registered in EVIDENCE.md | `results/stage_b1_nesting/`, `results/stage_b2_nesting/` |
| 1 | B2 [E10/E10a] sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 8.6 deg, B2 8.7 deg | `results/stage_b2_purify/sigma_cat_0.1/1.json` |
| 0 | B2 [E10/E10a] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 10.7 deg, B2 14.7 deg | `results/stage_b2_purify/sigma_cat_0.1/0.json` |
| 2 | B2 [E10/E10a] sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 11.6 deg, B2 11.6 deg | `results/stage_b2_purify/sigma_cat_0.1/2.json` |
| - | **E10 / E12 outcome (2026-10-14)** | E10 confirmed (definitional, D10): B2 nesting 2.82 deg on the complement reference, 10.31 deg absolute (now informational). E12 confirmed: rung-2 gap 3.1 -> 19.7 (Tier 1) / 18.7 (Tier 1+4); recovered 0.68 / 0.64 of the B1-B2 deficit (needs 0.60); pair validity 0.83 -> 1.00. Item 2 (texture): premise does not hold, all 4 texture directions vary, world not changed. Still failing in both arms: rung-2 angle ~10.5 deg, texture R2 0.882, leakage 0.028 | Clean world, 3 seeds only | `results/stage_b2_purify/` |
| 2 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 11.6 deg, B2 11.6 deg | `results/stage_b2_noop/sigma_cat_0.1/2.json` |
| 0 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 10.7 deg, B2 14.7 deg | `results/stage_b2_noop/sigma_cat_0.1/0.json` |
| 1 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 8.6 deg, B2 8.7 deg | `results/stage_b2_noop/sigma_cat_0.1/1.json` |
| - | **E14 + no-op control (2026-10-14)** | E14 confirmed (no metric damaged; subspace moves 3.6-11.6 deg vs untreated, reported not gated). No-op control: Tier 1 on B1's clean pairs trims 2.3-3.4% of pairs and lifts the rung-2 gap 27.3 -> 30.2; other metrics change < 0.006: not a strict no-op (strict and practical readings both fail). E13 deferred | Clean world, 3 seeds | `results/stage_b2_noop/` |
| - | **Gap-ratio fix closed (2026-10-14)** | Verdict: E12 confirmed (0.64; gap 17.0/19.5/19.5), E14 confirmed (subspace 0.76-1.41 deg from the clean one), no-op control not a strict no-op (2.3-3.4% of clean pairs trimmed), Tier 4 demoted (D11). Pending: E13 sweep (scheduled, GPU/overnight), probes (not run), Tier 2 rebuild (deferred, unsupervised). Tier 2 diagnosis: closest category pair ~1 radius apart, silhouette prefers 5 over 6 | Brief: `docs/FIXES/2026-10-13_gap_ratio.md` | `results/diagnostics/tier2/` |

| - | **No-op control ruling and analyses (2026-10-14)** | Owner: no-op control PASS under corrected criterion (D12 candidate; strict reading refuted-and-replaced). Trimmed fraction: B2 18.1% vs B1 clean 2.7%, excess 14.7-15.9% = rho-hat (true 16.5-17.0%). Purification moves the rung-2 subspace onto the clean B1 reference; toward the true identity subspace only on seed 0 (-4.0 deg), under 0.06 deg on seeds 1, 2. E14 stands confirmed (post-hoc criterion); blind re-check frozen inside the E13 sweep, which is SCHEDULED (GPU/overnight), not run | | `results/stage_b2_noop/ANALYSIS.md` |

| - | **Attribution battery E15-E17 (2026-10-14)** | E15: full-feature texture probe 0.894 / 0.907 / 0.930 vs recovered block 0.862 / 0.887 / 0.897; 76% of the texture shortfall is already in the probe (encoder side), 24% lost by the block; rule covers only seed 0 (encoder), seeds 1-2 in the uncovered 0.9-0.95 band, no seed reaches 0.95. E16: texture is not discrete or one-directional; world ruled out, no regeneration. E17: leakage gate re-frozen on normalized ||A21|| < 0.0209 (D13), retrospective: B1 arm meets it on 1 of 3 seeds, B2 arms 0, rung 1 0. E11 not scheduled pending owner call | `configs/gates_v2.yaml` | `results/diagnostics/attribution_battery/REPORT.md` |

| - | **E11 registered, scheduled, not run (2026-10-14)** | Owner ruling: E15's 0.9-0.95 band counts as the encoder branch (post-hoc amendment, all three seeds read encoder-limited). E11a multi-step prediction first, then E11b longer training (40,000 steps); floor-lowering prediction: texture probe >= 0.95 every seed, mean rung-1 angle <= 2.8 deg, mean B1-arm rung-2 angle <= 7.7 deg (thresholds Claude's, flagged). Claude caveat recorded: multi-step may not help the fast texture block | Needs a horizon option in train_encoder first | `docs/EVIDENCE.md` |
| 2 | B2 [E11a] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 11.5 deg, B2 11.7 deg | `results/stage_b2_e11a/sigma_cat_0.1/2.json` |
| 0 | B2 [E11a] sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 10.7 deg, B2 16.6 deg | `results/stage_b2_e11a/sigma_cat_0.1/0.json` |
| 1 | B2 [E11a] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 8.1 deg, B2 8.3 deg | `results/stage_b2_e11a/sigma_cat_0.1/1.json` |

| - | **E11a outcome (2026-10-14): REFUTED** | Horizon-3 alignment: texture probe 0.880 / 0.853 / 0.937 (needs 0.95; baseline 0.894 / 0.907 / 0.930), mean rung-1 angle 4.45 (baseline 3.78, needs 2.8), B1-arm rung-2 angle 10.10 (baseline 10.30, needs 7.7). Multi-step alignment did not lower the floor and slightly worsened it; matches the recorded caveat. First run under the new leakage gate: not met (0.044 B1 arm). Tier 1 gap recovery replicated (0.70). E11b next, not started | Horizon option built; horizon-1 path verified identical | `results/stage_b2_e11a/` |
| 1 | B2 [E11b] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 8.8 deg, B2 8.9 deg | `results/stage_b2_e11b/sigma_cat_0.1/1.json` |
| 2 | B2 [E11b] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 11.7 deg, B2 11.7 deg | `results/stage_b2_e11b/sigma_cat_0.1/2.json` |
| 0 | B2 [E11b] sigma_cat=0.1 | purity 1.00, K found 6 | rung-2 angle B1 9.8 deg, B2 9.8 deg | `results/stage_b2_e11b/sigma_cat_0.1/0.json` |

| - | **E11b outcome (2026-10-14): REFUTED** | 40,000 steps: texture probe 0.892 / 0.905 / 0.932 (baseline 0.894 / 0.907 / 0.930), mean rung-1 angle 3.63 (baseline 3.78), B1-arm rung-2 angle 10.08 (baseline 10.30): no change beyond seed noise. E11a and E11b both refuted; the encoder floor is not moved by multi-step alignment or 4x training. Side observation: seed 0 found K = 6 (purity 0.999), the only run where the clusterer found all six categories | Encoder cause still unidentified | `results/stage_b2_e11b/` |
| 2 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 11.6 deg, B2 11.6 deg | `results/stage_b2_gapfix_sweep/sigma_cat_0.1/2.json` |
| 0 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 10.7 deg, B2 14.7 deg | `results/stage_b2_gapfix_sweep/sigma_cat_0.1/0.json` |
| 1 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 8.6 deg, B2 8.7 deg | `results/stage_b2_gapfix_sweep/sigma_cat_0.1/1.json` |
| 2 | B2 [no-op control + E10c] sigma_cat=0.4 | purity 0.83, K found 5 | rung-2 angle B1 11.0 deg, B2 11.3 deg | `results/stage_b2_gapfix_sweep/sigma_cat_0.4/2.json` |
| 0 | B2 [no-op control + E10c] sigma_cat=0.4 | purity 0.97, K found 6 | rung-2 angle B1 10.5 deg, B2 10.6 deg | `results/stage_b2_gapfix_sweep/sigma_cat_0.4/0.json` |
| 1 | B2 [no-op control + E10c] sigma_cat=0.4 | purity 0.99, K found 6 | rung-2 angle B1 8.4 deg, B2 8.5 deg | `results/stage_b2_gapfix_sweep/sigma_cat_0.4/1.json` |
| 2 | B2 [no-op control + E10c] sigma_cat=0.6 | purity 0.85, K found 6 | rung-2 angle B1 10.7 deg, B2 13.2 deg | `results/stage_b2_gapfix_sweep/sigma_cat_0.6/2.json` |
| 0 | B2 [no-op control + E10c] sigma_cat=0.6 | purity 0.85, K found 6 | rung-2 angle B1 10.2 deg, B2 13.0 deg | `results/stage_b2_gapfix_sweep/sigma_cat_0.6/0.json` |
| 1 | B2 [no-op control + E10c] sigma_cat=0.6 | purity 0.84, K found 6 | rung-2 angle B1 8.4 deg, B2 10.4 deg | `results/stage_b2_gapfix_sweep/sigma_cat_0.6/1.json` |
| 2 | B2 [no-op control + E10c] sigma_cat=0.8 | purity 0.75, K found 9 | rung-2 angle B1 10.6 deg, B2 28.2 deg | `results/stage_b2_gapfix_sweep/sigma_cat_0.8/2.json` |
| 1 | B2 [no-op control + E10c] sigma_cat=0.8 | purity 0.74, K found 12 | rung-2 angle B1 8.4 deg, B2 69.6 deg | `results/stage_b2_gapfix_sweep/sigma_cat_0.8/1.json` |
| 0 | B2 [no-op control + E10c] sigma_cat=0.8 | purity 0.77, K found 11 | rung-2 angle B1 10.2 deg, B2 25.0 deg | `results/stage_b2_gapfix_sweep/sigma_cat_0.8/0.json` |
| 1 | B2 [no-op control + E10c] sigma_cat=1.0 | purity 0.65, K found 10 | rung-2 angle B1 8.3 deg, B2 83.5 deg | `results/stage_b2_gapfix_sweep/sigma_cat_1.0/1.json` |
| 0 | B2 [no-op control + E10c] sigma_cat=1.0 | purity 0.69, K found 10 | rung-2 angle B1 10.1 deg, B2 50.6 deg | `results/stage_b2_gapfix_sweep/sigma_cat_1.0/0.json` |
| 2 | B2 [no-op control + E10c] sigma_cat=1.0 | purity 0.71, K found 12 | rung-2 angle B1 10.7 deg, B2 61.9 deg | `results/stage_b2_gapfix_sweep/sigma_cat_1.0/2.json` |
| 0 | B2 [no-op control + E10c] sigma_cat=1.5 | purity 0.54, K found 9 | rung-2 angle B1 10.0 deg, B2 79.8 deg | `results/stage_b2_gapfix_sweep/sigma_cat_1.5/0.json` |
| 1 | B2 [no-op control + E10c] sigma_cat=1.5 | purity 0.52, K found 10 | rung-2 angle B1 8.4 deg, B2 87.9 deg | `results/stage_b2_gapfix_sweep/sigma_cat_1.5/1.json` |
| 2 | B2 [no-op control + E10c] sigma_cat=1.5 | purity 0.54, K found 10 | rung-2 angle B1 10.5 deg, B2 84.0 deg | `results/stage_b2_gapfix_sweep/sigma_cat_1.5/2.json` |

| - | **E13 outcome (2026-10-15): REFUTED as registered** | 18-run sweep. Contamination model: log-gap R2 0.667 (needs 0.8), purified above the curve in 10 of 17 runs (needs 90%). Tier 1 recovers the gap only in the clean world (sigma_cat 0.1: 2.7-3.9 -> 17.6-22.2); from sigma_cat 0.4 up it stays at 1-6 because cluster pairs carry within-category energy (observed: 0.342 vs 0.047 at sigma 0.4 seed 1 with 98% valid pairs). rho-hat valid only at sigma 0.1. Blind E14: no damage 18/18, subspace no farther in 14/18 (the 4 are runs where nothing was trimmed). Tier 4: no case (CV 1.38 vs 1.42). The E12 fix does not generalise across the sweep | Exploratory refit R2 0.714, a lead only | `results/stage_b2_gapfix_sweep/` |

| - | **Post-sweep recommended actions (2026-10-16)** | (1) D14 candidate: cluster-built gap judged against 0.6 x the perfect-cluster gap; E20 registered. Retrospective: sigma 0.4 Tier 1 meets it 3/3, sigma 0.6 neither arm (0.47-0.59), so 'clear at 0.4-0.6' is supported at 0.4 only; blind check on fresh seeds scheduled, not run. (2) Encoder-floor narrative retired: texture R2 and rung-1 angle shortfall are specific to sigma_cat 0.1; E11 reframed as not the binding constraint. (3) E18 (spectral K) drafted, E19 (world geometry) reserved pending definition; nothing built. (4) Theory erratum: the clean floor is the perfect-cluster eigenvalue, not the twins' (corrected model R2 0.810, post hoc) | | `results/stage_b2_gapfix_sweep/RECALIBRATION.md` |
| 3 | B2 [no-op control + E10c] sigma_cat=0.4 | purity 0.84, K found 5 | rung-2 angle B1 11.5 deg, B2 12.5 deg | `results/stage_b2_e20_blind/sigma_cat_0.4/3.json` |
| 5 | B2 [no-op control + E10c] sigma_cat=0.4 | purity 0.83, K found 5 | rung-2 angle B1 13.6 deg, B2 17.7 deg | `results/stage_b2_e20_blind/sigma_cat_0.4/5.json` |
| 4 | B2 [no-op control + E10c] sigma_cat=0.4 | purity 0.93, K found 9 | rung-2 angle B1 6.2 deg, B2 9.1 deg | `results/stage_b2_e20_blind/sigma_cat_0.4/4.json` |
| 3 | B2 [no-op control + E10c] sigma_cat=0.6 | purity 0.82, K found 6 | rung-2 angle B1 11.0 deg, B2 13.2 deg | `results/stage_b2_e20_blind/sigma_cat_0.6/3.json` |
| 4 | B2 [no-op control + E10c] sigma_cat=0.6 | purity 0.85, K found 8 | rung-2 angle B1 5.8 deg, B2 23.2 deg | `results/stage_b2_e20_blind/sigma_cat_0.6/4.json` |
| 5 | B2 [no-op control + E10c] sigma_cat=0.6 | purity 0.82, K found 11 | rung-2 angle B1 13.4 deg, B2 37.9 deg | `results/stage_b2_e20_blind/sigma_cat_0.6/5.json` |

| - | **E20 blind outcome (2026-10-16): NOT CONFIRMED as worded** | Fresh seeds 3-5: recalibrated gap criterion (0.6 x perfect-cluster gap) met by B2 + Tier 1 on 3/3 at sigma_cat 0.4 (ratios 0.62-0.76) and 1/3 at 0.6 (0.64 / 0.49 / 0.45). The two failing seeds at 0.6 found 8 and 11 clusters (passing seed 6): cluster-count instability. Corrected contamination model (v_cat frozen at 2.14): median error 0.24, passes narrowly (3 of 6 runs above 25%) | Blind; seeds 3-5 | `results/stage_b2_e20_blind/` |

| - | **E18 built (2026-10-16), not run** | `spectral_k` selector (Laplacian eigengap on a 15-NN self-tuning graph, K in 2..12, no labels), optional arms `b2_spectral` / `b2_spectral_purified` behind `cluster.spectral_k`, constants fixed beforehand; 3 new unit tests (44 pass); default pipeline behaviour unchanged. Run on the B2 world awaits go-ahead | Prediction (draft): K = 6 on every seed at sigma_cat 0.1, 0.4, 0.6 | `configs/stage_b2_e18.yaml` |
| 1 | B2 [E18] sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 8.6 deg, B2 8.7 deg | `results/stage_b2_e18/sigma_cat_0.1/1.json` |
| 2 | B2 [E18] sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 11.6 deg, B2 11.6 deg | `results/stage_b2_e18/sigma_cat_0.1/2.json` |
| 0 | B2 [E18] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 10.7 deg, B2 14.7 deg | `results/stage_b2_e18/sigma_cat_0.1/0.json` |
| 3 | B2 [E18] sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 12.3 deg, B2 14.7 deg | `results/stage_b2_e18/sigma_cat_0.1/3.json` |
| 4 | B2 [E18] sigma_cat=0.1 | purity 0.98, K found 6 | rung-2 angle B1 5.8 deg, B2 8.0 deg | `results/stage_b2_e18/sigma_cat_0.1/4.json` |
| 5 | B2 [E18] sigma_cat=0.1 | purity 0.98, K found 7 | rung-2 angle B1 14.2 deg, B2 14.3 deg | `results/stage_b2_e18/sigma_cat_0.1/5.json` |
| 0 | B2 [E18] sigma_cat=0.4 | purity 0.97, K found 6 | rung-2 angle B1 10.5 deg, B2 10.6 deg | `results/stage_b2_e18/sigma_cat_0.4/0.json` |
| 2 | B2 [E18] sigma_cat=0.4 | purity 0.83, K found 5 | rung-2 angle B1 11.0 deg, B2 11.3 deg | `results/stage_b2_e18/sigma_cat_0.4/2.json` |
| 1 | B2 [E18] sigma_cat=0.4 | purity 0.99, K found 6 | rung-2 angle B1 8.4 deg, B2 8.5 deg | `results/stage_b2_e18/sigma_cat_0.4/1.json` |
| 3 | B2 [E18] sigma_cat=0.4 | purity 0.84, K found 5 | rung-2 angle B1 11.5 deg, B2 12.5 deg | `results/stage_b2_e18/sigma_cat_0.4/3.json` |
| 5 | B2 [E18] sigma_cat=0.4 | purity 0.83, K found 5 | rung-2 angle B1 13.6 deg, B2 17.7 deg | `results/stage_b2_e18/sigma_cat_0.4/5.json` |
| 4 | B2 [E18] sigma_cat=0.4 | purity 0.93, K found 9 | rung-2 angle B1 6.2 deg, B2 9.1 deg | `results/stage_b2_e18/sigma_cat_0.4/4.json` |
| 0 | B2 [E18] sigma_cat=0.6 | purity 0.85, K found 6 | rung-2 angle B1 10.2 deg, B2 13.0 deg | `results/stage_b2_e18/sigma_cat_0.6/0.json` |
| 2 | B2 [E18] sigma_cat=0.6 | purity 0.85, K found 6 | rung-2 angle B1 10.7 deg, B2 13.2 deg | `results/stage_b2_e18/sigma_cat_0.6/2.json` |
| 1 | B2 [E18] sigma_cat=0.6 | purity 0.84, K found 6 | rung-2 angle B1 8.4 deg, B2 10.4 deg | `results/stage_b2_e18/sigma_cat_0.6/1.json` |
| 3 | B2 [E18] sigma_cat=0.6 | purity 0.82, K found 6 | rung-2 angle B1 11.0 deg, B2 13.2 deg | `results/stage_b2_e18/sigma_cat_0.6/3.json` |
| 5 | B2 [E18] sigma_cat=0.6 | purity 0.82, K found 11 | rung-2 angle B1 13.4 deg, B2 37.9 deg | `results/stage_b2_e18/sigma_cat_0.6/5.json` |
| 4 | B2 [E18] sigma_cat=0.6 | purity 0.85, K found 8 | rung-2 angle B1 5.8 deg, B2 23.2 deg | `results/stage_b2_e18/sigma_cat_0.6/4.json` |

| - | **E18 outcome (2026-10-16): REFUTED** | Spectral K = 6 in 1 of 18 runs (0/6 at sigma_cat 0.1, 0/6 at 0.4, 1/6 at 0.6); it overestimates K by 2-6 at 0.1 and 0.4 (8-12) and scatters 2-12 at 0.6; the largest eigengap is only 1.1-3.3x the second. Silhouette finds 6 in 7 of 18. Hypothesis (untested): identity sub-clusters inside the 8-D invariant output. Selector kept as an option, constants unchanged | 18 runs, frozen rule | `results/stage_b2_e18/` |
| 20 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 11.4 deg, B2 11.6 deg | `results/stage_b2_e21/sigma_cat_0.1/20.json` |
| 21 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 9.9 deg, B2 10.0 deg | `results/stage_b2_e21/sigma_cat_0.1/21.json` |
| 22 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 9.5 deg, B2 10.0 deg | `results/stage_b2_e21/sigma_cat_0.1/22.json` |
| 23 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 7.0 deg, B2 8.0 deg | `results/stage_b2_e21/sigma_cat_0.1/23.json` |
| 24 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.84, K found 5 | rung-2 angle B1 9.4 deg, B2 11.3 deg | `results/stage_b2_e21/sigma_cat_0.1/24.json` |
| 25 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 1.00, K found 6 | rung-2 angle B1 13.1 deg, B2 13.2 deg | `results/stage_b2_e21/sigma_cat_0.1/25.json` |
| 26 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 10.2 deg, B2 10.3 deg | `results/stage_b2_e21/sigma_cat_0.1/26.json` |
| 27 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 11.2 deg, B2 11.3 deg | `results/stage_b2_e21/sigma_cat_0.1/27.json` |
| 28 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 11.1 deg, B2 11.1 deg | `results/stage_b2_e21/sigma_cat_0.1/28.json` |
| 29 | B2 [no-op control + E10c] sigma_cat=0.1 | purity 0.83, K found 5 | rung-2 angle B1 7.4 deg, B2 8.3 deg | `results/stage_b2_e21/sigma_cat_0.1/29.json` |
| 20 | B2 [no-op control + E10c] sigma_cat=0.4 | purity 0.83, K found 5 | rung-2 angle B1 11.1 deg, B2 11.4 deg | `results/stage_b2_e21/sigma_cat_0.4/20.json` |
