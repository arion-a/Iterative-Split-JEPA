"""One-page diagram: where each part of the robot experiment came from (paper / our mechanism / new in this run)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
C = {"paper": "#f4c27a", "ours": "#8ec5e8", "new": "#a8dba8", "data": "#dddddd"}
fig, ax = plt.subplots(figsize=(13, 7.4)); ax.set_xlim(0, 13); ax.set_ylim(-0.5, 7.4); ax.axis("off")
def box(x, y, w, h, kind, title, body, star=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04", fc=C[kind], ec="#333", lw=2.2 if star else 1))
    ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top", fontsize=10.5, fontweight="bold")
    ax.text(x + w / 2, y + h - 0.62, body, ha="center", va="top", fontsize=8.8, linespacing=1.35)
def arrow(x1, y1, x2, y2): ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", lw=1.6, color="#333"))
ax.text(6.5, 7.1, "Robot experiment: what each part is and where it comes from", ha="center", fontsize=14, fontweight="bold")
box(0.3, 4.6, 2.6, 1.9, "data", "1  Robot images", "ManiSkill3 simulator\nPickCube, PushCube\n800 trajectories each\n2 cameras (base, side)")
box(3.5, 4.6, 3.1, 1.9, "paper", "2  Training (the paper's code)", "ResNet-50 -> 128 / 256 numbers\n4 losses: prediction, invariance,\nvariance, covariance\n200 epochs, our data", star=True)
box(7.2, 4.6, 2.3, 1.9, "data", "3  Frozen embedding", "one vector per image\nno more training\nfrom here on")
box(10.1, 4.6, 2.6, 1.9, "paper", "4  Paper's own split", "fixed halves:\nfirst half = 'invariant'\nrest = 'variant'\nscore = camera ratio")
box(0.3, 1.5, 3.4, 2.1, "ours", "5  Pairs (ours)", "rung 1: same frame, two cameras\nrung 2: same moment, different\ntrajectories (same camera)")
box(4.3, 1.5, 4.0, 2.1, "new", "6A  Eigen-split, NO whitening (new)", "covariance of pair differences taken\ndirectly in the paper's raw embedding;\nsmallest directions = invariant block", star=True)
box(8.9, 1.5, 3.8, 2.1, "new", "6B  Paper's halves as rung 1 (new)", "whiten inside the invariant half only,\nthen our rung 2 on trajectory pairs;\nreport the gap", star=True)
arrow(2.9, 5.55, 3.5, 5.55); arrow(6.6, 5.55, 7.2, 5.55); arrow(9.5, 5.55, 10.1, 5.55)
arrow(8.3, 4.6, 7.0, 3.6); arrow(3.7, 2.55, 4.3, 2.55); arrow(8.3, 2.55, 8.9, 2.55); arrow(8.3, 4.6, 10.8, 3.6)
ax.text(6.5, 0.95, "Scored the same way for 4, 6A and 6B: held-out trajectories (fit on 6 per group, score on 2), ratio of variant to invariant response", ha="center", fontsize=9)
for i, (k, t) in enumerate([("paper", "From the SplitJEPA paper (code unchanged)"), ("ours", "From our own mechanism (pairs, eigen-split, ladder)"), ("new", "New in this run (did not exist in earlier experiments)"), ("data", "Data / intermediate")]):
    ax.add_patch(FancyBboxPatch((0.4 + (i % 2) * 6.4, -0.05 - (i // 2) * 0.45), 0.3, 0.3, boxstyle="round,pad=0.02", fc=C[k], ec="#333")); ax.text(0.85 + (i % 2) * 6.4, 0.1 - (i // 2) * 0.45, t, fontsize=8.3, va="center")
ax.text(6.5, 0.62, "Thick outline = what the earlier robot experiments did not have: the paper's full 200-epoch training, plus splitting applied on that embedding.", ha="center", fontsize=9, style="italic")
fig.savefig("docs/img/robot_origin_diagram.png", dpi=170, bbox_inches="tight")
