# ROADMAP_TO_FINISH.md — from the current state to the finish line (stage V, video-first handshake)

Written 2026-10-20. This is the tracker: work the steps in order, tick them, and append one chain entry (`python -m isj.explog append …` or `isj.explog.append`) per step.
Binding order of authority is unchanged: `docs/DECISIONS.md` > `docs/EVIDENCE.md` > `docs/IMPLEMENTATION_PLAN.md` > this roadmap > `docs/source/*`.
Scope rule (AGENTS.md): steps marked **[OWNER]** need your decision or your material before anything runs; steps marked **[AGENT]** are mine once unblocked. No new prediction is run until it is written in `docs/EVIDENCE.md` first.

## 0. Where we are (2026-10-20)

| Item | State | Evidence |
|---|---|---|
| P0 housekeeping, rulings D13–D33, registrations | done | `docs/DECISIONS.md`, `docs/EVIDENCE.md` |
| P1 simulator, renderer, sealed audit | done | 59 tests green |
| P2–P3 handshake (3 seeds) | run: E31c′ confirmed; E31d, E31e(S1), P-stab refuted; P-ctrl met | `results/handshake/REPORT.md` |
| P4 hierarchical AR world | run: E35 refuted (RUNGS 1, registered 4); per-rung gates and control met | `results/hier/REPORT.md` |
| P5 real video, public clips | run, informational | `results/real/REPORT.md` |
| F1 follow-up | refuted: release-free slow-feature arm = main arm | `results/followup/*.json` |
| E36 | run: refuted as worded (closure ratio 1.25–1.32 against ≥ 2.0; (S) and control met) | `results/e36`, `docs/EVIDENCE.md` |
| Live capture on the owner's footage | **blocked on footage** | `docs/IMPLEMENTATION_PLAN.md` P5 step 5.3 |
| Log chain | valid (292 entries, 48 declared-superseded artifact references) | `python -c "from isj import explog; print(explog.verify())"` |

## 1. The finish line

The experiment is finished when all five hold:

1. **Every registered stage-V prediction has an outcome** in `docs/EVIDENCE.md` (confirmed, refuted, or "not run" with a written reason): E31c′, E31d, E31e, E31f, P-stab, P-ctrl, E35, E36, E37, E38, E43, E44–E47, F1.
2. **The live-capture handshake has been run on the owner's own footage** (E44 report-only, E45–E47 judged), or the owner has declared in writing that the live step is out of scope for this paper.
3. **One paper-ready results set exists:** the figures and tables of LIVE_DATA_PLAN §6 and the REPORTING formats, each tied to a chain entry and a raw JSON (SYNTHESIS E34, "no orphan theorems").
4. **Integrity checks pass:** full test suite, chain links and artifact digests (`explog.verify()`), criteria-hash checks, sealed-audit token scan.
5. **The owner has signed off** the limitations section and the open decisions in §4.

## 2. Phases and steps

Status key: ☐ pending · ☑ done · ⛔ blocked · ◇ optional (needs an owner go). Each step ends with a **chain entry** and, for phases, a **checkpoint (CP)**.

### Phase A — unblock and close E36 *(immediate, [AGENT])*
| ID | Step | Depends | Test / evidence | Status |
|---|---|---|---|---|
| A1 | Retry the shell until the permission check recovers; no workaround around git | — | `git status` runs | ☑ (recovered) |
| A2 | Write `configs/e36.criteria.sha256` from the `criteria` block; append the registration chain entry | A1 | `run_e36.py` stops refusing; entry in chain | ☑ |
| A3 | Commit and push the E36 setup | A2 | pushed commit | ☑ |
| A4 | Run `python experiments/run_e36.py` (3 seeds × coupled / control, about 10 min CPU) | A3 | `results/e36/*.json` | ☑ |
| A5 | Write outcome into `docs/EVIDENCE.md`, a STATUS row, a chain entry; commit, push | A4 | rule in the E36 registration | ☑ |
| **CP-A** | E36 has a recorded outcome; tree clean; chain valid | A5 | `explog.verify()` true | ☑ |

### Phase B — read the refuted handshake items honestly *(decision first, then [AGENT])*
The handshake left three open results: naming 0.79 against 0.99, seed disagreement 0.77 against 0.9, one seed whose core had 4 dimensions. Nothing is retuned; each follow-up is a new registered prediction.
| ID | Step | Depends | Test / evidence | Status |
|---|---|---|---|---|
| B1 | **[OWNER → decided by Claude under delegation: probe registered]** Choose: accept the refutations as the result, or register one scaling probe (more releases and encoder steps: does naming approach 0.99?) | CP-A | owner reply, recorded as a decision | ☑ |
| B2 | ◇ If probe chosen: write prediction and frozen config first (releases 150 → 450, steps 4000 → 8000; naming per seed); then build the larger datasets | B1 | prediction in `EVIDENCE.md` before any run | ☑ |
| B3 | ◇ Run the probe (about 40 min CPU), outcome entry, report | B2 | `results/scaling/*.json` | ☑ |
| B4 | ◇ (skipped by decision: minimal; stays a stated limitation) Nuisance limitation: one arm with multiplicative gain or shift nuisance (currently untested) | B1 | prediction first; one arm, 3 seeds | skipped |
| **CP-B** | Each refuted item has either an accepted-as-result note or a probe outcome | B1–B4 | `EVIDENCE.md` | ☑ |

### Phase C — the live capture *(owner-gated; the step that decides E44–E47)*
| ID | Step | Depends | Test / evidence | Status |
|---|---|---|---|---|
| C1 | **[OWNER]** Record per LIVE_DATA_PLAN §1: ≥ 30 releases, ≥ 60 fps, ≥ 20 s each, fixed tripod, static background, two bob markers, a ruler frame, varied release angles; note masses and rod lengths | — | the files | ⛔ |
| C2 | **[OWNER]** Upload the videos to the session (or push them to the repo under `data/live/`) as one file per release | C1 | files present | ⛔ |
| C3 | **[AGENT]** Two-marker tracker (colour thresholds per marker), pixel→metre scale from the ruler frame, energy from marker positions and velocities (smoothed differences, smoothing frozen first); unit tests on a synthetic two-marker render | C2 | `tests/test_live_tracker.py` | ☐ |
| C4 | **[AGENT]** Freeze `configs/live.yaml`: release-level split (train / val / test by release), E44 report-only (D13), E45–E47 thresholds copied unchanged from LIVE_DATA_PLAN §5, ε from measured per-step energy drift (D17-3); register before the run | C3 | criteria sha256 + `EVIDENCE.md` entry | ☐ |
| C5 | **[AGENT]** Run `experiments/run_real.py` on the footage (3 encoder seeds) | C4 | `results/live/*.json` | ☐ |
| C6 | **[AGENT]** Report in REPORTING format, outcomes for E44–E47, chain entries, commit | C5 | `results/live/REPORT.md` | ☐ |
| **CP-C** | E44–E47 have outcomes on the owner's footage; friction, tracker noise and release count stated | C6 | report + chain | ☐ |
Expected shape of the result (not a prediction): with friction, V holds only approximately and ε comes from measured drift; with ≥ 30 releases the between-release statistic is meaningful, which the 10 public clips could not give.

### Phase D — optional registered extensions *(each needs an owner go; none starts on its own)*
| ID | Step | Cost | Registration needed | Status |
|---|---|---|---|---|
| D1 (not run, reason in EVIDENCE) | E31f: define a frozen recurrence statistic for psi, run on existing handshake latents | minutes CPU | statistic + prediction | ◇ |
| D2 | E37/E38: stability boundary and consistency of the bridges; needs unstable or non-stationary dynamics the current pipeline cannot represent, so a design decision first | design + hours | new world + predictions | ◇ |
| D3 | E43 universality: render a spring and an orbit and look for the same conserved coordinate | about 20 min CPU + renderers | per-system prediction | ◇ |
| D4 | Pooling probe (augmentation + temporal pairs in one moment matrix; D17-4) | about 15 min CPU | prediction | ◇ |
| D5 | Paper-scale encoder (ResNet-50, 128×128, as in SplitJEPA robotics) on RunPod | GPU hours (trigger T2: ASK first) | ask batch | ◇ |
| **CP-D** | Every extension is either run with an outcome or listed as "not run, reason" in `EVIDENCE.md` | — | `EVIDENCE.md` | ☑ |

### Phase E — assemble the paper results *([AGENT], after CP-A and CP-C; CP-B/CP-D as chosen)*
| ID | Step | Test / evidence | Status |
|---|---|---|---|
| E1 | Registry table: every stage-V E-number with outcome, report path and chain index (extend `docs/STATUS.md`) | no E-number without an outcome line | ☑ |
| E2 | Figures: FIG 1 (psi over a chaotic release beside tracked energy), FIG 2 (psi against energy scatter with the verdict table), FIG 3 (reach curves), P-series panels where REPORTING requires them; generated from the raw JSONs by one script | `experiments/build_figures.py`; FIG 2 reproduces the handshake seed-0 naming (0.8487 vs 0.848), `tests/test_figures.py` | ☑ |
| E3 | Cross-track table (SYNTHESIS E34): each certificate (S, D, C, T) maps to a measured artifact; list the ones that have none | `docs/CROSS_TRACK.md` (orphans declared: full five-gate audit, NIM) | ☑ |
| E4 | Results text keyed to the SYNTHESIS paper skeleton (Sec 2–5): what is guaranteed, what is measured, what is open | `docs/PAPER_RESULTS.md`, numbers checked by `tests/test_paper_numbers.py` | ☑ |
| E5 | Limitations, stated plainly: additive-illumination nuisance only; E redundantly identified by two selectors; encoder-dependent naming; friction; thin real data until C is done | section in E4 | ☑ |
| **CP-E** | Every table and figure traces to a raw JSON and a chain entry | script + spot check | ☑ |

### Phase F — close-out *([AGENT] then [OWNER])*
| ID | Step | Test / evidence | Status |
|---|---|---|---|
| F1 | Full test suite, criteria-hash checks for every config (`handshake`, `hier`, `followup`, `e36`, `live`), sealed-audit scan | `pytest -q` green | ☑ |
| F2 | `explog.verify()` with artifacts; for any doc appended after logging, declare the stale reference superseded (owner-approved mechanism) | verify true | ☑ |
| F3 | Rebuild the log page (`python experiments/build_log_page.py`); update `explog/stages.json` (republishing the hosted page is left to the owner) | page current | ☑ |
| F4 | **[OWNER]** Sign off limitations and open decisions (§4) | written reply, chain entry | ☐ |
| **CP-F / FINISH** | All five finish-line conditions in §1 hold | §1 checklist | ☐ |

## 3. Registry of stage-V predictions (keep current; one line per outcome)

| ID | Prediction | Outcome | Where |
|---|---|---|---|
| E31c′ | certificate: V ≤ 0.05, ICC ≥ 0.9, L ≤ 1.02, rollout ≤ 0.35 | confirmed (3 seeds) | handshake report |
| E31d | naming ≥ 0.99 | refuted (0.786; with 3x data and 2x steps 0.970-0.978, still below) | handshake report, B1 outcome |
| B1 | naming +0.05 with 450 releases / 8000 steps | confirmed (gain +0.12/+0.29/+0.15) | `results/scaling`, EVIDENCE |
| E31e | S1 at lag 32; reach shorter for the fast block | S1 refuted (2 of 3 seeds); reach confirmed | handshake report |
| E31f | recurrence structure | not run (no frozen statistic) | D1 |
| P-stab | seed agreement ≥ 0.9 | refuted (0.766) | handshake report |
| P-ctrl | flat / shuffled arms < 0.9 | met (shuffled 0.790 close to main) | handshake report |
| E35 | RUNGS = 4 | refuted (RUNGS 1; arithmetic expectation recorded) | hier report |
| F1 | main beats release-free arm by ≥ 0.1 | refuted (gap 0.000 / 0.000 / −0.010) | followup |
| E36 | (S) passes and (D) fails in the coupled world; control closes | refuted as worded: (S) 6/6, control 1.000, coupled closure 1.25-1.32 against ≥ 2.0 | `results/e36`, EVIDENCE |
| E37, E38 | stability boundary, consistency | not run (reason in `EVIDENCE.md`) | D2 |
| E43 | same pattern in other systems | not run | D3 |
| E44 | ceiling probe | report-only (D13); public clips: poor | Phase C |
| E45–E47 | live-data predictions | blocked on footage | Phase C |

## 4. Decision queue

| # | Decision | Needed by | Recommendation |
|---|---|---|---|
| Q1 | Accept the handshake refutations as the result, or register the scaling probe (B1) | Phase B | register one probe: it is the only way to learn whether 0.79 is a data/training limit |
| Q2 | Upload the footage (C1–C2) and the masses and rod lengths | Phase C | this is the critical path to the finish line |
| Q3 | Which optional extensions (D1–D5) are in scope for this paper | Phase D | D1 only; D2 and D3 are separate studies |
| Q4 | GPU run on RunPod for a paper-scale encoder (D5) | Phase D | not needed for the finish line |

## 5. How to update this document

For each finished step: (1) change its status here and add the evidence path, (2) append one chain entry with `stage "V"`, `step "<ID>"`, (3) update §3 if a prediction got an outcome, (4) commit and push. Never edit an earlier outcome line; add a dated line below it. If a step needs a new prediction, write it in `docs/EVIDENCE.md` before any run.

## 6. Closing state (2026-10-20)

| Finish-line condition (§1) | State |
|---|---|
| 1. Every registered prediction has an outcome | **met**: confirmed / refuted / "not run with reason" in `docs/EVIDENCE.md`; E44–E47 recorded as blocked |
| 2. Live-capture handshake on the owner's footage | **open**: needs the recording (Phase C, steps C1–C2); C3–C6 are ready to run the moment the files arrive |
| 3. Paper-ready results set | **met**: `docs/PAPER_RESULTS.md`, `docs/CROSS_TRACK.md`, `results/figures/` |
| 4. Integrity checks | **met**: `python experiments/audit_stage_v.py` passes |
| 5. Owner sign-off of limitations and open decisions | **open**: the limitations are in `docs/PAPER_RESULTS.md` Sec 5 and the decision queue in §4 |

The experiment is complete except for the two owner-gated items (2 and 5). Phase C step C3 (two-marker tracker and energy calculation) is written when footage with known marker colours exists.

## 7. Public-data note (2026-10-20)
Downloaded on request into `data/public/` (not committed): **Columbia** rigid double pendulum (1100 clips × 60 frames, 128×128 RGB, 135 MB) and **Mendeley** angle/encoder time series (no video). Columbia could stand in for Phase C's release diversity (1100 releases) but its clips are short (60 frames), energy is not given, and its `phys_vars.npy` is a pickled object array that must be parsed safely before use. Nothing was run on it; Phase C's owner-footage step is unchanged.

**Update (2026-10-20):** Columbia was parsed safely (`src/isj/safe_npy.py`) and run (C1, C1b; `docs/EVIDENCE.md`, `docs/PAPER_RESULTS.md`): naming 0.88–0.90 against tracked energy, flat baseline 0.38–0.48, certificate partly met. This is real-data evidence from 1100 clips, but it does not replace the owner's footage for E44–E47 (clips are 60 frames, tracked energy is noisy, no controlled markers).

**Update (2026-10-21):** the Columbia full experiment (C2) ran to completion under the supervisor (`docs/COLUMBIA_FULL_PLAN.md`): not confirmed as registered; naming 0.91 and seed agreement 0.97 on 100 real videos with video-level splits. It is the strongest real-data evidence so far and replaces C1 as the main real result; the owner-footage test (E44-E47) remains the only open evidence step.

**Update (2026-10-21):** the gap study ran under the supervisor (`docs/GAPS_PLAN.md`): depth world (ladder 3 cuts vs single-lag 2) and two more real systems; G1 marked-bob footage still blocked (IBM `dax-cdn.cdn.appdomain.cloud` denied by the network policy; Mendeley has no video).

**Update (2026-10-21):** the other-data plan (`docs/OTHER_DATA_PLAN.md`) ran under the supervisor: HF controlled pendulum (all registered criteria met, carried by release grouping) and ManiSkill PickCube on the CPU (untestable with the 32×32 gray MLP encoder). Open follow-up if wanted: R1b with 64×64 RGB and a convolutional encoder.
