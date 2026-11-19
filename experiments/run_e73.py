"""E73 runner (registered in docs/EVIDENCE.md, 'E73 registration'): speed read-back from the eigen-split blocks in the original small world.
    PYTHONPATH=src python experiments/run_e73.py --recipe P --strength 0.5 --seeds 310 311 [--smoke 300]
Recipe P = configs/stage_b1.yaml (the E21 recipe: mirror encoder, alignment + SIGReg); recipe Q = configs/minimal_c4_baseline.yaml (generic MLP, predictive loss). Nothing else is changed."""
import argparse, copy, json, os, time
import torch, yaml
torch.set_num_threads(1)
from isj.stage_b1 import run_stage_b1
ap = argparse.ArgumentParser(); ap.add_argument("--recipe", required=True, choices=["P", "Q"]); ap.add_argument("--strength", type=float, required=True)
ap.add_argument("--seeds", type=int, nargs="*", default=[310, 311, 312, 313, 314]); ap.add_argument("--smoke", type=int); ap.add_argument("--out", default="results/e73"); a = ap.parse_args()
cfg = yaml.safe_load(open({"P": "configs/stage_b1.yaml", "Q": "configs/minimal_c4_baseline.yaml"}[a.recipe]))
cfg["world"]["coupling_strength"] = a.strength; cfg["encoder"]["rate_readout"] = 50000
if a.smoke: cfg["encoder"]["steps"] = a.smoke
folder = f"{a.out}/{a.recipe}_s{a.strength:g}"; os.makedirs(folder, exist_ok=True)
for s in a.seeds:
    path = f"{folder}/main_seed{s}.json"
    if os.path.exists(path) and not a.smoke: continue
    t0 = time.time(); r = run_stage_b1(copy.deepcopy(cfg), s); r["recipe"] = a.recipe; r["strength"] = a.strength
    if a.smoke: print("SMOKE", s, round(time.time() - t0), "s", "angles", [round(g["angle_deg"], 1) for g in r["rungs"]], "block_rho_hat", [round(x, 3) for x in r["block_rho_hat"]]); break
    json.dump(r, open(path, "w"), indent=1); print(a.recipe, a.strength, s, round(time.time() - t0), "s", "angles", [round(g["angle_deg"], 1) for g in r["rungs"]], "block_rho_hat", [round(x, 3) for x in r["block_rho_hat"]], flush=True)
