# Design proposal: SieveJEPA with the split learned by a nested loss (the blocks come from minimizing the loss)

**Status: design only (2026-11-17, owner asked for it). Nothing here is registered or run. Predictions and thresholds below are proposals for discussion, not frozen criteria.**

## 1. What this idea is
The embedding is cut into fixed slices, z = [z_1 | ... | z_L | core], and the encoder is trained so that **rung k's matched pairs agree on every slower slice**. The split is the result of minimizing the loss (as in the paper's robot code); no eigen-decomposition is needed to produce it. The eigen-split stays only as a **diagnostic** (the closed-form best cut of the trained embedding: its gap says how sharp the cut is).

**Loss (per batch):**  L = L_pred + lambda_inv * sum_k w_k * mean over rung-k pairs of || z_{>k}(u) - z_{>k}(v) ||^2 + L_var (hinge, each slice) + L_cov (decorrelate all outputs; plain Frobenius sums as in E45)
- the invariance terms are the cross-block leakage; they are nested because the slices slower than k sit inside the slices slower than k-1;
- the variance and covariance terms keep every slice informative and make the slices exclusive;
- block sizes d_k are fixed in advance (the paper does this too); choosing them is a separate question the eigen gap used to answer.

## 2. What already exists in this repository (a correction to my earlier statement that the nested loss had "not yet been run")
| Runs | What was done | What it showed | Limit |
|---|---|---|---|
| E40 to E45 | Generic MLP encoder, prediction objective plus `corr_inv_weight` = squared change of the later-block outputs across every correspondence family (this **is** the nested invariance term), plus variance and whitening terms | Depth 5: every rung clean on 10 of 10 seeds (E45), 9 of 10 on fresh seeds (E49); 4 blocks: rung 2 clean on 6 of 10 (refuted as registered) | Success was **read with the eigen-split ladder** (angle, gap), not from the trained slices directly; one mild-bend world |
| E52, E53 | Invertible encoder with that recipe | Information kept, but rungs aligned on only 2 of 10 (4 blocks) and 1 of 10 (5 blocks); 3x steps did not help | Possible routing of slices stuck from a random start (reading, not shown) |
| E54 | Invertible encoder, the paper's own objective only | Every rung clean on 10 of 10 | The easy world also passes with an untrained encoder |
| E55 | Same, harder world | Training repairs coupling strength 1 (5 of 5), not 2, 4, 8 (0 of 5) | Eigen-split read-out |
| E47, E66 | Robot, paper recipe with invariance terms; three heads | E66: heads separate progress and layout on PushCube (0.94 / 0.71) | Heads only 3-level; PickCube weak; scored partly by the ladder |

So the nested-loss idea has been run at depth 4 and 5 with a generic MLP and works there, but never **judged by the trained slices themselves**, never in the harder world, and never on rendered robot images.

## 3. What is new here
1. **Success is measured on the slices directly** (no eigen-decomposition at test time).
2. **The hard world** (E55 strengths 2, 4, 8), where the paper-objective encoder and the untrained encoder both fail.
3. **The routing problem (E52):** two arms, joint training from the start, and a **curriculum** that adds rung k's term every T steps, fastest rung first. (A hypothesis that the curriculum avoids stuck routing.)
4. **Depth:** 4 and 5 (existing comparison), then 8 and 10 in the synthetic world, then the E62 renders (conv encoder) with the retention gate from `DESIGN_ROBOT_DEPTH.md`.

## 4. Arms and worlds
Arms: **A** nested loss, joint; **B** nested loss, curriculum; **C** untrained encoder + eigen-split (the control the project learned it needs); **D** paper objective only + eigen-split (the E54/E55 recipe); **E** = A with the eigen-split run afterwards as a diagnostic (not a separate training). Worlds: W1 the E55 world at strengths {1, 2, 4, 8}, depth 4 and 5; W2 depth 8 and 10 at the strength where A passes in W1; W3 the E62 renders. 5 seeds per cell; pairs exact (oracle) and nested.

## 5. Measures
Direct, per slice k on held-out data: **presence** (nonlinear readout R^2 of its own layer), **leakage** (R^2 of every other layer, and the invariance residual ||z_{>k}(u)-z_{>k}(v)||^2 / variance), **core purity**. Health: smallest output-covariance eigenvalue at least 0.5 (E45 rule). Diagnostic only: gap and angle of the eigen-split on the trained embedding.

## 6. Proposed (unregistered) pass lines
In W1 at strengths 2, 4, 8 and depth 4 and 5: arm A or B has every slice present at 0.9 or more with leakage at most 0.1 on at least 7 of 10 seeds, while arms C and D have at most 2 of 10. At depth 8 and 10 (W2): the same on at least 4 of 5 seeds. Refuted if neither A nor B beats D in W1.

## 7. Risks and stated limits
- Routing can get stuck (E52); the curriculum arm tests one remedy, not all.
- The block sizes are given, not found; nested exact pairs are assumed (E67 shows that without them recovery collapses, and the loss version would learn the wrong invariances).
- One weight per rung is a tuning risk: fix lambda_inv and w_k = 1 in advance, as E40 did, and do not tune.
- W3 is the only arm on images, and the retention of small factors is the open problem there.

## 8. Cost
W1 and W2: CPU, minutes per run (E45-size MLPs; 30,000 steps). W3: about 1 to 2 GPU hours (about $0.5).

## 9. Open decisions for the owner
(i) arms to include (B and the untrained control are the two I would not drop); (ii) whether W3 is part of this; (iii) go-ahead; the pass lines above are mine to be changed before registration.
