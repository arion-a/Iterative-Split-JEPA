"""Exploratory diagnostic (not registered): why rung 2 finds the wrong block at 4 blocks with the generic MLP.
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
rungs = fit_ladder(pairs_fn, d, d_ks=list(s["d_ks"]), nesting_enforcement="hard")
z = world.sample(20000); r = wh(encode(enc, observe, z))
a_hat = audits.ridge_fit(z[:15000], r[:15000])[:-1].T                 # r ~ A z
orth = lambda M: torch.linalg.qr(M.double())[0].float()
img = {j: orth(a_hat[:, world.block_slice(j)]) for j in range(1, world.n_blocks + 1)}
out = {"cfg": cfgp, "seed": seed, "angles_deg": [rg.k and audits.max_angle_deg(rg.V, a_hat[:, world.block_slice(rg.k)]) for rg in rungs]}
V2 = rungs[1].V.double()
out["V2_direction_in_block_image"] = [[round(float((img[j].double().T @ V2[:, i]).square().sum()), 2) for j in range(1, world.n_blocks + 1)] for i in range(V2.shape[1])]   # per direction: squared cosine with block 1..4
out["rung_eigs"] = [[round(float(x), 3) for x in rg.eigvals[:8]] for rg in rungs]
fp = {}
for j in range(1, world.n_blocks + 1):                                # footprint of block j in the output: resample only block j
    u = world.sample(20000); v = u.clone(); v[:, world.block_slice(j)] = world.sample(20000)[:, world.block_slice(j)]
    dd = (wh(encode(enc, observe, u)) - wh(encode(enc, observe, v))).double(); ev = torch.linalg.eigvalsh(dd.T @ dd / len(dd)).flip(0)
    fp[j] = {"trace": round(float(ev.sum()), 2), "dims_above_5pct_of_top": int((ev > 0.05 * ev[0]).sum()), "top8": [round(float(x), 3) for x in ev[:8]]}
out["footprint"] = fp
fv = {}
for j in range(1, world.n_blocks + 1):                                # the actual footprint subspace of block j in the output (top eigenvectors of the resample-only-j moment)
    u = world.sample(20000); v = u.clone(); v[:, world.block_slice(j)] = world.sample(20000)[:, world.block_slice(j)]
    dd = (wh(encode(enc, observe, u)) - wh(encode(enc, observe, v))).double(); fv[j] = torch.linalg.eigh(dd.T @ dd / len(dd))[1].flip(1)[:, :world.block_dims[j - 1]].float()
out["angle_V_k_to_footprint_k_deg"] = [audits.max_angle_deg(rungs[0].V, fv[1]), audits.max_angle_deg(rungs[1].V, fv[2]), audits.max_angle_deg(rungs[2].V, fv[3])]
out["angle_linear_image_to_footprint_deg"] = [audits.max_angle_deg(a_hat[:, world.block_slice(j)], fv[j]) for j in range(1, world.n_blocks + 1)]
b2 = world.block_slice(2); ntr = 15000
out["z2_readout_r2_mlp"] = {"from_whole_embedding": audits.mlp_r2(r[:ntr], z[:ntr][:, b2], r[ntr:], z[ntr:][:, b2]), "from_V2_coordinates_only": audits.mlp_r2(r[:ntr] @ rungs[1].V, z[:ntr][:, b2], r[ntr:] @ rungs[1].V, z[ntr:][:, b2]),
                            "from_V2_linear": audits.linear_r2(r[:ntr] @ rungs[1].V, z[:ntr][:, b2], r[ntr:] @ rungs[1].V, z[ntr:][:, b2])}
out["presence_mlp"] = [round(audits.mlp_r2(r[:15000], z[:15000][:, world.block_slice(j)], r[15000:], z[15000:][:, world.block_slice(j)]), 2) for j in range(1, world.n_blocks + 1)]
print(json.dumps(out))
