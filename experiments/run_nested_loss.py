"""E68 / E71 runner (registered in docs/EVIDENCE.md, 'Owner instruction 2026-11-18').
    PYTHONPATH=src python experiments/run_nested_loss.py e68 --arm A --strength 4 --device cuda [--smoke 300]
    PYTHONPATH=src python experiments/run_nested_loss.py e71 --arm A --strength 0.5 --depth 16 --device cuda
Weight W for the whitening terms: smaller of {1, 10} whose 10,000-step seed-0 pilot has every output-covariance eigenvalue >= 0.5 (E45 rule);
neither healthy -> that world is not run (written to W.json). Arms: A joint, B curriculum (family k on from step 5000(k-1)), U untrained control (E71 only; ladder measure)."""
import argparse, copy, json, os, time
import numpy as np, torch, yaml
from isj.encoder import EncoderConfig, encode, train_encoder
from isj.stage_b1 import run_stage_b1
from isj.worlds import BlockWorld, CouplingMap
ap = argparse.ArgumentParser(); ap.add_argument("exp"); ap.add_argument("--arm", required=True); ap.add_argument("--strength", type=float, required=True)
ap.add_argument("--depth", type=int, default=4); ap.add_argument("--seeds", type=int, nargs="*"); ap.add_argument("--device", default="cpu"); ap.add_argument("--smoke", type=int)
ap.add_argument("--out", default="results/nested"); ap.add_argument("--W", type=float)   # --W fixes the whitening weight (gate runs only); a = ap.parse_args()
cfg0 = yaml.safe_load(open("configs/deep_mlp_d4_fix.yaml"))
K = a.depth; d = 4 * K
rhos = cfg0["world"]["rhos"] if K == 4 else [round(float(1 - x), 4) for x in np.geomspace(0.8, 0.04, K)]   # K > 4: rho_b = 1 - geomspace(0.8, 0.04, K)_b (as in E61)
cfg0["world"].update(block_dims=[4] * K, rhos=rhos, coupling_strength=a.strength, obs_dim=d)
cfg0["split"]["d_ks"] = [4] * (K - 1)
e = cfg0["encoder"]; e.update(slice_measures=True, device=a.device, hidden=16 * K)   # E71 scaling rule: hidden 16K (64 at K = 4)
if a.exp == "e71": e["steps"] = 7500 * K                                                   # E71 scaling rule: steps 7,500 K
seeds = a.seeds or ([250, 251, 252, 253, 254] if a.exp == "e68" else [280, 281, 282, 283, 284])
if a.arm == "B": e["corr_inv_schedule"] = [5000 * (k - 1) for k in range(1, K)]
if a.arm == "U": e.update(corr_inv_weight=0.0, corr_whiten_weight=0.0, lr=0.0, steps=1)   # untrained: the generic MLP at its random start (E69 control; ladder measure only)
folder = f"{a.out}/{a.exp}/{a.arm}/K{K}_s{a.strength:g}" if a.exp == "e71" else f"{a.out}/{a.exp}/{a.arm}/s{a.strength:g}"; os.makedirs(folder, exist_ok=True)
def pilot(W):
    w = cfg0["world"]; world = BlockWorld(list(w["block_dims"]), list(w["rhos"]), seed=0); obs = CouplingMap(world.d, w["coupling_layers"], w["coupling_strength"], w.get("obs_dim"), seed=0)
    ec = EncoderConfig(in_dim=obs.obs_dim, latent_dim=world.d, hidden=e["hidden"], steps=a.smoke or 10000, batch_size=e["batch_size"], lr=e["lr"], reg=e["reg"], var_weight=e["var_weight"], cov_weight=e["cov_weight"],
                       corr_inv_weight=e["corr_inv_weight"], corr_whiten_weight=W, corr_whiten_norm="sum", sigreg_weight=e["sigreg_weight"], arch="mlp", objective="predict", device=a.device,
                       corr_inv_schedule=tuple(e["corr_inv_schedule"]) if e.get("corr_inv_schedule") else None)
    enc, _ = train_encoder(world, obs, ec, 77_777); h = encode(enc, obs, world.sample(20000)); return float(torch.linalg.eigvalsh(torch.cov(h.T).double()).min())
wpath = f"{folder}/W.json"
if a.arm == "U": W = 0.0
elif a.W is not None: W = a.W
elif a.smoke: W = 1   # smoke runs test the code path only; no pilot
elif os.path.exists(wpath): W = json.load(open(wpath))["W"]
else:
    W, eigs = None, {}
    for cand in (1, 10):
        eigs[cand] = pilot(cand); print("pilot W", cand, "min eig", round(eigs[cand], 3), flush=True)
        if eigs[cand] >= 0.5: W = cand; break
    json.dump({"W": W, "pilot_min_eig": eigs}, open(wpath, "w"))
if W is None: print("no healthy weight: world not run"); raise SystemExit
e["corr_whiten_weight"] = W
if a.smoke: e["steps"] = a.smoke; cfg0["significance"]["n_perm"] = 20
for s in seeds:
    path = f"{folder}/main_seed{s}.json"
    if os.path.exists(path) and not a.smoke: continue
    t0 = time.time(); r = run_stage_b1(copy.deepcopy(cfg0), s); r["W"] = W; r["arm"] = a.arm; r["device"] = a.device
    if a.smoke: print("SMOKE", s, round(time.time() - t0), "s", [round(g["angle_deg"], 1) for g in r["rungs"]], r["slice"]["presence"] if r["slice"] else None); break
    json.dump(r, open(path, "w"), indent=1); print(a.arm, a.strength, s, round(time.time() - t0), "s", "presence", [round(x, 2) for x in (r["slice"] or {}).get("presence", [])], flush=True)
