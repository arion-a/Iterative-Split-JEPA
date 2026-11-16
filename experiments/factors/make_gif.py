"""Animated clip of the E62 ladder: the 48-number representation is carved into rung blocks, and each block's own effect on the image is shown.
    PYTHONPATH=src:experiments/factors python make_gif.py -> docs/img/ladder.gif"""
import json, io, sys, numpy as np, torch, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
from train_ae import AE
r = json.load(open("results/e62/e62.json")); B = torch.load("results/e62/blocks.pt")
ae = AE(); ae.load_state_dict(B["ae"]); ae.eval(); mean, mat = B["mean"].double(), B["matrix"].double(); inv = torch.linalg.inv(mat)
ds = [x["d"] for x in r["rungs"]] + [r["core_dim"]]; names = ["gripper", "arm pose", "cube yaw", "cube position", "cube colour", "light tint", "brightness", "camera distance / elevation", "camera azimuth (left over)"]
COL = {3: "#15803d", 4: "#0e7490", 5: "#1d4ed8", 6: "#7c3aed", 7: "#a21caf", 8: "#64748b"}; GREYC = "#cbd5e1"
what = {3: "the cube slides across the table", 4: "the cube changes colour", 5: "the light shifts colour", 6: "the whole scene gets brighter or darker", 7: "the camera moves back and forth / up and down", 8: "(what is left: the camera's sideways angle)"}
starts = np.cumsum([0] + ds); own = [x["reading"][k] for k, x in enumerate(r["rungs"])] + [r["core_reading"][8]]
def decode(k, t):
    v = B["blocks"][k][:, 0] if k < 8 else None
    if k == 8:                                   # core: leading direction of the left-over content is not stored; show the camera-azimuth effect via the factor probe-free direction = last block's complement (skipped)
        return None
    z = (mean + (t * v) @ inv).float()[None]
    with torch.no_grad(): return ae.decode(z)[0].permute(1, 2, 0).numpy()
def frame(active, t, title, sub, shown):
    fig = plt.figure(figsize=(9.6, 5.4), dpi=100); fig.patch.set_facecolor("white")
    fig.text(.03, .94, title, fontsize=17, fontweight="bold", va="top"); fig.text(.03, .875, sub, fontsize=11, color="#475569", va="top")
    ax = fig.add_axes([.03, .12, .52, .62]); ax.set_xlim(0, 16); ax.set_ylim(0, 3.4); ax.axis("off"); ax.text(0, 3.25, "the 48 numbers of one image's representation", fontsize=9.5, color="#64748b", va="bottom")
    for k in range(9):
        for c in range(ds[k]):
            idx = starts[k] + c; row, col = idx // 16, idx % 16; x, y = col, 2 - row
            if k < 3: fc = GREYC; a = 1 if shown >= 1 else .35
            else: fc = COL[k] if (k <= shown + 2 and shown >= 1 and (k - 2) <= shown) else "#f1f5f9"; a = 1
            ec = "black" if active == k else "white"; lw = 2.5 if active == k else 1.5
            ax.add_patch(Rectangle((x + .05, y + .05), .9, .9, fc=fc, ec=ec, lw=lw, alpha=a))
    ax.text(0, -.25, "grey = rungs 1–3 (gripper, arm pose, cube yaw): too small in the picture for a clean cut", fontsize=8.3, color="#64748b")
    return fig, ax
def render(fig):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=100); plt.close(fig); b.seek(0); return Image.open(b).convert("RGB")
frames = []; durs = []
def add(img, n=1, ms=70):
    for _ in range(n): frames.append(img); durs.append(ms)
fig, ax = frame(-1, 0, "Iterated splitting, rung by rung", "Start: all 48 numbers are one undivided cloud", 0); add(render(fig), 6, 80)
tt = np.concatenate([np.linspace(0, 3, 4), np.linspace(3, -3, 8)[1:], np.linspace(-3, 0, 4)[1:]])
for k in range(3, 8):
    for t in tt:
        fig, ax = frame(k, t, f"Rung {k+1}: {names[k]}", f"block of {ds[k]} numbers · its own factor read at R² = {own[k]:.2f}", k - 2)
        im = decode(k, t); a2 = fig.add_axes([.58, .12, .38, .68]); a2.imshow(np.kron(im, np.ones((1, 1, 1))), interpolation="bilinear"); a2.set_xticks([]); a2.set_yticks([])
        for s in a2.spines.values(): s.set_edgecolor(COL[k]); s.set_linewidth(4)
        fig.text(.77, .83, "move along this block →", ha="center", fontsize=10, color=COL[k], fontweight="bold"); fig.text(.77, .075, what[k], ha="center", fontsize=10.5)
        a3 = fig.add_axes([.60, .02, .34, .02]); a3.set_xlim(-3.3, 3.3); a3.axis("off"); a3.plot([-3, 3], [0, 0], color="#cbd5e1", lw=3); a3.scatter([t], [0], color=COL[k], s=60, zorder=3)
        add(render(fig), 1, 50)
fig, ax = frame(8, 0, "What is left", f"{ds[8]} numbers: the camera's sideways angle, read at R² = {own[8]:.2f}", 6); a2 = fig.add_axes([.58, .12, .38, .68]); a2.axis("off")
fig.text(.77, .5, "Each rung removed one named factor.\nWhat is left is the slowest one:\nthe camera's azimuth.", ha="center", fontsize=12); add(render(fig), 10, 100)
Image.fromarray(np.concatenate([np.array(frames[i]) for i in (0, 8, 20, 40)], 1)).save("/tmp/gif_check.png")
frames[0].save("docs/img/ladder.gif", save_all=True, append_images=frames[1:], duration=durs, loop=0, optimize=True)
print(len(frames), "frames", sum(durs) / 1000, "s")
