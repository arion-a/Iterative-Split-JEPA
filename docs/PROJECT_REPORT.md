# Project report: what has been done, how it works mathematically, and what came out

Written 2026-11-15 from the repository as it stands (code in `src/isj`, results in `results/`, predictions and outcomes in `docs/EVIDENCE.md`, run log in `docs/STATUS.md`).
Every number below is copied from a result file or from `docs/EVIDENCE.md`; nothing is re-tuned. Equations are in code blocks so they read the same everywhere; each one names the file where it is implemented.

---

## 0. The short version

**What the project tries to do.** Take raw video of a physical system (a swinging pendulum, a robot arm), learn a latent vector for every frame **without any physics labels**, and then *split* that vector into two parts:

* a **variant** part: directions that change a lot between two frames that are "matched" in some way (for example 8 frames apart, or the same frame seen with different lighting);
* an **invariant** part: directions that barely change between matched frames.

The split is repeated on the invariant part with a different kind of matching (a "ladder" of rungs), so the invariant core gets slower and more general at each rung. The claim under test is that the slowest direction of the core is a **dynamically valid abstraction** (a coordinate whose future depends only on itself), and that it can later be **named** (for a pendulum: "energy") by comparing with the simulator's or tracker's table, which the learning side never saw.

**Where it stands (honest).**

| Claim | Status |
|---|---|
| In simulation, the pipeline finds and certifies a slow coordinate | **Supported** (certificate passes on every seed; naming against energy 0.97–0.98 with enough data, below the 0.99 I pre-registered) |
| On real pendulum video (Columbia, 100 videos), the slow coordinate tracks energy | **Supported in part**: correlation 0.91, seed agreement 0.97, certificate partly passes; "energy" cannot be told apart from "swing amplitude" there |
| The same on other real data (NUS double pendulum) | **Not supported**: seeds disagree, rollout error 0.6–0.9, no fix tried reached the bar |
| A ladder of **several** rungs on real video / robot data | **Not shown**: real video gave at most one cut (63 directions vs 1); robot data gave none; several rungs have only worked in planted simulations |
| The ladder adds something over a plain slow-feature direction | **Not shown** (they gave the same answer) |

The defensible claim today: *the pipeline finds an energy-like slow coordinate without physics labels, in simulation and on one real dataset.*

---

## 1. The idea in plain words

Think of a film of a pendulum swinging. From frame to frame the pixels change a lot (the bob moves), but some things barely change over a whole video: the total energy, the length of the rod, the lighting. The project asks whether a learning system can find the "barely changes" directions **on its own** and prove they are meaningful.

Three ingredients, in the language of the project's source documents:

1. **Prediction fixes the content.** An encoder is trained to predict its own future latent (JEPA-style: no pixel reconstruction). Whatever helps predict survives; the rest is dropped.
2. **Correspondences fix the partition.** Which pairs of frames you call "matched" decides which directions count as invariant. Two renderings of the same frame (different lighting) say "lighting is nuisance". Two frames 8 steps apart say "whatever moves fast is variant". Different matchings give different splits.
3. **Iteration builds a ladder.** After a split, the invariant part is split again with the next matching. Each rung removes a faster layer, so the core gets slower.

Then two audits, both outside the learning:

* **Certificate** (is the coordinate a valid abstraction?): its future must be predictable from itself, with the same value giving the same future in different videos.
* **Naming** (what is it?): compare with a sealed table of true physical quantities, **after** the coordinate is fixed.

The code enforces the separation: `tests/test_sealed_audit.py` checks that the discovery modules contain no physics words, and evaluator code never feeds back into discovery.

---

## 2. The data (what is observed, and what is sealed)

"Release" below means one trajectory that starts from one initial condition (one video or clip). Quantities that are conserved within a release (energy, for an undamped pendulum) are what the method is looking for.

| Name | What it is | Size | What discovery sees | What the evaluator sees (sealed) | Used for |
|---|---|---|---|---|---|
| **Planted AR worlds** (`worlds.py`, `hier.py`) | Synthetic latent states, each block an AR(1) process with its own speed, scrambled into observations | 5 blocks × 4 dims, or 2 blocks | observations only | the true blocks | Stage A/B, hierarchical test, E36, depth world |
| **Simulated double pendulum** (`pendulum.py`) | RK4 simulation, rendered as 32×32 gray (Gaussian blobs for bobs and rods) plus additive illumination and pixel noise | 150 or 450 releases | frames, two lighting versions per release | angles, velocities, energy | Stage V handshake, scaling probe |
| **Columbia "state variables" videos** | Real videos of double (and single, elastic) pendulums, 32×32 gray | 100 videos × 660 frames (double); 1200 clips (single, elastic) | frames | tracked total / kinetic / potential energy | Real-video test (C1, C2, C3, G3) |
| **HF controlled pendulum** (`jimchen2/pendulum-cjepa-dataset`) | Rendered single pendulum, 200 videos × 72 frames, independently controlled sinusoidal lighting | 200 videos | frames | exact energy, angle, light angle | H1 |
| **ManiSkill PickCube** | Simulated robot arm picking a cube, two cameras (base, side), generated on this CPU | 150 episodes at 32×32 gray; 200 episodes at 64×64 RGB | frames from both cameras | cube, goal, tool-point, joint positions | R1, RL |
| **NUS double pendulum** (`MLDS-NUS/double_pendulum`) | Real lab footage, white bars on black, 720×720, 80,193 frames in 100 videos | 93 videos × 660 frames used | frames only | **no labels**; image-derived height, reach, motion | N, T1–T3, diagnostics |

How a frame is turned into discovery input (all shapes are `(releases, views, time, features)`):

```
frame x_t                      : D = 1024 numbers (32x32 gray), or 12288 (64x64 RGB)
two views of the same clip     : x~_t^(a) = x_t + sum_{j=1..4} c_j^(a) B_j        a in {0,1}
                                 B = {1, x, y, x*y} on [-1,1]^2, c ~ Uniform(-0.4, 0.4), constant for a whole clip and view
                                 (video_io.illumination_basis, real_video_io.illumination_views)
descriptor of frame t          : u_t = [ x~_t ; x~_t - x~_{t-1} ]        (2D numbers)
standardized                   : u'_t = (u_t - mean) / s     with one scalar s for each half (video_encoder.Standardizer)
```

The additive lighting is the **nuisance**: something that changes between views but should not matter.

---

## 3. The mathematics, step by step

Notation: `R` releases, `T` frames, `d = 64` latent dimension, `n` number of pairs, `τ` a time lag in frames.

### Step 1. Encoder: descriptor → latent (`video_encoder.py`, `encoder.py`)

A network `f` maps each standardized descriptor to a latent `z_t = f(u'_t) ∈ R^64`. It is an MLP (two hidden layers of 256, GELU) for 32×32 gray, and a small conv net for 64×64 (4 stride-2 convolutions then a linear head; 3-channel for RGB).

Training minimises four terms (AdamW, learning rate 0.003 with cosine decay in the second half, batch 256 or 128, 4000–8000 steps):

```
L = (1/|H|) * sum_{h in H}  MSE( g_h(z_t) , stopgrad(z_{t+h}) )        prediction (JEPA), H = {1, 8, 32}
  + 0.01 * sum_j max(0, 1 - sqrt(Var(z_j) + 1e-4))                      variance hinge: no dimension may shrink below std 1
  + 0.04 * (1/d) * sum_{i != j} C_ij^2        (C = covariance of z)     decorrelation: no two dimensions may copy each other
  + w_aug * MSE( z_t^(0) , z_t^(1) )                                    consistency of the two lighting views (w_aug = 0.2)
```

* The **prediction** term is what makes the latent keep what is predictable (the "content").
* The stop-gradient on the target and the **variance / covariance** terms prevent collapse (a Stage A fix: without them the latent collapses to a few directions).
* The **consistency** term makes the encoder insensitive to the lighting nuisance. Consequence worth remembering: the lighting is removed *by training*, not by the later split (section 6.3).

### Step 2. Whitening (`engine.fit_whitener`)

```
mu = mean(z),   C = cov(z) = V diag(lambda) V^T
W = V diag( max(lambda, 1e-5)^(-1/2) ) V^T            (ZCA, symmetric)
z~ = (z - mu) W
```

After this every direction has unit variance and no correlation. Two **unrelated** frames therefore differ by `E‖a-b‖² = 2` per direction: **chance level = 2**. A perfectly invariant direction differs by 0. Every later number is measured against this scale.

### Step 3. Correspondence pairs (`temporal_ladder.py`)

A *family* is a rule that produces pairs `(a_i, b_i)` of whitened latents that are supposed to share the slow content:

```
rendering pair (family "aug") : ( z~_t^(0) , z~_t^(1) )       same frame, two lightings (or two cameras)
lag pair (family "lag tau")   : ( z~_t , z~_{t+tau} )          same release, frames tau apart
shuffled control              : second element replaced by a random permutation (no real correspondence)
```

### Step 4. The difference moment and its spectrum (`engine.fit_rung`)

```
Delta_i = a_i - b_i                                        (a difference of matched pair i)
M = (1/n) * sum_i Delta_i Delta_i^T                        (d x d)
M restricted to the current content H_{k-1}:   M_k = H_{k-1}^T M H_{k-1}
M_k = sum_j lambda_j e_j e_j^T,    lambda_1 >= lambda_2 >= ...      (eigen-decomposition, descending)
```

`λ_j` is the mean squared change, between matched pairs, of the direction `e_j`. In whitened units: `λ ≈ 2` means unrelated, `λ ≈ 0` means invariant. For a block that is held fixed in the pair, `λ = 0`; for a block that is freely resampled, `λ = 2`; for a **temporal** AR(1) block with per-step coefficient `a`:

```
E[(z_t - z_{t+tau})^2] = 2 * (1 - a^tau)
```

So fast blocks (small `a`) have large `λ` and slow blocks (`a` near 1) have small `λ`. The spectrum of `M_k` is therefore a readout of the timescales present. (Values above 2, such as the 3.5 in section 4.2, occur for oscillating directions whose value at `t+τ` is anti-correlated with the value at `t`.)

### Step 5. Where to cut (`temporal_ladder.choose_block`)

```
S1 (skip):   lambda_1 <= 0.05 * 2 = 0.1       the family shows no variation at all -> skip it, try the next family
ratio_j  =   lambda_j / lambda_{j+1}          only for cuts with lambda_j > 0.1
j*       =   argmax_j ratio_j
cut if ratio_{j*} >= gamma_min = 2.0   -> d_k = j*,        else  S2 (no clean cut) -> the ladder stops
```

The **gap ratio** `ratio_{j*}` is the number quoted throughout the results ("2.4", "4.6"). A clean split needs a gap: a group of directions that change a lot, then a sharp drop to a group that change little.

### Step 6. The split itself, with hard nesting (`engine.fit_rung`)

```
V_k = H_{k-1} * [ e_1 ... e_{d_k} ]                    variant block (top d_k eigen-directions), orthonormal
H_k = H_{k-1} * [ e_{d_k+1} ... e_m ]                  invariant content = the complement, orthonormal
H_k  is a subspace of  H_{k-1}                          "hard nesting": a deeper core is always inside the previous one
```

### Step 7. Iterate (`temporal_ladder.run_ladder`)

Families are tried in order (rendering pair first, then lags of increasing size). Rung `k` computes the spectrum **inside** `H_{k-1}`, cuts, and passes `H_k` on. Ends when a family shows S2 (no gap), when no content is left, or when families run out. The final `H_K` is the **core**; `V_1 … V_K` are the **variant blocks**.

```
whitened latent z~  ( d = 64 )
        |  rung 1  (rendering pair)  ->  V_1 (nuisance directions)    H_1
        |  rung 2  (lag tau_1)       ->  V_2 (faster dynamics)        H_2   subset of H_1
        |  rung 3  (lag tau_2)       ->  V_3 (slower dynamics)        H_3   subset of H_2
        v
      core H_K  (what is left: slowest / most invariant)
```

### Step 8. Choosing one coordinate in the core: max-ICC direction (`temporal_ladder.fit_psi`)

If the core has more than one dimension, pick the direction that best separates releases from each other:

```
c_t   = z~_t H_K                                        (core coordinates, m-dimensional)
T     = cov(c)                                          total covariance
B     = cov of the per-release means of c               between-release covariance
solve   T^{-1/2} B T^{-1/2} u = lambda u ,   w = T^{-1/2} u_max
psi_t = (c_t . w - mean) / std                          the coordinate, standardized on the fitting releases
```

`λ_max` is the between-release variance share the fit reached ("ICC"). If the core has one dimension this step is trivial.

### Step 9. The certificate (`quotient_audit.certificate`)

All on held-out releases, with `q = ψ` standardized on the fitting releases, `K = 8`, `δ = 0.1` standard deviations:

```
ICC      = Var_over_releases( mean_{view,time} q ) / Var(q)            share of variance that is between releases (1 = constant within a release)
drift    = 95th percentile of |q_{t+K} - q_t| on validation releases
eps      = delta + 2 * drift                                           tolerance
V        = P( |q(s_{t+K}) - q(s'_{t'+K})| > eps  |  |q(s_t) - q(s'_t')| <= delta )   over pairs from DIFFERENT releases
           "two frames with the same q should have the same future"       (violation rate, want ~0)
q' = A q + b   fitted by least squares on one-step pairs (the latent transition F^)
L        = || A ||_2                                                   Lipschitz constant of F^ (<= 1 means non-expanding; ~1 = conserved)
rollout  = sqrt( mean ( F^K(q_t) - q_{t+K} )^2 ) / std(q)              K-step rollout error (0 = perfect, ~1 = no better than the mean)
```

Pass thresholds used in the real-video tests: `V ≤ 0.05`, `L ≤ 1.02`, `rollout ≤ 0.35`, `ICC ≥ 0.9`.

### Step 10. Naming and controls (evaluator side only, `handshake_eval.py`)

```
naming       = | Spearman( psi , E ) |          E = true or tracked energy; sign is arbitrary
flat arm     = top principal component of the raw latent (no split)               baseline: should name energy worse
shuffled arm = ladder with permuted lag partners                                  control: should find nothing
temporal-only= slowest direction of the lag-tau difference moment, no release grouping
seed agree.  = | Spearman( psi from seed a , psi from seed b ) |  on the test frames
ceiling      = held-out R^2 of a linear readout of E from the whole latent (report only)
```

### What is transformed, in what manner, ending where (one table)

| Object | Shape | Operation | Equation | Output |
|---|---|---|---|---|
| frames | (R, T, 1024) | add two lighting patterns | `x~ = x + Σ c_j B_j` | (R, 2, T, 1024) |
| descriptors | (R, 2, T-1, 2048) | frame and frame-difference, standardize | `u = [x~_t ; x~_t - x~_{t-1}]` | standardized descriptor |
| latent | (R, 2, T-1, 64) | learned encoder | minimise `L` above | `z` |
| whitened latent | same | ZCA | `z~ = (z - μ) C^{-1/2}` | unit-variance, uncorrelated; chance = 2 |
| pairs | (n, 64) × 2 | pick matched pairs | rendering / lag / shuffled | `a_i, b_i` |
| moment | (m, m) | average outer product of pair differences, inside current content | `M_k = H^T E[ΔΔ^T] H` | eigenvalues `λ_j` |
| cut | integer, subspaces | largest eigenvalue ratio above S1 level, ≥ 2.0 | `d_k = argmax λ_j/λ_{j+1}` | `V_k`, `H_k` (nested) |
| core coordinate | (R, 2, T-1, 1) | max between-release variance share | `T^{-1/2} B T^{-1/2} u = λ u` | `ψ` |
| certificate | 5 numbers | transition fit and rollout | `V, ICC, L, rollout` | pass / fail |
| name | 1 number | rank correlation with sealed table | `|ρ_s(ψ, E)|` | "energy-like" or not |

---

## 4. Worked examples of what the numbers mean

### 4.1 A planted world where the answer is known (hierarchical AR)

Five blocks, per-step coefficients `a = (0.2, 0.5, 0.75, 0.9, 0.95)`, lag `τ = 1`. The predicted eigenvalues are `λ_k = 2(1 − a_k)`:

```
lambda  = 1.6   1.0   0.5   0.2   0.1
ratio   =    1.6   2.0   2.5   2.0           (adjacent gap ratios; computed by hier.oracle_cut_gaps)
```

With the criterion `γ_min = 2.0` only the single best cut (2.5) is taken, so the ladder found **1 rung** where I had registered 4 (experiment E35, refuted as worded). The structural fact behind it, measured and proven in the AR world: **a cut's gap ratio can never exceed the ratio of timescales across it**. The depth world `a = (0.1, 0.9, 0.99, 0.999)` has ratios 9, 10, 10 at lag 1, and there the ladder takes **all 3 cuts on every seed**, a single-lag ladder only 2, and the shuffled control 0.

### 4.2 The same machinery on real video (Columbia, seed 0)

Ladder record from `results/columbia_full/0.json`:

```
rung 1  rendering pair : lambda_max = 0.001 (chance 2)  ->  S1, skipped    (the encoder already ignores the lighting)
rung 2  lag 8          : eigenvalues  3.51 3.45 3.36 ... 0.449 0.355 0.077
                         ratio at the last position = 0.355 / 0.077 = 4.6 >= 2.0  ->  CUT: 63 variant directions, 1 invariant
rung 3  lag 32         : the core has 1 dimension, nothing to split           ->  stop
```

Result: the core is a single direction; ψ is that direction. Its certificate on held-out videos: `V = 0.0`, `L = 0.985`, `rollout = 0.30`, `ICC = 0.68`; naming `|ρ| = 0.905` against tracked energy. (The tracked energy's own between-video ICC is only 0.553, because real energy decays inside a video, so ICC 0.9 was never reachable there.)

### 4.3 The same machinery on NUS (seed 0, baseline encoder)

```
rung 1  rendering pair : lambda_max = 0.0006        -> S1, skipped
rung 2  lag 8          : last eigenvalues 0.764 0.743 0.341   ratio 0.743/0.341 = 2.18 (criterion 2.0)  -> a cut, but barely
rung 3  lag 32         : core has 1 dimension      -> stop
```

A gap ratio of 2.2–2.5 sits close to the 2.0 criterion, so different seeds fell on different sides of it. That is why the seeds disagreed (agreement 0.07 on two seed pairs).

### 4.4 What the pendulum energy is

For the simulated double pendulum (`pendulum.py`, unit masses and lengths, `g = 9.81`):

```
E = 0.5*w1^2 + 0.5*( w1^2 + w2^2 + 2*w1*w2*cos(theta1 - theta2) ) - 2*g*cos(theta1) - g*cos(theta2)
```

With no damping `E` is constant for a whole release (so its ICC is 1); it is the slow direction the method should find. With damping or real friction it decays slowly (real videos).

---

## 5. The stages, in order: what was done, what was seen, what was found, what was fixed

### Stage A (2026-10-12): one split, synthetic world
* **Observation data:** 4 fast + 4 slow hidden numbers scrambled by a nonlinear map into 16 observed numbers; 30,000 matched pairs.
* **Mechanism:** the encoder above (no consistency term), whitening, one difference-moment split.
* **Result:** slow-block R² 0.99, angle about 1°, gap 59–138 on 5 seeds; every control (shuffled pairs, no prediction, no whitening) failed as it should.
* **Fix:** the first run collapsed (R² 0.43). Adding **stop-gradient** and the **covariance penalty** (weight 0.04) removed the collapse. One control bound ignored chance level and was replaced after seeing the run (declared in the record).

### Stage B1 / B2 (2026-10-13/14): second split, then building the pairs
* **B1:** the second rung with ground-truth pairs: nesting angle about 1.3°.
* **B2:** can rung-2 pairs be built from the rung-1 representation alone? Clustering the invariant content gives pairs; cluster purity 0.83 on clean worlds, degrading as categories overlap (rung-2 angle 49–90° at the hardest settings).
* **Fix:** a purification step (drop pairs with large energy in the invariant directions) raised the rung-2 gap from 3.1 to 19.7 and pair validity from 0.83 to 1.00. Records: `docs/B2.md`, `docs/P9_REPORT.md`, `docs/STATUS.md`.

### Stage V (2026-10-20 →): the "video-first handshake"
The framework is applied to video with a sealed evaluator. Each item: question, result.

| ID | What was run | Result |
|---|---|---|
| **Handshake E31** | Simulated double pendulum, 150 releases, 3 seeds | **Certificate confirmed** (V ≤ 0.005, ICC 0.97–0.99, L 0.99–1.00, rollout 0.12–0.23; energy passes the same checker, angle and a constant fail on ICC). **Naming refuted** at 0.99: 0.786 |
| **Scaling probe B1** | 450 releases, 8000 steps | **Confirmed**: naming 0.97–0.98, seed agreement 0.976–0.981; the gain is a data and training effect |
| **Hierarchical E35** | Planted 5-level AR world | **Refuted as worded**: 1 rung against 4 (section 4.1) |
| **F1** | release-free "temporal-only" arm | **Refuted**: it equals the main arm; the discovery is identified redundantly by temporal slowness and by release grouping |
| **E36** | coupled two-block world | **Refuted as worded**: closure gate ratio 1.25–1.32 against 2.0 |
| **Columbia C1 / C1b** (1100 clips) | real clips, tracked energy | naming 0.88–0.90 (met); certificate partly met; flat baseline 0.38–0.48 |
| **Columbia C2** (100 videos, video-level split) | full protocol | naming 0.905 / 0.914 / 0.912; agreement 0.965–0.967; V ≤ 0.025, L 0.985, rollout 0.29–0.30. **Not confirmed**: ICC 0.685 and one flat-control seed at 0.73 |
| **C3** | confound check | ψ correlates 0.91 with total energy, 0.51 with kinetic, 0.55 with potential, **0.91 with local swing amplitude**; energy and amplitude are not separable on this data |
| **G2 / G3** | depth world; single and elastic pendulum (real) | depth: 3 / 2 / 0 cuts (ladder / single lag / shuffled), precision threshold narrowly missed; single 0.95, elastic 0.83 (real clips, grouping not recoverable) |
| **H1** | HF controlled pendulum | all four criteria met (naming 0.96–0.97, light correlation 0.07), but the ladder never cut and the shuffled arm equals the main arm: the coordinate comes from release grouping here |
| **R1** | ManiSkill, 32×32 gray MLP | untestable: the encoder did not even represent the cube (R² 0.04) |
| **N** | NUS double pendulum, 93 videos, no labels | **Not confirmed**: seed agreement 0.07 / 0.07 / 0.79; rollout 0.84–0.96; ICC 0.29–0.37 |
| **T1–T3** | lags, representation, data on NUS (5 variants × 3 seeds) | **None supported.** Lags (1, 4, 16, 64) worse than (8, 32); more frames of the same videos change little; half the videos give low rollout but disagreeing seeds (agreement 0.03) and a shuffled arm that cuts too (degenerate); conv 64×64 with more frames is nearest (cut on every seed, agreement 0.88, rollout 0.60–0.64) |
| **Diagnostic** | what is inside the NUS split | lighting is absent from the latent (readout R² ≈ −0.05); the variant block carries the fast detail (reach R² 0.39–0.52, motion 0.62–0.69); the 1-d core is a weak slow "activity level" coordinate (rank correlation about 0.5 with 60-frame windowed motion and height spread; between-video ICC 0.28–0.41) |
| **RL** | multi-rung ladder on ManiSkill PickCube, 64×64 RGB conv encoder, 200 episodes | **Not confirmed**: no cut on any seed or arm (first-family gap ratio 1.1–1.2). The gate was met (cube readout R² 0.73–0.78), but the latent holds almost nothing about the arm (R² ≈ 0) or the goal |

### Fixes and corrections made along the way

| Problem | What was changed |
|---|---|
| Latent collapse in Stage A | stop-gradient plus covariance penalty |
| Noise floor `c(n)` swallowed real eigenvalues; white-noise exceeded it | S1 redefined as "largest eigenvalue ≤ 5% of chance"; block size = largest gap ratio among cuts above that level (decisions D28–D30) |
| Nuisance was a gain/shift that the encoder could not absorb | nuisance changed to **additive illumination**; **consistency term** added to the encoder loss; latent set to 64-d (decisions D28–D32) |
| The Stage A gap bar (10) cannot be reached with neighbouring timescales that differ by only 2–10× | `γ_min = 2.0` for temporal worlds (D18) |
| Stale or drifted log artifacts | entry 134 and others declared **superseded** by amendment entries; `DECIDE 1–15` promoted to D19–D32; trigger-bit meaning fixed (D33) |
| Tests of the supervisor wrote into the real log | logged as an incident; chain logging only if a plan opts in |
| Columbia: 99th-percentile break threshold gave about 1% false breaks | replaced by a contrast test over divisors; verification with two camera angles |
| Single and elastic clips were not in temporal order | pre-registered fallback: release = clip (grouping caveat stated) |
| A run crashed on an array in JSON | array stripped; the partial file kept in `results/scaling/failed_attempt1` |
| Cube height is constant in PickCube | evaluator uses cube (x, y) only |
| Installing the simulator downgraded numpy; no GPU driver | isolated environment; software Vulkan (Mesa lavapipe) |
| Out of memory at 64×64 (arrays were float64) | per-release streaming standardization (same statistics to about 1e-16, tested) |
| My NUS write-up said the ladder "never cuts" | corrected from the result files: gap ratios 1.99 / 2.003 / 2.36 at lag 8 (cut on two seeds, none on one) |
| One over-strict test assertion (core dimension 64 on every seed) | assertion corrected, results untouched |

The discipline throughout: predictions and pass thresholds were written and hashed **before** each run (`docs/EVIDENCE.md`, `configs/*.criteria.sha256`), outcomes were appended without editing, every raw result is in a hash-chained log (`explog/chain.jsonl`), and `python experiments/audit_stage_v.py` checks all of it.

---

## 6. What the evidence supports, and what it does not

### 6.1 Strongest evidence
1. **Simulation:** the certificate passes on every seed; a coordinate with between-release variance share 0.97–0.99 is found and names energy at 0.97–0.98.
2. **Columbia real video:** 100 videos, no video shared between train and test: naming 0.91, seed agreement 0.97, V ≤ 0.025, L 0.985, rollout 0.30; the shuffled-pair control is clearly below (0.75–0.83), so temporal structure matters beyond release grouping.
3. **Planted multi-timescale worlds:** several rungs work exactly where the arithmetic says they should (depth world: 3 cuts).

### 6.2 Weak or missing
* **More than one rung on real data.** Never obtained: real video gives one 63-vs-1 cut at most.
* **NUS:** the pipeline did not find a stable coordinate; five attempted fixes did not change that.
* **Energy versus amplitude:** not separable on the real double pendulum (partial correlations about 0.5 both ways).
* **ICC ≥ 0.9** is not reached on any real data (energy decays inside real videos), so the registered certificate is partly unmet there.
* **The ladder versus a plain slow-feature direction:** they agreed in every test so far.
* **Robot data:** the encoder represents the cube but not the arm or goal, so there is nothing for the lag rung to split off.
* **Colour and camera angle:** never tested on a real invariance (the footage is gray; the robot test failed upstream).

### 6.3 What the split does and does not do (from the NUS diagnostic)
* The **lighting nuisance is removed by the encoder's consistency loss**, not by the spectral split: in the latent, two lighting versions of a frame are identical (difference 0.000 to 0.002) and a readout of the lighting coefficients gets R² ≈ −0.05. The rendering rung is therefore skipped (S1) on all real data.
* The **variant block** holds the fast detail, as intended: frames 8 apart are unrelated in it (1.01 on a scale where 1 is unrelated), and it carries most of the readable frame content (motion R² 0.62–0.69 against 0.64–0.81 for the full latent).
* The **invariant core** is a single direction that changes less (0.17–0.36 on the same scale) and persists to lag 128; it follows slow activity levels but reads out little instantaneous content. It is a weak slow coordinate, not a clean "law-level" feature.

---

## 7. Related work found (search summaries only; verify before citing)

* Slow feature analysis and its video variants: [steady feature analysis](https://arxiv.org/pdf/1506.04714).
* Static versus dynamic latent codes: [hierarchical VAE for video](https://arxiv.org/pdf/1612.04440), [C-DSVAE](https://arxiv.org/pdf/2110.12091).
* JEPA and slow features: [V-JEPA](https://arxiv.org/html/2404.08471v1).
* Slow modes with timescale gaps and lag choice (the same question as our lag 8 versus 16): [VAMPnets](https://www.arxiv-vanity.com/papers/1710.06012/).
* Pixels to Hamiltonians: [Hamiltonian Neural Networks](https://arxiv.org/pdf/1906.01563), [Hamiltonian Generative Networks](https://ar5iv.labs.arxiv.org/html/1909.13789).
* Identifiability from temporal structure: [time-contrastive learning](https://arxiv.org/abs/1605.06336).

What looks different here: a post-hoc spectral cut with hard nesting over a ladder of correspondence families, a certificate on the discovered coordinate, and naming only afterwards against a sealed table.

---

## 8. Open items and sensible next steps (none started)

1. A ladder starting at lag 16 on NUS (the per-lag table peaks near lag 16, not 8): a new registered run.
2. A conv run on NUS with the base data and a larger step budget, to separate representation from data (one conv seed was degenerate).
3. Make the robot encoder represent the arm (larger latent, longer training, stronger weight on the frame-difference channel, purposeful arm motion), then retry the multi-rung test.
4. Owner-gated: your own footage (live-capture test), and the Hugging Face robot datasets you mentioned for further robot tests.

---

## 9. Where things are

| What | Where |
|---|---|
| Engine (whitening, spectral split, hard nesting) | `src/isj/engine.py` |
| Ladder over families, max-ICC selector | `src/isj/temporal_ladder.py` |
| Encoder and training loss | `src/isj/video_encoder.py`, `src/isj/encoder.py` |
| Certificate | `src/isj/quotient_audit.py` |
| Naming, controls, probes | `src/isj/handshake_eval.py` |
| Planted worlds, pendulum simulator and renderer | `src/isj/worlds.py`, `src/isj/hier.py`, `src/isj/pendulum.py` |
| Runs | `experiments/run_*.py` |
| Frozen criteria | `configs/*.yaml` with `*.criteria.sha256` |
| Predictions and outcomes (never edited) | `docs/EVIDENCE.md` |
| Paper-style summary of all results | `docs/PAPER_RESULTS.md` |
| Run log (hash-chained) | `explog/chain.jsonl`, `docs/STATUS.md` |
| One-command checks | `python -m pytest -q`, `python experiments/audit_stage_v.py` |
