import base64, io, glob, json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False, "font.size": 11})
RED, BLUE, GREY, GRN, ORG = "#c2410c", "#1d4ed8", "#64748b", "#15803d", "#ea580c"
def img(fig, w="100%"):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=170, bbox_inches="tight", facecolor="white"); plt.close(fig); return f'<img src="data:image/png;base64,{base64.b64encode(b.getvalue()).decode()}" style="width:{w}">'
load = lambda pat: [json.load(open(f)) for f in sorted(glob.glob(pat))]
# ---------- mechanism figure (2-number toy)
rng = np.random.default_rng(4)
def obs(z, s=.3):
    x = z.copy(); x[:, 0] = z[:, 0] + s * np.tanh(1.5 * z[:, 1]); x[:, 1] = z[:, 1] + s * np.tanh(1.5 * x[:, 0]); return x
th = .6; Rm = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]]); f = lambda z: obs(z) @ Rm.T
ref = f(rng.standard_normal((20000, 2))); mu = ref.mean(0); ev, V = np.linalg.eigh(np.cov((ref - mu).T)); W = V @ np.diag(ev ** -.5) @ V.T; wh = lambda q: (q - mu) @ W
u = rng.standard_normal((20000, 2)); v = u.copy(); v[:, 0] = rng.standard_normal(20000)
ru, rv = wh(f(u)), wh(f(v)); D = ru - rv; M = D.T @ D / len(D); lam, E = np.linalg.eigh(M); lam, E = lam[::-1], E[:, ::-1]
fig, axs = plt.subplots(1, 3, figsize=(12.5, 3.8)); p = wh(f(rng.standard_normal((700, 2))))
axs[0].scatter(p[:, 0], p[:, 1], s=4, color="#cbd5e1")
for i in range(5): axs[0].plot([ru[i, 0], rv[i, 0]], [ru[i, 1], rv[i, 1]], "-o", color=RED, ms=4)
axs[0].set_title("1  pairs (orange): same slow value,\ndifferent fast value", fontsize=10)
axs[1].scatter(D[:1500, 0], D[:1500, 1], s=3, color=RED, alpha=.4); axs[1].annotate("", xy=E[:, 0] * 3, xytext=-E[:, 0] * 3, arrowprops=dict(arrowstyle="<->", color="k", lw=2))
axs[1].set_title(f"2  subtract each pair: an oval.\nsizes along the two axes: {lam[0]:.2f} and {lam[1]:.2f}", fontsize=10)
h = E[:, 1]; pr = (p @ h)[:, None] * h[None, :]; axs[2].scatter(p[:, 0], p[:, 1], s=3, color="#e2e8f0"); axs[2].scatter(pr[:, 0], pr[:, 1], s=5, color=BLUE, alpha=.6)
axs[2].set_title("3  drop the long axis, keep the rest\n(what did not change)", fontsize=10)
for a in axs: a.set_xlim(-3.6, 3.6); a.set_ylim(-3.6, 3.6); a.set_aspect("equal"); a.set_xticks([]); a.set_yticks([]); a.axhline(0, color="#e2e8f0", lw=.6); a.axvline(0, color="#e2e8f0", lw=.6)
fig.tight_layout(); fig_mech = img(fig)
# ---------- dimension ladder
fig, ax = plt.subplots(figsize=(9, 2.9)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 7.4)
for i, dim in enumerate([28, 24, 20, 16, 12, 8, 4]):
    y = 6.9 - i * .98; w = 7 * dim / 28
    ax.add_patch(FancyBboxPatch((0, y - .3), w, .6, boxstyle="round,pad=0.02", fc=BLUE if i == 6 else "#93c5fd", ec="none")); ax.text(.12, y, f"{dim} directions", va="center", fontsize=8.5, color="white" if i == 6 else "#1e293b")
    ax.text(w + .15, y, f"rung {i+1}: block {i+1} removed (4 directions)" if i < 6 else "left: the slowest layer", va="center", fontsize=8.5, color=RED if i < 6 else BLUE)
fig_ladder = img(fig, "75%")
# ---------- baseline
fig, ax = plt.subplots(figsize=(5.2, 2.8)); ax.bar(["authors' code", "this project"], [.9980, .9889], yerr=[.0014, .0028], color=[GREY, BLUE], width=.5, capsize=4); ax.set_ylim(.97, 1.002); ax.set_ylabel("slow-part score (R²)"); ax.set_title("Starting point: one split, 2 layers (5 runs)", fontsize=10.5); fig_base = img(fig, "52%")
# ---------- plain 6-rung result
R = json.load(open("results/simple_depth.json")); ang = np.array([r["angle"] for r in R]); gap = np.array([r["gap"] for r in R])
fig, axs = plt.subplots(1, 2, figsize=(11.5, 3.5)); x = np.arange(1, 7)
for a in ang: axs[0].plot(x, a, "-o", color=BLUE, alpha=.55, ms=4)
axs[0].axhline(80, color="#94a3b8", ls="--"); axs[0].text(6.05, 76, "unrelated ≈ 80°", ha="right", va="top", fontsize=9, color="#64748b"); axs[0].axhline(5, color=GRN, ls=":"); axs[0].text(6.05, 9, "good < 5°", ha="right", fontsize=9, color=GRN)
axs[0].set_ylim(0, 92); axs[0].set_xlabel("rung"); axs[0].set_ylabel("angle to the true block (degrees)"); axs[0].set_title("How close each found block is to the truth", fontsize=10.5)
for g in gap: axs[1].plot(x, g, "-o", color=RED, alpha=.55, ms=4)
axs[1].axhline(10, color=GRN, ls=":"); axs[1].text(6.05, 11.5, "clean cut > 10", ha="right", fontsize=9, color=GRN); axs[1].axhline(1, color="#94a3b8", ls="--"); axs[1].text(6.05, 1.15, "no cut = 1", ha="right", fontsize=9, color="#64748b")
axs[1].set_yscale("log"); axs[1].set_ylim(.8, 300); axs[1].set_xlabel("rung"); axs[1].set_ylabel("gap"); axs[1].set_title("How sharp each cut is", fontsize=10.5)
for a in axs: a.set_xticks(x)
fig.tight_layout(); fig_res = img(fig)
rows6 = "".join(f"<tr><td>{k}</td><td>{np.median(ang[:,k-1]):.1f}°</td><td>{ang[:,k-1].min():.1f} – {ang[:,k-1].max():.1f}°</td><td>{np.median(gap[:,k-1]):.0f}</td></tr>" for k in range(1, 7))
# ---------- bend strength
worst = lambda rs: [max(g["angle_deg"] for g in r["rungs"]) for r in rs]
series = [("no encoder training", GREY, -.22, {s_: worst(load(f"results/minimal/e55/u/s{s_}/main_seed*.json")) for s_ in (1, 2, 4, 8)}),
          ("trained encoder", RED, 0.0, {0.5: worst(load("results/minimal/e54/d4/main_seed*.json")), **{s_: worst(load(f"results/minimal/e55/t/s{s_}/main_seed*.json")) for s_ in (1, 2, 4, 8)}}),
          ("trained, weak cuts still applied", GRN, .22, {2: worst(load("results/minimal/e56/main_seed*.json")), 4: worst(load("results/minimal/e57/b4_s4/main_seed*.json"))})]
pos = {0.5: 0, 1: 1, 2: 2, 4: 3, 8: 4}; fig, ax = plt.subplots(figsize=(10, 4.2))
for lab, col, off, d in series:
    for k_, vv in d.items():
        ax.scatter(np.full(len(vv), pos[k_] + off) + np.random.default_rng(0).uniform(-.04, .04, len(vv)), vv, s=22, color=col, alpha=.8, label=lab if k_ == list(d)[0] else None); ax.plot([pos[k_] + off - .08, pos[k_] + off + .08], [np.median(vv)] * 2, color="k", lw=2)
ax.axhline(80, color="#94a3b8", ls="--"); ax.text(4.45, 81.5, "unrelated ≈ 80°", ha="right", color="#64748b", fontsize=9); ax.axhline(5, color=GRN, ls=":"); ax.text(-.45, 6.3, "good < 5°", color=GRN, fontsize=9)
ax.set_xticks(range(5)); ax.set_xticklabels(["0.5 (mild)", "1", "2", "4", "8 (strong)"]); ax.set_xlabel("how strongly the generator bends the hidden numbers"); ax.set_ylabel("worst rung: angle to the truth (degrees)"); ax.set_ylim(0, 92); ax.legend(frameon=False, loc="center left", fontsize=9)
ax.set_title("Each dot is one run (4 layers); black bar = median", fontsize=10.5); fig_bend = img(fig)
# ---------- equal speeds
e38 = load("results/minimal/e38/main_seed*.json"); lad = np.array([r["payoff"]["ladder_angles_deg"] for r in e38]); sing = np.array([r["payoff"]["single_shot_angles_deg"] for r in e38])
fig, ax = plt.subplots(figsize=(7.5, 3.4)); xs = np.arange(lad.shape[1])
for j in range(len(e38)): ax.scatter(xs - .17 + np.random.default_rng(j).uniform(-.06, .06), lad[j], color=GRN, s=26); ax.scatter(xs + .17 + np.random.default_rng(j + 9).uniform(-.06, .06), sing[j], color=RED, s=26)
ax.scatter([], [], color=GRN, label="iterated splitting (uses pairs)"); ax.scatter([], [], color=RED, label="one split of adjacent-frame differences (no pairs)")
ax.set_xticks(xs); ax.set_xticklabels([f"rung {i+1}" for i in xs]); ax.set_ylabel("angle to the truth (degrees)"); ax.set_ylim(0, 95); ax.legend(frameon=False, fontsize=9, loc="center right"); fig_eq = img(fig, "72%")
sing_rng = f"{sing.min():.0f}–{sing.max():.0f}°"; lad_max = f"{lad.max():.1f}"
# ---------- pairs from data
e58 = load("results/minimal/e58/seed*.json"); arms = [("generator", "exact pairs", GRN), ("label", "same true cluster", BLUE), ("kmeans_slow", "clusters found from data (slow part)", ORG), ("kmeans_all", "clusters found from data (all)", RED), ("random", "random pairs", GREY)]
fig, ax = plt.subplots(figsize=(8.5, 3.9))
for key, lab, col in arms:
    m = np.array([[x["angle_deg"] for x in r["arms"][key]] for r in e58]); ax.plot(range(1, 6), np.median(m, 0), "-o", color=col, label=lab, lw=2)
ax.axhline(80, color="#94a3b8", ls="--"); ax.set_xticks(range(1, 6)); ax.set_xlabel("rung"); ax.set_ylabel("angle to the truth (degrees)"); ax.set_ylim(0, 92); ax.legend(frameon=False, fontsize=8.5, ncol=3, loc="upper center", bbox_to_anchor=(.5, -.2)); fig_pairs = img(fig, "85%")
# ---------- robot
rows = [l.split("|") for l in open("results/stage_r/STAGE_R_REPORT.md") if "treated" in l or "baseline" in l]
vals = [(r[1].strip(), r[2].strip(), float(r[8])) for r in rows if len(r) > 10 and r[8].strip().replace(".", "").isdigit()]
fig, ax = plt.subplots(figsize=(7.5, 3.1)); labs = [t[:4] + chr(10) + ("base" if a == "baseline" else "treat") for t, a, _ in vals]
ax.bar(range(len(vals)), [v for *_, v in vals], color=[RED if a == "treated" else GREY for _, a, _ in vals]); ax.axhline(3, color=GRN, ls="--"); ax.text(len(vals) - .5, 2.8, "needed: 3", ha="right", color=GRN)
ax.set_xticks(range(len(vals))); ax.set_xticklabels(labs, fontsize=7); ax.set_ylabel("viewpoint-block ratio"); fig_rob = img(fig, "72%")
html = open("experiments/full_report_template.html").read()
for k, v in {"FIG_MECH": fig_mech, "FIG_LADDER": fig_ladder, "FIG_BASE": fig_base, "FIG_RES": fig_res, "ROWS6": rows6, "FIG_BEND": fig_bend, "FIG_EQ": fig_eq, "SING": sing_rng, "LADMAX": lad_max, "FIG_PAIRS": fig_pairs, "FIG_ROB": fig_rob}.items(): html = html.replace("{{" + k + "}}", v)
open("docs/report/FULL.html", "w").write(html); print("ok")
