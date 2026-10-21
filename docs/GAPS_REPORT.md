# Gap-closing report (2026-10-21): what each gap came to

Plan `docs/PLAN_GAPS_ONE_BY_ONE.md`. Every prediction was registered in `docs/EVIDENCE.md` before its runs, criteria frozen by hash, and none was tuned after a refutation. "Closed" means the planned steps were executed to their stop rule, not that the prediction held.

| Gap | Question | Registered | Result | Outcome |
|---|---|---|---|---|
| 1. Cluster count (E18) | Why did the spectral count fail, and can it be fixed? | E31, E32 | Cause: count read in the 120-blob invariant space. In the slow subspace K = 6 on 10 / 9 / 6 / 3 / 0 of 10 runs at sigma_cat 0.1 / 0.4 / 0.6 / 0.8 / 1.0; both controls behave | Fixed up to sigma_cat 0.4 (E31 refuted only at 0.6); boundary located |
| 2. A failed rung damages the next | Does not applying a rung with no gap stop the carry-over? | E33 | Rung 1 not applied 10/10; rung 2 split 9/10 (3/10 without the gate); clean control no regression | **Confirmed** |
| 3. Deeper ladder | Do the four checks hold at 4 and 5 blocks, and does the error fall as 1/sqrt(n)? | E34 | Angles 0.6-2.1 deg, gaps 47-73, nesting and core hold at every rung; the strict leakage test flags (3/5 and 1/5 seeds pass; off-diagonal |R2| at most 0.0017); angle flat at about 1.25 deg from 10^4 to 10^6 pairs (slope -0.01) | **Refuted as registered**; located: leakage test sensitivity, and an error floor not set by the pair count |
| 4. Encoder keeps the content | Does a stronger SIGReg weight make the MLP keep every block? | E35 | 0/10 seeds at weight 0.1 and 0/10 at 1.0; presence got worse with weight | **Refuted**; presence stays a stated precondition |
| 5. Image features | Do the paper's block sizes (64 / 128) make the viewpoint a clean block? | E36 | P1 ratio 1.34-1.89 (needs 3), rung-1 gap 1.00; P3 and P4 hold, camera separation better than E24 | **Refuted**; located limit: frozen features; fine-tuning needs a GPU (handoff `docs/HANDOFF_E24_GPU.md`) |
| 6. Payoff | Is the hierarchy real, does it pay (synthetic world)? | E37 | Single-shot split also below 5 deg on 5/5 seeds (ladder 0.9-1.7 deg); shift-loss smaller after rung 2 on 3/5 seeds | **Both refuted** |

## Objective status
- **O2 (second split, core claim):** holds with ground-truth pairs and a mirror encoder (E21, E33, E34), and with a generic MLP when presence holds (E25-E30). Not secured: an encoder that keeps every block without a precondition (E35); image data (E36).
- **O3 (deep ladder):** recovery holds to depth 5; the 1/sqrt(n) scaling is not observed because the error sits at a floor; the registered strict leakage test is the first check to fail with depth.
- **O4 (payoff):** not shown. In the synthetic world a single eigendecomposition does about as well as the ladder, and the readout benefit is small and not consistent. The full Stage D is not attempted.

## Process notes
- The Stage C head training is not exactly reproducible on this machine (one option-off rerun gave rung-1 size 29 against 26 and P1 1.46 against 1.38); Stage C runs were limited to one thread each after three concurrent multithreaded runs stalled.
- Not started (awaiting the owner): pair-building from data beyond rung 2; longer training or other generic-encoder architectures; the fine-tuned ResNet-50 (GPU); the full Stage D; any change of the leakage test or the angle floor.
