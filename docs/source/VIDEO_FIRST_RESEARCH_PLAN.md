# Motion to Mechanism: Revised Video-First Experimental Plan

**Revision date:** 19 October 2026  
**Purpose:** Align the four-stage mathematical programme with the intended end-to-end hypothesis: discover increasingly abstract, predictive structure from video pixels without supplying physical variables such as energy, velocity, momentum, or mass to the learner.

## 1. The intellectual commitment

The learner receives video observations, not a table of physical state variables. A video is represented as an ordered tensor

\[
X_{1:T}\in[0,255]^{T\times H\times W\times C},
\]

or, for a frame-wise pixel vector,

\[
x_t=\operatorname{vec}(X_t)\in\mathbb R^{HWC}.
\]

The sequence axis must be preserved: collapsing the entire clip into one unordered vector would destroy the temporal ordering required to discover recurrence and dynamics. A video encoder or JEPA-style context encoder maps clips to latent states, and the iterative SplitJEPA/spectral procedure proposes nested invariant/variant structure from data-derived correspondences.

**Forbidden as discovery inputs or training targets:** simulator angles, angular velocities, energy, momentum, masses, lengths, gravity, or hand-authored phase labels. Such values may be retained in a sealed evaluation table and revealed only after the learned representation, splits, thresholds, and predictions are frozen. Post-hoc comparisons can then ask whether a discovered latent factor corresponds to a familiar physical quantity; they must not drive discovery.

## 2. What quotient spaces mean in this version

A quotient is not initially `Q_energy`, nor any other quotient defined using a named physical variable. It is an equivalence relation induced by a candidate learned abstraction. For a learned representation `z_t` and rung map `q_k`, the candidate abstract state is `q_k(z_t)` or a stable cluster/partition of that representation.

The Stage 1 condition remains the mathematical test:

\[
q_k(z(s_1))=q_k(z(s_2))\implies
q_k(z(F_a(s_1)))=q_k(z(F_a(s_2))).
\]

In the video experiment, concrete states `s` and transitions `F_a` are not supplied to the learner. They are available only in a simulator-side audit environment. Operationally, we test the learned abstraction by asking whether video-derived states that it merges remain predictively equivalent under the same observed continuation or controlled simulator intervention. The simulator's hidden state must not leak into training, pair construction, model selection, or early stopping.

## 3. End-to-end pipeline

1. **Pixels in:** record rendered double-pendulum videos as RGB frame sequences. Keep frame order and sampling times. Use fixed, documented resizing/normalization; preserve raw-frame provenance.
2. **Self-supervised representation:** train a video JEPA-style encoder/predictor on clips. Predict future/target latent representations rather than using physics labels. Keep camera/render nuisance variation in the dataset so the model cannot succeed only by memorizing appearance.
3. **Data-derived correspondences:** start from temporal adjacency, overlapping clips, repeated visual configurations, and independently sampled trajectories. At deeper rungs, construct correspondence candidates from the preceding rung's surviving representation, following the iterative SplitJEPA idea. Never construct these pairs using known angles, energy, or other oracle state variables.
4. **Spectral split:** form matched representation differences `Δr` from the data-derived pairs; estimate `M_k = E[Δr Δrᵀ]`; inspect its eigenspaces/gaps; split variant and invariant components subject to rank, excitation, and stability checks. A spectral gap is evidence about the chosen correspondence family, not proof of causal or physical meaning.
5. **Iterate:** pass only the surviving/invariant output to the next rung's correspondence builder. Freeze each rung before using it to construct the next. Stop when the preregistered rank/identifiability gate fails.
6. **Predict:** fit rung-specific latent predictors at preregistered horizons. Evaluate on held-out trajectories, not randomly held-out adjacent frames from training trajectories.
7. **Audit after freeze:** reveal simulator state and physical parameters only after model selection is complete. Test whether latent variables or combinations align with known quantities and whether their inferred relations remain predictive under held-out initial conditions and parameter changes.

## 4. Four stages, reinterpreted without changing their mathematical roles

### Stage 1 — Formal quotient criterion

**Role:** establish what any candidate abstraction must satisfy. The abstraction is a mathematical map, not a physical variable supplied to the learner. The current exact checker and double-pendulum angle-only counterexample remain valid as theorem/checker controls, but they do not constitute a learned video abstraction experiment.

**Empirical connection:** after the learned rung maps are frozen, evaluate whether the equivalence classes induced by the latent abstraction preserve successor/predictive classes. If the learned classes merge future-distinguishable cases, Stage 1 rejects that particular abstraction.

### Stage 2 — Pixel-to-latent representation and iterative splitting

**Role:** test whether data-derived correspondences and spectral splitting recover stable, repeatable latent factors from pixels. The central scientific risk is identifiability: without sufficiently varied trajectories and valid correspondence families, many different latent parameterizations may fit the same video distribution.

**Primary discovery question:** do the learned splits recur across seeds and held-out trajectories, and do their outputs retain predictive information at their designated timescales? Use a prespecified subspace/partition stability statistic as the stage's primary split diagnostic. Do not interpret the factors as energy or momentum yet.

**Essential controls:** shuffled temporal/correspondence pairs (should destroy meaningful variation structure); a no-split/base-JEPA baseline; a known synthetic video-like system with planted latent factors to validate the implementation. These controls test the extractor, not the physical meaning of real-video factors.

### Stage 3 — Predictive sufficiency and composition

**Role:** test whether the discovered rung states can predict their own future latent targets and whether predictions compose over multiple steps. Use a single preregistered primary score: normalized held-out latent prediction error at a designated horizon, compared with a flat/base representation and shuffled-split control. Report the error curve over horizons as a diagnostic, not as a fishing expedition for a favorable horizon.

The learned hierarchy is useful only if it adds predictive value beyond a flat baseline under the same data, capacity, and evaluation budget. Do not assume that every deeper rung must improve every horizon; a rung may target a slower or more invariant timescale. Require improvement at its preregistered horizon and no unacceptable loss at the task's declared horizon.

### Stage 4 — Failure boundaries of the end-to-end discovery process

**Role:** test where the assumptions fail and trace propagation. Keep the existing exact quotient, spectral-bridge, and rollout boundary tests as mathematical controls. Add the end-to-end video tests only after the pixel-to-latent pipeline exists. For each failed rung, distinguish: (a) insufficient/invalid correspondence variation, (b) unstable or non-identifiable spectral split, (c) abstraction merges future-distinguishable video states, and (d) local predictive defects amplified during rollout.

Stage 4 is not passed merely because a deliberately coarse hand-built abstraction fails. The end-to-end claim requires evidence that the **learned, video-derived** abstractions pass the corresponding tests on held-out data, plus boundary controls that demonstrate the tests can detect failure.

## 5. Double-pendulum video protocol

### Data construction

Render a family of double-pendulum videos from many initial conditions. Vary initial conditions substantially; include held-out trajectory seeds and, in a separate generalization split, held-out physical parameter settings. Vary camera viewpoint, background, lighting, texture, and rendering style in controlled arms so appearance cannot be the only stable shortcut. Keep all simulator state and physical parameters in a separate audit file keyed by opaque clip ID.

Recommended split: train/validation/test by whole trajectory, not by frame. The final test set must include initial conditions not seen in training. If testing transfer across mechanisms, hold out parameter combinations as a separate test, not mixed into ordinary held-out trajectories.

### Discovery-time inputs

`video_id`, ordered frames/pixel tensors, frame rate/time index, and optionally a declared camera/render grouping for nuisance-control analysis. If grouping is used for training, it must describe observation-generation conditions only; it must not encode physical state or mechanism labels. Do not pass simulator coordinates, velocities, energy, momentum, masses, lengths, or gravity into the encoder, split procedure, correspondence builder, loss, hyperparameter selection, or stopping rule.

### Post-freeze audit only

After all model decisions are frozen, join clip IDs to simulator ground truth. Evaluate latent-factor alignment with angle, angular velocity, energy, momentum-like quantities, and physical parameters as *interpretation targets*, not training targets. Test whether relationships found on training trajectories predict held-out trajectories and parameter regimes. A post-hoc correlation is not enough: check held-out predictive sufficiency and invariance to camera/render nuisance.

## 6. Hidden recurrence and higher abstraction

The proposed discovery target includes repeated patterns that recur only after multiple oscillation cycles or at particular temporal lags. This must be operationalized without providing cycle phase labels. Compute latent trajectories and recurrence structure from learned states: identify repeated neighborhoods or lagged similarity patterns on training data, freeze the discovered lag/structure, and test whether it recurs in held-out trajectories. Do not select a lag after examining final test outcomes.

A discovered recurring pattern is a candidate latent regularity, not automatically a conserved quantity or causal mechanism. Its interpretation is strengthened if it (i) repeats across initial conditions and camera nuisance, (ii) supports future prediction, and (iii) continues to organize trajectories when mechanism parameters are changed. Only after these tests should the latent structure be compared with named physics quantities.

## 7. Chaos and the meaning of prediction

Do not require indefinite exact frame-by-frame prediction of a chaotic double pendulum. Chaotic sensitivity makes long-horizon point predictions depend strongly on initial-state precision and model error. Preregister a short/intermediate horizon for pointwise latent prediction, and assess longer horizons using appropriate distributional or structural criteria (for example, recurrence statistics or attractor-level behavior) in a separately specified experiment. The model must be compared under equal initial observation and compute conditions. A failure at long horizon is not alone proof that no mechanism was learned; conversely, matching a short trajectory is not proof of mechanism discovery.

## 8. Primary metrics and controls: keep the experiment legible

- **Stage 2 primary diagnostic:** split/subspace stability across seeds and held-out trajectory resampling, with the stability definition and threshold frozen before evaluation.
- **Stage 3 primary metric:** normalized held-out latent prediction error at one preregistered horizon, with base-JEPA/flat-latent and shuffled-split controls.
- **Stage 1/4 quotient check:** within-class successor/predictive violation rate for the learned abstraction, with a tolerance frozen from numerical and representation noise on validation data.
- **Essential controls:** known-valid and known-invalid finite quotient; shuffled correspondences; no-split baseline; nuisance-only render variation; full-state simulator audit as a sealed evaluation reference; numerical convergence of the simulator.

Do not combine these into one composite score. Each stage has a different claim and therefore a different defining measurement. Secondary statistics should be reported only if they diagnose a preregistered failure mode.

## 9. Interpretation ladder

1. **Pixel prediction works:** the model predicts target representations; this alone may reflect visual/motion regularity.
2. **Stable split:** iterative spectral structure repeats across seeds/data splits; this establishes representation stability, not physical semantics.
3. **Predictive abstraction:** the learned rung supports held-out future prediction and passes quotient-consistency checks within the tested domain.
4. **Mechanism-related transfer:** latent relations remain useful across unseen initial conditions and controlled changes in mechanism parameters, without those parameters being training labels.
5. **Post-hoc physical interpretation:** latent factors/relations align with known physical quantities or laws on a sealed audit set. This is evidence for interpretation, not proof of unique recovery of the universe's complete mathematical description.

A positive result at one level does not automatically imply the next.

## 10. Current implementation status

**Already implemented:** exact quotient theorem/checker, synthetic spectral/stability bridge tests, composition/rollout bounds, finite and double-pendulum state-space boundary controls.

**Not yet implemented or executed:** video rendering dataset, raw pixel vectorization on a real video corpus, trained video encoder/JEPA, data-derived iterative SplitJEPA on those videos, learned latent recurrence analysis, learned-rung prediction benchmarks, or post-hoc ground-truth physics audit. No result in the existing package should be described as evidence that the video-first mechanism-discovery hypothesis has passed.

The immediate next experiment is therefore not another state-space quotient counterexample. It is the smallest reproducible **pixel-to-latent discovery pilot** with a rendered double-pendulum dataset, a no-split JEPA baseline, one split rung, shuffled-correspondence control, and held-out latent prediction test. Expand to deeper rungs only after this pilot passes its gates.
