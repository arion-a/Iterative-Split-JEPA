"""One-page 'how simple and how good' summary figure for a researcher."""
import json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
RED, BLUE, GRN, GREY = "#c2410c", "#1d4ed8", "#15803d", "#64748b"
dl = json.load(open("results/deep_ladder.json")); A10 = np.array([r["angle"] for r in dl if r["rungs"] == 10]); G10 = np.array([r["gap"] for r in dl if r["rungs"] == 10])
e = json.load(open("results/e62/e62.json")); M = np.array([x["reading"] for x in e["rungs"]] + [e["core_reading"]])
fig = plt.figure(figsize=(14, 7.6)); fig.patch.set_facecolor("white")
fig.text(.03, .95, "Iterated splitting: the whole method, and what it recovers", fontsize=21, fontweight="bold", va="top")
fig.text(.03, .905, "the layers.' values are never given: only matched pairs, and one axis-finding step per rung", fontsize=12, color="#475569", va="top")
ax = fig.add_axes([.03, .12, .27, .70]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
steps = [("1  Pair", "two samples that agree on every\nslower layer"), ("2  Subtract", "D = u − v: only the layer\nthat changed is left"), ("3  Find the axes", "eigenvectors of M = mean(D Dᵀ):\nthe long axes are that layer"), ("4  Cut", "remove those directions;\nwork inside what is left"), ("5  Repeat", "next rung, next layer")]
for i, (h, b) in enumerate(steps):
    y = .84 - i * .185; ax.add_patch(FancyBboxPatch((0, y - .03), 1, .15, boxstyle="round,pad=0.01,rounding_size=0.02", fc="#fffbeb", ec="#fde68a")); ax.text(.05, y + .075, h, fontsize=13, fontweight="bold", va="center"); ax.text(.05, y + .02, b, fontsize=10, va="center", color="#334155")
ax.set_title("The whole recipe", fontsize=12.5, loc="left", fontweight="bold")
a2 = fig.add_axes([.38, .15, .27, .62]); x = np.arange(1, 11); a2.bar(x, A10.mean(0), color=BLUE, yerr=[A10.mean(0) - A10.min(0), A10.max(0) - A10.mean(0)], capsize=3)
a2.axhline(80, color=RED, ls="--", lw=1.5); a2.text(5.5, 72, "unrelated directions ≈ 80°", color=RED, ha="center", fontsize=10); a2.set_ylim(0, 90); a2.set_xticks(x); a2.set_xlabel("rung"); a2.set_ylabel("error: angle to the true layer (degrees)")
a2.set_title("Synthetic world, 10 rungs\nevery cut within 3° of the truth", fontsize=12.5, loc="left", fontweight="bold"); a2.spines[["top", "right"]].set_visible(False)
a2.text(5.5, 12, f"sharpest gap {G10.max():.0f}, weakest {G10.min():.0f}\n(1 = no cut)", ha="center", fontsize=10, color=GREY)
a3 = fig.add_axes([.72, .15, .25, .62]); names = ["gripper", "arm pose", "cube yaw", "cube position", "cube colour", "light tint", "brightness", "cam. dist/elev", "cam. azimuth"]
a3.imshow(np.clip(M[3:, 3:], 0, 1), cmap="Blues", vmin=0, vmax=1); a3.set_xticks(range(6)); a3.set_xticklabels(names[3:], rotation=45, ha="right", fontsize=9); a3.set_yticks(range(6)); a3.set_yticklabels([f"rung {k}" for k in range(4, 9)] + ["left over"], fontsize=9.5)
for i in range(6):
    for j in range(6): a3.text(j, i, f"{M[3+i, 3+j]:.2f}", ha="center", va="center", fontsize=8.5, color="white" if M[3 + i, 3 + j] > .55 else "black")
a3.set_title("Simulator images: each rung's block\ncarries its own factor (a diagonal)", fontsize=12.5, loc="left", fontweight="bold")
fig.text(.03, .045, "Left: the rule. Middle: with exact pairs it recovers 10 nested layers. Right: on re-rendered scenes it recovers named factors in order (gripper, arm pose and cube yaw, too small in the picture, are not shown).", fontsize=10, color="#475569")
fig.savefig("docs/img/hero_summary.png", dpi=140, bbox_inches="tight", facecolor="white"); print(A10.max(), G10.min(), G10.max())
