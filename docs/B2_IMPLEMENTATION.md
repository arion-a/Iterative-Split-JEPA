# B2 spec (docs/B2.md): what exists, what differs, and how it is being incorporated

`docs/B2.md` is kept as written. This file records how the code follows it. Status: **done** / **partly** / **not yet**.

## 1. Spec against what I had built (runs r1 and r2)

| Spec item | Status | What I had |
| --- | --- | --- |
| World: 6 categories, each a tight Gaussian cluster; 20 identities per category; 2 textures per identity; sigma_cat sweepable | **differs** | Number of categories was swept (3/6/12, then 6/12/24). Identity and texture were continuous Gaussian blocks, not 20 and 2 discrete values. Within-category spread was fixed. |
| Construction metrics: purity, pair validity, cluster count vs true, misgroup rate | partly | Purity and pair validity (stored as the misgrouped-pair fraction) were recorded. The cluster count was given to k-means, not discovered. |
| Gates identical to B1 (5 deg, R2 above 0.9, gap above 10, nesting 5 deg, rank check, 3 seeds) | not yet | B2 numbers were reported but not judged against the B1 gates. |
| T1 construction cost: B2 within 2x of B1 per seed, delta per metric | partly | The generator-twin arm is B1 on the same encoder, world and seed. No delta table. |
| T2 purity 0.9 and pair validity 0.95 imply all gates pass | not yet | |
| T3 graceful degradation as sigma_cat varies, against the contamination bound | not yet | |
| T4 controls C1 (cross-cluster pairs), C2 (clusters from the variant block), C3 (singleton clusters), C4 (shuffled membership) | partly | A random-pairs arm only. |
| Report sections A-D, figures P2', P7, P8, P5, verdict line | not yet | |

## 2. How I am reading the parts the spec leaves open (all changeable)

1. **"20 identities, 2 textures each"** is read as a hierarchical Gaussian mixture, every level Gaussian inside itself: 6 category centres; within
   each category 20 identity centres; within each identity 2 texture centres. A sample picks a category, an identity and a texture and adds Gaussian
   jitter at each level. Blocks stay 4 numbers each (12 hidden numbers), the paper's coupling map, the mirror encoder and the paper's objective.
2. **sigma_cat** is the within-category jitter, measured against a unit between-category spread. Smaller means cleaner clusters. The sweep is chosen
   so purity runs from near 1.0 down to about 0.7.
3. **Discovering the cluster count.** The count is chosen from the data (silhouette score on a subsample, 2 to 12), so construction uses no ground truth.
   The planted count of 6 is used only to report "discovered vs true". An oracle-count variant is kept as an informational arm.
4. **B1 on the same world** is the generator-twin arm on the same trained encoder and seed, so the headline table compares like with like.
5. **Contamination bound** (monograph section 10): leakage at the next rung is at most the previous rung's leakage times (1 + 2 x misgroup rate). The monograph
   states it for R2 leakage. For the norm ||A21|| I draw it two ways (bound on the norm, and the square root of the bound) because the conversion is not stated.
6. **Gates** use the B1 criteria exactly, including B1's amended leakage floor (decided after seeing B1 data; flagged in the report).
7. **Controls.** C1: pairs drawn from different discovered clusters. C2: clusters built from the rung-1 variant (texture) output. C3: every sample its own
   cluster, so no valid pair exists. C4: cluster membership shuffled among samples, then paired within clusters (recorded, no required outcome).

## 3. The earlier runs

r1 (3/6/12 categories) and r2 (6/12/24 categories, fixed world) stay on record as an exploration of how the number of categories matters. The formal B2
run follows this spec and writes to `results/B2/` in the layout `docs/REPORTING.md` asks for.


## D9 nesting enforcement: implementation notes (2026-10-13)

* `src/isj/engine.py`: `fit_rung(..., nesting_enforcement="hard"|"soft"|"none", soft_lambda)`. Hard = restricted eigendecomposition inside H_k, then explicit
  project-and-QR guard. Soft = top-d_k eigenvectors of `M - lambda (I - P_k)`. None = unrestricted. `fit_ladder(..., pair_budgets=[n1, n2])` passes a
  per-rung pair count to the pair generator. `RungFit` records `max_sq_diff` and the enforcement mode.
* `src/isj/audits.py`: `rank_monitor(fit, delta)` returns lambda_min of the restricted moment, the noise-floor threshold
  `max||Delta h||^2 * sqrt(2 log(1/delta)/n)`, pass/fail, and n_pairs.
* Defaults for old runs are unchanged in effect: the old path was already restricted (= hard), so existing results are reproduced.
* `experiments/diagnose_nesting.py` is the diagnostic; output in `results/diagnostics/nesting/`. Finding: no engine setting lowers the B2 span-definition
  nesting figure; the repair the owner listed (rung-1 budget, rank completeness, gap) is applied in the E9 run and its effect is measured there.
