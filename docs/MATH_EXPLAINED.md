# The mathematics of the splitter, step by step

Figures: `docs/img/math_fig1.png` (transformations), `docs/img/math_fig2.png` (one rung, mild and strong bend), `docs/img/math_fig3.png` (eigenvalues, ideal and measured).
Code: `src/isj/engine.py` (`fit_whitener`, `fit_rung`, `fit_ladder`).

## 0. Objects and where they live
| Symbol | What it is | Space |
|---|---|---|
| z = (z_1, …, z_L) | hidden values, L groups, group k has d_k numbers (D = Σ d_k, here 20) | generator only; the splitter never sees it |
| x = f(z) | observation: fixed invertible nonlinear map (tanh couplings) | observation space |
| r = g(x) | embedding from the trained encoder | R^D |
| r~ = C^(-1/2)(r − μ) | whitened embedding, C = Cov(r), μ = mean | R^D |
| H_k | invariant content after k rungs: a matrix D × m_k with orthonormal columns | subspace of R^D |

The splitter works **only in R^D, on the whitened embeddings**: linear algebra on vectors r~.

## 1. Why a linear method can work: the local picture
Write r = h(z) with h = g∘f. If h were linear, r = A z, and A = [A_1 … A_L] (column blocks match groups). Changing only group k by δ_k changes r by A_k δ_k. So the embedding directions that move when group k moves are span(A_k), a d_k-dimensional subspace. **Finding group k's block means finding span(A_k).**

## 2. Whitening
r~ = C^(-1/2)(r − μ) makes Cov(r~) = I. If the groups are independent with unit variance (Σ_z = I) and r = A z, then C = A Aᵀ and r~ = (AAᵀ)^(-1/2) A z = Q z with Q = (AAᵀ)^(-1/2)A orthogonal (Q Qᵀ = I). So **after whitening the embedding is a rotation of z**, and the blocks Q_k = span of block k are mutually perpendicular. (Figure 1, last panel: whitening fixes the covariance but not the bend.)

## 3. Matched pairs and their difference
For rung k, a pair (u, v) has z_j(u) = z_j(v) for every j > k, and independent redraws for j ≤ k. The difference of the whitened embeddings is
D = r~(u) − r~(v) = Q (z(u) − z(v)) = Q (δ_1, …, δ_k, 0, …, 0).
Each δ_j is a difference of two independent unit-variance draws, so Var(δ_j) = 2 per coordinate.

## 4. The moment and the eigendecomposition
Inside the current content H = H_(k-1):
M = Hᵀ ( (1/N) Σ_i D_i D_iᵀ ) H  (m × m, symmetric, positive semi-definite).
Spectral theorem: M = E Λ Eᵀ, Λ = diag(λ_1 ≥ λ_2 ≥ …), E orthogonal.
In the exact linear case, the blocks already removed (j < k) are not in H, so M has **d_k eigenvalues equal to 2 and the rest equal to 0**. The top d_k eigenvectors span the block k image; the others span what did not change.

## 5. The cut
V_k = H E_[:, 1..d_k]  (variant block, D × d_k)
H_k = H E_[:, d_k+1..m]  (invariant content, D × (m − d_k))
Then H_kᵀ V_k = 0, and span(V_k) ⊕ span(H_k) = span(H).
Gap = λ_(d_k) / λ_(d_k+1). Infinite for exact data; large means a clean block.

## 6. Iteration
H_0 = I_D. Rung k uses new pairs (agree on groups j > k), computes M inside H_(k-1), and sets H_k as above. The only thing passed to the next rung is the matrix H_k. Dimensions: D → D − d_1 → D − d_1 − d_2 → … → d_L (the core). Result: R^D = V_1 ⊕ V_2 ⊕ … ⊕ V_(L-1) ⊕ H_(L-1), mutually perpendicular. Cost: one eigendecomposition of an at most D × D matrix per rung.

## 7. Scoring (only for tests; uses the true z)
Angle: θ = arccos σ_min(V_kᵀ U_k), where U_k is an orthonormal basis of the true image of group k (from a ridge regression of r~ on z) and σ_min the smallest singular value; 0 degrees is perfect, about 80 is unrelated.

## 8. What breaks the equations (figure 2, bottom row; figure 3)
1. **Nonlinear bend.** h is not linear, so r~(u) − r~(v) is no longer A_k δ_k: the change of group k traces a curved set, not a d_k-dimensional subspace. M gets extra mass in the "unchanged" directions, so λ_(d_k+1) rises and the gap falls (measured at strength 2: λ ≈ 1.94 for the top 4 against 0.53 for the next, gap 3.7 instead of infinite).
2. **Inexact pairs.** Cluster-built pairs share only the cluster, so the slower groups differ by small jitter ε: M gains a floor 2σ² in the "unchanged" directions (gap about 3 at σ = 0.3).
3. **Finite samples.** Eigenvalue estimates fluctuate at order 1/√N (measured slope −0.48, E48).
4. **Errors compound.** If rung 1 leaves a leak, it sits inside H_1 and adds to every later M.
5. **A lost direction.** If the encoder squashes a group (generic MLP), that group's image is not in R^D at full rank; no linear method recovers it.
