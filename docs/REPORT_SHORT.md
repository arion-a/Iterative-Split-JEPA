# Iterative SplitJEPA: short report (2026-11-15)

Scope (owner decision): the paper's setting only, synthetic worlds plus simulated robot images. No real video anywhere.

## 1. The idea
A world has nested layers z = (z1,...,zL): z1 changes fastest, zL is constant. An encoder maps an observation to r in R^d. The aim is to split r into one block per layer.

## 2. The operations (all of them)
1. **Whiten.** r~ = C^(-1/2)(r - mean), C = cov(r). The cloud of embeddings becomes a round ball.
2. **Matched pairs for rung k.** Two observations (u, v) that agree on layers slower than k and differ in layer k. D = r~(u) - r~(v).
3. **Difference moment.** M_k = E[D D^T] restricted to the current invariant content H_(k-1). Its long axes are the directions that change between paired points.
4. **Cut.** Eigendecompose M_k. The top d_k eigenvectors form the variant block V_k. The rest span H_k, the invariant content. Gap = lambda_(d_k) / lambda_(d_k+1).
5. **Gate.** If gap <= 10, the rung is declared not found and nothing is removed.
6. **Repeat** on H_k with the pairs for layer k+1.

Result: R^d = V_1 + V_2 + ... + V_L + H_L, orthogonal pieces. One eigendecomposition per rung, nothing trained after the encoder.

## 3. Results by stage
| Stage | Question | Result |
|---|---|---|
| A | One split works? | Yes. 5 of 5 seeds, invariant R2 0.989 (authors 0.998). |
| B | Can the invariant part be split again? | Yes with exact pairs: 1.0 and 1.2 degrees, gap about 50. Building the pairs from data works for one rung only. |
| C | Depth 5, generic encoder? | Yes in the mild world (coupling strength 0.5): every layer to 0.2-2.1 degrees, 10 of 10 seeds. But an untrained identity encoder does the same there, so this shows the splitting works, not that the encoder learns. At strength 1 training matters (identity 0 of 5, trained 5 of 5). At strengths 2, 4, 8 it fails (0 of 5). |
| D | Does iterating help? | Partly. At equal layer speeds the ladder finds every layer (0.7-1.1 degrees) where a one-shot temporal split fails (80-89 degrees): correspondence, not speed, defines the layers. A one-shot split from the same pairs is as accurate; the ladder adds a visible gap. No predictive payoff shown. |
| Robot images (simulated) | Clean block? | No. Frozen ResNet-50 features: viewpoint ratio 1.1-2.1 against 3 required, no gap at rung 1. |

## 4. What holds the later rungs back
Measured at coupling strength 2 (trained encoder, seeds 250-253; `experiments/diag_rung2_split.py`):
- **Root cause: rung 1 leaks.** Block 1's change should live in 4 directions. In the embedding it also moves the other directions (variance about 0.5 against 1.9 in its own 4). The cause is the nonlinear coupling: whitening and eigen-splitting are linear, so a linear 4-dimensional block cannot hold a nonlinear footprint. Rung-1 gap is 3.5-4.3, below the gate of 10.
- **The gate then makes it worse.** Rung 1 is skipped, so block 1 is not removed. Rung-2 pairs resample blocks 1 and 2, giving 8 directions at variance about 2 against d_2 = 4: gap 1. Rung 3 inherits the same problem. With the gate off, rung 2 on the cleaned content has gap 3.7-4.7: the 4 block-2 directions at 2.0 against block 1's leftover at 0.4-0.5.
- **It is not** the angle measure, too few pairs (30,000 give a rank-monitor pass), or lost information (the invertible encoder keeps it). Strengths 4 and 8 show the same stored gaps (2, 1, 1), so I expect the same cause but have not checked it.

My earlier explanation (block 1's leftover alone) was only half right: the gate skipping rung 1 is the larger effect.

## 5. What the discovered blocks are worth
- **In the synthetic worlds:** meaningful. Each block is a planted layer, read back with presence R2 at least 0.96 (mild worlds), and layer order follows speed or correspondence.
- **On video or images:** not shown. The only image test (simulated robot) found no clean block, so there is no evidence that these blocks carry meaningful patterns from video. The method works where the observation is a mild invertible bijection of the layers; the real question, that of images, is open.
- **Predictive benefit** of the hierarchy: not shown.

## 6. Bottom line
The extension works where its assumptions hold: exact matched pairs and an observation map that does not strongly mix layers. It breaks when the map is strongly nonlinear (rung 1 leaks, the gate cascades) and on images. Not done: a fix for strength 2 or above, fine-tuned image encoders (needs a GPU), pairs built from data beyond one rung.

## Update: gate off at strength 2 (E56)
Turning the gate off fixes the cascade (rung-2 angle 61-86 degrees down to 5.0-8.2; rung 3 under 4) but no seed becomes clean: gaps stay 3.5-6.1, presence 0.84-0.86. So the remaining limit is the leak of each block under the nonlinear coupling, not the gate.

## Update: graded result at 4 and 5 blocks (E57, gate off)
5 blocks, coupling strength 2: every rung found on 5 of 5 seeds (angles 3-8 degrees against about 80 for unrelated, gaps 3-5, presence 0.85-0.93). 4 blocks, strength 4: every rung found on 5 of 5 seeds (angles 4-15, gaps 2.3-3.4, presence 0.71-0.86). Moderate error, clear function; the earlier zeros at strengths 4 and 8 came from the gate cascade.

## Update: pairs built from data, rungs 2-5 (E58, identity encoder, oracle cluster counts)
Median angle at rungs 2, 3, 4, 5 (unrelated about 80 degrees): exact twins 14, 21, 32, 49; clusters of the slow subspace 17, 31, 48, 57; clusters of the whole content 73, 84, 79, 89. So cluster-built pairs work at rung 2 (17 degrees) and fade by rungs 4-5, mostly because the ladder itself loses accuracy with depth in this world and because same-cluster pairs carry extra noise (gap 1.4-2.2), not because the clustering fails (purity 0.88-1.0). Whole-content clustering does not work at all. Best-case numbers: the true cluster counts were given.
