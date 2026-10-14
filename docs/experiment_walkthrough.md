# Experiment walkthrough (plain English)

This is the step-by-step plan, derived from the Experimental Plan, with what each step builds, what
we measure, what counts as success, and where it stands. The live record of what actually happened
is `explog/LOG.md` (generated from the tamper-evident chain `explog/chain.jsonl`).

## The big idea

A world has hidden facts. Some change fast (lighting, texture), some change slowly (which object it
is, its category). We never see them directly, only scrambled observations. The project asks:

1. Can a model learn to **separate "what stays the same" from "what changes"** without ever
   reconstructing the input? (This is SplitJEPA, one split.)
2. Can we **repeat the split on the part that stayed the same**, getting a ladder of layers from
   fast to slow? (This is the new part, "iterative" SplitJEPA.)
3. Does the ladder hold up deeper, and is it actually useful?

Each stage below tests one of these, in order. A stage only starts when the previous one passes.

## Words used in this project

| Word | Meaning |
| --- | --- |
| hidden state / latent | the true underlying numbers that generate what we observe (known to us only because the world is synthetic) |
| block | one group of hidden numbers that change at the same speed |
| fast / slow, variant / invariant | the part that changes between matched pairs / the part that stays the same |
| matched pair | two observations that share the slow facts but differ in the fast ones |
| encoder | the small neural network that maps an observation to a learned representation |
| frozen | trained once, then not changed again while we test it |
| split | finding which directions of the representation are "changes a lot" vs "stays the same" |
| rung | one split on the ladder; rung 2 splits what rung 1 said stays the same |
| seed | one repeat with different random numbers; 5 seeds shows it is not luck |
| control | a run that *should* fail; if it does not fail, the success means nothing |
| R² | how well you can read the true hidden values back from the learned block (1 = perfectly, 0 = not at all) |
| angle | how far the learned direction is from the true direction (0° perfect, 90° unrelated) |
| gap ratio | how sharply "changes a lot" separates from "stays the same" (about 1 = no separation; 10+ = clean) |
| leakage | information about the fast group appearing inside the slow block (should be none) |
| coupling strength | how strongly the world scrambles hidden values into observations (harder when larger) |

## Stage A — one split with a trained network  (status: done, passes)

* **Question.** Does the full pipeline (not an idealised formula) recover a planted split?
* **World.** 4 fast + 4 slow hidden numbers, scrambled by a nonlinear map into 16 observed numbers.
* **Steps and where they live in the code.**
  1. Generate the world and matched pairs — `src/isj/worlds.py`.
  2. Train a small network to predict the next state, with extra terms that stop it collapsing to a
     few directions — `src/isj/encoder.py`.
  3. Freeze it; measure how observations spread (whitening) — `src/isj/engine.py`.
  4. On 30,000 matched pairs, find the "changes a lot" directions vs the "stays the same"
     directions — `src/isj/engine.py`.
  5. Measure against the truth on fresh data (R², angle, gap ratio, leakage) — `src/isj/audits.py`,
     `src/isj/stage_a.py`.
  6. Repeat for 5 seeds plus the controls — `experiments/run_stage_a.py`.
* **Success (fixed before running, in `configs/stage_a.yaml`).** Slow-block R² above 0.9, angle below
  5°, gap ratio above 10, no leakage; shuffling the pairs must remove the gap.
* **Result.** All met on all 5 seeds (R² 0.99, angle about 1°, gap 59–138). Controls failed as they should.
* **Still open.** Comparison with the paper authors' own code (needs your approval to run).

## Stage B — the core claim: split a second time  (status: not started)

* **Question.** Can the "stays the same" part from rung 1 be split again?
* **World.** Three levels (texture, identity, category) plus one hidden factor that cuts across levels.
* **Steps.** Rung 1 as in Stage A. Build rung-2 pairs by grouping rung-1 slow content into
  same-category clusters (measure how pure the clusters are, target at least 0.9). Split again inside the slow
  content. Check the new "changes" directions sit inside the old "stays the same" space.
* **Success.** Rung-2 angle below 5°; nesting holds; a "deviation map" points to the cross-cutting factor.
* **Controls.** Shuffled rung-2 pairs; injecting a rung with only one direction of variation (should break only that rung).

## Stage C — deeper ladder and scaling  (status: not started)

4–5 levels, four acceptance checks between rungs, error shrinking as 1/√(data size) at 10⁴, 10⁵, 10⁶
samples, and finding the first depth where it breaks. A located limit is itself a result.

## Stage D — does it help?  (status: not started)

Five matched methods on navigation/manipulation worlds, six pre-set metrics, three separate verdicts:
identification works / hierarchy is real / it pays.

## Rules every stage follows (from the plan)

* Success thresholds are written down and locked before running (a hash of them is checked).
* Every claim needs a measurement against the truth, a control that should fail, and a fixed threshold.
* Stage A may take at most three debugging rounds, then we stop and publish the negative result.
* No stage proceeds on accumulated effort alone.

## How the log works

`explog/chain.jsonl` is append-only. Each entry stores a fingerprint (hash) of the previous entry, so
changing or deleting any past entry breaks every later fingerprint and `python -m isj.explog verify`
reports it. Each entry says: what part of the experiment, how it was done, what came out, and what
that means for the project's larger goals (`explog/objectives.yaml`). The runner appends entries
automatically as runs start and finish. Entries written after the fact are flagged `retroactive`.
