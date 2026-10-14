"""Re-explain the 14 earlier log entries in plain language (one-off; entries are appended, never edited).

Numbers are computed from the saved run files, and reported under the paper's metric names.
"""
import glob
import json
import statistics as st

from isj import explog as L


def load(d, arm):
    return [json.load(open(f)) for f in sorted(glob.glob(f"runs/stage_a/{d}/{arm}_seed*.json"))]


def ms(rs, f, nd=3):
    v = [f(r) for r in rs]
    return f"{st.mean(v):.{nd}f} ± {st.stdev(v):.{nd}f}" if len(v) > 1 else f"{v[0]:.{nd}f}"


main, lej = load("r1", "main"), load("r1", "no_inv")
shuf, nopred, novar = load("r1", "shuffled"), load("r1", "no_pred"), load("r1", "no_var")


def P(did, output, relevance, verdict="info", stage="A"):
    return {"did": did, "output": output, "relevance": relevance, "verdict": verdict, "stage": stage}


rows = [
 (P("Read your plan, the monograph, the two ladder notes, the paper and the authors' code. Wrote down, and locked, what counts as success before running anything.",
    ["Nothing run yet.",
     "What the paper does: one split of a small synthetic world (8 hidden numbers: 4 invariant + 4 variant), plus robot images (800 trajectories = 100 groups of 8).",
     "The paper never splits twice. Splitting the invariant block again is our addition."],
    "Locking the pass numbers first means results can't be judged against moved goalposts. It also shows which part of the project is new and still untested."),
  "Reading and rules", [0, 1], "info", "-"),
 (P("Tested the splitting maths alone (no neural network) on a 5-level synthetic world, splitting four times in a row.",
    ["9 of 9 checks pass.",
     "Each of the 4 splits finds its block to within 0.5 degrees.",
     "Shuffled matched pairs destroy the split, as the theory says.",
     "A split given too little variation fails, and only that split (the next one is slightly affected).",
     "Error shrinks with more data at the expected rate."],
    "Shows the maths behind 'split the invariant block again' works under ideal conditions. It does not yet show it works with a trained encoder; that is Stage A.",
    "pass"), "Maths-only core test", [2], "pass", "core"),
 (P("Wrote the Stage A pipeline: make the synthetic world, train an encoder, ZCA-whiten, fit the spectral head on 30,000 matched pairs, and score with the paper's metrics. Locked the pass numbers in a config file.",
    ["Code and config written; the pass numbers are fingerprinted so the runner refuses to start if they are edited.",
     "Pass means: invariant R² above 0.9, angle below 5 degrees, gap ratio above 10, no leakage."],
    "This is the paper's single split rebuilt in our own code, which is the base Stage B (the second split) builds on."),
  "Stage A built", [3], "info", "A"),
 (P("First Stage A run (seed 0), with the settings exactly as the plan wrote them.",
    ["invariant_r2 0.43 (needs above 0.9)", "variant_r2 0.43", "angle 83 degrees (needs below 5)", "gap ratio 1.2 (needs above 10)", "Failed."],
    "At this point we could not claim the paper's single split works in our setup. This used 1 of the 3 debugging rounds the plan allows.",
    "fail"), "First run: failed", [4], "fail", "A"),
 (P("Tried four changes to how the encoder is trained, on the same seed, to see what the failure needed.",
    ["Adding a covariance penalty on the encoder output (keeping stop-gradient): invariant_r2 0.43 -> 0.99. Works.",
     "The other three variants stayed at invariant_r2 0.00-0.24, no better than the first run.",
     "Why the penalty helps was not measured; it is a guess."],
    "Found the training recipe Stage A needs. This is an encoder-training fix, not a change to what counts as success."),
  "Diagnosing the failure", [5, 13], "info", "A"),
 (P("Applied that fix to the config. Checked the locked pass numbers had not changed.",
    ["Encoder now trains with a covariance penalty (weight 0.04) and stop-gradient.", "Fingerprint of the pass numbers: identical before and after."],
    "Keeps the process honest: we changed how the encoder is trained, not how we judge it."),
  "Fix applied, rules unchanged", [6], "info", "A"),
 (P("Ran the main Stage A experiment: 5 random seeds, full pipeline, scored with the paper's metrics.",
    [f"invariant_r2 {ms(main, lambda r: r['invariant_r2'])}  (paper about 0.998)",
     f"variant_r2 {ms(main, lambda r: r['variant_r2'])}  (paper about 0.997)",
     f"global_r2 {ms(main, lambda r: r['global_r2'])}  (paper about 0.998)",
     f"a12_fro {ms(main, lambda r: r['leak_norms']['inv_from_var_fro'], 4)}  (paper 0.003)",
     f"a21_fro {ms(main, lambda r: r['leak_norms']['var_from_inv_fro'], 4)}  (paper 0.024)",
     f"block_purity {ms(main, lambda r: r['leak_norms']['block_purity'], 5)}  (paper about 0.99993)",
     f"Also: angle {ms(main, lambda r: r['angle_inv_deg'], 2)} degrees, gap ratio {ms(main, lambda r: r['gap_ratio'], 0)}.",
     "All pass thresholds met on every seed."],
    "Stage A passes: a trained encoder plus one spectral-head split separates invariant from variant about as cleanly as the paper reports. Slightly lower on the R² scores (0.989 vs 0.998), very close on the cross-block leakage (a12, a21) and block purity. This clears the way for Stage B.",
    "pass"), "Main result: Stage A passes", [7, 8], "pass", "A"),
 (P("Ran the runs that should fail, to make sure the pass means something.",
    [f"Shuffled matched pairs: gap ratio {min(r['gap_ratio'] for r in shuf):.2f}-{max(r['gap_ratio'] for r in shuf):.2f} (vs about 94 for the real run). Split destroyed.",
     f"No spectral head (the paper's LeJEPA baseline): invariant_r2 {ms(lej, lambda r: r['invariant_r2'])}, block_purity {ms(lej, lambda r: r['block_purity'] if 'block_purity' in r else r['leak_norms']['block_purity'])}, global_r2 unchanged ({ms(lej, lambda r: r['global_r2'])}).",
     "Paper's LeJEPA gets about 0.96 block R² here, much higher than our 0.49. Likely cause: their encoder is built to mirror the scrambling function. Not tested.",
     f"No prediction: invariant_r2 {min(r['invariant_r2'] for r in nopred):.2f}-{max(r['invariant_r2'] for r in nopred):.2f}.",
     f"No variance regularizer / no ZCA: invariant_r2 {min(r['invariant_r2'] for r in novar):.2f}-{max(r['invariant_r2'] for r in novar):.2f}."],
    "Each ingredient (prediction, matched pairs, whitening) is needed. Our result isn't an accident of the setup. The global_r2 staying the same without the spectral head matches the paper: the head separates the blocks, it does not change how much the representation holds.",
    "pass"), "Controls: they fail as they should", [9], "pass", "A"),
 (P("Changed one control check after seeing the results, and recorded that I did.",
    ["My own extra rule for the shuffled-pairs control (invariant_r2 below 0.5) was wrong: picking 4 of 8 directions at random already explains about half the variance.",
     "New rule: recovered angle above 45 degrees. Observed 73-88.",
     "The pass numbers for the main result were not touched."],
    "Disclosed because it was decided after seeing data. It only affects a control, not the Stage A verdict."),
  "Control rule corrected (disclosed)", [10], "info", "A"),
 (P("Re-ran the main arm with a harder (more strongly scrambled) world: coupling strength 1.0 and 2.0, 3 seeds each.",
    ["Strength 0.5 (main run): passes 5 of 5.",
     "Strength 1.0: invariant_r2 0.96, 0.79, 0.96. Two of three pass.",
     "Strength 2.0: invariant_r2 0.72, 0.50, 0.58. None pass.",
     "Paper also reports global_r2 falling as coupling grows (0.998 down to 0.877)."],
    "Shows where this recipe starts to break. Stage B should start at strength 0.5, where Stage A is solid."),
  "Harder worlds", [11], "info", "A"),
 (P("Have NOT run the authors' own simulation script.",
    ["My attempt was blocked by the safety check because the code came from the internet.",
     "I read all of it (about 270 lines); it only does math on the CPU."],
    "The plan wants this as the first direct comparison with the paper. It would tell us if the small gap in R² (0.989 vs 0.998) comes from our setup. Waiting on your yes.",
    "blocked"), "Paper's own simulation: waiting for you", [12], "blocked", "A"),
]

for plain, title, restates, verdict, stage in rows:
    plain["title"] = title
    L.append("note", f"Plain-language restatement: {title}", stage=stage, objectives=["OP"],
             plain=plain, restates=restates, retroactive=True,
             interpretation="Restates earlier chain entries in plain language; figures recomputed from run files.")
print(len(L.read_all()), "entries;", L.verify()[1])
