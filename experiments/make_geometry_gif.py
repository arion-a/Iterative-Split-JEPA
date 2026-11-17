"""3-D toy of the ladder with exact (ideal) maths: three layers, each one number, hidden in a rotated frame.
Pairs -> differences collapse onto a line -> that line is the fast layer's axis -> flatten along it -> repeat.
    python experiments/make_geometry_gif.py -> docs/img/geometry_ladder.gif"""
import io, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from PIL import Image
rng = np.random.default_rng(7); N = 260
Q, _ = np.linalg.qr(rng.normal(size=(3, 3)))                     # rotation hiding the layers
ef, em, es = Q[:, 0], Q[:, 1], Q[:, 2]                           # fast, middle, slow axes (the truth)
A = rng.normal(size=(N, 3)); X = A @ Q.T                         # points (rows): a_f*ef + a_m*em + a_s*es
col = plt.cm.viridis((A[:, 2] - A[:, 2].min()) / np.ptp(A[:, 2]))   # colour = slow value (follows the points through every step)
RED, ORG, BLU, GREY = "#c2410c", "#d97706", "#1d4ed8", "#94a3b8"
idx = np.arange(60)                                              # pairs drawn
Af = A.copy(); Af[:, 0] = rng.normal(size=N); V1 = Af @ Q.T      # rung-1 partners: same (a_m, a_s), fresh a_f
Ag = A.copy(); Ag[:, 0] = rng.normal(size=N); Ag[:, 1] = rng.normal(size=N); V2 = Ag @ Q.T   # rung-2 partners: same a_s, fresh a_f, a_m
Pf = np.eye(3) - np.outer(ef, ef); Pm = np.eye(3) - np.outer(ef, ef) - np.outer(em, em)
def lerp(a, b, s): return (1 - s) * a + s * b
ease = lambda s: s * s * (3 - 2 * s)
stages = [("① A cloud of points. Three hidden layers (fast, middle, slow) are mixed together.", 10), ("② Rung 1: pairs share the middle and slow layers, so each pair differs only along the fast axis.", 10),
          ("③ Subtract each pair: the differences pile up on one line. That line IS the fast layer.", 14), ("④ Cut it away: flatten the cloud along that line. What remains is flat.", 12),
          ("⑤ Rung 2: pairs now differ only along the middle axis. Their differences pile up on a second line.", 14), ("⑥ Cut that away too. One line is left: the slow layer.", 12), ("The ladder: three layers, each found by pairs plus one axis-finding step.", 14)]
frames = []; fno = 0; total = sum(n for _, n in stages)
def draw(title, pts, pairs=None, diffs=None, axes=(), dlim=2.7):
    global fno
    fig = plt.figure(figsize=(7.4, 6.2), dpi=100); ax = fig.add_subplot(111, projection="3d"); fig.patch.set_facecolor("white")
    ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], c=col, s=26, alpha=.8, depthshade=False)
    if pairs is not None:
        for a, b in zip(*pairs): ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color="#334155", lw=1.4, alpha=.9)
    if diffs is not None: ax.scatter(diffs[:, 0], diffs[:, 1], diffs[:, 2], color=RED, s=34, alpha=.9, depthshade=False)
    for v, c, lab in axes: ax.plot([-3.4 * v[0], 3.4 * v[0]], [-3.4 * v[1], 3.4 * v[1]], [-3.4 * v[2], 3.4 * v[2]], color=c, lw=3.5); ax.text(*(3.5 * v), lab, color=c, fontsize=10, fontweight="bold")
    ax.set_xlim(-dlim, dlim); ax.set_ylim(-dlim, dlim); ax.set_zlim(-dlim, dlim); ax.set_box_aspect((1, 1, 1)); ax.set_axis_off(); ax.view_init(18, 25 + 120 * fno / total)
    fig.text(.5, .955, title, ha="center", fontsize=11.5, fontweight="bold", color="#1e293b", wrap=True); fig.text(.5, .03, "point colour = value of the slowest layer (follows each point)", ha="center", fontsize=8.5, color="#64748b")
    b_ = io.BytesIO(); fig.savefig(b_, format="png", dpi=100); plt.close(fig); b_.seek(0); frames.append(Image.open(b_).convert("RGB")); fno += 1
for si, (title, n) in enumerate(stages):
    for f in range(n):
        s = ease((f + 1) / n)
        if si == 0: draw(title, X)
        elif si == 1: draw(title, X, pairs=(X[idx], V1[idx]))
        elif si == 2: d = X - V1; draw(title, X, diffs=lerp(X, d, s)[idx] if False else lerp(X[idx], (X - V1)[idx], s), axes=[(ef, RED, "fast layer")] if s > .9 else [])
        elif si == 3: draw(title, lerp(X, X @ Pf, s), axes=[(ef, RED, "fast layer")])
        elif si == 4: Xp = X @ Pf; draw(title, Xp, pairs=(Xp[idx], (V2 @ Pf)[idx]) if s < .3 else None, diffs=lerp(Xp[idx], ((X - V2) @ Pf)[idx], s) if s >= .3 else None, axes=[(ef, RED, "fast layer")] + ([(em, ORG, "middle layer")] if s > .9 else []))
        elif si == 5: draw(title, lerp(X @ Pf, X @ Pm, s), axes=[(ef, RED, "fast layer"), (em, ORG, "middle layer")])
        else: draw(title, X @ Pm, axes=[(ef, RED, "fast layer"), (em, ORG, "middle layer"), (es, BLU, "slow layer")])
frames[0].save("docs/img/geometry_ladder.gif", save_all=True, append_images=frames[1:], duration=[90] * (len(frames) - 12) + [160] * 12, loop=0, optimize=True)
Image.fromarray(np.concatenate([np.array(frames[i].resize((420, 320))) for i in (5, 18, 40, 70)], 1)).save("/tmp/geo_check.png"); print(len(frames), "frames")
