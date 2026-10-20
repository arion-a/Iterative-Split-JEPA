# LIVE_DATA_PLAN.md — handshake + certificates on real data, from scratch

Objective: reproduce the three-stage handshake (DISCOVERY -> CERTIFICATION
-> NAMING) on LIVE video, no simulator, and present it as the real-data
section of Paper 1. The synthetic pendulum remains the development
harness; this plan assumes nothing from it except its lessons
(E15 ceiling gate; checker discipline; frozen predictions).

=====================================================================
1. DATASETS (two tiers)
=====================================================================
TIER 1 — RECORDED LIVE (primary; full control, fastest path)
  Subject: a physical pendulum you film yourself.
    - Single pendulum (near-integrable: clean periodic structure).
    - Double pendulum (chaotic: the conserved-invariant test).
  Capture protocol (frozen):
    - Camera: fixed tripod, 60fps minimum, 1080p; static background;
      two colored markers on the bobs (for EVALUATOR tracking only).
    - Calibration frame: ruler in shot once (pixel->meter scale).
    - Initial conditions: >= 30 distinct releases spanning small-angle
      to chaotic regimes (angle/amplitude diversity = the cross-motion
      variation the discovery needs).
    - Duration: >= 20 s per release; train/val/test split by release.
    - Total: ~15-20 min of video. This is the whole dataset.
  Evaluator ground truth (naming/certification only, never fed to the
  framework): marker-tracked bob positions per frame -> velocities by
  differencing -> energy E(t) and angles. Standard color tracking, 50
  lines, fully reproducible.

TIER 2 — PUBLIC LIVE (generality extension; optional for Paper 1)
  DROID subset (or Open X-Embodignment): real robot video WITH
  proprioception. No clean conservation law; use for the TRANSPORT
  certificates and the reach/NIM rows, not for the energy naming.
  Naming there = proprio-derived quantities (gripper pose, object
  position if annotated).

=====================================================================
2. STAGE A' — DISCOVERY ON LIVE VIDEO (with the encoder fix as a GATE)
=====================================================================
LESSON FROM SYNTHETIC ATTEMPT 1: pure next-step latent prediction does
NOT preserve invariants (E15 ceiling R^2 = 0.35). Therefore:

ENCODER SPEC (frozen before capture):
  Input: clip descriptor [x_t ; x_t - x_{t-1}] (physics-free).
  Objective: latent prediction (multi-step) + CONSISTENCY across
  nuisance augmentations as the correspondence surrogate (two augmented
  views of the same clip = matched pair: share content, vary
  crop/color/lighting). This is the universal pairing source on live
  data and supplies the invariance pressure the synthetic encoder
  lacked. Plus variance regularizer.
  GATE (E15 ceiling, frozen threshold): a linear probe latent -> E
  (evaluator tracking) must reach R^2 >= 0.9 on the TRAIN releases
  before discovery proceeds. If it fails: remedy path (more capacity,
  stronger consistency weight, longer clips), maximum two remedies,
  then report the ceiling failure as the finding (that is a legitimate
  Paper result: "what live-data invariants survive off-the-shelf
  self-supervision").

DISCOVERY: whiten -> difference moments over (augmentation pairs +
  temporal pairs) -> invariant coordinate psi (conserved-along-motion,
  varying-across-releases selector). Output: unnamed pattern.

=====================================================================
3. STAGE B — CERTIFICATION ON VIDEO (no simulator)
=====================================================================
  V(psi): matched pairs = frames with |psi_i - psi_j| <= delta (frozen);
  successors = the video's own future frames (t + k); check
  |psi(t+k)_i - psi(t+k)_j| <= eps. Violation rate on held-out releases.
  Rollout closure + stability factor L from a psi-transition model.
  CONTROLS (evaluator-side, as in the synthetic spec):
    q_tracked-energy (expected V ~ 0; positive reference),
    q_position-only = (x1,y1,x2,y2) discarding velocities
    (expected V > 0 on the double pendulum: their angle-only analog —
    merges states with different velocities).
  Both controls use TRACKED quantities (evaluation layer), never the
  framework's inputs.

=====================================================================
4. STAGE C — NAMING (earned, post-hoc, oracle-only)
=====================================================================
  corr(psi, E) on held-out releases; frozen threshold 0.98 (live data
  noisier than synthetic 0.99). If earned: the discovered pattern is
  nameable as energy — physics' vocabulary applied after the fact.
  Report the full pipeline's physics-freedom explicitly: every input
  to the framework is a pixel vector.

=====================================================================
5. REGISTERED PREDICTIONS (live-data series, frozen before capture)
=====================================================================
  E44 ceiling gate passes (R^2 >= 0.9) within two remedies.
  E45 V(psi) <= floor AND V(q_position-only) > 0.5 on the double
      pendulum, on held-out releases.
  E46 corr(psi, E) >= 0.98 on single AND double pendulum releases
      (single: periodic regime; double: chaotic).
  E47 termination/depth: ladder depth = 1-2 on pendulum video (energy
      level then S1); fine levels show short reach (chaos signature).
  E48 (Tier 2, optional): reach/NIM rows on DROID with proprio naming.

=====================================================================
6. PAPER PRESENTATION (where each artifact lives)
=====================================================================
  FIG 1 (motivating): trajectory of psi over a chaotic release, colored
      by value, beside the tracked-energy curve — visually the same
      pattern; caption states discovery was physics-free.
  FIG 2 (handshake scatter): psi vs tracked E across all held-out
      releases (single + double), with the verdicts table
      (V(psi) ~ 0 / V(position-only) high).
  FIG 3 (reach): faithful-horizon curve on live video — psi rolls out
      far; fine levels roll out short.
  TABLE (NIM row, existing real-data section): augmented by the
      handshake verdicts; this section now EXCEEDS the SplitJEPA
      evidence standard (simulated robotics) on REAL data.
  SEC 5 scope: single/double pendulum are structured physics; broader
      natural video remains future work (E43 universality across
      systems stays registered).

=====================================================================
7. EXECUTION
=====================================================================
  Human (1 day): capture per protocol; run the tracker; upload frames.
  Coding agent: Stage A' training + gate; Stage B checker + controls;
  Stage C naming; figures. Reuse src/isj modules; new
  experiments/live_handshake.py; results under results/live_handshake/.
  Registry + STATUS updated per run. Nothing runs whose prediction is
  not registered.
