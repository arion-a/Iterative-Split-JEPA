# What was done, in plain terms (2026-11-14)

You asked for a simple account: what calculation was performed, what it does geometrically, how it relates to the original SplitJEPA, and what the experiments showed. Everything below is checked against the code (`src/isj/engine.py`, `worlds.py`, `encoder.py`, `stage_b1.py`) and the result files.

## 1. The original SplitJEPA (what it already does)
An encoder maps an observation x to a vector r in R^d. The vector is cut into two fixed parts, r = [r_H ; r_L]. It is trained with three terms: predict the next frame, make r_L the same for matched pairs (same slow content, different fast content), and keep every output varying (no collapse). The result: r_L holds only the slow, constant content; r_H holds the fast, changing content. One cut, coordinates fixed in advance, learned by training.

## 2. The extension (iterative SplitJEPA): the whole method is this, 5 steps
1. **Encode and whiten.** r -> r~ = C^(-1/2) (r - mean), where C is the covariance of r. Geometry: the cloud of embeddings becomes a round ball (no direction is stretched).
2. **Take matched pairs for layer k.** Pairs (u, v) that agree on everything slower than layer k and differ in layer k. Compute the difference D = r~(u) - r~(v).
3. **Look at the shape of the differences.** M = average of D D^T. Geometry: the cloud of difference vectors is an ellipsoid. Its **long axes** point along the directions that change between the paired points (the variant block). Its **short axes** point along directions that stay equal (the invariant content).
4. **Cut at the gap.** Eigendecompose M = sum lambda_i e_i e_i^T, lambda sorted descending. The top d_k eigenvectors are the variant block V_k. The rest span the invariant content H_k. The "gap" lambda_{d_k} / lambda_{d_k + 1} says how sharp the cut is (large gap = a real block exists; gap near 1 = nothing to split).
5. **Repeat inside H_k** with the pairs for layer k+1.

Nothing is rotated or trained in steps 2 to 5; it is one eigendecomposition per rung. The picture: R^d = V_1 + V_2 + ... + V_L + H_L, a stack of orthogonal subspaces; rung 1 peels V_1 off R^d, rung 2 peels V_2 off what is left, and so on. What remains at the end is the slowest block, the content constant across everything the pairs vary.

## 3. How it relates to the original code and objective
| Original SplitJEPA | This project |
|---|---|
| The split is fixed in coordinates and trained | The split is found afterwards by the eigendecomposition above (`fit_rung`) |
| One split | Repeated on the invariant part (`fit_ladder`) |
| Objective: prediction + invariance on pairs + variance | Same objective used to train the encoder; later also added the invariance and whitening terms with fixed coordinates (E40 to E45) for generic encoders |
| Their synthetic world and robot images | Our planted-layer worlds (`worlds.py`), then simulated robot images (Stage R) |

## 4. What worked, what did not (numbers from the records)
| Stage | What it asks | Result |
|---|---|---|
| **A** one split | Does the single split work in our code? | **Worked.** 5 of 5 seeds; invariant R² 0.989 against the authors' 0.998. |
| **B** iterate | Can the invariant part be split again? | **Worked** with exact pairs: found blocks within 1.0 and 1.2 degrees of the true ones, gaps about 50 (E21). **Did not work yet:** building the pairs from the data (works for one rung, in our own world). |
| **C** deeper | Does it keep working at 4 and 5 layers? (Update 2026-11-15: **yes with a generic encoder too**: a generic invertible encoder trained with the paper's own objective found every layer to 0.2-1.9 degrees on 10 of 10 seeds at 4 and 5 layers, E54.) | **Worked** to 5 layers with the encoder built from the generator (0.6 to 2.1 degrees). With a generic encoder it worked after I fixed my own training bug (E45: every 5-layer rung clean on 10 of 10 seeds; E49 on fresh seeds: 9 of 10). The 4-layer 'layer-2 failures' (clean on 6 to 9 of 10 seeds) turned out to be the angle ruler, not the splitter: layer 2 was found to within 1.3 degrees of where it actually acts in the embedding in all 7 runs checked. |
| **D** does it help | Does iterating help beyond one split? | **Mostly not shown.** At equal speeds the ladder works and a one-shot temporal split fails (E38: 0.7-1.1 vs 80-89 degrees). But a one-shot split from the same pairs is just as accurate; the ladder's gain is a visible gap. Robustness gain on a nuisance shift: 0.04. |
| **Real images** | Does it find a clean block in robot images? | **Did not work.** Viewpoint ratio 1.1 to 2.1 against the 3 required; no gap at rung 1. |

So the claim "nothing worked" is not right: the core mechanism works in the setting the theory assumes (exact matched pairs, an encoder that keeps the information). What has not worked is everything beyond that setting: building pairs from data, and real images.

## 5. Why it became so many experiments (my account)
- The pipeline is the five steps above. Every experiment reran that same pipeline with a different world, encoder, seed or test; there were not hundreds of different operations.
- Of the 51 numbered experiments, the ones that carry the result are few: A (one split), B/E21 (iterate), E34/E39 (depth), E38 (pairs beat speed), E45/E49 (generic encoder), Stage R (images). The rest were repairs and my own test designs: a generic encoder that collapsed because I left out a constraint the theory requires, tests that could not have shown the effect, thresholds I set and then argued with.
- I wrote results as "confirmed as registered" and "refuted as registered" for every item. That was accurate bookkeeping, but it hid the plain answer: the simple extension works where its assumptions hold and has not been shown to work outside them. I should have said that first.

## 6. The honest bottom line
- The theory's idea, repeated eigen-splitting of matched-pair differences, is implemented in one file (`src/isj/engine.py`) and works in its idealized setting.
- It does not yet work on realistic data, and it has not been shown to beat simpler alternatives in accuracy.
- The robot test failed in the same way the synthetic generic encoder first failed (collapsed output directions); the synthetic case was fixed by enforcing the whitening constraint, and the same terms did not fix the robot case.

Where the detail is: `docs/EVIDENCE.md` (every prediction and outcome), `docs/ROADMAP.md` (stage status), `docs/PROJECT_DRAFT.html` (diagrams).

## Correction 2026-11-15
An untrained identity encoder passes every check the trained encoders pass in the synthetic world (presence 0.99, angles under 2 degrees, gaps 63 to 107). So the synthetic results show that the eigen-splitting recovers planted layers from exact pairs when the observation is a mild nonlinear bijection; they do not show that encoder training does any work, and the E54 statement that it closes the generic-encoder question was too strong. A coupling-strength sweep (E55) tests where the world becomes hard enough that training matters.

## Result of E55 (2026-11-15)
In a harder world the untrained encoder fails from coupling strength 1. Training with the paper's objective repairs strength 1 (5 of 5 seeds clean) but not 2, 4 or 8 (0 of 5 each; layers 2 and 3 are not found at all). So encoder training matters, but only over a narrow range with this recipe.

## Correction 2026-11-15 (after reading the paper's public code)
Section 1 and 3 above describe the paper's split as a fixed slice trained with an invariance loss. That is how the paper's **robot** code works (`robot/hl_maniskill/`), but the paper's **synthetic** experiment (`simulation/`, repository splitjepa/splitjepa.github.io) does exactly what this project does: train a LeJEPA encoder, freeze it, ZCA-whiten, then take the eigenvectors of the covariance of matched-pair differences as the rotation (smallest directions = invariant block). So the iterated version here is the paper's synthetic split repeated rung by rung, not a replacement. The paper's robot data is not released (its README says the prepared episodes and pair files are not included).

Clarification (same day, owner's point): the paper's mechanism is a minimization, and so is the eigen-split. Choosing orthonormal directions Q that minimize the average pair-difference energy, average of ||Qᵀ D||², is solved exactly by the eigenvectors of the pair-difference covariance with the smallest eigenvalues (Rayleigh-Ritz / Ky Fan). The paper's robot code minimizes the same invariance term by gradient descent on the encoder, jointly with prediction and variance terms; its synthetic code solves it in closed form on a frozen encoder after whitening, as this project does. Each rung here repeats that minimization inside the directions left by the previous rung.
