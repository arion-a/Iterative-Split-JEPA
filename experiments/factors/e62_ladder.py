"""E62 analysis (registered in docs/EVIDENCE.md): the ladder on autoencoder latents of the nested scene-factor pairs; reading matrix, alignment, traversals.
    PYTHONPATH=src:experiments/factors python e62_ladder.py DATA_DIR OUT_DIR"""
import sys, json, os, numpy as np, torch
from isj import audits
from isj.engine import fit_rung, fit_whitener, select_block_count
from train_ae import AE
SIZES = [1, 2, 1, 2, 3, 2, 1, 2, 1]; OFF = np.cumsum([0] + SIZES)   # same as gen_factors.py (not imported: it needs the ManiSkill venv)
data, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True); torch.set_num_threads(4)
ck = torch.load(f"{data}/ae.pt"); ae = AE(); ae.load_state_dict(ck["state"]); ae.eval()
def enc(x):
    with torch.no_grad(): return torch.cat([ae.encode(torch.from_numpy(x[i:i + 500]).permute(0, 3, 1, 2).float() / 255) for i in range(0, len(x), 500)]).double()
P = np.load(f"{data}/probe.npz"); Zp, Fp = enc(P["x"]), torch.from_numpy(P["f"]).double(); Zu, Zv = {}, {}
for k in range(1, 9): d = np.load(f"{data}/pairs_k{k}.npz"); Zu[k], Zv[k] = enc(d["u"]), enc(d["v"])
wh = fit_whitener(torch.cat([Zu[k] for k in Zu]).float(), 1e-5); W = lambda z: wh(z.float()).double()
Pw = W(Zp); D = Pw.shape[1]; ntr = 6000
Ft = (Fp - Fp[:ntr].mean(0)) / Fp[:ntr].std(0)
def r2g(B, g):                                    # held-out R2 of factor group g from the block B, mean over the group's numbers
    X = Pw @ B; cols = list(range(OFF[g], OFF[g + 1]))
    return float(np.mean([audits.linear_r2(X[:ntr], Ft[:ntr, [c]], X[ntr:], Ft[ntr:, [c]]) for c in cols]))
I = torch.eye(D, dtype=torch.double); full = [r2g(I, g) for g in range(9)]; retained = [g for g in range(9) if full[g] >= 0.5]
res = {"latent": D, "ae_steps": ck["steps"], "ae_final_loss": ck["log"][-1][1], "full_latent_R2": full, "retained_factors": [g + 1 for g in retained], "rungs": []}
h = I; blocks = []
for k in range(1, 9):
    ru, rv = W(Zu[k]), W(Zv[k]); sw = torch.rand(len(ru)) < 0.5; ru, rv = torch.where(sw[:, None], rv, ru), torch.where(sw[:, None], ru, rv)
    pr = fit_rung(ru, rv, h, k=k, d_k=1); vals = pr.eigvals.double(); d = select_block_count(vals, 0.1 * float(vals[0])); fb = False
    if d == 0: d = int(torch.argmax(vals[:32] / vals[1:33].clamp_min(1e-12))) + 1; fb = True
    f = fit_rung(ru, rv, h, k=k, d_k=d); h = f.Q.double(); blocks.append(f.V.double())
    row = [r2g(f.V.double(), g) for g in range(9)]; best = max(retained, key=lambda g: row[g]) if retained else -1
    res["rungs"].append({"k": k, "d": d, "gap": f.gap_ratio, "fallback": fb, "reading": row, "best_retained_factor": best + 1, "aligned": bool(k - 1 in retained and best == k - 1 and row[k - 1] >= 0.5)})
    print(k, "d", d, "gap", round(f.gap_ratio, 2), "best factor", best + 1, "R2", round(row[best], 2), "own", round(row[k - 1], 2), flush=True)
res["core_reading"] = [r2g(h, g) for g in range(9)]; res["core_dim"] = int(h.shape[1])
res["n_aligned"] = sum(r["aligned"] for r in res["rungs"]); res["n_gap_ge_2"] = sum(r["gap"] >= 2 for r in res["rungs"])
json.dump(res, open(f"{out}/e62.json", "w"), indent=1)
torch.save({"blocks": blocks, "mean": wh.mean, "matrix": wh.matrix, "ae": ck["state"]}, f"{out}/blocks.pt")
print("aligned", res["n_aligned"], "of 8; gap>=2", res["n_gap_ge_2"], "of 8; retained", res["retained_factors"])
