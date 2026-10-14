# Evidence registry: pre-registered predictions

**Naming (owner, 2026-10-14).** E-numbers are predictions; P-numbers are report figures only (P1-P8). Mapping from the names used earlier in this repo:
P9 -> E9, P10 -> E10, P11 -> E11 (the nesting items); E10a -> E12, E10b -> E13, E10c -> E14 (the gap-ratio tests).
E12 = at least 60% of the B1-B2 gap deficit recovered; E13 = the contamination model fits across the sigma sweep; E14 = position holds or improves under purification.
The append-only experiment log, the machine-written run lines in `docs/STATUS.md`, and already-generated `REPORT.md` files keep the old names; read them through this mapping.

Created 2026-10-13T22:35Z. Predictions are written before the run and never edited. Outcomes are appended below the prediction.

## E9 (registered 2026-10-13T22:35Z, before any E9 run)

**Run.** Re-run B1 and B2 (docs/B2.md world and protocol) with hard nesting projection ON and the rung-1 pair budget doubled (60,000 against the
previous 30,000); the rung-2 budget is unchanged (30,000). 3 seeds. Results go to `results/stage_b1_nesting/` and `results/stage_b2_nesting/`.

**Prediction (written first, as supplied by the owner).**
* Nesting (both arms) drops toward about 2-4 degrees.
* The B1/B2 nesting gap stays about 0.
* The other gates improve or hold.
* The rank-check pass rate improves with the budget.

**Not part of the prediction (a note added at registration, by Claude).** In the earlier B2 run (results/B2, rung-1 budget 30,000) the nesting angle was
8.6-11.6 degrees while the rung-1 recovery angle was only 3.1-4.6 degrees, so most of that nesting figure is not inherited from rung-1 estimation error.
It is measured against the span of two linear-probe images, which are not orthogonal to the first block's image. Doubling the rung-1 budget therefore
may not move it much. This is a risk flag, not an amended prediction.

**Decision rule.** Confirmed if nesting for both arms falls into roughly 2-4 degrees and the other three statements hold; refuted otherwise. Report
the numbers either way. No parameter tuning to fit.

**Outcome (appended 2026-10-13, after the run): REFUTED as worded. Reports: `results/stage_b1_nesting/REPORT.md`, `results/stage_b2_nesting/REPORT.md`.**
Setup as registered: hard ON, pairs 60,000 / 30,000, 3 seeds. B2 was run in the clean world (sigma_cat 0.1) only, not the full sweep (one CPU); the B1 aggregate file flags leakage under the strict rule (seed 0, rung 1, R2 0.0002); under B1's amended floor-0.01 rule B1 passes every gate.
* *Nesting (both arms) drops toward 2-4 deg:* NOT confirmed. B1: 1.28 -> 1.22 deg (already below 2; no room to drop). B2 arm: 10.39 -> 10.31 deg (gate definition), unchanged. Against the orthogonal-complement truth B2 nesting is 2.82 +/- 0.55 deg, but that definition was not the gate and was in the 2-3 deg range before.
* *B1/B2 nesting gap ~0:* confirmed (B2 minus B1 = +0.10 +/- 0.21 deg, was +0.11).
* *Other gates improve or hold:* held, no change beyond noise. B2 still misses rung-2 angle, texture R2, rung-2 gap (3.1, from the discovered-K merge) and leakage; the B1 arm in the same world misses rung-2 angle, texture R2 and leakage.
* *Rank-check pass rate improves with budget:* no change, 3 of 3 seeds before and after (at ceiling); the new monitor passes 3 of 3 at both rungs.
Mechanism read: doubling the rung-1 budget moved the B2-world rung-1 angle by under 0.02 deg per seed (4.58/3.63/3.11 -> 4.59/3.62/3.12), the encoder-bias floor found in the diagnostics. The ~10 deg gate-definition nesting is the truth-definition gap (inherited 10.7-13.6 deg against span truth vs 3.1-4.6 against orthogonal-complement truth). No tuning done.
Follow-ups, registered as new predictions (not run): E10 - nesting measured against the orthogonal-complement truth (declared before the run as the gate) stays within 2-4 deg for the B2 arm in the clean world; E11 - a better-trained or less-nonlinear encoder lowers the B2-world rung-1 angle floor, and only then does the rung-1 budget start to matter.

## Diagnostic note before the E9 run (2026-10-13, written before any E9 run)

Nesting-angle laboratory (ideal world and B2 world, 3 seeds): inheritance confirmed in the ideal world; the n^-1/2 budget lever holds there but NOT in
the B2 world (rung-1 angle flat 3-4.7 deg from 7.5k to 480k pairs); the B2 span-definition nesting (8.5-11.5 deg) is mostly the truth-definition gap
(11.6-13.0 deg); against the orthogonal-complement truth nesting is 2.2-3.3 deg. E9 is run unchanged. Claude's expectation, recorded now and not
replacing the registered prediction: the span-definition nesting stays above 4 deg in B2 (so E9 as worded is refuted for B2 on that definition) while the
orthogonal-complement nesting lands in 2-4 deg; B1-arm nesting lands in 2-4 deg on either definition; budget doubling changes little.

## E10 (registered 2026-10-14, before the E10 run; this item was called P10 in an earlier Claude note)

**Run.** The next B2 run (clean world, 3 seeds) judges nesting by the D10 definition (orthogonal-complement reference, threshold 5 deg).
**Prediction (owner).** B2-arm nesting is about 3 deg and inside the gate; absolute nesting becomes an informational diagnostic.
**Caveat recorded now.** E9 already read 2.82 +/- 0.55 deg on this definition, so this is a definitional ruling (D10), not an independent test.
**Outcome (2026-10-14): CONFIRMED, as a definitional result.** B2 arm nesting on the D10 reference 2.82 +/- 0.55 deg (treated arm 2.79 +/- 0.50, B1 arm 2.80 +/- 0.48), inside the 5 deg gate on all 3 seeds. Absolute nesting 10.31 +/- 1.61 deg, now informational. Report: `results/stage_b2_purify/REPORT.md`.

## E12 (registered 2026-10-14, before the E12 run)

**Run.** Clean-world B2, 3 seeds, 60,000 / 30,000 pairs, hard nesting. Same encoder and pairs for three rung-2 arms: B2 as before; B2 + Tier 1 purification; B2 + Tier 1 + Tier 4 (D10a constants: factor 4 x median, 5 iterations max).
**Prediction (owner).** The treated arm (Tier 1 + Tier 4) recovers at least 60% of the B1-B2 rung-2 gap-ratio deficit at fixed cluster purity, where recovered = (treated gap - untreated B2 gap) / (B1 gap - untreated B2 gap), means over 3 seeds. Reference from E9: B1 27.3, B2 3.1.
**Decision rule.** Confirmed if recovered >= 0.60; refuted otherwise. Tier 1 alone is reported as informational. No tuning of the D10a constants after seeing results.
**Outcome (2026-10-14): CONFIRMED.** Rung-2 gap ratio: B1 27.3, B2 untreated 3.1, Tier 1 19.7 (recovered 0.68), Tier 1 + Tier 4 18.7 (recovered 0.64; the registered treatment). Pair validity 0.83 -> 1.00 (0.997 on seed 2) at unchanged cluster purity 0.83; 82% of pairs kept, 98-99% of valid pairs kept, 98.5-100% of invalid pairs dropped. Rung-2 gap now passes the gate (>10). Tier 4 added nothing over Tier 1 (gap 18.7 vs 19.7; a21_fro 0.078 vs 0.051). Rung-2 angle (10.6 deg, B1 arm 10.3), texture R2 (0.882) and leakage (0.028) still miss their gates, in the B1 arm as well. Report: `results/stage_b2_purify/REPORT.md`.

## Item 2 check (2026-10-14): texture block rank
The owner's concern: if "2 textures per identity" meant 2 discrete values, the 4-dimensional texture block would have about one direction of variation. Checked on the generator and data (seed 0, clean world): texture centres are random 4-D vectors (240 centres) plus Gaussian jitter in all 4 dimensions. Texture block covariance eigenvalues 1.21 / 1.13 / 1.07 / 1.00; rung-1 pair-difference moment on the texture block 1.38 / 1.22 / 1.10 / 0.92; within-identity centre-difference moment 2.40 / 2.08 / 1.86 / 1.49. All four directions vary, so the premise does not hold in this world and the world was not regenerated. The 0.882 texture R2 therefore has another cause, not identified here.

## Gap-ratio test series, relabelled (owner, 2026-10-14)
E12, E13, E14 are the gap-ratio tests for the purification tiers (E10 itself stays the nesting-definition ruling, D10).
* **E12, effectiveness:** registered above; CONFIRMED (0.64 of the B1-B2 deficit recovered, needs 0.60).
* **E13, contamination-model fit (REGISTERED, NOT RUN, deferred to GPU/overnight):** across the sigma_cat sweep (6 values x 3 seeds = 18 runs) measured rung-2 gap vs cluster purity follows lambda_d2 / (lambda_{d2+1}^clean + rho v_cat), and the purified points sit above that curve. Also covers the Tier 4 check that gap ratios become comparable across the sweep. Protocol and outcome to be written when run.
* **E14, no collateral damage (registered 2026-10-14; criterion stated AFTER the E12 run's numbers were seen, so it is not blind):** purification must not damage the position of the result. For each metric (rung-2 angle, identity R2, category core R2, nesting on the D10 reference, absolute nesting, block purity, a12_fro): the mean over 3 seeds of the treated arm must not be worse than the untreated arm by more than 1 seed-to-seed standard deviation of the untreated arm (improvements are reported, not counted as damage). Position: the angle between the untreated and treated rung-2 variant subspaces is reported per seed.
* **No-op control (registered 2026-10-14, before the run):** run Tier 1 (D10a constants) on B1's clean generator-twin pairs in the same world and encoders. Required outcome as the owner stated it: nothing trimmed and results unchanged (identical). Claude's expectation, recorded now: the strict form will NOT hold, because the rule drops pairs above 4 x the median score, which trims the upper tail of noise even on clean pairs (measured earlier: 1.4-2.1% of valid pairs dropped in B2). I expect about 1-2% of pairs trimmed and every metric within seed noise. Both readings are reported: strict (0 trimmed, identical) and practical (trimmed fraction and metric changes inside seed noise); which counts as the gate is the owner's call.

### Outcomes (2026-10-14), `results/stage_b2_noop/REPORT.md` (the untreated and treated arms reproduce the E12 run exactly)
* **E14: CONFIRMED** on the registered criterion. No metric is worse than untreated by more than 1 untreated seed-std, for Tier 1 and for Tier 1 + Tier 4; every metric moved in the better direction (rung-2 angle 11.68 -> 10.30 / 10.55 deg, a12_fro 0.344 -> 0.305 / 0.318, block purity 0.981 -> 0.987 / 0.986, nesting unchanged at 2.8 deg). Position was reported, not gated: the rung-2 variant subspace moves by 11.6 / 4.6 / 6.4 deg (Tier 1) and 7.4 / 3.6 / 4.1 deg (Tier 1 + Tier 4) per seed against the untreated one. Where it moves relative to the truth or to the B1 subspace was not measured here.
* **No-op control: FAIL on both readings.** Tier 1 on B1's clean pairs trims 2.3%, 2.5% and 3.4% of pairs (684 / 739 / 1020 of 30,000), above the 1-2% I predicted, so the strict reading (nothing trimmed, identical) fails and so does my practical reading (<= 2% trimmed). The effect on the metrics is small: rung-2 angle, identity R2, core R2, nesting and a21_fro change by under 0.006; the rung-2 gap ratio rises from 27.3 to 30.2 (largest per-seed change 3.2, inside one seed-std of 4.6). Reading: the 4 x median rule trims the upper noise tail of clean data and slightly sharpens the spectrum; it does not destroy clean data, but it is not a no-op. Whether that counts as a failure is the owner's call.
* **E13:** not run (deferred).

### Records after the owner's verdict (2026-10-14)
* **E12: CONFIRMED, gate met.** Rung-2 gap ratio per seed, untreated -> registered treatment (Tier 1 + Tier 4): 2.7 -> 17.0, 2.7 -> 19.5, 3.9 -> 19.5 (gate: above 10 on every seed). Tier 1 alone: 19.2, 22.2, 17.6. Recovered fraction of the B1-B2 deficit: 0.64 (needs 0.60); Tier 1 alone 0.68. Tier 4 added nothing and is demoted (D11): after the global ZCA it is close to a no-op.
* **E14 (position holds or improves): CONFIRMED.** No metric damaged (see the E14 criterion above). Position, per seed, angle between the rung-2 variant subspace and the clean B1-arm subspace, untreated -> Tier 1: 11.85 -> 0.76, 5.17 -> 0.90, 6.97 -> 1.41 deg. Purification moves the subspace onto the clean one. Per-seed before/after for the other metrics is in `results/stage_b2_noop/REPORT.md`.
* **E13 (contamination model fits across the sweep): SCHEDULED, not skipped.** 18 runs (6 sigma_cat values x 3 seeds); to run on GPU or overnight. Protocol as registered above.
* **Registered probes (no prediction yet, not run), per D11:** (A) soft redescending weights w = min(1, (c/s)^2) in place of the hard trim; (B) score normalized by the squared pair-difference norm; (C) whitening with the sample covariance over samples. Each needs its own written prediction before it runs. Trigger: no-op control fails or hard trim shows fragility. The no-op control failed on both readings (2.3-3.4% of clean pairs trimmed), so the trigger is met on the strict reading; whether to run them is the owner's call.

### Owner ruling on the no-op control and follow-ups (2026-10-14)
* **No-op control: PASS under the corrected criterion (D12 candidate).** The strict reading is refuted and replaced (reason in D12); the corrected criterion was set after the first result was seen, so this pass is retrospective. Evidence: `results/stage_b2_noop/ANALYSIS.md`.
* **Trimmed fraction as the contamination catch (for E13).** B2 treated runs trim 18.14 / 18.15 / 18.08% of pairs against a B1 clean baseline of 2.28 / 2.46 / 3.40% (mean 2.71%). The excess, 15.9 / 15.7 / 14.7%, is the empirical contamination catch rho-hat. The true mis-grouped fraction (evaluation only) is 17.0 / 16.7 / 16.5%, so rho-hat is a little below it.
* **Movement toward truth (E14 position).** Angle to the true identity subspace, untreated -> Tier 1: 14.74 -> 10.71, 8.66 -> 8.61, 11.65 -> 11.60 deg, while the subspace moved 11.6 / 4.6 / 6.4 deg. Seed 0 moves toward the truth (-4.0 deg); seeds 1 and 2 move onto the clean B1-arm subspace without getting closer to the truth (under 0.06 deg), because the B1 arm itself sits 8.6-11.6 deg from the true identity image. So purification moves the subspace onto the clean reference; the remaining angle to the truth is shared with the B1 arm.
* **E14 stands as CONFIRMED with a post-hoc criterion; blind re-confirmation registered inside the E13 sweep.** Criterion frozen now, before that sweep runs: (i) no metric worse than the untreated arm by more than 1 untreated seed-std (E14 rule above); (ii) in every run, the treated rung-2 subspace is no farther from the clean B1-arm subspace than the untreated one.
* **E13 sweep: SCHEDULED (not skipped), needs a GPU or an overnight window; nothing run.** 6 sigma_cat values (0.1, 0.4, 0.6, 0.8, 1.0, 1.5) x 3 seeds = 18 runs, one process per seed:
  `python experiments/run_stage_b2_spec.py --config configs/stage_b2_noop.yaml --out results/stage_b2_gapfix_sweep --seeds <0|1|2>` (that config has purification, the Tier 4 arm for the comparability check, the B1 no-op arm and saved subspaces). It provides gap-vs-purity for E13, rho-hat per run, and the blind E14 check; results go to a new directory, never overwritten.

## Attribution battery for the three red numbers (owner, 2026-10-14; registered here BEFORE the E15 and E17 runs)
Texture R2 0.882, rung-2 angle about 10 deg and leakage 0.028 have attribution, not a confirmed cause. In every report of this battery the decomposition numbers (theta(H_1, H_1*), inherited versus own error, per seed) are included as informational until the cause is confirmed. No tuning to fit; each outcome gets its own dated entry.

### E15 (registered 2026-10-14, before the run): full-feature texture probe, before any split
**Run.** Clean B2 world, 3 seeds, the same encoders as the E12 run (same seeds). Fit the linear ridge probe from the full whitened encoder features to the true texture block (15,000 train / 5,000 test, as in the pipeline) and report its R2 per seed, next to the recovered rung-1 texture block's variant R2 (0.882).
**Decision rule (owner).** Probe >= 0.95 with the recovered block at 0.882: the split loses texture variance, not the encoder (fix family: rung-1 side - texture variation in pairs, rung-1 budget, gap at the texture boundary). Probe < 0.9: the encoder never encoded texture properly (fix family: multi-step prediction, longer or better training = E11, slower texture timescale). Probe between 0.9 and 0.95: not covered by the rule; reported, neither branch is triggered, owner decides.
**Claude's expectation, recorded now.** The recovered block is a 4-direction linear read of the same features, so its R2 cannot exceed the full-feature probe's; the probe is therefore at least 0.882. I expect it at about 0.88-0.93, i.e. encoder-limited (below 0.95 on every seed).
**Outcome (2026-10-14), `results/diagnostics/attribution_battery/REPORT.md`, `results/diagnostics/e15/`:** probe R2 for the true texture from the full features 0.894 / 0.907 / 0.930 (mean 0.910); recovered texture block 0.862 / 0.887 / 0.897 (mean 0.882; identical to the pipeline run). Rule per seed: seed 0 encoder branch (<0.9); seeds 1 and 2 fall in the 0.9-0.95 band the rule does not cover; no seed reaches 0.95, so the split-loss branch is not supported on any seed. Of the 0.118 texture shortfall, 0.090 (76%) is already in the full-feature probe (encoder side) and 0.028 (24%) is lost by taking the 4-direction block. Texture is the weakest block in the probe (identity 0.93-0.95, category 0.97). Claude's expectation (probe about 0.88-0.93, below 0.95 on every seed) HELD. Reading: the evidence favours an encoder-limited texture block, but the registered rule formally covers only seed 0; the E11 schedule is therefore NOT registered yet and waits for the owner's call on the uncovered band.

### E16 (registered 2026-10-14): is texture discrete-valued per identity in the generator?
**Disclosure.** The generator check was made earlier on 2026-10-14 (item 2 check above), before this registration, so it is not a blind test.
**Answer, from the code and data.** Each identity has two texture centres (a discrete choice of one of two), but each centre is a random 4-D vector and each sample adds Gaussian jitter in all four dimensions (sigma_tex 0.3). Across the 240 centres the texture block has four varying directions: covariance eigenvalues 1.21 / 1.13 / 1.07 / 1.00; rung-1 pair-difference moment 1.38 / 1.22 / 1.10 / 0.92. Within a single identity the systematic variation is along one direction (the centre difference) plus jitter, but the pairs pool over 120 identities, so the pooled moment is full rank. So the block is not discrete-valued and not one-dimensional.
**Outcome (2026-10-14): NO, not discrete-valued and not one-dimensional.** See the answer above; the world is ruled out.
**Consequence.** The conditional branch (regenerate the world with continuous texture and re-run the clean-world B1 arm) is not triggered; the world is ruled out as the cause of the 4-direction concern. Prediction "texture R2 > 0.9 after regeneration" is moot.

### E17 (registered 2026-10-14, before the next run): leakage gate re-referenced to the paper's dimension scaling
**Calculation.** Paper: ||A21||_F normalized = 0.0053 at d = 4 and 0.0325 at d = 64. Power-law interpolation (exponent 0.654) at d = 12 gives 0.0109; sensitivity: linear interpolation 0.0089, log-linear 0.0161. Gate = predicted + 0.01 = **0.0209** (range 0.0189-0.0261 across the three interpolations).
**Gate frozen from the next run on:** ||A21||_F / sqrt(d_V) (the paper's normalized form, both rungs) below 0.0209. The old gate (largest off-diagonal |R2| below 0.01) is retired and recorded as post-hoc; the largest |R2| stays as an informational number.
**Prediction (Claude, recorded now, using data already seen).** On existing clean-world runs, normalized ||A21|| is 0.0157 / 0.0225 / 0.0223 for the B1 arm at rung 2 and 0.046 / 0.039 / 0.032 at rung 1. I therefore expect the new gate to be met on at most one B1-arm seed at rung 2 and to fail at rung 1, i.e. the calibrated gate does not by itself make leakage green. The existing data sit inside the interpolation sensitivity band, so the choice of power law matters for pass/fail on these seeds.

### E17 outcome and gate freeze (2026-10-14)
Gate frozen in `configs/gates_v2.yaml` (sha256 `bd04cd06...b027` in `configs/gates_v2.sha256`): normalized ||A21||_F below 0.0209 at both rungs, effective from the next run; the old post-hoc gate is retired. Prediction (made with existing data in view) HELD retrospectively: rung-2 B1 arm 0.0157 / 0.0225 / 0.0223 meets the gate on 1 of 3 seeds; B2 untreated (0.107 / 0.062 / 0.050) on 0; B2 + Tier 1 (0.021 / 0.026 / 0.028) on 0; rung 1 (0.046 / 0.039 / 0.032) on 0. The calibrated gate by itself does not turn leakage green; with the interpolation band 0.0189-0.0261 the B1-arm pass count would change, so the interpolation choice is flagged in D13.

### Ruling on the E15 rule (owner, 2026-10-14): the 0.9-0.95 band counts as the encoder branch
The E15 decision rule is amended to: probe >= 0.95 -> split loses texture; probe < 0.95 -> encoder-limited. The amendment was made after the E15 numbers were seen (seeds 1 and 2 fell in the band the original rule did not cover), so it is post-hoc and recorded as such. Under the amended rule E15 reads encoder-limited on all three seeds (probe 0.894 / 0.907 / 0.930). The E15 outcome above is left as written.

## E11 (registered 2026-10-14, before any E11 run; SCHEDULED, NOT RUN): lowering the encoder floor
Supersedes the one-line follow-up under E9 (which was labelled P11 at the time). Purpose: E15 puts about three quarters of the texture shortfall on the encoder side; the rung-1 angle floor (3.1-4.6 deg), the rung-2 angle about 10 deg (inherited) and the texture R2 0.882 are the attributed symptoms. Each variant changes only the encoder training; world, seeds, split and gates are unchanged (clean B2 world, sigma_cat 0.1, seeds 0-2, 60,000 / 30,000 pairs, hard nesting, Tier 1 purification as in the E12 run). Baseline numbers are those of the E12 run (`results/stage_b2_noop/`, E15 `results/diagnostics/e15/`).
**E11a, multi-step prediction (runs first).** The predictor is trained to predict the representation 1, 2 and 3 steps ahead (losses summed) instead of 1 step. Prerequisite not yet built: a `horizon` option in `train_encoder` and multi-step pairs from the world generator.
**E11b, longer training (runs after E11a is judged).** Same objective as the baseline, 40,000 steps instead of 10,000.
**Prediction for each variant (floor-lowering; the direction is the owner's, the thresholds are Claude's and are flagged for confirmation).** Confirmed if all three hold: (i) the full-feature texture probe (the E15 measure) is at least 0.95 on every seed; (ii) the mean rung-1 angle falls from 3.78 deg to at most 2.8 deg (a 25% drop); (iii) the mean rung-2 angle of the B1 arm (which inherits the floor) falls from 10.30 deg to at most 7.7 deg. Otherwise refuted; the three numbers are reported either way, with the decomposition (inherited versus own error) per seed as informational. No tuning to fit.
**Claude's caveat, recorded now (not an amended prediction).** The stated mechanism is not obvious for the fast block. The texture block has speed 0.2: its correlation across k steps falls like 0.2^k, so predicting further ahead gives texture less to predict, and the alignment term pulls consecutive frames together, which is the pressure that squashes a fast block. I therefore think E11a may leave the texture floor unchanged or make it worse, and E11b (more steps of the same objective) is the likelier of the two to help. E11a is registered first because the owner ordered it so; its refutation would be informative either way.
**Schedule.** Needs encoder retraining per seed (E11a: three encoders, each with 3-step data; E11b: three encoders at 4x the steps, several times the earlier run time on this single CPU). Nothing has been started; both go to a new results directory (`results/stage_b2_e11a/`, `results/stage_b2_e11b/`), never overwriting.

### E11a implementation note (2026-10-14, before the E11a run; does not change the registered prediction)
The registered text says the predictor is trained to predict 1, 2 and 3 steps ahead. The objective used throughout this project is the paper's `lejepa` form (alignment plus SIGReg, no predictor), so the multi-step variant is implemented as that objective's alignment term applied at lags 1, 2 and 3 and summed, with SIGReg on every encoded point of the chain. The horizon-1 code path is unchanged and verified identical to the earlier code (same sampled pairs, same training log and weights over 200 steps). Summing three alignment terms makes the alignment pressure up to 3 times that of the baseline at the same learning rate; this follows the registered "losses summed".
