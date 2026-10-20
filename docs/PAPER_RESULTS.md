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
| E44-E47 | blocked on the owner's footage |

## Sec 5 (boundaries) — what is guaranteed, measured, open
* **Measured:** certificate on a discovered coordinate; the data / training dependence of naming; the cut-gap bound in an AR world; redundancy of the two selectors.
* **Not shown:** that the temporal ladder adds anything over one slow-feature direction in this world (F1); that depth grows reach across levels (one level measured); the full five-gate rung audit; transport (NIM) in stage V.
* **Limitations:** nuisance is additive illumination only (gain and shift untested); naming stays below 0.99; simulated video; the closure gate is weakly sensitive for a 98%-pure core; the public real clips (10, one tracked link) are informational and their coordinate is probably per-clip appearance; the live-footage test (E44-E47) is not done.
