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

**Confirmation.** Pre-registered as P9 in `docs/EVIDENCE.md`.

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
The budget doubling in P9 is kept exactly as registered, but we expect it to do little in the B2 world (see EVIDENCE.md note). The gate keeps its frozen
(span) nesting definition; the orthogonal-complement nesting angle is added as one informational row (addition) so the two readings sit side by side.
No engine change can lower the span-definition figure, because it is a property of the truth definition and the encoder, not of the split.
