# Code behind the report "Iterated splitting of a learned representation" (FULL report)

This folder holds only the code, configs, tests and stored results that produced the results in that report. It is a copy, so you can read and run it without the rest of the repository.

- **Source state.** `src/`, `configs/`, `tests/` and the experiment scripts are exactly as in git commit `e2f41d5` (2026-11-18), the last commit before the later nested-loss work (E68 to E73) was written. All results in the report were produced by this code. (`experiments/make_full_report.py` is the current file; it only draws figures from stored results.)
- **Checked before packaging.** `experiments/simple_depth.py` re-run from this folder reproduces `stored_results/simple_depth.json` (largest difference in any angle 1.7e-12, in any gap ratio 5e-14). The 12 included test files pass (`PYTHONPATH=src python -m pytest tests`).
- **Not included:** the nested-loss / speed-recovery experiments E68 to E73 (separate work; code in the main repository), Stage B2, the pod and GPU orchestration, trained checkpoints, and the large image data (robot frames, the re-rendered scenes).

## 1. Read these five files first (about 1,800 lines)

| Order | File | What it holds |
|---|---|---|
| 1 | `src/isj/worlds.py` | The data: `BlockWorld` (l.21: hidden numbers, one AR(1) chain per layer, `sample` l.58, `transition_pairs` l.61, **`correspondence_pairs` l.75: the matched pairs**), `CouplingMap` (l.106: the "bend", the tanh coupling layers), `NestedMixtureWorld` (l.350: cluster world of E58) |
| 2 | `src/isj/engine.py` | **The method.** `fit_whitener` l.26 (r = C^-1/2 (e - mu)), `difference_moment` l.42 (M = 1/N sum D D^T), `eig_desc` l.51 (eigendecomposition), `gap_ratio` l.63, `fit_rung` l.118 (one rung: the d long axes become the block V, the rest H; "hard nesting" = the eigendecomposition is done inside H), `fit_ladder` l.208 (the loop over rungs) |
| 3 | `src/isj/audits.py` | The scoring: `principal_angles_deg` l.18, `max_angle_deg` l.25 (angle between the found block and the true layer), `linear_r2` l.54, `mlp_r2` l.58, `leakage_matrix` l.114 |
| 4 | `src/isj/encoder.py` | The encoders: `mlp` l.15, `InverseCouplingEncoder` l.40 (the paper's mirror-style encoder), `InvertibleCouplingEncoder` l.65, `train_encoder` l.132 (prediction objective or the paper's alignment objective), `encode` l.226 |
| 5 | `src/isj/stage_b1.py` | `run_stage_b1` l.26: builds the world, trains the encoder, whitens, runs the ladder with generator pairs, scores every rung; `payoff` (l.132) is the E38 comparison with a single split |

Report equation to code:

| Report | Code |
|---|---|
| z <- rho z + sqrt(1 - rho^2) eps (hidden numbers) | `worlds.py` `BlockWorld.transition_pairs` l.61 |
| R <- R + tanh(L W1); L <- L + tanh(R W2); ... (the bend) | `worlds.py` `CouplingMap.__call__` l.131; strength = scale of the W matrices |
| r = C^-1/2 (e - mu) (whitening) | `engine.py` `fit_whitener` l.26 |
| Pair, D = r(u) - r(v) | `worlds.py` `correspondence_pairs` l.75; `stage_b1.py` `pairs_fn` (l.52 to 60) |
| M = 1/N sum D D^T; M = sum lambda_j v_j v_j^T; gap = lambda_d / lambda_d+1 | `engine.py` l.42, l.51, l.63 |
| Block V = d top eigenvectors, H = the rest; repeat inside H | `engine.py` `fit_rung` l.118, `fit_ladder` l.208 |
| Angle to the true layer; gap | `audits.py` l.18 to 28; `stage_b1.py` per-rung dict (`angle_deg`, `gap_ratio`) |

## 2. Report section to code and stored results

| Report section | Experiment | Code to read | Config | Stored result |
|---|---|---|---|---|
| 3.1 one split reproduces the paper | Stage A | `experiments/run_stage_a.py`, `src/isj/stage_a.py` | `configs/stage_a.yaml` | numbers are typed into `experiments/make_full_report.py` (l.36); not re-derived here |
| 3.2 six rungs (7 layers) | - | `experiments/simple_depth.py` (the whole experiment in 17 lines; untrained encoder, exact pairs, mild bend) | in the script | `stored_results/simple_depth.json` |
| 3.3 8 and 10 rungs | E61 | `experiments/deep_ladder.py` | in the script (speeds 1 - logspace(0.8, 0.04, L)) | `stored_results/deep_ladder.json` |
| 3.4 how far the bend can go | E54 (strength 0.5), E55 (1, 2, 4, 8), E56 (strength 2 re-run), E57 | `experiments/run_stage_b1.py` (`--config`, `--out`, `--seeds`), `experiments/supervise_b1.sh`, chains `inv_paper_chain.sh`, `sweep_chain.sh`; scoring `analyse_inv_paper.py`, `analyse_sweep.py` | `configs/inv_paper_d4.yaml` (0.5), `configs/sweep/t_s*.yaml` (trained), `configs/sweep/u_s*.yaml` (untrained, learning rate 0); criteria `configs/*.criteria.yaml` (hash-frozen); E57's exact configuration is in `docs/EVIDENCE.md` of the main repository | `stored_results/minimal/e54` to `e57`, `INV_PAPER_REPORT.md`, `SWEEP_REPORT.md` |
| 3.5 the pairs define the layers | E38 | `experiments/run_stage_b1.py` with `payoff` on (single split computed in `stage_b1.py` l.132 to 140); `analyse_minimal.py` | `configs/minimal_c2.yaml` (all speeds 0.5) | `stored_results/minimal/e38` |
| 3.6 pairs built from the data | E58 | `experiments/run_nested_pairs.py` (arms: generator, label, kmeans_all, kmeans_slow, random); `src/isj/cluster.py` (`kmeans` l.8, `pairs_within_clusters` l.39, `purity` l.31); `worlds.py` `NestedMixtureWorld` l.350; `analyse_nested.py` | `configs/nested/pairs.yaml` | `stored_results/minimal/e58`, `NESTED_REPORT.md` |
| 3.7 simulated robot images | E59, E60, paper baseline, Stage R | Data: `experiments/robot_stage_r/gen_robot_data.py` (ManiSkill trajectories, two cameras), `extract_features.py` (frozen ResNet-50 features), `run_stage_c.py` (the ladder on frozen features), `analyse_stage_r.py`, `analyse_fixed.py`. Paper method: `experiments/robot_paper_baseline/train_paper.py` (runs the paper's own code), `embed_and_ladder.py` (the paper's split, then our ladder on the same embedding), `e59_analyses.py` (eigen-split of camera-pair differences), `e60_ladder3.py` (rungs 1 to 3), `verify_ratio.py` and `make_paper_format.py` (the paper's own scoring) | in the scripts | `stored_results/paper_baseline/` |
| 3.8 nameable factors | E62 | `experiments/factors/gen_factors.py` (re-renders PickCube with nested factors), `train_ae.py` (the small autoencoder), `e62_ladder.py` (the ladder and the reading matrix), `e62_figure.py` | in the scripts | `stored_results/e62/e62.json`, `e62_ladder.png` |
| Figures of the report | - | `experiments/make_full_report.py` (shows exactly which stored file feeds each figure) | | |

Several sections (3.4, 3.5, 3.6) read the result of one experiment from several stored folders; `make_full_report.py` lines 38 to 70 and 96 to 125 list which.

## 3. How to run

```
cd code_for_full_report
PYTHONPATH=src python -m pytest tests                    # 12 files, under a minute
mkdir -p results && PYTHONPATH=src python experiments/simple_depth.py     # 6 rungs, about a minute on CPU; compare with stored_results/simple_depth.json
PYTHONPATH=src python experiments/deep_ladder.py         # 8 and 10 rungs
PYTHONPATH=src python experiments/run_stage_b1.py --config configs/stage_b1.yaml --out runs/b1 --seeds 0   # one Stage B1 run
```
The robot and scene-factor scripts need the ManiSkill environment and a GPU; their usage lines are in each file's header.

## 4. Things to know while investigating

- `stage_b1.py` is the largest file (236 lines); `run_stage_b1` is long but linear: world, encoder, whitener, ladder (`fit_ladder`), evaluation on fresh latents (ground truth is used only there).
- Settings that decide the outcome and are easy to miss: **hard nesting** (`nesting_enforcement`), the **rung gate** (`rung_gate: true` in most configs; `configs/sweep/t_s2_nogate.yaml` is the variant with it off, and the report says the safeguard was switched off at the stronger bends, see E56 in `docs/EVIDENCE.md` of the main repository), the **block sizes** (given as `d_ks` in the Stage B1 configs; Stage A, `stage_a.py` l.57, chooses them with the gap rule `engine.select_block_count`), and the `corr_*` options in `encoder.py` (later E40 to E45 loss terms; absent from the configs included here).
- Two excluded test files: `test_b2_spec_parts.py` (Stage B2) and `test_depth_checks.py` (needs stored run folders that are not copied).
- The stored results are JSON per run; the report's tables are medians and ranges over them.
