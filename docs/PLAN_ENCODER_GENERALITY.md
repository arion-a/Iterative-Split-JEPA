# Plan: does iterative splitting work on any encoder's latent space? (E25-E27)

Created 2026-10-21 at the owner's request. Same rules as `docs/COMPLETION_PLAN.md`: predictions in `docs/EVIDENCE.md` are never edited (check: `python experiments/check_results.py evidence`), refuted results are results, nothing is tuned to fit, only work listed here is done; anything else goes to "Noted, not started" and waits. Criteria: `configs/layered.yaml` (decision D15), frozen by hash before any run.

Question: the owner holds that splitting is a property of the representation, so it should work on any encoder's output. Claude's reading of E23: the prediction-trained MLP may have dropped the fast block (speed 0.2), so nothing was there to split. Measure the right thing: first whether each true block is present in the embedding, then whether it is separable.

## Phase A: instruments, criteria, registration (before any run)
- [x] A1 Presence probe (`audits.mlp_r2`) wired into the B1 runner (`presence` field: linear and nonlinear R2 per true block); test `tests/test_presence.py`. **Done when:** the test passes and a smoke run writes the field. Done.
- [x] A2 Four equal-predictability configs and the E25 config; each code path smoke-tested (`--smoke 50`). Done.
- [x] A3 Layered criteria frozen (`configs/layered.yaml`, `configs/layered.sha256`; `analyse_layered.py` refuses to run if the hash changes). Done.
- [x] A4 Predictions E25-E27 registered in EVIDENCE, D15 in DECISIONS, plan entry in the log, committed and pushed before the first run. **Done when:** the commit exists. 

## Phase B: runs (30 runs, all B1 world, ground-truth pairs, seeds 30-34)
- [ ] B1 E25: `stage_b1_mlp.yaml` -> `results/stage_b1_e25`, arm main (5 files).
- [ ] B2 E26: `stage_b1_eqrho_mlp_predict.yaml` -> `results/stage_b1_e26`, arms main + shuffled_rung2 (10 files).
- [ ] B3 E27: three cells -> `results/stage_b1_e27/{mirror_lejepa,mlp_lejepa,mirror_predict}`, arm main (15 files).
- **Step check:** `python experiments/check_results.py enc [--final]` (right files and seeds, finite numbers, `presence` field present with three values in [-1, 1.01], encoder trained: minimum embedding std above 0.1). **Gate:** earlier checks rerun, `explog.verify()`, pytest, plan reread.

## Phase C: analysis and verdicts
- [ ] C1 `python experiments/analyse_layered.py` (rules written before the runs). **Done when:** `results/enc_generality/REPORT.md` has E25, E26, E27 verdicts.
- [ ] C2 Outcome lines for E25, E26, E27 appended in EVIDENCE (additions only), STATUS lines, one explog entry per verdict, table and log page rebuilt.
- **Gate:** as above.

## Phase D: investigation of whatever the verdicts leave open (analysis of the saved run files only; any new run is written under "Noted, not started")
- [ ] D1 If E25 is refuted (texture present): measure why the split still failed (pair-difference spectrum of the present block, effective rank of its image).
- [ ] D2 If any cell has PRESENT_NOT_SEPARABLE rungs: measure the effective rank (participation ratio of singular values) of the block's linear image and the pair-difference spectrum, to say whether the block is spread over many directions (nonlinear encoder) or the criteria are the issue.
- [ ] D3 If blocks are absent or partial even at equal speeds (E26 (a) fails): check training state (final loss, minimum embedding std) and probe capacity (a second probe size on the saved fields is not possible: encoders are not saved) and report what is and is not established.
- **Done when:** each open item is either explained with numbers or stated as not testable from the saved files.

## Phase E: close-out
- [ ] E1 Layered re-reading of earlier results (E21 mirror, E23, E24) from existing numbers, labelled analysis not new claims.
- [ ] E2 Final report `docs/ENCODER_GENERALITY_REPORT.md`: per test the prediction, result with numbers, outcome; what the evidence says about "any encoder"; limits.
- [ ] E3 Consistency pass, tests, `explog.verify()`, final push. No merge to main.

## Supervisor
`scratchpad/supervise_enc.sh` runs inside a Monitor: it launches up to 4 runs at a time from the job list (E25, E26, E27 cells; every runner resumes by file), relaunches after a container restart, and reports each change in file counts. The container restarts whenever the session is idle and kills background jobs, so a Monitor (30 minutes, re-armed on expiry) is kept active during Phase B.

## Log (newest last)
- 2026-10-21: plan written; Phase A done; Phase B starting.

## Noted, not started
- (empty)
