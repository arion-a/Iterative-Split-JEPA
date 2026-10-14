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

**Outcome (appended 2026-10-13, after the run): REFUTED as worded. Reports: `results/stage_b1_nesting/REPORT.md`, `results/stage_b2_nesting/REPORT.md`.**
Setup as registered: hard ON, pairs 60,000 / 30,000, 3 seeds. B2 was run in the clean world (sigma_cat 0.1) only, not the full sweep (one CPU); the B1 aggregate file flags leakage under the strict rule (seed 0, rung 1, R2 0.0002); under B1's amended floor-0.01 rule B1 passes every gate.
* *Nesting (both arms) drops toward 2-4 deg:* NOT confirmed. B1: 1.28 -> 1.22 deg (already below 2; no room to drop). B2 arm: 10.39 -> 10.31 deg (gate definition), unchanged. Against the orthogonal-complement truth B2 nesting is 2.82 +/- 0.55 deg, but that definition was not the gate and was in the 2-3 deg range before.
* *B1/B2 nesting gap ~0:* confirmed (B2 minus B1 = +0.10 +/- 0.21 deg, was +0.11).
* *Other gates improve or hold:* held, no change beyond noise. B2 still misses rung-2 angle, texture R2, rung-2 gap (3.1, from the discovered-K merge) and leakage; the B1 arm in the same world misses rung-2 angle, texture R2 and leakage.
* *Rank-check pass rate improves with budget:* no change, 3 of 3 seeds before and after (at ceiling); the new monitor passes 3 of 3 at both rungs.
Mechanism read: doubling the rung-1 budget moved the B2-world rung-1 angle by under 0.02 deg per seed (4.58/3.63/3.11 -> 4.59/3.62/3.12), the encoder-bias floor found in the diagnostics. The ~10 deg gate-definition nesting is the truth-definition gap (inherited 10.7-13.6 deg against span truth vs 3.1-4.6 against orthogonal-complement truth). No tuning done.
Follow-ups, registered as new predictions (not run): P10 - nesting measured against the orthogonal-complement truth (declared before the run as the gate) stays within 2-4 deg for the B2 arm in the clean world; P11 - a better-trained or less-nonlinear encoder lowers the B2-world rung-1 angle floor, and only then does the rung-1 budget start to matter.

## Diagnostic note before the P9 run (2026-10-13, written before any P9 run)

Nesting-angle laboratory (ideal world and B2 world, 3 seeds): inheritance confirmed in the ideal world; the n^-1/2 budget lever holds there but NOT in
the B2 world (rung-1 angle flat 3-4.7 deg from 7.5k to 480k pairs); the B2 span-definition nesting (8.5-11.5 deg) is mostly the truth-definition gap
(11.6-13.0 deg); against the orthogonal-complement truth nesting is 2.2-3.3 deg. P9 is run unchanged. Claude's expectation, recorded now and not
replacing the registered prediction: the span-definition nesting stays above 4 deg in B2 (so P9 as worded is refuted for B2 on that definition) while the
orthogonal-complement nesting lands in 2-4 deg; B1-arm nesting lands in 2-4 deg on either definition; budget doubling changes little.

## E10 (registered 2026-10-14, before the E10 run; earlier called P10 in a Claude note)

**Run.** The next B2 run (clean world, 3 seeds) judges nesting by the D10 definition (orthogonal-complement reference, threshold 5 deg).
**Prediction (owner).** B2-arm nesting is about 3 deg and inside the gate; absolute nesting becomes an informational diagnostic.
**Caveat recorded now.** P9 already read 2.82 +/- 0.55 deg on this definition, so this is a definitional ruling (D10), not an independent test.
**Outcome (2026-10-14): CONFIRMED, as a definitional result.** B2 arm nesting on the D10 reference 2.82 +/- 0.55 deg (treated arm 2.79 +/- 0.50, B1 arm 2.80 +/- 0.48), inside the 5 deg gate on all 3 seeds. Absolute nesting 10.31 +/- 1.61 deg, now informational. Report: `results/stage_b2_purify/REPORT.md`.

## E10a (registered 2026-10-14, before the E10a run)

**Run.** Clean-world B2, 3 seeds, 60,000 / 30,000 pairs, hard nesting. Same encoder and pairs for three rung-2 arms: B2 as before; B2 + Tier 1 purification; B2 + Tier 1 + Tier 4 (D10a constants: factor 4 x median, 5 iterations max).
**Prediction (owner).** The treated arm (Tier 1 + Tier 4) recovers at least 60% of the B1-B2 rung-2 gap-ratio deficit at fixed cluster purity, where recovered = (treated gap - untreated B2 gap) / (B1 gap - untreated B2 gap), means over 3 seeds. Reference from P9: B1 27.3, B2 3.1.
**Decision rule.** Confirmed if recovered >= 0.60; refuted otherwise. Tier 1 alone is reported as informational. No tuning of the D10a constants after seeing results.
**Outcome (2026-10-14): CONFIRMED.** Rung-2 gap ratio: B1 27.3, B2 untreated 3.1, Tier 1 19.7 (recovered 0.68), Tier 1 + Tier 4 18.7 (recovered 0.64; the registered treatment). Pair validity 0.83 -> 1.00 (0.997 on seed 2) at unchanged cluster purity 0.83; 82% of pairs kept, 98-99% of valid pairs kept, 98.5-100% of invalid pairs dropped. Rung-2 gap now passes the gate (>10). Tier 4 added nothing over Tier 1 (gap 18.7 vs 19.7; a21_fro 0.078 vs 0.051). Rung-2 angle (10.6 deg, B1 arm 10.3), texture R2 (0.882) and leakage (0.028) still miss their gates, in the B1 arm as well. Report: `results/stage_b2_purify/REPORT.md`.

## Item 2 check (2026-10-14): texture block rank
The owner's concern: if "2 textures per identity" meant 2 discrete values, the 4-dimensional texture block would have about one direction of variation. Checked on the generator and data (seed 0, clean world): texture centres are random 4-D vectors (240 centres) plus Gaussian jitter in all 4 dimensions. Texture block covariance eigenvalues 1.21 / 1.13 / 1.07 / 1.00; rung-1 pair-difference moment on the texture block 1.38 / 1.22 / 1.10 / 0.92; within-identity centre-difference moment 2.40 / 2.08 / 1.86 / 1.49. All four directions vary, so the premise does not hold in this world and the world was not regenerated. The 0.882 texture R2 therefore has another cause, not identified here.
