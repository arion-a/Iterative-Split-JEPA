"""Exploratory diagnostic (not registered): which part of block 2 is missing from the generic MLP's embedding.
    python experiments/diag_rung2.py CONFIG SEED  -> one JSON line
Retrains the encoder exactly as run_stage_b1 does, then reports, for the rung-2 variant block V2:
  - how much of each of its 4 directions lies in the true image of each block (squared cosines),
  - the footprint of each block in the output: eigenvalues of the moment of the output change when only that block is resampled,
  - rung-1 and rung-2 pair-difference eigenvalues."""
import sys, json, yaml, torch
from isj import audits
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
z = world.sample(20000); r = wh(encode(enc, observe, z)); n = 15000
out = {"cfg": cfgp, "seed": seed}
for j in (2, 3):                                  # block 2 (the affected one) and block 3 (for contrast)
    rows = []
    for i in range(world.block_slice(j).start, world.block_slice(j).stop):
        t = z[:, i:i + 1]
        f = lambda y: audits.mlp_r2(r[:n], y[:n], r[n:], y[n:])
        rows.append({"coordinate": i - world.block_slice(j).start + 1, "z_mlp_r2": f(t), "z_linear_r2": audits.linear_r2(r[:n], t[:n], r[n:], t[n:]),
                     "abs_z_mlp_r2": f(t.abs()), "sign_z_mlp_r2": f(torch.sign(t))})
    out[f"block{j}"] = rows
print(json.dumps(out))
