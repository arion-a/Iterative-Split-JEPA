# COLUMBIA_FULL_PLAN.md — the full handshake experiment on the Columbia real double-pendulum data (C2)

Written 2026-10-21 at the owner's request: re-run the whole experiment on the Columbia data, plan it phase by phase and step by step, supervise it, resolve issues, and finish.
Everything for C2 is in this one place: this plan (what and why), `plans/columbia_full.yaml` (the same steps, machine-readable), `experiments/supervisor.py` (runs them, verifies each, resumes), `configs/columbia_full.yaml` (frozen criteria and recipe), `docs/EVIDENCE.md` (the registered prediction and, later, the outcome), `results/columbia_full/` (raw results, `REPORT.md`, supervisor state).

**One command:** `python experiments/supervisor.py plans/columbia_full.yaml` (resumes after a halt; `--status` prints the tracker; `--reset <ID>` reruns a step).

## 1. Ground rules
* The theory is not on trial in the sense of "must pass": every criterion was frozen before the run and the result is reported as measured. Only **defects** are fixed (leakage, a faulty statistic, a crash), never thresholds. The supervisor halts on a real failure; a step is done only if its command **and** its check succeed.
* Criteria are **unchanged** from the handshake and from C1 (whose numbers were seen before this registration; disclosed). Release = video, split by video, so train and test never share a video.
* The simulator-free evaluator (tracked energy from `phys_vars.npy`, loaded through the allowlist-only unpickler `src/isj/safe_npy.py`) is used only for naming, controls and the report-only ceiling probe (D13). Not applicable to real data, therefore not run: E35 and E36 (planted worlds).

## 2. What C2 fixes relative to C1 (issues found and resolved)
| # | Issue in C1 | Resolution | Verified by |
|---|---|---|---|
| I1 | Neighbouring clip ids are consecutive windows of one video, so a contiguous-block split could share a video between train and test | Grouping recovered: 100 videos × 11 clips (pixel-continuity breaks fall on multiple-of-11 boundaries; tracked-angle continuity 87% vs random-pair median 0.74 rad); video = release; split by video (70 / 10 / 20) | `experiments/prep_columbia_full.py` (asserts ≥ 98% of breaks on the boundary), `tests/test_columbia_full.py` |
| I2 | "Between-clip share of tracked energy" came out above 1 (masked-variance artefact) | Proper one-way ANOVA ICC for unbalanced groups, `handshake_eval.anova_icc` | `tests/test_quotient_audit.py::test_anova_icc_known_values` |
| I3 | 4000-step encoder, small data | The B1 scaling recipe (8000 steps), chosen because B1 showed naming and seed agreement improve with scale in simulation; not tuned on Columbia | `configs/columbia_full.yaml` |
| I4 | No control arms in the first run | Flat, shuffled-pair and temporal-only arms are part of the registered run | `results/columbia_full/REPORT.md` |
| I5 | Test pollution of the chain by the supervisor's own unit tests (found while building it) | Supervisor logs to the chain only for plans with `chain: true`; the incident is recorded | chain note, `tests/test_supervisor.py` |

## 3. Registered predictions (text in `docs/EVIDENCE.md`, "C2")
(a) certificate on every seed, 20 test videos: V ≤ 0.05, between-video ICC ≥ 0.9, L ≤ 1.02, 8-step rollout ≤ 0.35 · (b) naming |Spearman(psi, tracked total energy)| ≥ 0.5 · (c) flat arm < 0.5 · (d) seed agreement ≥ 0.9. Each judged separately; "confirmed" only if all four hold. Claude's expectation: (b), (c) as in C1; (a) uncertain (rollout 0.43–0.45 in C1); (d) probably holds.

## 4. Phases, steps, tests and checkpoints
| Step | Phase | What | Test / check | Supervisor |
|---|---|---|---|---|
| S0.1 | 0 set-up | Supervisor behaves (done / halt / transient retry / resume / reset) | `tests/test_supervisor.py` | ☐ |
| S0.2 | 0 | Registration intact: hash matches, prediction text present, no C2 result exists yet | inline assertion | ☐ |
| S1.1 | 1 data | Group clips into videos, verify the rule, build video sequences and evaluator table | asserts in `prep_columbia_full.py` | ☐ |
| S1.2 | 1 | Grouping, shapes, valid-energy fraction (80–95%) | `tests/test_columbia_full.py -k grouping` | ☐ |
| S1.3 | 1 | **Phase 1 gate**: safe loader (blocks code execution), statistics, sealed-audit scan, audit | tests + `audit_stage_v.py --no-tests` | ☐ |
| S2.1 | 2 run | 3 seeds × arms {main, flat, shuffled, temporal-only}; certificate, naming, reach, seed agreement, report-only ceiling probe | results sanity test (all arms, finite, ICC in range, 3 seeds, 6 reach horizons) | ☐ |
| S3.1 | 3 analysis | Report in REPORTING format (gate table, controls, informational, C1 comparison) | non-empty `REPORT.md` | ☐ |
| S3.2 | 3 | Mechanical outcome (a)–(d) into EVIDENCE, STATUS and the chain | marker in EVIDENCE | ☐ |
| S4.1 | 4 close | Full audit: all tests, chain with digests, criteria hashes, every raw JSON logged, outcomes | `audit_stage_v.py` | ☐ |
| S4.2 | 4 | **Plan-alignment check**: every step done, registration unchanged, outcome after registration, all seeds logged | `check_plan_alignment.py` | ☐ |

Phase checkpoints are S1.3 (data) and S4.1–S4.2 (everything); after the run the agent also re-reads this plan against the report for misalignment (section 6).

## 5. After the supervisor finishes
Interpretation lines are added to `docs/EVIDENCE.md` below the mechanical outcome; `docs/PAPER_RESULTS.md` and `docs/ROADMAP_TO_FINISH.md` get one line each; the tree is committed and pushed. Nothing earlier is rewritten.

## 6. Issue log (filled during execution; newest last)
_(none yet — halts and fixes are recorded here and in the chain)_

## 7. Tracker
`python experiments/supervisor.py plans/columbia_full.yaml --status` is the live tracker; the final state is copied below when the plan completes.
