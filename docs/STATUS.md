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

| - | **Stage V handshake (2026-10-20)** | 3 seeds, 64-d encoder, additive-illumination nuisance | E31c' confirmed (V 0.003, ICC 0.973, L 0.993, rollout 0.232); E31d refuted (|Spearman| 0.786); E31e S1-at-lag-32 refuted (2/3 seeds); P-stab refuted (0.766); controls met; shuffled arm matches main (finding) | `results/handshake/REPORT.md` |
| - | **Stage V hierarchical (2026-10-20)** | AR world a=(.2,.5,.75,.9,.95), lags 1,2,4,8, 3 seeds | E35 refuted: RUNGS 1 (registered 4); found rung passes R2/(D)/(C)/L; shuffled control RUNGS 0 | `results/hier/REPORT.md` |
| - | **Stage V real video (2026-10-20)** | 10 public clips, informational | certificate passes trivially (V 0, ICC 0.989) but psi does not track tracker proxies (|Spearman| 0.11 / 0.31): likely per-clip appearance; owner capture blocked | `results/real/REPORT.md` |

| - | **Stage V F1 follow-up (2026-10-20)** | 3 seeds, same encoders as the handshake | F1 refuted: release-free temporal-only arm = main arm (gap 0.000 / 0.000 / −0.010); the discovery is redundantly identified by temporal slowness and by release grouping | `results/followup/*.json` |

| - | **Stage V E36 (2026-10-20)** | coupled vs uncoupled two-block world, 3 seeds | refuted as worded: (S) passes 6/6, control ratio 1.000, coupled ratio [1.252, 1.319, 1.247] (needed ≥ 2.0); world arithmetic 3.1 verified | `results/e36/*.json` |

| - | **Stage V B1 scaling probe (2026-10-20)** | 450 releases, 8000 steps, 3 seeds | confirmed: naming [0.848, 0.683, 0.828] → [0.97, 0.976, 0.978]; E31d still refuted (0.99); seed agreement 0.976-0.981; certificate holds | `results/scaling/main/*.json` |

| - | **Stage V Columbia real clips C1 / C1b (2026-10-20)** | 1100 real clips, 3 seeds, tracked energy as evaluator | C1 refuted as worded (naming [0.893, 0.895, 0.88] passes ≥ 0.5; rollout 0.43-0.45 and ICC 0.898 on seed 1 miss the sim-calibrated certificate); C1b confirmed (flat [0.477, 0.38, 0.471]) | `results/columbia`, `results/columbia_controls` |
