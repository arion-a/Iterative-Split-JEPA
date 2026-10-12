# Experiment log (generated from `explog/chain.jsonl`; do not edit)

Chain status at render time: **VALID** — 14 entries, head bdd406aeb3af

Head hash anchors this file; the same hash is quoted in the most recent git commit.

## #0 · genesis (retroactive) · stage - · plan §all
`c31b2652fe9fb453` ← `0000000000000000` · recorded 2026-10-12T21:52:00+00:00 · ref repo initial commit 97b639a

**What.** Start of the experiment log. Plan version: revised Experimental Plan + revised Monograph (Oct 2026). Both revisions fixed the points I had raised: sufficiency tolerance 5%, five per-rung checks, descending eigenvalue order, rung-2 cluster purity measured separately.

**How.** Read all four documents (plan, monograph, ladder bridge note, proof document) and the authors' repo.

**Bearing on objectives OP.** Fixes the rules before any result exists. Everything before this entry is not in the chain; entries marked retroactive were written afterwards from git history and saved run files.

---

## #1 · plan (retroactive) · stage A · plan §3
`ee41cb6b51e88cc2` ← `c31b2652fe9fb453` · recorded 2026-10-12T21:52:00+00:00

**What.** Understood the authors' paper and code: they test ONE split (fast vs slow hidden numbers) on a tiny synthetic world, then on robot pictures. They do not repeat the split; the ladder is our contribution.

**How.** Read arXiv 2610.12349 and cloned splitjepa.github.io (read only). Their simulation trains an 8-number network built as the exact mirror of the scrambling function, then does one eigen-split.

**Output.**
```json
{
 "their_data": "generated on the fly, no dataset; 8 hidden numbers (4+4); 30,000 pairs for the split",
 "their_headline": "slow/fast block R2 about 0.998 / 0.997",
 "their_robot_data": "800 successful ManiSkill trajectories per task, 128x128 images"
}
```

**Bearing on objectives O1.** Gives Stage A its comparison target. Our plan uses a generic network on 16 observed numbers (a deliberately different, harder setup), so any gap to their numbers must be explained.

---

## #2 · implementation (retroactive) · stage core · plan §3
`8c9314df86ed34b2` ← `ee41cb6b51e88cc2` · recorded 2026-10-12T21:52:00+00:00 · event 2026-10-12T16:24:53+00:00 · ref commit e633b34

**What.** Built the 'ideal-formula' core test: a 5-level world where we skip the neural network and test the split mathematics alone, then repeat the split four times in a row.

**How.** src/isj/worlds.py (world and matched pairs), src/isj/engine.py (the split and the ladder), tests/test_core_linear.py.

**Output.**
```json
{
 "tests_passed": "9 of 9",
 "what_they_check": [
  "each of 4 rungs recovers its block within 0.5 degrees",
  "shuffling the pairs removes the split (gap ratio ~1)",
  "a rung given only one direction of variation fails, and only that rung (plus slight contamination of the next)",
  "error shrinks like 1/sqrt(data) when noise is added"
 ]
}
```

**Bearing on objectives O0.** Reproduces the plan's 'validated core' independently in new code (objective O0). This is the maths being right; it says nothing yet about trained networks (that is Stage A).

**Verdict.** PASS

---

## #3 · implementation (retroactive) · stage A · plan §4.1
`5771d0b33efa2e7a` ← `8c9314df86ed34b2` · recorded 2026-10-12T21:52:00+00:00 · event 2026-10-12T16:24:53+00:00 · ref commit e633b34

**What.** Built Stage A: the full pipeline with a trained, frozen network, plus a locked configuration.

**How.** src/isj/encoder.py (network + training), src/isj/stage_a.py (pipeline), src/isj/audits.py (measurements), configs/stage_a.yaml (settings and success thresholds), experiments/run_stage_a.py (runner that refuses to start if the thresholds were edited).

**Output.**
```json
{
 "locked_thresholds_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe"
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Success thresholds from plan 4.1 are locked so results cannot be judged against moved goalposts (OP).

---

## #4 · run (retroactive) · stage A · plan §4.1
`8bb2be1a1ad818b7` ← `5771d0b33efa2e7a` · recorded 2026-10-12T21:52:00+00:00

**What.** FIRST Stage A run (seed 0) FAILED. The network did not recover the hidden values.

**How.** Plan settings as written: variance penalty only, weight 0.01. Result printed to console; no file saved.

**Output.**
```json
{
 "angle_degrees": 83.1,
 "gap_ratio": 1.2,
 "note": "numbers transcribed from the console; no artifact exists for this run",
 "slow_block_R2": 0.426,
 "target": "above 0.9",
 "target_angle": "below 5",
 "target_gap": "above 10"
}
```

**Bearing on objectives O1.** Pass/fail test of O1 came out FAIL. This was debugging round 1 of the 3 allowed by the plan.

**Verdict.** FAIL

---

## #5 · note (retroactive) · stage A · plan §4.1
`c2055d7249be7f56` ← `8bb2be1a1ad818b7` · recorded 2026-10-12T21:52:00+00:00

**What.** Diagnosed the failure: tried four variants of the training objective on seed 0 (console only).

**How.** Same world, same seed, changed only the training objective.

**Output.**
```json
{
 "variants": [
  {
   "angle": 88.7,
   "change": "no stop-gradient",
   "gap": 1.44,
   "slow_R2": 0.146,
   "verdict": "network collapses"
  },
  {
   "angle": 1.2,
   "change": "add covariance penalty 0.04 (keep stop-gradient)",
   "gap": 86.7,
   "slow_R2": 0.989,
   "verdict": "works"
  },
  {
   "angle": 89.7,
   "change": "both changes",
   "gap": 1.72,
   "slow_R2": 0.235,
   "verdict": "collapses"
  },
  {
   "angle": 88.4,
   "change": "authors' SIGReg regulariser, no stop-gradient",
   "gap": 1.18,
   "slow_R2": 0.0,
   "verdict": "collapses"
  }
 ]
}
```

**Bearing on objectives O1.** Plain reading: a penalty on variance alone lets the network copy one useful direction into all 8 outputs; a penalty on correlation between outputs prevents that. This is a training-recipe fix, not a change to what counts as success.

---

## #6 · amendment (retroactive) · stage A · plan §4.1
`210b1c65828bf9ba` ← `c2055d7249be7f56` · recorded 2026-10-12T21:52:00+00:00 · event 2026-10-12T16:30:06+00:00 · ref commit 8fe29a5

**What.** Changed the TRAINING RECIPE (not the success thresholds): added a correlation penalty (weight 0.04) and a stop-gradient on the prediction target.

**How.** configs/stage_a.yaml: encoder.cov_weight 0 -> 0.04, encoder.stop_grad true.

**Output.**
```json
{
 "locked_thresholds_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "locked_thresholds_unchanged": true
}
```

**Bearing on objectives O1, OP.** Keeps the process honest (OP): the thresholds' fingerprint is identical before and after.

---

## #7 · run (retroactive) · stage A · plan §4.1
`3ba065ae55c2e130` ← `210b1c65828bf9ba` · recorded 2026-10-12T21:52:00+00:00

**What.** Full Stage A run set 'r1': 25 runs = 5 seeds x (main + shuffled-pairs control + 3 ablations).

**How.** 5 seeds ran in parallel; each run saved as one immutable JSON file.

**Output.**
```json
{
 "runs": 25
}
```

**Artifacts.** `runs/stage_a/r1/main_seed0.json` (sha256 ad810fd568); `runs/stage_a/r1/main_seed1.json` (sha256 27eeb71bc5); `runs/stage_a/r1/main_seed2.json` (sha256 f1f599da56); `runs/stage_a/r1/main_seed3.json` (sha256 86a0860872); `runs/stage_a/r1/main_seed4.json` (sha256 569557df50); `runs/stage_a/r1/no_inv_seed0.json` (sha256 c043c015aa) … +19 more

**Bearing on objectives O1.** All the raw evidence for O1 lives in these files; their fingerprints are in this entry.

---

## #8 · result (retroactive) · stage A · plan §4.1
`47cd6040606c46a6` ← `3ba065ae55c2e130` · recorded 2026-10-12T21:52:00+00:00

**What.** Stage A main result: the model cleanly separated the slow hidden numbers from the fast ones, on all 5 seeds.

**Output.**
```json
{
 "angle_degrees_range": [
  0.87,
  1.25
 ],
 "fast_block_R2_range": [
  0.984,
  0.992
 ],
 "gap_ratio_range": [
  58.7,
  137.9
 ],
 "leakage_detected_on_any_seed": false,
 "slow_block_R2_range": [
  0.986,
  0.993
 ],
 "thresholds": "R2>0.9, angle<5, gap>10, no leakage"
}
```

**Artifacts.** `runs/stage_a/r1/report.json` (sha256 50909bd3c9)

**Bearing on objectives O1.** O1 is supported: a trained, frozen network plus one spectral split recovers the planted 2-block structure far inside the plan's thresholds. This is a necessary base for Stage B (splitting a second time) but does not itself test the ladder.

**Verdict.** PASS

---

## #9 · result (retroactive) · stage A · plan §4.1
`59d80ca18bb360d0` ← `47cd6040606c46a6` · recorded 2026-10-12T21:52:00+00:00

**What.** Controls: shuffling the pairs destroyed the split; removing prediction or the pairing step also destroyed it.

**Output.**
```json
{
 "no_pairing_step_slow_R2_range": "0.39-0.61",
 "no_prediction_slow_R2_range": "0.22-0.46",
 "no_whitening_slow_R2_range": "0.01-0.14",
 "shuffled_angle_degrees_range": [
  72.8,
  88.4
 ],
 "shuffled_gap_ratio_range": [
  1.0,
  1.02
 ]
}
```

**Bearing on objectives O1, OP.** These runs are supposed to fail. They did, so the main-arm success is attributable to the pairing information and to prediction, not an accident of the setup.

**Verdict.** PASS (controls behave)

---

## #10 · amendment (retroactive) · stage A · plan §2.6
`ddc0773f55c9dd3f` ← `59d80ca18bb360d0` · recorded 2026-10-12T21:52:00+00:00 · event 2026-10-12T16:34:38+00:00 · ref commit 0e0b530

**What.** Changed one CONTROL check after seeing results: the shuffled-pairs control was first marked failed by my own extra bound, which was wrong.

**How.** Old bound: slow-block R2 below 0.5. But picking 4 of 8 directions at random already explains about half the variance, so shuffled runs legitimately scored 0.31-0.54. New bound: recovered angle above 45 degrees (observed 73-88). The plan's own expectation (gap flattens) held throughout.

**Output.**
```json
{
 "pass_thresholds_changed": false
}
```

**Bearing on objectives OP.** Disclosed because it was decided after seeing data. It affects only a control, not the pass criteria.

---

## #11 · result (retroactive) · stage A · plan §4.1
`104e0c621b1fa9ea` ← `ddc0773f55c9dd3f` · recorded 2026-10-12T21:52:00+00:00

**What.** Scrambling-strength sweep: harder worlds are recovered worse.

**Output.**
```json
{
 "strength_0.5": "passes, 5/5 seeds",
 "strength_1.0": {
  "gap": [
   20.2,
   1.4,
   21.5
  ],
  "slow_R2": [
   0.959,
   0.788,
   0.961
  ],
  "verdict": "2 of 3 pass"
 },
 "strength_2.0": {
  "gap": [
   1.3,
   1.3,
   1.2
  ],
  "slow_R2": [
   0.718,
   0.503,
   0.58
  ],
  "verdict": "0 of 3 pass"
 }
}
```

**Artifacts.** `runs/stage_a/coupling1.0/main_seed0.json` (sha256 0ae91be7da); `runs/stage_a/coupling1.0/main_seed1.json` (sha256 aba67dd700); `runs/stage_a/coupling1.0/main_seed2.json` (sha256 439f7abad1); `runs/stage_a/coupling2.0/main_seed0.json` (sha256 cb7b3e4cac); `runs/stage_a/coupling2.0/main_seed1.json` (sha256 66513d6348); `runs/stage_a/coupling2.0/main_seed2.json` (sha256 0fd4f6b77b)

**Bearing on objectives O1.** Shows where this simple recipe starts to fail. It matches the direction the authors report. Plan criteria apply at strength 0.5; the sweep maps the limit. Stage B should be run at 0.5 first.

---

## #12 · blocked (retroactive) · stage A · plan §6
`dc1fa3bb32f2ef7d` ← `104e0c621b1fa9ea` · recorded 2026-10-12T21:52:00+00:00

**What.** Comparison against the authors' own code has NOT been run. The tool permission system blocked executing code cloned from their repo; I did not work around it.

**How.** Needs your explicit approval to run their simulation/run.py (about 270 lines, read in full) on seeds 0-4.

**Bearing on objectives O1, OP.** Plan section 6 makes this the first decisive comparison. Until done, I cannot say whether the difference between our numbers and theirs comes from our generic network or something else.

---

## #13 · note (retroactive) · stage A · plan §4.1
`bdd406aeb3af495b` ← `dc1fa3bb32f2ef7d` · recorded 2026-10-12T21:52:11+00:00

**What.** CORRECTION to entry #5 (and to my earlier chat summary): I said the first failure was the network collapsing onto a single direction. That mechanism was not measured. What was measured: without the correlation penalty the run fails (slow-block R2 0.43, 7 of 8 output directions still active); with it, it works (R2 0.99). Why the penalty helps is a hypothesis, not a finding.

**Bearing on objectives O1, OP.** The fix is empirically supported; the explanation is untested. Do not cite 'rank collapse' as established in any write-up unless a rank check is added.

---
