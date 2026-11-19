"""E58 (exploratory pipeline, registered in docs/EVIDENCE.md): cluster-built pairs for rungs 2-5 in a 6-level nested cluster world.
    python experiments/run_nested_pairs.py CONFIG SEED OUTDIR
Trains the encoder once (E54 recipe: invertible coupling encoder, paper objective). Rung 1 always uses generator twins. For each arm, rungs 2-5 use
  generator : exact twins (upper bound)      label : same true cell, rest independent (perfect clustering)
  kmeans_all: k-means (oracle cluster count = number of cells) on the invariant content H_(k-1)
  kmeans_slow: the same, after projecting H_(k-1) onto its slowest directions (smallest eigenvalues of the adjacent-frame change moment; their number = 4 x slower blocks, oracle)
  random    : unrelated pairs (control)
Reports per arm and rung: angle to the true block image, gap ratio, and for the k-means arms cluster purity and the share of mis-grouped pairs."""
import sys, json, yaml, time, torch
from isj import audits
from isj.cluster import kmeans, pairs_within_clusters, purity
from isj.encoder import EncoderConfig, encode, train_encoder
from isj.engine import fit_rung, fit_whitener
from isj.worlds import BlockWorld, CouplingMap, NestedMixtureWorld
cfgp, seed, outdir = sys.argv[1], int(sys.argv[2]), sys.argv[3]
t0 = time.time()
cfg = yaml.safe_load(open(cfgp)); w, e, s, nst = cfg["world"], cfg["encoder"], cfg["split"], cfg["nested"]
world = NestedMixtureWorld(list(w["block_dims"]), list(w["rhos"]), seed=seed, counts=list(nst["counts"]), sigma=nst["sigma"]); d, L = world.d, world.n_blocks
observe = CouplingMap(d, w["coupling_layers"], w["coupling_strength"], w.get("obs_dim"), seed=seed)
ec = EncoderConfig(in_dim=observe.obs_dim, latent_dim=d, hidden=e["hidden"], steps=e["steps"], batch_size=e["batch_size"], lr=e["lr"], reg=e["reg"], var_weight=e["var_weight"],
                   sigreg_weight=e["sigreg_weight"], arch=e["arch"], objective=e["objective"], coupling_layers=w["coupling_layers"], enc_layers=e.get("enc_layers", 6))
enc, _ = train_encoder(world, observe, ec, seed + 77_777)
wh = fit_whitener(encode(enc, observe, world.sample(s["num_whiten"])), s["zca_eps"])
R = lambda z: wh(encode(enc, observe, z))
n, N = s["num_pairs"], nst["cluster_samples"]
z_p = world.sample(s["probe_train"]); r_p = R(z_p)
a_hat = audits.ridge_fit(z_p, r_p)[:-1].T
image = {k: a_hat[:, world.block_slice(k)] for k in range(1, L + 1)}
z_c, lab_c = world.sample_with_labels(N); r_c = R(z_c)
za, zb = world.transition_pairs(N); ra, rb = R(za), R(zb)                   # adjacent frames, for the slow-subspace variant
out = {"seed": seed, "arms": {}}
for arm in ("generator", "label", "kmeans_all", "kmeans_slow", "random"):
    h, rungs = torch.eye(d), []
    for k in range(1, L):
        info = {}
        if k == 1 or arm in ("generator", "label", "random"):
            if k == 1 or arm == "generator": zu, zv = world.correspondence_pairs(n, k)
            elif arm == "label": zu, zv = world.label_pairs(n, k)
            else: zu, zv = world.sample(n), world.sample(n)
            ru, rv = R(zu), R(zv)
        else:
            x = r_c @ h                                                                  # invariant content H_(k-1)
            if arm == "kmeans_slow":
                dd = (rb - ra).double() @ h.double(); dim = sum(world.block_dims[k:])
                vals, vecs = torch.linalg.eigh(dd.T @ dd / len(dd)); x = (x.double() @ vecs[:, :dim]).float()      # slowest directions first (ascending)
            K = world.n_cells(k)
            lab, _, _ = kmeans(x, K, restarts=nst["kmeans_restarts"], seed=seed)
            true_cell = world.cell(lab_c, k)
            ia, ib = pairs_within_clusters(lab, seed)
            info = {"K": K, "purity": purity(lab, true_cell), "misgrouped": float((true_cell[ia] != true_cell[ib]).float().mean()), "n_pairs": len(ia)}
            ru, rv = r_c[ia], r_c[ib]
        fit = fit_rung(ru, rv, h, k=k, d_k=4, nesting_enforcement="hard")
        rungs.append({"k": k, "angle_deg": audits.max_angle_deg(fit.V, image[k]), "gap_ratio": fit.gap_ratio, **info})
        h = fit.Q
    out["arms"][arm] = rungs
out["seconds"] = round(time.time() - t0, 1)
import os; os.makedirs(outdir, exist_ok=True); json.dump(out, open(f"{outdir}/seed{seed}.json", "w"))
print(json.dumps({a: [(r["k"], round(r["angle_deg"], 1), round(r["gap_ratio"], 1), round(r.get("purity", -1), 2)) for r in v] for a, v in out["arms"].items()}))
