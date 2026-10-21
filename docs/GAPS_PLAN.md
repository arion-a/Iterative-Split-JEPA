# GAPS_PLAN.md — closing the three named gaps (2026-10-21)

Owner request: search the internet for how to find what would settle the claim, and close the gaps. Everything is in one place: this plan, `plans/close_gaps.yaml` (machine-readable, run by `experiments/supervisor.py`), `configs/gaps.yaml` (frozen criteria), `docs/EVIDENCE.md` ("G1-G3" registration, then "G outcome"), `results/depth/REPORT.md`, `results/system_*/`, `results/depth/`.
One command: `python experiments/supervisor.py plans/close_gaps.yaml` (resumes after a halt; `--status`).

## 1. The gaps and what the search found
| Gap | What would settle it | Found | Status |
|---|---|---|---|
| G1 energy vs amplitude | Real double-pendulum footage with marked bobs and tracked kinematics, so energy and amplitude can be decoupled | **IBM Double Pendulum Chaotic Dataset**: 21 real videos, ~40 s, 400 Hz, tracked markers, CDLA licence ([page](https://ibm.github.io/double-pendulum-chaotic-dataset/), [DAX](https://developer.ibm.com/exchanges/data/all/double-pendulum-chaotic/), [repo](https://github.com/IBM/double-pendulum-chaotic-dataset); original: Asseman et al. 2018). Hosted on `dax-cdn.cdn.appdomain.cloud`, **blocked by this environment's network policy** (502 through the proxy). **Mendeley** low-cost double pendulum ([data](https://data.mendeley.com/datasets/7yd2ntbh3w/1)): tracked angles and encoder data, **no video**. | **blocked**: needs the IBM host allowed (Network access → Allowed domains) or the owner's footage. Partial in-hand test: the elastic pendulum (spring energy decouples energy from angle amplitude) |
| G2 depth | A world whose adjacent timescale ratios are ≥ 10, with a single-lag arm to compare | Not a download: generated here (`hier.py`, AR blocks a = 0.1, 0.9, 0.99, 0.999) | run in this plan |
| G3 second system | Another physical system with ground-truth energy | **Columbia "Discovering state variables"** datasets on the authors' [project page](https://www.cs.columbia.edu/~bchen/neural-state-variables/) and [GitHub](https://github.com/BoyuanChen/neural-state-variables): single pendulum, elastic pendulum (1200 clips each, `phys_vars.npy` with total, kinetic, potential energy) — downloaded and used. Others seen: [Morpheus real-world](https://huggingface.co/datasets/physics-from-video/morpheus-real-world) (falling and bouncing ball, holonomic and double pendulum; no state table), DeepMind Hamiltonian-dynamics suite (rendered mass-spring and pendulum with phase-space truth), Zenodo flow-map data (simulation only) | run in this plan |

## 2. Phases and steps (tests and checkpoints)
| Step | Phase | What | Check |
|---|---|---|---|
| S0.1 | 0 | Registration intact: hash, prediction text, no G result yet | inline assertion |
| S0.2 | 0 | Depth-world arithmetic: cut gaps 9 / 10 / 10 at lag 1, clean at each rung's own lag, and at lag 1 the two slowest blocks fall below the S1 level (the mechanism behind D2) | `tests/test_gaps.py` |
| S1.1-S1.2 | 1 data | Decode both systems, load `phys_vars.npy` with the allowlist unpickler, recover the video grouping by the contrast test over the divisors of 1200 (no preset period) | asserts in `prep_system.py` |
| S1.3 | 1 | **Phase 1 gate**: grouping tests for both systems + audit | `tests/test_gaps.py -k grouping`, `audit_stage_v.py --no-tests` |
| S2.1 | 2 run | Depth world: ladder (lags 1, 4, 16) / single-lag / shuffled, 3 seeds | sanity test of the results |
| S2.2-S2.3 | 2 | Single and elastic pendulum: the C2 protocol, 3 seeds × 4 arms, correlations with every tracked quantity | sanity test per system |
| S3.1 | 3 | Mechanical verdicts S1-S4 per system and D1-D3, into EVIDENCE, STATUS, `results/depth/REPORT.md`, the chain | marker in EVIDENCE |
| S4.1 | 4 close | Full audit | `audit_stage_v.py` |
| S4.2 | 4 | Plan-alignment check: every step done, registration unchanged, outcome after registration, every result logged | `check_gaps_alignment.py` |

## 3. Predictions (text in EVIDENCE; thresholds frozen)
Per system, all seeds: grouping contrast ≥ 0.5; naming ≥ 0.5; main beats flat by ≥ 0.1; seed agreement ≥ 0.9. Depth: ladder finds exactly 3 cuts (R² ≥ 0.9, gap ratio ≥ 5); single-lag finds ≤ 2; shuffled finds 0. Confirmed only if all hold; reported as measured; nothing tuned.

## 4. Issue log
* **2026-10-21, S1.1 halted (supervisor worked as designed).** The single-pendulum clips are not in temporal order, so the video grouping cannot be recovered (adjacent-clip distance equals random-pair distance). Fix: a fallback fixed in `docs/EVIDENCE.md` before any run (release = clip, contiguous-block split, S1 reported not met, leakage risk stated); `prep_system.py` and the tests implement it, the criteria block and its hash are unchanged.

## 5. Tracker
`python experiments/supervisor.py plans/close_gaps.yaml --status`. Final state (plan complete, 2026-10-21):

| Step | Status | Attempts | Finished (UTC) |
|---|---|---|---|
| S0.1 | done | attempts 1 | 2026-10-21T09:03:25+00:00 |
| S0.2 | done | attempts 1 | 2026-10-21T09:03:25+00:00 |
| S1.1 | done | attempts 1 | 2026-10-21T09:16:02+00:00 |
| S1.2 | done | attempts 1 | 2026-10-21T09:17:13+00:00 |
| S1.3 | done | attempts 1 | 2026-10-21T09:17:14+00:00 |
| S2.1 | done | attempts 1 | 2026-10-21T09:18:43+00:00 |
| S2.2 | done | attempts 1 | 2026-10-21T09:31:49+00:00 |
| S2.3 | done | attempts 1 | 2026-10-21T09:43:20+00:00 |
| S3.1 | done | attempts 1 | 2026-10-21T09:43:20+00:00 |
| S4.1 | done | attempts 1 | 2026-10-21T09:43:43+00:00 |
| S4.2 | done | attempts 1 | 2026-10-21T09:43:43+00:00 |

**Result:** not confirmed as worded; see `docs/EVIDENCE.md` (G outcome and interpretation) and `results/depth/REPORT.md`.
