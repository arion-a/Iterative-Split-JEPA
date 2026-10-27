# Is there a paper in this? An assessment of the work so far

2026-10-27. Written from the records (`docs/EVIDENCE.md`, `docs/MINIMAL_CLAIMS_REPORT.md`, `docs/GAPS_REPORT.md`, `docs/ENCODER_GENERALITY_REPORT.md`, `docs/EXECUTION_AUDIT.md`, `results/`), not from memory. Nothing new was run for this.

## Bottom line
**Yes, there is a concrete, defensible result, but it is a validation-and-failure-map result in synthetic worlds, not a "works on real data" result.** The honest title of what we have is closer to "Iterative SplitJEPA: when the correspondence ladder works, and how it fails" than to "a new method that works". It can be written now as a technical report or workshop paper. It is not yet strong enough for a main-venue claim, for the reasons in section 4.

## 1. What is solid (ranked by strength)

| # | Result | Evidence | Why it is solid | Scope / caveat |
|---|---|---|---|---|
| 1 | **Correspondence, not speed, carries the identification.** At equal speeds the ladder splits every rung (worst angle 0.7-1.1 deg, gaps 164 and up) while a single eigendecomposition of adjacent-frame differences gives 80-89 deg, 5 of 5 seeds. At separated speeds both work (under 3.3 deg). | E38 (confirmed, registered before the runs), E37a, E26 | Large effect, registered prediction, with the algebra that predicts it (a degenerate eigenspace). | Mirror encoder, Gaussian-AR worlds; nearly a worked check of the theory's converse, not a new theorem. |
| 2 | **The ladder identifies nested layers to depth 5 under the theory's conditions.** Angles 0.6-2.1 deg, gap ratios 47-73, presence at least 0.98 at every rung, 5 of 5 seeds at 3, 4 and 5 blocks. | E21 (99 of 100 checks, one rank flag), E34, E39 | Reproduced across four registered runs on fresh seeds. | Mirror encoder (built from the generator's own structure), exact pairs. |
| 3 | **A failure map: each failure corresponds to a violated assumption, and the gap reports it.** Across 305 rungs with presence recorded: a gap over 10 never occurred without the block being present in the earlier encoders; 187 of 190 rungs with gap over 10 and block present were clean (the 3 misses before the gate existed). Gap 10 or less: 115 rungs, 7 clean. The rung gate removes the carry-over after a failed rung (3 of 10 to 9 of 10, E33). | E25-E30, E33, E41 | Prospective parts: E29, E30, E33. | The presence rule is **contradicted** by E43 (17 clean rungs below 0.95), so claim it as a pattern for the earlier encoders, not as a law. |
| 4 | **What makes a generic encoder keep the layers: the whitening constraint has to be enforced explicitly.** Prediction + invariance loss alone gives dimensional collapse (rank 9 of 12). Adding the whitening terms and 3x training turned rung 1 clean from 0 of 10 seeds to 9 of 10, both rungs from 0 to 7 of 10. | Audit, E40, E42, E43 | Large effect, mechanism diagnosed (dead covariance directions, Jacobian ranks). | E43 was **refuted as registered** (presence 0.95 not met); the rung-only reading is post hoc. Needs a fresh confirmatory run. |
| 5 | **Cluster-count from the slow subspace** fixes the wrong-space failure (E18): K = 6 on 10, 9, 6, 3, 0 of 10 runs at sigma 0.1, 0.4, 0.6, 0.8, 1.0, controls behave. | E31, E32 | Cause located; boundary located. | Hierarchical-mixture world of our own making; the boundary is a resolution limit. |
| 6 | **Negative results with located causes**: robot images with frozen ResNet-50 features show no clean block even at the paper's block sizes (viewpoint ratio 1.2-1.9 against the paper's 8-14, rung-1 gap 1.0); the scaling floor is the encoder, not the sample (linear core gives 0.5 deg and slope -0.49); a stronger SIGReg weight did not help (0.1 only; weight 1.0 was degenerate). | E24, E36, E34, E35 | Registered and refuted. | Frozen features, simulated robot data. |

## 2. What is not available
- **Real or image data:** no result. Everything on robot data is negative.
- **A payoff** (predictive benefit of the hierarchy): not shown. rho_k is vacuous in the gated ladder, and the shift-readout test was badly designed.
- **Generic encoders keeping the slowest block at depth:** E44 passes the rung criteria at 4 and 5 blocks but loses the core (presence 0.56 and 0.33) and has dead output directions; the likely cause (whitening penalty scale 1/d) is untested.
- **Scaling law with a learned encoder**, geometry and planning, beyond-Gaussian dynamics: not tested.

## 3. A paper that could be written now
**Working title:** "Iterative SplitJEPA: a conditional validation and a failure map."
**Abstract in two sentences (draft):** Under the theory's own conditions (correspondence families that expose each layer, and a representation that preserves them) an iterated spectral split recovers nested layers to depth 5 and separates layers that speed cannot (equal speeds: 0.7-1.1 degrees against 80-89 for a single-shot split). Where it fails the cause is a violated assumption that a gap and a covariance diagnostic reveal: a generic encoder drops the fast layer and collapses output rank unless the whitening constraint is enforced, after which rung splits become clean on most seeds, while the slowest layer is still lost at depth and real image features show no clean block.

**Sections and their evidence:** 1 Theory in one page (monograph Thms 4.1, 5.2, converse, assumptions A-ENC / A-GAP). 2 Setup (worlds, mirror and generic encoders, the four numbers: angle, gap ratio, presence, rho_k not used). 3 Results: (a) equal speeds (E38), (b) depth (E21, E34, E39), (c) failure map and gate (E25-E30, E33, E41), (d) encoder objective and rank collapse (E40-E44, audit), (e) cluster count (E31, E32). 4 Negative results and limits (robot images, scaling floor). 5 Process: pre-registration, the hash-chained log, the ledger of registered outcomes.

**Figures that already exist as data:** angle by rung and depth; the equal-speed contrast; presence against angle (the failure map); gate before and after; cluster count against noise; whitening spectra (the dead-direction diagnosis, from the audit). The results page built earlier covers most of them.

**The ledger itself is a selling point:** of the 14 latest registered predictions (E31-E44), 4 were confirmed and 10 refuted as registered, each with a located cause and no tuning. That is the "defensible" part.

## 4. Threats a reviewer will raise (and what to do)
1. **The mirror encoder is near-oracle.** Its architecture is the inverse of the generator's coupling layers. The paper's own simulation uses it, but a reviewer will say the positive results are by construction. Mitigation: lead with the generic-encoder results, and say so plainly.
2. **Own worlds, one author's criteria.** All worlds and thresholds are ours. Mitigation: the thresholds are the monograph's or earlier registered ones; add one independent world type.
3. **Post hoc readings.** The rung-only re-judgement of E43 and some criteria changes were after seeing data; each is flagged in `EVIDENCE.md`. Mitigation: one confirmatory run, registered first.
4. **No baselines beyond the single-shot split.** Add slow-feature and time-contrastive style baselines at equal speeds.
5. **Unfinished generic-encoder story** (core block lost at depth).

## 5. Smallest work that would make it a stronger paper (not started)
1. Fix the whitening scale (per-direction weight not divided by d) and re-run the 4 and 5 block case, registered with the same bar (about 20 runs, under an hour).
2. A confirmatory run of the E43 recipe on fresh seeds with the rung criteria and presence reported, registered first (10 runs).
3. One baseline family at equal speeds (about 10 runs).
4. One world with non-Gaussian latent dynamics, or the robot head trained with the whitening terms (the Stage C pipeline exists; 6 runs).

## 6. Recommendation
Write the technical report now from what is solid (section 1 rows 1-3 and 6 are enough for a clean story), with row 4 stated as a diagnosed, partly confirmed finding. Run items 1 and 2 first if you want the generic-encoder section to stand without a caveat. Do not claim real-data success or a payoff.
