# Minimal-claims plan: what the theory lets us claim, and the smallest tests that would land it

Written 2026-10-22 after reading the monograph (`From One Split to a Ladder`), the program note (`From Two Blocks to the Ladder`) and the question-ladder proof document. **Status: proposal only. Nothing in this plan has been run, registered or started. The owner decides.** Numbers marked "post hoc" were tabulated today from existing result files and are descriptive, not registered.

Plain-language rule: every term is explained where it first appears.

---

## 1. The bigger picture

### 1.1 What the theory says, in one pass

1. **Prediction alone cannot split a world.** Prediction plus whitening fixes the content only up to an arbitrary rotation (monograph Lemma 3.1, Remark 3.3). The split has to come from somewhere else. The program note and the impossibility result it cites (Locatello et al.) say the same: some declared bias is unavoidable.
2. **The bias is the correspondence.** A *correspondence family* D_k is a set of pairs that agree on everything slower than layer k and differ in layer k (Assumption 2.2). Given such a family, the part of the representation that stays the same across the pairs is the invariant content, and the part that changes is the variant block (Theorem 4.1, with its converse: with no correspondence exposing a layer, that layer is not identifiable). The program note says it directly: "the correspondences are the auxiliary variable" of nonlinear ICA.
3. **The invariant content is a smaller world of the same kind**, so the same step applies again (Theorem 5.2). That is the ladder. Its blocks nest by construction, and the dynamics on the surviving content stay closed.
4. **Block sizes come from gaps** in the spectrum (§6.2). How many pairs a rung needs grows with the inverse square of the gap (Davis-Kahan, eq. 5), which is why the gap spectrum is published with every rung.
5. **Each rung should keep exactly what is still predictable at its own time scale** (§8; question-ladder T2: the ladder ordering is the eigenvalue ordering). Six acceptance criteria are listed in §8.1 (identification, compression, predictive sufficiency, coarsening contract, nesting, coarsening).
6. **Three conditions carry the whole result.** H1: correspondences expose each layer (Assumption 2.2). H2: the representation preserves the layers as an orthogonal image of the whitened latent (Theorem 4.1's "post-prediction form"; the question-ladder register calls it **A-ENC, "the central empirical bet"**). H3: the sample is large relative to the gaps (**A-GAP**, "checkable: publish gap spectra").

The theorem is therefore of the form: H1 and H2 and H3 imply an identified, nested ladder. It is a conditional result, and the documents label it as one.

### 1.2 What our tests have actually done, read against H1-H3

| Condition | What we tested | What happened |
|---|---|---|
| H1 correspondences | Ground-truth pairs (B1); pairs built from clusters (B2, E18/E31/E32) | Exact pairs: works. Built pairs: works while the categories are separated (to noise 0.4), then merges. |
| H2 encoder keeps the layers | Mirror encoder (built to invert the world); generic MLP; frozen ImageNet features | Mirror: every rung clean. MLP: clean only when it keeps every block (presence at least 0.95); it drops the fast block under prediction objectives (E23, E25, E28, E35). Frozen image features: no clean block (E24, E36). |
| H3 gaps and sample size | Gap ratios, pair counts 10^4 to 10^6 | Synthetic gaps about 50; robot features 1.0 (no gap). |

Post hoc tabulation over the 305 rungs that have a recorded presence value (E25-E30, E33-E35):

| | Rungs | Clean (angle under 5 degrees) |
|---|---|---|
| Block present (0.95 or more) and gap over 10 | 190 | 187 (the 3 misses are all E30, before the gate existed) |
| Gap over 10 and block not present | 0 | n/a |
| Gap 10 or less | 115 | 7 (all conservative: flagged but actually fine) |

So the pattern is clean: **a large gap never appeared without the block being present, and a large gap with the block present was almost always a correct split.** The ladder does not fail for reasons the theory did not foresee. It fails exactly where one of H1-H3 fails, and it says so through the gap.

### 1.3 Where our execution departed from the theory (the honest list)

| # | Departure | Effect |
|---|---|---|
| a | **We never trained an encoder with the theory's objective.** Monograph Step 5 and eq. (11) train with a predictive term, an invariance loss on each correspondence family, and a variance/whitening term. Theorem 4.2 says the variant block is invertible on its layer, "enforced by the variance term". Our encoders had prediction or alignment plus SIGReg only, and the splitting was a post-hoc spectral head. | The encoder was never given the reason the theory says forces presence. E35 turned the SIGReg weight, which is the wrong knob. |
| b | **Our acceptance checks were not the theory's.** We used angle, variant R2, gap, leakage. The theory's (c) predictive sufficiency, (b) compression and (d)/(f) coarsening were never measured. | We have no predictive result at all, which is the point the owner cares about most. |
| c | **The scaling claim was measured against the wrong target.** Davis-Kahan bounds the error of the estimated eigenspace around the *representation's own* population eigenspace. We measured distance to the *true* block, which includes the encoder's nonlinearity. The same engine gives under 0.5 degrees on an exactly linear representation (`tests/test_core_linear.py`, with the monograph's -0.49 slope under noise). | E34's flat angle (about 1.25 degrees from 10^4 to 10^6 pairs) is the floor from the nonlinear encoder, which the theory does not claim to remove. With gap ratios near 50 the sampling term is already below that floor at 10^4. |
| d | **The leakage check was strict significance with no magnitude.** At large test sizes a real nonlinear floor (largest off-diagonal R2 0.0017) is always "significant". §10's own contamination monitor uses a tolerance tied to the target final leakage. | E34's only violated check is a property of the check, not of the ladder. |
| e | **The "ladder against single-shot" test used well-separated speeds.** T2 of the question ladder says the eigenvalue ordering is the persistence ordering, so a temporal single-shot works when speeds separate. | E37a could not have refuted the ladder. It confirmed T2. |
| f | **The payoff test used independent blocks.** The program note names the failure the invariance protects against as the co-varying nuisance. With independent blocks a payoff can only come from finite-sample noise. | E37b could not show a payoff by design. |

Items c-f are errors in what I specified and measured, not in the theory. Item a is a missing piece, and it is the only one that can change the answer to the "any encoder" question.

---

## 2. The claims, reasoned

Four claims. Each has the theory chain, the evidence we already hold, what would falsify it, and what it would still not show.

### Claim 1. Under H1-H3 the iterated split identifies nested blocks to depth 5, and what each rung keeps is predictively sufficient at its time scale

- **Chain.** Theorem 5.2 gives nesting and per-rung identification under H1-H3. Block-diagonal AR(1) dynamics (Assumption 2.1) give E[z(t+h) | z(t)] = A^h z(t) block by block, so the future of the layers at or above k depends only on those layers: H_k is closed, and the coarsening defect (eq. 10) is exactly zero. So a rung that keeps H_k loses nothing predictive about its own future, and what it removes (layer k) is predictable only over the short horizon where its own AR coefficient has not yet decayed (T2: l-step predictability decays as the l-th power of the eigenvalue).
- **Evidence already held.** E21 (3 blocks), E34 (4 and 5 blocks): angles 0.6-2.1 degrees, gap ratios 47-73 at every rung, presence at least 0.95, core readout at least 0.9. These are conditional on the mirror encoder and exact pairs, which is exactly the claim's scope.
- **What is new.** The predictive criterion (c), "rho_k at most 1.05" (the monograph's frozen delta_s = 0.05), which we have never measured. I operationalise it as: predict the *future content of H_k* at horizon h_k from the content before the rung (H_{k-1}) and from the content after it (H_k), with equal-capacity ridge regressions on held-out samples, and take the ratio of the errors. (The monograph does not spell out the target; this is the reading under which "at most 1 + delta_s" means "nothing predictive was discarded". It is a flagged choice.) Horizon h_k is the layer's own time scale, -1 / ln(rho_world_k) rounded up.
- **Control.** The existing shuffled-pairs arm at rung 2. If the metric cannot tell a correct rung from a wrong one it is not informative and is dropped (stated in advance).
- **Falsified if:** an angle, gap or rho_k criterion fails on more than one of five seeds at any rung, or the control does not exceed 1.05.
- **Does not show:** anything about learned encoders without the mirror's inductive bias, cluster-built pairs, or real data.
- **Honest note.** In this world rho_k near 1 follows from correct identification plus independence of blocks. Its value is that it states the result in the theory's own predictive language and that a wrong rung visibly fails it.

### Claim 2. The correspondence, not the speed, is what carries the identification

- **Chain.** With adjacent frames as pairs, layer k contributes variance proportional to 2(1 - rho_k) to every direction of the whitened difference moment. If two layers share a speed, their eigenvalues are equal, the eigenspace is degenerate, and one eigendecomposition cannot say which directions belong to which layer (any rotation inside the eigenspace is as good): the angle is arbitrary. A correspondence family D_k has difference support exactly on layer k whatever its speed (Assumption 2.2), so the ladder is unaffected. This is Q2 of the monograph and the converse of Theorem 4.1, and it is the claim that distinguishes the method from slow-feature methods that order layers by speed.
- **Evidence already held.** At separated speeds both methods work (E37a: ladder 0.9-1.7 degrees, single-shot 1.4-3.2 degrees, 5 of 5 seeds), which is what T2 predicts. At equal speeds the ladder has already been seen to split every rung (E26, 10 of 10 rungs, MLP), but the single-shot was not run there.
- **Test.** A two-by-two: {ladder, single-shot} against {equal speeds, separated speeds}. The separated cell exists (E37, seeds 120-124), so only the equal-speed cell is new.
- **Falsified if:** at equal speeds the single-shot split is also under 5 degrees, or the ladder is not.
- **Does not show:** that the same holds with learned encoders (that is Claim 4), or that correspondences can be built from data (outside this plan).

### Claim 3. Every failure we saw is a violated hypothesis, and the gap reports it without ground truth

- **Chain.** A-GAP is "checkable": the gap spectrum is observable from the data alone. A rung whose block does not exist has a flat spectrum (gap near 1), because the difference moment has no preferred directions; a rung whose block exists has a gap. The theory therefore predicts that a gap above 10 requires the block to be present, and that a gap at or below 10 means the rung should not be trusted. After a failed rung, the gate (E33, confirmed 9 of 10 against 3 of 10) removes the carry-over that would otherwise let a later rung have a gap but a wrong block.
- **Evidence already held.** The 305-rung table above (a large gap never without presence; 187 of 190 clean; the 3 misses are pre-gate) and E33. This claim is retrospective apart from E33.
- **Test.** A prospective version at no extra cost: score the confusion table on the new runs of Claims 1, 2 and 4 (all with the gate on), with the rule written first.
- **Falsified if:** a rung with a large gap and a present block is not clean in more than 5% of new rungs, or more than 10% of rungs with a small gap are clean.
- **Does not show:** that presence can be observed without ground truth (it cannot; the gap and the rank test are the observable detectors; presence is measured here only because the synthetic worlds have true latents).

### Claim 4. Training the encoder with the theory's own objective restores presence for a generic encoder

- **Chain.** Theorem 5.1 (simultaneous identification): with a predictive loss, an invariance loss on every family D_k, and whitening, the optimum is g_j(z) = A_jj z_j with each A_jj orthogonal, given variational complementarity. In words: each output block is forced to be an invertible image of its own layer. The invariance loss forces the later blocks to ignore layer k; the variance term plus the fixed block sizes (as in the paper's Appendix D) then force the early block to carry it. A prediction-only encoder has no such pressure (the fast layer is the least predictable and is the first to be dropped), which is exactly E25's result (texture presence -0.012 on 5 of 5 seeds). So the missing term is the one the theory prescribes.
- **Why it is a real test.** The theory asserts the outcome; nothing guarantees our implementation reaches it. The cited nonlinear result (Remark 3.2) assumes Gaussian inputs, and our coupling-map observations are not Gaussian, so this is a genuine bet that can be refuted.
- **Test.** The E25 cell (MLP, prediction objective, speeds 0.2 / 0.7 / 0.95, which drops the fast block) with one added term: for each k, the squared distance between the later-block outputs of the two members of a ground-truth pair from D_k, with a single weight (1.0, fixed in advance, not tuned). Same fresh seeds for a baseline arm (without the term) and a treated arm.
- **Falsified if:** presence is below 0.95 for any block on more than one of ten treated seeds, or the baseline does not fail (then the contrast is vacuous and the result is not informative).
- **Does not show:** that real images satisfy A-ENC (declared as the empirical bet), or that the block sizes can be found from data (the sizes are given, as in the paper).

### 2.5 Do these four reach the conclusion the theory predicts?

| The theory's conclusion | Covered by | Status if the claims hold |
|---|---|---|
| An identified split can be split again, to depth L, nested | Claim 1 | Reached, conditional on H1-H3 |
| Layers are told apart by correspondence, not speed | Claim 2 | Reached in the synthetic worlds |
| Each rung keeps what is predictable at its scale | Claim 1 (rho_k) | Reached in the Gaussian block world |
| The audits say when a rung is not trustworthy | Claim 3 | Reached (retrospective plus prospective) |
| The encoder objective enforces the conditions | Claim 4 | Reached or located (the uncertain one) |
| Block counts come from gaps | existing linear-core test and Stage A | Already established; not re-run |
| n^(-1/2) with the sample | `tests/test_core_linear.py` (linear core) | Established there; not claimed with a learned encoder |
| Straightened geometry, planning (§7), flag-variety belief (C4), beyond-Gaussian dynamics (Move 3) | none | **Not claimed** |
| Real video / image data | none | **Not claimed** (A-ENC is the declared bet) |

If Claims 1-3 hold and Claim 4 is confirmed, the result reads: **under the theory's own three conditions, the iterated correspondence split identifies nested hidden layers to depth 5 in controlled worlds, keeps what is predictive at each scale, separates layers that speed cannot, and its gap says when it cannot be trusted; and a generic encoder trained with the theory's objective keeps the layers.** If Claim 4 is refuted, the result is the same minus the last clause, with the located limit that the objective as implemented does not enforce presence, which is still defensible and is the honest statement of A-ENC.

---

## 3. What to cut

Nothing is deleted from the repository. "Cut" means: not used to support any claim, not re-run, not carried in the analysis.

| Cut | Why |
|---|---|
| Stage B2 world, cluster-count work (E18, E31, E32), Tier-1 purification, probe-image analysis (E22) | The claims take correspondences as given (H1, Assumption 2.2). Building pairs from data is the presupposition chain, a separate step. Its located limit (sigma 0.4) is stated, not extended. |
| Stage C robot pipeline (E24, E36), feature extraction, GPU handoff | There are no planted blocks, so none of Claims 1-4 can be tested there. Real images are the declared A-ENC bet. |
| Scaling sweep and bootstrap slope (E34 part b) | The theory can claim the rate only for the estimation part; the monograph's own linear-core test already shows it. Re-run only if the owner asks. |
| Encoder-generality machinery: ABSENT / PARTIAL / PRESENT_NOT_SEPARABLE / SPLIT classes, the linear presence probe, weight pilots and grids, E27 arms, E28 pilot | One presence number (nonlinear probe) per block does the job. |
| Separate metrics: variant R2, invariant-content R2, core R2, nesting angles (hard nesting makes them near-vacuous; angle to the true block implies them), permutation-null leakage matrix with Holm correction, eigenvalue lists, a12/a21, block purity, inherited-span angles, global R2 | Replaced by the four numbers in section 4. The leakage audit and its 1000 permutations are the slowest part of a run. |
| Engine modes: soft nesting, within-block whitening (D10a), horizon option, ablations no_pred / no_var / no_inv | Hard nesting only. |
| The independent-block shift test (E37b) | Replaced by rho_k (item f above). |
| Strict-significance leakage as a criterion | Replaced by a reported magnitude only. |
| Seed counts above 5, except Claim 4 (10) | Effects are large; Claim 4 is the one result that can come out mixed. |
| One registration per sub-question, with its own hashed criteria file | One registration for the programme, one criteria file. |

---

## 4. The minimal measurement set

All thresholds are numbers already used or stated in the monograph. No new constant.

| # | Quantity | Meaning (plain) | Threshold | Used by |
|---|---|---|---|---|
| 1 | **Angle** | How far the found block is from the true one (worst principal angle) | under 5 degrees | Claims 1, 2, 3, 4 |
| 2 | **Gap ratio** | How much stronger the block's directions are than the first one left out | over 10 | Claims 1, 3, 4 |
| 3 | **Presence** | How well the encoder output still holds each true block (nonlinear readout R2 from the whole embedding) | at least 0.95 | Claims 1, 3, 4 |
| 4 | **rho_k** | Error of predicting the kept content's future from the kept content, divided by the same from the content before the rung | at most 1.05 | Claim 1 |
| - | Control | The shuffled-pairs arm (gap near 1, angle large) | as before | Claims 1, 2 |

Reported only (not criteria): the worst single-shot angle (Claim 2); the gap, presence and clean flag per rung (the Claim 3 table); the largest off-diagonal leakage R2 (one number); and, for the user's picture, the predictability of each found variant block at horizon 1 against its own horizon h_k.

---

## 5. The minimal experiments, claim by claim

Seeds are fresh (130-134 and 140-149 are unused; 120-124 are reused only for the paired equal-speed cell). Every run uses ground-truth pairs, hard nesting and the rung gate (E33). Runs are single-threaded, four at a time.

### Claim 1: `configs/minimal_c1.yaml`
- World: 5 blocks of 4, speeds 0.2 / 0.45 / 0.7 / 0.85 / 0.95 (as E34), mirror encoder with the paper objective, 30,000 pairs per rung.
- Arms: main, seeds 130-134 (5 runs); shuffled_rung2, seeds 130-134 (5 runs). **10 runs.**
- Measured: angle, gap ratio, presence at every rung / block; rho_k at every rung of the main arm and rung 2 of the control.
- Draft prediction (flagged, the 4-of-5 level is the earlier one): on at least 4 of 5 seeds every rung has angle under 5 degrees, gap over 10, presence at least 0.95 for all five blocks, and rho_k at most 1.05; in the control, rung-2 gap is under 2 and rho_2 exceeds 1.05 on at least 4 of 5 seeds. If the control does not exceed 1.05 the rho_k metric is declared not informative.
- Stop rule: a failing criterion is a result; no tuning.

### Claim 2: `configs/minimal_c2.yaml`
- World: 3 blocks of 4, speeds all 0.5, mirror encoder, same settings as the E37 cell.
- Runs: main, seeds 120-124 (**5 new runs**), reusing the E37 separated-speed cell (seeds 120-124) for the other half of the two-by-two. The single-shot split is already computed inside the existing `payoff` option.
- Measured: worst-block angle for ladder and single-shot in each cell.
- Draft prediction (flagged): at equal speeds the ladder is under 5 degrees and the single-shot is 5 degrees or more, on 5 of 5 seeds; at separated speeds both are under 5 degrees (already seen).
- Stop rule: if the single-shot is also under 5 degrees at equal speeds, the claim that correspondences are needed is refuted for this setting and is reported as such.

### Claim 4: `configs/minimal_c4_baseline.yaml`, `configs/minimal_c4_treated.yaml`
- World: 3 blocks of 4, speeds 0.2 / 0.7 / 0.95 (the E25 cell), generic MLP encoder, 10,000 steps.
- Baseline arm: the E25 prediction objective unchanged. Treated arm: the same plus the invariance term of section 2 (single weight 1.0).
- Runs: seeds 140-149, both arms. **20 runs.**
- Measured: presence per block; angle and gap ratio per rung.
- Draft prediction (flagged; the 9-of-10 level is the earlier one): in the treated arm presence is at least 0.95 for all three blocks and both rungs have angle under 5 degrees and gap over 10 on at least 9 of 10 seeds; in the baseline arm texture presence is below 0.5 on at least 9 of 10 seeds (needed for the contrast to be informative).
- Stop rule: if the treated arm fails, presence stays a stated precondition and nothing else (no tuning of the weight, no other architecture).

### Claim 3: no separate runs
- The confusion table (gap over 10 or not; present or not; clean or not) is scored over all rungs of the 35 new runs. Rule written first: a rung with a large gap and a present block is clean in at least 95% of cases, and at most 10% of rungs with a small gap are clean (levels set from the post hoc table, flagged).

**Totals: 35 new runs, about 2 to 3 hours on four cores** (order of magnitude from E33 and E35; not measured for the new settings).

### Code needed (all small)
1. `BlockWorld.lag_pairs(n, h)`: the h-step transition, composing the AR(1) coefficient (about five lines).
2. A `predictive` option in `run_stage_b1.py` that computes rho_k for each rung (about 20 lines), and a `minimal` option that skips the permutation-null leakage audit and the linear presence probe (a few lines).
3. A `split` objective in `train_encoder`: the existing prediction objective plus the invariance term over `world.correspondence_pairs(n, k)` for each k (about 30 lines).
4. One analysis script that reads the five numbers and applies the rules.
5. Remove the shift-readout part of the `payoff` option (E37b is dropped).

The existing 52 tests must still pass; no new test beyond one smoke run per addition.

---

## 6. The plan, phase by phase

### Phase 0. Decide and freeze (no code)
- 0.1 Owner reads this document and decides (section 7). **Gate: go / no-go per claim.**
- 0.2 One registration page in `docs/EVIDENCE.md` for the programme (Claims 1-4 with their draft predictions, flagged), one criteria file with its hash, and the analysis script written, all before any run. Done when `check_results.py evidence` passes and the hash file is committed.
- 0.3 A short note in `docs/STATUS.md` listing the cut items of section 3 as "not used for these claims". Nothing deleted.

### Phase 1. The smallest code
- 1.1 `lag_pairs` and the `predictive` / `minimal` options. Done when a 3-block smoke run writes rho_k and the 52 tests pass.
- 1.2 The `split` objective. Done when a smoke run trains and writes the presence numbers.
- 1.3 The analysis script reproduces, from the stored E37 file, the single-shot and ladder angles it already reports (a check that the reader is right, no new claim).
- **Gate:** tests pass, evidence file unedited, smoke outputs have every field.

### Phase 2. Claim 2 (cheapest; no new code beyond the config)
- 2.1 Run the 5 equal-speed runs. 2.2 Score the two-by-two, record the outcome in `EVIDENCE.md`. **Gate:** counts complete, outcome recorded, tests pass. If refuted, stop that claim and report.

### Phase 3. Claim 1
- 3.1 Run the 10 runs (5 main, 5 shuffled). 3.2 Score angle, gap, presence, rho_k; record. **Gate** as above. If rho_k is not informative, say so and keep the other three numbers.

### Phase 4. Claim 4 (and Claim 3 scored on everything)
- 4.1 Run the 20 runs (10 baseline, 10 treated). 4.2 Score presence, angle and gap. 4.3 Score the Claim 3 table over all 35 runs. Record. **Gate** as above. If the treated arm fails: presence remains a stated precondition, the programme closes there.

### Phase 5. Write-up
- 5.1 One page: the four claims, each with its outcome, its scope and its located limit; the status of each theory statement (section 2.5); the cut list. 5.2 Refresh `explog/stages.json` and `docs/PLAN_*.md`; run tests and `explog.verify()`; push. No merge to `main`.

### Supervision
One supervisor script per phase (the existing `supervise_b1.sh` pattern, four runs at a time, resumable), a monitor re-armed while runs go, commit and push at every stop. Claim 2's runs can start as soon as Phase 1.1 is done.

---

## 7. Decisions for the owner

1. Go, no-go, or edit, claim by claim (the plan is independent per claim; Claim 2 is the cheapest and strongest single result).
2. Accept the one-weight choice (1.0) for the invariance term in Claim 4, set before the run and never tuned.
3. Accept my operationalisation of rho_k (target = future of the kept content, equal-capacity ridge).
4. Whether, **only after** Claim 4 is confirmed, to repeat the invariance-term test on the robot head (the Stage C pipeline exists; six runs). It is outside this plan and I will not start it.
5. Whether to retire the earlier registrations from the claim record (they stay in the log either way).

### What I expect, so you can weigh it
- Claims 1, 2 and 3: high confidence (the algebra and the existing tables say so). Claim 2 follows from a degenerate eigenspace at equal speeds.
- Claim 4: genuinely uncertain. It is the one that could come out refuted, and the one that matters for "any encoder".
- If Claim 4 is refuted, the defensible result is still Claims 1-3 plus a located A-ENC limit, which is exactly how the question-ladder document frames it ("the central empirical bet").

### Noted, not started
Deriving the rate relative to the representation's own eigenspace; building pairs from data beyond rung 2; geometry and planning (§7); the beyond-Gaussian master theorem; real-image encoders; the full Stage D.
