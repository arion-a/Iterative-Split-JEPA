"""Flow-style clip (inspired by the layout of the SplitJEPA project page's animations): an entangled video goes through a chain of splitters;
each splitter peels one pattern out (right) and passes the remainder (down) to the next rung. All videos are decoded from the real E62 blocks.
    PYTHONPATH=src:experiments/factors python make_flow_gif.py -> docs/img/video_split_flow.gif"""
import io, numpy as np, torch, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Circle, FancyBboxPatch
from PIL import Image
from isj import audits
from train_ae import AE
B = torch.load("results/e62/blocks.pt"); OFF = np.cumsum([0, 1, 2, 1, 2, 3, 2, 1, 2, 1])
ae = AE(); ae.load_state_dict(B["ae"]); ae.eval(); mean, mat = B["mean"].double(), B["matrix"].double(); inv = torch.linalg.inv(mat)
enc = lambda x: ae.encode(torch.from_numpy(x).permute(0, 3, 1, 2).float() / 255).detach().double()
C = np.load("data/e62/clip.npz"); Xc, Fc = C["x"], C["f"]; T = len(Xc); Zc = enc(Xc); Wc = (Zc - mean) @ mat; wbar, zbar = Wc.mean(0), Zc.mean(0)
P = np.load("data/e62/probe.npz"); Zp = torch.cat([enc(P["x"][i:i + 500]) for i in range(0, len(P["x"]), 500)]); Wp = (Zp - mean) @ mat; Fp = torch.from_numpy(P["f"]).double()
D = Wc.shape[1]; blocks = [b.double() for b in B["blocks"]]
dec = lambda z: ae.decode(z.float()).permute(0, 2, 3, 1).detach().numpy()
comps = [(Wc - wbar) @ b @ b.T for b in blocks]                                   # rungs 1..8
rest_core = (Wc - wbar) - sum(comps)                                              # core (left over)
GAIN = 3.0; base = dec(zbar[None])
def vid_of(comp_w): return np.clip(base + GAIN * (dec(zbar + comp_w @ inv) - base), 0, 1)
def remainder(extracted):                                                          # decode the clip with the extracted rungs' variation removed
    w = (Wc - wbar) - sum(comps[k] for k in extracted) if extracted else (Wc - wbar)
    return dec(zbar + w @ inv)
EXTR = [3, 4, 5, 6, 7]; names = ["where the cube is", "what colour the cube is", "the colour of the light", "how bright the scene is", "how far the camera is"]
cols = ["#15803d", "#0e7490", "#3b5bdb", "#7c3aed", "#a21caf"]
rem = [remainder(EXTR[:i]) for i in range(6)]
lay = [vid_of(comps[k]) for k in EXTR]
rem_lab = ["ENTANGLED VIDEO\neverything changes at once", "minus the cube's position", "minus the cube's colour", "minus the light's colour", "minus the brightness", "what is left:\nonly the camera's sideways swing"]
trs = []
for k in EXTR:
    g = k; j = OFF[g]; y = (Fp[:, j] - Fp[:, j].mean()) / Fp[:, j].std(); X = Wp @ blocks[k]; w_ = audits.ridge_fit(X[:6000], y[:6000, None])
    pred = (torch.cat([Wc @ blocks[k], torch.ones(T, 1, dtype=torch.double)], 1) @ w_).squeeze(1).numpy(); true = ((torch.from_numpy(Fc[:, j]) - Fp[:, j].mean()) / Fp[:, j].std()).numpy(); trs.append((true, pred))
def bez(p0, p1, p2, p3, n=60):
    t = np.linspace(0, 1, n)[:, None]; return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3
def curve(ax, pts, col, lw=2.6, arrow=False):
    ax.plot(pts[:, 0], pts[:, 1], color=col, lw=lw, alpha=.8, solid_capstyle="round", zorder=3)
W, H, TH, DY, Y0 = 1280, 720, 92, 104, 96
BGTOP, BGBOT = np.array([197, 225, 229]) / 255, np.array([227, 236, 228]) / 255
bg = (BGTOP[None, None, :] * (1 - np.linspace(0, 1, 64)[:, None, None]) + BGBOT[None, None, :] * np.linspace(0, 1, 64)[:, None, None]) * np.ones((64, 2, 3))
frames = []
for t in range(T):
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off"); ax.imshow(bg, extent=(0, W, H, 0), aspect="auto", zorder=0)
    ax.text(40, 30, "Iterated splitting peels patterns out of a video, one rung at a time", fontsize=20, fontweight="bold", color="#1e293b", va="center", zorder=5)
    ax.text(40, 62, "each rung removes one hidden pattern (right) and passes what remains (down) to the next rung", fontsize=11, color="#475569", va="center", zorder=5)
    for i in range(6):
        y = Y0 + i * DY; xl = 40
        ax.add_patch(FancyBboxPatch((xl - 3, y - 3), TH + 6, TH + 6, boxstyle="round,pad=0.5,rounding_size=6", fc="white", ec="#8b5e83" if i == 0 else "#94a3b8", lw=2, zorder=1)); ax.imshow(rem[i][t], extent=(xl, xl + TH, y + TH, y), interpolation="bilinear", zorder=2)
        ax.text(xl + TH + 12, y + TH / 2, rem_lab[i], fontsize=9.3, color="#8b5e83" if i == 0 else "#475569", va="center", fontweight="bold" if i == 0 else "normal", zorder=5)
        if i == 5: continue
        col = cols[i]; yc = y + TH / 2; nx = 490
        a_ = np.array([xl + TH + 150, yc]); n_ = np.array([nx, yc]); curve(ax, bez(np.array([xl + TH + 200, yc]), np.array([nx - 70, yc]), np.array([nx - 40, yc]), n_), "#8b5e83")
        ax.add_patch(Circle((nx, yc), 27, fc="#fdf1d6", ec="#e4c88b", lw=2, zorder=4)); ax.text(nx, yc - 4, "Split", fontsize=9, ha="center", va="center", fontweight="bold", color="#6b4f2a", zorder=5); ax.text(nx, yc + 9, f"rung {EXTR[i]+1}", fontsize=7.5, ha="center", va="center", color="#6b4f2a", zorder=5)
        up = bez(n_ + [27, -5], n_ + [150, -30], np.array([640, yc - 12]), np.array([700, yc - 2])); curve(ax, up, col)
        down = bez(n_ + [-8, 27], n_ + [-20, 70], np.array([140, y + DY - 6]), np.array([xl + TH / 2, y + DY - 2])); curve(ax, down, "#94a3b8")
        for path, c in ((up, col), (down, "#64748b")):                                    # moving dots along both branches
            for ph in (0, .5): p = path[int(((t / T * 3 + ph) % 1) * 59)]; ax.add_patch(Circle(p, 4.5, fc=c, ec="white", lw=1, zorder=6))
        xr = 700; ax.add_patch(FancyBboxPatch((xr - 3, y - 3), TH + 6, TH + 6, boxstyle="round,pad=0.5,rounding_size=6", fc="white", ec=col, lw=2.6, zorder=1)); ax.imshow(lay[i][t], extent=(xr, xr + TH, y + TH, y), interpolation="bilinear", zorder=2)
        ax.text(xr + TH + 18, y + 14, f"PATTERN {i+1}", fontsize=8, color=col, fontweight="bold", va="center", zorder=5); ax.text(xr + TH + 18, y + 34, names[i], fontsize=11.5, color="#1e293b", va="center", fontweight="bold", zorder=5)
        tx0, tw, th = xr + TH + 18, 330, 34; true, pred = trs[i]; sx = lambda a: tx0 + a * tw / (T - 1); sy = lambda v: y + 74 - (v - true.min()) / (np.ptp(true) + 1e-9) * th
        ax.plot(sx(np.arange(T)), sy(true), color="#cbd5e1", lw=3, zorder=3); ax.plot(sx(np.arange(T)), np.clip(sy(pred), y + 36, y + 80), color=col, lw=1.6, zorder=4); ax.scatter([sx(t)], [np.clip(sy(pred[t]), y + 36, y + 80)], color=col, s=22, zorder=5)
    ax.text(700, 686, "pictures are decoded from the autoencoder's numbers (soft);\nthe pattern pictures show the change magnified ×3", fontsize=8.5, color="#64748b", va="center", zorder=5)
    ax.text(700, Y0 + 5 * DY + 40, "grey line: true value over time   ·   coloured line: read from this rung's block", fontsize=9, color="#64748b", va="center", zorder=5)
    b_ = io.BytesIO(); fig.savefig(b_, format="png", dpi=100); plt.close(fig); b_.seek(0); frames.append(Image.open(b_).convert("RGB").resize((960, 540), Image.LANCZOS))
Image.fromarray(np.concatenate([np.array(frames[i]) for i in (0, 20)], 0)).save("/tmp/flow_check.png")
frames[0].save("docs/img/video_split_flow.gif", save_all=True, append_images=frames[1:], duration=95, loop=0, optimize=True); print(len(frames), "frames")
