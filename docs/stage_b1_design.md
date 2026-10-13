# Stage B1 — design (draft, nothing built, pass numbers not yet locked)

Written in plain words, using the paper's terms. Read it, change what you want, and only then
will the pass numbers be locked and anything be built.

## What B1 asks

If the matched pairs at each level are correct, can the invariant block of one split be split
again, with each split recovering its own block and the blocks nesting properly?

B1 does **not** ask whether those pairs can be built from the data. That is B2. Every B1 result
will be labelled "ground-truth pairs".

## Where each piece comes from

| Piece | Source |
| --- | --- |
| Difference of paired samples cancels the invariant part; the average outer product `M` of those differences is the thing we split | paper (Theorem 2, spectral head); monograph Thm 4.1, eq. (4); plan §2.3-2.4 |
| Pairs must collectively vary every variant direction (`M` full rank) | paper's full-rank variation condition; monograph Assumption 2.2; plan §2.1 |
| Splitting the invariant block again, rung by rung | monograph Thm 5.2; plan §2.4. **New in this project; the paper does not do it.** |
| Second-level pairs built by the generator, one level up from the paper's twins | **our extension** of the paper's twin-sampling |

## The world (all Gaussian, following the paper)

- Three blocks of 4 hidden numbers each, 12 in all: **texture** (fastest), **identity**, **category** (slowest).
- Separate speeds, as the plan asks (the paper uses one speed, 0.5): 0.2, 0.7, 0.95.
- Observations come from the paper's scrambling map (4 coupling layers, strength 0.5). No extra
  observed numbers: 12 hidden, 12 observed.
- No hidden cross-cutting factor in the first B1 run.

## The model (the paper's recipe)

- Mirror-style encoder, paper's objective (alignment + SIGReg, weight 1e-6), 10,000 steps,
  batch 256, learning rate 3e-3, then frozen.
- ZCA whitening on 30,000 samples.

## Steps

1. **Rung 1.** 30,000 twin pairs share identity and category and resample texture. Take the
   average outer product of their differences. The top 4 directions are the **variant** block
   (texture); the other 8 are the **invariant** block.
2. **Rung 2.** 30,000 twin pairs share category and resample identity. Re-encode, whiten, and
   project onto rung 1's 8-direction invariant block. Take the same average outer product. The
   top 4 directions are the variant block (identity); the remaining 4 are the invariant core
   (category).
3. Fix each block's rotation (gauge) so that rung-to-rung angles are comparable.

## What we measure, and the pass numbers (proposed)

Measured against the truth on fresh data (15,000 to fit, 5,000 to test), as in Stage A.

| What | Paper's name or the plan's | Pass if |
| --- | --- | --- |
| each rung's recovered block vs the true block | angle (plan) | below 5 degrees, both rungs |
| how well the true block can be read from the recovered block | `variant_r2` per rung; `invariant_r2` for the final core | above 0.9 |
| leakage between blocks | `a12_fro`, `a21_fro`, `block_purity` | reported next to the paper's values; no significant leakage by the permutation test (Holm, alpha 0.01) |
| rung 2's block lies inside what rung 1 left | nesting angle (plan) | below 5 degrees |
| how sharply the split separates | gap ratio (plan) | above 10 at each rung |
| pairs vary every variant direction | smallest eigenvalue of the pair-difference matrix | clearly above zero at each rung |

3 seeds. A pass means every line holds on every seed.

## Controls

Must fail, judged on the mean over seeds:
- **Shuffled second-level pairs.** Expect rung 2's angle above 45 degrees and gap ratio near 1.
- **One-direction-only variation at rung 2.** Breaks the "vary every direction" condition on
  purpose. Expect rung 2 to fail (angle above 10 degrees) while rung 1 still passes.

Recorded, with no pass-or-fail expectation:
- **No spectral head** (reading blocks off the encoder's coordinates). In Stage A with this
  encoder it still scored 0.96, so it cannot be required to fail. We record how much the
  spectral head adds.
- **No prediction** and **no regularizer / whitening**. We do not know that the mirror encoder
  fails without them, so no expectation is set.

## Cost and stopping

About 10 minutes of computing for all arms (3 seeds). If a line fails, we report where and why. We
do not keep adjusting until it passes.

## Risks, said plainly

1. **Separate speeds with the paper's objective.** The alignment term pulls consecutive frames
   together, which could squash the fast block. Whitening undoes moderate squashing, not extreme.
   A short earlier trial (in the log; its code is deleted) suggested it works, but that was
   only 2,000 steps and one seed.
2. **Generator-made pairs at rung 2.** A pass shows the mechanism works given correct pairs. It
   does not show we can build them.
3. **Strict leakage test.** On a trained encoder it could fire on tiny leakage. In Stage A it
   never did.

## Settings I need you to confirm

1. Block sizes 4 / 4 / 4 and three levels?
2. Separate speeds 0.2 / 0.7 / 0.95, or one speed like the paper?
3. Leave the hidden cross-cutting factor for after the basic split passes?
4. Keep the leakage rule strict, with no tolerance floor?
5. Are the pass numbers above right?
