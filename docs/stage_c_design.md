# Stage C design: the algorithm on the paper's robot data (ManiSkill3 PickCube-v1 and PushCube-v1)

Written 2026-10-20 before any Stage C code or run. Prediction: E24 in `docs/EVIDENCE.md`.

## What the SplitJEPA paper used (arXiv 2610.12349, Appendix D, as read from the paper's HTML text)
* Simulator and tasks: ManiSkill3, **PickCube-v1** and **PushCube-v1**.
* Data: 800 successful trajectories per task, organised into 100 matched groups of eight; 20% of each group held out for validation. Frames: 128x128 RGB from the third-person base camera. Frame counts and the way trajectories were generated are not stated.
* Encoder: an **ImageNet-initialized ResNet-50** whose embedding is split r = [r_H; r_L] (d_H = d_L = 64 for PickCube, 128 for PushCube), trained with L_pred + lambda_inv L_inv + lambda_var L_var.
* Pairs: viewpoint pairs = the same state rendered from the base and the side camera; trajectory pairs = frames of matched trajectories aligned by normalized execution progress within a group (weaker, approximate correspondences).
* Block validation (their Fig. 14): the normalized response of r_L is 8.4x (PickCube) and 14.0x (PushCube) that of r_H under viewpoint pairs, and 2.1x and 3.1x under matched-trajectory pairs.

## What we do (a reproduction, not a copy; the differences are deliberate and listed)
* **Data:** the same two ManiSkill3 tasks, generated here with ManiSkill's own motion-planning solutions (CPU software rendering). Matched group = trajectories that share the initial layout (same cube and goal) and differ in execution: each trajectory perturbs the planner's waypoints (random lateral offset of the reach point and a random speed scale). Two cameras, the default 128x128 base camera and one added side camera. Frames are resampled to a fixed number of frames per trajectory on a uniform progress grid. Held-out validation: 20% of trajectories per group.
* **Encoder:** the frozen ImageNet-initialized ResNet-50 (global-average-pooled 2048-d features), reduced by PCA to 128 dimensions on training frames; no SplitJEPA training of the encoder. This is a frozen-encoder test of the spectral ladder and differs from the paper's fine-tuned encoder.
* **Ladder:** whitening (engine ZCA), rung 1 on viewpoint pairs (variant block = viewpoint), rung 2 inside the rung-1 invariant content on trajectory pairs (same camera, same group, same progress; variant block = execution), invariant core = layout and phase. Block sizes chosen by the engine's gap rule (gap ratio above 10), not fixed in advance; hard nesting; Tier 1 purification is not used (the correspondences are given).
* **Block validation (Fig. 14 analogue):** response of a block to a pair set = mean over pairs of the distance between the block's coordinates, divided by the block's overall standard deviation (root mean squared distance to its mean over all frames). Ratio = variant-block response / invariant-block response.
* **Controls:** shuffled pairs (random frames), and a random coordinate split of the same size as the recovered blocks.
* **Ground truth in the simulator, used for evaluation only:** camera id, group id, initial cube and goal position, progress.

## Stated limits
Simulated robot data, not a physical robot; a frozen encoder that the paper did not use; our own trajectory-variation scheme; fewer trajectories if compute demands it (stated in the report). The paper's downstream behaviour-cloning and closed-loop results are out of scope.
