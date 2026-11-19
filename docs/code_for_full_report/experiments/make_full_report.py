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
    ax.add_patch(FancyBboxPatch((0, y - .3), w, .6, boxstyle="round,pad=0.02", fc=BLUE if i == 6 else "#93c5fd", ec="none")); ax.text(.12, y, f"{dim} directions" if dim > 4 else "4", va="center", fontsize=8.5, color="white" if i == 6 else "#1e293b")
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
# ---------- bend strength (method = trained encoder, every rung applied)
worst = lambda rs: [max(g["angle_deg"] for g in r["rungs"]) for r in rs]
series = [("no encoder training", GREY, -.17, {s_: worst(load(f"results/minimal/e55/u/s{s_}/main_seed*.json")) for s_ in (1, 2, 4)}),
          ("trained encoder", BLUE, .17, {0.5: worst(load("results/minimal/e54/d4/main_seed*.json")), 1: worst(load("results/minimal/e55/t/s1/main_seed*.json")), 2: worst(load("results/minimal/e56/main_seed*.json")), 4: worst(load("results/minimal/e57/b4_s4/main_seed*.json"))})]
pos = {0.5: 0, 1: 1, 2: 2, 4: 3}; fig, ax = plt.subplots(figsize=(9, 3.9))
for lab, col, off, d in series:
    for k_, vv in d.items():
        ax.scatter(np.full(len(vv), pos[k_] + off) + np.random.default_rng(0).uniform(-.04, .04, len(vv)), vv, s=24, color=col, alpha=.85, label=lab if k_ == list(d)[0] else None); ax.plot([pos[k_] + off - .09, pos[k_] + off + .09], [np.median(vv)] * 2, color="k", lw=2)
ax.axhline(80, color="#94a3b8", ls="--"); ax.text(3.45, 76, "unrelated directions ≈ 80°", ha="right", va="top", color="#64748b", fontsize=9)
ax.set_xticks(range(4)); ax.set_xticklabels(["0.5 (mild)", "1", "2", "4"]); ax.set_xlabel("bend strength"); ax.set_ylabel("worst rung: angle to the truth (degrees)"); ax.set_ylim(0, 95); ax.legend(frameon=False, loc="center left", fontsize=9)
fig_bend = img(fig, "88%")
# ---------- equal speeds
e38 = load("results/minimal/e38/main_seed*.json"); lad = np.array([r["payoff"]["ladder_angles_deg"] for r in e38]); sing = np.array([r["payoff"]["single_shot_angles_deg"] for r in e38])
fig, ax = plt.subplots(figsize=(7.5, 3.4)); xs = np.arange(lad.shape[1])
for j in range(len(e38)): ax.scatter(xs - .17 + np.random.default_rng(j).uniform(-.06, .06), lad[j], color=GRN, s=26); ax.scatter(xs + .17 + np.random.default_rng(j + 9).uniform(-.06, .06), sing[j], color=RED, s=26)
ax.scatter([], [], color=GRN, label="iterated splitting (uses pairs)"); ax.scatter([], [], color=RED, label="one split of adjacent-frame differences (no pairs)")
ax.set_xticks(xs); ax.set_xticklabels([f"rung {i+1}" for i in xs]); ax.set_ylabel("angle to the truth (degrees)"); ax.set_ylim(0, 95); ax.legend(frameon=False, fontsize=9, loc="center right"); fig_eq = img(fig, "72%")
sing_rng = f"{sing.min():.0f}–{sing.max():.0f}°"; lad_max = f"{lad.max():.1f}"
# ---------- pairs from data
e58 = load("results/minimal/e58/seed*.json"); arms = [("generator", "exact pairs", GRN), ("label", "same true cluster", BLUE), ("kmeans_slow", "clusters found from the data", ORG), ("random", "random pairs", GREY)]
fig, ax = plt.subplots(figsize=(8.5, 3.7))
for key, lab, col in arms:
    m = np.array([[x["angle_deg"] for x in r["arms"][key]] for r in e58]); ax.plot(range(1, 6), np.median(m, 0), "-o", color=col, label=lab, lw=2)
ax.set_xticks(range(1, 6)); ax.set_xlabel("rung"); ax.set_ylabel("angle to the truth (degrees)"); ax.set_ylim(0, 92); ax.legend(frameon=False, fontsize=9, ncol=4, loc="upper center", bbox_to_anchor=(.5, -.2)); fig_pairs = img(fig, "82%")

# ---------- explainers
g_ = np.random.default_rng(2); T_ = 40; rho_ = [0.2, 0.6, 0.95]; ts = np.zeros((T_, 3)); ts[0] = g_.standard_normal(3)
for t_ in range(1, T_): ts[t_] = [rho_[i] * ts[t_ - 1, i] + np.sqrt(1 - rho_[i] ** 2) * g_.standard_normal() for i in range(3)]
fig, ax = plt.subplots(figsize=(8, 2.5))
for i, (lab, col) in enumerate((("layer A: fast (ρ = 0.2)", RED), ("layer B: middle (ρ = 0.6)", ORG), ("layer C: slow (ρ = 0.95)", BLUE))): ax.plot(ts[:, i], color=col, lw=2, label=lab)
ax.set_xlabel("time step (video frame)"); ax.set_ylabel("one hidden number"); ax.legend(ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(.5, 1.28), fontsize=9); fig_speed = img(fig, "80%")
def obs2(z, s_=1.0):
    x = z.copy(); x[:, 0] = z[:, 0] + s_ * np.tanh(1.5 * z[:, 1]); x[:, 1] = z[:, 1] + s_ * np.tanh(1.5 * x[:, 0]); return x
rot = lambda q: q @ np.array([[np.cos(.6), -np.sin(.6)], [np.sin(.6), np.cos(.6)]]).T
zz = np.random.default_rng(5).standard_normal((20000, 2)); xx_ = rot(obs2(zz)); mu_ = xx_.mean(0); ev_, V_ = np.linalg.eigh(np.cov((xx_ - mu_).T)); W_ = V_ @ np.diag(ev_ ** -.5) @ V_.T
def gridpanel(ax, f, lim, title):
    for t_ in np.linspace(-2.5, 2.5, 11):
        s_ = np.linspace(-2.5, 2.5, 80)
        for ln in (np.c_[s_, np.full_like(s_, t_)], np.c_[np.full_like(s_, t_), s_]): q_ = f(ln); ax.plot(q_[:, 0], q_[:, 1], color="#cbd5e1", lw=.8)
    q_ = f(zz[:500]); ax.scatter(q_[:, 0], q_[:, 1], s=4, color=GREY, alpha=.5); ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal"); ax.set_title(title, fontsize=10); ax.set_xticks([]); ax.set_yticks([])
fig, axs = plt.subplots(1, 3, figsize=(12, 3.6))
gridpanel(axs[0], lambda q: q, 3.2, "hidden numbers z"); gridpanel(axs[1], lambda q: rot(obs2(q)), 4, "after the bend (the points)"); gridpanel(axs[2], lambda q: (rot(obs2(q)) - mu_) @ W_, 3.2, "after whitening")
fig_bendvis = img(fig)
fig, axs = plt.subplots(1, 2, figsize=(10, 3.3)); ideal = [2, 2, 2, 2, 0, 0, 0, 0]; real = [1.998, 1.977, 1.955, 1.938, .527, .465, .414, .397]
for ax, vals, t_ in ((axs[0], ideal, "exact pairs, no bend: sizes 2 and 0"), (axs[1], real, "measured, bend strength 2: sizes ≈ 1.95 and ≈ 0.45")):
    ax.bar(range(1, 9), vals, color=[RED] * 4 + [BLUE] * 4); ax.set_xticks(range(1, 9)); ax.set_xlabel("axis number (sorted by size)"); ax.set_ylabel("size of the spread"); ax.set_title(t_, fontsize=10); ax.set_ylim(0, 2.4)
fig_eig = img(fig, "85%")

# ---------- robot: four ways of splitting, camera-change (viewpoint) ratio
import json as _j
pb = lambda t, k: _j.load(open(f"results/paper_baseline/{t}_paper_fixed_slice.json"))[k]
lf = lambda n, t: _j.load(open(f"results/paper_baseline/{n}/{t}/split0.json"))["ratios"]["P1_view_V1_over_Q1"]
old = lambda arm, t: np.mean([_j.load(open(f))["ratios"]["P1_view_V1_over_Q1"] for f in sorted(glob.glob(f"results/stage_r/{arm}/{t}/split*.json"))])
rows_r = [("frozen image features\n+ small head", [old("baseline", "PickCube"), old("baseline", "PushCube")], GREY),
          ("paper's method (trained\nencoder, fixed halves)", [pb("PickCube", "paper_ratio_view_L_over_H"), pb("PushCube", "paper_ratio_view_L_over_H")], BLUE),
          ("iterated splitting on the\npaper-trained embedding", [lf("ladder_fixed", "PickCube"), lf("ladder_fixed", "PushCube")], RED)]
fig, ax = plt.subplots(figsize=(8.5, 3.6)); w = .26
for i, (lab, v, col) in enumerate(rows_r):
    ax.bar(np.arange(2) + (i - 1) * w, v, w, color=col, label=lab)
    for j, y in enumerate(v): ax.text(j + (i - 1) * w, y + .15, f"{y:.1f}", ha="center", fontsize=9)
ax.set_xticks([0, 1]); ax.set_xticklabels(["PickCube", "PushCube"]); ax.set_ylabel("viewpoint ratio (bigger = blocks separate)"); ax.set_ylim(0, 16); ax.legend(frameon=False, fontsize=8.5, ncol=3, loc="upper center", bbox_to_anchor=(.5, -.12))
fig_rob = img(fig, "80%")

# ---------- deeper ladders (E61) and nameable factors (E62)
dl = json.load(open("results/deep_ladder.json")); sd = json.load(open("results/simple_depth.json"))
sets = [("6 rungs", [(r["angle"], r["gap"]) for r in sd], GREY), ("8 rungs", [(r["angle"], r["gap"]) for r in dl if r["rungs"] == 8], BLUE), ("10 rungs", [(r["angle"], r["gap"]) for r in dl if r["rungs"] == 10], RED)]
fig, axs = plt.subplots(1, 2, figsize=(10, 3.4))
for lab, runs, col in sets:
    A = np.array([r[0] for r in runs]); G = np.array([r[1] for r in runs]); x = np.arange(1, A.shape[1] + 1)
    axs[0].plot(x, A.mean(0), "-o", color=col, ms=4, label=lab); axs[0].fill_between(x, A.min(0), A.max(0), color=col, alpha=.15)
    axs[1].plot(x, G.mean(0), "-o", color=col, ms=4, label=lab)
axs[0].set_xlabel("rung"); axs[0].set_ylabel("angle to true layer (degrees)"); axs[0].set_title("Error grows slowly and levels off", fontsize=10.5); axs[0].set_ylim(0, 5); axs[0].legend(frameon=False)
axs[1].set_xlabel("rung"); axs[1].set_ylabel("gap"); axs[1].set_yscale("log"); axs[1].set_ylim(10, 300); axs[1].set_title("Every cut stays sharp", fontsize=10.5)
fig_deep = img(fig, "88%")
fig_e62 = '<img src="data:image/png;base64,' + base64.b64encode(open("docs/img/e62_ladder.png", "rb").read()).decode() + '" style="width:100%">'

# ---------- layers in each experiment
fig, ax = plt.subplots(figsize=(11, 4.2)); ax.set_xlim(0, 11); ax.set_ylim(0, 4.2); ax.axis("off")
rows_l = [("Synthetic worlds", [f"layer {i}" for i in range(1, 8)], "4 hidden numbers each; speeds 0.2 … 0.95"),
          ("Robot images", ["camera", "trajectory", "progress", "layout"], "what the pairs hold fixed or vary"),
          ("Scene factors", ["gripper", "arm pose", "cube yaw", "cube pos.", "cube colour", "light tint", "brightness", "cam. dist/elev", "cam. azimuth"], "named factors set in the simulator")]
cols_l = ["#c2410c", "#ea580c", "#ca8a04", "#15803d", "#0e7490", "#1d4ed8", "#7c3aed", "#a21caf", "#64748b"]
for r, (name, items, note) in enumerate(rows_l):
    y = 3.0 - r * 1.35; ax.text(0.0, y + 0.95, name, fontsize=10.5, fontweight="bold"); ax.text(3.0, y + 0.95, note, fontsize=8.5, color="#64748b")
    w = 10.6 / len(items)
    for i, it in enumerate(items):
        ax.add_patch(FancyBboxPatch((i * w + 0.03, y), w - 0.1, 0.7, boxstyle="round,pad=0.02", fc=cols_l[i % 9] if len(items) > 4 or r == 0 else cols_l[i * 2], ec="white")); ax.text(i * w + w / 2 - 0.03, y + 0.35, it, ha="center", va="center", color="white", fontsize=8.3 if len(items) > 7 else 9)
ax.annotate("", (10.8, 0.1), (0.1, 0.1), arrowprops=dict(arrowstyle="-|>", lw=1.4, color="#334155")); ax.text(0.1, -0.2, "fastest (cut first)", fontsize=9); ax.text(10.8, -0.2, "slowest (left over)", fontsize=9, ha="right")
fig_layers = img(fig, "100%")

import base64 as _b
fig_flow_gif = '<img class="screen-only" src="data:image/gif;base64,' + _b.b64encode(open("docs/img/video_sieve_flow.gif", "rb").read()).decode() + '" style="width:100%">'
fig_flow_strip = '<img class="print-only" src="data:image/png;base64,' + _b.b64encode(open("docs/img/video_sieve_flow_strip.png", "rb").read()).decode() + '" style="width:100%">'

_png = lambda f, w="100%": '<img src="data:image/png;base64,' + _b.b64encode(open(f, "rb").read()).decode() + f'" style="width:{w}">'
fig_geo = '<img class="screen-only" src="data:image/gif;base64,' + _b.b64encode(open("docs/img/geometry_ladder.gif", "rb").read()).decode() + '" style="width:62%">' + '<img class="print-only" src="data:image/png;base64,' + _b.b64encode(open("docs/img/geometry_ladder_still.png", "rb").read()).decode() + '" style="width:62%">'
extra = {"FIG_HERO": _png("docs/img/hero_summary.png"), "FIG_GEO": fig_geo, "FIG_PAIRKNOB": _png("docs/img/pair_changes_layer.png"), "FIG_PEEL": _png("docs/img/peel_motion.png"), "FIG_TANGLE": _png("docs/img/messy_to_blocks.png", "78%")}
html = open("experiments/full_report_template.html").read()
for k, v in {"FIG_MECH": fig_mech, "FIG_SPEED": fig_speed, "FIG_BENDVIS": fig_bendvis, "FIG_EIG": fig_eig, "FIG_LADDER": fig_ladder, "FIG_BASE": fig_base, "FIG_RES": fig_res, "ROWS6": rows6, "FIG_BEND": fig_bend, "FIG_EQ": fig_eq, "SING": sing_rng, "LADMAX": lad_max, "FIG_PAIRS": fig_pairs, "FIG_ROB": fig_rob, "FIG_DEEP": fig_deep, "FIG_LAYERS": fig_layers, "FIG_FLOW": fig_flow_gif + fig_flow_strip, **extra, "FIG_E62": fig_e62}.items(): html = html.replace("{{" + k + "}}", v)
open("docs/report/FULL.html", "w").write(html); print("ok")
