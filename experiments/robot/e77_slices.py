"""E77 read-out of the fixed slices (registered in docs/EVIDENCE.md): held-out camera accuracy, layout R2 and progress R2 read from each slice of the embedding.
    PYTHONPATH=src python e77_slices.py EMB_NPY DATA_DIR OUT_JSON      slices: camera h[0:4], trajectory h[4:16], progress h[16:32], layout h[32:64]; ridge read-outs, train -> validation trajectories (the E76 split)"""
import sys, glob, json, numpy as np, torch
from isj import audits
emb, ddir, out = sys.argv[1], sys.argv[2], sys.argv[3]; SL = {"camera": (0, 4), "trajectory": (4, 16), "progress": (16, 32), "layout": (32, 64)}
E = torch.from_numpy(np.load(emb)).double(); files = sorted(glob.glob(f"{ddir}/group_*.npz")); S = torch.from_numpy(np.stack([np.load(f)["state"] for f in files])).double()
G, TT, K, _, D = E.shape; n_val = max(1, round(0.2 * TT)); g0 = torch.Generator().manual_seed(0)
perm = torch.stack([torch.randperm(TT, generator=g0) for _ in range(G)]); take = lambda X, idx: torch.stack([X[i, idx[i]] for i in range(G)])
Etr, Eva, Str, Sva = take(E, perm[:, n_val:]), take(E, perm[:, :n_val]), take(S, perm[:, n_val:]), take(S, perm[:, :n_val])
mu, sd = Etr.reshape(-1, D).mean(0), Etr.reshape(-1, D).std(0).clamp_min(1e-8); Ztr, Zva = (Etr - mu) / sd, (Eva - mu) / sd
cols = lambda names: torch.cat([torch.arange(*SL[n]) for n in names])
def cam_acc(c):
    a = torch.cat([Ztr[..., 0, :], Ztr[..., 1, :]]).reshape(-1, D)[:, c]; ya = torch.cat([-torch.ones(len(a) // 2), torch.ones(len(a) // 2)]).double()
    w = audits.ridge_fit(a, ya[:, None]); b = torch.cat([Zva[..., 0, :], Zva[..., 1, :]]).reshape(-1, D)[:, c]; yb = torch.cat([-torch.ones(len(b) // 2), torch.ones(len(b) // 2)]).double()
    return float(((torch.cat([b, torch.ones(len(b), 1, dtype=b.dtype)], 1) @ w).squeeze(1).sign() == yb).float().mean())
lay = lambda S_: torch.cat([S_[:, :, 0, 3:5].unsqueeze(2).expand(-1, -1, K, -1), S_[:, :, :, 6:9]], 3).reshape(-1, 5)
prog = lambda S_: torch.linspace(0, 1, K).view(1, 1, K).expand(S_.shape[0], S_.shape[1], K).reshape(-1, 1).double()
xtr, xva = Ztr[..., 0, :].reshape(-1, D), Zva[..., 0, :].reshape(-1, D); r2 = lambda c, ytr, yva: audits.linear_r2(xtr[:, c], ytr, xva[:, c], yva)
groups = {**{n: cols([n]) for n in SL}, "slices 2-4": cols(["trajectory", "progress", "layout"]), "all": torch.arange(D)}
res = {"camera_acc": {n: cam_acc(c) for n, c in groups.items()}, "layout_R2": {n: r2(c, lay(Str), lay(Sva)) for n, c in groups.items()}, "progress_R2": {n: r2(c, prog(Str), prog(Sva)) for n, c in groups.items()}}
json.dump(res, open(out, "w"), indent=1); print(json.dumps(res, indent=1)[:1500])
