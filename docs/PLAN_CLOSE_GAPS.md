# Plan: closing the gaps between "works on a representation that contains the structure" and "works in practice", especially for deeper ladders

Written 2026-10-21 at the owner's request. **Planning document only: nothing here has been registered or run.** Each phase registers its predictions in `docs/EVIDENCE.md` (additions only) and freezes its criteria by hash BEFORE its runs, as before; the numbers below marked "draft" are proposals, fixed only at registration. Same rules as the earlier plans: no tuning to fit, refuted results are results, a check after every step and a gate after every phase, a supervisor during runs, anything outside the plan goes to "Noted, not started".

## 0. What can honestly be aimed at
"Works in all cases" cannot be established by any finite set of tests. What can be established is: (1) the ladder works whenever stated preconditions hold (the encoder kept the content; correspondences are right; the blocks are separable), at the depths tested; and (2) when a precondition fails, the pipeline detects it and says so, instead of silently removing directions and damaging later rungs. Phases G1-G6 aim at those two things, with limits located where they exist.

## 1. The gaps: where they are, what in the process causes them, what could fix them

| # | Gap | Exact location in the process | Cause (evidence) | Proposed solution | Evidence status of the cause |
|---|---|---|---|---|---|
| G-a | **Deeper ladder never measured** (objective O3) | Evaluation code and verdict function, not the engine: `src/isj/stage_b1.py` lines 114-121 (`block_slice(3)`, `image[2]`, `image[3]`, `rungs[1]`) and `seed_checks` (`r1, r2 = r["rungs"]`) assume exactly 3 blocks and 2 splits. The engine (`fit_ladder`, `BlockWorld.correspondence_pairs`) already loops over any number of blocks | Read from the code; no run has used more than 3 blocks (`docs/TARGETS.md`: depth has no paper target; Stage C "not started") | Generalise the evaluator and verdicts to K blocks, then measure depth 3 to 6 and the scaling of angle error with pair budget; report the first violated gate | Established (code reading) |
| G-b | **A failed rung damages the next ones** | `fit_ladder`/`fit_rung` with fixed block sizes (`d_ks`): when a rung has no gap it still removes `d_k` directions, and the hard nesting projection (D9) makes the next rung work inside what is left | E30: after a failed rung 1 (texture absent), rung 2 at presence 0.99 split on only 3 of 10 seeds, angles continuous from 2.5 to 78 deg; earlier diagnostics: nesting error is mostly inherited from rung 1 | Gap-gated rungs with abstention: choose `d_k` by the gap rule (`select_block_count`, absolute gap as in Stage A) and, when no gap clears the threshold, remove nothing and report "no further block at this rung" | The failure is measured; the removal-of-arbitrary-directions explanation is a **hypothesis, untested** |
| G-c | **The encoder may not keep the content** | Representation learning, before the engine: the objective and its regulariser | E25: prediction-trained MLP dropped the fast block (presence about 0); E27: MLP + paper objective collapsed at weight 1e-6; E28/E29: with weight 0.01 it kept all blocks on only 6 of 15 seeds | (i) An unsupervised presence check usable without true latents (decoder reconstruction of the observation from the embedding); (ii) choose the encoder's regulariser weight / budget with that check, not with true latents; (iii) if the check fails, do not split and say why | Established that presence varies with objective and speeds; the proxy is a **hypothesis** |
| G-d | **Pairs built from data break when categories overlap** | Correspondence-family builder `src/isj/cluster.py` (hard K-means pairs; `spectral_k`) feeding rung 2 | Cluster purity ceiling 0.994 / 0.953 / 0.870 / 0.773 / 0.582 at sigma_cat 0.4 / 0.6 / 0.8 / 1.0 / 1.5 even for the best assignment; K selection by silhouette and by spectral eigengap both unreliable (E18: K=6 in 1/18); E20: criterion met at 0.4, 1 of 3 at 0.6; pairs for rung 3 and deeper do not exist | Soft (posterior-weighted) pairs and mixture-model K selection (BIC) in place of hard assignments; state the overlap beyond which the invariant is ill defined; extend pair-building to nested levels only after G-a and G-b work | Established for the limits; the soft-pair remedy is a **hypothesis** |
| G-e | **Real-image features do not concentrate the factor** | Encoder + block-size rule: frozen ImageNet features plus a small head | E24: camera readable from the variant block (0.93-1.00) and partly from the rest (0.61-0.69), gap ratio 1.1-1.8, rank monitor 0/3: the viewpoint change is spread over many directions, so a gap-based linear block does not exist | (i) Choose the block size by cumulative pair-difference energy where the factor is high-rank, evaluated on the existing E24 features; (ii) a learned encoder trained on images (the paper fine-tunes a ResNet-50; that needs a GPU the sandbox cannot reach; a small CNN on downsampled images is feasible on CPU) | The spread is observed; that it is the cause of the failed P1 is an **inference** |
| G-f | **No payoff test** (objective O4) | Nothing downstream is defined | Stage D "not started" | Two cheap tests in the ideal world: hierarchy is real (ladder vs a single-shot K-way split on the same pairs) and it pays (a readout of the slowest block under a shift of the nuisance distribution: after rung 1 vs after rung 2) | Design only |

## 2. Phases and steps (order: instruments first, then the cheapest decisive tests)

### Phase G0: instruments (no experiment; code and tests)
- [ ] G0.1 Generalise the B1 evaluator to K blocks: per-rung angle, variant R2, gap, rank test, leakage; nesting against the span of the slower blocks' images; core R2 on the last block; presence per block (already per block). **Done when:** a 3-block run reproduces a stored E21 run file's numbers exactly (regression test) and a 5-block smoke run writes all fields.
- [ ] G0.2 Generalise `seed_checks` and the layered classifier (`analyse_layered.py` style) to a rung list. **Done when:** unit tests on stored 3-block files give the same verdicts as today.
- [ ] G0.3 Config and world builders for K blocks (block_dims, rhos, d_ks). **Done when:** configs for K = 3, 4, 5, 6 smoke-run.
- Gate: the existing 45 tests pass; `explog.verify()`; no result file changed.

### Phase G1: how deep does the ladder go? (objective O3; ideal encoder, ground-truth pairs)
- [ ] G1.1 Register (draft): mirror encoder + paper objective, equal speeds, K = 3, 4, 5, 6 blocks of 4 latents, 5 seeds each; every per-rung criterion (angle below 5 deg, variant R2 at least 0.9, gap above 10, rank test) holds at every rung up to depth 5 on at least 4 of 5 seeds; the rung-k angle and the nesting angle as functions of k are reported; the first violated gate (if any) is located. Criteria hash-frozen.
- [ ] G1.2 Scaling: depth 5, pair budgets {7.5k, 15k, 30k, 60k} per rung, 5 seeds: registered prediction that the angle falls roughly as n^-1/2 (log-log slope between -0.7 and -0.3) at every rung, as seen in the ideal 3-block world.
- [ ] G1.3 Run (about 40 runs), score, record. **Done when:** a table of per-rung criteria vs depth and the located limit (or its absence up to depth 6) is in EVIDENCE and the report.

### Phase G2: fix the carry-over (G-b)
- [ ] G2.1 Implement gap-gated rungs with abstention as an option of `fit_rung`/`fit_ladder` (frozen rule: block size by the absolute-gap rule; abstain when the largest gap ratio is below a fixed value, draft 3); default behaviour unchanged. Unit tests: abstention removes nothing; clean data gives the same blocks as the fixed-size path.
- [ ] G2.2 Register (draft): on the E30 cell B setup (texture absent), rung 1 abstains on at least 8 of 10 fresh seeds and rung 2 is SPLIT on at least 8 of 10 (against 3 of 10 before); on clean worlds (the E21 Part A setup, 10 fresh seeds) the gated and fixed-size ladders agree within seed noise (no-regression control); sensitivity of the abstention level to be reported, not tuned.
- [ ] G2.3 Run (about 30 runs), score, record. **If refuted:** the cause of the carry-over is not the removed directions, and the plan reopens G-b with the diagnostics (which subspace rung 1 removed vs the identity image).

### Phase G3: encoders that keep the content (G-c)
- [ ] G3.1 Unsupervised presence proxy: held-out R2 of reconstructing the observation from the embedding with a small decoder (diagnostic only; training stays reconstruction-free). Register (draft): across E25/E26/E28-type runs (3 cells x 5 seeds, encoders kept this time) the proxy at or above a frozen level agrees with true minimum-block presence at or above 0.95 on at least 90% of runs.
- [ ] G3.2 Gate in the pipeline: if the proxy fails, report "encoder dropped content" and do not split.
- [ ] G3.3 Repair the MLP + paper-objective cell by choosing weight and budget with the proxy only (grid draft: weights {0.01, 0.1, 1.0} x steps {10k, 30k}, selection rule fixed first, spare seed), then confirm on 10 fresh seeds: true presence at least 0.95 and both rungs SPLIT on at least 8 of 10.
- [ ] G3.4 Record, including where the proxy and the true presence disagree.

### Phase G4: pairs built from data (G-d)
- [ ] G4.1 Soft (posterior-weighted) pair construction and mixture-model K selection (BIC) behind the existing cluster interface; unit tests.
- [ ] G4.2 Register (draft): at sigma_cat 0.6 and 0.8, 10 fresh seeds each, the D14 criterion (cluster-built gap at least 0.6 x the perfect-cluster gap) is met in at least 90% of seeds at 0.6 (E20: 1 of 3) and the BIC choice finds K = 6 in at least 90% of seeds at 0.4 and 0.6; the sigma at which it stops working is reported as the boundary of the claim.
- [ ] G4.3 Run, score, record. **Then**, only if G1 and G2 pass: nested pair-building for a 4-level mixture world (a world extension, registered separately) to test deep ladders from data.

### Phase G5: image data (G-e)
- [ ] G5.1 Re-analyse the existing E24 features (no new data): block size by cumulative energy instead of gap; register (draft) before looking: viewpoint response ratio V1/Q1 at least 3 and camera decoding at most 0.65 from the invariant content on at least 2 of 3 split seeds in both tasks.
- [ ] G5.2 A small CNN trained from scratch on downsampled images (CPU feasible), ladder on its output, presence check from G3; registered separately.
- [ ] G5.3 The paper's fine-tuned ResNet-50 needs a GPU outside this sandbox: prepare the handoff (`docs/HANDOFF_E24_GPU.md` pattern); not runnable here.

### Phase G6: does it pay? (G-f, objective O4; ideal world)
- [ ] G6.1 Hierarchy is real: on the same pairs, a single-shot K-way split (one eigendecomposition of the pooled pair-difference moment) vs the ladder; register (draft): the ladder's per-block angle is below 5 deg on at least 4 of 5 seeds, the single-shot split's is not.
- [ ] G6.2 It pays: train a linear readout of the slowest block on one nuisance distribution and test under a shift of the second block's distribution, same labels and encoder; draft prediction: the accuracy drop from the rung-2 invariant content is below 2 points and from the rung-1 content at least 10 points.
- [ ] G6.3 Run, score, record; the three verdicts (identification, hierarchy real, it pays) stated separately as the monograph requires.

### Phase H: close-out
- [ ] H1 Update the report with each objective's status and the located limits; refresh `explog/stages.json` (stale: Stage B still shows "next"); consistency pass, tests, `explog.verify()`, final push; no merge to main.

## 3. Checks and supervision
Same as `docs/PLAN_ENCODER_GENERALITY.md`: `experiments/check_results.py` extended per phase (files, seeds, finite numbers, fields, encoder not collapsed); predictions unedited check; a phase gate reruns all earlier checks, `explog.verify()` and pytest; a Monitor-based supervisor launches runs four at a time and is kept armed (the container restarts when idle and kills background jobs). Every phase registers its prediction and freezes its criteria by hash before the first run, and its analysis rule is written before the runs.

## 4. Size and what cannot be done here
Roughly 150 runs in total (G1 about 40, G2 about 30, G3 about 45, G4 about 30, G6 about 20) plus the G5 re-analysis; at the observed speed on 4 CPU cores that is on the order of 8-12 hours of compute (not measured for the new settings). Not runnable in this sandbox: fine-tuning a ResNet-50 (GPU needed; SSH and raw connections to GPU hosts are blocked here).

## 5. Priorities if time is short
G0 + G1 (the deeper ladder, the objective named in the question) and G2 (the one gap with a concrete failure mechanism in the data) first; then G6 (cheap, answers "does it pay"); then G3, G4, G5.

## Log (newest last)
- 2026-10-21: plan written; nothing registered or run.

## Noted, not started
- (empty)
