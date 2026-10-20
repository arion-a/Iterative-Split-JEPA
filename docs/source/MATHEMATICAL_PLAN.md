# MATHEMATICAL_PLAN.md — full model and protocol for the three unification moves

STATUS: specification only. Nothing in this document is executed here.
All predictions are registered BEFORE their runs per docs/EVIDENCE.md
discipline. This document is in sync with: docs/SYNTHESIS.md (the four
certificates S/D/C/T and conjecture C6), docs/UNIFICATION_PLAN.md (moves,
weeks, unification points UP1-UP4), docs/FORMAL_TRACK_SYNC.md (the
object mapping between tracks), docs/EVIDENCE_RUN_HIERARCHY.md (arms,
worlds), docs/STOP_CRITERIA.md (S1-S5), docs/DEPTH_METRICS.md (Rungs
battery). Where numbering collides, the REGISTRY MAP in Sec 6 is
authoritative.

=====================================================================
MOVE 1 — THE HANDSHAKE: positive double-pendulum quotient
=====================================================================

1.1 The dynamical system
Planar double pendulum, Hamiltonian, state s = (theta1, theta2,
omega1, omega2) in S = T^2 x R^2. Dynamics s_{t+1} = F(s_t) by a
symplectic integrator (velocity Verlet, step h fixed), with integrator
tolerance tau_int recorded (their package's convergence check:
max state discrepancy ~1e-15 across step halvings).

Total energy E(s) = T(omega) + V(theta) is a CONSERVED QUANTITY:
E(F(s)) = E(s) exactly (up to tau_int). This is what makes q_energy a
dynamically valid quotient BY CONSTRUCTION — the positive case.

1.2 The three candidate abstractions (inputs to the checker)
q_angle(s)   = (theta1, theta2)                [expected INVALID]
q_energy(s)  = E(s)                             [expected VALID: V=0]
q_learned(s) = psi(s)                           [the handshake case]

where psi is obtained WITHOUT state access, as our mechanism would:
  o_t = h(s_t)          observation map (bob positions first; pixels
                        are the later, video-stage variant)
  r_t = phi(o_t)        encoder (for the spec: a small trained net on
                        (o_t, o_{t+1}) prediction + whitening; frozen)
  M = E[Delta Delta^T]  difference moments over TEMPORAL pairs
                        (t, t+1) on a long trajectory (Takens-valid:
                        the reconstructed flow's slowest eigenfunction
                        tracks E for this near-integrable system)
  psi = the slowest nontrivial eigenfunction, quantized at tolerance.
Observation-only: no (theta, omega) enters the construction of psi.

1.3 The checker (their object, our wrapper — UP1)
Violation rate over held-out matched pairs:
  P_q(delta_q, eps) = { (s_i, s_j) : ||q(s_i) - q(s_j)|| <= delta_q }
  V(q) = |{ (i,j) in P_q : ||q(F(s_i)) - q(F(s_j))|| > eps }| / |P_q|
with delta_q, eps frozen before the run; eps >= 5 tau_int.
NOTE: their Stage-1 exact boundary theorem — for fixed deterministic F,
V(q) = 0 iff q is a semiconjugacy on the tested support — is the
certification standard; tau_int-scaled eps makes it continuous-valid.

1.4 Registered predictions (E31, frozen before running)
E31a: V(q_energy) = 0 within eps on all 3 seeds.
E31b: V(q_angle)  > 0.5 (reproduction; sanity floor).
E31c: V(q_learned) <= eps-V floor AND |corr(psi, E)| >= 0.99 on the
      held-out trajectory (3 seeds).
Protocol: 200 matched pairs per q per seed (their convention);
everything logged to results/handshake/.

DONE: theory certifies our mechanism's output on one real dynamical
system, in both directions (their checker on our psi; our psi matches
the theory's conserved object).

=====================================================================
MOVE 2 — HIERARCHICAL RUN: the ladder tested against the theory
=====================================================================

2.1 World (in sync with EVIDENCE_RUN_HIERARCHY + H-JEPA grounding)
Latent z = z_1 .. z_5 (blocks of 4), block-AR dynamics
z_{t+1} = A z_t + eps_t, A = diag(a_1..a_5) I_4-blockwise,
a = (0.20, 0.50, 0.75, 0.90, 0.95): adjacent timescale ratios
2.5, 1.5, 1.2, 1.08 — deliberately SPANNING the 2x spectral-gap
threshold (their Fig-5 boundary; our E35 tests it).
Observation o = g(z): paper-style 4-layer coupling scrambler.
Planted state counts 240 -> 60 -> 20 -> 6 -> 3 (depth battery).

2.2 Arms (matched): ARM-S (SplitJEPA single split = rung 1 only),
ARM-L (ladder: automated loop to S1-S5 termination), ARM-H (H-JEPA
recipe: end-to-end MLP upper levels, stride 2, SIGReg, NO
correspondences), ARM-F (full features), ARM-C (shuffled control).
Oracle hierarchy (ground-truth rungs) as diagnostic upper reference
for the theory's "oracle vs discovered" comparison.

2.3 The four-certificate rung gates (S/D/C/T — from SYNTHESIS.md)
After rung k's split, certify:
(S) STATIC — existing gates: leakage at permutation null; gap >
    gamma_min; rank check; nesting (D10 reference); coarsening defect
    in bootstrap null.  [empirical track]
(D) DYNAMIC — semiconjugacy in continuous form:
    E_k = E_z || q_k(F(z)) - F-hat_{k}(q_k(z)) ||^2,
    F-hat_k a per-level transition model (2-layer MLP, matched);
    PASS if E_k <= eps_D (frozen). Equivalent discrete check: the
    wrapper's V(q_k) at tolerance on held-out pairs.  [formal track]
(C) COMPOSITION — rollout closure and stability:
    e_k(K) = E || F-hat_k^K(q_k(z)) - q_k(F^K(z)) ||,
    L_k = sup_j (e_k(j+1)/e_k(j)) estimated by log-slope fit;
    PASS if L_k < 1 and e_k(K_k) <= eps_C at the rung's native
    horizon K_k (timescale-derived, frozen).  [formal track]
(T) TRANSPORT — NIM: probe for level-k labels under shifts of every
    faster level; PASS if drop <= frozen tolerance; plus the dynamic
    version: horizon loss under shift smallest at the core.  [both]
Gate semantics align with STOP_CRITERIA: (D)-fail at full rank =
recall-loss (S3 terminate); (C)-fail = stability boundary (their
Stage-3 curve; report L_k, terminate if unrepairable).

2.4 What the run tests of the THEORY (boundary predictions registered)
E35 timescale-gap threshold: measured RUNGS equals the number of
    levels above the 2x threshold (4 by construction); ARM-H's
    usable depth tracks the same count (its phenomenon, our boundary).
E36 spectral-/=>-dynamic gap: at least one rung with perfect (S) and
    failing (D) is found at the sub-threshold levels, and the gate
    catches it (their Stage-2 theorem, demonstrated in our setting).
E37 stability boundary: rungs' L_k partition {pass, boundary, fail}
    matching their Stage-3 curve (L=0.8/1.0/1.2 analogy) at fixed
    local defect.
E38 consistency: (S)-pass + (D)-fail occurs ONLY at the named bridges
    (contamination / within-jitter / rank / gap — their Stage-2
    variants vocabulary).

2.5 Depth battery + reach (from DEPTH_METRICS + the reach concept)
States-per-Rung, Bits-per-Rung, RUNGS, Abstraction Diagonal, plus
H_k(eps) faithful-horizon curves per level — the two-curve figure
(states collapse / reach grows) is the paper's central figure, testing
C6's empirical core (H grows where D,C hold; stalls at bridge failures).

=====================================================================
MOVE 3 — PAPER UNIFICATION (structure + content sources)
=====================================================================

Sec 2 THEORY   [formal track]: valid quotients (semiconjugacy; the
               checker; V(q)); the representation->quotient bridge
               (Stage-2 conditions + the spectral-/=>-dynamic theorem);
               composition with stability (Stage-3 bound); boundary
               conditions table; C6 stated.
Sec 3 MECHANISM[empirical track]: prediction fixes content,
               correspondence fixes partition, iteration builds the
               ladder; the four-certificate gates as rung acceptance.
Sec 4 EXPERIMENTS[both]: Move 1 handshake figure; parity vs SplitJEPA;
               Move 2 hierarchical tables + reach figure; boundaries
               AS MEASURED (E9/E13/E18/E20 with premise-vs-theorem
               framing); NIM real-data row.
Sec 5 BOUNDARIES[shared]: guarantees vs measurements vs open items
               (nonlinear lift C1b; learned-encoder transport; Lean
               uncompiled; oracle-vs-discovered gap quantified).

Unification points: UP1 checker wrapper (src/isj/quotient_audit.py);
UP2 gates call (D),(C); UP3 registry entries; UP4 this document's
skeleton.  Stays separate: Lean drafts; 3,645-system enumeration
(supplementary); spectral-K option (off).

=====================================================================
6. REGISTRY MAP (authoritative; resolves all collisions)
=====================================================================
E1-E20   as consolidated in docs/EVIDENCE.md (E1-E8 theory-derived,
         E9 nesting/budget REFUTED, E10 nesting definition [human
         ruling], E11 encoder floor [reclassified: definitional],
         E12/E14 gap-fix CONFIRMED, E13 REFUTED->revised model,
         E15-E17 texture/leakage battery, E18 spectral-K REFUTED,
         E19 world geometry, E20 gap criterion blind).
E21-E24  MINIMAL EVIDENCE RUN (docs/EVIDENCE_RUN_MINIMAL.md):
         identity-reliance, shift robustness, parity, controls.
E25-E30  PAPER 1 comparison + real-data NIM (docs/PAPER1_COMPARISON):
         parity, T2 delta, T3 horizon, W3 deep ladder, controls,
         NIM/transport set.
E31      HANDSHAKE (this document, Sec 1.4): a/b/c as above.
E32-E34  DEPTH BATTERY calibration (docs/DEPTH_METRICS.md): D=L,
         FD=L, DSS=planted counts (STOP_CRITERIA E35-E38 there are
         RENAMED to E39-E42 below).
E35-E38  [REASSIGNED] -> E39-E42  STOP CRITERIA (docs/STOP_CRITERIA):
         E39 S1 fires at L; E40 cross-domain merge; E41 budget
         allocation; E42 domain split.
E35-E38  THIS DOCUMENT (Move 2): timescale threshold; spectral-/=>
         dynamic gap; stability boundary; four-certificate
         consistency.
C6       THE REACH THEOREM (conjecture; docs/SYNTHESIS.md).
Hand to the agent with: "Adopt docs/MATHEMATICAL_PLAN.md as the
unified spec; apply the Sec 6 registry map; do not run anything whose
prediction is not registered."


=====================================================================
GOVERNING PRINCIPLE (added 2026-10-19; supersedes Move 1 Sec 1.2 framing)
=====================================================================
PHYSICS VARIABLES MAY APPEAR IN EXACTLY TWO PLACES, NEVER IN THE
FRAMEWORK:
  (1) the world GENERATOR that renders observations (the simulator is
      nature; video vectors are its output);
  (2) the EVALUATION layer that certifies and names (oracle, never fed
      back into the framework).
The framework DISCOVERS unnamed patterns from video vectors. Names
(energy, momentum, ...) are EARNED post-hoc: assigned only after a
discovered pattern passes certification and correlates with the quantity
physics names by that word. Discovery-first, naming-second, always.

=====================================================================
MOVE 1 — REVISED HANDSHAKE (video-first, three epistemic stages)
=====================================================================
STAGE A  DISCOVERY (unsupervised, physics-free).
  Input: VIDEO VECTOR — pixel frames rendered by the pendulum simulator
  (the generator; allowed). NO theta, omega, or energy anywhere.
  Pipeline: encoder phi trained self-supervised on the video (latent
  prediction + whitening); difference moments over TEMPORAL pairs
  (t, t+1) on long trajectories; the ladder's slow latent coordinate
  psi (slowest nontrivial eigenfunction, quantized). Output: psi, an
  UNNAMED pattern.

STAGE B  CERTIFICATION (theory, physics-free).
  Checker on video-derived states: V(psi) ~ 0 at frozen tolerance;
  rollout closure e(K); stability factor L < 1. Dynamic validity of
  the DISCOVERED pattern, established without physics.

STAGE C  NAMING (oracle, evaluation-only).
  Simulator state enters ONLY here: corr(psi, E(s)) on held-out
  trajectories. If ~1, the name "energy" is earned and assigned from
  outside. The evaluator-side candidates q_angle (expected V>0) and
  q_energy (expected V=0) serve ONLY as checker references/controls;
  neither is ever an input to the framework.

REGISTERED PREDICTIONS (replace E31a-c of Sec 1.4):
  E31c' V(psi) <= floor AND L < 1, with NO physics variable in the
        pipeline (the certificate is itself physics-free).
  E31d  corr(psi, E) >= 0.99  (naming earned; 3 seeds).
  E31e  Ladder terminates at the energy level: S1 fires below it; fine
        levels show SHORT reach — the framework discovers where
        predictability ends in a chaotic system (chaos signature).
  E31f  (structure, informational) recurrence/period content of psi
        matches the integrable-time structure (cycle-scale pattern).

FUTURE (registered, not in this run):
  E43  UNIVERSALITY: the same discovered pattern — nameable as energy —
       is found in videos of DIFFERENT physical systems (pendulum,
       spring, orbit). The unified-pattern hypothesis, made falsifiable.
