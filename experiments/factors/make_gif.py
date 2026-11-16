"""Animated clip of the E62 ladder as a staircase: each rung cuts a block from what the previous rung left, and the block's effect on the image appears beside it.
    PYTHONPATH=src:experiments/factors python make_gif.py -> docs/img/ladder.gif"""
import json, io, numpy as np, torch, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
from train_ae import AE
r = json.load(open("results/e62/e62.json")); B = torch.load("results/e62/blocks.pt")
ae = AE(); ae.load_state_dict(B["ae"]); ae.eval(); mean, mat = B["mean"].double(), B["matrix"].double(); inv = torch.linalg.inv(mat)
def decode(k, t):
    z = (mean + (t * B["blocks"][k][:, 0]) @ inv).float()[None]
    with torch.no_grad(): return ae.decode(z)[0].permute(1, 2, 0).numpy()
ds = [x["d"] for x in r["rungs"]]; own = [x["reading"][k] for k, x in enumerate(r["rungs"])]
# rows: (label, cells, colour, factor reading, thumbs?)
rows = [("Rungs 1–3", sum(ds[:3]), "#94a3b8", "gripper, arm pose, cube yaw: too small for a clean cut", None)]
cols = ["#15803d", "#0e7490", "#1d4ed8", "#7c3aed", "#a21caf"]; nm = ["cube position", "cube colour", "light tint", "brightness", "camera distance / elevation"]
for j, k in enumerate(range(3, 8)): rows.append((f"Rung {k+1}", ds[k], cols[j], f"{nm[j]}   (R² {own[k]:.2f})", k))
rows.append(("What is left", r["core_dim"], "#475569", f"camera sideways angle   (R² {r['core_reading'][8]:.2f})", None))
thumbs = {k: (decode(k, -3), decode(k, 3)) for k in range(3, 8)}
W, H, CW, CH, X0, Y0, DY = 1280, 720, 9, 24, 50, 120, 82
cum = np.cumsum([0] + [x[1] for x in rows])
def draw(row_i, p, ntop=None):
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    ax.text(50, 38, "Iterated splitting extracts one layer at a time", fontsize=24, fontweight="bold", va="center")
    ax.text(50, 76, "each rung cuts a block out of what the previous rung left behind; the picture beside it shows what that block controls", fontsize=12.5, color="#475569", va="center")
    if row_i is None or row_i >= 1: ax.text(790, 104, "image when the block is moved down (−) and up (+)", fontsize=9.5, color="#64748b", va="center")
    for i, (lab, n, col, desc, k) in enumerate(rows):
        if row_i is not None and i > row_i: break
        y = Y0 + i * DY; stage = 1.0 if (row_i is None or i < row_i) else p
        done = cum[i] if stage < .3 else cum[i + 1]                      # cells already extracted when this row is drawn
        for c in range(48):
            inblk = cum[i] <= c < cum[i + 1]; extracted = c < cum[i]
            fc = "#e2e8f0"; ec = "white"; lw = 1
            if extracted: fc = "#f1f5f9"                                  # taken out by an earlier rung: faded
            if inblk and stage >= .3: fc = col
            if inblk and stage < .3: fc = "#fde68a"; ec = "black"; lw = 1.6   # about to be cut: highlighted
            ax.add_patch(Rectangle((X0 + c * CW, y), CW - 1, CH, fc=fc, ec=ec, lw=lw))
        ax.text(X0 + 48 * CW + 14, y + CH / 2, lab, fontsize=13, fontweight="bold", va="center", color=col if stage >= .3 else "#94a3b8")
        if stage >= .6:
            a = min(1, (stage - .6) / .3)
            ax.text(X0 + 48 * CW + 14, y + CH / 2 + 24, desc, fontsize=10.5, va="center", color="#334155", alpha=a)
            if k is not None:
                for q, im in enumerate(thumbs[k]):
                    xx = 790 + q * 82; ax.imshow(im, extent=(xx, xx + 74, y + 66, y - 8), alpha=a, interpolation="bilinear", zorder=2)
                ax.text(790 + 164 + 10, y + 28, "→", fontsize=1, alpha=0)
        if stage >= .85 and i < len(rows) - 1:                            # stair step down to the next rung's remaining content
            xb = X0 + cum[i + 1] * CW
            ax.annotate("", (xb, y + DY), (xb, y + CH + 1), arrowprops=dict(arrowstyle="-|>", color="#334155", lw=1.4), zorder=3)
    return fig
def render(fig):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=100); plt.close(fig); b.seek(0); return Image.open(b).convert("RGB")
frames, durs = [], []
def add(img, n, ms):
    for _ in range(n): frames.append(img); durs.append(ms)
fig = draw(-1, 0); add(render(fig), 1, 500)
for i in range(len(rows)):
    for p in (0.15, 0.4, 0.6, 0.8, 1.0): add(render(draw(i, p)), 1, 120 if p < .5 else 90)
add(render(draw(None, 1)), 1, 1800)
Image.fromarray(np.concatenate([np.array(frames[i]) for i in (1, 12, 30, len(frames) - 1)], 0)[::2, ::2]).save("/tmp/gif_check.png")
frames[0].save("docs/img/ladder.gif", save_all=True, append_images=frames[1:], duration=durs, loop=0, optimize=True)
print(len(frames), "frames", sum(durs) / 1000, "s")
