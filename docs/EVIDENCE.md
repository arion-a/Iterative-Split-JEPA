# Evidence registry: pre-registered predictions

Created 2026-10-13T22:35Z. Predictions are written before the run and never edited. Outcomes are appended below the prediction.

## P9 (registered 2026-10-13T22:35Z, before any P9 run)

**Run.** Re-run B1 and B2 (docs/B2.md world and protocol) with hard nesting projection ON and the rung-1 pair budget doubled (60,000 against the
previous 30,000); the rung-2 budget is unchanged (30,000). 3 seeds. Results go to `results/stage_b1_nesting/` and `results/stage_b2_nesting/`.

**Prediction (written first, as supplied by the owner).**
* Nesting (both arms) drops toward about 2-4 degrees.
* The B1/B2 nesting gap stays about 0.
* The other gates improve or hold.
* The rank-check pass rate improves with the budget.

**Not part of the prediction (a note added at registration, by Claude).** In the earlier B2 run (results/B2, rung-1 budget 30,000) the nesting angle was
8.6-11.6 degrees while the rung-1 recovery angle was only 3.1-4.6 degrees, so most of that nesting figure is not inherited from rung-1 estimation error.
It is measured against the span of two linear-probe images, which are not orthogonal to the first block's image. Doubling the rung-1 budget therefore
may not move it much. This is a risk flag, not an amended prediction.

**Decision rule.** Confirmed if nesting for both arms falls into roughly 2-4 degrees and the other three statements hold; refuted otherwise. Report
the numbers either way. No parameter tuning to fit.

**Outcome.** (to be appended after the run)

## Diagnostic note before the P9 run (2026-10-13, written before any P9 run)

Nesting-angle laboratory (ideal world and B2 world, 3 seeds): inheritance confirmed in the ideal world; the n^-1/2 budget lever holds there but NOT in
the B2 world (rung-1 angle flat 3-4.7 deg from 7.5k to 480k pairs); the B2 span-definition nesting (8.5-11.5 deg) is mostly the truth-definition gap
(11.6-13.0 deg); against the orthogonal-complement truth nesting is 2.2-3.3 deg. P9 is run unchanged. Claude's expectation, recorded now and not
replacing the registered prediction: the span-definition nesting stays above 4 deg in B2 (so P9 as worded is refuted for B2 on that definition) while the
orthogonal-complement nesting lands in 2-4 deg; B1-arm nesting lands in 2-4 deg on either definition; budget doubling changes little.
