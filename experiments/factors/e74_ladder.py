"""E74 analysis (registered in docs/EVIDENCE.md): the iterated splitting on frozen embeddings of the E62 scene-factor images; same pipeline and rules as e62_ladder.py.
    PYTHONPATH=src python e74_ladder.py EMB_NPZ PROBE_NPZ OUT_JSON [NPAIRS]
EMB_NPZ: Zp, Zu1..8, Zv1..8 from extract_embeddings.py. PROBE_NPZ: data/e62/probe.npz (the factor values f). Reads held-out R2 of every factor group from each rung's block."""
import sys, json, numpy as np, torch
from isj import audits
from isj.engine import fit_rung, fit_whitener, select_block_count
SIZES = [1, 2, 1, 2, 3, 2, 1, 2, 1]; OFF = np.cumsum([0] + SIZES); NAMES = ["gripper", "arm pose", "cube yaw", "cube position", "cube colour", "light tint", "brightness", "camera dist/elev", "camera azimuth"]
emb, probe, out = sys.argv[1], sys.argv[2], sys.argv[3]; torch.set_num_threads(4); torch.manual_seed(0)
E = np.load(emb); Zp = torch.from_numpy(E["Zp"]).double(); Fp = torch.from_numpy(np.load(probe)["f"]).double()
Zu = {k: torch.from_numpy(E[f"Zu{k}"]).double() for k in range(1, 9)}; Zv = {k: torch.from_numpy(E[f"Zv{k}"]).double() for k in range(1, 9)}
n_pairs = len(Zu[1]); wh = fit_whitener(torch.cat([Zu[k] for k in Zu]).float(), 1e-5); W = lambda z: wh(z.float()).double()
Pw = W(Zp); D = Pw.shape[1]; ntr = 6000; Ft = (Fp - Fp[:ntr].mean(0)) / Fp[:ntr].std(0)
def r2g(B, g):                                    # held-out R2 of factor group g read from the block B (mean over the group's numbers); the probe's last 3000 images score it
    X = Pw @ B; cols = list(range(OFF[g], OFF[g + 1]))
    return float(np.mean([audits.linear_r2(X[:ntr], Ft[:ntr, [c]], X[ntr:], Ft[ntr:, [c]]) for c in cols]))
I = torch.eye(D, dtype=torch.double); full = [r2g(I, g) for g in range(9)]; retained = [g for g in range(9) if full[g] >= 0.5]
res = {"embedding_dim": D, "n_pairs_per_rung": n_pairs, "full_embedding_R2": full, "retained_factors": [g + 1 for g in retained], "rungs": []}
h = I
for k in range(1, 9):
    ru, rv = W(Zu[k]), W(Zv[k]); sw = torch.rand(len(ru)) < 0.5; ru, rv = torch.where(sw[:, None], rv, ru), torch.where(sw[:, None], ru, rv)
    pr = fit_rung(ru, rv, h, k=k, d_k=1); vals = pr.eigvals.double(); d = select_block_count(vals, 0.1 * float(vals[0])); fb = False
    if d == 0: d = int(torch.argmax(vals[:32] / vals[1:33].clamp_min(1e-12))) + 1; fb = True
    f = fit_rung(ru, rv, h, k=k, d_k=d); h = f.Q.double(); row = [r2g(f.V.double(), g) for g in range(9)]
    best = max(retained, key=lambda g: row[g]) if retained else -1
    res["rungs"].append({"k": k, "d": d, "gap": f.gap_ratio, "fallback": fb, "reading": row, "best_retained_factor": best + 1,
                         "aligned": bool(k - 1 in retained and best == k - 1 and row[k - 1] >= 0.5)})
    print(k, "d", d, "gap", round(f.gap_ratio, 2), "best retained factor", best + 1, "own R2", round(row[k - 1], 2), flush=True)
res["core_reading"] = [r2g(h, g) for g in range(9)]; res["core_dim"] = int(h.shape[1])
res["n_aligned"] = sum(r["aligned"] for r in res["rungs"]); res["n_gap_ge_2"] = sum(r["gap"] >= 2 for r in res["rungs"])
json.dump(res, open(out, "w"), indent=1)
print("retained", [NAMES[g] for g in retained], "| aligned", res["n_aligned"], "of 8; gap>=2", res["n_gap_ge_2"], "of 8; core", [round(x, 2) for x in res["core_reading"]])
