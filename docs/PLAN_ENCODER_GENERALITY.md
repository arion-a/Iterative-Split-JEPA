# Plan: does iterative splitting work on any encoder's latent space? (E25-E27)

Created 2026-10-21 at the owner's request. Same rules as `docs/COMPLETION_PLAN.md`: predictions in `docs/EVIDENCE.md` are never edited (check: `python experiments/check_results.py evidence`), refuted results are results, nothing is tuned to fit, only work listed here is done; anything else goes to "Noted, not started" and waits. Criteria: `configs/layered.yaml` (decision D15), frozen by hash before any run.

Question: the owner holds that splitting is a property of the representation, so it should work on any encoder's output. Claude's reading of E23: the prediction-trained MLP may have dropped the fast block (speed 0.2), so nothing was there to split. Measure the right thing: first whether each true block is present in the embedding, then whether it is separable.

## Phase A: instruments, criteria, registration (before any run)
- [x] A1 Presence probe (`audits.mlp_r2`) wired into the B1 runner (`presence` field: linear and nonlinear R2 per true block); test `tests/test_presence.py`. **Done when:** the test passes and a smoke run writes the field. Done.
- [x] A2 Four equal-predictability configs and the E25 config; each code path smoke-tested (`--smoke 50`). Done.
- [x] A3 Layered criteria frozen (`configs/layered.yaml`, `configs/layered.sha256`; `analyse_layered.py` refuses to run if the hash changes). Done.
- [x] A4 Predictions E25-E27 registered in EVIDENCE, D15 in DECISIONS, plan entry in the log, committed and pushed before the first run. **Done when:** the commit exists. 

## Phase B: runs (30 runs, all B1 world, ground-truth pairs, seeds 30-34)
- [x] B1 E25: `stage_b1_mlp.yaml` -> `results/stage_b1_e25`, arm main (5 files).
- [x] B2 E26: `stage_b1_eqrho_mlp_predict.yaml` -> `results/stage_b1_e26`, arms main + shuffled_rung2 (10 files).
- [x] B3 E27: three cells -> `results/stage_b1_e27/{mirror_lejepa,mlp_lejepa,mirror_predict}`, arm main (15 files).
- **Step check:** `python experiments/check_results.py enc [--final]` (right files and seeds, finite numbers, `presence` field present with three values in [-1, 1.01], encoder trained: minimum embedding std above 0.1). **Gate:** earlier checks rerun, `explog.verify()`, pytest, plan reread.

## Phase C: analysis and verdicts
- [x] C1 `python experiments/analyse_layered.py` (rules written before the runs). **Done when:** `results/enc_generality/REPORT.md` has E25, E26, E27 verdicts.
- [x] C2 Outcome lines for E25, E26, E27 appended in EVIDENCE (additions only), STATUS lines, one explog entry per verdict, table and log page rebuilt.
- **Gate:** as above.

## Phase D: investigation of whatever the verdicts leave open (analysis of the saved run files only; any new run is written under "Noted, not started")
- [x] D1 (not needed: E25 confirmed, not refuted) If E25 is refuted (texture present): measure why the split still failed (pair-difference spectrum of the present block, effective rank of its image).
- [x] D2 (not needed: no PRESENT_NOT_SEPARABLE rung in any cell) If any cell has PRESENT_NOT_SEPARABLE rungs: measure the effective rank (participation ratio of singular values) of the block's linear image and the pair-difference spectrum, to say whether the block is spread over many directions (nonlinear encoder) or the criteria are the issue.
- [x] D3 (triggered by E27, not E26: the MLP + paper-objective cell collapsed to a constant; cause found in the saved training state: regulariser weight 1e-6 copied from the mirror setup) Repair = E28, registered before its pilot:
  - [x] D3a Pilot: 5 regulariser weights {1e-4, 1e-3, 1e-2, 1e-1, 1} on seed 99, `configs/pilot/`, `results/stage_b1_e28_pilot/`.
  - [x] D3b Select the smallest weight with final minimum embedding std at least 0.5 (rule in EVIDENCE E28), write the chosen weight to the log and make `configs/stage_b1_eqrho_mlp_lejepa_w<chosen>.yaml` BEFORE launching E28.
  - [x] D3c E28 runs: 5 seeds (30-34), main arm, `results/stage_b1_e28`.
  - [x] D3d Score with `analyse_layered.py` (E28 section written before the runs), outcome in EVIDENCE, STATUS, log.
  - Original D3 text: check training state (final loss, minimum embedding std) and probe capacity (a second probe size on the saved fields is not possible: encoders are not saved) and report what is and is not established.
- **Done when:** each open item is either explained with numbers or stated as not testable from the saved files.

## Phase E: close-out
  - [x] D4 Prospective test of the stricter presence threshold (found in the descriptive analysis `PRESENCE_VS_SPLIT.md` after E28): E29, registered before its runs with `configs/layered_v2.yaml` frozen by hash.
    - [x] D4a E29 runs: E28 cell, seeds 35-44, `results/stage_b1_e29` (10 files); step check `check_results.py enc --final`.
    - [x] D4b Score with `experiments/analyse_e29.py` (rule written before the runs); outcome in EVIDENCE, STATUS, log; D15a stays a candidate unless E29 confirms it (then adopted in D15 as an amendment).
- [x] E1 Layered re-reading of earlier results (E21 mirror, E23, E24) from existing numbers, labelled analysis not new claims.
- [x] E2 Final report `docs/ENCODER_GENERALITY_REPORT.md`: per test the prediction, result with numbers, outcome; what the evidence says about "any encoder"; limits.
- [x] E3 Consistency pass, tests, `explog.verify()`, final push. No merge to main.

## Phase F: check and run the three criteria claims (owner request, 2026-10-21 later)
- [x] F1 Re-check claims 1-3 from the raw files with both probes (`experiments/verify_claims.py` -> `VERIFY_CLAIMS.md`). Result: claims 1 and 2 reproduce exactly (0 of 37 below 0.95 split; 42 of 43 at or above), claim 3 fits 80 of 80 but rests on a single distinguishing rung.
- [x] F2 Register E30 (prospective test, cells A and B, seeds 45-54, `configs/layered_v2.yaml` frozen) and write `analyse_e30.py` before any run; commit and push.
- [ ] F3 E30 runs: 20 files (`results/stage_b1_e30/A`, `.../B`); step check `check_results.py enc --final`.
- [ ] F4 Score with `analyse_e30.py`; outcome lines in EVIDENCE (additions only), STATUS, log; update the criteria paragraph of `docs/ENCODER_GENERALITY_REPORT.md` and D15a with the result.
- [ ] F5 Phase gate: earlier checks rerun, `explog.verify()`, pytest, plan reread; final push.

## Supervisor
`scratchpad/supervise_enc.sh` runs inside a Monitor: it launches up to 4 runs at a time from the job list (E25, E26, E27 cells; every runner resumes by file), relaunches after a container restart, and reports each change in file counts. The container restarts whenever the session is idle and kills background jobs, so a Monitor (30 minutes, re-armed on expiry) is kept active during Phase B.

## Log (newest last)
- 2026-10-21: plan written; Phase A done; Phase B starting.
- 2026-10-21 (later): Phases B and C done. E25 confirmed, E26 confirmed, E27 confirmed as registered but vacuous in the MLP + paper-objective cell (collapsed encoder). D1/D2 not needed. D3 triggered: E28 registered (repair of the collapsed cell); pilot next.
- 2026-10-21: E28 pilot: four of five pilot runs crashed at start (config typo: weights written as 1e-4 etc. are read by YAML as text, not numbers); fixed the number format in `configs/pilot/` and in the supervisor's E28 config step; no result was affected (the runs crashed before writing anything); the 1.0 pilot had run (minimum embedding std 0.944). The four were relaunched.
- 2026-10-21: E28 pilot done (minimum embedding std 1.3e-5 / 0.41 / 0.79 / 0.95 / 0.94 for weights 1e-4 / 1e-3 / 1e-2 / 1e-1 / 1.0). Weight chosen by the registered rule: 0.01; logged in the chain before any E28 run. E28 runs started.
- 2026-10-21: E28 scored: not confirmed (2 of 5 seeds split like the mirror, 3 partial). Descriptive analysis of 60 rungs: split rungs all had presence at least 0.972, partly present non-split rungs at most 0.911. E29 registered (prospective test of a 0.95 threshold, seeds 35-44) before its runs.
- 2026-10-21 (later): E29 scored: refuted as registered (8 of 9 rungs at 0.95+ split; 0 of 11 below split); the one exception sits in a run whose rung 1 had failed. Conditional descriptive rule fits 80 of 80 rungs. D15a not adopted as unconditional. Phase D done. Phase E next.
- 2026-10-21 (final): Phase E done. Layered re-reading and report `docs/ENCODER_GENERALITY_REPORT.md`; `docs/FINAL_REPORT.md` has an update note on the E23 reading. Plan complete; branch not merged to main (owner decides).
- 2026-10-21 (Phase F): re-check done; E30 registered (see EVIDENCE) and runs next.

## Noted, not started
- (empty)
