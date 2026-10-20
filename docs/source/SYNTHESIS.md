# THE SYNTHESIS — one framework, two branches

## 1. The unifying object

A DYNAMICALLY CERTIFIED ABSTRACTION LADDER is a filtration of quotient
maps q_1, q_2, ..., q_L together with latent transitions F-hat_{l,a},
such that FOUR conditions hold at every level:

  (S)  STATIC CERTIFICATION (empirical track):
       spectral identification — the rung's subspace is recovered from
       matched-pair moments with sufficient variation, spectral gap,
       measured leakage.  [our rung gates]
  (D)  DYNAMIC CERTIFICATION (formal track):
       q_l is a semiconjugacy — q_l(F_a(s)) = F-hat_{l,a}(q_l(s));
       merged states have merged successors; V(q_l) = 0 / E_l at tolerance.
  (C)  COMPOSITION CERTIFICATION (formal track):
       q_l preserves composition; rollout error is controlled by the
       stability factor L_l < 1 at the rung's horizon.
  (T)  TRANSPORT CERTIFICATION (both tracks):
       the same certificates hold across nuisance contexts
       (their cross-context consistency; our NIM).

The empirical branch CONSTRUCTS candidates and measures (S),(T).
The formal branch DEFINES (D),(C) and proves when (S) does or does not
imply them. The ladder is the first mechanism that can hold ALL FOUR.

## 2. The generator/evaluator split

  GENERATOR (learning):  prediction fixes content, correspondence fixes
  partition, iteration builds the filtration.  Output: candidate rungs.
  EVALUATOR (theory):    the quotient checker + rollout audit certifies
  each candidate as (D),(C); the audits report where it fails and WHY
  (which bridge condition broke).  Output: certificates + boundaries.

This division of labor is the architecture: theory specifies what must
be preserved; learning discovers candidates; evaluation certifies. No
single component does all three — and that is the framework's strength,
because each part is independently replaceable and independently testable.

## 3. The central theorem-shaped question (C6 — the reach theorem)

Under what conditions does quotienting a dynamical system by fast or
task-irrelevant distinctions INCREASE faithful prediction horizon while
preserving the dynamics of the variables that matter?

Formally: for the filtration above, when is H_{l+1}(eps) > H_l(eps)
at every level, with E_l, C_l small?  The answer has three parts,
one from each ingredient:

  INGREDIENT (formal):   the quotient must remove only distinctions
  irrelevant to the target dynamics (semiconjugacy); removed distinctions
  that affect successors destroy validity (Stage-1 boundary).
  INGREDIENT (empirical): the split must recover the intended subspace
  with sufficient variation and gap (Stage-2 bridge); spectral evidence
  alone is insufficient — the dynamic certificate is required.
  INGREDIENT (both):     the latent transition must be contractive
  enough to roll out (Stage-3 stability); and the context must not
  reintroduce the removed distinctions (transport).

C6 is open. The hierarchical run is its first empirical test; the
boundary theorems are its partial characterizations.

## 4. The three-stage pipeline as the operational form

  STAGE 1  IDENTIFY      (empirical):  recover candidate rungs from data.
  STAGE 2  CERTIFY       (formal):     check each rung against (D),(C).
  STAGE 3  DEPLOY/REFINE (both):       certified levels feed planners /
                                       probes / transport tests; failures
                                       route back with a named cause.

The failure boundaries are not accidents; they are the three known
bridge gaps, each with a designed detector:
  (S)->(D) gap: spectral-perfect but dynamically invalid [Stage 2].
  (D)->(C) gap: locally valid but unstable under rollout [Stage 3].
  context gap: valid in-distribution, fails under shift [transport].

## 5. What the synthesis predicts (register before the unified run)

E31  HANDSHAKE: the ladder's slowest rung on the double pendulum passes
     the quotient checker (V=0) AND is the energy-like mode.
E32  CONSISTENCY: at every rung where (S) passes, either (D) passes OR
     the failure mode is one of the three named bridges (audited).
E33  REACH: H_l grows with level wherever (D),(C) hold; growth stalls
     exactly where a bridge fails (boundary visible in the curves).
E34  CROSS-TRACK: every certificate in the formal package maps to a
     measured artifact in the empirical run (no orphan theorems).

## 6. Paper skeleton (one paper)

  Sec 2  Theory: dynamically valid quotients; the three bridges;
         composition/stability; the reach theorem statement (C6).
  Sec 3  Mechanism: the ladder (prediction/correspondence/iteration);
         the four-condition certification as rung gates.
  Sec 4  Experiments: handshake (pendulum); hierarchical run (P1-P5,
         E25-E30); boundary demonstrations (E9/E13/E18/E20 with
         premise-vs-theorem framing); NIM row.
  Sec 5  Boundaries: what is guaranteed, what is measured, what is open.

The correspondence table (docs/FORMAL_TRACK_SYNC.md) is the spine;
every section cites both halves through it.
