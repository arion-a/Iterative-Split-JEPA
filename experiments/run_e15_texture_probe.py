"""E15: how well can a linear probe read the TRUE texture from the full whitened encoder features, before any split?
Rebuilds each seed's encoder exactly as run_stage_b2_spec does (same seeds, same RNG order) and compares with the rung-1 texture block's variant R2.
    python experiments/run_e15_texture_probe.py --seed 0   ->   results/diagnostics/e15/seed<N>.json"""
import argparse, json, os
import torch, yaml
from isj import audits
from isj.encoder import EncoderConfig, encode, train_encoder
from isj.engine import fit_rung, fit_whitener
from isj.worlds import CouplingMap, HierarchicalMixtureWorld

ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, required=True); a = ap.parse_args()
cfg = yaml.safe_load(open("configs/stage_b2_nesting.yaml")); w, e, s = cfg["world"], cfg["encoder"], cfg["split"]
seed, sg = a.seed, cfg["sweep"]["clean_sigma_cat"]
world = HierarchicalMixtureWorld(list(w["block_dims"]), list(w["rhos"]), seed=seed, n_categories=w["n_categories"], n_identities=w["n_identities"],
                                 n_textures=w["n_textures"], sigma_cat=sg, sigma_id=w["sigma_id"], sigma_tex=w["sigma_tex"])
d = world.d
observe = CouplingMap(d, w["coupling_layers"], w["coupling_strength"], w.get("obs_dim"), seed=seed)
ecfg = EncoderConfig(in_dim=observe.obs_dim, latent_dim=d, hidden=e["hidden"], steps=e["steps"], batch_size=e["batch_size"], lr=e["lr"], reg=e["reg"],
                     var_weight=e["var_weight"], sigreg_weight=e["sigreg_weight"], arch=e["arch"], objective=e["objective"], coupling_layers=w["coupling_layers"])
enc, _ = train_encoder(world, observe, ecfg, seed + 77_777, False)
wh = fit_whitener(encode(enc, observe, world.sample(s["num_whiten"])), 1e-5)
R = lambda z: wh(encode(enc, observe, z))
ntr = s["probe_train"]
z_all, _ = world.sample_with_labels(ntr + s["probe_test"]); r_all = R(z_all)
ztr, zte, rtr, rte = z_all[:ntr], z_all[ntr:], r_all[:ntr], r_all[ntr:]
blk = {"texture": slice(0, 4), "identity": slice(4, 8), "category": slice(8, 12)}
out = {"seed": seed, "global_r2": audits.r2(audits.ridge_fit(ztr, rtr), zte, rte)}
# probe from the FULL features to the true block (the direction that matters for 'is the information in the encoder')
out["full_feature_probe_r2"] = {k: audits.linear_r2(rtr, ztr[:, v], rte, zte[:, v]) for k, v in blk.items()}
out["full_feature_probe_r2_per_texture_dim"] = [audits.linear_r2(rtr, ztr[:, i:i + 1], rte, zte[:, i:i + 1]) for i in range(4)]
# the recovered rung-1 texture block, same data order as the run (pairs drawn after the evaluation set)
u1, v1 = world.correspondence_pairs(s["num_pairs_per_rung"][0], 1)
fit1 = fit_rung(R(u1), R(v1), torch.eye(d), k=1, d_k=4)
out["recovered_texture_block_r2"] = audits.linear_r2(rtr @ fit1.V, ztr[:, :4], rte @ fit1.V, zte[:, :4])
out["recovered_invariant_content_r2"] = audits.linear_r2(rtr @ fit1.Q, ztr[:, 4:], rte @ fit1.Q, zte[:, 4:])
os.makedirs("results/diagnostics/e15", exist_ok=True)
json.dump(out, open(f"results/diagnostics/e15/seed{seed}.json", "w"), indent=1)
print(json.dumps(out))
