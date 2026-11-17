"""E67 (registered in docs/EVIDENCE.md): E62 ladder with non-nested pair sets.
    PYTHONPATH=src:experiments/factors python e67_ablation.py DATA_DIR OUT_JSON"""
import sys, json, numpy as np, torch
from isj import audits
from isj.engine import fit_rung, fit_whitener, select_block_count
from train_ae import AE
SIZES = [1, 2, 1, 2, 3, 2, 1, 2, 1]; OFF = np.cumsum([0] + SIZES)
data, out = sys.argv[1], sys.argv[2]; torch.set_num_threads(8); torch.manual_seed(0)
ck = torch.load(f"{data}/ae.pt"); ae = AE(); ae.load_state_dict(ck["state"]); ae.eval()
def enc(x):
    with torch.no_grad(): return torch.cat([ae.encode(torch.from_numpy(x[i:i + 500]).permute(0, 3, 1, 2).float() / 255) for i in range(0, len(x), 500)]).double()
P = np.load(f"{data}/probe.npz"); Zp, Fp = enc(P["x"]), torch.from_numpy(P["f"]).double(); Zu, Zv = {}, {}
for k in range(1, 9): d = np.load(f"{data}/pairs_k{k}.npz"); Zu[k], Zv[k] = enc(d["u"]), enc(d["v"]); print("enc", k, flush=True)
wh = fit_whitener(torch.cat([Zu[k] for k in Zu]).float(), 1e-5); W = lambda z: wh(z.float()).double()
Pw = W(Zp); D = Pw.shape[1]; ntr = 6000; Ft = (Fp - Fp[:ntr].mean(0)) / Fp[:ntr].std(0)
def r2g(B, g):
    X = Pw @ B; cols = list(range(OFF[g], OFF[g + 1]))
    return float(np.mean([audits.linear_r2(X[:ntr], Ft[:ntr, [c]], X[ntr:], Ft[ntr:, [c]]) for c in cols]))
I = torch.eye(D, dtype=torch.double); full = [r2g(I, g) for g in range(9)]; retained = [g for g in range(9) if full[g] >= 0.5]
def sets(arm):
    S = {k: (Zu[k], Zv[k]) for k in range(1, 9)}
    if arm.startswith("L"):
        p = int(arm[1:]) / 100; g = torch.Generator().manual_seed(7)
        for k in range(1, 8):
            m = torch.rand(len(Zu[k]), generator=g) < p; S[k] = (torch.where(m[:, None], Zu[8], Zu[k]), torch.where(m[:, None], Zv[8], Zv[k]))
    if arm == "R": S = {k: (Zu[9 - k], Zv[9 - k]) for k in range(1, 9)}
    return S
def run(arm):
    S = sets(arm); h = I; res = {"arm": arm, "rungs": []}
    for k in range(1, 9):
        ru, rv = W(S[k][0]), W(S[k][1]); sw = torch.rand(len(ru)) < 0.5; ru, rv = torch.where(sw[:, None], rv, ru), torch.where(sw[:, None], ru, rv)
        pr = fit_rung(ru, rv, h, k=k, d_k=1); vals = pr.eigvals.double(); d = select_block_count(vals, 0.1 * float(vals[0])); fb = False
        if d == 0: d = int(torch.argmax(vals[:32] / vals[1:33].clamp_min(1e-12))) + 1; fb = True
        f = fit_rung(ru, rv, h, k=k, d_k=d); h = f.Q.double(); row = [r2g(f.V.double(), g) for g in range(9)]
        best = max(retained, key=lambda g: row[g]); aligned = bool(k - 1 in retained and best == k - 1 and row[k - 1] >= 0.5)
        res["rungs"].append({"k": k, "d": d, "gap": f.gap_ratio, "fallback": fb, "reading": row, "best_retained_factor": best + 1, "aligned": aligned})
        print(arm, k, "d", d, "gap", round(f.gap_ratio, 2), "best", best + 1, round(row[best], 2), flush=True)
    core = [r2g(h, g) for g in range(9)]; res["core_reading"] = core; res["core_azimuth_R2"] = core[8]
    res["n_aligned"] = sum(r["aligned"] for r in res["rungs"]); res["n_gap_ge_2"] = sum(r["gap"] >= 2 for r in res["rungs"])
    leak = []
    for k in range(4, 8):
        slower = [g for g in retained if g + 1 > k]; leak.append(max(res["rungs"][k - 1]["reading"][g] for g in slower))
    res["leakage"] = float(np.mean(leak)); res["leak_per_rung_4to7"] = leak
    return res
R = {"retained": [g + 1 for g in retained], "arms": {a: run(a) for a in ["N", "L10", "L30", "R"]}}
json.dump(R, open(out, "w"), indent=1)
for a, r in R["arms"].items(): print(a, "aligned", r["n_aligned"], "gap>=2", r["n_gap_ge_2"], "leakage", round(r["leakage"], 3), "core azimuth", round(r["core_azimuth_R2"], 3))
