# Minimal claims: what the four tests showed (E38-E41)

2026-10-22. Plan `docs/EXEC_PLAN_MINIMAL.md`, reasoning `docs/PLAN_MINIMAL_CLAIMS.md`, predictions and outcomes `docs/EVIDENCE.md` (E38-E41), numbers `results/minimal/MINIMAL_REPORT.md`. 35 runs, CPU only, criteria frozen by hash before any run.

| Claim | Result | What it shows | Limit |
|---|---|---|---|
| **E38** Correspondence, not speed, carries the split | **Confirmed** (5 of 5 seeds) | At equal speeds the ladder's worst angle is 0.7-1.1 deg; a single eigendecomposition of the adjacent-frame differences gives 80-89 deg (a random split). At separated speeds both work (under 3.3 deg). | Mirror encoder, synthetic worlds. |
| **E39** Nested identification to depth 5, predictively sufficient | **Confirmed** (5 of 5 seeds), rho_k dropped as not informative | Five blocks, four rungs: angles 0.6-1.9 deg, gap ratios 51-68, presence at least 0.98 at every rung. rho_k is 1.000 everywhere, but also 1.000 in the control, because the gate does not apply a broken rung, so nothing is discarded. | Mirror encoder, exact pairs. rho_k cannot tell a correct rung from a gated wrong one. |
| **E40** Theory's invariance term makes a generic encoder keep every block | **Refuted** (0 of 10 seeds) | The term made the middle block fully present (0.99 on 10 of 10, against 0.42-0.99), but the fast block stayed absent (presence about 0, gaps 1.1-3.0). | Presence remains a stated precondition (the ladder document's A-ENC). Not tested: other weights or architectures (stop rule). |
| **E41** A violated hypothesis shows in the gap | **Refuted as registered** by the second line only | 31 of 31 rungs with a gap over 10 and the block present were clean. 5 of 39 rungs with a gap of 10 or less were also clean (13%, allowed 10%): the flag was conservative, never wrong in the trusting direction. | The 10% level was my guess. |

## Reading
- **What holds, defensibly:** under the theory's own conditions (correspondence families that expose each layer, and a representation that keeps the layers) the iterated split identifies nested layers to depth 5, and it does so by correspondence, not by speed (E38, E39; with E21, E33, E34). A large gap with the block present was never wrong (31 of 31 here; 187 of 190 over earlier runs, the three misses before the gate existed). The gate keeps a wrong rung from damaging what the ladder keeps.
- **What the theory's training term did not give:** E40 shows the invariance term alone does not force a nonlinear generic encoder to carry the fast, least-predictable layer. This matches the position of the question-ladder document: the encoder condition (A-ENC) is the central empirical bet, and here it fails for this objective and this encoder, in the one place the objective gave no incentive. The theory attributes the enforcement to the variance term (Theorem 4.2); an implementation of that term that acts on the first block's information, not only on marginal variance, is the untested piece.
- **Not claimed:** real images or video (A-ENC unverified there), pairs built from data beyond cluster limits (E31/E32), the n^(-1/2) rate with a learned encoder (established only in the linear core test), geometry and planning, a payoff test.

## Process notes
rho_k's non-informativeness was foreseen in the registration and handled by its registered branch. The 10% level in E41 and the 95% level are mine. Earlier registrations stay in the log; the items cut for these claims are listed in `docs/PLAN_MINIMAL_CLAIMS.md` section 3.
