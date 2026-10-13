# Binding decisions

Created 2026-10-13T22:35Z. Only decisions the owner has given or that were taken under `DECISION_POLICY.md` are listed. Append, never rewrite.

## D9. Nesting enforcement (owner-approved)

**Decision.** Each rung's variant block is forced to lie inside the previous rung's invariant content.
* `nesting_enforcement = hard` is the default and is on in every confirmatory run. After the spectral head estimates rung-(k+1)'s block V
  (in original feature coordinates), V is orthogonally projected onto the rung-k invariant basis and re-orthonormalized (QR).
* `soft` (eigendecompose M - lambda (I - P_k), lambda configurable) is implemented but **INACTIVE**: it must not be enabled in any confirmatory run.
  *Activation condition: stated in the owner's original D9 text, which was not supplied to this repository. Until it is supplied, soft stays off.*
* `none` is available for ablation.
* Per-rung pair budgets are configurable (the rung-1 budget is the remaining nesting-relevant knob).
* A rank-completeness monitor reports, per rung, lambda_min of the difference moment restricted to the intended variant subspace against the
  noise-floor threshold, with pass/fail per seed.

**Confirmation.** Pre-registered as P9 in `docs/EVIDENCE.md`.

**DECIDE (implementation).** The engine already eigendecomposes the difference moment inside H_k coordinates and maps back, so V lies in H_k by
construction; this is the "equivalent" form the decision allows. The explicit project-and-QR step is therefore a numerical no-op that is kept as a guard
and checked by a unit test. Alternative considered: project the top eigenvectors of the full-coordinate moment onto H_k; rejected as the primary path
because it is not equivalent (it ignores the restriction while choosing directions).
