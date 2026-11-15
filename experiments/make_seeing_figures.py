"""Figures that show the real pipeline on a 3-number world (one number per layer), using the real code (worlds.py, engine.py).
Encoder = identity on purpose (nothing trained), so what you see is the generator, the bend, whitening, pairs and the eigen-split."""
import numpy as np, torch, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from isj.worlds import BlockWorld, CouplingMap
from isj.engine import fit_whitener, fit_rung
torch.manual_seed(0)
world = BlockWorld([1, 1, 1], [0.2, 0.6, 0.95], seed=3)                 # layers: a (fast), b (medium), c (slow)
obs = CouplingMap(3, 4, 1.0, None, seed=3)
n = 1500
z = world.sample(n); x = obs(z)
wh = fit_whitener(obs(world.sample(30000)), 1e-5); r = wh(x)
Z, X, Rr = z.numpy(), x.numpy(), r.numpy()
# rung 1: pairs agree on b and c, differ in a. rung 2: agree on c, differ in a and b.
u1, v1 = world.correspondence_pairs(30000, 1); ru1, rv1 = wh(obs(u1)), wh(obs(v1))
fit1 = fit_rung(ru1, rv1, torch.eye(3), k=1, d_k=1)
u2, v2 = world.correspondence_pairs(30000, 2); ru2, rv2 = wh(obs(u2)), wh(obs(v2))
fit2 = fit_rung(ru2, rv2, fit1.Q, k=2, d_k=1)
V1, V2 = fit1.V.numpy()[:, 0], fit2.V.numpy()[:, 0]; H2 = fit2.Q.numpy()[:, 0]
cm = "coolwarm"
def cloud(ax, P, col, title, lab):
    ax.scatter(P[:, 0], P[:, 1], P[:, 2], c=col, cmap=cm, s=5, alpha=.7); ax.set_title(title, fontsize=10)
    ax.set_xlabel(lab[0], fontsize=8); ax.set_ylabel(lab[1], fontsize=8); ax.set_zlabel(lab[2], fontsize=8); ax.tick_params(labelsize=6)
# ---------- sheet 1: what the dots look like
fig = plt.figure(figsize=(16, 4.4))
cloud(fig.add_subplot(1, 4, 1, projection="3d"), Z, Z[:, 0], "1. hidden values z\n(colour = fast layer a)", ("a (fast)", "b", "c (slow)"))
cloud(fig.add_subplot(1, 4, 2, projection="3d"), X, Z[:, 0], "2. after the bend x = f(z)\n(same dots, colour = a)", ("x1", "x2", "x3"))
cloud(fig.add_subplot(1, 4, 3, projection="3d"), Rr, Z[:, 0], "3. whitened embedding r~\ncolour = FAST layer a", ("r~1", "r~2", "r~3"))
cloud(fig.add_subplot(1, 4, 4, projection="3d"), Rr, Z[:, 2], "4. the same dots\ncolour = SLOW layer c", ("r~1", "r~2", "r~3"))
fig.suptitle("Sheet 1: a dot is one sample. Colour shows where each hidden layer ends up inside the bent cloud (real code, 3 numbers)", fontsize=11); fig.tight_layout(rect=(0, 0, 1, .94)); fig.savefig("docs/img/see_sheet1.png", dpi=150); plt.close(fig)
# ---------- sheet 2: the splitting
D1 = (ru1 - rv1).numpy(); D2 = ((ru2 - rv2) @ fit1.Q).numpy()
fig = plt.figure(figsize=(16, 8.6))
ax = fig.add_subplot(2, 4, 1, projection="3d"); ax.scatter(*Rr.T, s=3, color="#dee2e6")
for i in range(12): ax.plot(*np.c_[ru1[i].numpy(), rv1[i].numpy()], "-o", color="#d9480f", ms=3)
ax.set_title("5. rung-1 pairs: two dots that agree on b and c,\ndiffer in a (orange segments)", fontsize=9)
ax = fig.add_subplot(2, 4, 2, projection="3d"); ax.scatter(*D1[:1500].T, s=3, color="#d9480f", alpha=.5)
for e, col in ((V1, "k"),): ax.plot(*np.c_[-3 * e, 3 * e], color=col, lw=3)
ax.set_title(f"6. differences D (one per pair): they lie along\none direction (black) = V1. eigenvalues {np.round(fit1.eigvals.numpy(), 2)}", fontsize=9)
ax = fig.add_subplot(2, 4, 3); q = fit1.Q.numpy(); P = Rr @ q
ax.scatter(P[:, 0], P[:, 1], c=Z[:, 2], cmap=cm, s=5); ax.set_title("7. remove V1: the dots seen in the 2 leftover directions H1\n(colour = c); a is gone from this view", fontsize=9); ax.set_aspect("equal")
ax = fig.add_subplot(2, 4, 4); ax.scatter(D2[:1500, 0], D2[:1500, 1], s=3, color="#e67700", alpha=.5)
for j in range(2): e = fit2.Q.numpy(); 
E = np.linalg.eigh(D2.T @ D2 / len(D2))[1][:, ::-1]
for j, col in zip(range(2), ("k", "#868e96")): ax.plot([-3 * E[0, j], 3 * E[0, j]], [-3 * E[1, j], 3 * E[1, j]], color=col, lw=3 if j == 0 else 1.5)
ax.set_title(f"8. rung 2: differences inside H1 (agree on c, differ in b)\nlong axis = V2, eigenvalues {np.round(fit2.eigvals.numpy(), 2)}", fontsize=9); ax.set_aspect("equal")
for i, (blk, name, true, col) in enumerate(((V1, "V1 (found by rung 1)", Z[:, 0], "a (fast)"), (V2, "V2 (found by rung 2)", Z[:, 1], "b (medium)"), (H2, "core (left over)", Z[:, 2], "c (slow)"))):
    ax = fig.add_subplot(2, 4, 5 + i); coord = Rr @ blk; ax.scatter(true, coord, s=4, color="#1c7ed6", alpha=.5)
    cc = abs(np.corrcoef(true, coord)[0, 1]); ax.set_xlabel(f"TRUE hidden value {col}"); ax.set_ylabel(f"coordinate along {name}"); ax.set_title(f"{9 + i}. found block vs truth: |correlation| = {cc:.2f}", fontsize=9)
ax = fig.add_subplot(2, 4, 8); ax.axis("off")
ax.text(0, .95, "How to read the bottom row", fontsize=11, weight="bold", va="top")
ax.text(0, .8, "Each dot is one sample. Horizontal: the hidden\nvalue the generator used (we know it, the method\ndoes not). Vertical: where the sample sits along\nthe direction the splitter found.\n\nA straight line = the splitter found that hidden\nvalue. Scatter with no line = it did not.", fontsize=9, va="top")
fig.suptitle("Sheet 2: the splitting on the same dots (real code: fit_rung; encoder untrained)", fontsize=11); fig.tight_layout(rect=(0, 0, 1, .95)); fig.savefig("docs/img/see_sheet2.png", dpi=150); plt.close(fig)
print("rung1 gap", fit1.gap_ratio, "rung2 gap", fit2.gap_ratio)
