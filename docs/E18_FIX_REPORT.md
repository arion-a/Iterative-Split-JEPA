# Report: the E18 refutation (spectral cluster count), its cause and its fix

Written 2026-10-21 at the end of Phase G4-K of `docs/PLAN_CLOSE_GAPS.md` (Gap 1 of `docs/PLAN_GAPS_ONE_BY_ONE.md`). Predictions: `docs/EVIDENCE.md` (E18, E31, E32; never edited), criteria `configs/slowk.criteria.yaml` (frozen by hash before any run), numbers `results/stage_b2_slowk/SLOWK_REPORT.md`, 60 runs on fresh seeds 60-69.

## Was the E18 issue fixed? Short answer
The cause is found and removed, and the fix works where the category structure is resolvable (sigma_cat up to 0.4: K = 6 in 10 of 10 and 9 of 10 runs). At 0.6 it is 6 of 10 (registered target of 9 of 10 missed), and the count slides to 5 as the categories overlap further. The goal the count serves, valid pairs for rung 2, is met at sigma_cat 0.1, 0.4 and 0.6.

## The problem and its cause
E18 chose the cluster count by the eigengap of a graph Laplacian on the rung-1 invariant output and found K = 6 in 1 of 18 runs. The cause: in the B2 world each of the 6 categories has its own 20 identity centres, so the 8-dimensional invariant output holds 6 x 20 = 120 blobs; the count read there is a count of identity-and-category blobs. An exploratory check on the true latents (not registered) showed the same selector, same constants, gives K = 6 in 9 of 9 configurations in the category block alone or in the 4 slowest directions of adjacent-frame change (found without labels), and 0 of 9 in the full invariant space. So the space was wrong, not the selector.

## The fix
`slow_subspace_k` (`src/isj/cluster.py`), option `cluster.slow_k` in the B2 pipeline (off by default; every other arm identical with it on or off, checked): (1) estimate the second moment of the adjacent-frame change inside the rung-1 invariant output; (2) take its slowest directions, their number from the largest eigenvalue ratio (abstain below 2.0, the one new constant, registered beforehand); (3) run the E18 selector, unchanged, in that subspace; (4) k-means at that K there; then pairs within clusters and Tier 1 as before. Theory fit: Remark 5.4 (terminate when the correspondence structure is not there: the selector abstains), nothing added to the encoder, no labels.

## Results (E31: 40 runs, E32: 20 runs; K = 6 is the planted count)
| sigma_cat | K = 6, slow subspace | K = 6, E18 (full space) | K = 6, silhouette | Mean purity (slow) | Rung-2 pair-quality criterion met after Tier 1: slow / silhouette / E18 |
|---|---|---|---|---|---|
| 0.1 | 10 / 10 | 1 / 10 | 3 / 10 | 1.000 | 10/10 / 10/10 / 9/10 |
| 0.4 | 9 / 10 | 2 / 10 | 2 / 10 | 0.974 | 10/10 / 10/10 / 3/10 |
| 0.6 | 6 / 10 | 0 / 10 | 2 / 10 | 0.901 | 9/9 / 7/9 / 1/9 |
| 0.8 | 3 / 10 | not run | not run | 0.803 | not scored |
| 1.0 | 0 / 10 | not run | not run | 0.702 | not scored |
Controls (registered with E31): with the time order destroyed the selector gave K = 6 in 0 of 10 runs at every level (it abstained); in a world with equal speeds it abstained in 10 of 10. Verdicts as registered: **E31 refuted** (part (a) at sigma_cat 0.6: 6 of 10, needed 9; parts (b), (c), (d) held); **E32 refuted** (K = 6 in 3 of 10 at 0.8 and 0 of 10 at 1.0; the purity-ceiling part held). **Located boundary: sigma_cat 0.4.**

## Why it stops at the boundary
Every miss is K = 5 (two categories merged), never a larger count; at sigma_cat 1.0 it is K = 5 in all 10 runs. The block size (4 slow directions, eigenvalue ratio 4.5-5.2) is right wherever checked; the angle between the slow subspace and the true category image (about 11-19 deg with the trained encoder, 2.5 deg with true latents) is the same in hits and misses. Four of the five misses at sigma_cat 0.4 and 0.6 come from worlds whose two closest category centres are close, but that is not a clean threshold. The reading is a resolution limit between neighbouring categories as the within-category spread grows, consistent with the purity ceiling (0.87 / 0.77 at 0.8 / 1.0); it is not a defect of the subspace or block-size step.

## Limits
- Needs adjacent-frame order and a speed difference between the category block and the identity block (without them it abstains, tested). The alternation fallback for data without time order (plan step G4K.4) was conditional on that case and was not built.
- Evaluated in one synthetic world (B2) with the mirror encoder; with a generic encoder, presence of the blocks (D15a) is a precondition.
- The subspace error with a trained encoder is 11-19 deg; the count is right in spite of it, but it is not the 2.5 deg of the idealised check.
- My level guesses for sigma_cat 0.8 and 1.0 were too optimistic; they were not tuned afterwards.

## What was not done (outside this fix)
Soft pairs and a BIC count were dropped from the plan as outside the theory and the experimental plan; pair-building for rung 3 and deeper from data is noted, not started.
