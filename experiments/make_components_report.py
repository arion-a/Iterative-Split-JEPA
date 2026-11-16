"""Components report: every component of the experiments, its critical 'trunk', the equations and visual explainers.
    PYTHONPATH=src python experiments/make_components_report.py -> docs/report/COMPONENTS.html (PDF via /tmp/pdf3.js)"""
import base64, io, json, numpy as np, torch, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from isj.worlds import BlockWorld, CouplingMap
from isj.engine import fit_whitener, fit_rung
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False, "font.size": 10.5})
RED, BLUE, GREY, GRN, ORG, PAP = "#c2410c", "#1d4ed8", "#64748b", "#15803d", "#ea580c", "#f4c27a"
def img(fig, w="100%"):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=165, bbox_inches="tight", facecolor="white"); plt.close(fig); return f'<img src="data:image/png;base64,{base64.b64encode(b.getvalue()).decode()}" style="width:{w}">'
torch.manual_seed(0); rng = np.random.default_rng(1)
# 1 speeds
fig, ax = plt.subplots(figsize=(8.6, 2.5))
for rho, c in ((0.2, RED), (0.7, ORG), (0.95, BLUE)):
    z = [0.0]
    for _ in range(80): z.append(rho * z[-1] + np.sqrt(1 - rho ** 2) * rng.standard_normal())
    ax.plot(z, color=c, label=f"ρ = {rho}  ({'fast' if rho < .5 else 'medium' if rho < .9 else 'slow'})")
ax.set_xlabel("frame"); ax.set_ylabel("one hidden number"); ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(.5, 1.28)); F_SPEED = img(fig, "82%")
# 2 bend grid
cm = CouplingMap(2, 4, 1.3, None, seed=3); g = np.linspace(-2, 2, 9); fig, axs = plt.subplots(1, 2, figsize=(8.2, 3.6))
for ax, f, t in ((axs[0], lambda p: p, "hidden numbers (a grid)"), (axs[1], lambda p: cm(torch.tensor(p, dtype=torch.float32)).numpy(), "after the 4 bend steps")):
    for v in g:
        l = np.stack([np.linspace(-2, 2, 60), np.full(60, v)], 1); m = f(l); ax.plot(m[:, 0], m[:, 1], color=BLUE, lw=1); m = f(l[:, ::-1].copy()); ax.plot(m[:, 0], m[:, 1], color=RED, lw=1)
    ax.set_aspect("equal"); ax.set_title(t, fontsize=10); ax.set_xticks([]); ax.set_yticks([])
F_BEND = img(fig, "80%")
# 3 whitening
A = np.array([[1.6, 0.5], [0.4, 0.5]]); X = rng.standard_normal((600, 2)) @ A.T; C = np.cov(X.T); w, V = np.linalg.eigh(C); Wm = V @ np.diag(w ** -.5) @ V.T; Y = (X - X.mean(0)) @ Wm
fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.3))
for ax, P, t in ((axs[0], X, "points: stretched, tilted"), (axs[1], Y, "whitened: r = C^(−1/2)(e − μ)")):
    ax.scatter(P[:, 0], P[:, 1], s=5, color=GREY, alpha=.6); ax.set_aspect("equal"); ax.set_title(t, fontsize=10); ax.set_xlim(-4.5, 4.5); ax.set_ylim(-4.5, 4.5)
th = np.linspace(0, 2 * np.pi, 100); axs[1].plot(np.cos(th), np.sin(th), color=RED, lw=1.5); F_WHITE = img(fig, "72%")
# 4 pair-sharing matrices
def share(ax, rows, cols, varied, rl, cl, title):
    for i in range(rows):
        for j in range(cols):
            v = varied(i, j); ax.add_patch(Rectangle((j, rows - 1 - i), 1, 1, fc=RED if v else "#bfdbfe", ec="white", lw=1.5)); ax.text(j + .5, rows - .5 - i, "differ" if v else "same", ha="center", va="center", fontsize=8.5, color="white" if v else "#1e3a8a")
    ax.set_xlim(0, cols); ax.set_ylim(0, rows); ax.set_xticks(np.arange(cols) + .5); ax.set_xticklabels(cl, fontsize=8); ax.set_yticks(np.arange(rows) + .5); ax.set_yticklabels(rl[::-1], fontsize=8)
    ax.set_title(title, fontsize=10); ax.spines[:].set_visible(False); ax.tick_params(length=0); ax.xaxis.tick_top()
fig, axs = plt.subplots(2, 1, figsize=(8.6, 7.4), gridspec_kw={"height_ratios": [7, 9]})
share(axs[0], 7, 6, lambda i, j: i <= j, [f"layer {i+1}" + (" (fastest)" if i == 0 else " (slowest)" if i == 6 else "") for i in range(7)], [f"rung {j+1}" for j in range(6)], "Synthetic world: pair for rung k")
share(axs[1], 9, 8, lambda i, j: i <= j, ["gripper", "arm pose", "cube yaw", "cube position", "cube colour", "light tint", "brightness", "camera dist/elev", "camera azimuth"], [f"rung {j+1}" for j in range(8)], "Scene factors: pair for rung k")
fig.tight_layout(h_pad=2.5); F_SHARE = img(fig, "76%")
# 5 pair differences: 2 layers
def two_layer(n=500):
    u = rng.standard_normal((n, 2)); v = u.copy(); v[:, 0] = rng.standard_normal(n); return u, v
u, v = two_layer(150); D = u - v; M = D.T @ D / len(D); lam, vec = np.linalg.eigh(M); lam, vec = lam[::-1], vec[:, ::-1]
fig, axs = plt.subplots(1, 3, figsize=(11, 3.5))
axs[0].scatter(u[:, 0], u[:, 1], s=12, color=BLUE, alpha=.7, label="u"); axs[0].scatter(v[:, 0], v[:, 1], s=12, color=RED, alpha=.7, label="v"); axs[0].set_title("1  matched pairs: share the slow\ncoordinate (y), redraw the fast (x)", fontsize=9.5); axs[0].legend(frameon=False, fontsize=8)
for i in range(40): axs[0].plot([u[i, 0], v[i, 0]], [u[i, 1], v[i, 1]], color=GREY, lw=.7)
axs[1].scatter(D[:, 0], D[:, 1], s=6, color=GREY, alpha=.6); axs[1].set_title("2  differences D = u − v:\nthey spread only along the fast axis", fontsize=9.5)
for l_, ve, c in ((lam[0], vec[:, 0], RED), (lam[1], vec[:, 1], BLUE)): axs[1].annotate("", ve * 2.6, (0, 0), arrowprops=dict(arrowstyle="-|>", color=c, lw=2))
axs[2].bar(["λ1", "λ2"], lam, color=[RED, BLUE]); axs[2].set_title("3  eigenvalues of M = mean(D Dᵀ)\n(ideal: 2 and 0)", fontsize=9.5)
for a in axs[:2]: a.set_aspect("equal"); a.set_xlim(-3.5, 3.5); a.set_ylim(-3.5, 3.5)
fig.tight_layout(); F_DIFF = img(fig, "95%")
# 6 real eigenvalue spectra, 6-rung world
rhos = [0.2, 0.4, 0.55, 0.7, 0.8, 0.9, 0.95]; world = BlockWorld([4] * 7, rhos, seed=250); d = world.d; obs = CouplingMap(d, 4, 0.5, None, seed=250)
wh = fit_whitener(obs(world.sample(30000)), 1e-5); R = lambda z: wh(obs(z)); h = torch.eye(d); specs = []
for k in range(1, 7):
    ru, rv = (R(t) for t in world.correspondence_pairs(30000, k)); f = fit_rung(ru, rv, h, k=k, d_k=4); specs.append((f.eigvals.numpy(), f.gap_ratio)); h = f.Q
fig, axs = plt.subplots(1, 3, figsize=(11, 3.2))
for ax, k in zip(axs, (0, 2, 5)):
    e, gp = specs[k]; ax.bar(range(1, len(e) + 1), e, color=[RED] * 4 + [GREY] * (len(e) - 4)); ax.set_title(f"rung {k+1}: {len(e)} directions, gap = {gp:.0f}", fontsize=10); ax.set_xlabel("direction (sorted by λ)"); ax.axvline(4.5, color="k", lw=.8, ls=":")
axs[0].set_ylabel("eigenvalue λ"); fig.tight_layout(); F_EIG = img(fig, "95%")
# 7 ladder bookkeeping
fig, ax = plt.subplots(figsize=(10, 2.7)); cols = [RED, ORG, "#ca8a04", GRN, BLUE, "#7c3aed"]; x = 0
for k in range(7):
    w_ = 4 if k < 6 else 4
    ax.add_patch(Rectangle((k * 4.4, 0.2), 4, 0.8, fc=cols[k % 6] if k < 6 else "#94a3b8", ec="white")); ax.text(k * 4.4 + 2, 0.6, f"layer {k+1}" if k < 6 else "core (layer 7)", ha="center", va="center", color="white", fontsize=8.5)
for k in range(6): ax.text(k * 4.4 + 2, 1.35, f"rung {k+1}\ncuts here", ha="center", fontsize=8); ax.annotate("", (k * 4.4 + 2, 1.05), (k * 4.4 + 2, 1.25), arrowprops=dict(arrowstyle="-|>", lw=1))
ax.set_xlim(-.3, 31.2); ax.set_ylim(0, 2); ax.axis("off"); ax.text(15, -.1, "28 directions in total: each rung removes 4, inside what is left (28 → 24 → 20 → 16 → 12 → 8 → 4)", ha="center", fontsize=9, color=GREY)
F_LADDER = img(fig, "92%")
# 8 angle schematic
fig, ax = plt.subplots(figsize=(4.6, 3.2)); ang = np.deg2rad(25)
ax.annotate("", (2, 0), (0, 0), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=2.4)); ax.annotate("", (2 * np.cos(ang), 2 * np.sin(ang)), (0, 0), arrowprops=dict(arrowstyle="-|>", color=RED, lw=2.4))
ax.text(2.05, -.12, "true block (hidden-number layer\nseen through the data)", color=BLUE, fontsize=8, va="top"); ax.text(2 * np.cos(ang) + .05, 2 * np.sin(ang) + .05, "found block V", color=RED, fontsize=8.5)
t = np.linspace(0, ang, 30); ax.plot(.7 * np.cos(t), .7 * np.sin(t), color="k", lw=1); ax.text(.8, .14, "θ", fontsize=12); ax.set_xlim(-.2, 3.4); ax.set_ylim(-.8, 1.3); ax.axis("off"); F_ANGLE = img(fig, "48%")
# 9 architectures
fig, ax = plt.subplots(figsize=(12.5, 4.4)); ax.set_xlim(0, 12.5); ax.set_ylim(0, 4.4); ax.axis("off")
def bx(x, y, w, h, c, t, s=8.7): ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03", fc=c, ec="#333")); ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=s)
def ar(x1, y1, x2, y2): ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", lw=1.3))
ax.text(.1, 4.2, "Paper's robot encoder (orange = from the paper)", fontsize=10, fontweight="bold")
bx(.1, 2.5, 1.6, 1.1, "#ddd", "image\n128×128×3"); bx(2.1, 2.5, 2.2, 1.1, PAP, "ResNet-50\n(ImageNet start)"); bx(4.7, 3.1, 1.9, .7, PAP, "invariant head\n(first d_H numbers)"); bx(4.7, 2.3, 1.9, .7, PAP, "variant head\n(rest)")
bx(7.2, 3.15, 2.0, .65, PAP, "invariance: same frame,\ntwo cameras agree"); bx(7.2, 2.35, 2.0, .65, PAP, "prediction: next frame\nfrom this frame + action"); bx(9.6, 3.15, 2.8, .65, PAP, "variance: keep every number\nspread out (hinge)"); bx(9.6, 2.35, 2.8, .65, PAP, "covariance (weight 0.04):\nnumbers stay uncorrelated")
ar(1.7, 3.05, 2.1, 3.05); ar(4.3, 3.05, 4.7, 3.45); ar(4.3, 3.05, 4.7, 2.65); ar(6.6, 3.45, 7.2, 3.45); ar(6.6, 2.65, 7.2, 2.65)
ax.text(.1, 1.85, "Scene-factor encoder (E62; green = new in this study)", fontsize=10, fontweight="bold")
bx(.1, .3, 1.6, 1.1, "#ddd", "image\n96×96×3"); bx(2.1, .3, 3.2, 1.1, "#a8dba8", "4 strided conv layers\n→ 48 numbers (the point)"); bx(5.7, .3, 3.0, 1.1, "#a8dba8", "4 transposed conv layers\n→ image back"); bx(9.1, .3, 3.3, 1.1, "#a8dba8", "reconstruction loss only:\nmean (image − rebuilt image)²")
ar(1.7, .85, 2.1, .85); ar(5.3, .85, 5.7, .85); ar(8.7, .85, 9.1, .85); F_ARCH = img(fig, "100%")
# 10 reading matrix schematic (ideal diagonal)
fig, ax = plt.subplots(figsize=(4.6, 3.2)); M_ = np.eye(5) * .9 + .02; ax.imshow(M_, cmap="Blues", vmin=0, vmax=1); ax.set_xticks(range(5)); ax.set_xticklabels([f"factor {i+1}" for i in range(5)], fontsize=7.5, rotation=45); ax.set_yticks(range(5)); ax.set_yticklabels([f"rung {i+1}" for i in range(5)], fontsize=8); ax.set_title("ideal: each rung's block carries\nits own factor only", fontsize=9); F_READ = img(fig, "48%")
H = open("experiments/components_template.html").read()
for k, v in {"F_SPEED": F_SPEED, "F_BEND": F_BEND, "F_WHITE": F_WHITE, "F_SHARE": F_SHARE, "F_DIFF": F_DIFF, "F_EIG": F_EIG, "F_LADDER": F_LADDER, "F_ANGLE": F_ANGLE, "F_ARCH": F_ARCH, "F_READ": F_READ}.items(): H = H.replace("{{" + k + "}}", v)
open("docs/report/COMPONENTS.html", "w").write(H); print("ok")
