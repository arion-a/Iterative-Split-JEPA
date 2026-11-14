"""Exploratory diagnostic (not registered): which block fills the rung-2 pair-difference spectrum.
    python experiments/diag_rung2_split.py CONFIG SEED  -> one JSON line
Retrains the encoder as run_stage_b1 does. For the content rung 2 acted on (H_prev), reports for each block j the moment of the output change
when only block j is resampled (projected into H_prev): trace and top eigenvalues; and rung 2's own pair moment eigenvalues and applied flags."""
import sys, json, yaml, torch
from isj.encoder import EncoderConfig, encode, train_encoder
from isj.engine import fit_ladder, fit_whitener
from isj.worlds import BlockWorld, CouplingMap
cfgp, seed = sys.argv[1], int(sys.argv[2])
cfg = yaml.safe_load(open(cfgp)); w, e, s = cfg["world"], cfg["encoder"], cfg["split"]
world = BlockWorld(list(w["block_dims"]), list(w["rhos"]), seed=seed); d = world.d
observe = CouplingMap(d, w["coupling_layers"], w["coupling_strength"], w.get("obs_dim"), seed=seed)
ec = EncoderConfig(in_dim=observe.obs_dim, latent_dim=d, hidden=e["hidden"], steps=e["steps"], batch_size=e["batch_size"], lr=e["lr"], reg=e["reg"], var_weight=e["var_weight"], cov_weight=e.get("cov_weight", 0.0),
                   corr_inv_weight=e.get("corr_inv_weight", 0.0), corr_var_weight=e.get("corr_var_weight", 0.0), corr_whiten_weight=e.get("corr_whiten_weight", 0.0), corr_whiten_norm=e.get("corr_whiten_norm", "dim"),
                   sigreg_weight=e["sigreg_weight"], arch=e["arch"], objective=e["objective"], coupling_layers=w["coupling_layers"])
enc, _ = train_encoder(world, observe, ec, seed + 77_777)
wh = fit_whitener(encode(enc, observe, world.sample(s["num_whiten"])), s["zca_eps"])
def pairs_fn(k):
    if k > world.n_blocks - 1: return None
    u, v = world.correspondence_pairs(s["num_pairs"], k)
    return wh(encode(enc, observe, u)), wh(encode(enc, observe, v))
rungs = fit_ladder(pairs_fn, d, d_ks=list(s["d_ks"]), nesting_enforcement="hard")
r2 = rungs[1]; H = r2.H_prev.double()
out = {"seed": seed, "applied": [bool(g.applied) for g in rungs], "gaps": [round(g.gap_ratio, 2) for g in rungs], "dim_H_prev_at_rung2": H.shape[1],
       "rung2_eigs_top8": [round(float(x), 3) for x in r2.eigvals[:8]]}
fp = {}
for j in range(1, world.n_blocks + 1):
    u = world.sample(20000); v = u.clone(); v[:, world.block_slice(j)] = world.sample(20000)[:, world.block_slice(j)]
    dd = (wh(encode(enc, observe, u)) - wh(encode(enc, observe, v))).double() @ H
    ev = torch.linalg.eigvalsh(dd.T @ dd / len(dd)).flip(0)
    fp[j] = {"trace": round(float(ev.sum()), 2), "top8": [round(float(x), 2) for x in ev[:8]]}
out["resample_only_block_j_in_H_prev"] = fp
print(json.dumps(out))
