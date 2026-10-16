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

## D13. Leakage gate re-referenced to the paper's dimension scaling (owner instruction, 2026-10-14)
**Decision.** The old leakage gate (largest off-diagonal |R2| below 0.01) was set after seeing B1 data and is a d = 8 style number applied to a d = 12 world. It is retired as post-hoc. From the next run on the leakage gate is ||A21||_F / sqrt(d_V) below 0.0209 at both rungs (E17: paper's 0.0053@d4 -> 0.0325@d64, power-law interpolation to d = 12 gives 0.0109, plus 0.01).
**DECIDE.** (1) The gate quantity is the paper's metric (normalized ||A21||_F), not max |R2|, because the paper's scaling law is for that quantity; a threshold in R2 units cannot be derived from it. Alternative considered: keep max |R2| and scale it; rejected, no paper number exists in those units. (2) Interpolation is a power law in d; alternatives (linear 0.0189, log-linear 0.0261) are listed in E17 and the existing data sit inside that band. (3) d = 12 for both rungs as instructed; rung 2 works inside an 8-dimensional content (power-law d = 8 would give 0.0183). All three are flagged for the owner.

## D14 (CANDIDATE, owner recommended action, 2026-10-16): the gap reference for cluster-built pairs is the perfect-cluster gap
**Ruling.** The frozen gate "rung-2 gap ratio above 10" was calibrated on the B1 twins, which share their category jitter exactly. Cluster-built pairs share only the label, so even perfect clusters have a lower achievable gap (measured on the perfect-cluster arm: 19.5, 5.3, 3.2, 2.3, 1.8, 1.3 at sigma_cat 0.1 to 1.5). For cluster-built arms the gap is therefore also judged against the achievable gap on the same encoder: **cluster-built gap >= 0.6 x the perfect-cluster gap**, applied only where the achievable gap is at least 3 (below that there is no usable cliff and the criterion is moot). The absolute gate (above 10) stays for the B1 twin arm and is reported for every arm.
**DECIDE.** (1) Reference = the measured gap of the perfect-cluster (label_pairs) arm on the same encoder and seed, not a fitted model: no extra parameters. Alternative considered: the analytic floor lambda_5(twins) + 2 sigma_cat^2; rejected because it overstates above sigma_cat 0.4 (see the erratum in EVIDENCE.md). (2) The 0.6 fraction is the E12 precedent (60% of the achievable). (3) The minimum achievable gap of 3 is Claude's constant, flagged. (4) The labels in the perfect-cluster arm are used for evaluation only, never in construction.
**Disclosure.** Set after the E13 sweep numbers were seen; applied to that data it is retrospective. A blind check on fresh seeds is registered as E20.
