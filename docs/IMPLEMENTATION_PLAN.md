# IMPLEMENTATION_PLAN.md — video-first handshake programme (stage V)

Written 2026-10-20. Sources (copied verbatim to `docs/source/`): COMPENDIUM, SYNTHESIS, MATHEMATICAL_PLAN, LIVE_DATA_PLAN,
VIDEO_FIRST_RESEARCH_PLAN. Binding order of authority: `docs/DECISIONS.md` > `docs/EVIDENCE.md` > this plan > the source documents.
Scope rule (AGENTS.md): only what is listed here is run. Everything else is "not run" with a reason.

## 0. What is built, in one paragraph

A rendered double-pendulum video world (generator side, physics allowed) → a physics-free pipeline (frame descriptor → predictive encoder →
whitening → **rung 1: nuisance split** from same-frame different-render pairs → **rung 2/3: temporal split** from lag pairs, inside rung 1's
invariant content, hard nesting D9) → an unnamed coordinate ψ chosen by between-release variance share (ICC) → certificate (V, ICC, L, rollout
error) → naming against the sealed simulator table (Spearman). Then a minimal hierarchical AR-world run of the same ladder, and the same
pipeline pointed at real video. The existing spectral engine (`src/isj/engine.py`, `audits.py`) is reused unchanged.

## 1. Rulings and decisions this plan rests on

Owner rulings (2026-10-20, in chat): **D13** ceiling gate report-only; **D14** naming by Spearman / flexible-readout R², never Pearson;
**D15** a non-degeneracy statistic accompanies every V; **D16** L = Lipschitz constant of F̂, L ≤ 1 allowed for conserved modes.
Owner-directed answers (D17, adopted by the instruction to implement): sequential nuisance-then-temporal rungs, no pooling of correspondence families;
release diversity + ICC; friction handled by calibrating ε on measured drift; depth (not state counts) planted in AR worlds; geometric lag ladder.
Full text in `docs/DECISIONS.md` D13–D17.

**Confirmed by the owner 2026-10-20 and promoted: DECIDE 1-9 → D19-D27, 10 → D18, 11-15 → D28-D32 (docs/DECISIONS.md).**

DECIDE lines (Claude, per DECISION_POLICY Step 5; rule = R-number of Step 4; the 5-bit pattern lists T1..T5 with 1 = the trigger is CLEAR (did not fire), matching the field name `triggers-clear`, so 11111 = no trigger fired;
convention fixed by D33; the first version of this plan had the bits inverted and was corrected on 2026-10-20):

```
DECIDE 20261020-1 | RK4 sub-stepped integrator, not velocity Verlet | rule R5 | triggers-clear: 11111 | 2026-10-20
   (non-separable double-pendulum Hamiltonian: Verlet is not symplectic there; step-halving check kept)
DECIDE 20261020-2 | Encoder trained by prediction + regulariser only, no alignment loss | rule R2 | triggers-clear: 11111 | 2026-10-20
   (paper's synthetic recipe; alignment in the encoder would remove the nuisance rung 1 must split)
DECIDE 20261020-3 | Encoder recipe = repo's validated hinge+cov (var 1e-2, cov 0.04), multi-horizon heads {1,8,32} | rule R3 | 11111 | 2026-10-20
DECIDE 20261020-4 | Block size per rung = largest gap ratio above the noise floor c(n), ratio >= gamma_min = 2.0 | rule R1 | 11111 | 2026-10-20
   (2x threshold is MATHEMATICAL_PLAN §2.1/E35; c(n) is STOP_CRITERIA S1)
DECIDE 20261020-5 | S1 operationalised: fires when no eigenvalue of the rung's difference moment exceeds c(n) | rule R5 | 11111 | 2026-10-20
   (source text says "lambda_min <= c(n)"; read as: the family exposes no variation on the remaining content)
DECIDE 20261020-6 | psi = max-ICC direction in the invariant core (generalised eigenproblem, release groups) | rule R5 | 11111 | 2026-10-20
DECIDE 20261020-7 | V uses delta = 0.1 std, eps = delta + 2 x q95 drift on validation (triangle rule); 200 cross-release pairs | rule R2/R1 | 11111 | 2026-10-20
   (200 pairs per q is the source convention; eps from validation noise is VIDEO_FIRST §8)
DECIDE 20261020-8 | L tolerance 1.02 for estimation error, rollout horizon K = 8 frames | rule R4 (tolerance is minimal) | 11111 | 2026-10-20
DECIDE 20261020-9 | Real data = public Morpheus double-pendulum videos (MIT), informational only, no gates | rule R5 | 11111 | 2026-10-20
DECIDE 20261020-11 | S1 amended: fires when lambda_max of the rung's moment <= 5% of an unmatched pair's energy (2 per whitened dim) | rule R5 | 01111 | 2026-10-20
   (found in the P2 planted-ladder unit test, before any registered run: the statistical floor c(n) is exceeded by white measurement noise in any
    invariant core at large n, so "variation above c(n)" never ends. Replaces the lambda-above-c(n) reading of DECIDE 5; c(n) is kept for block-size selection.)
DECIDE 20261020-12 | B^2 in c(n) = 99th percentile of squared pair differences, not the maximum | rule R5 | 01111 | 2026-10-20
   (the maximum is outlier-dominated; both are computed and the maximum is reported in the rung records)
DECIDE 20261020-13 | Block-size candidates need top eigenvalue > S1 level (5% of chance), not c(n) | rule R5 | 01111 | 2026-10-20
   (dev finding: for whitened d >= 32 the monograph floor B^2 sqrt(2 log(1/delta)/n) exceeds every eigenvalue; c(n) is still reported per rung)
DECIDE 20261020-14 | Encoder objective adds a consistency term (aug_weight 0.2) and latent 64-d; replaces DECIDE 2 | rule R1 | 01111 | 2026-10-20
   (LIVE_DATA_PLAN §2 specifies consistency across renderings; chosen on dev seed 100 by a physics-free diagnostic only: does the temporal family show a cut.
    No oracle quantity was looked at. Dev observations, not registered runs: 12-d and 32-d latents: no cut; 64-d with aug_weight 0 and nuisance 0.4: no cliff in the
    rendering-pair spectrum (S2); 64-d with 0.2: renderings agree (S1, nuisance absorbed), temporal family cuts 61|3.)
DECIDE 20261020-15 | Nuisance = additive 4-coefficient illumination pattern (amplitude 0.4); S1 on a family skips it, the ladder ends by S1 only when the last family is exhausted | rule R5/R1 | 01111 | 2026-10-20
   (the first renderer used gain/offset/shift: multiplicative and shift nuisance is not an additive latent block and gave no cliff; gain/shift arms are
    NOT tested and are a limitation. Skip-on-S1 is STOP_CRITERIA S1 read literally: terminate only if NONE of the families has variation.)
DECIDE 20261020-10 | S2 gap criterion for temporal worlds uses gamma_min 2.0, not the B1/B2 gate of 10 | rule R1 | 01111 | 2026-10-20
   (T1 fired: a gate is added to a new stage, so it is also escalated as A1; the B1/B2 gate stays untouched)
```

## 2. Registered predictions for this plan (frozen in `configs/handshake.yaml`, hash-checked; text in `docs/EVIDENCE.md`)

E31c′, E31d, E31e from MATHEMATICAL_PLAN (revised handshake), amended by D13–D16; pilot gate P-stab from VIDEO_FIRST §8; controls; E35 (hierarchical).
Not run, with reason: E31f (informational recurrence structure; no frozen statistic), E36–E38 (need a constructed bridge-failure world; the plain AR world is
stable by design), E43 (needs other physical systems), E44–E47 on the owner's own capture (blocked on capture; thresholds in LIVE_DATA_PLAN stand, E44 is report-only by D13).

## 3. Step-wise plans, checkpoints, tests

Every phase ends in a **checkpoint (CP)**: a list of tests that must pass before the next phase starts, then one chain entry (`explog`). A phase's run is
never repeated to improve a number; failed runs are kept.

### P0 — housekeeping (no compute)
| Step | Action | Evidence |
|---|---|---|
| 0.1 | Install torch (CPU), scipy, pytest, pillow, pypdf; record versions | log entry |
| 0.2 | Copy the five source documents to `docs/source/` | files + sha256 in log |
| 0.3 | Append D13–D17 to `docs/DECISIONS.md`; E-registrations to `docs/EVIDENCE.md`; row to `docs/STATUS.md` | git diff |
| 0.4 | Write `configs/handshake.yaml` + `.criteria.sha256` (and `hier.yaml`) | hash test |
| 0.5 | Read the SplitJEPA paper for encoder and data; record findings (§5) | log entry |
| **CP0** | `pytest tests/test_explog.py tests/test_handshake_config.py` pass; chain links verify; config hash matches | |

### P1 — simulator, renderer, sealed audit
| Step | Action | Test |
|---|---|---|
| 1.1 | `src/isj/pendulum.py`: double pendulum RK4 (optional damping γ), energy, frame renderer with nuisance (gain, offset, shift) | `test_pendulum.py::energy_conserved` (rel. drift ≤ 1e-6 over 10 s), `::step_halving` (≤ 1e-8), `::damped_decays` |
| 1.2 | `src/isj/video_data.py`: `save_dataset` writes `frames.npy` + `meta.json` (discovery) and `audit.npz` (sealed) in separate files; whole-release splits 100/25/25 | `::splits_disjoint`, `::audit_separate_file` |
| 1.3 | Seal check: discovery modules (`video_data` loader, `video_encoder`, `temporal_ladder`) contain no physics tokens | `test_sealed_audit.py` (token scan) |
| 1.4 | Renderer property: two nuisance draws of one state differ only through the nuisance; same nuisance + same state is deterministic | `::render_nuisance` |
| **CP1** | all P1 tests pass; one dataset built for seed 0 and its digests logged | |

### P2 — pilot (VIDEO_FIRST §10): encoder, one nuisance rung, one temporal rung, controls
| Step | Action | Test / gate |
|---|---|---|
| 2.1 | `video_encoder.py`: descriptor `[x_t; x_t − x_{t−1}]` → MLP → d = 12; predictive loss at horizons {1, 8, 32}, stop-gradient, hinge + cov regulariser | `test_video_encoder.py::no_collapse` (min latent std ≥ 0.5 on a tiny run) |
| 2.2 | `temporal_ladder.py`: whiten (ZCA, train), rung 1 aug pairs, rung 2 lag pairs (τ = 8) via `engine.fit_rung`, hard nesting, S1/S2 logic, ψ by ICC | `::ladder_recovers_planted` (synthetic latent with planted nuisance, fast, conserved coordinates: ψ ↔ conserved, Spearman ≥ 0.99), `::shuffled_pairs_flat` |
| 2.3 | Arms on 3 seeds: **split** (main), **flat** (no-split baseline: top principal component of the unwhitened latent), **shuffled** (rung-2 partners permuted) | gate **P-stab**: min pairwise abs. Spearman of ψ across seeds on test frames ≥ 0.9 |
| 2.4 | Control behaviour (evaluator side): Spearman(ψ, E) < 0.9 for flat and shuffled on all seeds | gate **P-ctrl** |
| **CP2** | unit tests pass; P-stab and P-ctrl reported. If P-stab fails, P3 numbers are reported but labelled "not licensed" (VIDEO_FIRST §10) | |

### P3 — handshake: certificate and naming
| Step | Action | Test / gate |
|---|---|---|
| 3.1 | `quotient_audit.py`: `violation_rate`, `icc`, `lipschitz`, `rollout_error`, `certificate` (V, ICC, L, e_norm) | `test_quotient_audit.py::conserved_passes` (V ≈ 0, ICC ≈ 1), `::constant_caught_by_icc`, `::fast_variable_fails` (V large), `::damped_eps_from_drift` (friction arm: V within drift-calibrated ε), `::lipschitz_identity_is_one` |
| 3.2 | Evaluator-side references via the sealed audit: q_energy, q_angle, q_const through the same checker | reported (expected: q_energy passes; q_angle fails V or ICC; q_const fails ICC) |
| 3.3 | Registered predictions on 3 seeds: **E31c′** V ≤ 0.05 ∧ ICC ≥ 0.9 ∧ L ≤ 1.02 ∧ e_norm(8) ≤ 0.35; **E31d** Spearman(ψ, E) ≥ 0.99; **E31e** S1 fires at rung 3 (τ = 32) and variant-block reach is shorter than ψ's | gate table per REPORTING §A |
| 3.4 | Report-only: ceiling probe (linear latent → E, R² on train releases) — never a gate, never a remedy trigger (D13) | informational table |
| **CP3** | `results/handshake/REPORT.md` written in REPORTING format; STATUS row; chain entries; verdict line | |

### P4 — hierarchical AR world (minimal)
| Step | Action | Test / gate |
|---|---|---|
| 4.1 | `hier.py`: 5 blocks × 4 dims, AR(1) a = (0.2, 0.5, 0.75, 0.9, 0.95), unit stationary variance, existing `CouplingMap` scrambler, mirror encoder (D4) | `test_hier.py::world_stats` (autocorrelation = a per block), `::oracle_gap_arithmetic` (cut gaps match 2(1−a^τ) ratios) |
| 4.2 | ARM-L (ladder, geometric lags 1, 2, 4, 8, stop by S1/S2), ARM-S (rung 1 only), ARM-C (shuffled pairs) on 3 seeds | **E35**: RUNGS = 4; controls: ARM-C RUNGS = 0 |
| 4.3 | Per-rung (D) and (C): E_k and e_k(K) as ratios to the oracle-block predictor (≤ 1.25), L_k = ‖F̂_k‖₂ ≤ 1.02; paper-standard variant / invariant R² ≥ 0.9 per rung on held-out trajectories (replaces the angle criterion; same quantity as REPORTING §B) | per-rung table |
| **CP4** | unit tests pass; E35 outcome and the measured gap table written; STATUS row; chain entries | |

### P5 — live / real data
| Step | Action | Test / gate |
|---|---|---|
| 5.1 | `real_video.py`: ffmpeg decode → fixed crop → 32×32 gray (discovery) and orange-arm colour tracker (evaluator only); augmentation pairs (gain, offset, shift) as the nuisance correspondence | `test_real_video.py::tracker_on_synthetic_rgb`, `::decode_roundtrip`, `::augment_pairs_differ_only_in_nuisance` |
| 5.2 | Download the public Morpheus real double-pendulum videos (MIT licence, 10 clips, 30 fps) and run the same ladder + certificate (ε from measured drift, D17-3) | informational table: ICC, V, L, ceiling probe R² (report-only), Spearman(ψ, partial-energy proxy) |
| 5.3 | Owner's own capture (LIVE_DATA_PLAN §1 tier 1): **blocked**, needs the physical recording; `experiments/run_real.py --data <dir>` accepts it unchanged | blocked entry in the log |
| **CP5** | unit tests pass; real-data report written with its caveats (10 releases, partial-energy proxy, friction, held out in time not in release); chain entries | |

## 4. Experiments, metrics and steps kept minimal

3 experiments: handshake (3 seeds × 3 arms), hierarchical (3 seeds × 3 arms), real video (1 run). Headline metrics only: V, ICC, L, rollout error,
Spearman, RUNGS, per-rung angle. No composite score. Anything else printed is labelled "informational".

## 5. What the SplitJEPA paper says about the encoder and data (arXiv:2610.12349, read 2026-10-20)

* Synthetic: MLP encoder, alignment + SIGReg objective, 10,000 updates, batch 256, lr 3e-3, SIGReg weight 1e-6; frozen afterwards; centred ZCA on 30,000
  representations; 30,000 matched pairs for the spectral head. This is what `src/isj/encoder.py` already follows (hinge recipe with cov weight as the amendment).
* Robotics: ManiSkill3 PickCube/PushCube — **simulated**, 128×128 RGB base-camera images, ImageNet-initialised ResNet-50, partitioned r = [r_H; r_L] (64+64 or 128+128),
  action-conditioned predictor with stop-gradient target, AdamW lr 3e-4, weight decay 1e-4, cosine decay, clip 10, 100–200 epochs; 800 trajectories in 100 matched
  groups; correspondences = same-state cross-view pairs and cross-trajectory pairs.
* The paper uses **no real data** (its conclusion names real-world scale as future work). So "training on a real dataset" here is beyond the paper: the real-data step uses
  a public real double-pendulum video set (§3 P5) and a small encoder, because the ResNet-50 route needs a GPU that this session does not have (no CUDA device; RunPod is
  connected but not used without an ask, trigger T2).

## 6. Questions escalated (DECISION_POLICY Step 3 format)

**A1**
Q: Should the gap criterion for temporal (AR-lag) worlds be 2.0 (MATHEMATICAL_PLAN's 2× threshold) rather than the B1/B2 gate of 10?
Options: (a) 2.0 for temporal worlds, B1/B2 gate untouched; (b) keep 10 everywhere; (c) a different value.
Recommend: (a) — at any lag the cut gap of this AR world cannot exceed the adjacent timescale ratio (2.05–2.73), measured table in P4.
Impact: (a) P4 can measure RUNGS; (b) P4 reports RUNGS = 0 by construction; (c) depends.
Reversible: yes, all options. Cost: none (a, b); (c) rerun ≈ minutes CPU.
On-silence: (a), already used (DECIDE 20261020-10).
**ANSWERED 2026-10-20 by the owner: (a); recorded as D18.**

**A2**
Q: The chain verify fails on artifacts only: entry 134 logged `src/isj/stage_b1.py`, which was edited afterwards. The hash links themselves verify. Declare it superseded (`known_stale`)?
Options: (a) append a decision entry declaring entry 134's artifact superseded; (b) leave as is and always verify with `check_artifacts=False`.
Recommend: (a). Impact: (a) full verify passes; (b) none. Reversible: (a) yes (append-only), (b) yes. Cost: none.
On-silence: (b); this plan does not alter earlier entries.
**ANSWERED 2026-10-20 by the owner: (a), declare entry 134 superseded (chain amendment entry, `known_stale`).**

## 7. Status at 2026-10-20 (checkpoints)

| Checkpoint | State | Evidence |
|---|---|---|
| CP0 | passed | chain, config hash, 13 tests |
| CP1 | passed | simulator, renderer, sealed audit, token scan |
| CP2/CP3 | run; mixed result | `results/handshake/REPORT.md`: E31c′ confirmed, E31d / E31e(S1) / P-stab refuted, controls met, shuffled arm = main arm |
| CP4 | run | `results/hier/REPORT.md`: E35 refuted (RUNGS 1), per-rung gates and control met |
| CP5 | run on public data; 5.3 blocked | `results/real/REPORT.md` (informational); owner capture needed |

Full test suite: 50 passed. Chain links verify (`explog.verify(check_artifacts=False)`); the artifact-digest failure on entry 134 predates this stage (A2).
Open for the owner: A1 (gap criterion for temporal worlds), A2 (declare entry 134 superseded), confirm DECIDE 1–15, the "triggers-clear" bit convention (settled, D33), and the owner's own capture.
Limitations: nuisance is additive illumination only (gain/shift untested); datasets differ per seed; real data is 10 clips with friction and a one-link tracker; the ResNet-50 / GPU route of the paper was not run.
