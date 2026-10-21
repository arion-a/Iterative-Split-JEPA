# Final report: the four requested checks (E21-E24) and the stale-artifact declaration

Written 2026-10-20 at the end of `docs/COMPLETION_PLAN.md`. Every number below is in the files named; predictions are in `docs/EVIDENCE.md` and were not edited (`experiments/check_results.py evidence` passes). Names follow the SplitJEPA paper's metrics: angle (subspace angle to the true block), variant R2 / invariant R2, gap ratio (λ_d/λ_{d+1}), nesting angle, leakage.

## What was asked and what came out

| Request | Item | Prediction (registered before the runs) | Result | Outcome |
|---|---|---|---|---|
| Re-run the key claims with more seeds and frozen criteria | **E21 Part A**: clean world (B1), mirror encoder, 10 fresh seeds (20-29), 3 arms | The frozen verdict rule gives PASS (or PASS with located risk); controls behave | 99 of 100 criterion-seed checks held: angles 0.98 / 1.18 deg, texture R2 0.958, identity R2 0.983, gap ratios 51.9 / 49.5, nesting 1.13 deg, off-diagonal |R2| 0.0006, D13 leakage gate met 10/10. The rank test flagged rung 2 on seed 21, and the frozen rule needs every seed, so it returns FAIL. Controls behaved (shuffled angle 78.7 deg, gap 1.01) | **Refuted as registered** (one flag) |
| same | **E21 Part B**: hierarchical world (B2), gap fix (Tier 1), sigma_cat 0.1 and 0.4, 10 seeds each | (i) sigma 0.1 recovers at least 0.60 of the gap deficit with gap above 10 in at least 90% of seeds; (ii) sigma 0.4 meets the E20 criterion in at least 90%; (iii) nesting below 5 deg in every run; (iv) no metric damaged | (i) 0.69, gap 19.3 (5.1 untreated, 25.7 clean), 10/10; (ii) 9/10; (iii) yes; (iv) yes | **Confirmed** |
| Test the probe-image explanation directly | **E22**: rung-2 angle against the identity image made orthogonal to the texture image | Orthogonalised angle at most 5 deg and at least 3 deg below the raw angle, each in at least 90% of 20 runs | 2.76 +/- 0.93 deg vs raw 10.07 +/- 1.63 deg; 20/20 and 20/20. Texture image sits 77.5 deg from identity+category images | **Confirmed** |
| Run one non-mirror encoder | **E23**: generic MLP encoder (Stage A recipe) in the B1 ladder, 5 seeds (30-34) | Every criterion except possibly texture R2 holds on at least 4 of 5 seeds | Only core invariant R2 held (5/5); 8 of 9 other criteria held on 0/5. Rung-1 gap 1.1 (rank-deficient on every seed), angles 82 / 81 deg, nesting 74 deg. The encoder itself trained normally (no collapse) and the shuffled control behaved | **Refuted as registered** |
| Use real-data-like robot data from the paper | **E24**: ManiSkill3 PickCube and PushCube, 100 groups x 8 trajectories each (simulated here), frozen ResNet-50 + small trained head, 3 split seeds per task | Viewpoint response ratio at least 3; trajectory ratio at least 1.5; controls behave; camera decodable from variant block (at least 0.9) and not from the invariant content (at most 0.65) | Viewpoint ratio 1.37 (PickCube) and 1.17 (PushCube), failing on every seed (paper: 8.4x, 14.0x); trajectory ratio 1.74 (3/3 seeds) and 1.51 (1/3); controls held; camera from invariant content 0.61 / 0.69. No clean block boundary (rung-1 gap 1.11 / 1.76, rank monitor 0/3) | **Not confirmed (both tasks)** |
| Declare the stale artifact in the log | log housekeeping | - | Done earlier (all stale fingerprints declared in the log); two more declared today (entry 296, the plan tracker). `explog.verify()` is True (419 entries) | Done |

## What this says about the central claim

- **Holds, on fresh seeds:** in the controlled worlds with the paper-style mirror encoder, the iterated split works. Both splits recover their blocks to about 1 deg, the gap ratios are about 50, nesting is about 1 deg and leakage meets the gate (E21 Part A). In the hierarchical world the gap fix works at sigma_cat 0.1 and meets its criterion at 0.4 (E21 Part B).
- **Explained:** the roughly 10 deg rung-2 angle is mostly how the identity probe image overlaps the texture image (E22), not an estimation limit.
- **Does not hold yet:** with a generic MLP encoder the first split is not recovered in the clean world (E23), and on simulated robot data with a frozen ImageNet encoder plus a small head the viewpoint change does not form a clean block (E24). So the claim is shown for an encoder built to invert the world, and not shown for learned encoders or for image data.
- **Reading for a write-up:** the result can be stated as a conditional one (the mechanism works when the encoder preserves the world's coordinates; every direct test of that holds), with E23 and E24 reported as the located limits. A claim that the ladder works with generic or image encoders would not be supported by these runs.

## Limits (as registered)

E21: clean and hierarchical worlds are our own constructions. E23: the run does not separate architecture, objective and training budget; none was varied. E24: simulated data generated here (motion-planning solutions with perturbed waypoints and speed; the paper's own trajectory generation is not stated), frozen ImageNet ResNet-50 plus a small trained head instead of the paper's fine-tuned encoder, our own trajectory-variation scheme. The paper's behaviour-cloning and closed-loop results are out of scope.

## Process notes

- Checks used: `experiments/check_results.py` (files, seeds, finite numbers, required fields, shapes, camera sanity, predictions unedited) after every step; phase gates reran all earlier checks, the log check and the 44 tests.
- One slip caught by the checks: an edit put a stray character on the registered E23 line; it was restored byte for byte and the check passes.
- The cloud container restarts whenever the session is idle and kills background jobs; Stage C needed three relaunches for that reason. Results are not affected (each run is independent and files are written complete).
- Not started, awaiting the owner: anything beyond the four requested items, including varying E23's architecture, objective or budget, and any fine-tuned-encoder version of E24.

## Where everything is

Plan and tick-off tracker `docs/COMPLETION_PLAN.md`; predictions and outcomes `docs/EVIDENCE.md`; run status `docs/STATUS.md`; hash-chained log `explog/chain.jsonl` with table view `docs/EXPERIMENT_TABLE.md`, `explog/LOG.md`, `explog/log_page.html`; reports `results/stage_b1_e21/E21_REPORT.md`, `results/stage_b2_e21/E21_E22_REPORT.md`, `results/stage_b1_e23/E23_REPORT.md`, `results/stage_c/REPORT.md`.

## Update 2026-10-21: the E23 reading above is superseded
E25 and E26 (`docs/ENCODER_GENERALITY_REPORT.md`) showed that the E23 failure came from the prediction-trained MLP discarding the fast block at speed 0.2 (texture presence about 0, 5 of 5 seeds). With equal speeds the same MLP and recipe kept every block and split both rungs on 5 of 5 seeds. So the sentence "with a generic MLP encoder the first split is not recovered" should be read as "...when the encoder has dropped the block"; it is not evidence that the splitter depends on the mirror encoder. The E23 verdict as registered (refuted) stands.
