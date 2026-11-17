# Design proposal: a deeper, larger robot-sim test of the mechanism (rungs 8 to 10)

**Status: design only (2026-11-17, owner asked for a design). Nothing here is registered or run. A go-ahead and the open decisions at the end are needed before any registration.**

## Why the E62 build cannot test depth 8 to 10
- It has 9 factors (8 rungs + the core), and 3 of them (gripper, arm pose, cube yaw) were not kept by the small autoencoder, so rungs 1 to 3 have no sharp cut.
- The three failing factors are also the smallest in pixel effect and the first in the order: the order and the effect size are confounded.
- One autoencoder, one data draw, one seed; alignment is judged by a readout only.
- The real recorded robot data has only four layers (layout, trajectory, progress, camera), so depth cannot be raised there: new controlled factors have to be rendered.

## Build
1. **Ten nested factors, all set through the simulator** (candidates, to be checked for controllability: gripper opening, arm pose, cube yaw, cube position, cube size, cube colour, floor/table colour, light tint, light brightness, camera distance/elevation, field of view, camera azimuth). Pick 10 whose effect on the image clears a floor; widen the ranges of the small ones.
2. **Retention gate before any ladder:** each factor must be readable from the full latent at R-squared 0.7 or more; a factor below that is enlarged or dropped and the data re-encoded. This removes the E62 failure mode (unkept factors) from the depth question.
3. **Order control:** three random factor orderings per seed, so position in the ladder and effect size are separated.
4. **Encoder:** a larger label-free autoencoder (latent 128, 128 x 128 images, about 20,000 steps, GPU about 1 hour) beside a no-training control (pixel PCA to the same size), as the identity-type control the project already learned to need.
5. **Data:** 20,000 exact pairs per rung, 10 rungs (about 400,000 images; the E62 render speed was about 200 images/s on CPU, so about 35 to 60 minutes). Render in chunks, encode on the fly, keep only latents (raw images at this size would be about 20 GB).
6. **Seeds:** 5 data/encoder draws per ordering.
7. **Ablations carried over:** nested versus leaky pairs (E67), exact versus cluster-built pairs for the first two rungs, and the one-shot split baseline.
8. **Optional (flagged, riskier):** add *progress* as a controlled layer by rendering states from recorded PickCube trajectories, to test the layer the real data failed on.

## Proposed (unregistered) pass criteria, for discussion
At least 8 of 10 rungs aligned (E62 definition plus an MLP readout) with gap at least 2, on at least 4 of 5 seeds, under at least 2 of 3 orderings; the no-training control fails at least as many rungs as E62's did; leakage no larger than in the nested control.

## Cost and risk
CPU rendering about 1 hour, encoder training about $0.25 of GPU, ladder runs minutes. Risks: some factors may not be controllable in ManiSkill; the autoencoder may still drop small factors (the gate catches this but could shrink the usable depth); oracle pairs remain, so this tests the mechanism, not pair-building.

## Open decisions for the owner
(i) the factor list; (ii) whether to include progress; (iii) go-ahead and GPU budget.
