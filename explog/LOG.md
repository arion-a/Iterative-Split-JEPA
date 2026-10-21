# Experiment log (generated from `explog/chain.jsonl`; do not edit)

Chain status at render time: **VALID** — 463 entries, head 8d2b64f77374

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

## #178 · run · stage B · plan §4.2
`0200caadc4d272ea` ← `b1366657559dce18` · recorded 2026-10-13T11:42:49+00:00

**What.** Stage B2 K=3 seed=2 finished

**Output.**
```json
{
 "cluster_purity": 0.999,
 "generator_angle": 2.47,
 "kmeans_angle": 89.56,
 "label_angle": 80.09,
 "random_angle": 79.55
}
```

**Artifacts.** `runs/stage_b2/r1/K3_seed2.json` (sha256 441152e952)

---

## #179 · run · stage B · plan §4.2
`e9c42230fda23107` ← `0200caadc4d272ea` · recorded 2026-10-13T11:42:51+00:00

**What.** Stage B2 K=3 seed=0 finished

**Output.**
```json
{
 "cluster_purity": 0.778,
 "generator_angle": 1.63,
 "kmeans_angle": 60.07,
 "label_angle": 76.62,
 "random_angle": 65.79
}
```

**Artifacts.** `runs/stage_b2/r1/K3_seed0.json` (sha256 943dc39f50)

---

## #180 · run · stage B · plan §4.2
`a6b9b99ebb2d1850` ← `e9c42230fda23107` · recorded 2026-10-13T11:42:51+00:00

**What.** Stage B2 K=3 seed=1 finished

**Output.**
```json
{
 "cluster_purity": 0.844,
 "generator_angle": 1.54,
 "kmeans_angle": 77.1,
 "label_angle": 69.7,
 "random_angle": 89.86
}
```

**Artifacts.** `runs/stage_b2/r1/K3_seed1.json` (sha256 18d71c3e5c)

---

## #181 · run · stage B · plan §4.2
`ba33bf1b63381892` ← `a6b9b99ebb2d1850` · recorded 2026-10-13T11:46:16+00:00

**What.** Stage B2 K=6 seed=2 finished

**Output.**
```json
{
 "cluster_purity": 0.801,
 "generator_angle": 1.9,
 "kmeans_angle": 17.76,
 "label_angle": 2.24,
 "random_angle": 73.61
}
```

**Artifacts.** `runs/stage_b2/r1/K6_seed2.json` (sha256 7c358e13ac)

---

## #182 · run · stage B · plan §4.2
`90f49a8292255e92` ← `ba33bf1b63381892` · recorded 2026-10-13T11:46:16+00:00

**What.** Stage B2 K=6 seed=1 finished

**Output.**
```json
{
 "cluster_purity": 0.645,
 "generator_angle": 1.26,
 "kmeans_angle": 19.87,
 "label_angle": 16.97,
 "random_angle": 84.4
}
```

**Artifacts.** `runs/stage_b2/r1/K6_seed1.json` (sha256 eead3b14ac)

---

## #183 · run · stage B · plan §4.2
`00377e457c492c21` ← `90f49a8292255e92` · recorded 2026-10-13T11:46:18+00:00

**What.** Stage B2 K=6 seed=0 finished

**Output.**
```json
{
 "cluster_purity": 0.813,
 "generator_angle": 1.77,
 "kmeans_angle": 6.55,
 "label_angle": 3.18,
 "random_angle": 69.78
}
```

**Artifacts.** `runs/stage_b2/r1/K6_seed0.json` (sha256 e73cf5da2a)

---

## #184 · run · stage B · plan §4.2
`45cba0e856a1c7c5` ← `00377e457c492c21` · recorded 2026-10-13T11:49:53+00:00

**What.** Stage B2 K=12 seed=2 finished

**Output.**
```json
{
 "cluster_purity": 0.457,
 "generator_angle": 1.58,
 "kmeans_angle": 4.01,
 "label_angle": 1.89,
 "random_angle": 80.34
}
```

**Artifacts.** `runs/stage_b2/r1/K12_seed2.json` (sha256 edd43d609d)

---

## #185 · run · stage B · plan §4.2
`28bc9459530b7e12` ← `45cba0e856a1c7c5` · recorded 2026-10-13T11:49:53+00:00

**What.** Stage B2 K=12 seed=1 finished

**Output.**
```json
{
 "cluster_purity": 0.525,
 "generator_angle": 3.04,
 "kmeans_angle": 4.17,
 "label_angle": 3.31,
 "random_angle": 88.92
}
```

**Artifacts.** `runs/stage_b2/r1/K12_seed1.json` (sha256 fc778844df)

---

## #186 · run · stage B · plan §4.2
`3eb67250d9d9269d` ← `28bc9459530b7e12` · recorded 2026-10-13T11:49:56+00:00

**What.** Stage B2 K=12 seed=0 finished

**Output.**
```json
{
 "cluster_purity": 0.584,
 "generator_angle": 1.72,
 "kmeans_angle": 4.85,
 "label_angle": 1.8,
 "random_angle": 89.85
}
```

**Artifacts.** `runs/stage_b2/r1/K12_seed0.json` (sha256 4651f9b1fd)

---

## #187 · result · stage B · plan §4.2
`27091336096d88ef` ← `3eb67250d9d9269d` · recorded 2026-10-13T11:51:20+00:00

**What.** B2 ran: pairs built by k-means can give a working second split when categories are many and fine (K=12, 4-5 degrees), but not when few (K=3) or in between (K=6).

**How.** 3 category counts x 3 seeds; one encoder per run; four ways to build rung-2 pairs on the same encoder (generator twins, same-true-category pairs, k-means pairs, random). Mean rung-2 angle in degrees (generator / true-category / k-means / random): K=3: 1.9 / 75.5 / 75.6 / 78.4; K=6: 1.7 / 7.5 / 14.7 / 75.9; K=12: 2.1 / 2.3 / 4.3 / 86.4. Mean k-means purity: 0.87 / 0.75 / 0.52.

**Output.**
```json
{
 "K12": {
  "angles_generator": [
   1.7,
   3.0,
   1.6
  ],
  "angles_kmeans": [
   4.8,
   4.2,
   4.0
  ],
  "angles_true_category": [
   1.8,
   3.3,
   1.9
  ],
  "purity": [
   0.584,
   0.525,
   0.457
  ]
 },
 "K3": {
  "angles_generator": [
   1.6,
   1.5,
   2.5
  ],
  "angles_kmeans": [
   60.1,
   77.1,
   89.6
  ],
  "angles_true_category": [
   76.6,
   69.7,
   80.1
  ],
  "purity": [
   0.778,
   0.844,
   0.999
  ]
 },
 "K6": {
  "angles_generator": [
   1.8,
   1.3,
   1.9
  ],
  "angles_kmeans": [
   6.5,
   19.9,
   17.8
  ],
  "angles_true_category": [
   3.2,
   17.0,
   2.2
  ],
  "purity": [
   0.813,
   0.645,
   0.801
  ]
 }
}
```

**Artifacts.** `runs/stage_b2/r1/K12_seed0.json` (sha256 4651f9b1fd); `runs/stage_b2/r1/K12_seed1.json` (sha256 fc778844df); `runs/stage_b2/r1/K12_seed2.json` (sha256 edd43d609d); `runs/stage_b2/r1/K3_seed0.json` (sha256 943dc39f50); `runs/stage_b2/r1/K3_seed1.json` (sha256 18d71c3e5c); `runs/stage_b2/r1/K3_seed2.json` (sha256 441152e952) … +3 more

---

## #188 · plan · stage log · plan §—
`7eadeb4dff97e864` ← `27091336096d88ef` · recorded 2026-10-13T11:53:42+00:00

**What.** Added REPORTING.md and TARGETS.md to the repo (verbatim) and wrote the plan for incorporating them.

**How.** docs/REPORTING.md and docs/TARGETS.md are your files unchanged; docs/REPORTING_IMPLEMENTATION.md has the requirement-by-requirement status, comparison against the paper, eight points that need your decision, and the build order. Nothing built yet.

**Artifacts.** `docs/REPORTING.md` (sha256 83c1784ccd); `docs/TARGETS.md` (sha256 1be00ab153); `docs/REPORTING_IMPLEMENTATION.md` (sha256 f8c90ec23e)

---

## #189 · plan · stage B · plan §4.2
`a80e630eca0ddb5d` ← `7eadeb4dff97e864` · recorded 2026-10-13T12:11:33+00:00

**What.** B2 rerun with a fixed world and the six paper metrics. First B2 run (r1) kept as legacy.

**How.** Fix: cluster centres are laid out so every one of the 4 category directions has equal between-cluster spread (needs more than 4 categories), so no direction holds only within-cluster jitter. New sweep: 6, 12, 24 categories x 3 seeds, one encoder per run. Every run now records global R2, invariant R2, variant R2, a12/a21 (raw and normalized) and block purity, plus how close paired samples are in category space. Results go to runs/stage_b2/r2; r1 stays as a legacy record (its 3-category runs were not a valid test). No pass numbers are locked; results are read sensibly against B1.

**Output.**
```json
{
 "output_dir": "runs/stage_b2/r2",
 "seeds": [
  0,
  1,
  2
 ],
 "sweep": [
  6,
  12,
  24
 ]
}
```

**Artifacts.** `configs/stage_b2.yaml` (sha256 de2bfdda09)

---

## #190 · run · stage B · plan §4.2
`c32652a4cd1372f5` ← `a80e630eca0ddb5d` · recorded 2026-10-13T12:15:15+00:00

**What.** Stage B2 K=6 seed=2 finished

**Output.**
```json
{
 "cluster_purity": 1.0,
 "generator_angle": 1.3,
 "kmeans_angle": 1.27,
 "label_angle": 1.3,
 "random_angle": 80.49
}
```

**Artifacts.** `runs/stage_b2/r2/K6_seed2.json` (sha256 c39b52eefc)

---

## #191 · run · stage B · plan §4.2
`6db7e639dd1059d1` ← `c32652a4cd1372f5` · recorded 2026-10-13T12:15:15+00:00

**What.** Stage B2 K=6 seed=1 finished

**Output.**
```json
{
 "cluster_purity": 0.833,
 "generator_angle": 1.2,
 "kmeans_angle": 2.23,
 "label_angle": 1.34,
 "random_angle": 82.98
}
```

**Artifacts.** `runs/stage_b2/r2/K6_seed1.json` (sha256 778fc3f679)

---

## #192 · run · stage B · plan §4.2
`30d575f2be7ff3f1` ← `6db7e639dd1059d1` · recorded 2026-10-13T12:15:17+00:00

**What.** Stage B2 K=6 seed=0 finished

**Output.**
```json
{
 "cluster_purity": 0.835,
 "generator_angle": 1.53,
 "kmeans_angle": 1.67,
 "label_angle": 1.65,
 "random_angle": 74.17
}
```

**Artifacts.** `runs/stage_b2/r2/K6_seed0.json` (sha256 db543a7663)

---

## #193 · run · stage B · plan §4.2
`4f45adc90890b845` ← `30d575f2be7ff3f1` · recorded 2026-10-13T12:18:51+00:00

**What.** Stage B2 K=12 seed=1 finished

**Output.**
```json
{
 "cluster_purity": 0.558,
 "generator_angle": 1.68,
 "kmeans_angle": 2.27,
 "label_angle": 2.27,
 "random_angle": 89.36
}
```

**Artifacts.** `runs/stage_b2/r2/K12_seed1.json` (sha256 673855cfd9)

---

## #194 · run · stage B · plan §4.2
`b853bfb6018a5105` ← `4f45adc90890b845` · recorded 2026-10-13T12:18:52+00:00

**What.** Stage B2 K=12 seed=0 finished

**Output.**
```json
{
 "cluster_purity": 0.584,
 "generator_angle": 1.84,
 "kmeans_angle": 2.29,
 "label_angle": 2.0,
 "random_angle": 87.45
}
```

**Artifacts.** `runs/stage_b2/r2/K12_seed0.json` (sha256 04a18acb52)

---

## #195 · run · stage B · plan §4.2
`a2d82e0da2d98e7b` ← `b853bfb6018a5105` · recorded 2026-10-13T12:18:52+00:00

**What.** Stage B2 K=12 seed=2 finished

**Output.**
```json
{
 "cluster_purity": 0.519,
 "generator_angle": 1.15,
 "kmeans_angle": 4.07,
 "label_angle": 1.35,
 "random_angle": 74.35
}
```

**Artifacts.** `runs/stage_b2/r2/K12_seed2.json` (sha256 f68806b407)

---

## #196 · run · stage B · plan §4.2
`7f48b357d34531e1` ← `a2d82e0da2d98e7b` · recorded 2026-10-13T12:22:38+00:00

**What.** Stage B2 K=24 seed=2 finished

**Output.**
```json
{
 "cluster_purity": 0.363,
 "generator_angle": 1.37,
 "kmeans_angle": 3.21,
 "label_angle": 1.47,
 "random_angle": 83.97
}
```

**Artifacts.** `runs/stage_b2/r2/K24_seed2.json` (sha256 0982985f59)

---

## #197 · run · stage B · plan §4.2
`85763e6e68b8d0ac` ← `7f48b357d34531e1` · recorded 2026-10-13T12:22:39+00:00

**What.** Stage B2 K=24 seed=1 finished

**Output.**
```json
{
 "cluster_purity": 0.396,
 "generator_angle": 1.74,
 "kmeans_angle": 6.73,
 "label_angle": 1.82,
 "random_angle": 87.36
}
```

**Artifacts.** `runs/stage_b2/r2/K24_seed1.json` (sha256 956d05ff66)

---

## #198 · run · stage B · plan §4.2
`d6efb68f1d8399c7` ← `85763e6e68b8d0ac` · recorded 2026-10-13T12:22:40+00:00

**What.** Stage B2 K=24 seed=0 finished

**Output.**
```json
{
 "cluster_purity": 0.331,
 "generator_angle": 1.66,
 "kmeans_angle": 2.97,
 "label_angle": 1.76,
 "random_angle": 88.46
}
```

**Artifacts.** `runs/stage_b2/r2/K24_seed0.json` (sha256 43da5bd601)

---

## #199 · plan · stage B · plan §4.2
`942abfb6fdb0900a` ← `d6efb68f1d8399c7` · recorded 2026-10-13T12:26:43+00:00

**What.** Formal B2 (docs/B2.md) targets locked; run launched: sigma_cat sweep x 3 seeds, one encoder per run.

**How.** World: 6 categories x 20 identities x 2 textures, all Gaussian inside (my reading of the spec, docs/B2_IMPLEMENTATION.md). Gates = B1's frozen criteria incl. its amended leakage floor. Targets T1-T4 and controls C1-C4 frozen in configs/stage_b2_spec.yaml (hash in stage_b2_spec.targets.sha256). Arms on one encoder per run: B1 generator twins, B2 k-means with discovered cluster count, oracle-count k-means, perfect-label pairs, C1 cross-cluster, C2 variant-block clusters, C3 singleton, C4 shuffled. Results to results/B2/, one line per run in docs/STATUS.md. A 300-step code check (not a result) confirmed the wiring.

**Output.**
```json
{
 "seeds": [
  0,
  1,
  2
 ],
 "sigma_cat_sweep": [
  0.1,
  0.4,
  0.6,
  0.8,
  1.0,
  1.5
 ],
 "targets": {
  "T1_construction_cost": {
   "applies_to": "clean world (sigma_cat = clean_sigma_cat)",
   "max_ratio": 2.0,
   "rule": "per seed, B2 (discovered-count k-means) rung-2 angle <= 2 x the B1 (generator twins) rung-2 angle, same encoder and seed"
  },
  "T2_purity_threshold": {
   "pair_validity_min": 0.95,
   "purity_min": 0.9,
   "rule": "every run with cluster purity >= 0.9 and pair validity >= 0.95 passes all gates"
  },
  "T3_graceful_degradation": {
   "angle_limit_deg": 5.0,
   "bound": "||A21||_rung2 <= ||A21||_rung1 x (1 + 2 x misgroup rate)  (monograph section 10; the sqrt form is also drawn)",
   "purity_floor_for_no_cliff": 0.7,
   "rule": "across the sigma_cat sweep, rung-2 angle and ||A21|| grow smoothly with misgroup rate; no run with purity >= 0.7 has a rung-2 angle above 5 deg; measured ||A21|| stays below the contamination bound"
  },
  "T4_loud_failure": {
   "C1_cross_cluster": {
    "angle_min_deg": 10.0,
    "rule": "split must not identify identity: rung-2 angle above 10 deg, and the pair-validity check fires (validity below 0.95)"
   },
   "C2_variant_clusters": {
    "angle_min_deg": 10.0,
    "rule": "must fail: rung-2 angle above 10 deg"
   },
   "C3_singleton": {
    "rule": "no valid pairs exist, so the rank check fires (zero pairs)"
   },
   "C4_shuffled": {
    "rule": "recorded, no required outcome"
   }
  }
 }
}
```

**Artifacts.** `configs/stage_b2_spec.yaml` (sha256 cb806eed90); `docs/B2.md` (sha256 5f6fb137b3); `docs/B2_IMPLEMENTATION.md` (sha256 c1f64ebef8)

---

## #200 · run · stage B · plan §4.2
`a772ffb010765197` ← `942abfb6fdb0900a` · recorded 2026-10-13T12:30:48+00:00

**What.** Stage B2 sigma_cat=0.1 seed=2 finished

**Output.**
```json
{
 "angle_b1": 11.62,
 "angle_b2": 11.71,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/B2/sigma_cat_0.1/2.json` (sha256 e96f30aeeb)

---

## #201 · run · stage B · plan §4.2
`e2132e87aa3ae69e` ← `a772ffb010765197` · recorded 2026-10-13T12:30:52+00:00

**What.** Stage B2 sigma_cat=0.1 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.67,
 "angle_b2": 14.37,
 "k_found": 5,
 "purity": 0.835
}
```

**Artifacts.** `results/B2/sigma_cat_0.1/0.json` (sha256 67326a627a)

---

## #202 · run · stage B · plan §4.2
`5cb265280259a7dc` ← `e2132e87aa3ae69e` · recorded 2026-10-13T12:30:54+00:00

**What.** Stage B2 sigma_cat=0.1 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.77,
 "angle_b2": 8.84,
 "k_found": 5,
 "purity": 0.833
}
```

**Artifacts.** `results/B2/sigma_cat_0.1/1.json` (sha256 659d18f30b)

---

## #203 · run · stage B · plan §4.2
`b5d6e3a38f0288e2` ← `5cb265280259a7dc` · recorded 2026-10-13T12:32:48+00:00

**What.** Stage B2 sigma_cat=0.4 seed=2 finished

**Output.**
```json
{
 "angle_b1": 11.07,
 "angle_b2": 11.4,
 "k_found": 5,
 "purity": 0.833
}
```

**Artifacts.** `results/B2/sigma_cat_0.4/2.json` (sha256 36049ce668)

---

## #204 · run · stage B · plan §4.2
`9af80a2693818ce7` ← `b5d6e3a38f0288e2` · recorded 2026-10-13T12:32:54+00:00

**What.** Stage B2 sigma_cat=0.4 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.42,
 "angle_b2": 10.65,
 "k_found": 6,
 "purity": 0.96
}
```

**Artifacts.** `results/B2/sigma_cat_0.4/0.json` (sha256 a11a87e115)

---

## #205 · run · stage B · plan §4.2
`14e3434fdc3666dc` ← `9af80a2693818ce7` · recorded 2026-10-13T12:32:55+00:00

**What.** Stage B2 sigma_cat=0.4 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.54,
 "angle_b2": 8.81,
 "k_found": 5,
 "purity": 0.833
}
```

**Artifacts.** `results/B2/sigma_cat_0.4/1.json` (sha256 d0c63007fa)

---

## #206 · run · stage B · plan §4.2
`3c142cc807fb0014` ← `14e3434fdc3666dc` · recorded 2026-10-13T12:34:50+00:00

**What.** Stage B2 sigma_cat=0.6 seed=2 finished

**Output.**
```json
{
 "angle_b1": 10.8,
 "angle_b2": 12.17,
 "k_found": 5,
 "purity": 0.814
}
```

**Artifacts.** `results/B2/sigma_cat_0.6/2.json` (sha256 97680d3372)

---

## #207 · run · stage B · plan §4.2
`04eafc21f92f379a` ← `3c142cc807fb0014` · recorded 2026-10-13T12:34:55+00:00

**What.** Stage B2 sigma_cat=0.6 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.2,
 "angle_b2": 13.69,
 "k_found": 6,
 "purity": 0.851
}
```

**Artifacts.** `results/B2/sigma_cat_0.6/0.json` (sha256 e44d0cbff8)

---

## #208 · run · stage B · plan §4.2
`e7042cd827569709` ← `04eafc21f92f379a` · recorded 2026-10-13T12:34:57+00:00

**What.** Stage B2 sigma_cat=0.6 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.49,
 "angle_b2": 9.33,
 "k_found": 5,
 "purity": 0.822
}
```

**Artifacts.** `results/B2/sigma_cat_0.6/1.json` (sha256 8aec28caa6)

---

## #209 · run · stage B · plan §4.2
`409ee894f4222344` ← `e7042cd827569709` · recorded 2026-10-13T12:37:01+00:00

**What.** Stage B2 sigma_cat=0.8 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.17,
 "angle_b2": 18.42,
 "k_found": 7,
 "purity": 0.767
}
```

**Artifacts.** `results/B2/sigma_cat_0.8/0.json` (sha256 da79a117e1)

---

## #210 · run · stage B · plan §4.2
`e6c25e0bd1af0ede` ← `409ee894f4222344` · recorded 2026-10-13T12:37:03+00:00

**What.** Stage B2 sigma_cat=0.8 seed=2 finished

**Output.**
```json
{
 "angle_b1": 10.71,
 "angle_b2": 34.55,
 "k_found": 12,
 "purity": 0.782
}
```

**Artifacts.** `results/B2/sigma_cat_0.8/2.json` (sha256 5b925b0606)

---

## #211 · run · stage B · plan §4.2
`9f1e43acf8f1c521` ← `e6c25e0bd1af0ede` · recorded 2026-10-13T12:37:07+00:00

**What.** Stage B2 sigma_cat=0.8 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.38,
 "angle_b2": 10.6,
 "k_found": 6,
 "purity": 0.766
}
```

**Artifacts.** `results/B2/sigma_cat_0.8/1.json` (sha256 5cdd82f216)

---

## #212 · run · stage B · plan §4.2
`64155201093fe02d` ← `9f1e43acf8f1c521` · recorded 2026-10-13T12:39:19+00:00

**What.** Stage B2 sigma_cat=1.0 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.1,
 "angle_b2": 49.26,
 "k_found": 11,
 "purity": 0.699
}
```

**Artifacts.** `results/B2/sigma_cat_1.0/0.json` (sha256 21d8818a42)

---

## #213 · run · stage B · plan §4.2
`d62c2d15171f64ae` ← `64155201093fe02d` · recorded 2026-10-13T12:39:20+00:00

**What.** Stage B2 sigma_cat=1.0 seed=2 finished

**Output.**
```json
{
 "angle_b1": 10.78,
 "angle_b2": 50.76,
 "k_found": 11,
 "purity": 0.696
}
```

**Artifacts.** `results/B2/sigma_cat_1.0/2.json` (sha256 f879425935)

---

## #214 · run · stage B · plan §4.2
`f15113197e454f74` ← `d62c2d15171f64ae` · recorded 2026-10-13T12:39:27+00:00

**What.** Stage B2 sigma_cat=1.0 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.3,
 "angle_b2": 82.39,
 "k_found": 12,
 "purity": 0.683
}
```

**Artifacts.** `results/B2/sigma_cat_1.0/1.json` (sha256 387eff3a91)

---

## #215 · run · stage B · plan §4.2
`967e4343b125e10e` ← `f15113197e454f74` · recorded 2026-10-13T12:41:31+00:00

**What.** Stage B2 sigma_cat=1.5 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.09,
 "angle_b2": 82.13,
 "k_found": 12,
 "purity": 0.57
}
```

**Artifacts.** `results/B2/sigma_cat_1.5/0.json` (sha256 a5bbc8f923)

---

## #216 · run · stage B · plan §4.2
`e6818748062c4c65` ← `967e4343b125e10e` · recorded 2026-10-13T12:41:34+00:00

**What.** Stage B2 sigma_cat=1.5 seed=2 finished

**Output.**
```json
{
 "angle_b1": 10.55,
 "angle_b2": 89.63,
 "k_found": 9,
 "purity": 0.523
}
```

**Artifacts.** `results/B2/sigma_cat_1.5/2.json` (sha256 43571b8ca7)

---

## #217 · run · stage B · plan §4.2
`99fdc66490f46430` ← `e6818748062c4c65` · recorded 2026-10-13T12:41:38+00:00

**What.** Stage B2 sigma_cat=1.5 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.36,
 "angle_b2": 79.46,
 "k_found": 9,
 "purity": 0.481
}
```

**Artifacts.** `results/B2/sigma_cat_1.5/1.json` (sha256 a3849cb5c0)

---

## #218 · result · stage B · plan §4.2
`3782f45374a8709c` ← `99fdc66490f46430` · recorded 2026-10-13T12:43:44+00:00

**What.** Formal B2 finished (18 runs): construction costs little, but the world is too hard for the gates and past purity ~0.8 the split breaks.

**How.** results/B2 (6 spread values x 3 seeds), report at results/B2/REPORT.md and docs/b2_results.html. Gates are B1's; B1 on the same encoders misses them too.

**Output.**
```json
{
 "T1": "met (ratios 1.35, 1.01, 1.01)",
 "T2": "could not be tested (discovered count merges two categories, purity 0.83)",
 "T3": "not met: angle jumps below purity ~0.8 (11.7 deg at 0.83, 21 at 0.77, 61 at 0.69, 84 at 0.52); ||A21|| over the contamination bound in 18 of 18 runs",
 "T4": "met (C1-C3 fail as required)"
}
```

**Artifacts.** `results/B2/REPORT.md` (sha256 224ad4cedd); `docs/b2_results.html` (sha256 67466ee6fb)

---

## #219 · decision · stage log · plan §—
`352cd5d23aa1db75` ← `3782f45374a8709c` · recorded 2026-10-13T22:35:28+00:00

**What.** DECIDE: created AGENTS.md, DECISION_POLICY.md, docs/DECISIONS.md (D9) and docs/EVIDENCE.md (P9) from the owner's message, because they were not in the repository.

**How.** Alternatives: ask the owner for the originals (rejected: the instruction says decide-don't-ask), or proceed without records (rejected: P9 must be registered before the run). Unknown content: D9's soft-enforcement activation condition (marked 'not supplied'; soft stays off in all confirmatory runs) and the derivation document (the noise-floor threshold is taken from monograph section 10).

**Artifacts.** `AGENTS.md` (sha256 852586f597); `DECISION_POLICY.md` (sha256 bbdd5bd9cb); `docs/DECISIONS.md` (sha256 b676752a3c); `docs/EVIDENCE.md` (sha256 203c69c592)

---

## #220 · decision · stage B2 · plan §D9
`b713bc574ce7d208` ← `352cd5d23aa1db75` · recorded 2026-10-13T22:43:44+00:00

**What.** D9 revision after nesting-angle diagnostics: hard stays default, soft armed but inactive; budget lever flat in B2 world; span-vs-perp truth gap 11.6-13 deg

**How.** experiments/diagnose_nesting.py: ideal 3-block world + trained B2 world (3 seeds), budget sweep, soft lambda sweep, none

**Output.**
```json
{
 "b2_nesting_perp_deg": "2.2-3.3",
 "b2_nesting_span_deg": "8.5-11.5",
 "b2_rung1_angle_deg": "3.1-4.7 flat in n1",
 "ideal_slope": -0.51,
 "truth_gap_deg": "11.6-13.0"
}
```

**Artifacts.** `results/diagnostics/nesting/ideal_world.json` (sha256 ad5f2347eb); `results/diagnostics/nesting/b2world_seed0.json` (sha256 e802575f21); `results/diagnostics/nesting/b2world_seed1.json` (sha256 a13e2bde05); `results/diagnostics/nesting/b2world_seed2.json` (sha256 73ee709296)

**Bearing on objectives —.** DECIDE: keep hard default; soft off (activation = truth outside H_k and reachable without contamination); gate keeps span definition, perp added as informational. Foreign-direction regime did not replicate the owner's claim.

---

## #221 · run · stage B · plan §4.2
`83682e7f32189064` ← `b713bc574ce7d208` · recorded 2026-10-13T22:45:14+00:00

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

**Artifacts.** `configs/stage_b1_nesting.yaml` (sha256 62dfddd6dd)

---

## #222 · run · stage B · plan §4.2
`72e9a68eda62a2dc` ← `83682e7f32189064` · recorded 2026-10-13T22:45:14+00:00

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

**Artifacts.** `configs/stage_b1_nesting.yaml` (sha256 62dfddd6dd)

---

## #223 · run · stage B · plan §4.2
`a0305283f5f1d45b` ← `72e9a68eda62a2dc` · recorded 2026-10-13T22:45:14+00:00

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

**Artifacts.** `configs/stage_b1_nesting.yaml` (sha256 62dfddd6dd)

---

## #224 · run · stage B · plan §4.2
`9da337fdf0c745d9` ← `a0305283f5f1d45b` · recorded 2026-10-13T22:52:51+00:00

**What.** Stage B1 arm=main seed=2 finished

**Output.**
```json
{
 "core_invariant_r2": 0.976,
 "rung_angles_deg": [
  1.06,
  1.18
 ],
 "seconds": 457.8,
 "variant_r2": [
  0.955,
  0.979
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/main_seed2.json` (sha256 05e9210d37)

---

## #225 · run · stage B · plan §4.2
`ada7bec40496daad` ← `9da337fdf0c745d9` · recorded 2026-10-13T22:53:14+00:00

**What.** Stage B1 arm=main seed=0 finished

**Output.**
```json
{
 "core_invariant_r2": 0.98,
 "rung_angles_deg": [
  0.66,
  1.48
 ],
 "seconds": 480.0,
 "variant_r2": [
  0.961,
  0.985
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/main_seed0.json` (sha256 a3e5a86ef6)

---

## #226 · run · stage B · plan §4.2
`155216ce65a23ba2` ← `ada7bec40496daad` · recorded 2026-10-13T22:53:29+00:00

**What.** Stage B1 arm=main seed=1 finished

**Output.**
```json
{
 "core_invariant_r2": 0.978,
 "rung_angles_deg": [
  1.13,
  1.18
 ],
 "seconds": 495.3,
 "variant_r2": [
  0.959,
  0.984
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/main_seed1.json` (sha256 ccd7aba990)

---

## #227 · run · stage B · plan §4.2
`86a2584c348e62e5` ← `155216ce65a23ba2` · recorded 2026-10-13T22:53:43+00:00

**What.** Stage B2 sigma_cat=0.1 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.68,
 "angle_b2": 14.74,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_nesting/sigma_cat_0.1/0.json` (sha256 a211423f61)

---

## #228 · run · stage B · plan §4.2
`861518b96350174d` ← `86a2584c348e62e5` · recorded 2026-10-13T22:54:07+00:00

**What.** Stage B2 sigma_cat=0.1 seed=2 finished

**Output.**
```json
{
 "angle_b1": 11.58,
 "angle_b2": 11.65,
 "k_found": 5,
 "purity": 0.836
}
```

**Artifacts.** `results/stage_b2_nesting/sigma_cat_0.1/2.json` (sha256 74e4d8c91b)

---

## #229 · run · stage B · plan §4.2
`aa5158c28fb1e6bb` ← `861518b96350174d` · recorded 2026-10-13T22:54:23+00:00

**What.** Stage B2 sigma_cat=0.1 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.63,
 "angle_b2": 8.66,
 "k_found": 5,
 "purity": 0.835
}
```

**Artifacts.** `results/stage_b2_nesting/sigma_cat_0.1/1.json` (sha256 d8a8a153e0)

---

## #230 · run · stage B · plan §4.2
`d9d5b25ffc5212c3` ← `aa5158c28fb1e6bb` · recorded 2026-10-13T22:57:50+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=2 finished

**Output.**
```json
{
 "core_invariant_r2": 0.556,
 "rung_angles_deg": [
  1.21,
  73.96
 ],
 "seconds": 299.0,
 "variant_r2": [
  0.955,
  0.554
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/shuffled_rung2_seed2.json` (sha256 1ba99117c9)

---

## #231 · run · stage B · plan §4.2
`efe926e285dbf03b` ← `d9d5b25ffc5212c3` · recorded 2026-10-13T22:58:09+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=0 finished

**Output.**
```json
{
 "core_invariant_r2": 0.494,
 "rung_angles_deg": [
  0.93,
  87.38
 ],
 "seconds": 295.4,
 "variant_r2": [
  0.961,
  0.495
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/shuffled_rung2_seed0.json` (sha256 d7b19edb2a)

---

## #232 · run · stage B · plan §4.2
`6439a46774add93c` ← `efe926e285dbf03b` · recorded 2026-10-13T22:58:22+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=1 finished

**Output.**
```json
{
 "core_invariant_r2": 0.517,
 "rung_angles_deg": [
  1.09,
  89.74
 ],
 "seconds": 292.7,
 "variant_r2": [
  0.959,
  0.512
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/shuffled_rung2_seed1.json` (sha256 0bf3df5acb)

---

## #233 · run · stage B · plan §4.2
`0a34462cc089ac42` ← `6439a46774add93c` · recorded 2026-10-13T23:02:19+00:00

**What.** Stage B1 arm=rank1_rung2 seed=2 finished

**Output.**
```json
{
 "core_invariant_r2": 0.528,
 "rung_angles_deg": [
  1.06,
  75.62
 ],
 "seconds": 268.9,
 "variant_r2": [
  0.955,
  0.534
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/rank1_rung2_seed2.json` (sha256 bfa19e9b8a)

---

## #234 · run · stage B · plan §4.2
`f6ad4863bc301982` ← `0a34462cc089ac42` · recorded 2026-10-13T23:02:40+00:00

**What.** Stage B1 arm=rank1_rung2 seed=0 finished

**Output.**
```json
{
 "core_invariant_r2": 0.486,
 "rung_angles_deg": [
  0.66,
  84.02
 ],
 "seconds": 271.2,
 "variant_r2": [
  0.961,
  0.486
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/rank1_rung2_seed0.json` (sha256 83e23eb0e2)

---

## #235 · run · stage B · plan §4.2
`7242f5a7ee728d71` ← `f6ad4863bc301982` · recorded 2026-10-13T23:02:52+00:00

**What.** Stage B1 arm=rank1_rung2 seed=1 finished

**Output.**
```json
{
 "core_invariant_r2": 0.581,
 "rung_angles_deg": [
  1.13,
  81.22
 ],
 "seconds": 270.0,
 "variant_r2": [
  0.959,
  0.589
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/rank1_rung2_seed1.json` (sha256 7e14ef7f6a)

---

## #236 · run · stage B · plan §4.2
`117cd8e8e1592379` ← `7242f5a7ee728d71` · recorded 2026-10-13T23:06:53+00:00

**What.** Stage B1 arm=no_inv seed=2 finished

**Output.**
```json
{
 "core_invariant_r2": 0.784,
 "rung_angles_deg": [
  31.28,
  27.22
 ],
 "seconds": 274.1,
 "variant_r2": [
  0.807,
  0.88
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/no_inv_seed2.json` (sha256 cd8c022c15)

---

## #237 · run · stage B · plan §4.2
`0f487b61f3d0b586` ← `117cd8e8e1592379` · recorded 2026-10-13T23:07:15+00:00

**What.** Stage B1 arm=no_inv seed=0 finished

**Output.**
```json
{
 "core_invariant_r2": 0.747,
 "rung_angles_deg": [
  36.2,
  25.28
 ],
 "seconds": 274.8,
 "variant_r2": [
  0.741,
  0.878
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/no_inv_seed0.json` (sha256 173a010416)

---

## #238 · run · stage B · plan §4.2
`d32ac31fde825a20` ← `0f487b61f3d0b586` · recorded 2026-10-13T23:07:27+00:00

**What.** Stage B1 arm=no_inv seed=1 finished

**Output.**
```json
{
 "core_invariant_r2": 0.742,
 "rung_angles_deg": [
  34.82,
  31.93
 ],
 "seconds": 275.3,
 "variant_r2": [
  0.735,
  0.852
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/no_inv_seed1.json` (sha256 12d49be806)

---

## #239 · run · stage B · plan §4.2
`950445af7131bdb9` ← `d32ac31fde825a20` · recorded 2026-10-13T23:11:29+00:00

**What.** Stage B1 arm=no_pred seed=2 finished

**Output.**
```json
{
 "core_invariant_r2": 0.986,
 "rung_angles_deg": [
  0.41,
  1.05
 ],
 "seconds": 275.5,
 "variant_r2": [
  0.99,
  0.989
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/no_pred_seed2.json` (sha256 75069386c6)

---

## #240 · run · stage B · plan §4.2
`0e962af98b02dfe8` ← `950445af7131bdb9` · recorded 2026-10-13T23:11:51+00:00

**What.** Stage B1 arm=no_pred seed=0 finished

**Output.**
```json
{
 "core_invariant_r2": 0.989,
 "rung_angles_deg": [
  0.34,
  1.28
 ],
 "seconds": 275.5,
 "variant_r2": [
  0.989,
  0.988
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/no_pred_seed0.json` (sha256 06d3392f78)

---

## #241 · run · stage B · plan §4.2
`3df3bea971e8d77a` ← `0e962af98b02dfe8` · recorded 2026-10-13T23:12:04+00:00

**What.** Stage B1 arm=no_pred seed=1 finished

**Output.**
```json
{
 "core_invariant_r2": 0.985,
 "rung_angles_deg": [
  0.34,
  0.92
 ],
 "seconds": 277.2,
 "variant_r2": [
  0.986,
  0.986
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/no_pred_seed1.json` (sha256 14a7fa6356)

---

## #242 · run · stage B · plan §4.2
`6b2031045c322aad` ← `3df3bea971e8d77a` · recorded 2026-10-13T23:16:06+00:00

**What.** Stage B1 arm=no_var seed=2 finished

**Output.**
```json
{
 "core_invariant_r2": 0.976,
 "rung_angles_deg": [
  2.38,
  9.81
 ],
 "seconds": 276.5,
 "variant_r2": [
  0.875,
  0.968
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/no_var_seed2.json` (sha256 0cc434c727)

---

## #243 · run · stage B · plan §4.2
`3086e3ead4acbd96` ← `6b2031045c322aad` · recorded 2026-10-13T23:16:27+00:00

**What.** Stage B1 arm=no_var seed=0 finished

**Output.**
```json
{
 "core_invariant_r2": 0.98,
 "rung_angles_deg": [
  2.11,
  9.52
 ],
 "seconds": 276.7,
 "variant_r2": [
  0.881,
  0.969
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/no_var_seed0.json` (sha256 775b2b7aa3)

---

## #244 · run · stage B · plan §4.2
`16576cc406cfbbe7` ← `3086e3ead4acbd96` · recorded 2026-10-13T23:16:41+00:00

**What.** Stage B1 arm=no_var seed=1 finished

**Output.**
```json
{
 "core_invariant_r2": 0.978,
 "rung_angles_deg": [
  2.64,
  7.43
 ],
 "seconds": 276.3,
 "variant_r2": [
  0.848,
  0.946
 ]
}
```

**Artifacts.** `results/stage_b1_nesting/no_var_seed1.json` (sha256 e506d542a2)

---

## #245 · result · stage B · plan §4.2
`826b6ed057f6d91d` ← `16576cc406cfbbe7` · recorded 2026-10-13T23:16:41+00:00

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

**Artifacts.** `results/stage_b1_nesting/report_20261013T231641052680.json` (sha256 4a7360e693)

**Verdict.** FAIL

---

## #246 · result · stage B · plan §P9
`cd3b2b660236fa66` ← `826b6ed057f6d91d` · recorded 2026-10-13T23:17:08+00:00

**What.** P9 outcome: REFUTED as worded (nesting unchanged: B1 1.22 deg, B2 10.31 deg gate definition / 2.82 deg orthogonal-complement; gap ~0 confirmed; other gates held)

**Output.**
```json
{
 "b1_nesting": "1.28->1.22",
 "b2_minus_b1_gap": 0.1,
 "b2_nesting_gate": "10.39->10.31",
 "b2_nesting_perp": 2.82,
 "rank_pass": "3/3 before and after"
}
```

**Artifacts.** `results/stage_b1_nesting/REPORT.md` (sha256 d2d397cd55); `results/stage_b2_nesting/REPORT.md` (sha256 8e87c06543)

**Bearing on objectives —.** Refuted as worded; reported as first-class result, no tuning. Cause: encoder-bias floor at rung 1 plus truth-definition gap; follow-ups P10/P11 registered.

**Verdict.** refuted

---

## #247 · run · stage B · plan §4.2
`3aecf971fcbd1d7c` ← `cd3b2b660236fa66` · recorded 2026-10-14T01:45:58+00:00

**What.** Stage B2 sigma_cat=0.1 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.63,
 "angle_b2": 8.66,
 "k_found": 5,
 "purity": 0.835
}
```

**Artifacts.** `results/stage_b2_purify/sigma_cat_0.1/1.json` (sha256 6f23d7e94e)

---

## #248 · run · stage B · plan §4.2
`f974ed856f6abea8` ← `3aecf971fcbd1d7c` · recorded 2026-10-14T01:46:01+00:00

**What.** Stage B2 sigma_cat=0.1 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.68,
 "angle_b2": 14.74,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_purify/sigma_cat_0.1/0.json` (sha256 20710aaa24)

---

## #249 · run · stage B · plan §4.2
`2ae8efd4b6017879` ← `f974ed856f6abea8` · recorded 2026-10-14T01:46:03+00:00

**What.** Stage B2 sigma_cat=0.1 seed=2 finished

**Output.**
```json
{
 "angle_b1": 11.58,
 "angle_b2": 11.65,
 "k_found": 5,
 "purity": 0.836
}
```

**Artifacts.** `results/stage_b2_purify/sigma_cat_0.1/2.json` (sha256 afedfbaff2)

---

## #250 · decision · stage B2 · plan §D10
`3974902815b81f31` ← `2ae8efd4b6017879` · recorded 2026-10-14T01:46:46+00:00

**What.** D10: nesting gate judged on orthogonal-complement reference (owner ruling); absolute nesting informational. D10a: Tier 1 purification and Tier 4 within-H1 whitening defined; E10/E10a registered before the run

**Output.**
```json
{
 "texture_block_cov_eig": "1.21/1.13/1.07/1.00"
}
```

**Artifacts.** `docs/DECISIONS.md` (sha256 926c258d56); `docs/EVIDENCE.md` (sha256 1dc003d3b6)

**Bearing on objectives —.** DECIDE: constants fixed before run (factor 4 x median, 5 iterations). Disclosure: D10 chosen after P9 showed 2.82 deg on the new definition. Item 2 checked: texture block has 4 varying directions, no world change.

---

## #251 · result · stage B2 · plan §E10a
`dd334914dd78f0ee` ← `3974902815b81f31` · recorded 2026-10-14T01:46:46+00:00

**What.** E10 confirmed (definitional); E10a confirmed: rung-2 gap 3.1 -> 18.7 (recovered 0.64 of the B1-B2 deficit, needs 0.60)

**Output.**
```json
{
 "gap_b1": 27.3,
 "gap_b2": 3.1,
 "gap_tier1": 19.7,
 "gap_tier1_4": 18.7,
 "nesting_absolute": 10.31,
 "nesting_complement": 2.82,
 "validity": "0.83->1.00"
}
```

**Artifacts.** `results/stage_b2_purify/REPORT.md` (sha256 e99cf56888)

**Bearing on objectives —.** Tier 1 does the work; Tier 4 adds nothing. Rung-2 angle, texture R2, leakage still miss in both arms.

**Verdict.** confirmed

---

## #252 · run · stage B · plan §4.2
`a6ef5dbf5e770154` ← `dd334914dd78f0ee` · recorded 2026-10-14T03:53:51+00:00

**What.** Stage B2 sigma_cat=0.1 seed=2 finished

**Output.**
```json
{
 "angle_b1": 11.58,
 "angle_b2": 11.65,
 "k_found": 5,
 "purity": 0.836
}
```

**Artifacts.** `results/stage_b2_noop/sigma_cat_0.1/2.json` (sha256 1db29d1d18)

---

## #253 · run · stage B · plan §4.2
`e899020ac45a3fbe` ← `a6ef5dbf5e770154` · recorded 2026-10-14T03:53:53+00:00

**What.** Stage B2 sigma_cat=0.1 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.68,
 "angle_b2": 14.74,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_noop/sigma_cat_0.1/0.json` (sha256 cfca2fa8c6)

---

## #254 · run · stage B · plan §4.2
`d9761a0725b61b46` ← `e899020ac45a3fbe` · recorded 2026-10-14T03:53:54+00:00

**What.** Stage B2 sigma_cat=0.1 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.63,
 "angle_b2": 8.66,
 "k_found": 5,
 "purity": 0.835
}
```

**Artifacts.** `results/stage_b2_noop/sigma_cat_0.1/1.json` (sha256 33779cbb78)

---

## #255 · result · stage B2 · plan §E10c
`f1af31df52390292` ← `d9761a0725b61b46` · recorded 2026-10-14T03:54:15+00:00

**What.** E10c confirmed; Tier 1 no-op control failed both readings (2.3-3.4% of clean pairs trimmed, rung-2 gap 27.3 -> 30.2, other metrics within 0.006)

**Output.**
```json
{
 "e10c": "confirmed",
 "noop_gap": "27.3->30.2",
 "noop_trim_fraction": "0.023-0.034",
 "subspace_move_deg_tier1": "11.6/4.6/6.4"
}
```

**Artifacts.** `results/stage_b2_noop/REPORT.md` (sha256 aa28f4d93e)

**Bearing on objectives —.** Purification does not damage the result, but is not a strict no-op on clean pairs: the 4 x median rule trims the noise tail. Owner decides whether this is a failure.

**Verdict.** mixed

---

## #256 · decision · stage B2 · plan §D11
`b2e9a9284e71973e` ← `f1af31df52390292` · recorded 2026-10-14T04:05:15+00:00

**What.** Naming fix and gap-fix rulings: E9/E10/E11 (nesting), E12/E13/E14 (gap ratio); Tier 1 canonical, Tier 4 demoted, probes registered not run, E13 scheduled, Tier 2 rebuild deferred and unsupervised (D11)

**Output.**
```json
{
 "E12": "confirmed 0.64, gate 17.0/19.5/19.5",
 "E13": "scheduled",
 "E14": "confirmed, subspace 0.76/0.90/1.41 deg from B1 reference",
 "noop": "failed both readings"
}
```

**Artifacts.** `docs/DECISIONS.md` (sha256 0e78e1a952); `docs/EVIDENCE.md` (sha256 632a169fb7); `docs/FIXES/2026-10-13_gap_ratio.md` (sha256 c5f052011a)

**Bearing on objectives —.** Earlier log rows use the old names (P9, P10, P11, E10a/b/c); mapping is in docs/EVIDENCE.md. DECIDE: Tier 4 made opt-in in code (purify.tier4, default false); historic configs set it true.

---

## #257 · note · stage B2 · plan §Tier2
`be3a367c9fa5a9bf` ← `b2e9a9284e71973e` · recorded 2026-10-14T04:05:15+00:00

**What.** Tier 2 diagnosis (analysis only): the sixth category is missed because the closest pair of category centres sits about one cluster radius apart in the clusterer's input, so silhouette prefers 5 over 6; k=6 separates them on 2 of 3 seeds; seed 2 also has k-means local minima

**Output.**
```json
{
 "closest_pair_over_radius": "1.13/1.05/0.90",
 "k6_purity": "0.999/1.0/0.901",
 "silhouette_prefers_5_in": "17/20,20/20,20/20 subsamples"
}
```

**Artifacts.** `results/diagnostics/tier2/seed0.json` (sha256 597ac573a7); `results/diagnostics/tier2/seed1.json` (sha256 d2b6ee8eec); `results/diagnostics/tier2/seed2.json` (sha256 40780096a8)

**Bearing on objectives —.** No rebuild. Owner statement recorded for the log: the iterative splitting mechanism passed every direct test; every remaining red number was traced to inputs (pairs) or the ruler (definitions), each with a fix, a prediction or an owner. Claude note: the rung-2 angle (~10 deg in both arms), texture R2 0.882 and leakage 0.028 have no confirmed cause yet.

---

## #258 · decision · stage B2 · plan §D12
`a233ca62efbfd676` ← `be3a367c9fa5a9bf` · recorded 2026-10-14T04:15:25+00:00

**What.** Owner ruling: Tier 1 no-op control PASS under the corrected criterion (D12 candidate); strict byte-identity reading refuted and replaced; E13 sweep scheduled; E14 blind re-confirmation frozen

**Output.**
```json
{
 "angle_to_truth_untreated_to_treated": "14.74->10.71, 8.66->8.61, 11.65->11.60",
 "rho_hat_excess": "0.159/0.157/0.147",
 "trimmed_B2": "0.181",
 "trimmed_clean": "0.023/0.025/0.034",
 "true_rho": "0.170/0.167/0.165"
}
```

**Artifacts.** `docs/DECISIONS.md` (sha256 a2e6d81263); `docs/EVIDENCE.md` (sha256 c81c982e46); `docs/FIXES/2026-10-13_gap_ratio.md` (sha256 f49b2c2259); `results/stage_b2_noop/ANALYSIS.md` (sha256 9d7ad83b02)

**Bearing on objectives —.** The corrected criterion was set after the control was seen, so the pass is retrospective. Claude's operationalization of 'no systematic harm' (worse on every seed and mean worsening over 0.5 seed-std) is flagged for owner confirmation. Earlier rows call the strict result a FAIL; this row replaces that reading.

---

## #259 · result · stage B2 · plan §E15-E17
`5c9d0225d0b59fe7` ← `a233ca62efbfd676` · recorded 2026-10-14T04:34:06+00:00

**What.** Attribution battery: E15 texture probe 0.910 (blocks 0.882): 76% of the texture shortfall is on the encoder side; E16 world ruled out; E17 leakage gate re-frozen at 0.0209 on normalized ||A21|| (D13)

**Output.**
```json
{
 "block": "0.862/0.887/0.897",
 "encoder_share": "0.76",
 "gate": 0.0209,
 "gate_met_b1_arm": "1/3",
 "probe": "0.894/0.907/0.930"
}
```

**Artifacts.** `results/diagnostics/attribution_battery/REPORT.md` (sha256 3b2c4bd4ff); `configs/gates_v2.yaml` (sha256 30bc3d52d5); `docs/EVIDENCE.md` (sha256 3136fb3d81); `docs/DECISIONS.md` (sha256 ad7bfa5595)

**Bearing on objectives —.** DECIDE: E11 not scheduled because the E15 rule leaves the 0.9-0.95 band uncovered (seeds 1, 2); owner decides. DECIDE (D13): the leakage gate is on the paper's normalized ||A21|| not max |R2|, power-law interpolation, d=12 for both rungs; alternatives listed in E17.

**Verdict.** mixed

---

## #260 · decision · stage B2 · plan §E11
`74b4a3a99680f63a` ← `5c9d0225d0b59fe7` · recorded 2026-10-14T05:45:03+00:00

**What.** E15 rule amended (0.9-0.95 band = encoder branch, post-hoc); E11 registered and scheduled (E11a multi-step prediction, then E11b longer training), not run

**Output.**
```json
{
 "e11_thresholds": "probe>=0.95 each seed; rung-1 angle<=2.8; B1-arm rung-2 angle<=7.7",
 "e15_probe": "0.894/0.907/0.930"
}
```

**Artifacts.** `docs/EVIDENCE.md` (sha256 99275d0334); `docs/FIXES/2026-10-13_gap_ratio.md` (sha256 21d54dc78a); `docs/STATUS.md` (sha256 0513290951)

**Bearing on objectives —.** DECIDE: thresholds for the E11 prediction (25% drop in the rung-1 and rung-2 angles, texture probe at the E15 0.95 line) are Claude's, flagged for owner confirmation; direction and order (multi-step first) are the owner's. Caveat recorded: a speed-0.2 block has little to predict at longer horizons, so E11a may not lower the texture floor.

---

## #261 · run · stage B · plan §4.2
`04c816541481f018` ← `74b4a3a99680f63a` · recorded 2026-10-14T06:23:48+00:00

**What.** Stage B2 sigma_cat=0.1 seed=2 finished

**Output.**
```json
{
 "angle_b1": 11.5,
 "angle_b2": 11.71,
 "k_found": 5,
 "purity": 0.831
}
```

**Artifacts.** `results/stage_b2_e11a/sigma_cat_0.1/2.json` (sha256 d0a9f23b8c)

---

## #262 · run · stage B · plan §4.2
`89a3d501ddae80b7` ← `04c816541481f018` · recorded 2026-10-14T06:23:50+00:00

**What.** Stage B2 sigma_cat=0.1 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.69,
 "angle_b2": 16.62,
 "k_found": 5,
 "purity": 0.836
}
```

**Artifacts.** `results/stage_b2_e11a/sigma_cat_0.1/0.json` (sha256 6c601008bd)

---

## #263 · run · stage B · plan §4.2
`4918b6893379204a` ← `89a3d501ddae80b7` · recorded 2026-10-14T06:23:57+00:00

**What.** Stage B2 sigma_cat=0.1 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.12,
 "angle_b2": 8.28,
 "k_found": 5,
 "purity": 0.833
}
```

**Artifacts.** `results/stage_b2_e11a/sigma_cat_0.1/1.json` (sha256 31670e84b7)

---

## #264 · result · stage B2 · plan §E11a
`6b9de09e4b96a205` ← `4918b6893379204a` · recorded 2026-10-14T06:24:51+00:00

**What.** E11a refuted: multi-step alignment (horizon 3) did not lower the encoder floor (texture probe 0.880/0.853/0.937, rung-1 angle 4.45, B1-arm rung-2 angle 10.10)

**Output.**
```json
{
 "gap_tier1": 17.6,
 "leak_gate_met": "0 of 3 arms",
 "probe": "0.880/0.853/0.937",
 "rung1_angle": 4.45,
 "rung2_angle_b1": 10.1
}
```

**Artifacts.** `results/stage_b2_e11a/REPORT.md` (sha256 f9513e1eb8); `docs/EVIDENCE.md` (sha256 be6184affa)

**Bearing on objectives —.** First-class refutation, no tuning. Matches the caveat registered with E11 (speed-0.2 block has little to predict at longer horizons; alignment pressure rises). DECIDE: the leakage gate of configs/gates_v2.yaml was applied for the first time here (first run after the E17 freeze). DECIDE: horizon implemented as the lejepa alignment term at lags 1..3, summed; horizon-1 path verified identical to the earlier code.

**Verdict.** refuted

---

## #265 · run · stage B · plan §4.2
`4fa2d47e17779bb4` ← `6b9de09e4b96a205` · recorded 2026-10-14T09:51:37+00:00

**What.** Stage B2 sigma_cat=0.1 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.77,
 "angle_b2": 8.92,
 "k_found": 5,
 "purity": 0.833
}
```

**Artifacts.** `results/stage_b2_e11b/sigma_cat_0.1/1.json` (sha256 1fc740a70c)

---

## #266 · run · stage B · plan §4.2
`5fe58d4e30229634` ← `4fa2d47e17779bb4` · recorded 2026-10-14T09:51:41+00:00

**What.** Stage B2 sigma_cat=0.1 seed=2 finished

**Output.**
```json
{
 "angle_b1": 11.65,
 "angle_b2": 11.73,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_e11b/sigma_cat_0.1/2.json` (sha256 01fa1969c1)

---

## #267 · run · stage B · plan §4.2
`481a8cbf67fef3f2` ← `5fe58d4e30229634` · recorded 2026-10-14T09:51:42+00:00

**What.** Stage B2 sigma_cat=0.1 seed=0 finished

**Output.**
```json
{
 "angle_b1": 9.82,
 "angle_b2": 9.82,
 "k_found": 6,
 "purity": 0.999
}
```

**Artifacts.** `results/stage_b2_e11b/sigma_cat_0.1/0.json` (sha256 6ca3fde726)

---

## #268 · result · stage B2 · plan §E11b
`ce8acf77b65bf3d6` ← `481a8cbf67fef3f2` · recorded 2026-10-14T09:52:18+00:00

**What.** E11b refuted: 4x longer training (40,000 steps) did not move the encoder floor (texture probe 0.892/0.905/0.932, rung-1 angle 3.63, B1-arm rung-2 angle 10.08); seed 0 incidentally found K=6

**Output.**
```json
{
 "probe": "0.892/0.905/0.932",
 "rung1_angle": 3.63,
 "rung2_angle_b1": 10.08,
 "seed0_K": 6,
 "seed0_purity": 0.999
}
```

**Artifacts.** `results/stage_b2_e11b/REPORT.md` (sha256 3e2b17b5d1); `docs/EVIDENCE.md` (sha256 213dc95572)

**Bearing on objectives —.** First-class refutation, no tuning. Both E11 variants refuted; E15 attribution to the encoder side stands but its cause is not identified. Seed-0 K=6 is a one-seed lead. The report's printed recovery fraction (0.62) is not comparable with E12 because seed 0 lifted the untreated gap.

**Verdict.** refuted

---

## #269 · run · stage B · plan §4.2
`a5e0cb7e8e1c6388` ← `ce8acf77b65bf3d6` · recorded 2026-10-15T00:26:08+00:00

**What.** Stage B2 sigma_cat=0.1 seed=2 finished

**Output.**
```json
{
 "angle_b1": 11.58,
 "angle_b2": 11.65,
 "k_found": 5,
 "purity": 0.836
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_0.1/2.json` (sha256 81d779c6bc)

---

## #270 · run · stage B · plan §4.2
`c5a0c4699626ba9f` ← `a5e0cb7e8e1c6388` · recorded 2026-10-15T00:26:11+00:00

**What.** Stage B2 sigma_cat=0.1 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.68,
 "angle_b2": 14.74,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_0.1/0.json` (sha256 80e3f5329c)

---

## #271 · run · stage B · plan §4.2
`4af29f9f48fcb4dc` ← `c5a0c4699626ba9f` · recorded 2026-10-15T00:26:12+00:00

**What.** Stage B2 sigma_cat=0.1 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.63,
 "angle_b2": 8.66,
 "k_found": 5,
 "purity": 0.835
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_0.1/1.json` (sha256 eb3e838be6)

---

## #272 · run · stage B · plan §4.2
`b79bf0bccf073a39` ← `4af29f9f48fcb4dc` · recorded 2026-10-15T00:28:03+00:00

**What.** Stage B2 sigma_cat=0.4 seed=2 finished

**Output.**
```json
{
 "angle_b1": 11.02,
 "angle_b2": 11.34,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_0.4/2.json` (sha256 ceb6826083)

---

## #273 · run · stage B · plan §4.2
`bf9ca526c8b81d2f` ← `b79bf0bccf073a39` · recorded 2026-10-15T00:28:08+00:00

**What.** Stage B2 sigma_cat=0.4 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.48,
 "angle_b2": 10.62,
 "k_found": 6,
 "purity": 0.967
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_0.4/0.json` (sha256 840f190912)

---

## #274 · run · stage B · plan §4.2
`273f55d83f2dccb0` ← `bf9ca526c8b81d2f` · recorded 2026-10-15T00:28:10+00:00

**What.** Stage B2 sigma_cat=0.4 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.42,
 "angle_b2": 8.54,
 "k_found": 6,
 "purity": 0.99
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_0.4/1.json` (sha256 82d811cab5)

---

## #275 · run · stage B · plan §4.2
`805f7fbe716f33ff` ← `273f55d83f2dccb0` · recorded 2026-10-15T00:30:01+00:00

**What.** Stage B2 sigma_cat=0.6 seed=2 finished

**Output.**
```json
{
 "angle_b1": 10.73,
 "angle_b2": 13.25,
 "k_found": 6,
 "purity": 0.848
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_0.6/2.json` (sha256 2faadfce2b)

---

## #276 · run · stage B · plan §4.2
`7f6c42facc0e7371` ← `805f7fbe716f33ff` · recorded 2026-10-15T00:30:06+00:00

**What.** Stage B2 sigma_cat=0.6 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.24,
 "angle_b2": 13.05,
 "k_found": 6,
 "purity": 0.849
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_0.6/0.json` (sha256 7b139c5f07)

---

## #277 · run · stage B · plan §4.2
`230208d56949d97b` ← `7f6c42facc0e7371` · recorded 2026-10-15T00:30:06+00:00

**What.** Stage B2 sigma_cat=0.6 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.43,
 "angle_b2": 10.38,
 "k_found": 6,
 "purity": 0.835
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_0.6/1.json` (sha256 bfd7058a8b)

---

## #278 · run · stage B · plan §4.2
`b7e137be0741fb2d` ← `230208d56949d97b` · recorded 2026-10-15T00:32:08+00:00

**What.** Stage B2 sigma_cat=0.8 seed=2 finished

**Output.**
```json
{
 "angle_b1": 10.64,
 "angle_b2": 28.23,
 "k_found": 9,
 "purity": 0.747
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_0.8/2.json` (sha256 b9b0bb5014)

---

## #279 · run · stage B · plan §4.2
`dc8f45713a19e595` ← `b7e137be0741fb2d` · recorded 2026-10-15T00:32:11+00:00

**What.** Stage B2 sigma_cat=0.8 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.38,
 "angle_b2": 69.57,
 "k_found": 12,
 "purity": 0.744
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_0.8/1.json` (sha256 0e34d99db1)

---

## #280 · run · stage B · plan §4.2
`f50874bd3d1f837d` ← `dc8f45713a19e595` · recorded 2026-10-15T00:32:11+00:00

**What.** Stage B2 sigma_cat=0.8 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.2,
 "angle_b2": 24.98,
 "k_found": 11,
 "purity": 0.769
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_0.8/0.json` (sha256 e74ec3d605)

---

## #281 · run · stage B · plan §4.2
`1da8d8fe93cef2b7` ← `f50874bd3d1f837d` · recorded 2026-10-15T00:34:15+00:00

**What.** Stage B2 sigma_cat=1.0 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.32,
 "angle_b2": 83.5,
 "k_found": 10,
 "purity": 0.653
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_1.0/1.json` (sha256 312c7371b9)

---

## #282 · run · stage B · plan §4.2
`302a52d16c3c03c5` ← `1da8d8fe93cef2b7` · recorded 2026-10-15T00:34:16+00:00

**What.** Stage B2 sigma_cat=1.0 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.14,
 "angle_b2": 50.65,
 "k_found": 10,
 "purity": 0.688
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_1.0/0.json` (sha256 2e60d88b94)

---

## #283 · run · stage B · plan §4.2
`d4d44e29f01672c2` ← `302a52d16c3c03c5` · recorded 2026-10-15T00:34:16+00:00

**What.** Stage B2 sigma_cat=1.0 seed=2 finished

**Output.**
```json
{
 "angle_b1": 10.69,
 "angle_b2": 61.92,
 "k_found": 12,
 "purity": 0.711
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_1.0/2.json` (sha256 9ee82ce1a0)

---

## #284 · run · stage B · plan §4.2
`16c15035e3613c97` ← `d4d44e29f01672c2` · recorded 2026-10-15T00:36:22+00:00

**What.** Stage B2 sigma_cat=1.5 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.04,
 "angle_b2": 79.76,
 "k_found": 9,
 "purity": 0.541
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_1.5/0.json` (sha256 db733e9582)

---

## #285 · run · stage B · plan §4.2
`5084e7cbd2f5a02f` ← `16c15035e3613c97` · recorded 2026-10-15T00:36:24+00:00

**What.** Stage B2 sigma_cat=1.5 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.41,
 "angle_b2": 87.93,
 "k_found": 10,
 "purity": 0.518
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_1.5/1.json` (sha256 110d04c6ef)

---

## #286 · run · stage B · plan §4.2
`96dc27c77e64fa28` ← `5084e7cbd2f5a02f` · recorded 2026-10-15T00:36:26+00:00

**What.** Stage B2 sigma_cat=1.5 seed=2 finished

**Output.**
```json
{
 "angle_b1": 10.49,
 "angle_b2": 84.02,
 "k_found": 10,
 "purity": 0.543
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/sigma_cat_1.5/2.json` (sha256 bfcfacc279)

---

## #287 · result · stage B2 · plan §E13
`2d46214a0b2f7d92` ← `96dc27c77e64fa28` · recorded 2026-10-15T00:37:51+00:00

**What.** E13 refuted as registered: the contamination model does not fit across the sweep (log-gap R2 0.667), purified points above the curve in 10 of 17 runs; Tier 1 recovers the gap only in the clean world

**Output.**
```json
{
 "above_curve": "10/17",
 "e14_blind_closer": "14/18",
 "e14_nodamage": "18/18",
 "r2": 0.667,
 "rho_hat_corr": -0.5,
 "tier1_gap_clean": "19.2/22.2/17.6",
 "tier1_gap_sigma_ge_0.4": "1-6",
 "tier4_cv": "1.384 vs 1.419"
}
```

**Artifacts.** `results/stage_b2_gapfix_sweep/E13_REPORT.md` (sha256 020d973870); `docs/EVIDENCE.md` (sha256 4d1e7bc878); `docs/FIXES/2026-10-13_gap_ratio.md` (sha256 df6f369c2b)

**Bearing on objectives —.** First-class refutation, no tuning. Observed (not proven) reason: cluster-built valid pairs carry within-category energy (~2 sigma_cat^2), unlike the B1 twins, so the purifier's silent-direction premise fails at sigma_cat >= 0.4. The exploratory refit (R2 0.714) is post hoc and does not rescue the model. E12 stays confirmed for the clean world only.

**Verdict.** refuted

---

## #288 · decision · stage B2 · plan §D14
`a35033cfa67680c2` ← `2d46214a0b2f7d92` · recorded 2026-10-16T08:47:25+00:00

**What.** Owner's post-sweep recommended actions recorded: D14 candidate (gap reference for cluster-built pairs), E20 registered, encoder-floor narrative retired, E18 drafted / E19 reserved, theory erratum for the contamination model

**Output.**
```json
{
 "achievable_gap": "19.5/5.3/3.2/2.3/1.8/1.3",
 "corrected_model": "R2 0.810, err 0.12, above curve 14/17",
 "e20_retro": "sigma0.4 Tier1 3/3 untreated 2/3; sigma0.6 0/3 (0.47-0.59)"
}
```

**Artifacts.** `docs/DECISIONS.md` (sha256 abb5b1db8f); `docs/EVIDENCE.md` (sha256 2c5ffd46f1); `docs/FIXES/2026-10-13_gap_ratio.md` (sha256 9e38593081); `results/stage_b2_gapfix_sweep/RECALIBRATION.md` (sha256 c3dd7b5248)

**Bearing on objectives —.** DECIDE (D14): reference = measured perfect-cluster gap (no fitted model); fraction 0.6 from E12; minimum achievable gap 3 is Claude's constant. DECIDE: E20 prediction could not be written before the numbers were seen; the sweep evaluation is retrospective and a blind run on seeds 3-5 is scheduled, not run. DECIDE: E18 drafted with Claude's thresholds; E19 not written because 'world geometry' is undefined. The owner's expectation that gaps clear at sigma 0.4-0.6 held at 0.4 and not at 0.6.

---

## #289 · run · stage B · plan §4.2
`9c095fb6df760737` ← `a35033cfa67680c2` · recorded 2026-10-16T08:52:19+00:00

**What.** Stage B2 sigma_cat=0.4 seed=3 finished

**Output.**
```json
{
 "angle_b1": 11.49,
 "angle_b2": 12.55,
 "k_found": 5,
 "purity": 0.836
}
```

**Artifacts.** `results/stage_b2_e20_blind/sigma_cat_0.4/3.json` (sha256 d369aac7e9)

---

## #290 · run · stage B · plan §4.2
`25d7ec2c34b61e55` ← `9c095fb6df760737` · recorded 2026-10-16T08:52:20+00:00

**What.** Stage B2 sigma_cat=0.4 seed=5 finished

**Output.**
```json
{
 "angle_b1": 13.6,
 "angle_b2": 17.69,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_e20_blind/sigma_cat_0.4/5.json` (sha256 5c0b6daa69)

---

## #291 · run · stage B · plan §4.2
`22a55081233cc3de` ← `25d7ec2c34b61e55` · recorded 2026-10-16T08:52:24+00:00

**What.** Stage B2 sigma_cat=0.4 seed=4 finished

**Output.**
```json
{
 "angle_b1": 6.23,
 "angle_b2": 9.11,
 "k_found": 9,
 "purity": 0.933
}
```

**Artifacts.** `results/stage_b2_e20_blind/sigma_cat_0.4/4.json` (sha256 d19529a11c)

---

## #292 · run · stage B · plan §4.2
`56ec8317b58d1e48` ← `22a55081233cc3de` · recorded 2026-10-16T08:54:06+00:00

**What.** Stage B2 sigma_cat=0.6 seed=3 finished

**Output.**
```json
{
 "angle_b1": 10.96,
 "angle_b2": 13.2,
 "k_found": 6,
 "purity": 0.823
}
```

**Artifacts.** `results/stage_b2_e20_blind/sigma_cat_0.6/3.json` (sha256 50647b3357)

---

## #293 · run · stage B · plan §4.2
`c0a73b59fb0c25d7` ← `56ec8317b58d1e48` · recorded 2026-10-16T08:54:13+00:00

**What.** Stage B2 sigma_cat=0.6 seed=4 finished

**Output.**
```json
{
 "angle_b1": 5.82,
 "angle_b2": 23.24,
 "k_found": 8,
 "purity": 0.853
}
```

**Artifacts.** `results/stage_b2_e20_blind/sigma_cat_0.6/4.json` (sha256 49a85a1ca0)

---

## #294 · run · stage B · plan §4.2
`49ce19dbbbbf1216` ← `c0a73b59fb0c25d7` · recorded 2026-10-16T08:54:15+00:00

**What.** Stage B2 sigma_cat=0.6 seed=5 finished

**Output.**
```json
{
 "angle_b1": 13.42,
 "angle_b2": 37.88,
 "k_found": 11,
 "purity": 0.821
}
```

**Artifacts.** `results/stage_b2_e20_blind/sigma_cat_0.6/5.json` (sha256 71b59453ae)

---

## #295 · result · stage B2 · plan §E20
`fdd9688c427e656a` ← `49ce19dbbbbf1216` · recorded 2026-10-16T08:54:45+00:00

**What.** E20 blind check: recalibrated gap criterion met on 3/3 fresh seeds at sigma_cat 0.4, 1/3 at 0.6; prediction not confirmed as worded; corrected contamination model passes narrowly (median error 0.24)

**Output.**
```json
{
 "K_found_sigma0.6": "6/8/11",
 "model_median_err": 0.24,
 "sigma0.4_tier1": "3/3 (0.76/0.62/0.68)",
 "sigma0.6_tier1": "1/3 (0.64/0.49/0.45)"
}
```

**Artifacts.** `results/stage_b2_e20_blind/E20_REPORT.md` (sha256 e9628d5aaa); `docs/EVIDENCE.md` (sha256 36722e9132)

**Bearing on objectives —.** Settings were frozen before launch. The yardstick is met at 0.4; at 0.6 the failing seeds are the ones with unstable cluster counts (8 and 11 found), pointing at cluster-count selection (E18 draft). Corrected model: lead that passed a blind test by a small margin; 3 of 6 runs individually above 25% error.

**Verdict.** mixed

---

## #296 · implementation · stage B2 · plan §E18
`544c4dd52f676ec1` ← `fdd9688c427e656a` · recorded 2026-10-16T09:03:53+00:00

**What.** E18 spectral K selection built and unit-tested (not run on the B2 world): Laplacian eigengap selector, optional spectral arms in the B2 pipeline

**Output.**
```json
{
 "constants": "15-NN, scale neighbour 7, subsample 3000, K in 2..12",
 "tests": "44 pass"
}
```

**Artifacts.** `src/isj/cluster.py` (sha256 a5b9171e97); `src/isj/stage_b2_spec.py` (sha256 d962da9275); `configs/stage_b2_e18.yaml` (sha256 f1f769e49e); `tests/test_spectral_k.py` (sha256 3728b96b19); `docs/EVIDENCE.md` (sha256 f988d04c06)

**Bearing on objectives —.** DECIDE: selector constants are standard defaults fixed before any use on the B2 world and not tuned on world data (E18 predicts K on that data); the unit tests use synthetic blobs only. DECIDE: integration is opt-in (default off) so earlier results reproduce; verified by an identical 200-step smoke output for the existing arms. The 200-step smoke numbers for the spectral arms are not results.

---

## #297 · run · stage B · plan §4.2
`adc6a0e31a038a4b` ← `544c4dd52f676ec1` · recorded 2026-10-16T10:37:03+00:00

**What.** Stage B2 sigma_cat=0.1 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.63,
 "angle_b2": 8.66,
 "k_found": 5,
 "purity": 0.835
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.1/1.json` (sha256 514337bbeb)

---

## #298 · run · stage B · plan §4.2
`0a7d629bbccde807` ← `adc6a0e31a038a4b` · recorded 2026-10-16T10:37:04+00:00

**What.** Stage B2 sigma_cat=0.1 seed=2 finished

**Output.**
```json
{
 "angle_b1": 11.58,
 "angle_b2": 11.65,
 "k_found": 5,
 "purity": 0.836
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.1/2.json` (sha256 c5573a797f)

---

## #299 · run · stage B · plan §4.2
`3598d2013b74be17` ← `0a7d629bbccde807` · recorded 2026-10-16T10:37:06+00:00

**What.** Stage B2 sigma_cat=0.1 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.68,
 "angle_b2": 14.74,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.1/0.json` (sha256 479ad413c6)

---

## #300 · run · stage B · plan §4.2
`26df13664349c615` ← `3598d2013b74be17` · recorded 2026-10-16T10:38:54+00:00

**What.** Stage B2 sigma_cat=0.1 seed=3 finished

**Output.**
```json
{
 "angle_b1": 12.3,
 "angle_b2": 14.72,
 "k_found": 5,
 "purity": 0.836
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.1/3.json` (sha256 1ffac03573)

---

## #301 · run · stage B · plan §4.2
`5b9d4ed83b79a258` ← `26df13664349c615` · recorded 2026-10-16T10:38:55+00:00

**What.** Stage B2 sigma_cat=0.1 seed=4 finished

**Output.**
```json
{
 "angle_b1": 5.82,
 "angle_b2": 8.02,
 "k_found": 6,
 "purity": 0.978
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.1/4.json` (sha256 8161f87656)

---

## #302 · run · stage B · plan §4.2
`fc4ed56bdca17c30` ← `5b9d4ed83b79a258` · recorded 2026-10-16T10:38:56+00:00

**What.** Stage B2 sigma_cat=0.1 seed=5 finished

**Output.**
```json
{
 "angle_b1": 14.22,
 "angle_b2": 14.29,
 "k_found": 7,
 "purity": 0.984
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.1/5.json` (sha256 aa578753b6)

---

## #303 · run · stage B · plan §4.2
`6891ae947835ab06` ← `fc4ed56bdca17c30` · recorded 2026-10-16T10:40:44+00:00

**What.** Stage B2 sigma_cat=0.4 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.48,
 "angle_b2": 10.62,
 "k_found": 6,
 "purity": 0.967
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.4/0.json` (sha256 fbab1a257b)

---

## #304 · run · stage B · plan §4.2
`4bdb0fbb572a63b1` ← `6891ae947835ab06` · recorded 2026-10-16T10:40:45+00:00

**What.** Stage B2 sigma_cat=0.4 seed=2 finished

**Output.**
```json
{
 "angle_b1": 11.02,
 "angle_b2": 11.34,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.4/2.json` (sha256 f281c2f347)

---

## #305 · run · stage B · plan §4.2
`bf3c74bbecbb3e8a` ← `4bdb0fbb572a63b1` · recorded 2026-10-16T10:40:49+00:00

**What.** Stage B2 sigma_cat=0.4 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.42,
 "angle_b2": 8.54,
 "k_found": 6,
 "purity": 0.99
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.4/1.json` (sha256 c31534cb49)

---

## #306 · run · stage B · plan §4.2
`adb5524e7384e32f` ← `bf3c74bbecbb3e8a` · recorded 2026-10-16T10:42:34+00:00

**What.** Stage B2 sigma_cat=0.4 seed=3 finished

**Output.**
```json
{
 "angle_b1": 11.49,
 "angle_b2": 12.55,
 "k_found": 5,
 "purity": 0.836
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.4/3.json` (sha256 760d0a168f)

---

## #307 · run · stage B · plan §4.2
`32ea505a376b5c81` ← `adb5524e7384e32f` · recorded 2026-10-16T10:42:42+00:00

**What.** Stage B2 sigma_cat=0.4 seed=5 finished

**Output.**
```json
{
 "angle_b1": 13.6,
 "angle_b2": 17.69,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.4/5.json` (sha256 ef1538ec92)

---

## #308 · run · stage B · plan §4.2
`33d7c897332a6eed` ← `32ea505a376b5c81` · recorded 2026-10-16T10:42:51+00:00

**What.** Stage B2 sigma_cat=0.4 seed=4 finished

**Output.**
```json
{
 "angle_b1": 6.23,
 "angle_b2": 9.11,
 "k_found": 9,
 "purity": 0.933
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.4/4.json` (sha256 6bb7b88dfe)

---

## #309 · run · stage B · plan §4.2
`34868baaccf2fb27` ← `33d7c897332a6eed` · recorded 2026-10-16T10:44:29+00:00

**What.** Stage B2 sigma_cat=0.6 seed=0 finished

**Output.**
```json
{
 "angle_b1": 10.24,
 "angle_b2": 13.05,
 "k_found": 6,
 "purity": 0.849
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.6/0.json` (sha256 6e131d9d7a)

---

## #310 · run · stage B · plan §4.2
`34ed493b0b2f1b5b` ← `34868baaccf2fb27` · recorded 2026-10-16T10:44:36+00:00

**What.** Stage B2 sigma_cat=0.6 seed=2 finished

**Output.**
```json
{
 "angle_b1": 10.73,
 "angle_b2": 13.25,
 "k_found": 6,
 "purity": 0.848
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.6/2.json` (sha256 d4a17c1451)

---

## #311 · run · stage B · plan §4.2
`aca72ecc232cdf2c` ← `34ed493b0b2f1b5b` · recorded 2026-10-16T10:44:45+00:00

**What.** Stage B2 sigma_cat=0.6 seed=1 finished

**Output.**
```json
{
 "angle_b1": 8.43,
 "angle_b2": 10.38,
 "k_found": 6,
 "purity": 0.835
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.6/1.json` (sha256 806a770564)

---

## #312 · run · stage B · plan §4.2
`b0afcc02fb50980e` ← `aca72ecc232cdf2c` · recorded 2026-10-16T10:46:21+00:00

**What.** Stage B2 sigma_cat=0.6 seed=3 finished

**Output.**
```json
{
 "angle_b1": 10.96,
 "angle_b2": 13.2,
 "k_found": 6,
 "purity": 0.823
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.6/3.json` (sha256 24ef9ad0b5)

---

## #313 · run · stage B · plan §4.2
`6d6b91c911712415` ← `b0afcc02fb50980e` · recorded 2026-10-16T10:46:32+00:00

**What.** Stage B2 sigma_cat=0.6 seed=5 finished

**Output.**
```json
{
 "angle_b1": 13.42,
 "angle_b2": 37.88,
 "k_found": 11,
 "purity": 0.821
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.6/5.json` (sha256 e2be3dbc63)

---

## #314 · run · stage B · plan §4.2
`be2ff5de93f2d29e` ← `6d6b91c911712415` · recorded 2026-10-16T10:46:39+00:00

**What.** Stage B2 sigma_cat=0.6 seed=4 finished

**Output.**
```json
{
 "angle_b1": 5.82,
 "angle_b2": 23.24,
 "k_found": 8,
 "purity": 0.853
}
```

**Artifacts.** `results/stage_b2_e18/sigma_cat_0.6/4.json` (sha256 211c4b574f)

---

## #315 · result · stage B2 · plan §E18
`517f1766c4505786` ← `be2ff5de93f2d29e` · recorded 2026-10-16T10:47:18+00:00

**What.** E18 refuted: spectral K selection found K=6 in 1 of 18 runs (silhouette 7 of 18); it overestimates K at sigma_cat 0.1 and 0.4 and scatters at 0.6

**Output.**
```json
{
 "K_sigma0.1": "10/8/8/10/11/10",
 "K_sigma0.4": "8/12/11/8/12/9",
 "K_sigma0.6": "12/3/6/10/8/2",
 "eigengap_ratio": "1.1-3.3",
 "silhouette_K6": "7/18",
 "spectral_K6": "1/18"
}
```

**Artifacts.** `results/stage_b2_e18/E18_REPORT.md` (sha256 cbcb41cc05); `docs/EVIDENCE.md` (sha256 1a3768b0db)

**Bearing on objectives —.** First-class refutation, constants not tuned. Hypothesis, untested: identity sub-clusters inside the 8-dim invariant output make both rules mis-count (spectral over, silhouette under). The cluster-count instability seen at sigma 0.6 in E20 is not resolved by this selector; E19 stays undefined.

**Verdict.** refuted

---

## #316 · note · stage B · plan §log
`6a06ceef4ce696bd` ← `517f1766c4505786` · recorded 2026-10-20T03:14:15+00:00

**What.** Declared stale: artifact src/isj/stage_b1.py of entry 134 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #317 · note · stage B · plan §log
`79ea7efe61f725dc` ← `6a06ceef4ce696bd` · recorded 2026-10-20T03:14:15+00:00

**What.** Declared stale: artifact experiments/run_stage_b1.py of entry 134 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #318 · note · stage B · plan §log
`4b5339be457a712d` ← `79ea7efe61f725dc` · recorded 2026-10-20T03:14:15+00:00

**What.** Declared stale: artifact docs/B2_IMPLEMENTATION.md of entry 199 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #319 · note · stage B · plan §log
`78ede720e6e5c6e6` ← `4b5339be457a712d` · recorded 2026-10-20T03:14:15+00:00

**What.** Declared stale: artifact AGENTS.md of entry 219 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #320 · note · stage B · plan §log
`cc600927148fa80c` ← `78ede720e6e5c6e6` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/DECISIONS.md of entry 219 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #321 · note · stage B · plan §log
`04ececa21fed7dee` ← `cc600927148fa80c` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/EVIDENCE.md of entry 219 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #322 · note · stage B · plan §log
`0d907b5a7fee4712` ← `04ececa21fed7dee` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/DECISIONS.md of entry 250 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #323 · note · stage B · plan §log
`d7039e694e8697c4` ← `0d907b5a7fee4712` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/EVIDENCE.md of entry 250 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #324 · note · stage B · plan §log
`dddc69bb60588039` ← `d7039e694e8697c4` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact results/stage_b2_noop/REPORT.md of entry 255 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #325 · note · stage B · plan §log
`9ef31285f0b2202b` ← `dddc69bb60588039` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/DECISIONS.md of entry 256 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #326 · note · stage B · plan §log
`c2be9569d0e9428e` ← `9ef31285f0b2202b` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/EVIDENCE.md of entry 256 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #327 · note · stage B · plan §log
`4704e69ce948f0ce` ← `c2be9569d0e9428e` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/FIXES/2026-10-13_gap_ratio.md of entry 256 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #328 · note · stage B · plan §log
`f6bf4fd77bd35bf9` ← `4704e69ce948f0ce` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/DECISIONS.md of entry 258 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #329 · note · stage B · plan §log
`ce6bd01f9a8716f7` ← `f6bf4fd77bd35bf9` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/EVIDENCE.md of entry 258 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #330 · note · stage B · plan §log
`fe4867360748e417` ← `ce6bd01f9a8716f7` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/FIXES/2026-10-13_gap_ratio.md of entry 258 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #331 · note · stage B · plan §log
`c69abffeb09a3509` ← `fe4867360748e417` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/EVIDENCE.md of entry 259 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #332 · note · stage B · plan §log
`b12f50a3db011244` ← `c69abffeb09a3509` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/DECISIONS.md of entry 259 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #333 · note · stage B · plan §log
`507f777e48eb7d33` ← `b12f50a3db011244` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/EVIDENCE.md of entry 260 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #334 · note · stage B · plan §log
`403e94d2cff3a555` ← `507f777e48eb7d33` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/FIXES/2026-10-13_gap_ratio.md of entry 260 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #335 · note · stage B · plan §log
`c1759d9638586fb4` ← `403e94d2cff3a555` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/STATUS.md of entry 260 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #336 · note · stage B · plan §log
`0790ec128cfeebb6` ← `c1759d9638586fb4` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/EVIDENCE.md of entry 264 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #337 · note · stage B · plan §log
`7e4e31c33d3ed03e` ← `0790ec128cfeebb6` · recorded 2026-10-20T03:14:16+00:00

**What.** Declared stale: artifact docs/EVIDENCE.md of entry 268 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #338 · note · stage B · plan §log
`29a4d77f53cedb53` ← `7e4e31c33d3ed03e` · recorded 2026-10-20T03:14:17+00:00

**What.** Declared stale: artifact docs/EVIDENCE.md of entry 287 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #339 · note · stage B · plan §log
`4864e3bf40f3f0bf` ← `29a4d77f53cedb53` · recorded 2026-10-20T03:14:17+00:00

**What.** Declared stale: artifact docs/FIXES/2026-10-13_gap_ratio.md of entry 287 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #340 · note · stage B · plan §log
`b1c13961e077a5c1` ← `4864e3bf40f3f0bf` · recorded 2026-10-20T03:14:17+00:00

**What.** Declared stale: artifact docs/EVIDENCE.md of entry 288 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #341 · note · stage B · plan §log
`36c1c2eebcd22fd4` ← `b1c13961e077a5c1` · recorded 2026-10-20T03:14:17+00:00

**What.** Declared stale: artifact docs/FIXES/2026-10-13_gap_ratio.md of entry 288 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #342 · note · stage B · plan §log
`17aa2eccdd5ec05d` ← `36c1c2eebcd22fd4` · recorded 2026-10-20T03:14:17+00:00

**What.** Declared stale: artifact docs/EVIDENCE.md of entry 295 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #343 · note · stage B · plan §log
`158394befa07d2f5` ← `17aa2eccdd5ec05d` · recorded 2026-10-20T03:14:17+00:00

**What.** Declared stale: artifact docs/EVIDENCE.md of entry 296 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #344 · note · stage B · plan §log
`f4610efb8bf4702b` ← `158394befa07d2f5` · recorded 2026-10-20T03:14:17+00:00

**What.** Declared stale: artifact docs/EVIDENCE.md of entry 315 changed after it was logged (later edits, see git history); the chain itself is intact

**Bearing on objectives —.** Housekeeping. The artifact fingerprint recorded at that entry no longer matches the file because the file was edited later (for B1: per-rung budgets, nesting options and attribution fields added for D9; behaviour at default settings unchanged). Git history holds every version.

---

## #345 · run · stage B · plan §4.2
`bdc10ce3fdc48444` ← `f4610efb8bf4702b` · recorded 2026-10-20T03:30:21+00:00

**What.** Stage B1 run started: seeds [20, 21, 22, 23, 24, 25, 26, 27, 28, 29], arms ['main', 'shuffled_rung2', 'rank1_rung2']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  20,
  21,
  22,
  23,
  24,
  25,
  26,
  27,
  28,
  29
 ]
}
```

**Artifacts.** `configs/stage_b1.yaml` (sha256 ae1f0bfc5d)

---

## #346 · run · stage B · plan §4.2
`4adcb878559b2533` ← `bdc10ce3fdc48444` · recorded 2026-10-20T03:36:14+00:00

**What.** Stage B1 arm=main seed=20 finished

**Output.**
```json
{
 "core_invariant_r2": 0.979,
 "rung_angles_deg": [
  0.87,
  0.99
 ],
 "seconds": 353.6,
 "variant_r2": [
  0.956,
  0.983
 ]
}
```

**Artifacts.** `results/stage_b1_e21/main_seed20.json` (sha256 14bccf1691)

---

## #347 · run · stage B · plan §4.2
`1d7c1c48a0d2ca7d` ← `4adcb878559b2533` · recorded 2026-10-20T03:36:37+00:00

**What.** Stage B2 sigma_cat=0.1 seed=20 finished

**Output.**
```json
{
 "angle_b1": 11.41,
 "angle_b2": 11.61,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.1/20.json` (sha256 f76acd34c8)

---

## #348 · run · stage B · plan §4.2
`a02cb8c25efa4b9f` ← `1d7c1c48a0d2ca7d` · recorded 2026-10-20T03:40:23+00:00

**What.** Stage B2 sigma_cat=0.1 seed=21 finished

**Output.**
```json
{
 "angle_b1": 9.92,
 "angle_b2": 9.97,
 "k_found": 5,
 "purity": 0.835
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.1/21.json` (sha256 18910611f9)

---

## #349 · run · stage B · plan §4.2
`e53d458393466f40` ← `a02cb8c25efa4b9f` · recorded 2026-10-20T03:41:41+00:00

**What.** Stage B1 arm=main seed=21 finished

**Output.**
```json
{
 "core_invariant_r2": 0.981,
 "rung_angles_deg": [
  0.84,
  1.26
 ],
 "seconds": 326.0,
 "variant_r2": [
  0.961,
  0.981
 ]
}
```

**Artifacts.** `results/stage_b1_e21/main_seed21.json` (sha256 b14fc51b3d)

---

## #350 · run · stage B · plan §4.2
`fce6cdb5b7bd6f06` ← `e53d458393466f40` · recorded 2026-10-20T03:43:13+00:00

**What.** Stage B2 sigma_cat=0.1 seed=22 finished

**Output.**
```json
{
 "angle_b1": 9.54,
 "angle_b2": 9.97,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.1/22.json` (sha256 f17c17878c)

---

## #351 · run · stage B · plan §4.2
`2133a70d81495d40` ← `fce6cdb5b7bd6f06` · recorded 2026-10-20T03:46:03+00:00

**What.** Stage B2 sigma_cat=0.1 seed=23 finished

**Output.**
```json
{
 "angle_b1": 7.04,
 "angle_b2": 8.01,
 "k_found": 5,
 "purity": 0.835
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.1/23.json` (sha256 63f65d4ba3)

---

## #352 · run · stage B · plan §4.2
`2806235b306f12a3` ← `2133a70d81495d40` · recorded 2026-10-20T03:46:12+00:00

**What.** Stage B1 arm=main seed=22 finished

**Output.**
```json
{
 "core_invariant_r2": 0.977,
 "rung_angles_deg": [
  1.46,
  1.15
 ],
 "seconds": 271.7,
 "variant_r2": [
  0.951,
  0.982
 ]
}
```

**Artifacts.** `results/stage_b1_e21/main_seed22.json` (sha256 52fc2db7dc)

---

## #353 · run · stage B · plan §4.2
`14cdb00e23a3d26e` ← `2806235b306f12a3` · recorded 2026-10-20T03:48:48+00:00

**What.** Stage B2 sigma_cat=0.1 seed=24 finished

**Output.**
```json
{
 "angle_b1": 9.38,
 "angle_b2": 11.34,
 "k_found": 5,
 "purity": 0.836
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.1/24.json` (sha256 fac6662c93)

---

## #354 · note · stage C · plan §infra
`f4094166d28b11a5` ← `14cdb00e23a3d26e` · recorded 2026-10-20T04:26:15+00:00

**What.** Vast.ai: stopped instance 56833962 (RTX PRO 5000) at the owner's request; attached a throwaway SSH public key (Vast key id 1617010, fingerprint SHA256:7LtHXiNP...mB2JM) to instance 56833948 (RTX 5090) at the owner's request; an accidental empty key entry (id 1617005) was created by a failed key generation and removed at once

**Output.**
```json
{
 "instance_stopped": 56833962,
 "key_attached_to": 56833948,
 "key_id": 1617010,
 "removal": "DELETE /api/v0/instances/56833948/ssh/1617010/"
}
```

**Bearing on objectives —.** DECIDE: the private key stays only in the session scratchpad and is never printed; the public key must be removed from the instance when the GPU work ends. Direct SSH from this sandbox is still blocked until the owner adds a Bash permission rule for ssh; nothing has connected to the instance.

---

## #355 · run · stage B · plan §4.2
`4f088e346dd250b0` ← `f4094166d28b11a5` · recorded 2026-10-20T10:22:18+00:00

**What.** Stage B1 run started: seeds [20, 21, 22, 23, 24, 25, 26, 27, 28, 29], arms ['main', 'shuffled_rung2', 'rank1_rung2']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  20,
  21,
  22,
  23,
  24,
  25,
  26,
  27,
  28,
  29
 ]
}
```

**Artifacts.** `configs/stage_b1.yaml` (sha256 ae1f0bfc5d)

---

## #356 · run · stage B · plan §4.2
`2a19723774a1f198` ← `4f088e346dd250b0` · recorded 2026-10-20T19:20:01+00:00

**What.** Stage B1 run started: seeds [20, 21, 22, 23, 24, 25, 26, 27, 28, 29], arms ['main', 'shuffled_rung2', 'rank1_rung2']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  20,
  21,
  22,
  23,
  24,
  25,
  26,
  27,
  28,
  29
 ]
}
```

**Artifacts.** `configs/stage_b1.yaml` (sha256 ae1f0bfc5d)

---

## #357 · run · stage B · plan §4.2
`6c3686c409945905` ← `2a19723774a1f198` · recorded 2026-10-20T19:24:29+00:00

**What.** Stage B1 arm=main seed=23 finished

**Output.**
```json
{
 "core_invariant_r2": 0.981,
 "rung_angles_deg": [
  0.85,
  0.85
 ],
 "seconds": 267.0,
 "variant_r2": [
  0.954,
  0.978
 ]
}
```

**Artifacts.** `results/stage_b1_e21/main_seed23.json` (sha256 a9944c506b)

---

## #358 · run · stage B · plan §4.2
`407c512ced867ad7` ← `6c3686c409945905` · recorded 2026-10-20T19:24:50+00:00

**What.** Stage B2 sigma_cat=0.1 seed=25 finished

**Output.**
```json
{
 "angle_b1": 13.14,
 "angle_b2": 13.21,
 "k_found": 6,
 "purity": 1.0
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.1/25.json` (sha256 ade7e5d92c)

---

## #359 · run · stage B · plan §4.2
`89bce6c23d2682f0` ← `407c512ced867ad7` · recorded 2026-10-20T19:35:41+00:00

**What.** Stage B1 run started: seeds [20, 21, 22, 23, 24, 25, 26, 27, 28, 29], arms ['main', 'shuffled_rung2', 'rank1_rung2']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  20,
  21,
  22,
  23,
  24,
  25,
  26,
  27,
  28,
  29
 ]
}
```

**Artifacts.** `configs/stage_b1.yaml` (sha256 ae1f0bfc5d)

---

## #360 · run · stage B · plan §4.2
`a2e32f1da9dba82f` ← `89bce6c23d2682f0` · recorded 2026-10-20T19:39:50+00:00

**What.** Stage B1 arm=main seed=24 finished

**Output.**
```json
{
 "core_invariant_r2": 0.98,
 "rung_angles_deg": [
  0.84,
  1.35
 ],
 "seconds": 248.8,
 "variant_r2": [
  0.957,
  0.984
 ]
}
```

**Artifacts.** `results/stage_b1_e21/main_seed24.json` (sha256 69308ca1dd)

---

## #361 · run · stage B · plan §4.2
`9831f15912064a1e` ← `a2e32f1da9dba82f` · recorded 2026-10-20T19:40:18+00:00

**What.** Stage B2 sigma_cat=0.1 seed=26 finished

**Output.**
```json
{
 "angle_b1": 10.17,
 "angle_b2": 10.3,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.1/26.json` (sha256 c18ba50318)

---

## #362 · note · stage C · plan §—
`501f6c41988d6dd5` ← `9831f15912064a1e` · recorded 2026-10-20T19:57:54+00:00

**What.** Completion plan created: docs/COMPLETION_PLAN.md tracks E21/E22 (finish + score), E23 (run + score), E24 (data, features, Stage C, verdict) and close-out, with done-when conditions per step. No new experiment registered.

**Artifacts.** `docs/COMPLETION_PLAN.md` (sha256 b3d3bd2135)

**Bearing on objectives —.** Planning document only; predictions unchanged.

---

## #363 · run · stage B · plan §4.2
`8dd937a66cc079c0` ← `501f6c41988d6dd5` · recorded 2026-10-20T19:58:14+00:00

**What.** Stage B1 run started: seeds [20, 21, 22, 23, 24, 25, 26, 27, 28, 29], arms ['main', 'shuffled_rung2', 'rank1_rung2']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  20,
  21,
  22,
  23,
  24,
  25,
  26,
  27,
  28,
  29
 ]
}
```

**Artifacts.** `configs/stage_b1.yaml` (sha256 ae1f0bfc5d)

---

## #364 · note · stage B · plan §—
`794bff1f14ae01b8` ← `8dd937a66cc079c0` · recorded 2026-10-20T20:02:10+00:00

**What.** Entry 296 recorded src/isj/stage_b2_spec.py before the E22 fields (image_geometry, angle_orth_deg) were added to it; declared stale. The E18 results are unaffected (the added fields are extra outputs).

**Bearing on objectives —.** Housekeeping: the fingerprint of a code file moved because it was extended for E22, not because any recorded result changed.

---

## #365 · run · stage B · plan §4.2
`3ec30bc12df7f0f6` ← `794bff1f14ae01b8` · recorded 2026-10-20T20:03:33+00:00

**What.** Stage B1 arm=main seed=25 finished

**Output.**
```json
{
 "core_invariant_r2": 0.985,
 "rung_angles_deg": [
  0.94,
  1.11
 ],
 "seconds": 319.3,
 "variant_r2": [
  0.966,
  0.987
 ]
}
```

**Artifacts.** `results/stage_b1_e21/main_seed25.json` (sha256 9788dfda3c)

---

## #366 · run · stage B · plan §4.2
`15662c9bc47c0a2b` ← `3ec30bc12df7f0f6` · recorded 2026-10-20T20:04:21+00:00

**What.** Stage B2 sigma_cat=0.1 seed=27 finished

**Output.**
```json
{
 "angle_b1": 11.18,
 "angle_b2": 11.25,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.1/27.json` (sha256 c68927f73e)

---

## #367 · note · stage C · plan §—
`ed8620971685ce36` ← `15662c9bc47c0a2b` · recorded 2026-10-20T20:04:38+00:00

**What.** docs/COMPLETION_PLAN.md is a living tracker (ticked off and extended as steps finish); entry 362 fingerprinted its first version, so that reference is declared superseded. Progress on it is recorded by separate chain entries.

**Bearing on objectives —.** Housekeeping: the tracker is meant to change.

---

## #368 · run · stage B · plan §4.2
`bd985bd2c57997a7` ← `ed8620971685ce36` · recorded 2026-10-20T20:07:38+00:00

**What.** Stage B2 sigma_cat=0.1 seed=28 finished

**Output.**
```json
{
 "angle_b1": 11.07,
 "angle_b2": 11.07,
 "k_found": 5,
 "purity": 0.833
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.1/28.json` (sha256 1a098e1b83)

---

## #369 · run · stage B · plan §4.2
`7535e2feda9c2311` ← `bd985bd2c57997a7` · recorded 2026-10-20T20:08:57+00:00

**What.** Stage B1 arm=main seed=26 finished

**Output.**
```json
{
 "core_invariant_r2": 0.982,
 "rung_angles_deg": [
  0.84,
  1.18
 ],
 "seconds": 323.9,
 "variant_r2": [
  0.96,
  0.986
 ]
}
```

**Artifacts.** `results/stage_b1_e21/main_seed26.json` (sha256 1a19a31c49)

---

## #370 · run · stage B · plan §4.2
`28fe49390722f945` ← `7535e2feda9c2311` · recorded 2026-10-20T20:09:51+00:00

**What.** Stage B2 sigma_cat=0.1 seed=29 finished

**Output.**
```json
{
 "angle_b1": 7.4,
 "angle_b2": 8.3,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.1/29.json` (sha256 c0803abb69)

---

## #371 · run · stage B · plan §4.2
`6402d734848dd6ba` ← `28fe49390722f945` · recorded 2026-10-20T20:12:03+00:00

**What.** Stage B2 sigma_cat=0.4 seed=20 finished

**Output.**
```json
{
 "angle_b1": 11.08,
 "angle_b2": 11.38,
 "k_found": 5,
 "purity": 0.833
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.4/20.json` (sha256 c27084e1d7)

---

## #372 · run · stage B · plan §4.2
`9b1bb779e8c6cb26` ← `6402d734848dd6ba` · recorded 2026-10-20T20:12:46+00:00

**What.** Stage B1 arm=main seed=27 finished

**Output.**
```json
{
 "core_invariant_r2": 0.98,
 "rung_angles_deg": [
  0.85,
  0.9
 ],
 "seconds": 229.6,
 "variant_r2": [
  0.954,
  0.983
 ]
}
```

**Artifacts.** `results/stage_b1_e21/main_seed27.json` (sha256 c5ce7d25e4)

---

## #373 · run · stage B · plan §4.2
`d393799bd2153344` ← `9b1bb779e8c6cb26` · recorded 2026-10-20T20:14:14+00:00

**What.** Stage B2 sigma_cat=0.4 seed=21 finished

**Output.**
```json
{
 "angle_b1": 10.31,
 "angle_b2": 10.92,
 "k_found": 5,
 "purity": 0.832
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.4/21.json` (sha256 8962938508)

---

## #374 · run · stage B · plan §4.2
`0718e84389049adc` ← `d393799bd2153344` · recorded 2026-10-20T20:16:26+00:00

**What.** Stage B2 sigma_cat=0.4 seed=22 finished

**Output.**
```json
{
 "angle_b1": 9.63,
 "angle_b2": 11.05,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.4/22.json` (sha256 cb8cdc40b1)

---

## #375 · run · stage B · plan §4.2
`5840c5a063e7cd95` ← `0718e84389049adc` · recorded 2026-10-20T20:16:40+00:00

**What.** Stage B1 arm=main seed=28 finished

**Output.**
```json
{
 "core_invariant_r2": 0.98,
 "rung_angles_deg": [
  0.83,
  1.67
 ],
 "seconds": 233.8,
 "variant_r2": [
  0.962,
  0.987
 ]
}
```

**Artifacts.** `results/stage_b1_e21/main_seed28.json` (sha256 e27d44fac2)

---

## #376 · run · stage B · plan §4.2
`4636ab24d16a2f00` ← `5840c5a063e7cd95` · recorded 2026-10-20T20:18:45+00:00

**What.** Stage B2 sigma_cat=0.4 seed=23 finished

**Output.**
```json
{
 "angle_b1": 8.4,
 "angle_b2": 9.12,
 "k_found": 5,
 "purity": 0.831
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.4/23.json` (sha256 81b3ee028a)

---

## #377 · run · stage B · plan §4.2
`63511b84b0588794` ← `4636ab24d16a2f00` · recorded 2026-10-20T20:20:29+00:00

**What.** Stage B1 arm=main seed=29 finished

**Output.**
```json
{
 "core_invariant_r2": 0.977,
 "rung_angles_deg": [
  1.44,
  1.36
 ],
 "seconds": 228.6,
 "variant_r2": [
  0.957,
  0.983
 ]
}
```

**Artifacts.** `results/stage_b1_e21/main_seed29.json` (sha256 394c61e3de)

---

## #378 · run · stage B · plan §4.2
`c01c776ac9e2fd79` ← `63511b84b0588794` · recorded 2026-10-20T20:20:53+00:00

**What.** Stage B2 sigma_cat=0.4 seed=24 finished

**Output.**
```json
{
 "angle_b1": 10.41,
 "angle_b2": 11.32,
 "k_found": 5,
 "purity": 0.832
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.4/24.json` (sha256 7de290bc7c)

---

## #379 · run · stage B · plan §4.2
`c509aa3da87a3656` ← `c01c776ac9e2fd79` · recorded 2026-10-20T20:23:07+00:00

**What.** Stage B2 sigma_cat=0.4 seed=25 finished

**Output.**
```json
{
 "angle_b1": 12.39,
 "angle_b2": 12.44,
 "k_found": 6,
 "purity": 0.994
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.4/25.json` (sha256 82d6f2beeb)

---

## #380 · run · stage B · plan §4.2
`6439fe04774d1e6b` ← `c509aa3da87a3656` · recorded 2026-10-20T20:24:10+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=20 finished

**Output.**
```json
{
 "core_invariant_r2": 0.861,
 "rung_angles_deg": [
  0.86,
  35.87
 ],
 "seconds": 221.4,
 "variant_r2": [
  0.959,
  0.863
 ]
}
```

**Artifacts.** `results/stage_b1_e21/shuffled_rung2_seed20.json` (sha256 b9741db935)

---

## #381 · run · stage B · plan §4.2
`6c60d66d084c016a` ← `6439fe04774d1e6b` · recorded 2026-10-20T20:25:17+00:00

**What.** Stage B2 sigma_cat=0.4 seed=26 finished

**Output.**
```json
{
 "angle_b1": 9.1,
 "angle_b2": 9.15,
 "k_found": 5,
 "purity": 0.834
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.4/26.json` (sha256 e2f247f5dc)

---

## #382 · run · stage B · plan §4.2
`a27cb206e2892ac9` ← `6c60d66d084c016a` · recorded 2026-10-20T20:27:24+00:00

**What.** Stage B2 sigma_cat=0.4 seed=27 finished

**Output.**
```json
{
 "angle_b1": 11.75,
 "angle_b2": 12.04,
 "k_found": 5,
 "purity": 0.832
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.4/27.json` (sha256 a619d4c224)

---

## #383 · run · stage B · plan §4.2
`85d208fb1cb197e6` ← `a27cb206e2892ac9` · recorded 2026-10-20T20:27:53+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=21 finished

**Output.**
```json
{
 "core_invariant_r2": 0.562,
 "rung_angles_deg": [
  0.88,
  88.8
 ],
 "seconds": 222.4,
 "variant_r2": [
  0.962,
  0.554
 ]
}
```

**Artifacts.** `results/stage_b1_e21/shuffled_rung2_seed21.json` (sha256 bc031f6de8)

---

## #384 · run · stage B · plan §4.2
`b093fa4bb740d257` ← `85d208fb1cb197e6` · recorded 2026-10-20T20:29:31+00:00

**What.** Stage B2 sigma_cat=0.4 seed=28 finished

**Output.**
```json
{
 "angle_b1": 10.51,
 "angle_b2": 11.27,
 "k_found": 5,
 "purity": 0.831
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.4/28.json` (sha256 16fa15bf30)

---

## #385 · run · stage B · plan §4.2
`c1b1d2fa25fa6e64` ← `b093fa4bb740d257` · recorded 2026-10-20T20:31:53+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=22 finished

**Output.**
```json
{
 "core_invariant_r2": 0.577,
 "rung_angles_deg": [
  1.44,
  86.25
 ],
 "seconds": 240.1,
 "variant_r2": [
  0.95,
  0.57
 ]
}
```

**Artifacts.** `results/stage_b1_e21/shuffled_rung2_seed22.json` (sha256 fb74f9617d)

---

## #386 · run · stage B · plan §4.2
`eb7bb01227f4c991` ← `c1b1d2fa25fa6e64` · recorded 2026-10-20T20:31:56+00:00

**What.** Stage B2 sigma_cat=0.4 seed=29 finished

**Output.**
```json
{
 "angle_b1": 7.52,
 "angle_b2": 9.75,
 "k_found": 6,
 "purity": 0.899
}
```

**Artifacts.** `results/stage_b2_e21/sigma_cat_0.4/29.json` (sha256 5762108aa9)

---

## #387 · run · stage B · plan §4.2
`88e5ebee4d59620b` ← `eb7bb01227f4c991` · recorded 2026-10-20T20:32:32+00:00

**What.** Stage B1 run started: seeds [30, 31, 32, 33, 34], arms ['main', 'shuffled_rung2']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  30,
  31,
  32,
  33,
  34
 ]
}
```

**Artifacts.** `configs/stage_b1_mlp.yaml` (sha256 2ef82b4ccc)

---

## #388 · run · stage B · plan §4.2
`f85ffd473d82d7d3` ← `88e5ebee4d59620b` · recorded 2026-10-20T20:33:05+00:00

**What.** Stage B1 arm=main seed=30 finished

**Output.**
```json
{
 "core_invariant_r2": 0.965,
 "rung_angles_deg": [
  74.0,
  68.33
 ],
 "seconds": 32.6,
 "variant_r2": [
  -0.001,
  0.535
 ]
}
```

**Artifacts.** `results/stage_b1_e23/main_seed30.json` (sha256 529e960c66)

---

## #389 · run · stage B · plan §4.2
`fc0e5d4a84613aa7` ← `f85ffd473d82d7d3` · recorded 2026-10-20T20:33:36+00:00

**What.** Stage B1 arm=main seed=31 finished

**Output.**
```json
{
 "core_invariant_r2": 0.983,
 "rung_angles_deg": [
  84.65,
  86.65
 ],
 "seconds": 31.1,
 "variant_r2": [
  -0.0,
  0.716
 ]
}
```

**Artifacts.** `results/stage_b1_e23/main_seed31.json` (sha256 1c9924a118)

---

## #390 · run · stage B · plan §4.2
`f6264a738fda0f3f` ← `fc0e5d4a84613aa7` · recorded 2026-10-20T20:34:06+00:00

**What.** Stage B1 arm=main seed=32 finished

**Output.**
```json
{
 "core_invariant_r2": 0.909,
 "rung_angles_deg": [
  89.42,
  86.9
 ],
 "seconds": 29.9,
 "variant_r2": [
  -0.001,
  0.451
 ]
}
```

**Artifacts.** `results/stage_b1_e23/main_seed32.json` (sha256 7be24ab7d4)

---

## #391 · run · stage B · plan §4.2
`3fa72968b966280c` ← `f6264a738fda0f3f` · recorded 2026-10-20T20:34:37+00:00

**What.** Stage B1 arm=main seed=33 finished

**Output.**
```json
{
 "core_invariant_r2": 0.957,
 "rung_angles_deg": [
  88.46,
  88.82
 ],
 "seconds": 31.6,
 "variant_r2": [
  -0.001,
  0.476
 ]
}
```

**Artifacts.** `results/stage_b1_e23/main_seed33.json` (sha256 c33a99c0e2)

---

## #392 · run · stage B · plan §4.2
`596048dca0b75300` ← `3fa72968b966280c` · recorded 2026-10-20T20:35:08+00:00

**What.** Stage B1 arm=main seed=34 finished

**Output.**
```json
{
 "core_invariant_r2": 0.959,
 "rung_angles_deg": [
  73.91,
  74.71
 ],
 "seconds": 30.3,
 "variant_r2": [
  -0.0,
  0.349
 ]
}
```

**Artifacts.** `results/stage_b1_e23/main_seed34.json` (sha256 d222fddd52)

---

## #393 · run · stage B · plan §4.2
`0b9526a2aa2a1735` ← `596048dca0b75300` · recorded 2026-10-20T20:35:36+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=23 finished

**Output.**
```json
{
 "core_invariant_r2": 0.478,
 "rung_angles_deg": [
  0.8,
  86.06
 ],
 "seconds": 223.1,
 "variant_r2": [
  0.954,
  0.475
 ]
}
```

**Artifacts.** `results/stage_b1_e21/shuffled_rung2_seed23.json` (sha256 9ac7f3fdba)

---

## #394 · run · stage B · plan §4.2
`01cea9236ffa0162` ← `0b9526a2aa2a1735` · recorded 2026-10-20T20:35:40+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=30 finished

**Output.**
```json
{
 "core_invariant_r2": 0.557,
 "rung_angles_deg": [
  59.08,
  86.69
 ],
 "seconds": 32.0,
 "variant_r2": [
  -0.001,
  0.218
 ]
}
```

**Artifacts.** `results/stage_b1_e23/shuffled_rung2_seed30.json` (sha256 8a0144334b)

---

## #395 · run · stage B · plan §4.2
`550bcd15dd879d09` ← `01cea9236ffa0162` · recorded 2026-10-20T20:36:10+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=31 finished

**Output.**
```json
{
 "core_invariant_r2": 0.511,
 "rung_angles_deg": [
  83.94,
  87.43
 ],
 "seconds": 30.6,
 "variant_r2": [
  -0.0,
  0.402
 ]
}
```

**Artifacts.** `results/stage_b1_e23/shuffled_rung2_seed31.json` (sha256 26c0c7923f)

---

## #396 · run · stage B · plan §4.2
`4d3d5831618145a8` ← `550bcd15dd879d09` · recorded 2026-10-20T20:36:40+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=32 finished

**Output.**
```json
{
 "core_invariant_r2": 0.385,
 "rung_angles_deg": [
  74.75,
  83.27
 ],
 "seconds": 30.0,
 "variant_r2": [
  -0.0,
  0.236
 ]
}
```

**Artifacts.** `results/stage_b1_e23/shuffled_rung2_seed32.json` (sha256 d81fd03f26)

---

## #397 · run · stage B · plan §4.2
`6c732a09e0012a76` ← `4d3d5831618145a8` · recorded 2026-10-20T20:37:12+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=33 finished

**Output.**
```json
{
 "core_invariant_r2": 0.623,
 "rung_angles_deg": [
  80.73,
  89.21
 ],
 "seconds": 31.7,
 "variant_r2": [
  -0.0,
  0.342
 ]
}
```

**Artifacts.** `results/stage_b1_e23/shuffled_rung2_seed33.json` (sha256 80e2ea7d5b)

---

## #398 · run · stage B · plan §4.2
`ef74e49db8d825f6` ← `6c732a09e0012a76` · recorded 2026-10-20T20:37:43+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=34 finished

**Output.**
```json
{
 "core_invariant_r2": 0.543,
 "rung_angles_deg": [
  87.43,
  82.92
 ],
 "seconds": 31.4,
 "variant_r2": [
  -0.0,
  0.211
 ]
}
```

**Artifacts.** `results/stage_b1_e23/shuffled_rung2_seed34.json` (sha256 6b8bb2620b)

---

## #399 · run · stage B · plan §4.2
`35e635a23f154abf` ← `ef74e49db8d825f6` · recorded 2026-10-20T20:39:14+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=24 finished

**Output.**
```json
{
 "core_invariant_r2": 0.563,
 "rung_angles_deg": [
  0.91,
  89.8
 ],
 "seconds": 218.1,
 "variant_r2": [
  0.957,
  0.571
 ]
}
```

**Artifacts.** `results/stage_b1_e21/shuffled_rung2_seed24.json` (sha256 0c3b1bd554)

---

## #400 · result · stage B · plan §E23
`580b6907e1fee32e` ← `35e635a23f154abf` · recorded 2026-10-20T20:40:16+00:00

**What.** E23 (generic MLP encoder, B1 ladder, seeds 30-34): REFUTED as registered. 8 of 9 non-excepted criteria held on 0 of 5 seeds; only core invariant R2 held (5 of 5). Rung 1 found no split (gap 1.1, rank-deficient on every seed, angle 82 deg, texture R2 -0.001); rung 2 angle 81 deg, gap 2.2; nesting 74 deg. Shuffled control behaved.

**How.** python experiments/run_stage_b1.py --config configs/stage_b1_mlp.yaml --seeds 30-34 --arms main shuffled_rung2; scored by experiments/analyse_e23.py with the E21 Part A scorer and leakage floor 0.01

**Output.**
```json
{
 "criteria_seeds_passing": {
  "all_other_non_excepted": 0,
  "core_invariant_r2": 5
 },
 "nesting_deg": 74.4,
 "rung1_angle_deg": 82.1,
 "rung1_gap": 1.1,
 "rung2_angle_deg": 81.1,
 "shuffled_control": "behaved"
}
```

**Artifacts.** `results/stage_b1_e23/E23_REPORT.md` (sha256 9d78fc5a2f); `experiments/analyse_e23.py` (sha256 281c9b7463)

**Bearing on objectives O2.** With the generic MLP encoder and the Stage A prediction recipe, the ladder's first split is not recovered in the B1 world, although the encoder trained normally and keeps the category content. The run does not separate architecture, objective and training budget.

**Verdict.** refuted

---

## #401 · run · stage B · plan §4.2
`1878974d27df2b63` ← `580b6907e1fee32e` · recorded 2026-10-20T20:42:57+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=25 finished

**Output.**
```json
{
 "core_invariant_r2": 0.533,
 "rung_angles_deg": [
  0.74,
  79.04
 ],
 "seconds": 222.6,
 "variant_r2": [
  0.966,
  0.529
 ]
}
```

**Artifacts.** `results/stage_b1_e21/shuffled_rung2_seed25.json` (sha256 1dfb07bce9)

---

## #402 · run · stage B · plan §4.2
`c167d2fe73cfc0a0` ← `1878974d27df2b63` · recorded 2026-10-20T20:46:30+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=26 finished

**Output.**
```json
{
 "core_invariant_r2": 0.485,
 "rung_angles_deg": [
  0.74,
  74.21
 ],
 "seconds": 213.4,
 "variant_r2": [
  0.961,
  0.492
 ]
}
```

**Artifacts.** `results/stage_b1_e21/shuffled_rung2_seed26.json` (sha256 ac0f803553)

---

## #403 · run · stage B · plan §4.2
`f346c40174b78acd` ← `c167d2fe73cfc0a0` · recorded 2026-10-20T20:49:54+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=27 finished

**Output.**
```json
{
 "core_invariant_r2": 0.562,
 "rung_angles_deg": [
  0.89,
  82.33
 ],
 "seconds": 203.6,
 "variant_r2": [
  0.955,
  0.569
 ]
}
```

**Artifacts.** `results/stage_b1_e21/shuffled_rung2_seed27.json` (sha256 da6d823b3c)

---

## #404 · run · stage B · plan §4.2
`803c21bc151c6943` ← `f346c40174b78acd` · recorded 2026-10-20T20:53:21+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=28 finished

**Output.**
```json
{
 "core_invariant_r2": 0.479,
 "rung_angles_deg": [
  0.73,
  75.78
 ],
 "seconds": 207.6,
 "variant_r2": [
  0.963,
  0.478
 ]
}
```

**Artifacts.** `results/stage_b1_e21/shuffled_rung2_seed28.json` (sha256 7044252e73)

---

## #405 · run · stage B · plan §4.2
`bee17235959f96c1` ← `803c21bc151c6943` · recorded 2026-10-20T20:56:42+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=29 finished

**Output.**
```json
{
 "core_invariant_r2": 0.439,
 "rung_angles_deg": [
  1.33,
  88.56
 ],
 "seconds": 200.2,
 "variant_r2": [
  0.956,
  0.453
 ]
}
```

**Artifacts.** `results/stage_b1_e21/shuffled_rung2_seed29.json` (sha256 8ddec7e805)

---

## #406 · run · stage B · plan §4.2
`699a8c77ab819169` ← `bee17235959f96c1` · recorded 2026-10-20T21:00:11+00:00

**What.** Stage B1 arm=rank1_rung2 seed=20 finished

**Output.**
```json
{
 "core_invariant_r2": 0.563,
 "rung_angles_deg": [
  0.87,
  82.75
 ],
 "seconds": 209.7,
 "variant_r2": [
  0.956,
  0.558
 ]
}
```

**Artifacts.** `results/stage_b1_e21/rank1_rung2_seed20.json` (sha256 17c5526d7e)

---

## #407 · run · stage B · plan §4.2
`7b71c77f57d5aa83` ← `699a8c77ab819169` · recorded 2026-10-20T21:03:33+00:00

**What.** Stage B1 arm=rank1_rung2 seed=21 finished

**Output.**
```json
{
 "core_invariant_r2": 0.507,
 "rung_angles_deg": [
  0.84,
  87.47
 ],
 "seconds": 201.8,
 "variant_r2": [
  0.961,
  0.503
 ]
}
```

**Artifacts.** `results/stage_b1_e21/rank1_rung2_seed21.json` (sha256 95321c71e4)

---

## #408 · run · stage B · plan §4.2
`a851ced1661896ee` ← `7b71c77f57d5aa83` · recorded 2026-10-20T21:06:58+00:00

**What.** Stage B1 arm=rank1_rung2 seed=22 finished

**Output.**
```json
{
 "core_invariant_r2": 0.467,
 "rung_angles_deg": [
  1.46,
  79.8
 ],
 "seconds": 204.7,
 "variant_r2": [
  0.951,
  0.473
 ]
}
```

**Artifacts.** `results/stage_b1_e21/rank1_rung2_seed22.json` (sha256 13d00b51ba)

---

## #409 · run · stage B · plan §4.2
`6064d72be6f2fd53` ← `a851ced1661896ee` · recorded 2026-10-20T21:10:21+00:00

**What.** Stage B1 arm=rank1_rung2 seed=23 finished

**Output.**
```json
{
 "core_invariant_r2": 0.641,
 "rung_angles_deg": [
  0.85,
  64.47
 ],
 "seconds": 203.1,
 "variant_r2": [
  0.954,
  0.632
 ]
}
```

**Artifacts.** `results/stage_b1_e21/rank1_rung2_seed23.json` (sha256 7cfe765975)

---

## #410 · run · stage B · plan §4.2
`5c2f8e3b8d776671` ← `6064d72be6f2fd53` · recorded 2026-10-20T21:13:44+00:00

**What.** Stage B1 arm=rank1_rung2 seed=24 finished

**Output.**
```json
{
 "core_invariant_r2": 0.504,
 "rung_angles_deg": [
  0.84,
  77.42
 ],
 "seconds": 203.4,
 "variant_r2": [
  0.957,
  0.515
 ]
}
```

**Artifacts.** `results/stage_b1_e21/rank1_rung2_seed24.json` (sha256 cb736fec5b)

---

## #411 · run · stage B · plan §4.2
`73dc19119d9d9d99` ← `5c2f8e3b8d776671` · recorded 2026-10-20T21:17:12+00:00

**What.** Stage B1 arm=rank1_rung2 seed=25 finished

**Output.**
```json
{
 "core_invariant_r2": 0.621,
 "rung_angles_deg": [
  0.94,
  69.25
 ],
 "seconds": 207.5,
 "variant_r2": [
  0.966,
  0.612
 ]
}
```

**Artifacts.** `results/stage_b1_e21/rank1_rung2_seed25.json` (sha256 b37991814f)

---

## #412 · run · stage B · plan §4.2
`f3102a2b2ea74caa` ← `73dc19119d9d9d99` · recorded 2026-10-20T21:20:34+00:00

**What.** Stage B1 arm=rank1_rung2 seed=26 finished

**Output.**
```json
{
 "core_invariant_r2": 0.528,
 "rung_angles_deg": [
  0.84,
  82.89
 ],
 "seconds": 202.5,
 "variant_r2": [
  0.96,
  0.53
 ]
}
```

**Artifacts.** `results/stage_b1_e21/rank1_rung2_seed26.json` (sha256 cb197be181)

---

## #413 · run · stage B · plan §4.2
`76c098486de02ef0` ← `f3102a2b2ea74caa` · recorded 2026-10-20T21:23:55+00:00

**What.** Stage B1 arm=rank1_rung2 seed=27 finished

**Output.**
```json
{
 "core_invariant_r2": 0.493,
 "rung_angles_deg": [
  0.85,
  87.24
 ],
 "seconds": 200.8,
 "variant_r2": [
  0.954,
  0.491
 ]
}
```

**Artifacts.** `results/stage_b1_e21/rank1_rung2_seed27.json` (sha256 1c3e94423f)

---

## #414 · run · stage B · plan §4.2
`5597e0137871a453` ← `76c098486de02ef0` · recorded 2026-10-20T21:27:18+00:00

**What.** Stage B1 arm=rank1_rung2 seed=28 finished

**Output.**
```json
{
 "core_invariant_r2": 0.319,
 "rung_angles_deg": [
  0.83,
  81.05
 ],
 "seconds": 202.2,
 "variant_r2": [
  0.962,
  0.323
 ]
}
```

**Artifacts.** `results/stage_b1_e21/rank1_rung2_seed28.json` (sha256 866eaf9e64)

---

## #415 · run · stage B · plan §4.2
`c18387e28aec835b` ← `5597e0137871a453` · recorded 2026-10-20T21:30:43+00:00

**What.** Stage B1 arm=rank1_rung2 seed=29 finished

**Output.**
```json
{
 "core_invariant_r2": 0.511,
 "rung_angles_deg": [
  1.44,
  84.55
 ],
 "seconds": 205.3,
 "variant_r2": [
  0.957,
  0.519
 ]
}
```

**Artifacts.** `results/stage_b1_e21/rank1_rung2_seed29.json` (sha256 df7d30c84c)

---

## #416 · result · stage B · plan §E21
`badebc8fb1f57a5c` ← `c18387e28aec835b` · recorded 2026-10-20T21:31:49+00:00

**What.** E21 (confirmatory re-run, fresh seeds 20-29): Part A (B1 world, 30 runs) REFUTED as registered: the frozen rule needs every criterion on every seed and the rank test flagged rung 2 on seed 21; the other 99 of 100 criterion-seed checks held (angles ~1 deg, texture R2 0.958, identity R2 0.983, gap ratios ~50, nesting 1.13 deg, D13 leakage gate met 10/10), controls behaved. Part B (B2 world, 20 runs) CONFIRMED: sigma 0.1 recovery 0.69 with Tier 1 gap above 10 in 10/10; sigma 0.4 E20 criterion in 9/10; nesting below 5 deg in every run; no metric damaged. E21 as a whole not confirmed.

**How.** experiments/run_stage_b1.py (stage_b1.yaml, arms main/shuffled_rung2/rank1_rung2, seeds 20-29) and run_stage_b2_spec.py (stage_b2_noop.yaml, sigma 0.1 and 0.4, seeds 20-29); scored by experiments/analyse_e21_e22.py against the registered text

**Output.**
```json
{
 "deficit_recovered_sigma0.1": 0.69,
 "e20_criterion_sigma0.4": "9/10",
 "partA": "refuted (rank_test fails on seed 21)",
 "partA_criteria_checks_passing": "99/100",
 "partB": "confirmed (4/4 sub-claims)",
 "tier1_gap_sigma0.1": 19.3
}
```

**Artifacts.** `results/stage_b1_e21/E21_REPORT.md` (sha256 afd74de954); `results/stage_b2_e21/E21_E22_REPORT.md` (sha256 15a705a565); `experiments/analyse_e21_e22.py` (sha256 3690662850)

**Bearing on objectives O2.** On fresh seeds the mechanism numbers reproduce and the Tier 1 gap fix holds; the registered all-seeds verdict rule is broken by a single rank-test flag.

**Verdict.** mixed: part A refuted, part B confirmed

---

## #417 · result · stage B · plan §E22
`2c5e9a6aac0b63fc` ← `badebc8fb1f57a5c` · recorded 2026-10-20T21:31:49+00:00

**What.** E22 (probe-image explanation, direct test on the E21 Part B runs): CONFIRMED. Orthogonalised rung-2 angle at most 5 deg in 20 of 20 runs (mean 2.76 deg; largest 4.85), at least 3 deg below the raw angle in 20 of 20 (raw 10.07 deg). Texture image sits 77.5 deg from the identity+category images; orthogonalising removes 0.5-1.6% of the identity image.

**How.** fields image_geometry and angle_orth_deg in the E21 Part B run files; scored by experiments/analyse_e21_e22.py

**Output.**
```json
{
 "orth_angle_mean_deg": 2.76,
 "raw_angle_mean_deg": 10.07,
 "runs_3deg_lower": "20/20",
 "runs_orth_le_5": "20/20"
}
```

**Artifacts.** `results/stage_b2_e21/E21_E22_REPORT.md` (sha256 15a705a565)

**Bearing on objectives O2.** The roughly 10 deg rung-2 angle is mostly a definition effect of the identity probe image overlapping the texture image, not an estimation floor.

**Verdict.** confirmed

---

## #418 · result · stage C · plan §E24
`f11b2f04fade23e0` ← `2c5e9a6aac0b63fc` · recorded 2026-10-20T22:51:03+00:00

**What.** E24 (robot data, ManiSkill3 PickCube-v1 and PushCube-v1, 100 groups x 8 trajectories each, frozen ResNet-50 + JEPA head, 3 split seeds per task): NOT confirmed for either task. P1 viewpoint response ratio 1.37 (PickCube) and 1.17 (PushCube) against the registered threshold 3 (paper 8.4x / 14.0x), failing on every seed; P2 trajectory ratio 1.74 (PickCube, 3/3 seeds) and 1.51 (PushCube, 1/3 seeds) against 1.5; P3 controls held; P4 camera decoding from the variant block 0.93-1.00 but from the invariant content 0.61 (PickCube) and 0.69 (PushCube) against the 0.65 bound. No clean block boundary: rung-1 gap ratio 1.11 / 1.76, rank monitor passed 0/3 at both rungs.

**How.** experiments/robot: gen_robot_data.py (200 groups), extract_features.py (frozen ResNet-50), run_stage_c.py (head 6000 steps, split seeds 0-2 per task), build_stage_c_report.py; scored against the registered E24 text

**Output.**
```json
{
 "P1_ratio": {
  "PickCube": 1.37,
  "PushCube": 1.17
 },
 "P2_ratio": {
  "PickCube": 1.74,
  "PushCube": 1.51
 },
 "P3": "held",
 "P4_camera_from_Q1": {
  "PickCube": 0.612,
  "PushCube": 0.686
 },
 "rung1_gap_ratio": {
  "PickCube": 1.11,
  "PushCube": 1.76
 },
 "verdict": "not confirmed (both tasks)"
}
```

**Artifacts.** `results/stage_c/REPORT.md` (sha256 10f0ab0a5f); `results/stage_c/PickCube/split0.json` (sha256 377838a4ce); `results/stage_c/PushCube/split0.json` (sha256 c44bfc3c1c)

**Bearing on objectives O3.** On simulated robot data with a frozen ImageNet encoder plus a small trained head, the viewpoint change does not separate into a clean block, so the paper-style two-block response ratios are not reproduced; the claim is limited to what the registered setup tests (frozen encoder, simulated data, our own trajectory scheme).

**Verdict.** refuted

---

## #419 · note · stage C · plan §close-out
`d782cce44fefdf09` ← `f11b2f04fade23e0` · recorded 2026-10-20T22:57:36+00:00

**What.** Completion plan finished: Phases 0-4 done. Final report docs/FINAL_REPORT.md: E21 Part A refuted as registered (one rank-test flag; 99/100 checks pass), E21 Part B confirmed, E22 confirmed, E23 refuted (generic MLP encoder does not recover the first split), E24 not confirmed on either task (no clean viewpoint block with frozen ResNet-50 features on simulated robot data). Tests 44 passed; log verifies; predictions unedited.

**Artifacts.** `docs/FINAL_REPORT.md` (sha256 a53512d317); `docs/COMPLETION_PLAN.md` (sha256 f3e9743b4d)

**Bearing on objectives O2, O3.** The mechanism is supported with the mirror encoder in the controlled worlds (E21, E22); it is not shown with a generic encoder (E23) or on the simulated robot data (E24).

---

## #420 · note · stage C · plan §—
`3b629012fc99147b` ← `d782cce44fefdf09` · recorded 2026-10-20T22:57:47+00:00

**What.** Entry 420 fingerprinted docs/COMPLETION_PLAN.md before the plan's last ticks were written; the plan is a living tracker, so that reference is declared superseded.

**Bearing on objectives —.** Housekeeping only; no result changed.

---

## #421 · note · stage C · plan §—
`e7e38133efd22b75` ← `3b629012fc99147b` · recorded 2026-10-20T22:57:55+00:00

**What.** Entry 419 (completion close-out) fingerprinted docs/COMPLETION_PLAN.md before the plan's last ticks were written; the plan is a living tracker, so that reference is declared superseded. (The previous housekeeping entry named index 420 by mistake; entry 419 is the correct one.)

**Bearing on objectives —.** Housekeeping only; no result changed.

---

## #422 · plan · stage B · plan §E25-E27 registration
`2f5fd47aace3c7d1` ← `e7e38133efd22b75` · recorded 2026-10-21T01:28:28+00:00

**What.** Owner request 2026-10-21: test whether iterative splitting works on the latent space of any encoder. Registered E25 (is the fast block absent from the prediction-trained MLP at the original speeds), E26 (equal predictability, generic MLP + prediction recipe), E27 (architecture x objective at equal predictability; the owner's claim that no present block is unseparable). Decision D15 adds layered criteria (presence first, then separability), frozen by hash before any run. Instruments added: nonlinear presence probe in the B1 runner.

**How.** docs/EVIDENCE.md E25-E27 and docs/DECISIONS.md D15 written before the runs; plan docs/PLAN_ENCODER_GENERALITY.md; criteria configs/layered.yaml (sha in configs/layered.sha256)

**Artifacts.** `configs/layered.yaml` (sha256 9700adeee8); `configs/layered.sha256` (sha256 b372c3bd14); `configs/stage_b1_mlp.yaml` (sha256 2ef82b4ccc); `configs/stage_b1_eqrho_mlp_predict.yaml` (sha256 ed2af0d144); `configs/stage_b1_eqrho_mirror_lejepa.yaml` (sha256 c47f81349d); `configs/stage_b1_eqrho_mlp_lejepa.yaml` (sha256 69e5527e20) … +2 more

**Bearing on objectives O2.** Pre-registration: thresholds (presence 0.9 present, 0.5 absent) and the verdict rules are fixed before data.

---

## #423 · note · stage B · plan §—
`43be8cb78de3cc92` ← `2f5fd47aace3c7d1` · recorded 2026-10-21T01:28:38+00:00

**What.** Housekeeping: entry 288 fingerprinted docs/DECISIONS.md, which was legitimately extended afterwards (D15 / presence probe / new check modes); reference declared superseded. No recorded result changed.

**Bearing on objectives —.** Housekeeping only.

---

## #424 · run · stage B · plan §4.2
`ba4501046e5d4eb6` ← `43be8cb78de3cc92` · recorded 2026-10-21T01:29:05+00:00

**What.** Stage B1 run started: seeds [30, 31, 32, 33, 34], arms ['main', 'shuffled_rung2']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  30,
  31,
  32,
  33,
  34
 ]
}
```

**Artifacts.** `configs/stage_b1_eqrho_mlp_predict.yaml` (sha256 ed2af0d144)

---

## #425 · run · stage B · plan §4.2
`2d10c67e5d28643b` ← `ba4501046e5d4eb6` · recorded 2026-10-21T01:29:05+00:00

**What.** Stage B1 run started: seeds [30, 31, 32, 33, 34], arms ['main']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  30,
  31,
  32,
  33,
  34
 ]
}
```

**Artifacts.** `configs/stage_b1_mlp.yaml` (sha256 2ef82b4ccc)

---

## #426 · run · stage B · plan §4.2
`d835dbdb943a0af9` ← `2d10c67e5d28643b` · recorded 2026-10-21T01:29:05+00:00

**What.** Stage B1 run started: seeds [30, 31, 32, 33, 34], arms ['main']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  30,
  31,
  32,
  33,
  34
 ]
}
```

**Artifacts.** `configs/stage_b1_eqrho_mirror_lejepa.yaml` (sha256 c47f81349d)

---

## #427 · run · stage B · plan §4.2
`3a3ecc1fc90fd486` ← `d835dbdb943a0af9` · recorded 2026-10-21T01:29:05+00:00

**What.** Stage B1 run started: seeds [30, 31, 32, 33, 34], arms ['main']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  30,
  31,
  32,
  33,
  34
 ]
}
```

**Artifacts.** `configs/stage_b1_eqrho_mlp_lejepa.yaml` (sha256 69e5527e20)

---

## #428 · run · stage B · plan §4.2
`8a51eec92f14c050` ← `3a3ecc1fc90fd486` · recorded 2026-10-21T01:29:39+00:00

**What.** Stage B1 arm=main seed=30 finished

**Output.**
```json
{
 "core_invariant_r2": 0.965,
 "rung_angles_deg": [
  74.0,
  68.33
 ],
 "seconds": 33.8,
 "variant_r2": [
  -0.001,
  0.535
 ]
}
```

**Artifacts.** `results/stage_b1_e25/main_seed30.json` (sha256 fc51c73f5d)

---

## #429 · run · stage B · plan §4.2
`706790ff4a8d81c0` ← `8a51eec92f14c050` · recorded 2026-10-21T01:29:39+00:00

**What.** Stage B1 arm=main seed=30 finished

**Output.**
```json
{
 "core_invariant_r2": 0.987,
 "rung_angles_deg": [
  0.31,
  0.98
 ],
 "seconds": 34.1,
 "variant_r2": [
  0.987,
  0.986
 ]
}
```

**Artifacts.** `results/stage_b1_e26/main_seed30.json` (sha256 dbed4c4ad0)

---

## #430 · run · stage B · plan §4.2
`f6668eba41b38e1c` ← `706790ff4a8d81c0` · recorded 2026-10-21T01:30:10+00:00

**What.** Stage B1 arm=main seed=31 finished

**Output.**
```json
{
 "core_invariant_r2": 0.983,
 "rung_angles_deg": [
  84.65,
  86.65
 ],
 "seconds": 31.2,
 "variant_r2": [
  -0.0,
  0.716
 ]
}
```

**Artifacts.** `results/stage_b1_e25/main_seed31.json` (sha256 c8cd75e051)

---

## #431 · run · stage B · plan §4.2
`2055b5e100b24ba7` ← `f6668eba41b38e1c` · recorded 2026-10-21T01:30:11+00:00

**What.** Stage B1 arm=main seed=31 finished

**Output.**
```json
{
 "core_invariant_r2": 0.986,
 "rung_angles_deg": [
  0.26,
  1.09
 ],
 "seconds": 31.8,
 "variant_r2": [
  0.986,
  0.985
 ]
}
```

**Artifacts.** `results/stage_b1_e26/main_seed31.json` (sha256 a11cbc6376)

---

## #432 · run · stage B · plan §4.2
`2e4ca729dbb71ac8` ← `2055b5e100b24ba7` · recorded 2026-10-21T01:30:42+00:00

**What.** Stage B1 arm=main seed=32 finished

**Output.**
```json
{
 "core_invariant_r2": 0.987,
 "rung_angles_deg": [
  0.27,
  0.89
 ],
 "seconds": 31.2,
 "variant_r2": [
  0.988,
  0.987
 ]
}
```

**Artifacts.** `results/stage_b1_e26/main_seed32.json` (sha256 51311cbbb2)

---

## #433 · run · stage B · plan §4.2
`ff812515b2fbe9cc` ← `2e4ca729dbb71ac8` · recorded 2026-10-21T01:30:43+00:00

**What.** Stage B1 arm=main seed=32 finished

**Output.**
```json
{
 "core_invariant_r2": 0.909,
 "rung_angles_deg": [
  89.42,
  86.9
 ],
 "seconds": 32.9,
 "variant_r2": [
  -0.001,
  0.451
 ]
}
```

**Artifacts.** `results/stage_b1_e25/main_seed32.json` (sha256 aa74f07159)

---

## #434 · run · stage B · plan §4.2
`0fe2fb2d73942dec` ← `ff812515b2fbe9cc` · recorded 2026-10-21T01:31:13+00:00

**What.** Stage B1 arm=main seed=33 finished

**Output.**
```json
{
 "core_invariant_r2": 0.987,
 "rung_angles_deg": [
  0.3,
  1.04
 ],
 "seconds": 31.1,
 "variant_r2": [
  0.987,
  0.988
 ]
}
```

**Artifacts.** `results/stage_b1_e26/main_seed33.json` (sha256 e456e13e86)

---

## #435 · run · stage B · plan §4.2
`1dfcbe82d21d3cfd` ← `0fe2fb2d73942dec` · recorded 2026-10-21T01:31:13+00:00

**What.** Stage B1 arm=main seed=33 finished

**Output.**
```json
{
 "core_invariant_r2": 0.957,
 "rung_angles_deg": [
  88.46,
  88.82
 ],
 "seconds": 30.6,
 "variant_r2": [
  -0.001,
  0.476
 ]
}
```

**Artifacts.** `results/stage_b1_e25/main_seed33.json` (sha256 f85991a099)

---

## #436 · run · stage B · plan §4.2
`58a640a4a254b671` ← `1dfcbe82d21d3cfd` · recorded 2026-10-21T01:31:45+00:00

**What.** Stage B1 arm=main seed=34 finished

**Output.**
```json
{
 "core_invariant_r2": 0.984,
 "rung_angles_deg": [
  0.66,
  0.94
 ],
 "seconds": 31.6,
 "variant_r2": [
  0.982,
  0.983
 ]
}
```

**Artifacts.** `results/stage_b1_e26/main_seed34.json` (sha256 a86a7b197b)

---

## #437 · run · stage B · plan §4.2
`33e40a74554adb8d` ← `58a640a4a254b671` · recorded 2026-10-21T01:31:46+00:00

**What.** Stage B1 arm=main seed=34 finished

**Output.**
```json
{
 "core_invariant_r2": 0.959,
 "rung_angles_deg": [
  73.91,
  74.71
 ],
 "seconds": 32.1,
 "variant_r2": [
  -0.0,
  0.349
 ]
}
```

**Artifacts.** `results/stage_b1_e25/main_seed34.json` (sha256 7346fd96b1)

---

## #438 · run · stage B · plan §4.2
`606330ed02b4e3d3` ← `33e40a74554adb8d` · recorded 2026-10-21T01:32:05+00:00

**What.** Stage B1 run started: seeds [30, 31, 32, 33, 34], arms ['main']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  30,
  31,
  32,
  33,
  34
 ]
}
```

**Artifacts.** `configs/stage_b1_eqrho_mirror_predict.yaml` (sha256 2dc78a0fce)

---

## #439 · run · stage B · plan §4.2
`52a9b43ccbf548df` ← `606330ed02b4e3d3` · recorded 2026-10-21T01:32:16+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=30 finished

**Output.**
```json
{
 "core_invariant_r2": 0.493,
 "rung_angles_deg": [
  0.42,
  76.9
 ],
 "seconds": 31.0,
 "variant_r2": [
  0.987,
  0.483
 ]
}
```

**Artifacts.** `results/stage_b1_e26/shuffled_rung2_seed30.json` (sha256 f583fca347)

---

## #440 · run · stage B · plan §4.2
`d95fd14377ce7068` ← `52a9b43ccbf548df` · recorded 2026-10-21T01:32:34+00:00

**What.** Stage B1 arm=main seed=30 finished

**Output.**
```json
{
 "core_invariant_r2": 0.997,
 "rung_angles_deg": [
  0.16,
  1.0
 ],
 "seconds": 29.3,
 "variant_r2": [
  0.996,
  0.997
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mirror_predict/main_seed30.json` (sha256 2df0b909ee)

---

## #441 · run · stage B · plan §4.2
`1b5a5b8593491c1e` ← `d95fd14377ce7068` · recorded 2026-10-21T01:32:41+00:00

**What.** Stage B1 arm=main seed=30 finished

**Output.**
```json
{
 "core_invariant_r2": 1.0,
 "rung_angles_deg": [
  0.01,
  0.92
 ],
 "seconds": 216.2,
 "variant_r2": [
  1.0,
  1.0
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mirror_lejepa/main_seed30.json` (sha256 1fff61923d)

---

## #442 · run · stage B · plan §4.2
`7902114f3682f40b` ← `1b5a5b8593491c1e` · recorded 2026-10-21T01:32:46+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=31 finished

**Output.**
```json
{
 "core_invariant_r2": 0.379,
 "rung_angles_deg": [
  0.3,
  81.63
 ],
 "seconds": 30.0,
 "variant_r2": [
  0.987,
  0.378
 ]
}
```

**Artifacts.** `results/stage_b1_e26/shuffled_rung2_seed31.json` (sha256 d4c7d73847)

---

## #443 · run · stage B · plan §4.2
`81dd21d98084a84d` ← `7902114f3682f40b` · recorded 2026-10-21T01:32:58+00:00

**What.** Stage B1 arm=main seed=30 finished

**Output.**
```json
{
 "core_invariant_r2": -0.0,
 "rung_angles_deg": [
  62.52,
  82.9
 ],
 "seconds": 232.5,
 "variant_r2": [
  -0.002,
  0.0
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mlp_lejepa/main_seed30.json` (sha256 60d9fe784b)

---

## #444 · run · stage B · plan §4.2
`47f0d4b1b6aa3b7a` ← `81dd21d98084a84d` · recorded 2026-10-21T01:33:03+00:00

**What.** Stage B1 arm=main seed=31 finished

**Output.**
```json
{
 "core_invariant_r2": 0.995,
 "rung_angles_deg": [
  0.22,
  0.93
 ],
 "seconds": 28.9,
 "variant_r2": [
  0.996,
  0.993
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mirror_predict/main_seed31.json` (sha256 c721648537)

---

## #445 · run · stage B · plan §4.2
`f37537c26d225fd2` ← `47f0d4b1b6aa3b7a` · recorded 2026-10-21T01:33:16+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=32 finished

**Output.**
```json
{
 "core_invariant_r2": 0.502,
 "rung_angles_deg": [
  0.31,
  80.01
 ],
 "seconds": 30.4,
 "variant_r2": [
  0.988,
  0.514
 ]
}
```

**Artifacts.** `results/stage_b1_e26/shuffled_rung2_seed32.json` (sha256 75085282a1)

---

## #446 · run · stage B · plan §4.2
`684fc7b4e8c00c8c` ← `f37537c26d225fd2` · recorded 2026-10-21T01:33:32+00:00

**What.** Stage B1 arm=main seed=32 finished

**Output.**
```json
{
 "core_invariant_r2": 0.994,
 "rung_angles_deg": [
  0.35,
  0.99
 ],
 "seconds": 28.9,
 "variant_r2": [
  0.994,
  0.994
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mirror_predict/main_seed32.json` (sha256 f979cbc743)

---

## #447 · run · stage B · plan §4.2
`c43f61df36b058aa` ← `684fc7b4e8c00c8c` · recorded 2026-10-21T01:33:46+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=33 finished

**Output.**
```json
{
 "core_invariant_r2": 0.553,
 "rung_angles_deg": [
  0.41,
  78.17
 ],
 "seconds": 29.8,
 "variant_r2": [
  0.987,
  0.561
 ]
}
```

**Artifacts.** `results/stage_b1_e26/shuffled_rung2_seed33.json` (sha256 f67680bd3f)

---

## #448 · run · stage B · plan §4.2
`3164077c066abf31` ← `c43f61df36b058aa` · recorded 2026-10-21T01:34:01+00:00

**What.** Stage B1 arm=main seed=33 finished

**Output.**
```json
{
 "core_invariant_r2": 0.995,
 "rung_angles_deg": [
  0.14,
  1.03
 ],
 "seconds": 28.6,
 "variant_r2": [
  0.995,
  0.995
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mirror_predict/main_seed33.json` (sha256 68e255aa99)

---

## #449 · run · stage B · plan §4.2
`be7462c302ba70ca` ← `3164077c066abf31` · recorded 2026-10-21T01:34:16+00:00

**What.** Stage B1 arm=shuffled_rung2 seed=34 finished

**Output.**
```json
{
 "core_invariant_r2": 0.414,
 "rung_angles_deg": [
  0.74,
  88.09
 ],
 "seconds": 30.2,
 "variant_r2": [
  0.982,
  0.415
 ]
}
```

**Artifacts.** `results/stage_b1_e26/shuffled_rung2_seed34.json` (sha256 0927a07bfb)

---

## #450 · run · stage B · plan §4.2
`566c855d803beffb` ← `be7462c302ba70ca` · recorded 2026-10-21T01:34:29+00:00

**What.** Stage B1 arm=main seed=34 finished

**Output.**
```json
{
 "core_invariant_r2": 0.996,
 "rung_angles_deg": [
  0.18,
  0.84
 ],
 "seconds": 28.4,
 "variant_r2": [
  0.996,
  0.996
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mirror_predict/main_seed34.json` (sha256 6cd2b6e555)

---

## #451 · run · stage B · plan §4.2
`80a5c03e28ba5389` ← `566c855d803beffb` · recorded 2026-10-21T01:35:14+00:00

**What.** Stage B1 run started: seeds [34, 33, 32], arms ['main']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  34,
  33,
  32
 ]
}
```

**Artifacts.** `configs/stage_b1_eqrho_mirror_lejepa.yaml` (sha256 c47f81349d)

---

## #452 · run · stage B · plan §4.2
`3d5a3f1170692fa7` ← `80a5c03e28ba5389` · recorded 2026-10-21T01:35:15+00:00

**What.** Stage B1 run started: seeds [34, 33, 32], arms ['main']

**Output.**
```json
{
 "criteria_sha256": "5d924c59ef363fc8420eec3f2d27412d12f3156c206e1cd464bfab61d8631403",
 "label": "ground-truth pairs",
 "seeds": [
  34,
  33,
  32
 ]
}
```

**Artifacts.** `configs/stage_b1_eqrho_mlp_lejepa.yaml` (sha256 69e5527e20)

---

## #453 · run · stage B · plan §4.2
`732fdcb747e0152c` ← `3d5a3f1170692fa7` · recorded 2026-10-21T01:36:07+00:00

**What.** Stage B1 arm=main seed=31 finished

**Output.**
```json
{
 "core_invariant_r2": 0.999,
 "rung_angles_deg": [
  0.06,
  0.89
 ],
 "seconds": 205.5,
 "variant_r2": [
  0.999,
  0.999
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mirror_lejepa/main_seed31.json` (sha256 12a672f4b9)

---

## #454 · run · stage B · plan §4.2
`e2d34150efc69bca` ← `732fdcb747e0152c` · recorded 2026-10-21T01:36:38+00:00

**What.** Stage B1 arm=main seed=31 finished

**Output.**
```json
{
 "core_invariant_r2": 0.0,
 "rung_angles_deg": [
  82.86,
  85.16
 ],
 "seconds": 220.1,
 "variant_r2": [
  -0.0,
  -0.0
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mlp_lejepa/main_seed31.json` (sha256 d982567cea)

---

## #455 · run · stage B · plan §4.2
`06940365cf3e3a78` ← `e2d34150efc69bca` · recorded 2026-10-21T01:38:59+00:00

**What.** Stage B1 arm=main seed=34 finished

**Output.**
```json
{
 "core_invariant_r2": 1.0,
 "rung_angles_deg": [
  0.01,
  0.8
 ],
 "seconds": 224.5,
 "variant_r2": [
  1.0,
  1.0
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mirror_lejepa/main_seed34.json` (sha256 d7e4753b35)

---

## #456 · run · stage B · plan §4.2
`66214ad27b5674e9` ← `06940365cf3e3a78` · recorded 2026-10-21T01:39:16+00:00

**What.** Stage B1 arm=main seed=34 finished

**Output.**
```json
{
 "core_invariant_r2": -0.0,
 "rung_angles_deg": [
  54.71,
  89.51
 ],
 "seconds": 241.8,
 "variant_r2": [
  0.0,
  -0.001
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mlp_lejepa/main_seed34.json` (sha256 7b71e6db75)

---

## #457 · run · stage B · plan §4.2
`aea9eb573159c09d` ← `66214ad27b5674e9` · recorded 2026-10-21T01:39:40+00:00

**What.** Stage B1 arm=main seed=32 finished

**Output.**
```json
{
 "core_invariant_r2": 0.998,
 "rung_angles_deg": [
  0.11,
  0.9
 ],
 "seconds": 213.4,
 "variant_r2": [
  0.999,
  0.997
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mirror_lejepa/main_seed32.json` (sha256 0583846332)

---

## #458 · run · stage B · plan §4.2
`f037d56c6c8cceec` ← `aea9eb573159c09d` · recorded 2026-10-21T01:40:25+00:00

**What.** Stage B1 arm=main seed=32 finished

**Output.**
```json
{
 "core_invariant_r2": -0.0,
 "rung_angles_deg": [
  75.26,
  81.92
 ],
 "seconds": 227.7,
 "variant_r2": [
  -0.002,
  -0.0
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mlp_lejepa/main_seed32.json` (sha256 2cc8503fef)

---

## #459 · run · stage B · plan §4.2
`f773cfdd3a27c1b5` ← `f037d56c6c8cceec` · recorded 2026-10-21T01:42:39+00:00

**What.** Stage B1 arm=main seed=33 finished

**Output.**
```json
{
 "core_invariant_r2": 0.999,
 "rung_angles_deg": [
  0.11,
  1.08
 ],
 "seconds": 219.9,
 "variant_r2": [
  0.999,
  0.997
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mirror_lejepa/main_seed33.json` (sha256 ec1051526b)

---

## #460 · run · stage B · plan §4.2
`d9c5522e1aaf3ef7` ← `f773cfdd3a27c1b5` · recorded 2026-10-21T01:43:05+00:00

**What.** Stage B1 arm=main seed=33 finished

**Output.**
```json
{
 "core_invariant_r2": 0.001,
 "rung_angles_deg": [
  72.54,
  88.62
 ],
 "seconds": 228.9,
 "variant_r2": [
  0.0,
  -0.001
 ]
}
```

**Artifacts.** `results/stage_b1_e27/mlp_lejepa/main_seed33.json` (sha256 4f559a5e36)

---

## #461 · result · stage B · plan §E25-E28
`706d3d7c91e9f745` ← `d9c5522e1aaf3ef7` · recorded 2026-10-21T01:44:26+00:00

**What.** E25 CONFIRMED (the prediction-trained MLP drops the fast block at the original speeds: texture presence -0.012, 5/5 seeds; identity partial 0.744; category 0.993). E26 CONFIRMED (equal speeds, same MLP and recipe: all blocks present 0.991, both rungs SPLIT on 5/5 seeds, every B1 criterion 5/5). E27 CONFIRMED as registered but vacuous in one cell: mirror+paper, mirror+prediction and MLP+prediction all present and SPLIT 5/5; MLP+paper objective collapsed to a constant (min std 1e-5) because the regulariser weight 1e-6 was copied from the mirror setup, so that cell is uninformative. E28 registered to repair that cell with a regulariser weight chosen by a training-health rule on a pilot seed.

**How.** experiments/analyse_layered.py on results/stage_b1_e25, e26, e27/*; E28 registered in docs/EVIDENCE.md before its pilot

**Output.**
```json
{
 "E25": "confirmed",
 "E26": "confirmed",
 "E27": "confirmed as registered, vacuous in the MLP+paper cell (collapse)",
 "presence_E26": 0.991,
 "texture_presence_E25": -0.012
}
```

**Artifacts.** `results/enc_generality/REPORT.md` (sha256 17b52e111a)

**Bearing on objectives O2.** Whether a block can be split is decided first by whether the encoder kept it. With the content present, the split worked in every encoder and objective cell that did not collapse. The earlier E23 failure was the prediction-trained encoder discarding the fast block.

**Verdict.** confirmed

---

## #462 · note · stage B · plan §—
`8d2b64f77374a121` ← `706d3d7c91e9f745` · recorded 2026-10-21T01:44:45+00:00

**What.** Housekeeping: entry 422 fingerprinted experiments/analyse_layered.py, which was extended afterwards (E28 section written before the E28 runs); reference declared superseded. No recorded result changed.

**Bearing on objectives —.** Housekeeping only.

---
