# Stage A record (plan §4.1)

Criteria frozen in `configs/stage_a.yaml` (sha256 in `configs/stage_a.criteria.sha256`):
invariant R² > 0.9, angle < 5°, gap ratio > 10, leakage at the permutation null
(Holm, α = 0.01; effect-size floor R² < 0.01 — **pending confirmation, not in the plan**).
Recorded runs: `runs/stage_a/r1` (code at commit 8fe29a5), `runs/stage_a/coupling{1.0,2.0}`.

## Debug rounds (stop rule: halt after three)

| Round | Finding | Change |
| --- | --- | --- |
| 0 (first run, seed 0) | RED: invariant R² 0.43, gap 1.2. Hinge variance alone permits rank collapse | — |
| 1 | stop-grad + covariance 0.04 → R² 0.989, angle 1.2°, gap 87. Without stop-grad: collapse (pred loss 0.002) | `cov_weight` 0 → 0.04, `stop_grad: true` (recipe only; criteria hash unchanged) |

## Main arm, coupling 0.5, 5 seeds — PASS on every criterion, every seed

| seed | inv R² | var R² | angle inv/var (°) | gap ratio | leakage R² | strict null |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0.989 | 0.990 | 1.25 / 0.39 | 86.7 | 0.0000 | yes |
| 1 | 0.986 | 0.988 | 0.99 / 0.34 | 58.7 | -0.0003 | yes |
| 2 | 0.990 | 0.992 | 0.87 / 0.30 | 114.7 | -0.0011 | yes |
| 3 | 0.993 | 0.992 | 0.87 / 0.24 | 137.9 | -0.0003 | yes |
| 4 | 0.986 | 0.984 | 1.00 / 0.47 | 72.4 | -0.0005 | yes |

The leakage rule needed no floor here: no off-diagonal test was significant on any seed.
The gap rule selected d = 4 on every seed.

## Controls (all behave as required)

* shuffled pairs: gap ratio 1.00–1.02, angle 73–88°, selected d = 0.
  *Post-hoc amendment:* my first control bound (invariant R² < 0.5) ignored chance level (a random
  4-of-8 projection already explains ~0.5); replaced by angle > 45° after seeing run r1. Pass
  criteria were not touched. The plan's own expectation (flat gap) held on all seeds.
* no prediction: invariant R² 0.22–0.46, gap 1.0–1.2.
* no correspondence step (identity rotation): invariant R² 0.39–0.61, angle 69–88°.
* no variance/ZCA: invariant R² 0.01–0.14, gaps 1.2–14 (spectrum not interpretable without whitening).

## Coupling sweep (main arm, 3 seeds each)

| coupling | inv R² | angle (°) | gap ratio | verdict |
| --- | --- | --- | --- | --- |
| 0.5 | 0.986–0.993 | 0.9–1.3 | 59–138 | pass |
| 1.0 | 0.959, 0.788, 0.961 | 1.6, 2.1, 0.9 | 20.2, 1.4, 21.5 | seed 1 fails (R² < 0.9, gap < 10, leakage significant) |
| 2.0 | 0.718, 0.503, 0.580 | 6.5, 4.9, 10.4 | ~1.3 | fail |

Recovery degrades monotonically with coupling, as the authors report (global R² 0.998 → 0.877).
The plan's pass criteria apply at coupling 0.5; the sweep is the recovery-vs-coupling curve.

## Not yet done

* **Comparison with the authors' simulation** (plan §6: Stage A's first decisive comparison).
  Their `simulation/run.py` is cloned in the scratchpad but has not been run (execution of
  external code was blocked pending user approval). Until it runs, differences in encoder
  recipe (generic MLP, 16-d observations, hinge+covariance vs their exact-inverse coupling
  encoder, 8-d observations, SIGReg) cannot be attributed.
* `obs_dim = 8` ablation of our own pipeline (cheap; `--set world.obs_dim=8`).
