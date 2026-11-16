# Verification of what we borrowed from the SplitJEPA paper (2026-11-16)

**Sources read this pass:** the paper's full HTML text (arXiv 2610.12349v1, three chunks; the last ~9,000 characters, the tail of Table 6 and Appendix D.2 "Temporal Transferability / Controlled Intervention", were seen only as a summary) and the authors' released code, the project repository `splitjepa/splitjepa.github.io` (folders `simulation/` for the synthetic world, `robot/` for the ManiSkill experiment, `lean/`). The paper's HTML names no code link; the project site is the only link. The `robot/` folder that ran on the pod is byte-identical to the repository's (checked with `diff -r`). `train_paper.py` only overrides the epoch count.

| # | What we said or did | What the source says | Status |
|---|---|---|---|
| 1 | Split = whiten, then eigen-decompose the pair-difference moment; smallest directions = invariant | Paper text: ZCA on 30,000 representations, uncentered moment of 30,000 pair differences, bottom d_H eigenspace = invariant. Code: same, but the differences are **centered** first (N−1) | Verified. We use the uncentered form (the text's); centering changed no robot conclusion (E59 re-check below) |
| 2 | Synthetic world: 4+4 numbers, OU pairs rho=0.5, 4 tanh coupling layers, strength 0.5 | Same (paper Sec. 4.1 / App. C.1; `simulation/run.py`) | Verified |
| 3 | Paper objective for the synthetic encoder: alignment + SIGReg (weight 1e-6), 10,000 steps, batch 256, lr 3e-3, cosine in the second half | Same in `lejepa.py`; our `encoder.py` `lejepa` objective and SIGReg match it line by line | Verified |
| 4 | Paper's own synthetic encoder | A **mirror** (learned inverse couplings, built from the generator's structure), not a generic network | Our docs already flagged this limit; the components report now says it |
| 5 | Robot: ResNet-50 (ImageNet) with invariant and variant heads, d_H=d_L=64 (Pick) / 128 (Push), batch 32 transitions + 32 pairs, AdamW lr 3e-4, wd 1e-4, cosine, clip 10 | Same in code and paper text | Verified |
| 6 | Robot losses `pred + inv + variance + 0.04 cov` | Code: weights 1, 1, 1, 0.04. The paper text names the terms and gives no weights. Code details: **variance is a mean (not a sum)** of the hinge; inv and pred are mean squared errors; pred target is stop-gradient | **Corrected**: our components report had variance as a sum (copied from our own `encoder.py`) |
| 7 | PushCube trained 200 epochs, like PickCube | Paper config: PickCube 200, **PushCube 100** | **Deviation**, now stated in the reports |
| 8 | Robot data | Paper: 800 successful trajectories in 100 groups of eight, base + side camera, 128x128; data **not released**. Ours: same structure, our own trajectories, action replaced by a stand-in (end-effector movement padded to 8) | Stated as a difference; comparison with the paper's numbers is indirect |
| 9 | "Paper's reported 8.4 and 14.0" | Appendix D.2 (not Sec. 4.2): normalized response D_B = (1/sqrt(d_B)) \|\|(r_B(x)-r_B(x'))/sigma_B\|\|, per-coordinate sigma; ratio D_L/D_H (PickCube 1.51/0.18 = 8.4) | **Our ratio is a different normalization.** Re-scored here with the paper's definition on the 200-epoch embeddings (below) |
| 10 | "One split reproduces the paper: 0.989 vs 0.998" | Paper Table 1: invariant R² 0.9979, global R² 0.9977 (SplitJEPA, 5 seeds); no "slow part" score exists | **Corrected wording**: 0.989 is our generic encoder; the mirror encoder gives 0.9977 global R², matching |
| 11 | Table 4 (strength 0.5 / 1 / 2: 0.9979 / 0.9565 / 0.8765) | Confirmed, App. C.5, seed-00 diagnostic; only these three strengths | Verified; our sweep to 4 is our extension |
| 12 | The paper has no ladder / iteration | Single pass: train, freeze, ZCA, one bottom-d_H eigenspace | Verified; the ladder is ours |
| 13 | Cluster-built pairs | Ours (not in the paper). The test used the **true cluster count** and supplied rung-1 pairs, in a nested-mixture world | **Caveat added** to the reports |

## Re-scoring with the paper's own definition (200-epoch embeddings, held-out trajectories)
`experiments/robot/paper_baseline/verify_ratio.py`, results `results/paper_baseline/VERIFY_ratio_*.json`. Ratio of the variant block's response to the invariant block's, camera pairs; "mean of norms" = mean over pairs of D_B; "rms" = root-mean-square over pairs; "ours" = the normalization used in most of our tables.

| | paper def. (mean of norms) | paper def. (rms) | ours |
|---|---|---|---|
| PickCube paper's halves | 5.08 | 3.70 | 3.69 |
| PickCube eigen-split, no whitening | 6.88 | 5.21 | 5.05 |
| PickCube eigen-split, centered differences | 6.09 | 5.02 | 4.68 |
| PushCube paper's halves | 5.95 | 4.50 | 4.49 |
| PushCube eigen-split, no whitening | 9.26 | 6.34 | 7.34 |
| PushCube eigen-split, centered differences | 9.24 | 6.42 | 7.30 |

Reading: the paper's own halves score 5.1 / 6.0 under the paper's definition (the paper reports 8.4 / 14.0 on its own data and trajectories, so our runs do not reproduce those). The eigen-split beats the paper's halves under every definition and with or without centering.

## Not verified
* The last ~9,000 characters of the paper's HTML were read only as a summary.
* The paper's `lean/` formal proofs were not read.
* Rows of the components report's "which component is used where" table beyond the checked ones (pairs-from-data, robot, scene factors) come from the experiment records, not a config-by-config audit.
