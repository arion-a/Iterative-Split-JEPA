import base64, io, json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False, "font.size": 11})
RED, BLUE, GREY, GRN = "#c2410c", "#1d4ed8", "#64748b", "#15803d"
def img(fig):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=170, bbox_inches="tight", facecolor="white"); plt.close(fig); return f'<img src="data:image/png;base64,{base64.b64encode(b.getvalue()).decode()}">'
# ---- mechanism figure (2-number toy, mild bend)
rng = np.random.default_rng(4)
def obs(z, s=.3):
    x = z.copy(); x[:, 0] = z[:, 0] + s * np.tanh(1.5 * z[:, 1]); x[:, 1] = z[:, 1] + s * np.tanh(1.5 * x[:, 0]); return x
th = .6; Rm = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]]); f = lambda z: obs(z) @ Rm.T
ref = f(rng.standard_normal((20000, 2))); mu = ref.mean(0); ev, V = np.linalg.eigh(np.cov((ref - mu).T)); W = V @ np.diag(ev ** -.5) @ V.T; wh = lambda q: (q - mu) @ W
u = rng.standard_normal((20000, 2)); v = u.copy(); v[:, 0] = rng.standard_normal(20000)       # pairs: same slow number (col 1), different fast number (col 0)
ru, rv = wh(f(u)), wh(f(v)); D = ru - rv; M = D.T @ D / len(D); lam, E = np.linalg.eigh(M); lam, E = lam[::-1], E[:, ::-1]
fig, axs = plt.subplots(1, 4, figsize=(15, 3.7), gridspec_kw={"width_ratios": [1, 1, 1, 1.25]})
p = wh(f(rng.standard_normal((700, 2)))); axs[0].scatter(p[:, 0], p[:, 1], s=4, color="#cbd5e1")
for i in range(5): axs[0].plot([ru[i, 0], rv[i, 0]], [ru[i, 1], rv[i, 1]], "-o", color=RED, ms=4)
axs[0].set_title("1  matched pairs\n(orange: same slow value,\ndifferent fast value)", fontsize=10)
axs[1].scatter(D[:1500, 0], D[:1500, 1], s=3, color=RED, alpha=.4)
axs[1].annotate("", xy=E[:, 0] * 3, xytext=-E[:, 0] * 3, arrowprops=dict(arrowstyle="<->", color="k", lw=2)); axs[1].text(*(E[:, 0] * 3.1), "long axis\n= block found", fontsize=9, ha="left", va="bottom")
axs[1].set_title("2  subtract each pair:\nthe differences form an oval", fontsize=10)
h = E[:, 1]; pr = (p @ h)[:, None] * h[None, :]; axs[2].scatter(p[:, 0], p[:, 1], s=3, color="#e2e8f0"); axs[2].scatter(pr[:, 0], pr[:, 1], s=5, color=BLUE, alpha=.6)
axs[2].set_title("3  remove the long axis,\nkeep what did not change", fontsize=10)
for a in axs[:3]: a.set_xlim(-3.6, 3.6); a.set_ylim(-3.6, 3.6); a.set_aspect("equal"); a.set_xticks([]); a.set_yticks([]); a.axhline(0, color="#e2e8f0", lw=.6); a.axvline(0, color="#e2e8f0", lw=.6)
ax = axs[3]; ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 7.8); ax.set_title("4  repeat on what is left", fontsize=10)
for i, dim in enumerate([28, 24, 20, 16, 12, 8, 4]):
    y = 7.0 - i * 1.0; w = 9 * dim / 28
    ax.add_patch(FancyBboxPatch((0, y - .35), w, .7, boxstyle="round,pad=0.02", fc=BLUE if i == 6 else "#93c5fd", ec="none")); ax.text(.15, y, f"{dim} directions" if i == 0 else f"{dim}", va="center", fontsize=8.5, color="white" if i == 6 else "#1e293b")
    if i < 6: ax.text(w + .15, y, f"rung {i+1}: removes block {i+1} (4)", va="center", fontsize=8.5, color=RED)
    else: ax.text(w + .15, y, "core = slowest layer", va="center", fontsize=8.5, color=BLUE)
fig.tight_layout(); fig_mech = img(fig)
# ---- results
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
rows = "".join(f"<tr><td>{k}</td><td>{np.median(ang[:,k-1]):.1f}°</td><td>{ang[:,k-1].min():.1f} – {ang[:,k-1].max():.1f}°</td><td>{np.median(gap[:,k-1]):.0f}</td></tr>" for k in range(1, 7))
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: Letter; margin: 14mm 12mm; }} body{{font:15px/1.5 "DejaVu Sans",sans-serif;color:#1e293b;margin:0}} .w{{max-width:900px;margin:auto;padding:8px}}
h1{{font-size:26px;margin:0 0 4px}} h2{{font-size:18px;margin:20px 0 6px;border-top:2px solid #e2e8f0;padding-top:10px}} img{{width:100%;display:block;margin:8px 0}}
.box{{background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:10px 14px;margin:10px 0}} .warn{{background:#fff7ed;border-color:#fed7aa}}
table{{border-collapse:collapse;margin:8px 0}} td,th{{border:1px solid #e2e8f0;padding:5px 12px;text-align:center}} th{{background:#f1f5f9}} code{{background:#f1f5f9;padding:1px 6px;border-radius:4px}} ol li{{margin:4px 0}}</style></head><body><div class="w">
<h1>Iterated splitting over 6 rungs</h1>
<div class="box"><b>The question.</b> A frame becomes a point in a space with many coordinates. The frame is built from layers of hidden numbers that change at different speeds. Can we split the space, layer by layer, from the fastest layer to the slowest, using only pairs of points?</div>
<h2>The mechanism</h2>
{fig_mech}
<ol>
<li><b>Pair.</b> Two points that agree on every layer slower than the one we ask about, and differ in that layer (here the generator copies those layers, so the pairs are exact).</li>
<li><b>Subtract.</b> <code>D = point 1 − point 2</code> for every pair. The differences stretch only in the directions that layer moves.</li>
<li><b>Find the long axes.</b> <code>M = average of D × Dᵀ</code> (a table of how the differences spread), then eigendecompose it: <code>M = Σ λᵢ vᵢ vᵢᵀ</code>. The directions with big <code>λ</code> are the block for that layer. <code>gap = λ(last big) / λ(first small)</code>.</li>
<li><b>Remove it and repeat</b> on the directions that did not change, with pairs for the next layer. What is left at the end is the slowest layer.</li></ol>
<p>Before step 1 the points are whitened (rescaled so no direction is stretched more than another). Nothing is trained after that.</p>
<h2>The result: 7 layers, 6 rungs, 5 runs</h2>
{fig_res}
<table><tr><th>Rung</th><th>Angle (median)</th><th>Angle (range)</th><th>Gap (median)</th></tr>{rows}</table>
<div class="box"><b>Reading it.</b> Every one of the 6 rungs finds its layer: angles of 0.3 – 2.2° (unrelated directions would give about 80°) and gaps of 72 – 137 (a clean cut needs more than 10). The error grows slightly with depth, from 0.4° at rung 1 to about 2° at rung 6, but stays small.</div>
<div class="box warn"><b>Conditions.</b> This is the plain case: the pairs are exact, the bend between hidden numbers and points is mild, no encoder is trained (in this mild case training makes no difference, which I checked), and the data is generated by me. It is not shown to hold when pairs have to be built from the data, when the bend is strong, or on real images.</div>
</div></body></html>"""
open("docs/report/SIMPLE.html", "w").write(html); print("ok")
