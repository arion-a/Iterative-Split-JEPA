"""Exploratory diagnostic (not registered, true latents, 3 seeds x sigma_cat 0.1/0.4/0.6): in which space does the spectral cluster-count selector find K = 6?
    python experiments/diag_k_selection_space.py > results/diagnostics/k_selection/output.txt"""
import torch, numpy as np
from isj.worlds import HierarchicalMixtureWorld
from isj.cluster import spectral_k, kmeans, purity
res = {}
for sig in (0.1, 0.4, 0.6):
    for seed in (0, 1, 2):
        w = HierarchicalMixtureWorld([4, 4, 4], [0.2, 0.7, 0.95], seed=seed, n_categories=6, n_identities=20, n_textures=2, sigma_cat=sig)
        x, lab = w.sample_with_labels(6000)
        inv = x[:, 4:]                                  # identity + category (the rung-1 invariant truth)
        cat = x[:, 8:]                                  # category block only (oracle)
        a, b = w.transition_pairs(20000)                # adjacent frames
        d = (b - a)[:, 4:]                              # change in the invariant coordinates
        m = (d.T @ d) / len(d)                          # second moment of the temporal change
        vals, vecs = torch.linalg.eigh(m)               # ascending: slowest directions first
        slow = inv @ vecs[:, :4]                        # 4 slowest directions (no labels used)
        out = []
        for name, f in (("full 8-d invariant", inv), ("category block (oracle)", cat), ("4 slowest directions (no labels)", slow)):
            k, _ = spectral_k(f, seed=seed)
            out.append((name, k))
        # how close is the slow subspace to the category block? principal angles
        q = torch.linalg.qr(vecs[:, :4])[0]; cb = torch.zeros(8, 4); cb[4:, :] = torch.eye(4)
        ang = torch.rad2deg(torch.arccos(torch.linalg.svdvals(q.T @ cb).clamp(max=1))).max().item()
        res[(sig, seed)] = (out, ang)
        print(sig, seed, [f"{n.split(' (')[0][:14]}={k}" for n, k in out], f"slow-vs-category angle {ang:.1f} deg", flush=True)
