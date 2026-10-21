# Report: does iterative splitting work on the latent space of any encoder? (E25-E30)

Written 2026-10-21 at the end of `docs/PLAN_ENCODER_GENERALITY.md`. Predictions are in `docs/EVIDENCE.md` (never edited; the check passes), criteria in `configs/layered.yaml` (decision D15) and `configs/layered_v2.yaml`, numbers in `results/enc_generality/` (`REPORT.md`, `E29_REPORT.md`, `PRESENCE_VS_SPLIT.md`). All runs: B1 world (three blocks of 4 latents, 4 coupling layers, ground-truth pairs), 10,000 training steps.

## The question and the answer in one paragraph
The owner's position: splitting is a property of the representation, so it should work on any encoder's output. What the tests show: the split works on a learned encoder's latents whenever the encoder has kept the content almost fully (a mirror encoder, or a generic MLP trained so that it keeps every block: E26, E27, and the good seeds of E28/E29), and fails when the encoder has discarded the content. The earlier failure (E23) was of the second kind: a prediction-trained MLP throws away a block it cannot predict, so there was nothing to split. Not every generic encoder keeps the content reliably (E28/E29: 6 of 15 seeds of one MLP + paper-objective setup did), which is a property of how that encoder was trained, not of the splitter.

## What was run and what came out

| Test | Question | Registered prediction | Result | Outcome |
|---|---|---|---|---|
| E25 | Did the prediction-trained MLP (E23 setup, speeds 0.2 / 0.7 / 0.95) drop the fast block? | Texture presence below 0.5 and category presence at least 0.9, on at least 4 of 5 seeds | Texture presence -0.012 (5 of 5 seeds), identity 0.744 (partial), category 0.993; rung 1 ABSENT on 5 of 5 | **Confirmed** |
| E26 | Equal speeds (0.5 each), same MLP and recipe | All blocks present on at least 4 of 5 seeds; every B1 criterion except possibly texture R2 on at least 4 of 5; control behaves | All blocks 0.991 on 5 of 5; both rungs SPLIT on 5 of 5; every criterion 5 of 5; control behaved | **Confirmed** |
| E27 | Architecture x objective at equal speeds: does any present block fail to split? | No cell has a present-but-not-separable rung on 2 or more seeds | Mirror + paper, mirror + prediction, MLP + prediction: presence 0.99+, SPLIT 5 of 5. MLP + paper objective: collapsed to a constant (regulariser weight 1e-6 copied from the mirror setup) | **Confirmed as registered, empty in the collapsed cell** |
| E28 | Repair the collapsed cell (weight 0.01, chosen by a training-health rule on a spare seed) | All blocks present and both rungs split on at least 4 of 5 seeds | No collapse; 2 of 5 seeds split like the mirror (gap 80 / 54, angles under 1 deg), 3 kept the blocks only partly (presence 0.82-0.95) and failed | **Not confirmed** |
| E29 | Fresh seeds 35-44 of the E28 cell: is presence at least 0.95 enough, and below it never enough? | Every rung at 0.95+ splits; no rung in [0.5, 0.95) splits | Below 0.95: 0 of 11 split (held). At 0.95+: 8 of 9 split; the exception is rung 2 of a run whose rung 1 had failed | **Refuted as registered** (one rung) |
| E30 | Fresh seeds 45-54, two cells (the E28 cell; MLP + prediction at speeds 0.35 / 0.6 / 0.8): test the 0.95 threshold and the 'previous rung must split' rule | Below 0.95 never splits and at least 90% at 0.95+ split; the conditional rule agrees on at least 95% and no rung after a failed rung splits | Below 0.95: 0 of 22 split (held). At 0.95+: 11 of 18; all 7 failures are rung 2 after a failed rung 1. Conditional rule 37 of 40; 3 of 10 rungs after a failed rung split | **Refuted** (both claims) |

## The right criteria, as far as the data go (updated after E30)
1. **Presence first.** Check that each true block is recoverable from the whole embedding (nonlinear probe; linear alongside; both gave the same counts). Judge splitting only for blocks that are present, and say separately which blocks are absent or partial. This separates "the encoder dropped it" (E25) from "the splitter missed it".
2. **Necessary: presence of about 0.95 or better.** Across E25-E30 (120 rungs) no rung below 0.95 split (0 of 59; 0 of 33 in the two prospective tests E29 and E30). The 0.9 bar frozen in D15 was too lenient.
3. **Sufficient when the earlier rungs worked.** A block at 0.95 or better split on 50 of 50 rungs where rung 1 was being judged or the previous rung had split (16 of 16 in the prospective tests).
4. **After a failed rung there is no guarantee either way.** E30 refuted the rule "the previous rung must split": of 11 rungs at 0.95 or better after a failed rung, 3 split. The error carries over continuously (cell B rung 2: angles from 2.5 to 78 deg, gap ratios up to 121 where a clean block was found), so later rungs should be judged on their own criteria and reported with the nesting angle. The cause suggested by the numbers (a failed rung removes arbitrary directions that cut into the next rung's content) is a hypothesis and was not tested.
5. **Separability criteria unchanged:** the hash-frozen B1 criteria (angle, variant R2, gap ratio, rank test, leakage).
What was predicted and failed: the stricter reading "presence at 0.95 always splits" (E29, one exception) and "the previous rung must split" (E30, 3 of 10 split anyway). An earlier version of this report said the rule fit all 80 rungs; the re-check showed that rested on a single distinguishing rung, which E30 then contradicted.

## Earlier results re-read through the layered view (analysis of existing numbers, no new claim)
- **E21 (mirror encoder, original speeds):** all latents recoverable (linear R2 0.97-0.98), so presence holds; both rungs SPLIT on 99 of 100 criterion-seed checks. E27's mirror cells (presence 0.996 / 0.994) agree.
- **E23:** the same configuration as E25, which measured it: texture ABSENT, identity PARTIAL, category present. The E23 verdict stands as registered, and its cause is the encoder's loss of the fast block, not the splitter.
- **E24 (simulated robot data, frozen ImageNet encoder + trained head):** no true latent blocks exist to probe, so presence cannot be scored the same way. Camera identity is readable from the variant block (0.93-1.00) and also partly from the rest, with no gap (1.1-1.8): in spirit "present but not separable". That reading is informal and E24 was not re-run.

## Limits
Synthetic Gaussian blocks with ground-truth pairs; presence is measured against the true latents, which only synthetic worlds provide. One MLP size and one training budget (10,000 steps); the E28/E29 cell's partial seeds might improve with another weight or longer training (not tested). The 0.95 threshold and the conditional rule come from the data they describe, with E29 as a partial prospective check. E24-type real-image encoders were not re-tested.

## Process notes
- Mistakes caught and fixed: the paper's regulariser weight copied into the MLP cell (collapse; found from the saved training state); pilot configs written as `1e-4`, which YAML reads as text (four runs crashed before writing anything, configs fixed, runs repeated); a shell cleanup command that killed its own shell (no data affected); a script label ("collapsed or absent") that did not describe E28 (outcome recorded in words).
- The integrity checks (`experiments/check_results.py enc`) flag the collapsed E27 cell by design; that is the documented collapse.
- The cloud container restarts whenever the session is idle and kills background jobs; a monitor was kept active during every run.
- Not started, awaiting the owner: another weight or a longer run for the MLP + paper-objective cell; a direct test of why a failed rung damages the next one.
