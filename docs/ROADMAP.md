# Roadmap and live status (updated at each step)

**Scope (owner's decision, 2026-11-14): the project claims only the paper's setting: synthetic latent worlds plus the simulated robot data (ManiSkill3). No real-world video.**

Last updated: 2026-11-13. Tick = done and recorded in `docs/EVIDENCE.md`. "Open" = not started or running. The owner decides what starts.

## Stage A: one split on a trained encoder: DONE
- [x] Reproduce the single split of the original paper (5 of 5 seeds), controls behave

## Stage B: the second split: DONE under conditions
- [x] Exact pairs, mirror encoder: both rungs about 1 degree (E21)
- [x] Gap fix, probe-image explanation (E12, E22); cluster count in the slow subspace (E31, E32; boundary noise 0.4)
- [x] Failed rung does not damage the next: the rung gate (E33)
- [ ] Open (not started): build pairs from data for rung 3 and deeper

## Stage C: the deep ladder: MOSTLY DONE
- [x] Depth 3 to 5 with the mirror encoder (E34, E39)
- [x] Generic MLP with the theory's terms keeps every rung and the slowest block to depth 5 (E40 to E45; the whitening scale was an execution error)
- [x] Located the first failing check (strict leakage test with the mirror encoder; dead directions from the whitening scale with the generic encoder)
- [x] The 1/sqrt(n) rate with a learned encoder, measured against its own eigenspace: slope -0.48, interval contains -0.5 (E48)
- [x] Confirmatory run of the E45 recipe on fresh seeds (E49): the core and covariance health hold on 20 of 20 runs; 5 blocks all lines met; 4 blocks rung 2 clean on only 6 of 10 (needs 7): refuted as registered
- [x] Why rung 2 at 4 blocks 'fails': it does not. It finds block 2's actual footprint to 1.0-1.3 deg in all 7 runs checked; the angle criterion measures the distance to the best linear image, which is 53-82 deg off when the encoder embeds block 2 non-linearly (readable to R2 about 0.7 in about one seed in three)
- [x] Located: in a flagged seed one of block 2's four coordinates is mostly missing from the embedding (R2 0.34; another 0.70), not sign-folded, not nonlinear-hidden; block 3 unaffected (follow-up 2 in `EVIDENCE.md`)
- [ ] Open (owner's call, nothing started): judge generic-encoder rungs by completeness (readout from the found block against readout from the whole embedding) instead of the angle to the linear image; and whether any training change can stop a coordinate being dropped

- [x] Invertible coupling encoder with the E45 recipe at 4 and 5 blocks (E52, synthetic): information kept (presence 0.94+ on 99 of 100 blocks), but rungs aligned on only 2 of 10 (4 blocks) and 1 of 10 (5 blocks) seeds: refuted
- [ ] Running: E53, the same encoder at 3x the steps on the four failing 4-block seeds (is it too few steps?)

## Stage D: does it help?: NOT DONE
- [x] Identification works (synthetic, under the conditions)
- [x] Correspondence, not speed, carries the split (E38)
- [x] The ladder against a pooled one-shot baseline: equal accuracy, but only the ladder has a detectable gap (E50)
- [x] A payoff test with a co-varying nuisance (E51): the core is more robust (0.99-1.00 against 0.95-0.96) but by less than the registered 0.2: refuted as registered
- [ ] Not attempted: the full Stage D (five matched methods, six metrics)

## Stage R: robot images (the real-data row): RUN, NEGATIVE
- [x] R0 rebuilt the robot data and features on this machine (100 groups x 8 trajectories per task)
- [x] R1 E46: dead output directions in the baseline head on 6 of 6 runs (confirmed)
- [x] R2 E47: the head with the invariance and whitening terms: rank fixed, viewpoint block still not formed (P1 1.1 to 1.25), refuted on both tasks
- [ ] Handoff (E47 refuted): fine-tune the ResNet-50 as the paper does (needs a GPU); and a variant-block term for viewpoint pairs, not started

## Write-up
- [x] Assessment and draft page (`docs/PAPER_ASSESSMENT.md`, `docs/PROJECT_DRAFT.html`)
- [ ] Technical report text (after the Stage R decision)

## Counts
Registered items E1 to E47; the latest 16 outcomes (E31 to E45, plus E46 and E47 pending): see `docs/EVIDENCE.md`.
