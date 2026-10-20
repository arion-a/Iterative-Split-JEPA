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


## Stage V registrations (2026-10-20, written before any stage-V run; criteria frozen in `configs/handshake.yaml`, sha256 in `configs/handshake.criteria.sha256`)

Numbering follows MATHEMATICAL_PLAN §6 (authoritative per that document). Source predictions are the owner's; amendments are D13–D16.

**E31c′ (certificate, physics-free).** Run: handshake, 3 seeds, held-out test releases. Prediction: the discovered coordinate psi has V ≤ 0.05 (δ = 0.1 std, ε = δ + 2·q95 validation drift, K = 8 frames, 200 cross-release pairs),
ICC ≥ 0.9, L ≤ 1.02, rollout RMSE/std ≤ 0.35 at K = 8. Decision rule: confirmed only if all four hold on every seed. Claude's expectation, recorded now: hard to meet; the encoder has to make a conserved quantity linearly accessible (the 0.35 ceiling seen in the synthetic attempt).
**E31d (naming).** Prediction: Spearman(psi, E) ≥ 0.99 on held-out test frames, every seed (D14). Claude's expectation: likely refuted, because Spearman across frames is limited by within-release noise of psi (ICC 0.9 alone caps it near 0.95).
**E31e (termination and reach).** Prediction: the ladder stops by S1 at rung 3 (lag 32) and the variant (fast) block's faithful horizon is shorter than psi's: NMSE of the variant block at horizon 32 ≥ 0.5 while psi's is ≤ 0.1225 (= 0.35², the rollout bound).
**P-stab (pilot).** Prediction: minimum pairwise |Spearman| between seeds' psi on test frames ≥ 0.9. **P-ctrl.** Prediction: the flat baseline and the shuffled-pair arm both have |Spearman(psi, E)| < 0.9 on every seed (evaluator side only).
**E31f:** not run (no frozen statistic). **E44 (ceiling):** report-only (D13), no prediction.
**E35 (hierarchical, minimal; MATHEMATICAL_PLAN §2.4 verbatim).** "Measured RUNGS equals the number of levels above the 2× threshold (4 by construction)." Run: AR world a = (0.2, 0.5, 0.75, 0.9, 0.95), lags 1, 2, 4, 8, 3 seeds. Controls: shuffled pairs give RUNGS = 0.
Claude's expectation, recorded now and not replacing the registered text: fewer than 4. The cut gap across level k/k+1 is (1−a_k^τ)/(1−a_{k+1}^τ), never above the adjacent timescale ratio (2.31, 2.40, 2.73, 2.05) and 1.60, 2.00, 2.50, 2.00 at lag 1, so only one cut clears 2× with margin.
E36, E37, E38: not run (need a constructed bridge-failure world; the plain AR world is stable by design). E43: not run. E44–E47 on the owner's own capture: blocked on capture.

**Amendment before any stage-V run (2026-10-20):** the operational rule for S1 in E31e is replaced (DECIDE 20261020-11): S1 fires when the rung's difference moment has lambda_max ≤ 5% of an unmatched pair's energy (2 per whitened dimension). Reason: the source reading (variation above c(n)) never terminates because white measurement noise exceeds the statistical floor in any invariant core; found by the planted-ladder unit test. Config re-frozen (criteria sha256 f27cbe99… → 27c53661…); no run had used the old hash.

**Second amendment before any stage-V registered run (2026-10-20):** recipe changes found on dev seed 100 (physics-free diagnostics only), none touching a criterion: block-size floor (DECIDE 13), encoder consistency term and 64-d latent (DECIDE 14), additive illumination nuisance and skip-on-S1 (DECIDE 15). Consequence for E31e: "S1 fires at rung 3" is evaluated as "the lag-32 family (third family) exposes no variation and ends the ladder by S1"; the rendering-pair family is expected to end in S1 too (absorbed by the encoder), so the ladder splits once (lag 8). Datasets rebuilt with the new renderer; the first three datasets (gain/offset/shift renderer, digests in chain entry CP1) were never used by a run.

**P4 frozen criteria (2026-10-20, before the hierarchical run; `configs/hier.yaml`, sha256 in `configs/hier.criteria.sha256`).** Beyond E35 (RUNGS = 4; shuffled-pair control RUNGS = 0): every found rung must have variant R² and invariant R² ≥ 0.9 on held-out trajectories, (D) residual and (C) 8-step rollout error within 1.25× of the oracle-block predictor, L ≤ 1.02 (D16). Arms: ladder (lags 1, 2, 4, 8) and shuffled control, 3 seeds, mirror encoder (D4). Prediction text for E35 above stands.

### Outcomes (2026-10-20), stage V handshake, `results/handshake/REPORT.md` (3 seeds, run as registered after the two amendments above)
* **E31c′: CONFIRMED** on every seed: V 0.003 ± 0.005 (≤ 0.05), ICC 0.973 ± 0.003 (≥ 0.9), L 0.993 ± 0.001 (≤ 1.02), 8-step rollout 0.232 ± 0.008 (≤ 0.35). The evaluator-side q_energy reference passes (V 0, ICC 1); q_angle fails ICC (0.37); q_const has V = 0 and ICC = 0, i.e. the non-degeneracy statistic does its job. Claude's expectation (hard to meet) was wrong for the certificate.
* **E31d: REFUTED.** |Spearman(ψ, E)| = 0.786 ± 0.074 (needs 0.99), as expected. The ceiling probe (report-only, D13) reads R² 0.93 / 0.91 / 0.79 on test, so E is mostly but not fully linearly present.
* **E31e: S1 at lag 32 REFUTED as worded** (seeds 0, 1 end by S1 at lag 32 on a 1-d core; seed 2 splits a 4-d core into 3 + 1, lambda_max/chance 0.153 > 0.05). **Reach part confirmed:** NMSE at horizon 32 is 0.666 for the variant block and 0.057 for ψ.
* **P-stab: REFUTED:** 0.766 ± 0.058 (needs 0.9). **P-ctrl: met:** flat 0.257, shuffled 0.790 (< 0.9), shuffled ladder S2 on all seeds.
* **Finding, not predicted:** the shuffled arm's ψ is as good as the main arm's (ICC 0.974 vs 0.973, naming 0.790 vs 0.786). The shuffled ladder stops at S2 and keeps the full content, and the max-ICC selector over release groups then finds the same coordinate. So release grouping is itself the correspondence that identifies the invariant here; the temporal rung's contribution is not shown by this run.

### Outcome (2026-10-20), stage V hierarchical (P4), `results/hier/REPORT.md`
* **E35: REFUTED as worded.** RUNGS = 1 on all 3 seeds (registered 4). One cut is taken, blocks {1,2,3} | {4,5} (gap ratio 2.23–2.31 against the oracle arithmetic 2.5); the lag-2 family on blocks 4–5 gives 1.75–1.81 (< 2) so the ladder ends by S2. This is the outcome recorded as Claude's expectation before the run. **Control met:** shuffled pairs give RUNGS 0 on every seed.
* **Per-rung gates met** for the one found rung: variant R² 0.959 ± 0.011, invariant R² 0.989 ± 0.003, (D) 1.074 ± 0.017 and (C) 1.005 ± 0.001 times the oracle, L 0.949 ± 0.002.
* Measured eigenvalues of the lag-1 moment follow the arithmetic 2(1−a) (1.6, 1.0, 0.5, 0.2, 0.1). Escalation A1 (gap criterion for temporal worlds) stands.

### Outcome (2026-10-20), stage V real video (P5), `results/real/REPORT.md` — informational, no registered prediction
10 public real double-pendulum clips, held out in time. Certificate passes (V 0, ICC 0.989, L 0.989) but psi correlates weakly with the tracker proxies (|Spearman| 0.11 with speed², 0.31 with height) and the report-only ceiling probe is poor (R² −0.49 / 0.07). With 10 clips the max-ICC direction most likely encodes per-clip appearance. No energy naming is claimed. `psi_icc_fit` 1.088 in the JSON is a ddof artefact (direction unaffected; code corrected after the run).

## F1 (registered 2026-10-20, before the F1 run; follow-up chosen by the owner)
**Question.** In the handshake the shuffled-pair arm named as well as the main arm (|Spearman| 0.790 vs 0.786). Is the discovery carried by the release-grouped ICC selector rather than the temporal split?
**Run.** Same three datasets, encoders retrained with the same seeds and recipe (`configs/handshake.yaml`). Two arms on each seed: **main** (ladder + max-ICC selector, as before) and **temporal-only** (no release information: psi = the lowest-eigenvalue direction of the lag-8 difference moment over the whole whitened latent, i.e. linear slow-feature analysis). `configs/followup.yaml`, criteria hash in `configs/followup.criteria.sha256`.
**Prediction (written first, Claude's).** Release grouping carries it: |Spearman(psi, E)| of main exceeds temporal-only by at least 0.1 on every seed. **Decision rule:** confirmed if the gap is ≥ 0.1 on all three seeds; refuted otherwise (then the temporal split alone finds a coordinate about as good, and the shuffled-arm equality has another explanation). Reproduction check, informational: main's |Spearman| should be within 0.05 of the handshake values (0.786 mean; per seed in results/handshake/main/*.json). No tuning after the result.
