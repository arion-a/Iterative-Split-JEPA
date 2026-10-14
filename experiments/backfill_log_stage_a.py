"""One-off: record, as clearly-flagged retroactive entries, what happened before the log existed.

Run once on an empty chain. Everything here comes from the session transcript, git history, and the
immutable run artifacts under runs/stage_a/.
"""
import glob
import json
import os

from isj import explog as L

R = dict(retroactive=True)
r1 = sorted(glob.glob("runs/stage_a/r1/*_seed*.json"))

L.append("genesis",
         "Start of the experiment log. Plan version: revised Experimental Plan + revised Monograph (Oct 2026). "
         "Both revisions fixed the points I had raised: sufficiency tolerance 5%, five per-rung checks, "
         "descending eigenvalue order, rung-2 cluster purity measured separately.",
         stage="-", step="all", objectives=["OP"],
         how="Read all four documents (plan, monograph, ladder bridge note, proof document) and the authors' repo.",
         interpretation="Fixes the rules before any result exists. Everything before this entry is not in the chain; "
                        "entries marked retroactive were written afterwards from git history and saved run files.",
         event_ref="repo initial commit 97b639a", **R)

L.append("plan",
         "Understood the authors' paper and code: they test ONE split (fast vs slow hidden numbers) on a tiny "
         "synthetic world, then on robot pictures. They do not repeat the split; the ladder is our contribution.",
         stage="A", step="3", objectives=["O1"],
         how="Read arXiv 2610.12349 and cloned splitjepa.github.io (read only). Their simulation trains an 8-number "
             "network built as the exact mirror of the scrambling function, then does one eigen-split.",
         outputs={"their_data": "generated on the fly, no dataset; 8 hidden numbers (4+4); 30,000 pairs for the split",
                  "their_robot_data": "800 successful ManiSkill trajectories per task, 128x128 images",
                  "their_headline": "slow/fast block R2 about 0.998 / 0.997"},
         interpretation="Gives Stage A its comparison target. Our plan uses a generic network on 16 observed numbers "
                        "(a deliberately different, harder setup), so any gap to their numbers must be explained.",
         **R)

L.append("implementation",
         "Built the 'ideal-formula' core test: a 5-level world where we skip the neural network and test the split "
         "mathematics alone, then repeat the split four times in a row.",
         stage="core", step="3", objectives=["O0"],
         how="src/isj/worlds.py (world and matched pairs), src/isj/engine.py (the split and the ladder), "
             "tests/test_core_linear.py.",
         outputs={"tests_passed": "9 of 9",
                  "what_they_check": ["each of 4 rungs recovers its block within 0.5 degrees",
                                      "shuffling the pairs removes the split (gap ratio ~1)",
                                      "a rung given only one direction of variation fails, and only that rung "
                                      "(plus slight contamination of the next)",
                                      "error shrinks like 1/sqrt(data) when noise is added"]},
         interpretation="Reproduces the plan's 'validated core' independently in new code (objective O0). "
                        "This is the maths being right; it says nothing yet about trained networks (that is Stage A).",
         verdict="PASS", event_ref="commit e633b34", event_time="2026-10-12T16:24:53+00:00", **R)

L.append("implementation",
         "Built Stage A: the full pipeline with a trained, frozen network, plus a locked configuration.",
         stage="A", step="4.1", objectives=["O1", "OP"],
         how="src/isj/encoder.py (network + training), src/isj/stage_a.py (pipeline), src/isj/audits.py (measurements), "
             "configs/stage_a.yaml (settings and success thresholds), experiments/run_stage_a.py (runner that refuses "
             "to start if the thresholds were edited).",
         outputs={"locked_thresholds_sha256": open("configs/stage_a.criteria.sha256").read().strip()},
         artifact_paths=["configs/stage_a.yaml"],
         interpretation="Success thresholds from plan 4.1 are locked so results cannot be judged against moved goalposts (OP).",
         event_ref="commit e633b34", event_time="2026-10-12T16:24:53+00:00", **R)

L.append("run",
         "FIRST Stage A run (seed 0) FAILED. The network did not recover the hidden values.",
         stage="A", step="4.1", objectives=["O1"],
         how="Plan settings as written: variance penalty only, weight 0.01. Result printed to console; no file saved.",
         outputs={"slow_block_R2": 0.426, "target": "above 0.9",
                  "angle_degrees": 83.1, "target_angle": "below 5",
                  "gap_ratio": 1.2, "target_gap": "above 10",
                  "note": "numbers transcribed from the console; no artifact exists for this run"},
         interpretation="Pass/fail test of O1 came out FAIL. This was debugging round 1 of the 3 allowed by the plan.",
         verdict="FAIL", **R)

L.append("note",
         "Diagnosed the failure: tried four variants of the training objective on seed 0 (console only).",
         stage="A", step="4.1", objectives=["O1"],
         how="Same world, same seed, changed only the training objective.",
         outputs={"variants": [
             {"change": "no stop-gradient", "slow_R2": 0.146, "angle": 88.7, "gap": 1.44, "verdict": "network collapses"},
             {"change": "add covariance penalty 0.04 (keep stop-gradient)", "slow_R2": 0.989, "angle": 1.2, "gap": 86.7,
              "verdict": "works"},
             {"change": "both changes", "slow_R2": 0.235, "angle": 89.7, "gap": 1.72, "verdict": "collapses"},
             {"change": "authors' SIGReg regulariser, no stop-gradient", "slow_R2": 0.0, "angle": 88.4, "gap": 1.18,
              "verdict": "collapses"}]},
         interpretation="Plain reading: a penalty on variance alone lets the network copy one useful direction into all "
                        "8 outputs; a penalty on correlation between outputs prevents that. This is a training-recipe "
                        "fix, not a change to what counts as success.",
         **R)

L.append("amendment",
         "Changed the TRAINING RECIPE (not the success thresholds): added a correlation penalty (weight 0.04) and a "
         "stop-gradient on the prediction target.",
         stage="A", step="4.1", objectives=["O1", "OP"],
         how="configs/stage_a.yaml: encoder.cov_weight 0 -> 0.04, encoder.stop_grad true.",
         outputs={"locked_thresholds_unchanged": True,
                  "locked_thresholds_sha256": open("configs/stage_a.criteria.sha256").read().strip()},
         interpretation="Keeps the process honest (OP): the thresholds' fingerprint is identical before and after.",
         event_ref="commit 8fe29a5", event_time="2026-10-12T16:30:06+00:00", **R)

L.append("run",
         "Full Stage A run set 'r1': 25 runs = 5 seeds x (main + shuffled-pairs control + 3 ablations).",
         stage="A", step="4.1", objectives=["O1"],
         how="5 seeds ran in parallel; each run saved as one immutable JSON file.",
         outputs={"runs": len(r1)}, artifact_paths=r1,
         interpretation="All the raw evidence for O1 lives in these files; their fingerprints are in this entry.",
         **R)

main = [json.load(open(p)) for p in r1 if os.path.basename(p).startswith("main_")]
L.append("result",
         "Stage A main result: the model cleanly separated the slow hidden numbers from the fast ones, on all 5 seeds.",
         stage="A", step="4.1", objectives=["O1"],
         outputs={"slow_block_R2_range": [round(min(m['invariant_r2'] for m in main), 3), round(max(m['invariant_r2'] for m in main), 3)],
                  "fast_block_R2_range": [round(min(m['variant_r2'] for m in main), 3), round(max(m['variant_r2'] for m in main), 3)],
                  "angle_degrees_range": [round(min(m['angle_inv_deg'] for m in main), 2), round(max(m['angle_inv_deg'] for m in main), 2)],
                  "gap_ratio_range": [round(min(m['gap_ratio'] for m in main), 1), round(max(m['gap_ratio'] for m in main), 1)],
                  "leakage_detected_on_any_seed": any(m['leak_any_significant'] for m in main),
                  "thresholds": "R2>0.9, angle<5, gap>10, no leakage"},
         artifact_paths=["runs/stage_a/r1/report.json"],
         interpretation="O1 is supported: a trained, frozen network plus one spectral split recovers the planted "
                        "2-block structure far inside the plan's thresholds. This is a necessary base for Stage B "
                        "(splitting a second time) but does not itself test the ladder.",
         verdict="PASS", **R)

sh = [json.load(open(p)) for p in r1 if os.path.basename(p).startswith("shuffled_")]
L.append("result",
         "Controls: shuffling the pairs destroyed the split; removing prediction or the pairing step also destroyed it.",
         stage="A", step="4.1", objectives=["O1", "OP"],
         outputs={"shuffled_gap_ratio_range": [round(min(m['gap_ratio'] for m in sh), 2), round(max(m['gap_ratio'] for m in sh), 2)],
                  "shuffled_angle_degrees_range": [round(min(m['angle_inv_deg'] for m in sh), 1), round(max(m['angle_inv_deg'] for m in sh), 1)],
                  "no_prediction_slow_R2_range": "0.22-0.46",
                  "no_pairing_step_slow_R2_range": "0.39-0.61",
                  "no_whitening_slow_R2_range": "0.01-0.14"},
         interpretation="These runs are supposed to fail. They did, so the main-arm success is attributable to the "
                        "pairing information and to prediction, not an accident of the setup.",
         verdict="PASS (controls behave)", **R)

L.append("amendment",
         "Changed one CONTROL check after seeing results: the shuffled-pairs control was first marked failed by my "
         "own extra bound, which was wrong.",
         stage="A", step="2.6", objectives=["OP"],
         how="Old bound: slow-block R2 below 0.5. But picking 4 of 8 directions at random already explains about half "
             "the variance, so shuffled runs legitimately scored 0.31-0.54. New bound: recovered angle above 45 degrees "
             "(observed 73-88). The plan's own expectation (gap flattens) held throughout.",
         outputs={"pass_thresholds_changed": False},
         interpretation="Disclosed because it was decided after seeing data. It affects only a control, not the pass criteria.",
         event_ref="commit 0e0b530", event_time="2026-10-12T16:34:38+00:00", **R)

L.append("result",
         "Scrambling-strength sweep: harder worlds are recovered worse.",
         stage="A", step="4.1", objectives=["O1"],
         outputs={"strength_0.5": "passes, 5/5 seeds",
                  "strength_1.0": {"slow_R2": [0.959, 0.788, 0.961], "gap": [20.2, 1.4, 21.5], "verdict": "2 of 3 pass"},
                  "strength_2.0": {"slow_R2": [0.718, 0.503, 0.580], "gap": [1.3, 1.3, 1.2], "verdict": "0 of 3 pass"}},
         artifact_paths=sorted(glob.glob("runs/stage_a/coupling*/main_seed*.json")),
         interpretation="Shows where this simple recipe starts to fail. It matches the direction the authors report. "
                        "Plan criteria apply at strength 0.5; the sweep maps the limit. Stage B should be run at 0.5 first.",
         **R)

L.append("blocked",
         "Comparison against the authors' own code has NOT been run. The tool permission system blocked executing "
         "code cloned from their repo; I did not work around it.",
         stage="A", step="6", objectives=["O1", "OP"],
         how="Needs your explicit approval to run their simulation/run.py (about 270 lines, read in full) on seeds 0-4.",
         interpretation="Plan section 6 makes this the first decisive comparison. Until done, I cannot say whether the "
                        "difference between our numbers and theirs comes from our generic network or something else.",
         **R)
print("backfilled", len(L.read_all()), "entries")
