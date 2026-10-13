# Experiment log (generated from `explog/chain.jsonl`; do not edit)

Chain status at render time: **VALID** — 178 entries, head b1366657559d

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

## #14 · note (retroactive) · stage - · plan §—
`8fd4750d720e4350` ← `bdd406aeb3af495b` · recorded 2026-10-12T22:41:07+00:00

**What.** Plain-language restatement: Reading and rules

**Bearing on objectives OP.** Restates earlier chain entries in plain language; figures recomputed from run files.

---

## #15 · note (retroactive) · stage core · plan §—
`35adf1ea7707201b` ← `8fd4750d720e4350` · recorded 2026-10-12T22:41:07+00:00

**What.** Plain-language restatement: Maths-only core test

**Bearing on objectives OP.** Restates earlier chain entries in plain language; figures recomputed from run files.

---

## #16 · note (retroactive) · stage A · plan §—
`ae11ef51472fc261` ← `35adf1ea7707201b` · recorded 2026-10-12T22:41:07+00:00

**What.** Plain-language restatement: Stage A built

**Bearing on objectives OP.** Restates earlier chain entries in plain language; figures recomputed from run files.

---

## #17 · note (retroactive) · stage A · plan §—
`9dafd55e76e3af63` ← `ae11ef51472fc261` · recorded 2026-10-12T22:41:07+00:00

**What.** Plain-language restatement: First run: failed

**Bearing on objectives OP.** Restates earlier chain entries in plain language; figures recomputed from run files.

---

## #18 · note (retroactive) · stage A · plan §—
`91e2edf0415ed9da` ← `9dafd55e76e3af63` · recorded 2026-10-12T22:41:07+00:00

**What.** Plain-language restatement: Diagnosing the failure

**Bearing on objectives OP.** Restates earlier chain entries in plain language; figures recomputed from run files.

---

## #19 · note (retroactive) · stage A · plan §—
`a26dccfbc359d071` ← `91e2edf0415ed9da` · recorded 2026-10-12T22:41:07+00:00

**What.** Plain-language restatement: Fix applied, rules unchanged

**Bearing on objectives OP.** Restates earlier chain entries in plain language; figures recomputed from run files.

---

## #20 · note (retroactive) · stage A · plan §—
`f25d04b7241be2ed` ← `a26dccfbc359d071` · recorded 2026-10-12T22:41:07+00:00

**What.** Plain-language restatement: Main result: Stage A passes

**Bearing on objectives OP.** Restates earlier chain entries in plain language; figures recomputed from run files.

---

## #21 · note (retroactive) · stage A · plan §—
`1b3723851d86a751` ← `f25d04b7241be2ed` · recorded 2026-10-12T22:41:07+00:00

**What.** Plain-language restatement: Controls: they fail as they should

**Bearing on objectives OP.** Restates earlier chain entries in plain language; figures recomputed from run files.

---

## #22 · note (retroactive) · stage A · plan §—
`80cc306cdf87a4a9` ← `1b3723851d86a751` · recorded 2026-10-12T22:41:07+00:00

**What.** Plain-language restatement: Control rule corrected (disclosed)

**Bearing on objectives OP.** Restates earlier chain entries in plain language; figures recomputed from run files.

---

## #23 · note (retroactive) · stage A · plan §—
`5cd11ec699720a32` ← `80cc306cdf87a4a9` · recorded 2026-10-12T22:41:07+00:00

**What.** Plain-language restatement: Harder worlds

**Bearing on objectives OP.** Restates earlier chain entries in plain language; figures recomputed from run files.

---

## #24 · note (retroactive) · stage A · plan §—
`e5f4f87c619c3392` ← `5cd11ec699720a32` · recorded 2026-10-12T22:41:07+00:00

**What.** Plain-language restatement: Paper's own simulation: waiting for you

**Bearing on objectives OP.** Restates earlier chain entries in plain language; figures recomputed from run files.

---

## #25 · implementation · stage log · plan §—
`d48139201d2f567a` ← `e5f4f87c619c3392` · recorded 2026-10-12T22:43:08+00:00

**What.** Built the plain-language log page and the helpers that feed it.

**How.** experiments/build_log_page.py renders only entries that carry a 'plain' block; experiments/restate_log_plain.py re-explained the first 14 entries; run_stage_a.py now writes its own plain rows; explog/stages.json holds the stage tracker.

---

## #26 · run · stage A · plan §6
`0bbc095c740069c0` ← `d48139201d2f567a` · recorded 2026-10-12T23:25:41+00:00 · ref commit a8d65ec of the authors' repo

**What.** Ran the authors' own simulation script, unmodified, on seeds 0-4.

**How.** simulation/run.py from github.com/splitjepa/splitjepa.github.io (commit a8d65ec), CPU, 10,000 training steps, run as published after your approval.

**Output.**
```json
{
 "summary": [
  "Paper's SplitJEPA, run by the authors' script, 5 seeds (ours in brackets):",
  "invariant_r2 0.9980 ± 0.0014  [ours 0.9889 ± 0.0028]",
  "variant_r2 0.9974 ± 0.0018  [ours 0.9889 ± 0.0030]",
  "global_r2 0.9977 ± 0.0016  [ours 0.9890 ± 0.0028]",
  "a12_fro 0.0034 ± 0.0020  [ours 0.0075 ± 0.0024]",
  "a21_fro 0.0233 ± 0.0027  [ours 0.0223 ± 0.0043]",
  "block_purity 0.99993 ± 0.00002  [ours 0.99993 ± 0.00003]",
  "Paper's LeJEPA baseline (no spectral head), same script:",
  "invariant_r2 0.9619 ± 0.0327 (ours without spectral head: 0.486 ± 0.080)",
  "a12_fro 0.3292 ± 0.2138, a21_fro 0.3314 ± 0.2159 (ours: about 1.42)",
  "global_r2 0.9977 ± 0.0016 (identical to SplitJEPA, as in the paper)"
 ]
}
```

**Artifacts.** `runs/stage_a/reference/seed=0.json` (sha256 badfd60662); `runs/stage_a/reference/seed=1.json` (sha256 9ec5c853d0); `runs/stage_a/reference/seed=2.json` (sha256 858eadef53); `runs/stage_a/reference/seed=3.json` (sha256 77cf34ce3a); `runs/stage_a/reference/seed=4.json` (sha256 aa95a144a8)

---

## #27 · plan · stage A · plan §6
`3582ebceda02ec1f` ← `0bbc095c740069c0` · recorded 2026-10-13T00:29:24+00:00

**What.** Encoder-recipe ablations for Stage A: find where our ~0.01 gap in invariant_r2 (ours 0.989, authors' script 0.998) comes from.

**How.** Five variants x 5 seeds, main arm only, one change at a time from our Stage A config (see config overrides in run directories runs/stage_a/enc_*).

**Output.**
```json
{
 "reading_rule": "A variant 'explains' the gap if its mean invariant_r2 closes at least half of the 0.009 difference to 0.998; judged on 5-seed means.",
 "variants": [
  "obs_dim 8",
  "steps 10000",
  "obs_dim 8 + steps 10000",
  "paper objective (alignment+SIGReg) on our generic network, obs_dim 8",
  "authors-style mirror encoder (own reimplementation) + paper objective, obs_dim 8, 10000 steps"
 ]
}
```

---

## #28 · run · stage A · plan §4.1
`dd0ef666b6424650` ← `3582ebceda02ec1f` · recorded 2026-10-13T00:30:57+00:00

**What.** Stage A run set started: runs/stage_a/enc_obs8, seeds [1], overrides ['world.obs_dim=8']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8"
 ],
 "seeds": [
  1
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #29 · run · stage A · plan §4.1
`ccefb07dc6670313` ← `dd0ef666b6424650` · recorded 2026-10-13T00:30:57+00:00

**What.** Stage A run set started: runs/stage_a/enc_obs8, seeds [3], overrides ['world.obs_dim=8']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8"
 ],
 "seeds": [
  3
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #30 · run · stage A · plan §4.1
`9ae606ea7ae402a2` ← `ccefb07dc6670313` · recorded 2026-10-13T00:30:58+00:00

**What.** Stage A run set started: runs/stage_a/enc_obs8, seeds [2], overrides ['world.obs_dim=8']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8"
 ],
 "seeds": [
  2
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #31 · run · stage A · plan §4.1
`31086b0813eda53c` ← `9ae606ea7ae402a2` · recorded 2026-10-13T00:30:58+00:00

**What.** Stage A run set started: runs/stage_a/enc_obs8, seeds [0], overrides ['world.obs_dim=8']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8"
 ],
 "seeds": [
  0
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #32 · run · stage A · plan §4.1
`af0ab2016a5a8073` ← `31086b0813eda53c` · recorded 2026-10-13T00:30:58+00:00

**What.** Stage A run set started: runs/stage_a/enc_obs8, seeds [4], overrides ['world.obs_dim=8']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8"
 ],
 "seeds": [
  4
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #33 · run · stage A · plan §4.1
`cc5ca91ada1935e4` ← `af0ab2016a5a8073` · recorded 2026-10-13T00:31:44+00:00

**What.** Stage A arm=main seed=4 finished

**Output.**
```json
{
 "angle_inv_deg": 0.83205,
 "angle_var_deg": 0.29255,
 "gap_ratio": 114.65996,
 "global_r2": 0.99041,
 "invariant_r2": 0.99139,
 "leak_any_significant": false,
 "leak_r2_max": -0.00057,
 "seconds": 45.8,
 "selected_d": 4,
 "variant_r2": 0.98925
}
```

**Artifacts.** `runs/stage_a/enc_obs8/main_seed4.json` (sha256 15d873f8dd)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #34 · result · stage A · plan §4.1
`a7b667b58d6a8715` ← `cc5ca91ada1935e4` · recorded 2026-10-13T00:31:44+00:00

**What.** Stage A aggregate over seeds [4]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_obs8/report.json` (sha256 d95206c59b)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #35 · run · stage A · plan §4.1
`31c10fd09334f1fa` ← `a7b667b58d6a8715` · recorded 2026-10-13T00:31:44+00:00

**What.** Stage A arm=main seed=1 finished

**Output.**
```json
{
 "angle_inv_deg": 1.12516,
 "angle_var_deg": 0.62604,
 "gap_ratio": 69.60754,
 "global_r2": 0.98766,
 "invariant_r2": 0.98611,
 "leak_any_significant": false,
 "leak_r2_max": -0.00032,
 "seconds": 46.7,
 "selected_d": 4,
 "variant_r2": 0.98909
}
```

**Artifacts.** `runs/stage_a/enc_obs8/main_seed1.json` (sha256 f6082b5224)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #36 · result · stage A · plan §4.1
`5223849cc505cd6a` ← `31c10fd09334f1fa` · recorded 2026-10-13T00:31:44+00:00

**What.** Stage A aggregate over seeds [1]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_obs8/report.json` (sha256 5ce7ba5288)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #37 · run · stage A · plan §4.1
`0300616554f870ff` ← `5223849cc505cd6a` · recorded 2026-10-13T00:31:44+00:00

**What.** Stage A arm=main seed=0 finished

**Output.**
```json
{
 "angle_inv_deg": 1.34807,
 "angle_var_deg": 0.45388,
 "gap_ratio": 75.28947,
 "global_r2": 0.99007,
 "invariant_r2": 0.98945,
 "leak_any_significant": false,
 "leak_r2_max": -2e-05,
 "seconds": 46.4,
 "selected_d": 4,
 "variant_r2": 0.99032
}
```

**Artifacts.** `runs/stage_a/enc_obs8/main_seed0.json` (sha256 af3ba357eb)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #38 · result · stage A · plan §4.1
`724b125f33b62e10` ← `0300616554f870ff` · recorded 2026-10-13T00:31:44+00:00

**What.** Stage A aggregate over seeds [0]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_obs8/report.json` (sha256 80f7ee23cd)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #39 · run · stage A · plan §4.1
`59707818dde8bc40` ← `724b125f33b62e10` · recorded 2026-10-13T00:31:45+00:00

**What.** Stage A arm=main seed=2 finished

**Output.**
```json
{
 "angle_inv_deg": 0.88821,
 "angle_var_deg": 0.21206,
 "gap_ratio": 112.47668,
 "global_r2": 0.99174,
 "invariant_r2": 0.99193,
 "leak_any_significant": false,
 "leak_r2_max": -0.00117,
 "seconds": 47.1,
 "selected_d": 4,
 "variant_r2": 0.99149
}
```

**Artifacts.** `runs/stage_a/enc_obs8/main_seed2.json` (sha256 7809f9c5c5)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #40 · result · stage A · plan §4.1
`f7ecc4abaee7d728` ← `59707818dde8bc40` · recorded 2026-10-13T00:31:45+00:00

**What.** Stage A aggregate over seeds [2]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_obs8/report.json` (sha256 9468f63ffd)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #41 · run · stage A · plan §4.1
`8a687c1fb778e9c1` ← `f7ecc4abaee7d728` · recorded 2026-10-13T00:31:45+00:00

**What.** Stage A arm=main seed=3 finished

**Output.**
```json
{
 "angle_inv_deg": 1.03726,
 "angle_var_deg": 0.20559,
 "gap_ratio": 102.89003,
 "global_r2": 0.99045,
 "invariant_r2": 0.99089,
 "leak_any_significant": false,
 "leak_r2_max": -0.00029,
 "seconds": 47.6,
 "selected_d": 4,
 "variant_r2": 0.98994
}
```

**Artifacts.** `runs/stage_a/enc_obs8/main_seed3.json` (sha256 80811b1de0)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #42 · result · stage A · plan §4.1
`e46fe0df4535d4c7` ← `8a687c1fb778e9c1` · recorded 2026-10-13T00:31:45+00:00

**What.** Stage A aggregate over seeds [3]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_obs8/report.json` (sha256 0ec1179517)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #43 · run · stage A · plan §4.1
`ec8bbeeeae081c61` ← `e46fe0df4535d4c7` · recorded 2026-10-13T00:31:48+00:00

**What.** Stage A run set started: runs/stage_a/enc_steps10k, seeds [3], overrides ['encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 16,
 "overrides": [
  "encoder.steps=10000"
 ],
 "seeds": [
  3
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #44 · run · stage A · plan §4.1
`104f3b2a7945122a` ← `ec8bbeeeae081c61` · recorded 2026-10-13T00:31:48+00:00

**What.** Stage A run set started: runs/stage_a/enc_steps10k, seeds [1], overrides ['encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 16,
 "overrides": [
  "encoder.steps=10000"
 ],
 "seeds": [
  1
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #45 · run · stage A · plan §4.1
`d50973e0cb18f1d3` ← `104f3b2a7945122a` · recorded 2026-10-13T00:31:48+00:00

**What.** Stage A run set started: runs/stage_a/enc_steps10k, seeds [2], overrides ['encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 16,
 "overrides": [
  "encoder.steps=10000"
 ],
 "seeds": [
  2
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #46 · run · stage A · plan §4.1
`851c81d1ec634fcc` ← `d50973e0cb18f1d3` · recorded 2026-10-13T00:31:48+00:00

**What.** Stage A run set started: runs/stage_a/enc_steps10k, seeds [0], overrides ['encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 16,
 "overrides": [
  "encoder.steps=10000"
 ],
 "seeds": [
  0
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #47 · run · stage A · plan §4.1
`04c913ac1798cad3` ← `851c81d1ec634fcc` · recorded 2026-10-13T00:31:48+00:00

**What.** Stage A run set started: runs/stage_a/enc_steps10k, seeds [4], overrides ['encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 16,
 "overrides": [
  "encoder.steps=10000"
 ],
 "seeds": [
  4
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #48 · run · stage A · plan §4.1
`7cf4ee6f9e70adab` ← `04c913ac1798cad3` · recorded 2026-10-13T00:32:44+00:00

**What.** Stage A arm=main seed=4 finished

**Output.**
```json
{
 "angle_inv_deg": 1.22046,
 "angle_var_deg": 0.28432,
 "gap_ratio": 81.72709,
 "global_r2": 0.98877,
 "invariant_r2": 0.98916,
 "leak_any_significant": false,
 "leak_r2_max": 4e-05,
 "seconds": 56.1,
 "selected_d": 4,
 "variant_r2": 0.98825
}
```

**Artifacts.** `runs/stage_a/enc_steps10k/main_seed4.json` (sha256 2788ae0884)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #49 · result · stage A · plan §4.1
`39a93862a823f8af` ← `7cf4ee6f9e70adab` · recorded 2026-10-13T00:32:44+00:00

**What.** Stage A aggregate over seeds [4]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_steps10k/report.json` (sha256 d95206c59b)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #50 · run · stage A · plan §4.1
`f0c8603e0557c576` ← `39a93862a823f8af` · recorded 2026-10-13T00:32:45+00:00

**What.** Stage A arm=main seed=3 finished

**Output.**
```json
{
 "angle_inv_deg": 0.9663,
 "angle_var_deg": 0.2859,
 "gap_ratio": 119.36984,
 "global_r2": 0.9922,
 "invariant_r2": 0.99277,
 "leak_any_significant": false,
 "leak_r2_max": -0.0009,
 "seconds": 56.7,
 "selected_d": 4,
 "variant_r2": 0.99154
}
```

**Artifacts.** `runs/stage_a/enc_steps10k/main_seed3.json` (sha256 41f587156a)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #51 · result · stage A · plan §4.1
`254b7ddda55a185b` ← `f0c8603e0557c576` · recorded 2026-10-13T00:32:45+00:00

**What.** Stage A aggregate over seeds [3]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_steps10k/report.json` (sha256 0ec1179517)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #52 · run · stage A · plan §4.1
`115a71c9ad0401e0` ← `254b7ddda55a185b` · recorded 2026-10-13T00:32:45+00:00

**What.** Stage A arm=main seed=1 finished

**Output.**
```json
{
 "angle_inv_deg": 1.49231,
 "angle_var_deg": 0.38169,
 "gap_ratio": 62.02815,
 "global_r2": 0.98837,
 "invariant_r2": 0.98714,
 "leak_any_significant": false,
 "leak_r2_max": -0.00029,
 "seconds": 57.0,
 "selected_d": 4,
 "variant_r2": 0.9894
}
```

**Artifacts.** `runs/stage_a/enc_steps10k/main_seed1.json` (sha256 320e58f1ab)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #53 · result · stage A · plan §4.1
`f6ca7c6760d7decb` ← `115a71c9ad0401e0` · recorded 2026-10-13T00:32:45+00:00

**What.** Stage A aggregate over seeds [1]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_steps10k/report.json` (sha256 5ce7ba5288)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #54 · run · stage A · plan §4.1
`d1b8f5c34679aae6` ← `f6ca7c6760d7decb` · recorded 2026-10-13T00:32:45+00:00

**What.** Stage A arm=main seed=2 finished

**Output.**
```json
{
 "angle_inv_deg": 1.12365,
 "angle_var_deg": 0.17769,
 "gap_ratio": 117.80727,
 "global_r2": 0.99276,
 "invariant_r2": 0.99265,
 "leak_any_significant": false,
 "leak_r2_max": 1e-05,
 "seconds": 57.3,
 "selected_d": 4,
 "variant_r2": 0.99266
}
```

**Artifacts.** `runs/stage_a/enc_steps10k/main_seed2.json` (sha256 82c17d5a2e)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #55 · result · stage A · plan §4.1
`50e0d39f8977be57` ← `d1b8f5c34679aae6` · recorded 2026-10-13T00:32:45+00:00

**What.** Stage A aggregate over seeds [2]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_steps10k/report.json` (sha256 9468f63ffd)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #56 · run · stage A · plan §4.1
`538b216083b46bf7` ← `50e0d39f8977be57` · recorded 2026-10-13T00:32:45+00:00

**What.** Stage A arm=main seed=0 finished

**Output.**
```json
{
 "angle_inv_deg": 0.96482,
 "angle_var_deg": 0.27837,
 "gap_ratio": 95.07519,
 "global_r2": 0.99119,
 "invariant_r2": 0.98996,
 "leak_any_significant": false,
 "leak_r2_max": -0.00108,
 "seconds": 57.4,
 "selected_d": 4,
 "variant_r2": 0.99228
}
```

**Artifacts.** `runs/stage_a/enc_steps10k/main_seed0.json` (sha256 9c6a91ab19)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #57 · result · stage A · plan §4.1
`6d3edb6d5c2ff49a` ← `538b216083b46bf7` · recorded 2026-10-13T00:32:45+00:00

**What.** Stage A aggregate over seeds [0]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_steps10k/report.json` (sha256 80f7ee23cd)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #58 · run · stage A · plan §4.1
`af32ed52d5cb25c6` ← `6d3edb6d5c2ff49a` · recorded 2026-10-13T00:32:48+00:00

**What.** Stage A run set started: runs/stage_a/enc_obs8_steps10k, seeds [1], overrides ['world.obs_dim=8', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.steps=10000"
 ],
 "seeds": [
  1
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #59 · run · stage A · plan §4.1
`ec44254513c24663` ← `af32ed52d5cb25c6` · recorded 2026-10-13T00:32:48+00:00

**What.** Stage A run set started: runs/stage_a/enc_obs8_steps10k, seeds [2], overrides ['world.obs_dim=8', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.steps=10000"
 ],
 "seeds": [
  2
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #60 · run · stage A · plan §4.1
`5682c9d60d6e4134` ← `ec44254513c24663` · recorded 2026-10-13T00:32:49+00:00

**What.** Stage A run set started: runs/stage_a/enc_obs8_steps10k, seeds [3], overrides ['world.obs_dim=8', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.steps=10000"
 ],
 "seeds": [
  3
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #61 · run · stage A · plan §4.1
`bc432c79b57465a8` ← `5682c9d60d6e4134` · recorded 2026-10-13T00:32:49+00:00

**What.** Stage A run set started: runs/stage_a/enc_obs8_steps10k, seeds [4], overrides ['world.obs_dim=8', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.steps=10000"
 ],
 "seeds": [
  4
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #62 · run · stage A · plan §4.1
`2b063ec1960b8606` ← `bc432c79b57465a8` · recorded 2026-10-13T00:32:49+00:00

**What.** Stage A run set started: runs/stage_a/enc_obs8_steps10k, seeds [0], overrides ['world.obs_dim=8', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.steps=10000"
 ],
 "seeds": [
  0
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #63 · run · stage A · plan §4.1
`5f123dd124a41737` ← `2b063ec1960b8606` · recorded 2026-10-13T00:33:58+00:00

**What.** Stage A arm=main seed=3 finished

**Output.**
```json
{
 "angle_inv_deg": 1.07112,
 "angle_var_deg": 0.21902,
 "gap_ratio": 137.67907,
 "global_r2": 0.99241,
 "invariant_r2": 0.99291,
 "leak_any_significant": false,
 "leak_r2_max": -0.00083,
 "seconds": 69.4,
 "selected_d": 4,
 "variant_r2": 0.99175
}
```

**Artifacts.** `runs/stage_a/enc_obs8_steps10k/main_seed3.json` (sha256 c54aef7c11)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #64 · result · stage A · plan §4.1
`f3bfc417be8a3b79` ← `5f123dd124a41737` · recorded 2026-10-13T00:33:58+00:00

**What.** Stage A aggregate over seeds [3]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_obs8_steps10k/report.json` (sha256 0ec1179517)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #65 · run · stage A · plan §4.1
`08e9e2bc32b40af5` ← `f3bfc417be8a3b79` · recorded 2026-10-13T00:33:58+00:00

**What.** Stage A arm=main seed=0 finished

**Output.**
```json
{
 "angle_inv_deg": 0.87656,
 "angle_var_deg": 0.42428,
 "gap_ratio": 83.66134,
 "global_r2": 0.99108,
 "invariant_r2": 0.99046,
 "leak_any_significant": false,
 "leak_r2_max": -0.00098,
 "seconds": 69.7,
 "selected_d": 4,
 "variant_r2": 0.99156
}
```

**Artifacts.** `runs/stage_a/enc_obs8_steps10k/main_seed0.json` (sha256 d0f4b553b4)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #66 · result · stage A · plan §4.1
`10c232370f437fd0` ← `08e9e2bc32b40af5` · recorded 2026-10-13T00:33:58+00:00

**What.** Stage A aggregate over seeds [0]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_obs8_steps10k/report.json` (sha256 80f7ee23cd)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #67 · run · stage A · plan §4.1
`d99395b8a5a22ab5` ← `10c232370f437fd0` · recorded 2026-10-13T00:33:59+00:00

**What.** Stage A arm=main seed=4 finished

**Output.**
```json
{
 "angle_inv_deg": 1.14151,
 "angle_var_deg": 0.2693,
 "gap_ratio": 136.58002,
 "global_r2": 0.99219,
 "invariant_r2": 0.99299,
 "leak_any_significant": false,
 "leak_r2_max": 2e-05,
 "seconds": 69.9,
 "selected_d": 4,
 "variant_r2": 0.99127
}
```

**Artifacts.** `runs/stage_a/enc_obs8_steps10k/main_seed4.json` (sha256 9b8e2143bd)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #68 · result · stage A · plan §4.1
`26d4195acafe6ae3` ← `d99395b8a5a22ab5` · recorded 2026-10-13T00:33:59+00:00

**What.** Stage A aggregate over seeds [4]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_obs8_steps10k/report.json` (sha256 d95206c59b)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #69 · run · stage A · plan §4.1
`473bd4701f67747d` ← `26d4195acafe6ae3` · recorded 2026-10-13T00:33:59+00:00

**What.** Stage A arm=main seed=1 finished

**Output.**
```json
{
 "angle_inv_deg": 1.22914,
 "angle_var_deg": 0.41631,
 "gap_ratio": 79.21165,
 "global_r2": 0.98932,
 "invariant_r2": 0.98807,
 "leak_any_significant": false,
 "leak_r2_max": -0.00029,
 "seconds": 70.3,
 "selected_d": 4,
 "variant_r2": 0.99044
}
```

**Artifacts.** `runs/stage_a/enc_obs8_steps10k/main_seed1.json` (sha256 17bd5ed5f0)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #70 · result · stage A · plan §4.1
`6d40776a821e0ef1` ← `473bd4701f67747d` · recorded 2026-10-13T00:33:59+00:00

**What.** Stage A aggregate over seeds [1]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_obs8_steps10k/report.json` (sha256 5ce7ba5288)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #71 · run · stage A · plan §4.1
`68e771c64a353fb2` ← `6d40776a821e0ef1` · recorded 2026-10-13T00:34:00+00:00

**What.** Stage A arm=main seed=2 finished

**Output.**
```json
{
 "angle_inv_deg": 0.97306,
 "angle_var_deg": 0.20922,
 "gap_ratio": 148.47128,
 "global_r2": 0.993,
 "invariant_r2": 0.99363,
 "leak_any_significant": false,
 "leak_r2_max": 1e-05,
 "seconds": 71.7,
 "selected_d": 4,
 "variant_r2": 0.9922
}
```

**Artifacts.** `runs/stage_a/enc_obs8_steps10k/main_seed2.json` (sha256 76bda6b9b4)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #72 · result · stage A · plan §4.1
`034aca2fb978ace5` ← `68e771c64a353fb2` · recorded 2026-10-13T00:34:00+00:00

**What.** Stage A aggregate over seeds [2]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_obs8_steps10k/report.json` (sha256 9468f63ffd)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #73 · run · stage A · plan §4.1
`1b4c38412909bd40` ← `034aca2fb978ace5` · recorded 2026-10-13T00:34:04+00:00

**What.** Stage A run set started: runs/stage_a/enc_lejepa_mlp, seeds [3], overrides ['world.obs_dim=8', 'encoder.objective=lejepa']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.objective=lejepa"
 ],
 "seeds": [
  3
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #74 · run · stage A · plan §4.1
`212c5b678a2374e9` ← `1b4c38412909bd40` · recorded 2026-10-13T00:34:04+00:00

**What.** Stage A run set started: runs/stage_a/enc_lejepa_mlp, seeds [0], overrides ['world.obs_dim=8', 'encoder.objective=lejepa']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.objective=lejepa"
 ],
 "seeds": [
  0
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #75 · run · stage A · plan §4.1
`cd4f894505ecfa3b` ← `212c5b678a2374e9` · recorded 2026-10-13T00:34:04+00:00

**What.** Stage A run set started: runs/stage_a/enc_lejepa_mlp, seeds [4], overrides ['world.obs_dim=8', 'encoder.objective=lejepa']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.objective=lejepa"
 ],
 "seeds": [
  4
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #76 · run · stage A · plan §4.1
`dace66c2a133f560` ← `cd4f894505ecfa3b` · recorded 2026-10-13T00:34:05+00:00

**What.** Stage A run set started: runs/stage_a/enc_lejepa_mlp, seeds [1], overrides ['world.obs_dim=8', 'encoder.objective=lejepa']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.objective=lejepa"
 ],
 "seeds": [
  1
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #77 · run · stage A · plan §4.1
`3e94ada9ab806972` ← `dace66c2a133f560` · recorded 2026-10-13T00:34:05+00:00

**What.** Stage A run set started: runs/stage_a/enc_lejepa_mlp, seeds [2], overrides ['world.obs_dim=8', 'encoder.objective=lejepa']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.objective=lejepa"
 ],
 "seeds": [
  2
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #78 · run · stage A · plan §4.1
`1888da1c736fdcb8` ← `3e94ada9ab806972` · recorded 2026-10-13T00:41:25+00:00

**What.** Stage A arm=main seed=3 finished

**Output.**
```json
{
 "angle_inv_deg": 71.22747,
 "angle_var_deg": 82.12871,
 "gap_ratio": 1.1635,
 "global_r2": 0.00081,
 "invariant_r2": -0.00029,
 "leak_any_significant": false,
 "leak_r2_max": -9e-05,
 "seconds": 441.1,
 "selected_d": 7,
 "variant_r2": 0.00186
}
```

**Artifacts.** `runs/stage_a/enc_lejepa_mlp/main_seed3.json` (sha256 a1914daaad)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #79 · result · stage A · plan §4.1
`bb0dc2e62fb976d2` ← `1888da1c736fdcb8` · recorded 2026-10-13T00:41:25+00:00

**What.** Stage A aggregate over seeds [3]: main arm FAIL; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": false,
  "angle": false,
  "gap_ratio": false,
  "invariant_r2": false,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_lejepa_mlp/report.json` (sha256 a102d930b4)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** FAIL

---

## #80 · run · stage A · plan §4.1
`e6ab804ece0e20f5` ← `bb0dc2e62fb976d2` · recorded 2026-10-13T00:41:38+00:00

**What.** Stage A arm=main seed=2 finished

**Output.**
```json
{
 "angle_inv_deg": 88.92768,
 "angle_var_deg": 53.66025,
 "gap_ratio": 1.07075,
 "global_r2": -0.00133,
 "invariant_r2": -0.00062,
 "leak_any_significant": false,
 "leak_r2_max": 0.00032,
 "seconds": 453.3,
 "selected_d": 7,
 "variant_r2": -0.00136
}
```

**Artifacts.** `runs/stage_a/enc_lejepa_mlp/main_seed2.json` (sha256 5991eeac6c)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #81 · result · stage A · plan §4.1
`3527bf306b88262b` ← `e6ab804ece0e20f5` · recorded 2026-10-13T00:41:38+00:00

**What.** Stage A aggregate over seeds [2]: main arm FAIL; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": false,
  "angle": false,
  "gap_ratio": false,
  "invariant_r2": false,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_lejepa_mlp/report.json` (sha256 71b907d9c6)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** FAIL

---

## #82 · run · stage A · plan §4.1
`6bc9d85c3930064b` ← `3527bf306b88262b` · recorded 2026-10-13T00:41:38+00:00

**What.** Stage A arm=main seed=1 finished

**Output.**
```json
{
 "angle_inv_deg": 87.88998,
 "angle_var_deg": 75.90703,
 "gap_ratio": 1.05322,
 "global_r2": -0.00052,
 "invariant_r2": -0.00012,
 "leak_any_significant": false,
 "leak_r2_max": -4e-05,
 "seconds": 453.8,
 "selected_d": 7,
 "variant_r2": 1e-05
}
```

**Artifacts.** `runs/stage_a/enc_lejepa_mlp/main_seed1.json` (sha256 b954ff99b7)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #83 · result · stage A · plan §4.1
`f7e6a35a00469c5a` ← `6bc9d85c3930064b` · recorded 2026-10-13T00:41:38+00:00

**What.** Stage A aggregate over seeds [1]: main arm FAIL; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": false,
  "angle": false,
  "gap_ratio": false,
  "invariant_r2": false,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_lejepa_mlp/report.json` (sha256 86011d9240)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** FAIL

---

## #84 · run · stage A · plan §4.1
`97f8a92b535ec958` ← `f7e6a35a00469c5a` · recorded 2026-10-13T00:41:38+00:00

**What.** Stage A arm=main seed=0 finished

**Output.**
```json
{
 "angle_inv_deg": 81.74979,
 "angle_var_deg": 82.03834,
 "gap_ratio": 1.36589,
 "global_r2": -0.0018,
 "invariant_r2": -0.00049,
 "leak_any_significant": false,
 "leak_r2_max": -0.00044,
 "seconds": 453.9,
 "selected_d": 7,
 "variant_r2": -0.00124
}
```

**Artifacts.** `runs/stage_a/enc_lejepa_mlp/main_seed0.json` (sha256 f531dca75b)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #85 · result · stage A · plan §4.1
`c9d83fb15fe949d1` ← `97f8a92b535ec958` · recorded 2026-10-13T00:41:38+00:00

**What.** Stage A aggregate over seeds [0]: main arm FAIL; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": false,
  "angle": false,
  "gap_ratio": false,
  "invariant_r2": false,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_lejepa_mlp/report.json` (sha256 ea6bf35c65)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** FAIL

---

## #86 · run · stage A · plan §4.1
`7aca60bdd689bf59` ← `c9d83fb15fe949d1` · recorded 2026-10-13T00:41:39+00:00

**What.** Stage A arm=main seed=4 finished

**Output.**
```json
{
 "angle_inv_deg": 81.85034,
 "angle_var_deg": 78.13753,
 "gap_ratio": 1.12158,
 "global_r2": 0.00097,
 "invariant_r2": -0.00047,
 "leak_any_significant": true,
 "leak_r2_max": 0.00147,
 "seconds": 454.6,
 "selected_d": 7,
 "variant_r2": -0.00018
}
```

**Artifacts.** `runs/stage_a/enc_lejepa_mlp/main_seed4.json` (sha256 837b0c6348)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #87 · result · stage A · plan §4.1
`0ec018daa6c83206` ← `7aca60bdd689bf59` · recorded 2026-10-13T00:41:39+00:00

**What.** Stage A aggregate over seeds [4]: main arm FAIL; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": false,
  "angle": false,
  "gap_ratio": false,
  "invariant_r2": false,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_lejepa_mlp/report.json` (sha256 28ed08bda9)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** FAIL

---

## #88 · run · stage A · plan §4.1
`31541b421165f3cf` ← `0ec018daa6c83206` · recorded 2026-10-13T00:41:42+00:00

**What.** Stage A run set started: runs/stage_a/enc_mirror, seeds [3], overrides ['world.obs_dim=8', 'encoder.arch=inverse_coupling', 'encoder.objective=lejepa', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.arch=inverse_coupling",
  "encoder.objective=lejepa",
  "encoder.steps=10000"
 ],
 "seeds": [
  3
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #89 · run · stage A · plan §4.1
`c3f61be5cd52807f` ← `31541b421165f3cf` · recorded 2026-10-13T00:41:42+00:00

**What.** Stage A run set started: runs/stage_a/enc_mirror, seeds [4], overrides ['world.obs_dim=8', 'encoder.arch=inverse_coupling', 'encoder.objective=lejepa', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.arch=inverse_coupling",
  "encoder.objective=lejepa",
  "encoder.steps=10000"
 ],
 "seeds": [
  4
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #90 · run · stage A · plan §4.1
`be8a1161e7f891ec` ← `c3f61be5cd52807f` · recorded 2026-10-13T00:41:42+00:00

**What.** Stage A run set started: runs/stage_a/enc_mirror, seeds [0], overrides ['world.obs_dim=8', 'encoder.arch=inverse_coupling', 'encoder.objective=lejepa', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.arch=inverse_coupling",
  "encoder.objective=lejepa",
  "encoder.steps=10000"
 ],
 "seeds": [
  0
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #91 · run · stage A · plan §4.1
`cc1af8e6c0e089e4` ← `be8a1161e7f891ec` · recorded 2026-10-13T00:41:42+00:00

**What.** Stage A run set started: runs/stage_a/enc_mirror, seeds [2], overrides ['world.obs_dim=8', 'encoder.arch=inverse_coupling', 'encoder.objective=lejepa', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.arch=inverse_coupling",
  "encoder.objective=lejepa",
  "encoder.steps=10000"
 ],
 "seeds": [
  2
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #92 · run · stage A · plan §4.1
`fa2815daff899c2d` ← `cc1af8e6c0e089e4` · recorded 2026-10-13T00:41:42+00:00

**What.** Stage A run set started: runs/stage_a/enc_mirror, seeds [1], overrides ['world.obs_dim=8', 'encoder.arch=inverse_coupling', 'encoder.objective=lejepa', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.arch=inverse_coupling",
  "encoder.objective=lejepa",
  "encoder.steps=10000"
 ],
 "seeds": [
  1
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #93 · run · stage A · plan §4.1
`7a325d8e75acd5af` ← `fa2815daff899c2d` · recorded 2026-10-13T00:50:44+00:00

**What.** Stage A arm=main seed=2 finished

**Output.**
```json
{
 "angle_inv_deg": 0.96089,
 "angle_var_deg": 0.19124,
 "gap_ratio": 186.09853,
 "global_r2": 0.99606,
 "invariant_r2": 0.9962,
 "leak_any_significant": false,
 "leak_r2_max": -0.0,
 "seconds": 542.2,
 "selected_d": 4,
 "variant_r2": 0.99578
}
```

**Artifacts.** `runs/stage_a/enc_mirror/main_seed2.json` (sha256 791fe646c2)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #94 · result · stage A · plan §4.1
`1094b2e92b547433` ← `7a325d8e75acd5af` · recorded 2026-10-13T00:50:44+00:00

**What.** Stage A aggregate over seeds [2]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_mirror/report.json` (sha256 01930d1961)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #95 · run · stage A · plan §4.1
`d0b922d9c274467a` ← `1094b2e92b547433` · recorded 2026-10-13T00:50:46+00:00

**What.** Stage A arm=main seed=3 finished

**Output.**
```json
{
 "angle_inv_deg": 1.00327,
 "angle_var_deg": 0.25653,
 "gap_ratio": 117.05117,
 "global_r2": 0.99628,
 "invariant_r2": 0.99558,
 "leak_any_significant": false,
 "leak_r2_max": -0.00097,
 "seconds": 543.8,
 "selected_d": 4,
 "variant_r2": 0.99689
}
```

**Artifacts.** `runs/stage_a/enc_mirror/main_seed3.json` (sha256 36a0e41277)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #96 · result · stage A · plan §4.1
`007f79e7a5e14fba` ← `d0b922d9c274467a` · recorded 2026-10-13T00:50:46+00:00

**What.** Stage A aggregate over seeds [3]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_mirror/report.json` (sha256 fb09ad3101)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #97 · run · stage A · plan §4.1
`e4e92b9b950b8a20` ← `007f79e7a5e14fba` · recorded 2026-10-13T00:50:48+00:00

**What.** Stage A arm=main seed=0 finished

**Output.**
```json
{
 "angle_inv_deg": 0.87757,
 "angle_var_deg": 0.25267,
 "gap_ratio": 219.7798,
 "global_r2": 0.99786,
 "invariant_r2": 0.99762,
 "leak_any_significant": false,
 "leak_r2_max": -0.00103,
 "seconds": 545.7,
 "selected_d": 4,
 "variant_r2": 0.998
}
```

**Artifacts.** `runs/stage_a/enc_mirror/main_seed0.json` (sha256 03e75ae9d3)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #98 · result · stage A · plan §4.1
`0f8c38a9b841eabd` ← `e4e92b9b950b8a20` · recorded 2026-10-13T00:50:48+00:00

**What.** Stage A aggregate over seeds [0]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_mirror/report.json` (sha256 edb53998a8)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #99 · run · stage A · plan §4.1
`3f781dcc17f98d5f` ← `0f8c38a9b841eabd` · recorded 2026-10-13T00:50:49+00:00

**What.** Stage A arm=main seed=4 finished

**Output.**
```json
{
 "angle_inv_deg": 1.17927,
 "angle_var_deg": 0.1802,
 "gap_ratio": 259.95674,
 "global_r2": 0.99831,
 "invariant_r2": 0.99842,
 "leak_any_significant": false,
 "leak_r2_max": -4e-05,
 "seconds": 547.4,
 "selected_d": 4,
 "variant_r2": 0.99808
}
```

**Artifacts.** `runs/stage_a/enc_mirror/main_seed4.json` (sha256 64c5b90b47)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #100 · result · stage A · plan §4.1
`31f9ac8dc4fc124e` ← `3f781dcc17f98d5f` · recorded 2026-10-13T00:50:49+00:00

**What.** Stage A aggregate over seeds [4]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_mirror/report.json` (sha256 600d379b21)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #101 · run · stage A · plan §4.1
`2bc9e5fcbb0e7604` ← `31f9ac8dc4fc124e` · recorded 2026-10-13T00:50:50+00:00

**What.** Stage A arm=main seed=1 finished

**Output.**
```json
{
 "angle_inv_deg": 1.30873,
 "angle_var_deg": 0.00499,
 "gap_ratio": 128442.46549,
 "global_r2": 1.0,
 "invariant_r2": 0.99999,
 "leak_any_significant": false,
 "leak_r2_max": -0.00033,
 "seconds": 548.3,
 "selected_d": 4,
 "variant_r2": 0.99982
}
```

**Artifacts.** `runs/stage_a/enc_mirror/main_seed1.json` (sha256 c7acdf6344)

**Bearing on objectives O1.** Direct test of O1: trained frozen encoder + one spectral split vs plan §4.1 thresholds.

---

## #102 · result · stage A · plan §4.1
`c375fbc1f57a2df5` ← `2bc9e5fcbb0e7604` · recorded 2026-10-13T00:50:50+00:00

**What.** Stage A aggregate over seeds [1]: main arm PASS; controls {}

**Output.**
```json
{
 "controls": {},
 "criteria": {
  "PASS": true,
  "angle": true,
  "gap_ratio": true,
  "invariant_r2": true,
  "leakage": true
 }
}
```

**Artifacts.** `runs/stage_a/enc_mirror/report.json` (sha256 349f84c38a)

**Bearing on objectives O1, OP.** Stage A decision point (plan §5 row 1): PASS -> proceed to Stage B rung 1. FAIL -> debug round (max 3) then halt and publish the negative.

**Verdict.** PASS

---

## #103 · run · stage A · plan §4.1
`ad0b28533e8d15ee` ← `c375fbc1f57a2df5` · recorded 2026-10-13T00:51:25+00:00

**What.** Stage A run set started: runs/stage_a/enc_mirror, seeds [1], overrides ['world.obs_dim=8', 'encoder.arch=inverse_coupling', 'encoder.objective=lejepa', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.arch=inverse_coupling",
  "encoder.objective=lejepa",
  "encoder.steps=10000"
 ],
 "seeds": [
  1
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #104 · run · stage A · plan §4.1
`d1de6007e582cb5c` ← `ad0b28533e8d15ee` · recorded 2026-10-13T00:51:25+00:00

**What.** Stage A run set started: runs/stage_a/enc_mirror, seeds [2], overrides ['world.obs_dim=8', 'encoder.arch=inverse_coupling', 'encoder.objective=lejepa', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.arch=inverse_coupling",
  "encoder.objective=lejepa",
  "encoder.steps=10000"
 ],
 "seeds": [
  2
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #105 · run · stage A · plan §4.1
`dbc6c52a63f1a7d2` ← `d1de6007e582cb5c` · recorded 2026-10-13T00:51:25+00:00

**What.** Stage A run set started: runs/stage_a/enc_mirror, seeds [4], overrides ['world.obs_dim=8', 'encoder.arch=inverse_coupling', 'encoder.objective=lejepa', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.arch=inverse_coupling",
  "encoder.objective=lejepa",
  "encoder.steps=10000"
 ],
 "seeds": [
  4
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #106 · run · stage A · plan §4.1
`06fb7f9e17b4db71` ← `dbc6c52a63f1a7d2` · recorded 2026-10-13T00:51:25+00:00

**What.** Stage A run set started: runs/stage_a/enc_mirror, seeds [0], overrides ['world.obs_dim=8', 'encoder.arch=inverse_coupling', 'encoder.objective=lejepa', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.arch=inverse_coupling",
  "encoder.objective=lejepa",
  "encoder.steps=10000"
 ],
 "seeds": [
  0
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #107 · run · stage A · plan §4.1
`e89dd58503cfded0` ← `06fb7f9e17b4db71` · recorded 2026-10-13T00:51:25+00:00

**What.** Stage A run set started: runs/stage_a/enc_mirror, seeds [3], overrides ['world.obs_dim=8', 'encoder.arch=inverse_coupling', 'encoder.objective=lejepa', 'encoder.steps=10000']

**How.** experiments/run_stage_a.py -> isj.stage_a.run_stage_a (train frozen MLP encoder, ZCA, difference-moment split on 30k matched pairs, probe on disjoint latents)

**Output.**
```json
{
 "coupling": 0.5,
 "criteria_sha256": "88f4ba5618ed5f5176a09e2daa116a3b22cf37c246be861d526a54cefac07cfe",
 "obs_dim": 8,
 "overrides": [
  "world.obs_dim=8",
  "encoder.arch=inverse_coupling",
  "encoder.objective=lejepa",
  "encoder.steps=10000"
 ],
 "seeds": [
  3
 ]
}
```

**Artifacts.** `configs/stage_a.yaml` (sha256 1de20dc38a)

**Bearing on objectives O1, OP.** Criteria are hash-checked before any run starts (OP: thresholds fixed before the run).

---

## #108 · run · stage A · plan §4.1
`dbaa3120903611f2` ← `e89dd58503cfded0` · recorded 2026-10-13T01:00:11+00:00

**What.** Stage A arm=no_inv seed=1 finished

**Output.**
```json
{
 "angle_inv_deg": 0.91701,
 "angle_var_deg": 0.59084,
 "gap_ratio": 128442.46549,
 "global_r2": 1.0,
 "invariant_r2": 0.99994,
 "leak_any_significant": false,
 "leak_r2_max": -0.00025,
 "seconds": 526.4,
 "selected_d": 4,
 "variant_r2": 0.99991
}
```

**Artifacts.** `runs/stage_a/enc_mirror/no_inv_seed1.json` (sha256 744283b730)

**Bearing on objectives O1.** Ablation for O1: without the correspondence-driven rotation, prediction alone leaves the blocks mixed (Lemma 3.1).

---

## #109 · run · stage A · plan §4.1
`12ada911384cc72a` ← `dbaa3120903611f2` · recorded 2026-10-13T01:00:17+00:00

**What.** Stage A arm=no_inv seed=3 finished

**Output.**
```json
{
 "angle_inv_deg": 19.73436,
 "angle_var_deg": 19.50846,
 "gap_ratio": 117.05117,
 "global_r2": 0.99628,
 "invariant_r2": 0.95735,
 "leak_any_significant": true,
 "leak_r2_max": 0.04121,
 "seconds": 531.7,
 "selected_d": 4,
 "variant_r2": 0.95604
}
```

**Artifacts.** `runs/stage_a/enc_mirror/no_inv_seed3.json` (sha256 dc2b8f046c)

**Bearing on objectives O1.** Ablation for O1: without the correspondence-driven rotation, prediction alone leaves the blocks mixed (Lemma 3.1).

---

## #110 · run · stage A · plan §4.1
`8b40fd9db2b0f21a` ← `12ada911384cc72a` · recorded 2026-10-13T01:00:32+00:00

**What.** Stage A arm=no_inv seed=2 finished

**Output.**
```json
{
 "angle_inv_deg": 32.1802,
 "angle_var_deg": 31.56478,
 "gap_ratio": 186.09853,
 "global_r2": 0.99606,
 "invariant_r2": 0.91587,
 "leak_any_significant": true,
 "leak_r2_max": 0.08626,
 "seconds": 547.0,
 "selected_d": 4,
 "variant_r2": 0.90981
}
```

**Artifacts.** `runs/stage_a/enc_mirror/no_inv_seed2.json` (sha256 160d78764d)

**Bearing on objectives O1.** Ablation for O1: without the correspondence-driven rotation, prediction alone leaves the blocks mixed (Lemma 3.1).

---

## #111 · run · stage A · plan §4.1
`82068b61c59dcdee` ← `8b40fd9db2b0f21a` · recorded 2026-10-13T01:00:37+00:00

**What.** Stage A arm=no_inv seed=0 finished

**Output.**
```json
{
 "angle_inv_deg": 13.10489,
 "angle_var_deg": 12.80909,
 "gap_ratio": 219.7798,
 "global_r2": 0.99786,
 "invariant_r2": 0.98412,
 "leak_any_significant": true,
 "leak_r2_max": 0.01216,
 "seconds": 551.5,
 "selected_d": 4,
 "variant_r2": 0.98547
}
```

**Artifacts.** `runs/stage_a/enc_mirror/no_inv_seed0.json` (sha256 171376f61a)

**Bearing on objectives O1.** Ablation for O1: without the correspondence-driven rotation, prediction alone leaves the blocks mixed (Lemma 3.1).

---

## #112 · run · stage A · plan §4.1
`90c04adfd84f68e8` ← `82068b61c59dcdee` · recorded 2026-10-13T01:00:38+00:00

**What.** Stage A arm=no_inv seed=4 finished

**Output.**
```json
{
 "angle_inv_deg": 25.99347,
 "angle_var_deg": 26.14758,
 "gap_ratio": 259.95674,
 "global_r2": 0.99831,
 "invariant_r2": 0.95036,
 "leak_any_significant": true,
 "leak_r2_max": 0.04838,
 "seconds": 553.2,
 "selected_d": 4,
 "variant_r2": 0.94982
}
```

**Artifacts.** `runs/stage_a/enc_mirror/no_inv_seed4.json` (sha256 19d48f6fdf)

**Bearing on objectives O1.** Ablation for O1: without the correspondence-driven rotation, prediction alone leaves the blocks mixed (Lemma 3.1).

---

## #113 · result · stage A · plan §6
`57677fd0244721f5` ← `90c04adfd84f68e8` · recorded 2026-10-13T01:01:10+00:00

**What.** Encoder-recipe ablations finished: the 0.009 gap is the encoder design, not our pipeline.

**How.** Five variants x 5 seeds (main arm), plus the no-spectral-head baseline for the mirror encoder, 5 seeds.

**Output.**
```json
{
 "summary": [
  "Starting point: ours 0.989 vs the authors' script 0.998 (gap 0.009).",
  "1. 8 observed numbers: invariant_r2 0.9900 ± 0.0023",
  "2. 10,000 steps: 0.9903 ± 0.0024",
  "3. both: 0.9916 ± 0.0023  (closes about 30% of the gap at most; the rule asked for half)",
  "4. paper's objective on our generic network: -0.0004 ± 0.0002  (collapsed; nothing recovered)",
  "5. mirror-style encoder + paper objective: invariant_r2 0.9976 ± 0.0018, a12_fro 0.0034 ± 0.0019, a21_fro 0.0231 ± 0.0021  (authors: 0.9980, 0.0034, 0.0233)",
  "Paper's LeJEPA baseline (no spectral head) with our mirror encoder: invariant_r2 0.9615 ± 0.0325, a12_fro 0.331 ± 0.216  (authors: 0.9619, 0.329)"
 ]
}
```

**Artifacts.** `runs/stage_a/enc_lejepa_mlp/main_seed0.json` (sha256 f531dca75b); `runs/stage_a/enc_lejepa_mlp/main_seed1.json` (sha256 b954ff99b7); `runs/stage_a/enc_lejepa_mlp/main_seed2.json` (sha256 5991eeac6c); `runs/stage_a/enc_lejepa_mlp/main_seed3.json` (sha256 a1914daaad); `runs/stage_a/enc_lejepa_mlp/main_seed4.json` (sha256 837b0c6348); `runs/stage_a/enc_mirror/main_seed0.json` (sha256 03e75ae9d3) … +24 more

---

## #114 · result · stage B · plan §4.2
`0759d8207d0ecaef` ← `57677fd0244721f5` · recorded 2026-10-13T01:01:10+00:00

**What.** Stage B maths-only core: three levels plus a planted cross-cutting factor, no encoder.

**How.** tests/test_stage_b_core.py; worlds.BlockWorld(cross_block=...), audits.deviation_map

**Output.**
```json
{
 "T_with_factor": 2.03,
 "T_without": "about 0",
 "nominal_angle_160k": "0.1-0.3",
 "nominal_angle_40k": "1.5-1.6"
}
```

---

## #115 · note · stage log · plan §—
`055c18da4a1d2658` ← `0759d8207d0ecaef` · recorded 2026-10-13T01:01:40+00:00

**What.** Integrity housekeeping: 21 earlier references to report.json files are declared superseded.

**How.** Five parallel seed-workers each rewrote the same derived report.json in their run folder, so earlier fingerprints of it went stale. The per-seed result files (the evidence) are unchanged, and every number quoted in the log was computed from them. The runner now writes a uniquely named, never-overwritten report per invocation.

---

## #116 · decision · stage B · plan §4.2
`afb3b8b66c97843e` ← `055c18da4a1d2658` · recorded 2026-10-13T01:27:31+00:00

**What.** Decision (from you): Stage B follows the paper's methods and data generation. Only the iterated splitting is new.

**How.** Gaussian hidden numbers throughout; observations from the paper's coupling map with no extra observed numbers (obs_dim = d); mirror-style encoder trained with the paper's objective (alignment + SIGReg); rung-2 matched pairs made like the paper's (twin samples share the slower blocks, resample the faster one). Clustering-built pairs deferred.

**Output.**
```json
{
 "departures_from_paper_so_far": [
  "16 observed numbers (plan §6 'our choice')",
  "generic network (plan §6 'our choice')",
  "predictor + covariance penalty + stop-gradient recipe (mine)",
  "discrete-category idea for clustering (mine)"
 ]
}
```

---

## #117 · plan · stage B · plan §4.2
`c92c361e20c9dd35` ← `afb3b8b66c97843e` · recorded 2026-10-13T01:28:12+00:00

**What.** Stage B pass numbers locked before any Stage B run.

**How.** configs/stage_b.yaml criteria block; fingerprint stored in configs/stage_b.criteria.sha256.

**Output.**
```json
{
 "controls": {
  "no_inv": {
   "rung1_angle_min_deg": 5.0
  },
  "no_pred": {
   "rung1_angle_min_deg": 5.0
  },
  "no_var": {
   "note": "recorded, no hard expectation"
  },
  "rank1_rung2": {
   "rung1_angle_max_deg": 5.0,
   "rung2_angle_min_deg": 10.0
  },
  "shuffled_rung2": {
   "rung2_angle_min_deg": 45.0,
   "rung2_gap_ratio_max": 2.0
  }
 },
 "criteria": {
  "deviation_T_min": 0.5,
  "deviation_T_over_null_max": 3.0,
  "deviation_direction_angle_max_deg": 5.0,
  "deviation_recurrence_angle_max_deg": 5.0,
  "gate_G1_rung1_angle_max_deg": 5.0,
  "nesting_angle_max_deg": 5.0,
  "note_gap_ratio": "reported, not gating: the planted factor deliberately sits in the spectrum (gap about 2)",
  "rung_angle_max_deg": 5.0
 },
 "criteria_sha256": "f2bd7ac25aff678552573b6a726f07bc32ca975248bd39619334dc3023216ba9",
 "seeds": [
  0,
  1,
  2
 ]
}
```

**Artifacts.** `configs/stage_b.yaml` (sha256 f63148b602)

---

## #118 · amendment · stage B · plan §4.2
`8d160d6d1c2700b3` ← `c92c361e20c9dd35` · recorded 2026-10-13T01:30:17+00:00

**What.** Corrected two Stage B control thresholds before any registered run.

**How.** configs/stage_b.yaml controls block (not part of the locked criteria hash). A 2,000-step smoke run (not counted) showed the real second-split gap ratio is about 1.94, because the planted factor sits just under the real blocks.

**Output.**
```json
{
 "controls_judged_on": "mean over seeds (was: every seed)",
 "pass_criteria_changed": false,
 "shuffled_rung2.rung2_gap_ratio_max": "2.0 -> 1.3"
}
```

---

## #119 · run · stage B · plan §4.2
`685caf8455f7e4a3` ← `8d160d6d1c2700b3` · recorded 2026-10-13T01:30:20+00:00

**What.** Stage B run started: seeds [1], arms ['main', 'null', 'shuffled_rung2', 'rank1_rung2', 'no_pred', 'no_inv', 'no_var']

**Output.**
```json
{
 "criteria_sha256": "f2bd7ac25aff678552573b6a726f07bc32ca975248bd39619334dc3023216ba9",
 "seeds": [
  1
 ]
}
```

**Artifacts.** `configs/stage_b.yaml` (sha256 98aab0dd02)

---

## #120 · run · stage B · plan §4.2
`2436ffdab91c0c68` ← `685caf8455f7e4a3` · recorded 2026-10-13T01:30:20+00:00

**What.** Stage B run started: seeds [2], arms ['main', 'null', 'shuffled_rung2', 'rank1_rung2', 'no_pred', 'no_inv', 'no_var']

**Output.**
```json
{
 "criteria_sha256": "f2bd7ac25aff678552573b6a726f07bc32ca975248bd39619334dc3023216ba9",
 "seeds": [
  2
 ]
}
```

**Artifacts.** `configs/stage_b.yaml` (sha256 98aab0dd02)

---

## #121 · run · stage B · plan §4.2
`0b871038fc479484` ← `2436ffdab91c0c68` · recorded 2026-10-13T01:30:20+00:00

**What.** Stage B run started: seeds [0], arms ['main', 'null', 'shuffled_rung2', 'rank1_rung2', 'no_pred', 'no_inv', 'no_var']

**Output.**
```json
{
 "criteria_sha256": "f2bd7ac25aff678552573b6a726f07bc32ca975248bd39619334dc3023216ba9",
 "seeds": [
  0
 ]
}
```

**Artifacts.** `configs/stage_b.yaml` (sha256 98aab0dd02)

---

## #122 · note · stage B · plan §—
`a0ac7a5d9baf3f77` ← `0b871038fc479484` · recorded 2026-10-13T01:30:28+00:00

**What.** configs/stage_b.yaml was edited after entry #117 (the control corrections); entry #117's fingerprint of it is declared superseded.

**How.** The locked pass criteria did not change (their hash is unchanged); only the controls block did. This entry records the digest of the amended file that the registered runs use.

**Output.**
```json
{
 "criteria_sha256_unchanged": "f2bd7ac25aff678552573b6a726f07bc32ca975248bd39619334dc3023216ba9"
}
```

**Artifacts.** `configs/stage_b.yaml` (sha256 98aab0dd02)

---

## #123 · note · stage B · plan §4.2
`d5519a290a7320ea` ← `a0ac7a5d9baf3f77` · recorded 2026-10-13T02:02:26+00:00

**What.** The first launch of the registered Stage B runs was interrupted by an environment restart; no result files exist. Relaunching.

**How.** Machine uptime was 4 minutes when checked; the three background processes started at 01:30 had been killed. runs/stage_b/r1 was empty, so nothing was lost and no partial result is being reused.

---

## #124 · run · stage B · plan §4.2
`d3d203898bcb80f7` ← `d5519a290a7320ea` · recorded 2026-10-13T02:02:29+00:00

**What.** Stage B run started: seeds [1], arms ['main', 'null', 'shuffled_rung2', 'rank1_rung2', 'no_pred', 'no_inv', 'no_var']

**Output.**
```json
{
 "criteria_sha256": "f2bd7ac25aff678552573b6a726f07bc32ca975248bd39619334dc3023216ba9",
 "seeds": [
  1
 ]
}
```

**Artifacts.** `configs/stage_b.yaml` (sha256 98aab0dd02)

---

## #125 · run · stage B · plan §4.2
`c6cf9e93cf3ac1c9` ← `d3d203898bcb80f7` · recorded 2026-10-13T02:02:29+00:00

**What.** Stage B run started: seeds [2], arms ['main', 'null', 'shuffled_rung2', 'rank1_rung2', 'no_pred', 'no_inv', 'no_var']

**Output.**
```json
{
 "criteria_sha256": "f2bd7ac25aff678552573b6a726f07bc32ca975248bd39619334dc3023216ba9",
 "seeds": [
  2
 ]
}
```

**Artifacts.** `configs/stage_b.yaml` (sha256 98aab0dd02)

---

## #126 · run · stage B · plan §4.2
`13cc82479ff54f33` ← `c6cf9e93cf3ac1c9` · recorded 2026-10-13T02:02:29+00:00

**What.** Stage B run started: seeds [0], arms ['main', 'null', 'shuffled_rung2', 'rank1_rung2', 'no_pred', 'no_inv', 'no_var']

**Output.**
```json
{
 "criteria_sha256": "f2bd7ac25aff678552573b6a726f07bc32ca975248bd39619334dc3023216ba9",
 "seeds": [
  0
 ]
}
```

**Artifacts.** `configs/stage_b.yaml` (sha256 98aab0dd02)

---

## #127 · note · stage B · plan §4.2
`26f15b845ca0c8d8` ← `13cc82479ff54f33` · recorded 2026-10-13T02:03:19+00:00

**What.** Stage B runs relaunched, then stopped at your request about a minute in. No results.

**How.** I relaunched the runs, you told me to stop, and I wrongly told you nothing had been launched. A check showed three processes running; I stopped them. runs/stage_b/r1 has no result files.

---

## #128 · note · stage B · plan §—
`13b392c77131fbc4` ← `26f15b845ca0c8d8` · recorded 2026-10-13T02:04:32+00:00

**What.** Stage B material deleted at your request, to be restarted later after some design choices.

**How.** Deleted: Stage B config and locked fingerprint, pipeline, runner, maths-only test, all run logs, and the Stage B-only code in worlds.py (cross-cutting factor option) and audits.py (leftover-direction detector). Kept: mirror-style encoder and the paper's objective (used by the Stage A ablations). The log entries are kept because the log is append-only; the deleted files stay recoverable from git commit 17a23b2.

---

## #129 · note · stage B · plan §—
`3cec93c156b8e550` ← `13b392c77131fbc4` · recorded 2026-10-13T02:53:52+00:00

**What.** Correction: the paper makes matched pairs only once (one split). It never makes second-split pairs.

**How.** Earlier I wrote that second-split pairs would be 'made like the paper's matched pairs'. That was wrong: the paper's twins share the invariant block and resample the variant block, for a single split. Extending this to a second level is our own construction. The earlier decision entry is not edited (the log is append-only); this entry corrects it.

---

## #130 · decision · stage B · plan §4.2
`a8b9460fb6ae0c2b` ← `3cec93c156b8e550` · recorded 2026-10-13T02:53:52+00:00

**What.** Decision (from you): second-split pairs come from clusters, each Gaussian inside itself; the paper's spectral split is applied between clusters.

**How.** Hidden world becomes nested Gaussian clusters (category contains identities, identity contains texture variation). Rung-2 pairs are built from the data by clustering the first split's invariant output: two samples from the same cluster form a pair. Then the same difference-moment split as the paper separates directions that vary within a cluster from directions that do not. Still open: the meaning of 'reducing the samples from anything between the two structures'; my reading is to drop ambiguous samples that lie between clusters before pairing.

**Output.**
```json
{
 "known_risk": "the encoder's SIGReg regulariser pushes embeddings toward one Gaussian, which may squash clusters",
 "my_defaults": [
  "flat first, nested if needed",
  "leave the cross-cutting factor for a later step",
  "paper's mirror encoder and objective",
  "pass numbers written down and locked before any run"
 ],
 "open_question": "reading of 'reducing the samples from anything between the two variant-invariant structures'"
}
```

---

## #131 · note · stage B · plan §—
`0334d36b7ad211a0` ← `a8b9460fb6ae0c2b` · recorded 2026-10-13T05:15:01+00:00

**What.** Corrected meaning of 'reducing the samples between the two structures': it means taking the difference of the paired samples, which cancels the invariant part. Not dropping ambiguous samples.

**How.** You supplied the derivation: for pairs sharing u, the invariant outputs must agree, so B(v1 - v2) = 0; if the pair differences collectively span the variant space (M full rank) then B = 0, and orthogonality of Q then forces C = 0. This is paper Theorem 2, monograph Theorem 4.1/4.2, plan §2.3. My earlier reading (drop in-between samples) in the decision entry is therefore wrong; that entry is not edited.

---

## #132 · decision · stage B · plan §4.2
`43d90c3957d1641a` ← `0334d36b7ad211a0` · recorded 2026-10-13T05:15:01+00:00

**What.** Plan amendment: Stage B is split into B1 (mechanism, ground-truth pairs, all Gaussian) and B2 (construction, pairs built by clustering, Gaussian clusters). B1 first.

**How.** Matches plan §4.2's own aim of never confusing imperfect correspondence construction with rung contamination as the cause of a failed rung 2. B1 design written in docs/stage_b1_design.md as a draft; pass numbers are proposed, NOT locked, and nothing is built.

**Output.**
```json
{
 "B1": "does the ladder identify deeper rungs, given correct pairs; all-Gaussian",
 "B2": "can rung-(k+1) pairs be built without ground truth, by clustering rung-k output; Gaussian clusters",
 "open_settings": [
  "block sizes 4/4/4, three levels",
  "speeds 0.2/0.7/0.95 or one speed",
  "cross-cutting factor after the basic split passes",
  "leakage rule strict, no floor",
  "pass numbers"
 ]
}
```

**Artifacts.** `docs/stage_b1_design.md` (sha256 b0ba82a4b7)

---

## #133 · plan · stage B · plan §4.2
`04aac591fe614c84` ← `43d90c3957d1641a` · recorded 2026-10-13T05:27:21+00:00

**What.** Stage B1 pass numbers locked, with your two additions. Nothing built or run yet.

**How.** configs/stage_b1.yaml criteria block; fingerprint in configs/stage_b1.criteria.sha256. You approved the draft design ('all fine') with two additions: keep separate speeds and treat a texture-only variant_r2 failure as a located risk; gate on the category core (last 4 directions) reaching invariant_r2 above 0.9.

**Output.**
```json
{
 "controls": {
  "must_fail": {
   "rank1_rung2": {
    "rung1_angle_max_deg": 5.0,
    "rung2_angle_min_deg": 10.0
   },
   "shuffled_rung2": {
    "rung2_angle_min_deg": 45.0,
    "rung2_gap_ratio_max": 2.0
   }
  },
  "recorded_no_expectation": [
   "no_inv",
   "no_pred",
   "no_var"
  ]
 },
 "criteria": {
  "core_invariant_r2_min": 0.9,
  "gap_ratio_min": 10.0,
  "leakage": "no significant off-diagonal at the permutation null (Holm, alpha 0.01), each rung; strict",
  "located_risk_rule": "ADDED: if the ONLY criterion that fails (on any seed) is rung-1 variant_r2 (texture), the verdict is PASS_WITH_LOCATED_RISK and it is logged as the located risk (separate speeds + the paper's alignment objective squash the fast block), not as a B1 failure. Any other failure is FAIL.",
  "nesting_angle_max_deg": 5.0,
  "rank_test": "smallest eigenvalue of the variant block's pair-difference moment is above the monograph's rank-deficiency bound B^2*sqrt(2 log(1/delta)/n), delta 0.01, at each rung",
  "rung_angle_max_deg": 5.0,
  "variant_r2_min": 0.9
 },
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "seeds": [
  0,
  1,
  2
 ]
}
```

**Artifacts.** `configs/stage_b1.yaml` (sha256 ae1f0bfc5d); `docs/stage_b1_design.md` (sha256 b0ba82a4b7)

---

## #134 · implementation · stage B · plan §4.2
`142a0ecf6a433510` ← `04aac591fe614c84` · recorded 2026-10-13T05:29:20+00:00

**What.** Built the Stage B1 pipeline, runner and verdict-rule tests. No registered run has been launched.

**How.** src/isj/stage_b1.py (pipeline + locked verdict rule), experiments/run_stage_b1.py, tests/test_stage_b1_eval.py. A 300-step code-path check (seed 0, nothing saved) confirmed the pipeline runs end to end; it is NOT a result.

**Output.**
```json
{
 "code_path_check_300_steps_not_a_result": {
  "core_invariant_r2": 0.966,
  "main_angles_deg": [
   1.5,
   2.4
  ],
  "no_inv_angles": [
   47.2,
   31.5
  ],
  "rank1_rung2_angle": 79.2,
  "shuffled_rung2_angle": 52.3
 },
 "tests": "20 pass (6 new, covering the located-risk rule and the category-core gate)"
}
```

**Artifacts.** `src/isj/stage_b1.py` (sha256 f65492948f); `experiments/run_stage_b1.py` (sha256 0865d374e3); `docs/stage_b1_design.md` (sha256 0e092e7cd4)

---

## #135 · note · stage B · plan §—
`140276d5985bcb80` ← `142a0ecf6a433510` · recorded 2026-10-13T05:29:42+00:00

**What.** docs/stage_b1_design.md was updated to the approved version; earlier fingerprints of the draft are declared superseded.

**How.** The design document changed from draft to approved (the two additions, confirmed settings, a corrected cost estimate of about 15 minutes instead of 10). The locked pass numbers live in configs/stage_b1.yaml and did not change after locking. This entry records the digest of the approved document.

**Artifacts.** `docs/stage_b1_design.md` (sha256 0e092e7cd4)

---

## #136 · run · stage B · plan §4.2
`f58cc58c92603ec3` ← `140276d5985bcb80` · recorded 2026-10-13T05:34:30+00:00

**What.** Stage B1 run started: seeds [2], arms ['main', 'shuffled_rung2', 'rank1_rung2', 'no_inv', 'no_pred', 'no_var']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  2
 ]
}
```

**Artifacts.** `configs/stage_b1.yaml` (sha256 ae1f0bfc5d)

---

## #137 · run · stage B · plan §4.2
`2e89fbb5325a7b66` ← `f58cc58c92603ec3` · recorded 2026-10-13T05:34:30+00:00

**What.** Stage B1 run started: seeds [0], arms ['main', 'shuffled_rung2', 'rank1_rung2', 'no_inv', 'no_pred', 'no_var']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  0
 ]
}
```

**Artifacts.** `configs/stage_b1.yaml` (sha256 ae1f0bfc5d)

---

## #138 · run · stage B · plan §4.2
`85da03bc2bba41eb` ← `2e89fbb5325a7b66` · recorded 2026-10-13T05:34:30+00:00

**What.** Stage B1 run started: seeds [1], arms ['main', 'shuffled_rung2', 'rank1_rung2', 'no_inv', 'no_pred', 'no_var']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  1
 ]
}
```

**Artifacts.** `configs/stage_b1.yaml` (sha256 ae1f0bfc5d)

---

## #139 · run · stage B · plan §4.2
`76791ad2b79fdc11` ← `85da03bc2bba41eb` · recorded 2026-10-13T05:42:17+00:00

**What.** Stage B1 arm=main seed=1 finished

**Output.**
```json
{
 "core_invariant_r2": 0.978,
 "rung_angles_deg": [
  1.21,
  1.25
 ],
 "seconds": 466.4,
 "variant_r2": [
  0.957,
  0.983
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/main_seed1.json` (sha256 ed93c3cc3d)

---

## #140 · run · stage B · plan §4.2
`b7bd9ffae623d6ef` ← `76791ad2b79fdc11` · recorded 2026-10-13T05:42:17+00:00

**What.** Stage B1 arm=main seed=0 finished

**Output.**
```json
{
 "core_invariant_r2": 0.981,
 "rung_angles_deg": [
  0.77,
  1.45
 ],
 "seconds": 466.5,
 "variant_r2": [
  0.962,
  0.984
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/main_seed0.json` (sha256 19ba2314bd)

---

## #141 · run · stage B · plan §4.2
`88c25e07c5643565` ← `b7bd9ffae623d6ef` · recorded 2026-10-13T05:42:22+00:00

**What.** Stage B1 arm=main seed=2 finished

**Output.**
```json
{
 "core_invariant_r2": 0.976,
 "rung_angles_deg": [
  1.18,
  1.37
 ],
 "seconds": 472.2,
 "variant_r2": [
  0.955,
  0.98
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/main_seed2.json` (sha256 a779523c76)

---

## #142 · run · stage B · plan §4.2
`d4c5e62695d19417` ← `88c25e07c5643565` · recorded 2026-10-13T05:49:25+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=0 finished

**Output.**
```json
{
 "core_invariant_r2": 0.565,
 "rung_angles_deg": [
  0.65,
  75.03
 ],
 "seconds": 427.9,
 "variant_r2": [
  0.96,
  0.567
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/shuffled_rung2_seed0.json` (sha256 a9df816249)

---

## #143 · run · stage B · plan §4.2
`def50bfa6395300d` ← `d4c5e62695d19417` · recorded 2026-10-13T05:49:42+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=1 finished

**Output.**
```json
{
 "core_invariant_r2": 0.325,
 "rung_angles_deg": [
  1.22,
  77.41
 ],
 "seconds": 444.9,
 "variant_r2": [
  0.958,
  0.337
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/shuffled_rung2_seed1.json` (sha256 ac7375896e)

---

## #144 · run · stage B · plan §4.2
`e644c74547ee34d9` ← `def50bfa6395300d` · recorded 2026-10-13T05:49:50+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=2 finished

**Output.**
```json
{
 "core_invariant_r2": 0.689,
 "rung_angles_deg": [
  1.24,
  56.25
 ],
 "seconds": 448.0,
 "variant_r2": [
  0.956,
  0.685
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/shuffled_rung2_seed2.json` (sha256 a93e05d061)

---

## #145 · run · stage B · plan §4.2
`8a0742b347e92642` ← `e644c74547ee34d9` · recorded 2026-10-13T05:56:06+00:00

**What.** Stage B1 arm=rank1_rung2 seed=0 finished

**Output.**
```json
{
 "core_invariant_r2": 0.492,
 "rung_angles_deg": [
  0.77,
  83.52
 ],
 "seconds": 401.8,
 "variant_r2": [
  0.962,
  0.48
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/rank1_rung2_seed0.json` (sha256 5718abc659)

---

## #146 · run · stage B · plan §4.2
`71ca6beaaed77817` ← `8a0742b347e92642` · recorded 2026-10-13T05:57:09+00:00

**What.** Stage B1 arm=rank1_rung2 seed=1 finished

**Output.**
```json
{
 "core_invariant_r2": 0.573,
 "rung_angles_deg": [
  1.21,
  82.95
 ],
 "seconds": 447.6,
 "variant_r2": [
  0.957,
  0.579
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/rank1_rung2_seed1.json` (sha256 8044d5c940)

---

## #147 · run · stage B · plan §4.2
`62534d5c12e5e6b6` ← `71ca6beaaed77817` · recorded 2026-10-13T05:57:15+00:00

**What.** Stage B1 arm=rank1_rung2 seed=2 finished

**Output.**
```json
{
 "core_invariant_r2": 0.533,
 "rung_angles_deg": [
  1.18,
  75.45
 ],
 "seconds": 445.1,
 "variant_r2": [
  0.955,
  0.536
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/rank1_rung2_seed2.json` (sha256 dd7f13f1b7)

---

## #148 · run · stage B · plan §4.2
`1d734409df9f86e3` ← `62534d5c12e5e6b6` · recorded 2026-10-13T06:03:07+00:00

**What.** Stage B1 arm=no_inv seed=0 finished

**Output.**
```json
{
 "core_invariant_r2": 0.744,
 "rung_angles_deg": [
  36.25,
  25.2
 ],
 "seconds": 420.6,
 "variant_r2": [
  0.742,
  0.875
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/no_inv_seed0.json` (sha256 878eb1ae73)

---

## #149 · run · stage B · plan §4.2
`bdbfa732e61ce219` ← `1d734409df9f86e3` · recorded 2026-10-13T06:04:43+00:00

**What.** Stage B1 arm=no_inv seed=1 finished

**Output.**
```json
{
 "core_invariant_r2": 0.742,
 "rung_angles_deg": [
  34.79,
  31.76
 ],
 "seconds": 453.4,
 "variant_r2": [
  0.737,
  0.856
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/no_inv_seed1.json` (sha256 69362d6906)

---

## #150 · run · stage B · plan §4.2
`f55c4671447898ad` ← `bdbfa732e61ce219` · recorded 2026-10-13T06:04:44+00:00

**What.** Stage B1 arm=no_inv seed=2 finished

**Output.**
```json
{
 "core_invariant_r2": 0.788,
 "rung_angles_deg": [
  31.29,
  27.43
 ],
 "seconds": 448.0,
 "variant_r2": [
  0.807,
  0.88
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/no_inv_seed2.json` (sha256 4e57c8e27c)

---

## #151 · run · stage B · plan §4.2
`b8f92aa6f3fdd53e` ← `f55c4671447898ad` · recorded 2026-10-13T06:10:12+00:00

**What.** Stage B1 arm=no_pred seed=0 finished

**Output.**
```json
{
 "core_invariant_r2": 0.989,
 "rung_angles_deg": [
  0.31,
  1.26
 ],
 "seconds": 424.8,
 "variant_r2": [
  0.989,
  0.988
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/no_pred_seed0.json` (sha256 96c256d3c3)

---

## #152 · run · stage B · plan §4.2
`31729e84513dade8` ← `b8f92aa6f3fdd53e` · recorded 2026-10-13T06:12:06+00:00

**What.** Stage B1 arm=no_pred seed=2 finished

**Output.**
```json
{
 "core_invariant_r2": 0.986,
 "rung_angles_deg": [
  0.51,
  0.97
 ],
 "seconds": 442.5,
 "variant_r2": [
  0.99,
  0.989
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/no_pred_seed2.json` (sha256 f099aa1649)

---

## #153 · run · stage B · plan §4.2
`2b36bfb9c533d698` ← `31729e84513dade8` · recorded 2026-10-13T06:12:07+00:00

**What.** Stage B1 arm=no_pred seed=1 finished

**Output.**
```json
{
 "core_invariant_r2": 0.985,
 "rung_angles_deg": [
  0.47,
  1.03
 ],
 "seconds": 444.1,
 "variant_r2": [
  0.986,
  0.986
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/no_pred_seed1.json` (sha256 89179d349b)

---

## #154 · run · stage B · plan §4.2
`54774d2d0c6daeb6` ← `2b36bfb9c533d698` · recorded 2026-10-13T06:17:21+00:00

**What.** Stage B1 arm=no_var seed=0 finished

**Output.**
```json
{
 "core_invariant_r2": 0.981,
 "rung_angles_deg": [
  2.31,
  9.4
 ],
 "seconds": 429.4,
 "variant_r2": [
  0.881,
  0.968
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/no_var_seed0.json` (sha256 d34e426867)

---

## #155 · run · stage B · plan §4.2
`e8c41d2c71cfb068` ← `54774d2d0c6daeb6` · recorded 2026-10-13T06:19:46+00:00

**What.** Stage B1 arm=no_var seed=1 finished

**Output.**
```json
{
 "core_invariant_r2": 0.978,
 "rung_angles_deg": [
  2.69,
  7.44
 ],
 "seconds": 459.5,
 "variant_r2": [
  0.851,
  0.946
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/no_var_seed1.json` (sha256 56deceea46)

---

## #156 · run · stage B · plan §4.2
`5882befd615f48ed` ← `e8c41d2c71cfb068` · recorded 2026-10-13T06:19:48+00:00

**What.** Stage B1 arm=no_var seed=2 finished

**Output.**
```json
{
 "core_invariant_r2": 0.976,
 "rung_angles_deg": [
  2.86,
  9.73
 ],
 "seconds": 461.5,
 "variant_r2": [
  0.872,
  0.969
 ]
}
```

**Artifacts.** `runs/stage_b1/r1/no_var_seed2.json` (sha256 f911c9e549)

---

## #157 · result · stage B · plan §4.2
`a52d60ea658970cc` ← `5882befd615f48ed` · recorded 2026-10-13T06:19:48+00:00

**What.** Stage B1 aggregate: FAIL

**Output.**
```json
{
 "controls": {
  "rank1_rung2": true,
  "shuffled_rung2": true
 },
 "failing_criteria": [
  "leakage"
 ],
 "verdict": "FAIL"
}
```

**Artifacts.** `runs/stage_b1/r1/report_20261013T061948105124.json` (sha256 34aedfd959)

**Verdict.** FAIL

---

## #158 · note · stage B · plan §4.2
`651f4008a989dfc1` ← `a52d60ea658970cc` · recorded 2026-10-13T06:21:15+00:00

**What.** B1 result explained: the one failing line is leakage on one seed, with an effect size of 0.0003. The locked verdict stays FAIL.

**How.** Seed 2, rung 1: the strict permutation test (Holm, alpha 0.01) flagged 'rest->own' leakage with held-out R2 = +0.0003. The other five rung-seed combinations were not flagged; their R2 values are -0.0011 to +0.0002. Every other criterion passed on all 3 seeds. The rule was locked strict with no floor at your request; it has not been changed.

**Output.**
```json
{
 "effect_size_R2": 0.0003,
 "failing": [
  "leakage, seed 2 rung 1"
 ],
 "no_prediction_arm_failed": false,
 "squash_risk_materialised": false,
 "texture_variant_r2": [
  0.962,
  0.957,
  0.955
 ],
 "verdict": "FAIL (locked rule)"
}
```

---

## #159 · plan · stage B · plan §4.2
`7baf15e2496743e9` ← `651f4008a989dfc1` · recorded 2026-10-13T06:26:56+00:00

**What.** Supplementary replication of B1: 12 more seeds (3-14), main arm only, to see whether the strict leakage flag recurs. Reading rule fixed before launch.

**How.** Same locked configuration (configs/stage_b1.yaml, criteria hash unchanged), same code; only the seed list differs. The registered B1 verdict (FAIL on one strict-leakage flag, seed 2) is NOT replaced by this; this is a follow-up to understand it. Reading rule: the test is 1% per rung, so with 24 new rung-checks about 0.24 flags are expected by chance. 0 or 1 flagged rungs = consistent with chance; 2 = ambiguous; 3 or more = a real, tiny, systematic leakage.

**Output.**
```json
{
 "arm": "main",
 "rule": {
  "0-1": "chance",
  "2": "ambiguous",
  "3+": "systematic tiny leakage"
 },
 "seeds": [
  3,
  4,
  5,
  6,
  7,
  8,
  9,
  10,
  11,
  12,
  13,
  14
 ]
}
```

---

## #160 · run · stage B · plan §4.2
`53a189abbfbc74eb` ← `7baf15e2496743e9` · recorded 2026-10-13T06:27:01+00:00

**What.** Stage B1 run started: seeds [6, 10, 14], arms ['main']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  6,
  10,
  14
 ]
}
```

**Artifacts.** `configs/stage_b1.yaml` (sha256 ae1f0bfc5d)

---

## #161 · run · stage B · plan §4.2
`8c15d5f35a05ca95` ← `53a189abbfbc74eb` · recorded 2026-10-13T06:27:01+00:00

**What.** Stage B1 run started: seeds [4, 8, 12], arms ['main']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  4,
  8,
  12
 ]
}
```

**Artifacts.** `configs/stage_b1.yaml` (sha256 ae1f0bfc5d)

---

## #162 · run · stage B · plan §4.2
`4a5c93932bd9dc21` ← `8c15d5f35a05ca95` · recorded 2026-10-13T06:27:01+00:00

**What.** Stage B1 run started: seeds [5, 9, 13], arms ['main']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  5,
  9,
  13
 ]
}
```

**Artifacts.** `configs/stage_b1.yaml` (sha256 ae1f0bfc5d)

---

## #163 · run · stage B · plan §4.2
`ee52365c2944485a` ← `4a5c93932bd9dc21` · recorded 2026-10-13T06:27:01+00:00

**What.** Stage B1 run started: seeds [3, 7, 11], arms ['main']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  3,
  7,
  11
 ]
}
```

**Artifacts.** `configs/stage_b1.yaml` (sha256 ae1f0bfc5d)

---

## #164 · run · stage B · plan §4.2
`2fa2bc5418a62bd3` ← `ee52365c2944485a` · recorded 2026-10-13T06:34:55+00:00

**What.** Stage B1 arm=main seed=3 finished

**Output.**
```json
{
 "core_invariant_r2": 0.98,
 "rung_angles_deg": [
  0.98,
  1.18
 ],
 "seconds": 473.7,
 "variant_r2": [
  0.953,
  0.981
 ]
}
```

**Artifacts.** `runs/stage_b1/more_seeds/main_seed3.json` (sha256 b8c6835e09)

---

## #165 · run · stage B · plan §4.2
`a5441439490a0f67` ← `2fa2bc5418a62bd3` · recorded 2026-10-13T06:35:00+00:00

**What.** Stage B1 arm=main seed=6 finished

**Output.**
```json
{
 "core_invariant_r2": 0.978,
 "rung_angles_deg": [
  1.07,
  1.14
 ],
 "seconds": 479.0,
 "variant_r2": [
  0.953,
  0.981
 ]
}
```

**Artifacts.** `runs/stage_b1/more_seeds/main_seed6.json` (sha256 19fd7c0608)

---

## #166 · run · stage B · plan §4.2
`a3c92688b50ad2ab` ← `a5441439490a0f67` · recorded 2026-10-13T06:35:04+00:00

**What.** Stage B1 arm=main seed=4 finished

**Output.**
```json
{
 "core_invariant_r2": 0.977,
 "rung_angles_deg": [
  1.0,
  1.02
 ],
 "seconds": 483.5,
 "variant_r2": [
  0.954,
  0.985
 ]
}
```

**Artifacts.** `runs/stage_b1/more_seeds/main_seed4.json` (sha256 bfc06f4400)

---

## #167 · run · stage B · plan §4.2
`c3dfdf33b0effd7e` ← `a3c92688b50ad2ab` · recorded 2026-10-13T06:35:05+00:00

**What.** Stage B1 arm=main seed=5 finished

**Output.**
```json
{
 "core_invariant_r2": 0.978,
 "rung_angles_deg": [
  1.18,
  1.73
 ],
 "seconds": 483.7,
 "variant_r2": [
  0.957,
  0.98
 ]
}
```

**Artifacts.** `runs/stage_b1/more_seeds/main_seed5.json` (sha256 cedee4f01d)

---

## #168 · run · stage B · plan §4.2
`a9cbca6ac5e0f415` ← `c3dfdf33b0effd7e` · recorded 2026-10-13T06:42:39+00:00

**What.** Stage B1 arm=main seed=7 finished

**Output.**
```json
{
 "core_invariant_r2": 0.977,
 "rung_angles_deg": [
  1.19,
  1.98
 ],
 "seconds": 464.4,
 "variant_r2": [
  0.952,
  0.976
 ]
}
```

**Artifacts.** `runs/stage_b1/more_seeds/main_seed7.json` (sha256 33aa047ccc)

---

## #169 · run · stage B · plan §4.2
`26efce3547c626a3` ← `a9cbca6ac5e0f415` · recorded 2026-10-13T06:42:44+00:00

**What.** Stage B1 arm=main seed=8 finished

**Output.**
```json
{
 "core_invariant_r2": 0.982,
 "rung_angles_deg": [
  0.57,
  1.26
 ],
 "seconds": 459.8,
 "variant_r2": [
  0.962,
  0.984
 ]
}
```

**Artifacts.** `runs/stage_b1/more_seeds/main_seed8.json` (sha256 47fe8df0ff)

---

## #170 · run · stage B · plan §4.2
`a02a341aaf446c9f` ← `26efce3547c626a3` · recorded 2026-10-13T06:42:45+00:00

**What.** Stage B1 arm=main seed=10 finished

**Output.**
```json
{
 "core_invariant_r2": 0.98,
 "rung_angles_deg": [
  1.0,
  1.43
 ],
 "seconds": 465.3,
 "variant_r2": [
  0.962,
  0.986
 ]
}
```

**Artifacts.** `runs/stage_b1/more_seeds/main_seed10.json` (sha256 aa34127d27)

---

## #171 · run · stage B · plan §4.2
`8794b26b5c2bb00f` ← `a02a341aaf446c9f` · recorded 2026-10-13T06:42:47+00:00

**What.** Stage B1 arm=main seed=9 finished

**Output.**
```json
{
 "core_invariant_r2": 0.977,
 "rung_angles_deg": [
  1.27,
  0.98
 ],
 "seconds": 462.0,
 "variant_r2": [
  0.952,
  0.984
 ]
}
```

**Artifacts.** `runs/stage_b1/more_seeds/main_seed9.json` (sha256 06156e214e)

---

## #172 · run · stage B · plan §4.2
`f8f0a786471cba99` ← `8794b26b5c2bb00f` · recorded 2026-10-13T06:50:32+00:00

**What.** Stage B1 arm=main seed=11 finished

**Output.**
```json
{
 "core_invariant_r2": 0.979,
 "rung_angles_deg": [
  1.2,
  1.44
 ],
 "seconds": 472.8,
 "variant_r2": [
  0.953,
  0.984
 ]
}
```

**Artifacts.** `runs/stage_b1/more_seeds/main_seed11.json` (sha256 b7e4650230)

---

## #173 · run · stage B · plan §4.2
`0f5c89514db20ad3` ← `f8f0a786471cba99` · recorded 2026-10-13T06:50:37+00:00

**What.** Stage B1 arm=main seed=12 finished

**Output.**
```json
{
 "core_invariant_r2": 0.978,
 "rung_angles_deg": [
  1.28,
  1.49
 ],
 "seconds": 472.4,
 "variant_r2": [
  0.954,
  0.981
 ]
}
```

**Artifacts.** `runs/stage_b1/more_seeds/main_seed12.json` (sha256 bec8d13395)

---

## #174 · run · stage B · plan §4.2
`810f36d53e770231` ← `0f5c89514db20ad3` · recorded 2026-10-13T06:50:42+00:00

**What.** Stage B1 arm=main seed=14 finished

**Output.**
```json
{
 "core_invariant_r2": 0.979,
 "rung_angles_deg": [
  1.07,
  0.76
 ],
 "seconds": 476.7,
 "variant_r2": [
  0.954,
  0.981
 ]
}
```

**Artifacts.** `runs/stage_b1/more_seeds/main_seed14.json` (sha256 f184b932da)

---

## #175 · run · stage B · plan §4.2
`1a2e3303019defaa` ← `810f36d53e770231` · recorded 2026-10-13T06:50:44+00:00

**What.** Stage B1 arm=main seed=13 finished

**Output.**
```json
{
 "core_invariant_r2": 0.979,
 "rung_angles_deg": [
  0.82,
  1.35
 ],
 "seconds": 477.6,
 "variant_r2": [
  0.956,
  0.98
 ]
}
```

**Artifacts.** `runs/stage_b1/more_seeds/main_seed13.json` (sha256 d31a7511d2)

---

## #176 · result · stage B · plan §4.2
`7bcbd7605a6a7acb` ← `1a2e3303019defaa` · recorded 2026-10-13T06:51:29+00:00

**What.** B1 replication, 12 more seeds: 3 of 24 rung-checks flagged by the strict leakage test. By the rule fixed beforehand (3 or more), this is a real but tiny systematic leakage.

**How.** Seeds 3-14, main arm, locked configuration and code unchanged. Flagged: seed 6 rung 1 (R2 +0.0006), seed 12 rung 1 (+0.0005), seed 13 rung 2 (+0.0003). Combined with the registered run (seed 2 rung 1, +0.0003): 4 of 30 rung-checks flagged; about 0.3 expected by chance. Every other locked criterion passed on all 12 new seeds.

**Output.**
```json
{
 "flagged_rung_checks": "3 of 24 (4 of 30 with the registered seeds)",
 "locked_verdict_of_registered_run": "FAIL (unchanged)",
 "max_leakage_R2": 0.0006,
 "other_criteria_failing_on_any_new_seed": "none",
 "ranges_12_new_seeds": {
  "core_invariant_r2": "0.977-0.982",
  "gap_ratio": "37-57",
  "nesting_deg": "0.75-1.96",
  "rung1_angle_deg": "0.57-1.28",
  "rung1_variant_r2": "0.952-0.962",
  "rung2_angle_deg": "0.76-1.98",
  "rung2_variant_r2": "0.976-0.986"
 }
}
```

**Artifacts.** `runs/stage_b1/more_seeds/main_seed10.json` (sha256 aa34127d27); `runs/stage_b1/more_seeds/main_seed11.json` (sha256 b7e4650230); `runs/stage_b1/more_seeds/main_seed12.json` (sha256 bec8d13395); `runs/stage_b1/more_seeds/main_seed13.json` (sha256 d31a7511d2); `runs/stage_b1/more_seeds/main_seed14.json` (sha256 f184b932da); `runs/stage_b1/more_seeds/main_seed3.json` (sha256 b8c6835e09) … +6 more

---

## #177 · decision · stage B · plan §4.2
`b1366657559dce18` ← `7bcbd7605a6a7acb` · recorded 2026-10-13T11:33:26+00:00

**What.** Ruling (from you): B1 is not a fail. The strict leakage rule is amended, after seeing the data, to an effect-size floor of R2 below 0.01 (floor proposed by Claude, changeable).

**How.** Original locked rule (strict permutation test, no floor) mechanically flagged a tiny leakage (R2 0.0003-0.0006) on 4 of 30 rung-checks, so the registered run's computed verdict was FAIL. That record is NOT altered. Your ruling: the effect is negligible and B1 is not a fail. Amended rule: every off-diagonal held-out R2 below 0.01; every other locked criterion unchanged. Applied by re-scoring the existing 15 seeds (experiments/rescore_b1.py); no rerun. This is a post-hoc amendment and is reported as such.

**Output.**
```json
{
 "amended_rule_reading": "all criteria hold on all 15 seeds",
 "floor": 0.01,
 "max_offdiag_leak_R2_magnitude_over_15_seeds": 0.0014,
 "original_locked_rule_reading": "flagged 4 of 30 rung-checks; computed verdict FAIL",
 "rule_decided": "after seeing data"
}
```

**Artifacts.** `runs/stage_b1/rescore_amended_leakage_rule.json` (sha256 4e9519fcb8); `experiments/rescore_b1.py` (sha256 0d724785a6)

---
