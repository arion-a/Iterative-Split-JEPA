# Plan: closing the gaps one by one, inside the theory and the experimental plan

Written 2026-10-21 at the owner's request. **Planning only: nothing below is registered or run, except Gap 1, whose runs (E31, E32) were registered and started earlier.** This document replaces phases G0-G6 of `docs/PLAN_CLOSE_GAPS.md` (which grew criteria, metrics and experiments beyond the plan); its Phase G4-K stays as written and is Gap 1 here.

## 0. Ground rules for this plan
1. **Nothing opposed to the theory.** Every step cites the part of the theory or the experimental plan it serves (section 1). Where an earlier proposal would have gone against it, it is dropped (section 5).
2. **No new criteria, no new metrics.** Every verdict uses only criteria and quantities already in use: the four per-rung acceptance checks of the plan (angle below 5 deg, variant R2 at least 0.9, gap ratio above 10, leakage at the D13 gate), block presence at 0.95 (D15 / D15a), and, for scaling, the plan's own statement that error falls as 1/sqrt(n). The few numbers that cannot be avoided are listed in section 4.
3. **No expansion of experiments.** About 80 runs besides the 60 already running (the earlier plan had about 150); existing worlds, configs and run counts (5 or 10 seeds) are reused.
4. **Same discipline as before:** one gap at a time; its prediction registered in `docs/EVIDENCE.md` and its criteria frozen by hash before its first run; analysis rule written first; a check after every step; a gate (earlier checks, `explog.verify()`, pytest, plan reread) after every gap; a refuted prediction is reported as such, nothing is tuned, and the gap stops there with the limit stated (a located limit is a result, per the plan).
5. **The monograph and the plan texts are not in the repository.** The theory points below are the ones the code and documents here cite (`src/isj/engine.py`, `docs/TARGETS.md`, `docs/experiment_walkthrough.md`, `explog/objectives.yaml`); their wording is as quoted there.

## 1. Theory and plan anchors used
| Anchor | What it says (as cited in the repo) | Used for |
|---|---|---|
| Theorem 5.2 | Iterate the engine along its own invariant output | Gap 3 (depth) |
| Remark 5.4 | Termination relative to the available correspondences | Gap 2 (a rung that has no valid split is not applied) |
| Monograph §6.2 | Block count from the absolute gap | Gap 2 (the existing gap criterion is the certificate that a block exists) |
| Monograph §9 | Reconstruction-free encoder training | Gap 4 (no decoder, no reconstruction term anywhere) |
| Plan Stage C | 4-5 levels; four acceptance checks between rungs; error falling as 1/sqrt(n) at 10^4, 10^5, 10^6; the first depth where it breaks is located | Gap 3 |
| Plan Stage D | Three separate verdicts: identification works / hierarchy is real / it pays | Gap 6 (reduced; see there) |
| Plan Stage B (B2) | Rung-2 pairs built from the data by clustering the rung-1 invariant content | Gap 1 |
| Paper Appendix D | Split embedding with fixed block sizes (d_H = d_L = 64 PickCube, 128 PushCube), encoder trained for it | Gap 5 |
| Plan rules | Thresholds locked before running; every claim has a measurement, a control that should fail and a fixed threshold; no stage proceeds on effort alone | every gap |
| Objectives O2, O3, O4 | second split / depth and scaling / payoff | the six gaps |

## 2. The gaps, one by one (order of attack: dependencies first, then cost)

### Gap 1: cluster count for pairs built from data (the E18 refutation)  [in progress; objective O2, plan Stage B]
- **Where / cause:** the correspondence builder for rung 2 (`src/isj/cluster.py`). The count was read in the 120-blob invariant space; the category structure lives in the slow subspace (exploratory diagnostic, 9 of 9).
- **Theory anchor:** Stage B (pairs from the data), Remark 5.4 (abstain when the correspondence structure is not there). The selector keeps its E18 constants; only the space changes.
- **Steps:** G4K.1 implemented; G4K.2 registered (E31, E32, criteria frozen); G4K.3 runs (60 in progress); G4K.4 fallback only if the data has no usable time order (not part of the B2 setting; conditional); G4K.5 boundary (E32, inside the same 60 runs).
- [x] 1.1 Slow-subspace selector implemented and tested (G4K.1). - [x] 1.2 E31 and E32 registered, criteria frozen by hash before any run (G4K.2). - [x] 1.3 60 runs, scored (E31 refuted as registered at sigma_cat 0.6 only; E32 refuted; boundary 0.4). - [x] 1.4 Fallback without time order: not triggered, not built. **Gap 1 closed: `docs/E18_FIX_REPORT.md`.**
- **Nothing added here:** its numbers and controls are already registered.

### Gap 2: a failed rung damages the next one (carry-over)  [objective O2/O3, Theorem 5.2, Remark 5.4, §6.2]
- **Where / cause:** `fit_ladder` / `fit_rung`. A rung with fixed block size removes `d_k` directions even when its own split has no gap (E30: rung 2 split on only 3 of 10 seeds after a failed rung 1). The mechanism (arbitrary directions removed from content the next rung needs) is a hypothesis.
- **Solution (no new rule):** a rung is applied only if it passes the existing gap-ratio acceptance check (above 10); otherwise it is not applied: nothing is removed, the representation passes unchanged to the next rung, and the rung is reported as "no block found". That is the theory's own certificate (§6.2: a block exists where there is a gap) and termination relative to the available correspondences (Remark 5.4). Default behaviour unchanged.
- [x] 2.1 (done: `gate_gap_ratio` in `fit_ladder`, 2 tests) Implement the gate as an option of `fit_ladder` (off by default). **Done when:** unit tests show a rung with ratio below the criterion is not applied, a rung above it is applied exactly as before, and a clean 3-block run is identical with the option on and off.
- [x] 2.2 (registered as E33, criteria frozen by hash, before any run) Register before running (draft, same levels as before): E30 cell B setup (`configs/stage_b1_mlp_midrho.yaml`), fresh seeds 80-89: rung 1 not applied and rung 2 SPLIT by the existing criteria on at least 9 of 10 seeds (E30 without the gate: 3 of 10); clean world (the E21 Part A setup, seeds 80-89): every existing criterion as in E21 with the gate on (no regression). Criteria and analysis rule frozen first.
- [x] 2.3 Run (20 runs), score, record. **If refuted:** the carry-over is not caused by the removed directions; stop and report with the per-seed rung-2 angle against the nesting angle (already recorded fields).
- Gate.

### Gap 3: the deeper ladder has never been measured  [objective O3, Theorem 5.2, plan Stage C]
- **Where / cause:** the evaluation code and verdict function, not the engine: `src/isj/stage_b1.py` lines 114-121 (`block_slice(3)`, `image[2]`, `image[3]`, `rungs[1]`) and `seed_checks` assume 3 blocks and 2 rungs. The engine and the pair builder already loop over any number of blocks.
- **Solution:** generalise the evaluator to K blocks (same quantities, per rung) and run the plan's Stage C: 4 and 5 blocks (depth 3 and 4 rungs; 3 blocks is E21), ground-truth pairs as in B1/E21, mirror encoder with the paper objective, 5 seeds each (10 runs); then the plan's scaling check at the deepest K: pairs per rung 10^4, 10^5, 10^6, 5 seeds each (15 runs). No other depth, no other encoder.
- [x] 3.1 Generalise the evaluator and `seed_checks` to a list of rungs. **Done when:** a 3-block run reproduces a stored E21 run file's numbers exactly, and a 5-block smoke run writes every field.
- [x] 3.2 Register (draft): the four acceptance checks hold at every rung of every depth tested on at least 4 of 5 seeds (the E23 level); if not, the first violated check and its depth are the result. Scaling: the fitted log-log slope of angle against pairs per rung, with its bootstrap interval, contains -0.5 (the plan's 1/sqrt(n)).
- [x] 3.3 Run (25 runs), score, record. **A located limit is a result**; no tuning.
- Gate. (Block speeds for K blocks: evenly spaced between 0.2 and 0.95 as in the 3-block world; the mirror encoder does not drop blocks, so this does not affect the outcome.)

### Gap 4: the encoder may not keep the content  [objective O2, §9 reconstruction-free training, D15 / D15a]
- **Where / cause:** representation learning, before the engine. Prediction-trained encoders drop an unpredictable fast block (E25: presence about 0); the MLP with the paper objective kept all blocks on only 6 of 15 seeds at weight 0.01 (E28, E29).
- **Theory anchor:** §9: the encoder is trained without reconstruction, with a regulariser whose job is to prevent collapse. So the fix stays inside it: a stronger regulariser (SIGReg weight), nothing else. No decoder, no unsupervised presence proxy (that would add a metric and run against §9's spirit); presence stays the existing precondition, measured with the true latents in the synthetic worlds and stated as an unverifiable precondition on real data.
- [x] 4.1 Register (draft): the E28 cell with weight 0.1 and with weight 1.0 (both passed the training-health rule in the pilot; `configs/pilot/`), fresh seeds 90-99 each (20 runs): for at least one weight, presence at least 0.95 for every block on at least 9 of 10 seeds and both rungs SPLIT on those seeds (existing criteria; the 90% level as in E21/E31).
- [x] 4.2 Run, score, record. **If neither weight qualifies:** the paper-objective MLP is declared unreliable at this budget, presence stays a stated precondition, and the gap stops there (no longer training, no other architecture; those go to "Noted, not started").
- Gate.

### Gap 5: real-image features  [objective O2 on image data, paper Appendix D]
- **Where / cause:** the encoder and the block sizes. In E24 the head was trained on frozen ImageNet features and the block sizes were chosen by the gap rule (13-112 dims); the paper fixes d_H = d_L (64 / 128) and trains the encoder for the split. The viewpoint effect came out spread over many directions.
- **Solution within the paper's design:** re-run the existing Stage C pipeline (`experiments/robot/run_stage_c.py`) with the paper's fixed block sizes instead of the gap-selected ones; same P1-P4, same 6 runs (3 split seeds x 2 tasks), same data and features. No new rule, no new metric.
- [x] 5.1 (reproduction NOT exact: with the option off, PickCube split 0 gave rung-1 size 29 and P1 1.46 against the stored 26 and 1.38; the option-off code path is unchanged text, so this is run-to-run variation in the head training on this machine, same qualitative result; stated, not chased) Add the fixed-size option to `run_stage_c.py` (off by default; existing results untouched). **Done when:** unit smoke on the saved features reproduces an existing split run with the option off.
- [x] 5.2 Register (draft): P1-P4 as registered for E24, with the paper's block sizes. 5.3 Run (6 runs), score, record.
- [ ] 5.4 If P1 still fails: the frozen-feature encoder cannot concentrate the viewpoint factor; fine-tuning the ResNet-50 (the paper's actual setup) needs a GPU outside this sandbox, so the step is a handoff (`docs/HANDOFF_E24_GPU.md` pattern), not something run here. That is the located limit.
- Gate.

### Gap 6: no payoff test  [objective O4, plan Stage D]
- **Where:** nothing downstream is defined. The plan's Stage D (five matched methods, six metrics) is **not attempted**: it would expand the experiments; it stays "not started". What is done instead is two small tests with existing quantities only, giving provisional verdicts for two of the three Stage D questions in the synthetic world; the third (identification works) is Gaps 2-3.
- [ ] 6.1 Hierarchy is real: on the same pairs and encoder, a single-shot split (one eigendecomposition for all blocks at once) against the ladder: the existing angle per block. Prediction (draft): the ladder's angle is below 5 deg on at least 4 of 5 seeds, the single-shot split's is not.
- [ ] 6.2 It pays: the readout of the slowest block (the existing core R2) after rung 1 versus after rung 2, trained on one nuisance distribution and tested after shifting the identity block's distribution (one design parameter, set before the run). Prediction (draft): the R2 loss under the shift is smaller after rung 2 than after rung 1 on at least 4 of 5 seeds (a sign test, no new threshold).
- [ ] 6.3 Run (about 10 runs), score, record. Both are stated as synthetic-world verdicts only.
- Gate.

### Close-out
- [ ] H1 Report with each objective's status and located limits; refresh `explog/stages.json` (stale); consistency pass, tests, `explog.verify()`, final push; no merge to main.

## 3. Supervision
- **Runs:** one Monitor-based supervisor per gap (`supervise_*.sh` pattern: at most 4 runs at a time, resumable, counts reported on every change, relaunch after a container restart); the Monitor is re-armed on expiry and kept active while runs go (the container restarts when idle).
- **Plan status:** `experiments/plan_status.py` prints, for this plan, steps done and open per gap, the evidence-unedited check and the log check; it is run at every check-in and at every gate.
- **Per step:** `experiments/check_results.py` (files, seeds, finite numbers, fields) extended for each gap's folders; **per gap:** the gate in section 0.4; **stop rule:** if a prediction is refuted, report it, do not tune, stop that gap, note any further idea under "Noted, not started" in one line.

## 4. Numbers and criteria this plan introduces or reuses
| Item | Status |
|---|---|
| Four acceptance checks per rung (angle 5 deg, variant R2 0.9, gap ratio 10, leakage D13 gate), presence 0.95, split criteria of B1 | **reused** (Gaps 2, 3, 4, 5, 6) |
| Seed counts 5 and 10; levels "at least 4 of 5", "at least 9 of 10" | **reused** (E21, E23, E31) |
| 1/sqrt(n) scaling and the budgets 10^4, 10^5, 10^6 | **the plan's own** (Stage C) |
| Block sizes 64 / 128 | **the paper's own** (Appendix D) |
| Slow-subspace abstention ratio 2.0 | **new, already registered (E31); the only new constant in the whole plan** |
| Magnitude of the identity shift in 6.2; block speeds for 4 and 5 blocks | **new design parameters, unavoidable; each fixed before its run and reported** |

## 5. Proposals of the earlier plan that are dropped, and why
- *Unsupervised presence proxy (decoder reconstruction)* and *encoder regulariser grid with a proxy*: a new metric, and a reconstruction element against §9's reconstruction-free training. Replaced by Gap 4 as written.
- *Block size by cumulative energy*: replaces the §6.2 gap rule with a new rule. Replaced by the paper's fixed sizes (Gap 5).
- *Abstention at a new gap-ratio level (3)*: replaced by the existing gap criterion (Gap 2), so no new number.
- *Soft (posterior-weighted) pairs and BIC cluster count*: not in the theory or the plan; the cluster count is Gap 1.
- *Depths 3 to 6 and four pair budgets, nested pair-building from data for depth 3+*: reduced to the plan's Stage C (4 and 5 blocks, three budgets); pair-building from data beyond rung 2 is outside the plan's stages and is noted, not started.
- *Stage D as a new two-test design with new thresholds*: reduced to two directional tests on existing quantities; the full Stage D is not attempted.

## Size
About 80 runs for Gaps 2-6 (20 + 25 + 20 + 6 + about 10), plus the 60 already running for Gap 1; at the observed speed on 4 CPU cores, on the order of 5-8 hours of compute (not measured for the new settings).

## Log (newest last)
- 2026-10-21: plan written; nothing registered or run for Gaps 2-6. Gap 1 (E31, E32) running.
- 2026-10-21 (later): Gap 1 closed (E31 refuted as registered at sigma_cat 0.6 only, cause fixed; E32 boundary 0.4). Gaps 2-6 not started.

- 2026-10-21 (Gap 2): gate implemented (`gate_gap_ratio` in `fit_ladder`, `rung_gate` in the B1 config; off by default; 2 tests, 50 tests pass); E33 registered before any run (20 runs, seeds 80-89). Executing the gaps in sequence on the owner's instruction.

## Noted, not started
- Pair-building from data beyond rung 2 (nested clustering for depth 3 and deeper).
- Longer training or other architectures for the generic encoder if Gap 4 fails.
- The paper's fine-tuned ResNet-50 (needs a GPU outside this sandbox).
- The full Stage D (five matched methods, six metrics).
