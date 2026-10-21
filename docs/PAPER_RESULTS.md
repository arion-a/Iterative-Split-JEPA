# PAPER_RESULTS.md — stage V results, keyed to the SYNTHESIS paper skeleton (2026-10-20)

Every number below has a raw JSON and a chain entry (`docs/STATUS.md`, `explog/chain.jsonl`). Predictions and outcomes: `docs/EVIDENCE.md`. Figures: `results/figures/`.

## The central claim and what the evidence supports
**Claim under test:** from pixels alone, with no physics variable in the framework, the pipeline can (1) find an unnamed coordinate, (2) certify it as a dynamically valid abstraction, and (3) earn the name "energy" afterwards by comparison with the sealed simulator table.

| Part | Result | Source |
|---|---|---|
| (1) discover | A coordinate psi with between-release variance share 0.97-0.99 is found on every seed; it is stable across seeds only with enough data (0.766 at 150 releases; 0.976-0.981 at 450 releases and 8000 steps) | handshake, B1 |
| (2) certify | Confirmed on every seed in both settings: V ≤ 0.005, L 0.99-1.00, 8-step rollout error 0.12-0.23; q_energy passes the same checker, q_angle and a constant fail (ICC) | E31c′ |
| (3) name | Refuted at the registered 0.99: |Spearman| 0.786 (150 releases) → 0.970 / 0.976 / 0.978 (450 releases); the gain is a data / training effect (B1 confirmed) | E31d, B1 |

Controls: the flat baseline (no split) stays at 0.03-0.26; shuffled temporal pairs end the ladder by S2 as required.

## Real clips (Columbia, 1100 releases, tracked energy as evaluator) — added 2026-10-20
A one-dimensional core is found from real pixels and tracks the tracked total energy at |Spearman| 0.893 / 0.895 / 0.880 on held-out clips (registered ≥ 0.5: met); the flat no-split baseline reaches 0.38-0.48 (C1b: confirmed). The certificate calibrated on simulation is only partly met on real clips (V and L pass; 8-step rollout 0.43-0.45 against 0.35; ICC 0.898 on one seed against 0.9), so C1 is refuted as worded. As in simulation, a release-free slow direction names energy exactly as well as the ladder. Caveats: noisy tracked energy, 60-frame clips, neighbouring clips may share a video (contiguous-block split).

## Real clips, full video-level experiment (Columbia C2, 100 videos, 2026-10-21) — supersedes the clip-level C1 as the main real result
No shared video between train (70), validation (10) and test (20). Naming |Spearman| with tracked energy 0.905 / 0.914 / 0.912; seed agreement 0.97; V ≤ 0.025, L 0.985, 8-step rollout 0.29-0.30 (all pass). Not met: between-video ICC 0.685 (≥ 0.9; the tracked energy itself has 0.553 because real energy decays within a video) and the flat control on one seed (0.731, 0.482, 0.472 against < 0.5). Temporal-only = main; shuffled-pair arm clearly below main (0.75-0.83), so on real video temporal structure matters beyond release grouping. C2 is NOT CONFIRMED as registered (4 predictions, 2 fully met).

**Confound check (C3, 2026-10-21).** The Columbia coordinate correlates 0.91 with total energy but only about 0.5 with kinetic and 0.55 with potential energy alone, so it is energy-like, not purely kinetic or positional. It correlates equally (0.91) with local swing amplitude, and energy and amplitude correlate 0.90 with each other, so "energy" cannot be separated from "amplitude" on this data (partial correlations about 0.5 both ways). The name "energy" is therefore supported as "energy-like slow coordinate", not as energy opposed to amplitude.

## Sec 2-3 (theory and mechanism) — what the experiments touch
* Prediction fixes content, correspondences fix the partition: confirmed in the AR world; with correct pairs the lag ladder recovers a clean cut (variant R² 0.96-0.98, invariant 0.98-0.99, gap ratio 19-33 in E36's world).
* The cut gap cannot exceed the adjacent timescale ratio; measured eigenvalues follow 2(1−a) (hierarchical run). With the 2× criterion (D18) only one of four cuts in the planted five-level world is taken (E35 refuted as worded).
* Nuisance enters through the rendering-pair family; with a consistency term the encoder absorbs it (S1), without it no clean cut appears (dev finding, additive-illumination nuisance only).

## Sec 4 (experiments) — outcomes in one table
| ID | Outcome |
|---|---|
| E31c′ certificate | confirmed |
| E31d naming ≥ 0.99 | refuted (0.786; 0.970-0.978 after scaling) |
| E31e | S1-at-lag-32 refuted as worded; reach (fast block shorter than psi) confirmed |
| P-stab | refuted at 150 releases; 0.976-0.981 at 450 (informational) |
| P-ctrl | met |
| E35 | refuted (RUNGS 1, registered 4) |
| F1 | refuted: a release-free slow-feature direction names energy as well as the ladder (the discovery is redundantly identified in this world) |
| E36 | refuted as worded: (S) 6/6, control closes (1.00), coupled closure ratio 1.25-1.32 against ≥ 2.0 (the world has the failure, ≈ 3.1; the learned core's 2% recovery error floors the ratio) |
| B1 | confirmed |
| E31f, E37, E38, E43 | not run, reasons in EVIDENCE |
| C1 (Columbia real clips) | refuted as worded: naming 0.88-0.90 met, certificate partly met |
| C1b (Columbia controls) | confirmed: flat 0.38-0.48 |
| C2 (Columbia full, video level) | not confirmed: (b) naming 0.91 and (d) agreement 0.97 met; (a) ICC 0.685 (target's own 0.553) and (c) flat 0.73 on seed 0 not met |
| C3 (Columbia confound check) | confirmed: total 0.91 > kinetic 0.51, potential 0.55; amplitude 0.91, not separable from energy |
| E44-E47 | blocked on the owner's footage |

## Sec 5 (boundaries) — what is guaranteed, measured, open
* **Measured:** certificate on a discovered coordinate; the data / training dependence of naming; the cut-gap bound in an AR world; redundancy of the two selectors.
* **Not shown:** that the temporal ladder adds anything over one slow-feature direction in this world (F1); that depth grows reach across levels (one level measured); the full five-gate rung audit; transport (NIM) in stage V.
* **Limitations:** nuisance is additive illumination only (gain and shift untested); naming stays below 0.99 in simulation (0.97-0.98 at best) and 0.88-0.90 on real clips; real evidence is the 1100 Columbia clips (short, noisy tracked energy, possible shared-video leakage); the closure gate is weakly sensitive for a 98%-pure core; the public real clips (10, one tracked link) are informational and their coordinate is probably per-clip appearance; the live-footage test (E44-E47) is not done.
