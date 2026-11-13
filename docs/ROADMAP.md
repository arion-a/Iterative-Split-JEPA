# Roadmap and live status (updated at each step)

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
- [ ] Running: a confirmatory run of the E45 recipe on fresh seeds (E49, waits for Stage R)

## Stage D: does it help?: NOT DONE
- [x] Identification works (synthetic, under the conditions)
- [x] Correspondence, not speed, carries the split (E38)
- [x] The ladder against a pooled one-shot baseline: equal accuracy, but only the ladder has a detectable gap (E50)
- [x] A payoff test with a co-varying nuisance (E51): the core is more robust (0.99-1.00 against 0.95-0.96) but by less than the registered 0.2: refuted as registered
- [ ] Not attempted: the full Stage D (five matched methods, six metrics)

## Stage R: robot images (the real-data row): RUNNING
- [ ] R0 rebuild the robot data and features on this machine (running: generation, then ResNet-50 features)
- [ ] R1 E46: dead output directions in the baseline head (6 runs)
- [ ] R2 E47: the head with the invariance and whitening terms (6 runs); held-out-scene readouts
- [ ] If E47 is refuted: handoff for fine-tuning the ResNet-50 (GPU), not run here

## Write-up
- [x] Assessment and draft page (`docs/PAPER_ASSESSMENT.md`, `docs/PROJECT_DRAFT.html`)
- [ ] Technical report text (after the Stage R decision)

## Counts
Registered items E1 to E47; the latest 16 outcomes (E31 to E45, plus E46 and E47 pending): see `docs/EVIDENCE.md`.
