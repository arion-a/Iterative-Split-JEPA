# Step-by-step plan for E68 / E69 (nested loss), with the mathematics that is programmed

**Status (2026-11-18): plan for the owner's review. The registered predictions are in `docs/EVIDENCE.md` (E68, E69) and are unchanged. No E68/E69 run has been made. A GPU pod was created and terminated again (no run on it) so that it would not bill while this plan is reviewed.**

## 0. What is reused and what is new
**Reused unchanged:** the world (`worlds.py`), the E45 recipe and weights (`configs/deep_mlp_d4_fix.yaml`), the Stage-B1 evaluation (ladder, angles, gaps, presence, health), the E55 "clean" rule.
**New, all small (made before this plan; to be regression-tested in step 2):** (i) `corr_inv_schedule` in `encoder.py` (curriculum arm); (ii) `device` in `encoder.py` (training on a GPU, encoder returned on the CPU); (iii) slice measures in `stage_b1.py` (new key `slice`); (iv) the runner `experiments/run_nested_loss.py`; (v) the analysis script (step 6, not yet written).

## 1. The mathematics, exactly as it will be programmed
**World.** K blocks of 4 numbers, z = (z_1, ..., z_K) in R^{4K}, block 1 fastest. Stationary AR(1) per block: z' = rho_b z + sqrt(1 - rho_b^2) eps, rho = (0.2, 0.5, 0.75, 0.95) for K = 4 (`transition_pairs`). Observation x = g_s(z), the coupling map of strength s with 4K outputs (`CouplingMap`).
**Rung-k pairs** (`correspondence_pairs(n, k)`): u ~ N(0, I); v = u with blocks 1..k replaced by fresh draws; blocks k+1..K identical (exact, nested).
**Encoder** h = f(x) in R^{4K} (MLP, 2 hidden layers of width 64 (128 for K > 4), GELU); slice h_b = h[4(b-1) : 4b]; "tail_k" = h[4k : 4K] (every slice slower than k). Predictor p (MLP).
**Loss per step** (`train_encoder`, lines 191-213; weights fixed, never tuned):

L = MSE( p(h_t), sg(h_{t+1}) )
 + sum_{k=1}^{K-1} 1[step >= t_k] * { 1.0 * mean( (tail_k(u) - tail_k(v))^2 ) + W * || Cov(h_k(u) - h_k(v)) - 2 I ||_F^2 }
 + W * || Cov(h) - I ||_F^2
 + 0.01 * sum_j max(0, 1 - std(h_j)) + 0.04 * (mean squared off-diagonal of Cov(h))

where h_k(.) is slice k of the encoder output on rung-k pairs, sg = stop-gradient, ||.||_F^2 is a plain sum (E45), t_k = 0 for all k (arm A) or t_k = 5000 (k - 1) (arm B). W is picked per world by the E45 pilot rule (smaller of {1, 10} giving lambda_min(Cov(h)) >= 0.5 at seed 0 after 10,000 steps).
**Slice measures** (held out; 15,000 train / 5,000 test samples; R^2 of a small MLP probe, the repository's `audits.mlp_r2`):
presence_b = R^2( z_b <- h_b ); leakage_b = max_{c < b} R^2( z_c <- h_b ) (b = 2..K); duplication_b = R^2( z_c <- h_b ), c > b (reported only); health = lambda_min(Cov(h)).
**Slice-clean seed:** presence_b >= 0.9 for all b, leakage_b <= 0.1 for all b >= 2, health >= 0.5. **Ladder-clean seed (E55):** every rung angle < 5 degrees and gap > 10, every presence (whitened embedding) >= 0.95.

## 2. Steps (each ends in a pass/fail check; a failed check stops the work and is reported, nothing is tuned)
1. **Freeze the code and the weights.** Commit the new code; no later edit without a note in `EVIDENCE.md`.
2. **Regression gate G1 (old behaviour unchanged).** With `device = cpu` and no schedule, the training loss log for 300 steps, seed fixed, must equal the log from the code before my edits (`git stash` copy): bit-for-bit. *Catches: broken edits to `train_encoder`.*
3. **Unit tests (added to `tests/`):** (T1) schedule: at step < 5000 only family 1's term is non-zero (count terms); (T2) slice measures on a synthetic embedding h = z (permuted) give presence ~ 1, leakage ~ 0, and on h = random noise give presence ~ 0; (T3) CPU and GPU runs of the same 200 steps agree in loss to 1e-3 (GPU test only on the pod). *Catches: slice indexing and device errors.*
4. **Reproduction gate G2 (the pipeline reproduces a stored result).** Arm A at strength 0.5, one stored E45 seed (160): the ladder-clean status and presence must agree with `results/minimal/e45/d4` for that seed, within seed-level noise (angles within 1 degree). *Catches: the runner or config assembly differing from the E45 pipeline.*
5. **Pilots.** For each strength (and depth) pick W by the rule above; write `W.json`; a world with no healthy W is not run (reported).
6. **Analysis script before the runs.** `experiments/analyse_e68_e69.py` implements the two clean rules above and the registered verdict lines (a), (b), (c); tested on made-up result files (T4) so the verdict logic is checked before any real result exists.
7. **E68 runs** (registered: arms A and B x strengths 1, 2, 4, 8 x seeds 250-254 = 40 runs) on **one GPU pod** (as the owner requires): up to 8 processes in parallel on the pod (the model is tiny, so throughput comes from parallel processes, not from one big kernel); results downloaded to this machine **before** the pod is terminated.
8. **Verdict for E68** by the analysis script; record in `EVIDENCE.md`; commit and push.
9. **E69 only if E68 (b) holds** (registered): choose s9 by the stated rule; run depth 8 and 10 (nested arm + untrained control); verdict; record.

## 3. Risks and how the plan answers them
- *Edits break the old code path* -> G1, plus the 58 existing tests (all pass after the edits, run with `PYTHONPATH=src`).
- *Wrong slice indices* -> T2, and the slices are the same `block_slice` the loss uses.
- *GPU and CPU differ* -> T3 (and a note that GPU runs are not bit-identical to CPU runs).
- *Runner differs from the E45 pipeline* -> G2.
- *Verdict logic wrong* -> T4 before any run.
- *Pod cost* (this pod type bills 0.50 USD/h, not the earlier 0.22): about 40 runs in parallel; the time per run is measured in G1/G2 on the pod and reported before the main batch starts.

## 3b. Update (owner, same day): depth to 10, 12, 15 rungs (E71 replaces E69's depths)
- **New experiment E71 (registered in `EVIDENCE.md`):** K = 11, 13, 16 blocks (10, 12, 15 rungs; d = 44, 52, 64), hidden width 16K, steps 7,500 K, speeds 1 - geomspace(0.8, 0.04, K); E71a at the mild strength 0.5 (depth alone), E71b at the hard strength s9 (only if E68 (b) holds).
- **New per-rung measure (math):** r_k = mean_{rung-k pairs} || tail_k(u) - tail_k(v) ||^2 / mean variance(tail_k); rung k is clean if presence_k >= 0.9, leakage_k <= 0.1, r_k <= 0.05. This is computed in `stage_b1.py` (to be added in step 3 and covered by T2 and a new test T5: r_k is 0 for an embedding whose tail ignores the pair difference, and about 2 for random outputs).
- **Plan changes:** step 5 (pilots) and step 7 (runs) now include the E71 cells; step 9 is replaced by "E71a runs (independent of E68), E71b only if E68 (b) holds"; the pod runs the K = 16 cell first because it is the slowest.
- **Cost check before the batch:** a timed 300-step run per K on the pod, from which the total pod hours are computed and reported to the owner before the batch starts.

## 4. Known rough edge to fix before step 2
The `rhos` line in the runner is written clumsily; it will be replaced by the plain rule: K = 4 uses the config's speeds; K > 4 uses rho_b = 1 - geomspace(0.8, 0.04, K)_b (as in E61).
