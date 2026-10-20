# Completion plan: from the current stage to the finishing line

Created 2026-10-20. Tracks only work the owner has already asked for. Binding order of authority is unchanged: `docs/DECISIONS.md`, `docs/EVIDENCE.md` (pre-registered predictions, never edited), `docs/REPORTING.md`, `DECISION_POLICY.md`. Scope rule (AGENTS.md): do only what is asked; anything else seen on the way is noted in one line under "Noted, not started" at the bottom and waits for the owner.

How to use this file: tick a step only when its **done when** line is true, put the date and the evidence path next to it, and add one line to the Log at the bottom. One explog entry per phase closed (`explog.append("note", ...)`), and `explog.verify()` must stay True.

## Where we are (2026-10-20 19:35 UTC)

| Item | State |
|---|---|
| E21 Part A (B1 world, 3 arms x seeds 20-29 = 30 runs) | 4 / 30 files |
| E21 Part B (B2 world, sigma_cat 0.1 and 0.4, seeds 20-29 = 20 runs) | 6 / 20 files |
| E22 (probe-image test) | uses the E21 Part B run files; nothing separate to run |
| E23 (generic MLP encoder, B1 ladder, seeds 30-34, arms main + shuffled_rung2 = 10 runs) | config ready (`configs/stage_b1_mlp.yaml`), not started |
| E24 (robot data, PickCube + PushCube, 100 groups of 8 each) | about 20 / 100 and 15 / 100 groups; GPU route blocked from this sandbox |
| Environment | 4 CPU cores, no GPU; the container restarts about every 15 minutes and kills background jobs |

## Phase 0: keep the jobs alive (runs through every other phase)

- [ ] 0.1 Relaunch protocol. After any restart (`uptime` shows a few minutes, `pgrep -fc "run_stage|gen_robot"` shows 0 or 1), relaunch the same commands. All runners skip result files that exist, so nothing is lost except the run in progress.
  - E21 B1: `python experiments/run_stage_b1.py --config configs/stage_b1.yaml --out results/stage_b1_e21 --seeds 20..29 --arms main shuffled_rung2 rank1_rung2`
  - E21 B2: `python experiments/run_stage_b2_spec.py --config configs/stage_b2_noop.yaml --out results/stage_b2_e21 --seeds 20..29 --sigmas 0.1 0.4`
  - Robot data: `bash experiments/robot/run_gen.sh <proc> <n_procs>` (needs `ms310` env in the scratchpad)
  - Set `OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=src`; logs go to the scratchpad `logs/` folder.
- [ ] 0.2 Commit and push new result files, `explog/chain.jsonl` and `docs/STATUS.md` at every check, so a restart never loses saved results.
- **Done when:** every phase below has its files on the branch. This phase has no end of its own.
- **Known risk:** progress is about one finished run per 15 minutes under restarts. If it does not improve, the owner decides (see Phase 3 fallback and the GPU handoff `docs/HANDOFF_E24_GPU.md`).

## Phase 1: finish E21 and record E21 and E22

- [ ] 1.1 B1 runs complete: 30 files in `results/stage_b1_e21/`. **Done when:** `ls results/stage_b1_e21/*.json | wc -l` is 30.
- [ ] 1.2 B2 runs complete: 10 files in each of `results/stage_b2_e21/sigma_cat_0.1/` and `.../sigma_cat_0.4/`. **Done when:** both directories hold 10 files.
- [ ] 1.3 Run the analysis: `python experiments/analyse_e21_e22.py` (writes `E21_REPORT.md` and `E21_E22_REPORT.md` under the results folders). **Done when:** both reports exist and list per-criterion counts over the 10 seeds.
- [ ] 1.4 Score against the registered E21 text in `docs/EVIDENCE.md` without changing it: Part A (frozen B1 verdict rule, controls, D13 leakage gate reported); Part B (i) sigma 0.1 recovery >= 0.60 and gap > 10 in >= 90% of seeds, (ii) sigma 0.4 gap >= 0.6 x perfect-cluster gap in >= 90%, (iii) nesting angle < 5 deg in every run, (iv) no metric damaged beyond one untreated seed-std. Each part and sub-claim reported separately.
- [ ] 1.5 Score E22 from the same files: orthogonalised-identity rung-2 angle <= 5 deg in >= 90% of the 20 runs, and >= 3 deg below the raw angle in >= 90%. Refuted if it stays near the raw angle.
- [ ] 1.6 Record: outcome lines for E21 and E22 appended under their entries in `docs/EVIDENCE.md` (outcome only, prediction text untouched), a `docs/STATUS.md` line, and an explog entry with the verdicts and plain-language result (paper metric names, per `docs/REPORTING.md`).
- **Done when:** E21 and E22 each have a verdict (confirmed, partly confirmed, or refuted) written in EVIDENCE, STATUS and explog, and committed.
- **Estimate (unmeasured):** 26 B1 files and 14 B2 files still to go.

## Phase 2: E23, a non-mirror encoder

- [x] 2.1 Start when a core is free. `python experiments/run_stage_b1.py --config configs/stage_b1_mlp.yaml --out results/stage_b1_e23 --seeds 30 31 32 33 34 --arms main shuffled_rung2 --criteria-sha configs/stage_b1.criteria.sha256`. The criteria block in that config must hash to the value in `configs/stage_b1.criteria.sha256` (checked at start).
- [x] 2.2 **Done when:** 10 files in `results/stage_b1_e23/`.
- [x] 2.3 Score per criterion over the 5 seeds with the same scorer used for B1 (check whether `experiments/build_b1_report.py` or `rescore_b1.py` accepts the E23 folder; if neither does, report per-criterion pass counts directly from the run files and say so). Registered prediction: each registered B1 criterion except possibly the texture variant R2 holds on >= 4 of 5 seeds; shuffled control behaves. Refuted if two or more criteria fail on two or more seeds.
- [x] 2.4 Record outcome in EVIDENCE, STATUS, explog. **Done when:** E23 has a verdict on the branch.

## Phase 3: E24, robot data (the largest phase)

- [ ] 3.1 Data generation: 100 groups per task in `data/robot/PickCube` and `data/robot/PushCube` (`.gitignore` keeps `data/` out of git). **Done when:** both folders hold 100 `group_*.npz` files. Estimate: about 157 s per group per process under load, so 200 groups on 2 processes is about 4.5 hours of uninterrupted running; on all 4 cores after E21 and E23 finish, about 2 hours.
- [ ] 3.2 Feature extraction: `python experiments/robot/extract_features.py --task PickCube --threads 4` and the same for PushCube. Frozen ImageNet ResNet-50, 2048-d, float16 per group. CPU run is slow (roughly 100,000 images). **Done when:** `data/robot/feat/` holds a feature file per group for both tasks.
- [ ] 3.3 Stage C runs: for each task and split seed 0, 1, 2: `PYTHONPATH=src python experiments/robot/run_stage_c.py --task <T> --split-seed <S> --out results/stage_c --head-steps 6000`. **Done when:** six result files exist in `results/stage_c/`.
- [ ] 3.4 Report: `python experiments/robot/build_stage_c_report.py`. **Done when:** the report and figure exist with per-task, per-criterion tables.
- [ ] 3.5 Verdict per task against the registered E24 text: P1 viewpoint response V1/Q1 >= 3 (paper 8.4x PickCube, 14.0x PushCube), P2 trajectory response V2/Q2 >= 1.5 (paper 2.1x, 3.1x), P3 controls (shuffled-pair rung-1 gap ratio < 2; random split both ratios < 1.5), P4 camera id decoded >= 0.9 from the rung-1 variant block and <= 0.65 from the invariant content. Confirmed for a task only if P1-P4 all hold; a finding that no gap clears the threshold is a result.
- [ ] 3.6 Report the limits in plain words: simulated data, frozen ImageNet encoder with a trained head, our own trajectory-variation scheme, any reduced group count.
- [ ] 3.7 Record outcome in EVIDENCE, STATUS, explog. **Done when:** E24 has a per-task verdict on the branch.
- **Fallback (owner decides, flagged if used):** if generation cannot finish, report E24 on the groups that exist, state the count, and keep the registered criteria unchanged. Alternative route: the owner runs `docs/HANDOFF_E24_GPU.md` from a session that can reach the GPU box; its results come back on branch `claude/vast-results`.

## Phase 4: close-out

- [ ] 4.1 Consistency pass: EVIDENCE, STATUS, DECISIONS and explog agree on every outcome since E9; `python -c "from isj import explog; print(explog.verify())"` prints True; 44+ tests pass (`python -m pytest -q`).
- [ ] 4.2 Regenerate the combined reports that exist for earlier stages if their inputs changed (`experiments/build_e10_report.py`, `build_e11_summary.py`), only where a new result touches them.
- [ ] 4.3 One final plain-language report of what was asked: for every registered item since the restart (E21, E22, E23, E24) the prediction, the result with its numbers, and the outcome, including refuted ones, plus the paper-readiness answer redone with the new evidence.
- [ ] 4.4 Final push of the working branch. Merging to `main` only when the owner says so.
- **Done when:** the final report is committed and the owner has it.

## Checks (kept minimal; the owner asked for strong checks after every step and a review after every phase)

**After every step** (automatic, `python experiments/check_results.py <mode> [--final]`; modes `e21b1`, `e21b2`, `e23`, `data`, `feat`, `evidence`): right file names and seeds, JSON loads, every number finite, required fields present (including the E22 fields), image and feature shapes, both cameras present and different, every trajectory successful. These test integrity, not the claim; claims are scored only by the analysis scripts against the registered text. A step is not ticked until its check passes with `--final` where it has a count.

**Predictions never edited:** `check_results.py evidence` fails if any line of `docs/EVIDENCE.md` was deleted or changed since commit `b0c0a10` (outcome lines may only be added).

**Phase gate (after every phase, before starting the next):** (1) rerun the step checks of every earlier phase, not just the current one; (2) `explog.verify()` is True and `python -m pytest -q` passes; (3) reread this plan against the branch: counts in the table at the top match the files, no step ticked without evidence, nothing run that is not in the plan; (4) one explog entry for the phase and a Log line below stating the gate result; (5) rebuild `docs/EXPERIMENT_TABLE.md` and the log page (`python experiments/build_log_table.py; python experiments/build_log_page.py`). If any check fails the phase stays open and the failure is written in the Log.

**The record:** `explog/chain.jsonl` is the hash-chained database (each entry holds what happened, how, outputs, artifact fingerprints, the objective it serves, interpretation, verdict, and a plain-language block with relevance). `docs/EXPERIMENT_TABLE.md` is the table view: idea (objective), what happened, record (hash, artifacts), contribution (verdict, reading), relevance. `explog/LOG.md` and `explog/log_page.html` are the long views. All are generated from the chain.

## Order and dependencies

Phase 0 runs throughout. Phase 1 and the Phase 3 data generation run in parallel now (4 cores). Phase 2 starts when Phase 1's B1 or B2 job frees a core. Phase 3.2 onward needs 3.1. Phase 4 needs Phases 1-3 (or the owner's fallback decision).

## Log (newest last)

- 2026-10-20 19:35 UTC: plan written. E21 B1 4/30, B2 6/20; robot data 20 and 15 of 100 groups. Container restarts about every 15 minutes; jobs relaunched after each.
- 2026-10-20 20:55 UTC: E21 Part B complete (20/20, final check passes). E23 complete (10/10): REFUTED as registered (8 of 9 non-excepted criteria 0/5 seeds; rung-1 gap 1.1). Phase 2 gate: evidence unedited (PASS), explog verify True, integrity checks pass for all files so far. Phase 1 awaits B1 (14/30); Phase 3 data at 50/40 of 100.

## Noted, not started

- E23 refuted as registered; it does not separate architecture, objective and training budget (none was varied). Waiting for the owner; nothing started.

- `explog.verify()` was False on 2026-10-20 (entry 296 stale after the E22 fields were added to `stage_b2_spec.py`); declared stale the same day, verify True again.
