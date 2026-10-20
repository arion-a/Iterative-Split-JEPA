# Handoff: run E24 (robot data, Stage C) on the Vast GPU box

For a session that can SSH to the box. The cloud session that wrote this cannot (its network only allows HTTPS). Do only this; do not design or register anything new (see AGENTS.md scope rule).

## What E24 is
Test the algorithm on simulated robot data like the SplitJEPA paper (Appendix D): ManiSkill3 `PickCube-v1` and `PushCube-v1`, 128x128 base camera, 100 groups of 8 successful trajectories per task. Viewpoint pairs (base vs side camera) give rung 1; trajectory pairs aligned by normalized progress give rung 2 inside the rung-1 invariant block. Design: `docs/stage_c_design.md`. Pre-registered prediction: `docs/EVIDENCE.md`, entry E24. Do not edit it.

## Pre-registered criteria (per task; all four must hold for "confirmed")
- P1: rung-1 variant-block response >= 3x the invariant block under viewpoint pairs.
- P2: rung-2 variant-block response >= 1.5x the invariant core under trajectory pairs.
- P3: shuffled-pair control gives rung-1 gap ratio < 2; random coordinate split of the same block sizes gives both ratios < 1.5.
- P4: camera id decoded with accuracy >= 0.9 from the rung-1 variant block and <= 0.65 from the rung-1 invariant content.
A finding that no gap clears the threshold is itself a result. Report refuted outcomes as they are.

## Where the code is
Repo `arion-a/Iterative-Split-JEPA`, branch `claude/blissful-turing-7cdrv0` (private; use a fine-grained token with Contents read+write; never print or commit it). Files, all under `experiments/robot/`:
- `vast_worker.sh`: the whole pipeline (system libs, Python 3.10 env, data generation, feature extraction, Stage C for 3 split seeds x 2 tasks, report, push of small results). It resumes. Run it from `~/bootstrap` after `git pull`, in the box terminal, with `GITHUB_TOKEN` exported.
- `gen_robot_data.py`, `extract_features.py`, `run_stage_c.py`, `build_stage_c_report.py`: the steps it calls.

## Known problem, fixed on the branch
The first attempt on the box failed at `import torch` with `undefined symbol: ncclCommResume`: the box image's NCCL shadowed the one torch ships. `vast_worker.sh` now does `export LD_LIBRARY_PATH=` after activating the venv (commit `bf64f46`). Check the `[torch]` line in the log shows `cuda available: True` before the long steps run.

## Box facts (from the other session; may differ per instance)
RTX 5090 (Blackwell: needs CUDA 12.8+ wheels, the script installs cu128), 32 CPU cores, ~251 GB RAM, 16 GB disk, `/workspace` not persistent. Rendering falls back to CPU (lavapipe) if the NVIDIA Vulkan driver is not exposed; the CPU motion planner is the slow part either way. Rough estimate for the whole run: 45-90 minutes, untimed.

## Output
Small result files go to branch `claude/vast-results` (JSON, report, figure, logs). Big arrays stay on the box. The cloud session reads that branch and writes the E24 report. If you hit an error, fix it in the repo, commit to `claude/blissful-turing-7cdrv0`, and say what you changed.

## When finished
Stop the instance (billing runs while it is up), and remove any key you added to it.
