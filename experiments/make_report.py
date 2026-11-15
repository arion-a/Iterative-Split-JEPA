"""Builds docs/report/REPORT.html (+ figures) from the real code on ONE example world: 3 layers x 2 numbers = 6 numbers per sample."""
import base64, io, numpy as np, torch, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from isj.worlds import BlockWorld, CouplingMap
from isj.engine import fit_whitener, fit_rung
torch.manual_seed(1)
world = BlockWorld([2, 2, 2], [0.2, 0.6, 0.95], seed=11)           # layer A (fast), B (middle), C (slow); 2 numbers each
obs = CouplingMap(6, 4, 1.0, None, seed=11)
n = 4000
z = world.sample(n); x = obs(z)
wh = fit_whitener(obs(world.sample(40000)), 1e-5); r = wh(x)
names = ["A1", "A2", "B1", "B2", "C1", "C2"]
RED, BLUE, GRN, GREY, ORG = "#c2410c", "#1d4ed8", "#15803d", "#64748b", "#ea580c"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False, "font.size": 11})
def img(fig, w=None):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=170, bbox_inches="tight", facecolor="white"); plt.close(fig)
    return f'<img src="data:image/png;base64,{base64.b64encode(b.getvalue()).decode()}" style="width:{w or "100%"}">'
# ---------------- pairs and fits
u1, v1 = world.correspondence_pairs(30000, 1); ru1, rv1 = wh(obs(u1)), wh(obs(v1))
f1 = fit_rung(ru1, rv1, torch.eye(6), k=1, d_k=2)
u2, v2 = world.correspondence_pairs(30000, 2); ru2, rv2 = wh(obs(u2)), wh(obs(v2))
f2 = fit_rung(ru2, rv2, f1.Q, k=2, d_k=2)
Rn = r.numpy(); Zn = z.numpy()
# ---------------- figure: speeds over time (same rule as the world's transition)
g = np.random.default_rng(2); T = 40; rho = [0.2, 0.6, 0.95]; ts = np.zeros((T, 3)); ts[0] = g.standard_normal(3)
for t in range(1, T): ts[t] = [rho[i] * ts[t - 1, i] + np.sqrt(1 - rho[i] ** 2) * g.standard_normal() for i in range(3)]
fig, ax = plt.subplots(figsize=(8, 2.6))
for i, (lab, col) in enumerate((("A  fast (keep 20%)", RED), ("B  middle (keep 60%)", ORG), ("C  slow (keep 95%)", BLUE))): ax.plot(ts[:, i], color=col, lw=2, label=lab)
ax.set_xlabel("time step (video frame)"); ax.set_ylabel("one hidden number"); ax.legend(ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(.5, 1.25)); fig_speed = img(fig)
# ---------------- figure: mixing (hidden numbers vs embedding coordinates, before whitening)
corr = np.corrcoef(np.c_[Zn, x.numpy()].T)[:6, 6:]
fig, axs = plt.subplots(1, 2, figsize=(9, 3.6))
for ax, M, t in ((axs[0], np.eye(6), "Hidden number → itself (ideal)"), (axs[1], corr, "Hidden number → embedding coordinate (real)")):
    im = ax.imshow(np.abs(M), cmap="Blues", vmin=0, vmax=1); ax.set_xticks(range(6)); ax.set_xticklabels([f"e{i+1}" for i in range(6)]); ax.set_yticks(range(6)); ax.set_yticklabels(names); ax.set_title(t, fontsize=10)
    ax.spines[:].set_visible(False)
fig.colorbar(im, ax=axs, shrink=.8, label="how strongly they move together (0 to 1)"); fig_mix = img(fig)
# ---------------- figure: covariance before / after whitening, and a 2D look
c_before = np.cov(x.numpy().T); c_after = np.cov(Rn.T)
fig, axs = plt.subplots(1, 4, figsize=(13, 3.3))
for ax, M, t in ((axs[0], c_before, "spread table BEFORE whitening"), (axs[1], c_after, "spread table AFTER whitening")):
    im = ax.imshow(M, cmap="RdBu_r", vmin=-2, vmax=2); ax.set_title(t, fontsize=9); ax.set_xticks(range(6)); ax.set_yticks(range(6)); ax.set_xticklabels([f"e{i+1}" for i in range(6)], fontsize=8); ax.set_yticklabels([f"e{i+1}" for i in range(6)], fontsize=8)
X0 = x.numpy()
axs[2].scatter(X0[:, 0], X0[:, 1], s=3, color=GREY, alpha=.5); axs[2].set_title("two coordinates BEFORE:\nstretched and tilted", fontsize=9); axs[2].set_aspect("equal")
axs[3].scatter(Rn[:, 0], Rn[:, 1], s=3, color=BLUE, alpha=.5); axs[3].set_title("the same two AFTER:\nround, same spread everywhere", fontsize=9); axs[3].set_aspect("equal")
fig_white = img(fig)
# ---------------- figure: eigen picture for rung 1 (differences oval in 2 coordinates + spread table + eigenvalues)
D1 = (ru1 - rv1).numpy(); M1 = D1.T @ D1 / len(D1); ev1, E1 = np.linalg.eigh(M1); ev1, E1 = ev1[::-1], E1[:, ::-1]
fig, axs = plt.subplots(1, 3, figsize=(13, 3.6))
im = axs[0].imshow(M1, cmap="RdBu_r", vmin=-2, vmax=2); axs[0].set_title("spread table of the differences\n(rung 1)", fontsize=10); axs[0].set_xticks(range(6)); axs[0].set_yticks(range(6)); axs[0].set_xticklabels([f"e{i+1}" for i in range(6)], fontsize=8); axs[0].set_yticklabels([f"e{i+1}" for i in range(6)], fontsize=8)
p = D1 @ E1[:, :2]; axs[1].scatter(p[:1500, 0], p[:1500, 1], s=3, color=RED, alpha=.5); axs[1].set_title("the differences, seen along the two\nlongest axes found", fontsize=10); axs[1].set_aspect("equal")
q = D1 @ E1[:, [2, 3]]; axs[1].scatter(q[:1500, 0], q[:1500, 1], s=3, color=BLUE, alpha=.5)
axs[2].bar(range(1, 7), ev1, color=[RED] * 2 + [BLUE] * 4); axs[2].set_xlabel("axis number (sorted by size)"); axs[2].set_ylabel("how much the differences spread"); axs[2].set_title(f"2 big axes, 4 much smaller\n(gap {ev1[1]/ev1[2]:.0f} : 1)", fontsize=10)
fig_eig1 = img(fig)
# ---------------- figure: flow of dimensions
fig, ax = plt.subplots(figsize=(10, 3.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4.2)
u = 10 / 6
def bar(x0, w, y, col, txt):
    ax.add_patch(FancyBboxPatch((x0, y), w, .6, boxstyle="round,pad=0.02", fc=col, ec="none")); ax.text(x0 + w / 2, y + .3, txt, ha="center", va="center", color="white", fontsize=10, weight="bold")
ax.text(0, 3.85, "Start: all 6 directions of the embedding", fontsize=10.5, weight="bold", va="center"); bar(0, 10, 3.0, GREY, "6 directions")
ax.text(0, 2.55, "After rung 1: split off A, keep the rest", fontsize=10.5, weight="bold", va="center"); bar(0, 2 * u, 1.7, RED, "A block: 2"); bar(2 * u, 4 * u, 1.7, BLUE, "kept: 4 directions that did NOT change")
ax.text(2 * u, 1.25, "After rung 2 (works only inside the kept 4): split off B, what is left is C", fontsize=10.5, weight="bold", va="center"); bar(2 * u, 2 * u, .4, ORG, "B block: 2"); bar(4 * u, 2 * u, .4, GRN, "left over = C: 2")
fig_flow = img(fig)
# ---------------- figure: rung 2 differences inside the kept 4 directions
Dk = ((ru2 - rv2) @ f1.Q).numpy(); M2 = Dk.T @ Dk / len(Dk); ev2, E2 = np.linalg.eigh(M2); ev2, E2 = ev2[::-1], E2[:, ::-1]
fig, axs = plt.subplots(1, 2, figsize=(10, 3.3))
im = axs[0].imshow(M2, cmap="RdBu_r", vmin=-2, vmax=2); axs[0].set_title("spread table of rung-2 differences\n(only the 4 kept directions)", fontsize=10); axs[0].set_xticks(range(4)); axs[0].set_yticks(range(4))
axs[1].bar(range(1, 5), ev2, color=[ORG] * 2 + [GRN] * 2); axs[1].set_xlabel("axis number"); axs[1].set_ylabel("spread"); axs[1].set_title(f"2 big axes (B), 2 small (C stayed the same)\ngap {ev2[1]/ev2[2]:.0f} : 1", fontsize=10); fig_eig2 = img(fig)
# ---------------- figure: check against truth: how well can each TRUE layer be predicted from each FOUND block
def r2(coord, target):
    X = np.c_[coord, np.ones(len(coord))]; W = np.linalg.lstsq(X, target, rcond=None)[0]; res = ((target - X @ W) ** 2).sum(0); tot = ((target - target.mean(0)) ** 2).sum(0); return float((1 - res / tot).mean())
blocks = {"found by rung 1": Rn @ f1.V.numpy(), "found by rung 2": Rn @ f2.V.numpy(), "left over": Rn @ f2.Q.numpy()}
true = {"A (fast)": Zn[:, 0:2], "B (middle)": Zn[:, 2:4], "C (slow)": Zn[:, 4:6]}
T3 = np.array([[r2(c, t) for t in true.values()] for c in blocks.values()])
fig, ax = plt.subplots(figsize=(6.2, 3.3)); im = ax.imshow(T3, cmap="Greens", vmin=0, vmax=1)
ax.set_xticks(range(3)); ax.set_xticklabels(true.keys()); ax.set_yticks(range(3)); ax.set_yticklabels(blocks.keys()); ax.xaxis.tick_top()
for i in range(3):
    for j in range(3): ax.text(j, i, f"{T3[i,j]:.2f}", ha="center", va="center", color="white" if T3[i, j] > .5 else "#334155", fontsize=12, weight="bold")
ax.spines[:].set_visible(False); fig_truth = img(fig, "70%")
# ---------------- tables of example rows
fmt = lambda v: f"{v:+.2f}"
def rowtab(rows, labels, cls):
    h = "<table class='nums'><tr><th></th>" + "".join(f"<th class='{'a' if i<2 else 'b' if i<4 else 'c'}'>{nm}</th>" for i, nm in enumerate(names)) + "</tr>"
    for lab, row, cl in zip(labels, rows, cls): h += f"<tr><td class='lab'>{lab}</td>" + "".join(f"<td class='{c}'>{fmt(v)}</td>" for v, c in zip(row, cl)) + "</tr>"
    return h + "</table>"
torch.manual_seed(7); ua, va = world.correspondence_pairs(1, 1); ub, vb = world.correspondence_pairs(1, 2)
ua, va, ub, vb = [t[0].numpy() for t in (ua, va, ub, vb)]
same, diff, neutral = "same", "diff", ""
t_pair1 = rowtab([ua, va, va - ua], ["sample 1", "its partner", "difference"], [[neutral] * 6, [diff] * 2 + [same] * 4, [diff] * 2 + [same] * 4])
t_pair2 = rowtab([ub, vb, vb - ub], ["sample 1", "its partner", "difference"], [[neutral] * 6, [diff] * 4 + [same] * 2, [diff] * 4 + [same] * 2])
zs = z[:3].numpy(); xs = x[:3].numpy(); rs = r[:3].numpy()
t_hidden = rowtab(zs, ["sample 1", "sample 2", "sample 3"], [[neutral] * 6] * 3)
t_after = "<table class='nums'><tr><th></th>" + "".join(f"<th>e{i+1}</th>" for i in range(6)) + "</tr>" + "".join(f"<tr><td class='lab'>sample {i+1}</td>" + "".join(f"<td>{fmt(v)}</td>" for v in rs[i]) + "</tr>" for i in range(3)) + "</table>"

# ---------------- the bend written out: worked example, straight-line version, weights
torch.manual_seed(1); z1s = world.sample(1); xs_ = z1s.clone(); steps = [("start (hidden numbers)", xs_[0].numpy().copy())]
for i, w in enumerate(obs.weights):
    L_, R_ = xs_[:, :3], xs_[:, 3:]
    if i % 2 == 0: R_ = R_ + torch.tanh(L_ @ w)
    else: L_ = L_ + torch.tanh(R_ @ w)
    xs_ = torch.cat([L_, R_], 1); steps.append((f"after step {i+1}", xs_[0].numpy().copy()))
assert torch.allclose(xs_, obs(z1s))
t_steps = "<table class='nums'><tr><th></th>" + "".join(f"<th>e{i+1}</th>" for i in range(6)) + "</tr>" + "".join(f"<tr><td class='lab'>{nm}</td>" + "".join(f"<td>{fmt(v)}</td>" for v in vals) + "</tr>" for nm, vals in steps) + "</table>"
zz_ = world.sample(20000); xx_ = obs(zz_).numpy(); Zq = zz_.numpy(); Aq = np.linalg.lstsq(np.c_[Zq, np.ones(len(Zq))], xx_, rcond=None)[0][:-1].T
t_A = "<table class='nums'><tr><th></th>" + "".join(f"<th class='{'a' if i<2 else 'b' if i<4 else 'c'}'>{nm}</th>" for i, nm in enumerate(names)) + "</tr>" + "".join(f"<tr><td class='lab'>e{r_+1}</td>" + "".join(f"<td style='background:rgba(29,78,216,{min(abs(v)/1.7,1)*.55:.2f})'>{v:+.2f}</td>" for v in Aq[r_]) + "</tr>" for r_ in range(6)) + "</table>"
def wtab(w): return "<table class='nums' style='display:inline-table;margin:4px 10px 4px 0'>" + "".join("<tr>" + "".join(f"<td>{v:+.2f}</td>" for v in row) + "</tr>" for row in w.numpy()) + "</table>"
t_W = "".join(f"<div style='display:inline-block;vertical-align:top'><div class='cap'>W{i+1} (step {i+1})</div>{wtab(w)}</div>" for i, w in enumerate(obs.weights))
t4_term = float(np.tanh(z1s[0, :3].numpy() @ obs.weights[0].numpy()[:, 0]))
w0c = obs.weights[0].numpy()[:, 0]


# ---------------- hand check: exact noise-free toy, hand answers vs the real fit_rung
q = 1 / np.sqrt(2); Qm = torch.tensor([[q, q, 0], [q, -q, 0], [0, 0, 1.0]], dtype=torch.float32)           # r = Q z: orthogonal, so the embedding is already "whitened"
da = np.array([2.0, -2.0, 1.0, -1.0]); db = np.array([3.0, -3.0, 1.0, -1.0]); da2 = np.array([1.0, -2.0, 3.0, 0.5])
base = np.zeros((4, 3))
u1h = torch.tensor(base, dtype=torch.float32); v1h = torch.tensor(np.c_[da, 0 * da, 0 * da], dtype=torch.float32)
h1 = fit_rung(u1h @ Qm.T, v1h @ Qm.T, torch.eye(3), k=1, d_k=1)
u2h = torch.tensor(base, dtype=torch.float32); v2h = torch.tensor(np.c_[da2, db, 0 * da], dtype=torch.float32)
h2 = fit_rung(u2h @ Qm.T, v2h @ Qm.T, h1.Q, k=2, d_k=1)
vec = lambda t: "(" + ", ".join(f"{abs(v):.3f}" if abs(v) < 1e-6 else f"{v:+.3f}" for v in t) + ")"
hand = {"H_EV1": ", ".join(f"{v:.2f}" for v in h1.eigvals.numpy()), "H_V1": vec(h1.V.numpy()[:, 0] * np.sign(h1.V.numpy()[0, 0])), "H_EV2": ", ".join(f"{v:.2f}" for v in h2.eigvals.numpy()),
        "H_V2": vec(h2.V.numpy()[:, 0] * np.sign(h2.V.numpy()[0, 0])), "H_CORE": vec(h2.Q.numpy()[:, 0] * np.sign(h2.Q.numpy()[2, 0]))}



# ---------------- pipeline-at-a-glance figure with the formulas
fig, ax = plt.subplots(figsize=(13, 5.2)); ax.axis("off"); ax.set_xlim(0, 13); ax.set_ylim(0, 5.2)
def box(x0, y0, w, h, col, head, body, tc="white"):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0.03", fc=col, ec="none")); ax.text(x0 + w / 2, y0 + h - .28, head, ha="center", va="center", color=tc, fontsize=10.5, weight="bold"); ax.text(x0 + w / 2, y0 + (h - .5) / 2, body, ha="center", va="center", color=tc, fontsize=8.6, linespacing=1.5)
arr = lambda x0, y0, x1, y1: ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color="#475569", lw=1.8))
box(.1, 3.2, 2.9, 1.8, "#475569", "1  Hidden numbers z", "layers A, B, C\n(groups of numbers,\nfast to slow)\nthe method never sees z")
box(3.5, 3.2, 3.1, 1.8, "#7c3aed", "2  Bend  e = f(z)", "4 steps, e.g.\nright = right + tanh(left × W1)\nleft = left + tanh(right × W2) …")
box(7.0, 3.2, 2.7, 1.8, "#0f766e", "3  Whiten", "r = C^(-1/2) (e − mean)\nC = spread table (covariance)\nof all dots")
box(10.1, 3.2, 2.8, 1.8, "#1d4ed8", "4  Matched pairs", "two samples that agree\non all layers slower\nthan the one asked about")
arr(3.0, 4.1, 3.5, 4.1); arr(6.6, 4.1, 7.0, 4.1); arr(9.7, 4.1, 10.1, 4.1)
box(10.1, .2, 2.8, 2.5, "#c2410c", "5  Differences", "D = r(u) − r(v)\nfor every pair\nspread table of the D's:\nM = average of D × Dᵀ")
box(6.9, .2, 2.9, 2.5, "#b45309", "6  Long axes", "M = Σ λᵢ vᵢ vᵢᵀ\n(eigendecomposition)\ntop d eigenvectors = block V\ngap = λd / λ(d+1)")
box(3.5, .2, 3.1, 2.5, "#15803d", "7  Cut and repeat", "V = layer found\nH = directions left (unchanged)\nnext rung: pairs for the next\nlayer, work only inside H")
box(.1, .2, 2.9, 2.5, "#334155", "8  Check (tests only)", "angle between V and the\ntrue layer's directions;\nhidden numbers used only\nhere, for scoring")
arr(11.5, 3.2, 11.5, 2.7); arr(10.1, 1.45, 9.8, 1.45); arr(6.9, 1.45, 6.6, 1.45); arr(3.5, 1.45, 3.0, 1.45)
fig_pipe = img(fig)

# ================= real results figures =================
import glob, json
def load(pat): return [json.load(open(f)) for f in sorted(glob.glob(pat))]
worst = lambda rs: [max(g["angle_deg"] for g in r["rungs"]) for r in rs]
RUN = {"u": load, "t": load}
fig, ax = plt.subplots(figsize=(10, 4.4))
series = [("untrained encoder, gate on", GREY, -.22, {s_: worst(load(f"results/minimal/e55/u/s{s_}/main_seed*.json")) for s_ in (1, 2, 4, 8)}),
          ("trained encoder, gate on", RED, 0.0, {0.5: worst(load("results/minimal/e54/d4/main_seed*.json")), **{s_: worst(load(f"results/minimal/e55/t/s{s_}/main_seed*.json")) for s_ in (1, 2, 4, 8)}}),
          ("trained encoder, gate off", GRN, .22, {2: worst(load("results/minimal/e56/main_seed*.json")), 4: worst(load("results/minimal/e57/b4_s4/main_seed*.json"))})]
pos = {0.5: 0, 1: 1, 2: 2, 4: 3, 8: 4}
for lab, col, off, d in series:
    for k_, v in d.items():
        ax.scatter(np.full(len(v), pos[k_] + off) + np.random.default_rng(0).uniform(-.04, .04, len(v)), v, s=22, color=col, alpha=.8, label=lab if k_ == list(d)[0] else None)
        ax.plot([pos[k_] + off - .08, pos[k_] + off + .08], [np.median(v)] * 2, color="k", lw=2)
ax.axhline(80, color="#94a3b8", ls="--"); ax.text(4.45, 81.5, "unrelated ≈ 80°", ha="right", color="#64748b", fontsize=9); ax.axhline(5, color="#16a34a", ls=":"); ax.text(-.45, 6.3, "clean < 5°", color="#16a34a", fontsize=9)
ax.set_xticks(range(5)); ax.set_xticklabels(["0.5", "1", "2", "4", "8"]); ax.set_xlabel("how hard the bend is (coupling strength)"); ax.set_ylabel("worst-rung angle to the truth (degrees)"); ax.set_ylim(0, 92); ax.legend(frameon=False, loc="center left", fontsize=9)
ax.set_title("Result 1: found blocks vs the truth as the bend gets stronger (each dot = one run, 4 layers; black = median)", fontsize=10.5); fig_r1 = img(fig)
# per rung angle + gap for two cells
def cell(ax_a, ax_g, rs, ttl, col):
    nr = len(rs[0]["rungs"])
    for r in rs:
        ax_a.plot(range(1, nr + 1), [g["angle_deg"] for g in r["rungs"]], "-o", color=col, alpha=.6, ms=4); ax_g.plot(range(1, nr + 1), [g["gap_ratio"] for g in r["rungs"]], "-o", color=col, alpha=.6, ms=4)
    ax_a.axhline(5, color="#16a34a", ls=":"); ax_a.axhline(80, color="#94a3b8", ls="--"); ax_a.set_ylim(0, 90); ax_a.set_title(ttl, fontsize=10); ax_a.set_xlabel("rung"); ax_a.set_xticks(range(1, nr + 1))
    ax_g.axhline(10, color="#16a34a", ls=":"); ax_g.axhline(1, color="#94a3b8", ls="--"); ax_g.set_yscale("log"); ax_g.set_xlabel("rung"); ax_g.set_xticks(range(1, nr + 1))
fig, axs = plt.subplots(2, 3, figsize=(12.5, 6.4)); axs[0, 0].set_ylabel("angle (degrees)"); axs[1, 0].set_ylabel("gap (log scale)")
cell(axs[0, 0], axs[1, 0], load("results/minimal/e54/d5/main_seed*.json"), "5 layers, mild bend (E54)", BLUE)
cell(axs[0, 1], axs[1, 1], load("results/minimal/e57/b5_s2/main_seed*.json"), "5 layers, strength 2, gate off (E57)", ORG)
cell(axs[0, 2], axs[1, 2], load("results/minimal/e57/b4_s4/main_seed*.json"), "4 layers, strength 4, gate off (E57)", RED)
fig.suptitle("Result 2: every rung, every run. Top: angle (green dotted = clean, grey dashed = unrelated). Bottom: gap (green dotted = 10, grey = no block)", fontsize=10.5); fig.tight_layout(rect=(0, 0, 1, .95)); fig_r2 = img(fig)
# E38 equal speeds
e38 = load("results/minimal/e38/main_seed*.json"); lad = np.array([r["payoff"]["ladder_angles_deg"] for r in e38]); sing = np.array([r["payoff"]["single_shot_angles_deg"] for r in e38])
fig, ax = plt.subplots(figsize=(7.5, 3.6)); xs = np.arange(lad.shape[1]); w = .35
for j in range(len(e38)): ax.scatter(xs - w / 2 + np.random.default_rng(j).uniform(-.06, .06), lad[j], color=GRN, s=26); ax.scatter(xs + w / 2 + np.random.default_rng(j + 9).uniform(-.06, .06), sing[j], color=RED, s=26)
ax.scatter([], [], color=GRN, label="ladder (uses matched pairs)"); ax.scatter([], [], color=RED, label="one-shot split of adjacent-frame differences (no pairs)")
ax.set_xticks(xs); ax.set_xticklabels([f"rung {i+1}" for i in xs]); ax.set_ylabel("angle to the truth (degrees)"); ax.set_ylim(0, 95); ax.legend(frameon=False, fontsize=9, loc="center right")
ax.set_title("Result 3: all layers change at the same speed (E38, 5 runs)", fontsize=10.5); fig_r3 = img(fig, "75%")
# E58 cluster pairs
e58 = load("results/minimal/e58/seed*.json"); arms = [("generator", "exact twins", GRN), ("label", "perfect clusters", BLUE), ("kmeans_slow", "clusters from data (slow part)", ORG), ("kmeans_all", "clusters from data (whole)", RED), ("random", "random pairs", GREY)]
fig, ax = plt.subplots(figsize=(8.5, 3.9))
for key, lab, col in arms:
    m = np.array([[x["angle_deg"] for x in r["arms"][key]] for r in e58]); ax.plot(range(1, 6), np.median(m, 0), "-o", color=col, label=lab, lw=2)
ax.axhline(80, color="#94a3b8", ls="--"); ax.set_xticks(range(1, 6)); ax.set_xlabel("rung"); ax.set_ylabel("angle to the truth (degrees)"); ax.set_ylim(0, 92); ax.legend(frameon=False, fontsize=8.5, ncol=3, loc="upper center", bbox_to_anchor=(.5, -.2))
ax.set_title("Result 4: pairs built from the data itself (E58; median of 5 runs; best case: true cluster counts given)", fontsize=10); fig_r4 = img(fig)
# robot
rows = [l.split("|") for l in open("results/stage_r/STAGE_R_REPORT.md") if l.startswith("| Push") or l.startswith("| Pick") or l.startswith("| Stack") or "treated" in l or "baseline" in l]
vals = [(r[1].strip(), r[2].strip(), float(r[8])) for r in rows if len(r) > 10 and r[8].strip().replace(".", "").isdigit()]
fig, ax = plt.subplots(figsize=(7.5, 3.2)); labs = [t[:4] + chr(10) + ("base" if a == "baseline" else "treat") for t, a, _ in vals]; ax.bar(range(len(vals)), [v for *_, v in vals], color=[RED if a == "treated" else GREY for _, a, _ in vals])
ax.axhline(3, color="#16a34a", ls="--"); ax.text(len(vals) - .5, 2.8, "needed: 3", ha="right", color="#16a34a"); ax.set_xticks(range(len(vals))); ax.set_xticklabels(labs, fontsize=7); ax.set_ylabel("viewpoint-block ratio")
ax.set_title("Result 5: simulated robot images (frozen image features): the block is not separated", fontsize=10.5); fig_r5 = img(fig, "75%")
e54 = load("results/minimal/e54/d*/main_seed*.json"); ang54 = [g["angle_deg"] for r in e54 for g in r["rungs"]]; gap54 = [g["gap_ratio"] for r in e54 for g in r["rungs"]]
sing_rng = f"{sing.min():.0f}–{sing.max():.0f}°"; lad_max = f"{lad.max():.1f}"
r54 = f"{min(ang54):.1f} – {max(ang54):.1f}°, gap {min(gap54):.0f} – {max(gap54):.0f}"

html = open("experiments/report_template.html").read()
for k, v in {"FIG_PIPE": fig_pipe, "FIG_R1": fig_r1, "FIG_R2": fig_r2, "FIG_R3": fig_r3, "FIG_R4": fig_r4, "FIG_R5": fig_r5, "R54": r54, "SING": sing_rng, "LADMAX": lad_max, **hand, "FIG_SPEED": fig_speed, "FIG_MIX": fig_mix, "FIG_WHITE": fig_white, "FIG_EIG1": fig_eig1, "FIG_FLOW": fig_flow, "FIG_EIG2": fig_eig2, "FIG_TRUTH": fig_truth, "T_HIDDEN": t_hidden, "T_AFTER": t_after, "T_PAIR1": t_pair1, "T_PAIR2": t_pair2,
             "EV1": ", ".join(f"{v:.2f}" for v in ev1), "EV2": ", ".join(f"{v:.2f}" for v in ev2), "GAP1": f"{ev1[1]/ev1[2]:.0f}", "GAP2": f"{ev2[1]/ev2[2]:.0f}", "T_STEPS": t_steps, "T_A": t_A, "T_W": t_W, "Z1": ", ".join(f"{v:+.2f}" for v in z1s[0].numpy()), "W0C": ", ".join(f"{v:+.2f}" for v in w0c), "ARG": f"{float(z1s[0,:3].numpy() @ w0c):.2f}", "TH": f"{t4_term:.2f}", "B2": f"{float(z1s[0,3]):+.2f}", "B2NEW": f"{float(z1s[0,3])+t4_term:+.2f}", "R2_AA": f"{T3[0,0]:.2f}", "R2_BB": f"{T3[1,1]:.2f}", "R2_CC": f"{T3[2,2]:.2f}"}.items(): html = html.replace("{{" + k + "}}", v)
open("docs/report/REPORT.html", "w").write(html); print("ok", ev1, ev2, T3.round(2))
