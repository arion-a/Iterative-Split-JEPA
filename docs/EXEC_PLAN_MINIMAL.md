# Execution plan: the four minimal claims

Written 2026-10-22. Reasoning for each claim is in `docs/PLAN_MINIMAL_CLAIMS.md`; this file is the runnable version. **Nothing here has been started or registered; it begins only on the owner's go.** Tick boxes as steps finish.

Rules that hold throughout: predictions and criteria are frozen by hash before any run; no tuning after a result; a refuted claim is reported and that claim stops; `docs/EVIDENCE.md` gains lines only; runs are ground-truth-pair, hard-nesting, rung gate on (E33); single-threaded, at most four runs at once.

## The four numbers (all thresholds already in use)

| Metric | Definition | Pass |
|---|---|---|
| **Angle** | Worst principal angle between the found block and the true block (probe-recovered image) | under 5 degrees |
| **Gap ratio** | Eigenvalue ratio lambda_d / lambda_(d+1) of the rung's pair-difference moment | over 10 |
| **Presence** | Held-out R2 of a 2-layer tanh readout of each true block from the whole whitened embedding | at least 0.95 |
| **rho_k** | Held-out error of predicting the future of the kept content (horizon h_k = ceil(-1/ln of the layer's world speed)) from the kept content, divided by the same error from the content before the rung (equal-capacity ridge) | at most 1.05 |

Reported only: single-shot angle (one eigendecomposition of the adjacent-frame difference moment, blocks read off in eigenvalue order); largest off-diagonal leakage R2.

## Experiments, passing results, verdicts

| ID | Claim | Config | Arms, seeds | Runs | Pass (frozen before runs) |
|---|---|---|---|---|---|
| **E38** | 2. Correspondence, not speed, carries the split | `minimal_c2.yaml`: 3 blocks of 4, speeds all 0.5, mirror encoder, 30k pairs | main, seeds 120-124 (the separated-speed cell is the existing E37 file, same seeds) | 5 | At equal speeds, worst ladder angle under 5 on 5 of 5 seeds **and** worst single-shot angle 5 or more on 5 of 5 seeds. Separated-speed cell: both under 5 (already recorded). |
| **E39** | 1. Nested identification to depth 5, predictively sufficient | `minimal_c1.yaml`: 5 blocks of 4, speeds 0.2 / 0.45 / 0.7 / 0.85 / 0.95, mirror encoder, 30k pairs | main and shuffled_rung2, seeds 130-134 | 10 | Main: each of angle, gap, presence (all five blocks) and rho_k holds at every rung on at least 4 of 5 seeds. Control: rung-2 gap under 2 and rho_2 over 1.05 on at least 4 of 5 seeds. If the control's rho_2 fails, rho_k is declared not informative and dropped; the claim is then judged on angle, gap and presence. |
| **E40** | 4. The theory's invariance term restores presence for a generic encoder | `minimal_c4_baseline.yaml` (E25 cell: MLP, prediction objective, speeds 0.2 / 0.7 / 0.95); `minimal_c4_treated.yaml` (same plus `corr_inv_weight: 1.0`, fixed, never tuned) | both arms, seeds 140-149 | 20 | Treated: presence at least 0.95 for all three blocks, and both rungs with angle under 5 and gap over 10, on at least 9 of 10 seeds. Baseline: texture presence under 0.5 on at least 9 of 10 seeds (otherwise the contrast is vacuous and the result is "not informative"). |
| **E41** | 3. A violated hypothesis shows up in the gap | no runs; scored on the main arms of E38-E40 | all 30 main-arm runs | 0 | Among rungs with gap over 10 and presence at least 0.95, at least 95% have angle under 5; among rungs with gap 10 or less, at most 10% do. Each cell needs at least 10 rungs, otherwise "not informative". |

Verdict per claim: **confirmed** if every pass line holds; **refuted** if any fails (the failing line is the located limit); **not informative** only where stated. **Total 35 new runs**, about 2 to 3 hours on four cores (order of magnitude from E33 / E35, not measured for these settings).

## Steps

### Phase 0: freeze (no runs)
- [x] 0.1 Owner approves, edits or drops claims; confirms the invariance weight (1.0) and the rho_k reading.
- [x] 0.2 Write the E38-E41 registration into `docs/EVIDENCE.md` (the table above, predictions flagged as Claude's), `configs/minimal.criteria.yaml` and its hash file, and `experiments/analyse_minimal.py` (reads only the numbers above and applies the rules). **Done when** `check_results.py evidence` passes and the hash is committed.
- [x] 0.3 One line in `docs/STATUS.md`: items cut in `docs/PLAN_MINIMAL_CLAIMS.md` section 3 are not used for these claims (nothing deleted).

### Phase 1: code (smallest set)
- [x] 1.1 `BlockWorld.lag_pairs(n, h)` (the h-step AR(1) transition), plus the `predictive` option in `run_stage_b1.py` computing rho_k per rung, and a `minimal` option that skips the permutation-null leakage audit and the linear presence probe. **Done when** a 3-block smoke run writes rho_k and `pytest` passes (52 tests).
- [x] 1.2 `corr_inv_weight` in `train_encoder`: the existing objective plus, for each k, the mean squared distance between the later-block outputs of the two members of a pair from `world.correspondence_pairs(n, k)`. **Done when** a smoke run trains and writes presence.
- [x] 1.3 The shift-readout part of the `payoff` option removed (E37b is dropped); the analysis script reproduces the stored E37 single-shot and ladder angles. **Done when** they match.
- [x] 1.4 The six configs written. **Gate:** tests pass, evidence file unedited, every smoke output has its fields.

### Phase 2: E38 (equal speeds; cheapest, no code beyond the config)
- [x] 2.1 Run the 5 runs. 2.2 Score, record the outcome in `EVIDENCE.md`. **Gate:** 5 of 5 files, finite numbers, evidence unedited. If refuted, report it and stop this claim.

### Phase 3: E39
- [x] 3.1 Run the 10 runs. 3.2 Score and record; state whether rho_k was informative. **Gate** as above.

### Phase 4: E40 and E41
- [x] 4.1 Run the 20 runs (10 baseline, 10 treated). 4.2 Score E40 and record. **If the treated arm fails:** presence stays a stated precondition, no weight tuning, no other architecture; the programme continues with E41 on what exists.
- [x] 4.3 Score E41 over all 30 main-arm runs and record.

### Phase 5: close
- [ ] 5.1 One page: each claim, its outcome, scope and located limit; the status of each theory statement. 5.2 Refresh `explog/stages.json`, rebuild the log table and page, run tests and `explog.verify()`, push. No merge to `main`.

## How it is run
- One supervisor job file per phase using the existing `supervise_b1.sh` (four at a time, `setsid nohup`, counts reported on change) with a Monitor re-armed every 30 minutes; commit and push at each stop.
- Container restarts kill unfinished runs; each run writes its file complete, so reruns are safe and nothing is overwritten.
- Run order is E38, E39, E40; E38 can start as soon as step 1.1 and its config exist.

## What is deliberately not in this plan
Cluster building from data, robot images and the GPU fine-tune, scaling sweeps, new metrics, any weight or architecture search, geometry and planning. The robot-head repeat of E40 is offered to the owner only after E40 is confirmed.
