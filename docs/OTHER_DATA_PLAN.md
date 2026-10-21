# OTHER_DATA_PLAN.md — a second controlled pendulum dataset and the SplitJEPA robotics setting (2026-10-21)

Owner request: find another pendulum video dataset with a controlled environment and clear ground truth, and check whether the robot data used by the SplitJEPA paper can test our design. Everything is in one place: this plan, `plans/other_data.yaml` (run by `experiments/supervisor.py`), `configs/other_data.yaml` (frozen criteria), `docs/EVIDENCE.md` ("H1 and R1", later "H1/R1 outcome"), `results/robot/REPORT.md`, `results/hf_pendulum/`, `results/robot/`.
One command: `python experiments/supervisor.py plans/other_data.yaml` (resumes after a halt; `--status`).

## 1. What was found
| Item | Finding | Use |
|---|---|---|
| Controlled pendulum video with clear ground truth | **Hugging Face `jimchen2/pendulum-cjepa-dataset`** ([page](https://huggingface.co/datasets/jimchen2/pendulum-cjepa-dataset)): 200 rendered pendulum videos, 196×196, 12 fps, 72 frames; RK4 physics with random initial angle and damping; **lighting controlled independently** (own labels); exact per-frame angle, velocity, energy; whole-video train/val split (160/40). Simulated, in an independent renderer with shadows | **H1** |
| Other candidates | IBM Double Pendulum Chaotic Dataset (real, tracked markers; host blocked by the network policy); Mendeley double pendulum (tracking and encoder data, no video); Columbia single/elastic/double pendulum (used before); DeepMind Hamiltonian-dynamics suite (rendered, phase-space truth, would need its generator) | not used here |
| SplitJEPA paper's robot data | ManiSkill3 **PickCube / PushCube**, simulated, 128×128 RGB, matched groups of eight trajectories, cross-view pairs (base and side cameras) and cross-trajectory pairs; invariant = cube and goal state, variant = robot configuration, camera, lighting ([paper](https://arxiv.org/abs/2610.12349), [project page](https://splitjepa.github.io/)). The linked repository is the project page only: no data generator, no dataset | **R1**: regenerated here with ManiSkill itself |
| Can ManiSkill run here? | **Yes**, on the CPU: `mani_skill` 3.0.1 + `sapien` 3.0.3 in an isolated Python environment (the main environment needs numpy 2, ManiSkill needs numpy < 2), software Vulkan via Mesa lavapipe (`apt install mesa-vulkan-drivers`), `sim_backend="cpu"`; about 17 steps per second with two renders | R1 |
| Real robot datasets | Open X-Embodiment, DROID (1.7 TB; 2 GB sample of 100 trajectories), BridgeData V2, LeRobot datasets on the Hugging Face hub (`LeRobotDataset("lerobot/pusht")`); none has a conserved quantity, they would test only the invariant/variant split (scene or task constant per episode versus arm motion and viewpoint) | not run; needs a registered prediction and a frame-rate-aware lag schedule |

## 2. Why R1 is a real test of the design, not a rerun
The SplitJEPA setting has a *correspondence family that is a real nuisance*: two cameras on the same state. Our pipeline already uses such a family at its first rung. The theory predicts which quantities end up in the invariant core: those present in **every** member of the family. The cube is visible from both cameras; the goal sphere is visible only from the side camera. So the cube's initial position should be recoverable from the cross-view core, the goal should **not**, and the arm (variant, fast) should be read out better from the variant block than from the core.

## 3. Phases, steps, checks
| Step | Phase | What | Check |
|---|---|---|---|
| S0.1 | 0 | Registration intact; no result yet | inline assertion |
| S0.2 | 0 | ManiSkill usable on CPU: environment builds, both cameras render | inline assertion |
| S1.1 | 1 data | Decode the 200 HF videos and label CSVs | asserts in `prep_hfpend.py` |
| S1.2 | 1 | Generate 150 PickCube episodes × 60 steps × 2 cameras (seeds 0-149, smooth random actions) | in `gen_maniskill.py` |
| S1.3 | 1 | **Phase 1 gate**: data tests (energy decays, splits 140/20/40, goal and cube vary, arm moves, cameras differ) + audit | `tests/test_other_data.py`, `audit_stage_v.py --no-tests` |
| S2.1 | 2 run | H1: 3 seeds × arms main / flat / shuffled / temporal-only | sanity test |
| S2.2 | 2 | R1: 3 seeds; held-out ridge readouts of simulator state from core, variant block, flat top PCs, full latent | sanity test |
| S3.1 | 3 | Mechanical verdicts H-a..H-d, R-a..R-c into EVIDENCE, STATUS, report, chain | marker in EVIDENCE |
| S4.1-S4.2 | 4 close | Full audit; plan-alignment check | `audit_stage_v.py`, `check_other_alignment.py` |

## 4. Predictions
Text in EVIDENCE ("H1 and R1"); thresholds frozen in `configs/other_data.yaml`: H-a naming ≥ 0.5, H-b main − flat ≥ 0.1, H-c |Spearman| with the controlled light < 0.3, H-d agreement ≥ 0.9; R-a core readout of the cube's initial position R² ≥ 0.5, R-b flat lower by ≥ 0.1, R-c tcp better from the variant block by ≥ 0.2. Goal (side view only) is informational: expected absent from the cross-view core.

## 5. Issue log
_(halts and fixes are recorded here and in the chain)_

## 6. Tracker
`python experiments/supervisor.py plans/other_data.yaml --status` (final state copied here when the plan completes).
