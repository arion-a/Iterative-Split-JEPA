"""Recovered vs true speed (E73, E72, E71b), one point per seed and block/slice. python experiments/make_rate_picture.py -> docs/img/rate_recovery.png"""
import glob, json, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
rhos = lambda K: [float(1 - x) for x in np.geomspace(0.8, 0.04, K)]
J = lambda p: [json.load(open(f)) for f in sorted(glob.glob(p))]
fig, ax = plt.subplots(1, 3, figsize=(15, 5), dpi=130)
T = [0.20, 0.70, 0.95]; a = ax[0]
for tag, c, m, lab in (("P_s0.5", "#1b7f3b", "o", "paper recipe, strength 0.5"), ("P_s1", "#2a6fdb", "s", "paper recipe, strength 1"), ("Q_s1", "#c0392b", "x", "predictive-loss MLP, strength 1 (blocks NOT recovered)")):
    for j, r in enumerate(J(f"results/e73/{tag}/main_seed*.json")): a.scatter(T, r["block_rho_hat"], c=c, marker=m, s=38, alpha=.8, label=lab if j == 0 else None)
a.set_title("E73: small 3-layer world\n(blocks by eigen-split, 5 seeds)")
for i, (EXP, STR, t) in enumerate((("e72", "0.5", "E72: deep worlds, strength 0.5\n(slow slices only, K = 11, 13, 16)"), ("e71b", "1", "E71b: deep worlds, strength 1\n(slow slices only, K = 11, 13, 16)"))):
    a = ax[i + 1]; root = "results/nested_pod_e72" if EXP == "e72" else "results/nested_pod_e71b"
    for K, c in ((11, "#1b7f3b"), (13, "#2a6fdb"), (16, "#d68910")):
        tr = rhos(K); sl = [b for b in range(K) if tr[b] >= 0.86]
        for j, r in enumerate(J(f"{root}/results/nested/{EXP}/A/K{K}_s{STR}/main_seed*.json")): a.scatter([tr[b] for b in sl], [r["slice"]["rho_hat"][b] for b in sl], c=c, s=22, alpha=.7, label=f"K = {K}" if j == 0 else None)
    a.set_title(t)
for a in ax:
    a.plot([0, 1], [0, 1], "k--", lw=1, label="recovered = true"); a.set_xlim(0, 1.02); a.set_ylim(0, 1.02); a.set_xlabel("true speed rho (from the simulator)"); a.grid(alpha=.25)
ax[0].set_ylabel("recovered speed (lag-1 correlation of the block)"); [a.legend(loc="upper left" if k == 0 else "lower right", fontsize=8) for k, a in enumerate(ax)]
ax[1].set_xlim(.84, 1); ax[1].set_ylim(.84, 1); ax[2].set_xlim(.84, 1); ax[2].set_ylim(.84, 1)
plt.tight_layout(); plt.savefig("docs/img/rate_recovery.png")
