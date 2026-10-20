# Binding decisions

Created 2026-10-13T22:35Z. Only decisions the owner has given or that were taken under `DECISION_POLICY.md` are listed. Append, never rewrite.

## D9. Nesting enforcement (owner-approved)

**Decision.** Each rung's variant block is forced to lie inside the previous rung's invariant content.
* `nesting_enforcement = hard` is the default and is on in every confirmatory run. After the spectral head estimates rung-(k+1)'s block V
  (in original feature coordinates), V is orthogonally projected onto the rung-k invariant basis and re-orthonormalized (QR).
* `soft` (eigendecompose M - lambda (I - P_k), lambda configurable) is implemented but **INACTIVE**: it must not be enabled in any confirmatory run.
  *Activation condition (supplied by the owner, 2026-10-13): deploy soft only if (a) the true target structure lies measurably OUTSIDE the estimated H_k,
  and (b) it can be reached at a lambda that keeps foreign-direction contamination out. Neither holds in any current world, so soft stays armed but off.*
* `none` is available for ablation.
* Per-rung pair budgets are configurable (the rung-1 budget is the remaining nesting-relevant knob).
* A rank-completeness monitor reports, per rung, lambda_min of the difference moment restricted to the intended variant subspace against the
  noise-floor threshold, with pass/fail per seed.

**Confirmation.** Pre-registered as E9 in `docs/EVIDENCE.md`.

**DECIDE (implementation).** The engine already eigendecomposes the difference moment inside H_k coordinates and maps back, so V lies in H_k by
construction; this is the "equivalent" form the decision allows. The explicit project-and-QR step is therefore a numerical no-op that is kept as a guard
and checked by a unit test. Alternative considered: project the top eigenvectors of the full-coordinate moment onto H_k; rejected as the primary path
because it is not equivalent (it ignores the restriction while choosing directions).


### D9 revision (2026-10-13, after the nesting-angle diagnostics; evidence in `results/diagnostics/nesting/`, summary in `docs/STATUS.md`)

**Reasoning chain (owner's analysis) and what our code showed.**
1. *Inheritance.* The nesting angle is almost all rung-1 subspace error carried forward. Ideal 3-block world: replicated (nesting 0.05-0.21 deg
   against inherited 0.07-0.28 deg; rung-2 intrinsic error ~0.4 deg or less).
2. *Budget lever.* In the ideal world the rung-1 error falls as n^-1/2 (fitted slope -0.51; 0.36 -> 0.04 deg from 5k to 320k pairs). Replicated.
   **In our trained-encoder B2 world it does not hold:** the rung-1 angle is flat at 3-4.7 deg from 7.5k to 480k pairs. That floor is encoder bias
   (the encoder is only approximately linear in the latents), not sampling noise, so more rung-1 pairs cannot lower it.
3. *Soft vs hard.* Isotropic regime: soft approaches hard as lambda grows (lambda 0.1 -> 1000: 21.7 -> 0.10 deg; hard 0.10 deg). Recall-loss regime
   (true structure outside H_k): neither works (about 90 deg). Foreign-direction regime: the owner's "hard still wins" did NOT replicate in our engine
   (hard 51 deg, soft 44-81 deg), because texture directions are resampled freely in the rung-2 pairs. In the B2 world soft with lambda >= 3 equals hard
   to within 0.1 deg; lambda 0.3 is far worse (16-28 deg); no enforcement is 78-84 deg.
4. *Truth definition.* In the B2 world the 8.6-11.6 deg nesting figure is mostly a measurement-definition gap. The two truths (span of probe images
   of blocks 2+3, as the B2 gate uses; versus the orthogonal complement of block 1's image, which is what the method targets) differ by 11.6-13.0 deg
   because the probe images of different blocks are not orthogonal. Against the orthogonal-complement truth, nesting is 2.2-3.3 deg, inherited error
   3.1-4.6 deg and clean-input rung-2 recovery error 1.4-2.1 deg.

**DECIDE.** Hard projection stays the default (it matches soft at large lambda and beats none by a wide margin). Soft stays armed and inactive.
The budget doubling in E9 is kept exactly as registered, but we expect it to do little in the B2 world (see EVIDENCE.md note). The gate keeps its frozen
(span) nesting definition; the orthogonal-complement nesting angle is added as one informational row (addition) so the two readings sit side by side.
No engine change can lower the span-definition figure, because it is a property of the truth definition and the encoder, not of the split.


## D10. Nesting gate definition (owner ruling, 2026-10-14)

**Decision.** The nesting gate is measured against the relative reference: the orthogonal complement of the first block's probe image (the quantity the spectral head can identify). The threshold is unchanged (the frozen 5 deg). The absolute nesting angle (against the span of the true identity and category probe images) is kept and reported, but is reclassified as an informational encoder-quality diagnostic, not a gate. This applies to every run from E10 onward. No earlier result is rewritten.

**Disclosure.** The owner chose this definition after the E9 data showed 2.82 deg on it (10.31 deg on the old one). It is therefore a definitional ruling, not a pre-registered pass. Runs from E10 onward are the first judged under a yardstick frozen before the run.

## D10a. Tier 1 and Tier 4 for the second split (owner instruction, 2026-10-14)

The repository does not define "Tier 1" or "Tier 4"; the owner's one-line descriptions are implemented as follows (Claude's reading, flag if wrong).
* **Tier 1, purification loop.** On the cluster-built rung-2 pairs: fit the rung-2 difference moment inside H_1; score every pair by its energy in the bottom (invariant) eigendirections of that moment; drop pairs whose score exceeds 4 x the median score; re-estimate; repeat until the kept set stops changing or 5 iterations. Constants fixed here, before the run.
* **Tier 4, within-H_1 whitening.** Whiten the content coordinates inside H_1 with the covariance of the pair endpoints' content coordinates before the eigendecomposition, then map back and re-orthonormalize inside H_1 (nesting preserved). Note: after the global ZCA, an orthonormal subspace of the population already has identity covariance, so this may change little; it is measured, not assumed.

## D11. Gap-ratio fix: what is canonical (owner ruling, 2026-10-14)
* **Tier 1 (purification, hard trim) is canonical as built** (`purify_pairs`; D10a constants: drop pairs scoring over 4 x the median, 5 iterations max). No churn.
* **Tier 4 (within-H_1 whitening) is demoted:** off by default, kept only as an option for non-whitened pipelines. Reason: after the global ZCA whitening an orthonormal subspace of the population already has identity covariance, so the extra whitening is close to a no-op; measured: gap 18.7 with it against 19.7 without (E12 run). Config key `purify.tier4` (default false); the historic E12 configs set it true so they reproduce.
* **Variants are registered probes only** (soft weights w = min(1, (c/s)^2); score normalized by the squared pair-difference norm; sample-covariance whitening over samples). They run only if the no-op control fails or the hard trim shows fragility, and each gets its own prediction before it runs. Note: the no-op control did fail (it trims 2.3-3.4% of clean pairs), so the trigger condition is met on the strict reading; nothing has been run.
* **Tier 2 (clusterer) rebuild waits** until the program turns to deployment claims. It must stay fully unsupervised: no generator labels anywhere in cluster construction. A diagnosis of the existing clustering is the only Tier 2 work now.
* **Tier 3 (background subtraction)** stays inactive.

## D12 (CANDIDATE, owner ruling 2026-10-14): the no-op control tests safety, not inaction
**Ruling.** The strict reading of the Tier 1 no-op control (nothing trimmed, results byte-identical) is refuted and replaced. Reason: it demands inaction, and a purifier that scores pairs against a median cannot be inactive on noisy clean data by construction; the question that matters is whether it is safe.
**Corrected criterion, frozen prospectively for every future no-op control.** On clean (correctly matched) pairs, Tier 1 passes if (a) it trims at most about 5% of the pairs, (b) no metric is degraded beyond seed noise, and (c) there is no systematic harm. Claude's operationalization, for the owner to confirm: (b) the mean worsening of each metric against the unpurified arm is at most 1 seed-to-seed standard deviation of the unpurified arm; (c) harm is systematic if the metric is worse on every seed AND the mean worsening exceeds 0.5 seed-std.
**Retrospective application, disclosed.** The criterion was set after the first control was seen. Applied to that control (`results/stage_b2_noop/ANALYSIS.md`): trimmed 2.3 / 2.5 / 3.4%; the largest worsening of any metric is 0.14 seed-std (five metrics are worse on all three seeds, all by 0.14 seed-std or less); rung-2 gap improves. Result: PASS.


## Stage V (video-first handshake) — added 2026-10-20

## D13. Ceiling gate is report-only (owner ruling, 2026-10-20)
**Decision.** The "ceiling gate" of LIVE_DATA_PLAN §2 (linear probe latent → tracked E, R² ≥ 0.9 before discovery proceeds, with up to two remedies) is **report-only**.
It is computed on the train releases and reported as an informational row. It never gates discovery, never triggers a remedy, and never feeds back into the framework.
**Reason.** An oracle value used for selection or stopping contradicts the governing principle (MATHEMATICAL_PLAN) and VIDEO_FIRST §5.

## D14. Naming statistic (owner ruling, 2026-10-20)
**Decision.** Naming is judged by Spearman rank correlation (or a flexible-readout R²), never Pearson. Any monotone function of a conserved quantity is equally conserved, so a rank statistic is the correct test. Thresholds stay as registered (sim 0.99, live 0.98).

## D15. Non-degeneracy statistic (owner ruling, 2026-10-20)
**Decision.** Every violation rate V is reported with a non-degeneracy statistic, because a constant map has V = 0. Operationalised (Claude, DECIDE 20261020-6/7): ICC = share of the coordinate's variance that is between releases, plus the validation-calibrated ε used in V.

## D16. Stability factor (owner ruling, 2026-10-20)
**Decision.** L is the Lipschitz constant of the latent transition F̂ (spectral norm for a linear F̂). L ≤ 1 is allowed, because a conserved mode has F̂ = identity and L = 1 exactly.
Claude's operationalisation: pass if L ≤ 1.02 (estimation tolerance, DECIDE 20261020-8). Rollout closure e(K) is reported separately.

## D17. Answers to the six smaller theory gaps (owner-directed, 2026-10-20; adopted by the instruction to implement)
1. Nuisance is split first, by same-frame different-render pairs (rung 1); the temporal split runs inside rung 1's invariant content (rung 2+), hard nesting (D9).
2. Release diversity is a data requirement (generator-side choice of initial conditions); the invariant must vary between releases (ICC); effective sample size for the invariant is the number of releases.
3. Friction: E is an approximate quotient; ε is calibrated on measured per-step drift (validation), plus tracking noise; a damped simulator arm is a unit test, not a separate experiment.
4. Augmentation pairs and temporal pairs are not pooled in one moment matrix (the pooled null space is the intersection, but the spectrum depends on an arbitrary mixing weight, and temporal pairs are only approximately matched). Pooling is a possible probe with its own prediction; none is registered.
5. Planted state counts (240→…→3) belong to the discrete mixture worlds. In continuous AR worlds only depth (number of blocks, their timescales) is planted; States-per-Rung there is measured, informational.
6. At rung k+1 of a temporal-only world the correspondence family is the pair (t, t+τ_{k+1}) on the previous rung's invariant content, with a fixed geometric lag schedule τ_k = 2^(k−1)·τ_0. Data-adaptive lags would be a registered probe.

## Candidate for owner confirmation (not binding): D18 — see docs/IMPLEMENTATION_PLAN.md §1 DECIDE lines 1–10 and §6 A1/A2.

## D18. Gap criterion for temporal worlds (owner ruling, 2026-10-20; answers A1)
**Decision.** In temporal (AR-lag) worlds the spectral-gap criterion is gamma_min = 2.0 (the 2x threshold of MATHEMATICAL_PLAN). The B1/B2 gate of 10 is unchanged and applies only to those stages.
**Note.** The line above headed "Candidate for owner confirmation: D18" referred to the list of Claude DECIDE lines (docs/IMPLEMENTATION_PLAN.md §1); that list is not a decision and keeps no D-number until confirmed. It is not rewritten (append-only).
**Disclosure.** The value was already in use for the hierarchical run (DECIDE 20261020-10); this ruling confirms it, no rerun needed.


## D19–D32. Stage V DECIDE lines 1–15, confirmed and promoted (owner instruction, 2026-10-20)
Source: `docs/IMPLEMENTATION_PLAN.md` §1 (DECIDE 20261020-1 … -15). DECIDE 10 is D18 (already a ruling). Where one choice replaced another, both are kept and the replacement is named; none is deleted.

* **D19** (was DECIDE 1). Double-pendulum integrator: RK4 with sub-steps (dt_int 1e-3), not velocity Verlet; the Hamiltonian is not separable, so Verlet is not symplectic there. A step-halving check is kept.
* **D20** (was DECIDE 2). Encoder trained by multi-horizon prediction + regulariser only, no alignment loss. **Superseded by D31.**
* **D21** (was DECIDE 3). Encoder recipe = the repo's validated hinge + covariance regulariser (var 1e-2, cov 0.04), prediction heads at horizons {1, 8, 32}.
* **D22** (was DECIDE 4). Block size per rung = largest gap ratio, ratio >= gamma_min = 2.0. **Amended by D30** (which eigenvalues count as candidates).
* **D23** (was DECIDE 5). S1 read as "no eigenvalue above c(n)". **Replaced by D28.**
* **D24** (was DECIDE 6). The coordinate psi = the maximum-ICC direction in the invariant core (generalised eigenproblem, release groups; physics-free).
* **D25** (was DECIDE 7). Violation rate V: delta = 0.1 std, eps = delta + 2 x q95 validation drift (triangle rule), 200 cross-release matched pairs.
* **D26** (was DECIDE 8). L tolerance 1.02 for estimation error; rollout horizon K = 8 frames.
* **D27** (was DECIDE 9). Real data = public Morpheus double-pendulum clips (MIT), informational only, no gates.
* **D28** (was DECIDE 11). S1 amended: fires when lambda_max of a family's difference moment is <= 5% of an unmatched pair's energy (2 per whitened dimension). Replaces D23.
* **D29** (was DECIDE 12). B^2 in c(n) = the 99th percentile of squared pair differences, not the maximum; c(n) is reported per rung.
* **D30** (was DECIDE 13). Block-size candidates must have top eigenvalue above the S1 level (5% of chance), not c(n); c(n) exceeds every eigenvalue for whitened d >= 32. Amends D22.
* **D31** (was DECIDE 14). Encoder objective adds a consistency term between two renderings of a frame (aug_weight 0.2) and uses a 64-d latent (LIVE_DATA_PLAN §2); chosen on dev seed 100 by a physics-free diagnostic only. Supersedes D20.
* **D32** (was DECIDE 15). Nuisance = additive 4-coefficient illumination pattern (amplitude 0.4), not gain/offset/shift (untested, a stated limitation); S1 on a family skips that family, and the ladder ends by S1 only when the last family is exhausted.

**Not settled by this confirmation:** which way the five-bit "triggers" pattern runs in the DECISION_POLICY log format (the plan used 1 = fired). It stays flagged.


## D33. Trigger-pattern convention in DECIDE log lines (owner instruction, 2026-10-20)
**Decision.** In `triggers-clear: <T1..T5>` a 1 means the trigger is CLEAR (did not fire), a 0 means it fired. A DECIDE-D line (no trigger fired) therefore reads `11111`.
**Correction.** The stage-V plan first used the inverse (1 = fired). The 15 DECIDE lines in `docs/IMPLEMENTATION_PLAN.md` §1 were flipped (`00000` -> `11111`, and the one-trigger-fired lines `10000` -> `01111`: T1 fired for DECIDE 10-15 where a gate or criterion was added or changed). Earlier chain entries are not rewritten; no chain entry carried the pattern.
