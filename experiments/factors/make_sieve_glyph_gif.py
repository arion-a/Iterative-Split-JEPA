"""Sieve clip, clearer version: the pattern each rung catches is shown as a simple animated glyph driven by the values read from that rung's block
(a dot on a table, a colour swatch, a lamp colour, a brightness meter, a camera on an arc), not as a decoded video. Real videos appear only at the start and the end.
    PYTHONPATH=src:experiments/factors python make_sieve_glyph_gif.py -> docs/img/video_sieve_flow.gif"""
import io, numpy as np, torch, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Polygon
from PIL import Image
from isj import audits
from train_ae import AE
B = torch.load("results/e62/blocks.pt"); OFF = np.cumsum([0, 1, 2, 1, 2, 3, 2, 1, 2, 1])
ae = AE(); ae.load_state_dict(B["ae"]); ae.eval(); mean, mat = B["mean"].double(), B["matrix"].double(); inv = torch.linalg.inv(mat)
enc = lambda x: ae.encode(torch.from_numpy(x).permute(0, 3, 1, 2).float() / 255).detach().double()
C = np.load("data/e62/clip.npz"); Xc, Fc = C["x"], C["f"]; T = len(Xc); Zc = enc(Xc); Wc = (Zc - mean) @ mat; wbar, zbar = Wc.mean(0), Zc.mean(0)
P = np.load("data/e62/probe.npz"); Zp = torch.cat([enc(P["x"][i:i + 500]) for i in range(0, len(P["x"]), 500)]); Wp = (Zp - mean) @ mat; Fp = torch.from_numpy(P["f"]).double()
blocks = [b.double() for b in B["blocks"]]; dec = lambda z: ae.decode(z.float()).permute(0, 2, 3, 1).detach().numpy()
comps = [(Wc - wbar) @ b @ b.T for b in blocks]; EXTR = [3, 4, 5, 6, 7]
rem0 = dec(zbar + (Wc - wbar) @ inv); rem5 = dec(zbar + ((Wc - wbar) - sum(comps)) @ inv)         # real videos: everything, and what is left once all five patterns are taken out
def read(g):                                                        # values of factor group g, read from rung g's block (ridge fitted on the probe set)
    V = blocks[g]; X = Wp @ V; outs = []
    for j in range(OFF[g], OFF[g + 1]):
        y = (Fp[:, j] - Fp[:, j].mean()) / Fp[:, j].std(); w = audits.ridge_fit(X[:6000], y[:6000, None]); p = (torch.cat([Wc @ V, torch.ones(T, 1, dtype=torch.double)], 1) @ w).squeeze(1)
        outs.append((p * Fp[:, j].std() + Fp[:, j].mean()).numpy())
    return np.stack(outs, 1)
vals = {g: read(g) for g in EXTR}; true = {g: Fc[:, OFF[g]:OFF[g + 1]] for g in EXTR}
coords = {}; ndim = {}
for g_ in EXTR:
    r_ = vals[g_]; coords[g_] = (r_ - r_.mean(0)) / (r_.std(0) + 1e-9); ndim[g_] = r_.shape[1]
cyc = {}
for g_ in EXTR:
    f_ = np.abs(np.fft.rfft(vals[g_][:, 0] - vals[g_][:, 0].mean())); cyc[g_] = int(np.argmax(f_[1:9]) + 1)
names = ["where the cube is", "what colour the cube is", "the colour of the light", "how bright the scene is", "how far the camera is"]
short = ["cube position", "cube colour", "light colour", "brightness", "camera"]; cols = ["#15803d", "#0e7490", "#3b5bdb", "#7c3aed", "#a21caf"]
LO = np.array([0.0, -1, -1, -np.pi / 2, -0.06, -0.06, 0.1, 0.1, 0.1, -0.4, -0.4, 0.25, 0.38, 0.6, -0.5]); HI = np.array([0.04, 1, 1, np.pi / 2, 0.06, 0.06, 1, 1, 1, 0.4, 0.4, 0.75, 0.52, 0.95, 0.5])
def glyph(ax, i, t, x0, y0, S=92):
    g = EXTR[i]; v = vals[g][t]; cx, cy = x0 + S / 2, y0 + S / 2
    if i == 0:                                                      # cube position: a dot on a table, with a short trail
        ax.add_patch(Rectangle((x0 + 8, y0 + 8), S - 16, S - 16, fc="#fde9d6", ec="#d9b99b", lw=1.5, zorder=3))
        for k in range(8, -1, -1):
            tt = max(0, t - k); p = vals[3][tt]; px, py = cx + p[0] / 0.06 * 30, cy + p[1] / 0.06 * 30
            ax.add_patch(Circle((px, py), 5 + (8 - k) * .35, fc=cols[0], alpha=.15 + .1 * (8 - k) if k else 1, ec="none", zorder=4))
    elif i == 1:                                                    # colour: a swatch
        c = np.clip((v - LO[6:9]) / (HI[6:9] - LO[6:9]), 0, 1) * .9 + .1; c = np.clip(v, 0, 1)
        ax.add_patch(Circle((cx, cy), 30, fc=c, ec="#334155", lw=2, zorder=4)); ax.add_patch(Circle((cx - 9, cy - 10), 7, fc="white", alpha=.35, ec="none", zorder=5))
    elif i == 2:                                                    # light colour: a glowing lamp tint
        c = np.array([1 + v[0], 1.0, 1 + v[1]]); c = np.clip(c / c.max(), 0, 1)
        for r_, a in ((38, .25), (30, .45), (22, .8)): ax.add_patch(Circle((cx, cy), r_, fc=c, alpha=a, ec="none", zorder=3))
        ax.add_patch(Circle((cx, cy), 9, fc="white", ec="none", zorder=5))
    elif i == 3:                                                    # brightness: a meter and a sun
        lvl = np.clip((v[0] - .25) / .5, 0, 1)
        ax.add_patch(Rectangle((x0 + 14, y0 + 10), 18, S - 20, fc="white", ec="#334155", lw=1.8, zorder=3)); ax.add_patch(Rectangle((x0 + 14, y0 + 10 + (S - 20) * (1 - lvl)), 18, (S - 20) * lvl, fc="#facc15", ec="none", zorder=4))
        ax.add_patch(Circle((x0 + 62, cy), 8 + 14 * lvl, fc="#fde047", alpha=.55 + .4 * lvl, ec="#ca8a04", lw=1.5, zorder=4))
        for a in np.linspace(0, 2 * np.pi, 9)[:-1]: ax.plot([x0 + 62 + (12 + 14 * lvl) * np.cos(a), x0 + 62 + (17 + 18 * lvl) * np.cos(a)], [cy + (12 + 14 * lvl) * np.sin(a), cy + (17 + 18 * lvl) * np.sin(a)], color="#ca8a04", lw=1.5, zorder=4)
    else:                                                           # camera: a camera on an arc around the scene (distance and elevation)
        ox, oy = x0 + 64, y0 + S - 18; r = 22 + (v[0] - .38) / .14 * 30; e = v[1]; px, py = ox - r * np.cos(e), oy - r * np.sin(e)
        ax.add_patch(Rectangle((ox - 7, oy - 7), 14, 14, fc="#f97316", ec="#9a3412", lw=1.2, zorder=4)); th = np.linspace(0.5, 1.05, 20); ax.plot(ox - 52 * np.cos(th), oy - 52 * np.sin(th), color="#cbd5e1", lw=1.5, ls="--", zorder=3)
        ax.plot([px, ox], [py, oy], color="#a21caf", lw=1.4, ls=":", zorder=4); ax.add_patch(FancyBboxPatch((px - 8, py - 6), 16, 12, boxstyle="round,pad=0.5,rounding_size=2", fc="#a21caf", ec="white", zorder=5))
BGTOP, BGBOT = np.array([197, 225, 229]) / 255, np.array([227, 236, 228]) / 255
bg = (BGTOP[None, None, :] * (1 - np.linspace(0, 1, 64)[:, None, None]) + BGBOT[None, None, :] * np.linspace(0, 1, 64)[:, None, None]) * np.ones((64, 2, 3))
def bez(p0, p1, p2, p3, n=60):
    t = np.linspace(0, 1, n)[:, None]; return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3
W, H, TH, DY, Y0 = 1280, 720, 92, 104, 96; frames = []
for t in range(T):
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off"); ax.imshow(bg, extent=(0, W, H, 0), aspect="auto", zorder=0)
    ax.text(40, 30, "SieveJEPA: Sieving patterns out of video data", fontsize=22, fontweight="bold", color="#1e293b", va="center", zorder=5)
    ax.text(40, 62, "each rung of the sieve catches one hidden pattern (right: that rung's own numbers over time) and lets the rest fall through (down)", fontsize=11, color="#475569", va="center", zorder=5)
    for i in range(6):
        y = Y0 + i * DY; yc = y + TH / 2
        if i in (0, 5):                                              # real video thumbnails: the whole video, and what is left at the end
            ax.add_patch(FancyBboxPatch((37, y - 3), TH + 6, TH + 6, boxstyle="round,pad=0.5,rounding_size=6", fc="white", ec="#8b5e83" if i == 0 else "#94a3b8", lw=2, zorder=1)); ax.imshow((rem0 if i == 0 else rem5)[t], extent=(40, 40 + TH, y + TH, y), interpolation="bilinear", zorder=2)
        if i == 5: ax.text(150, yc, "WHAT IS LEFT\nonly the camera's sideways swing", fontsize=9.5, color="#475569", fontweight="bold", va="center", zorder=5)
        if i < 5:                                                    # pills: the patterns still mixed together at this level
            for k, j in enumerate(range(i, 5)):
                ax.add_patch(FancyBboxPatch((150, y + 24 + k * 14 + (0 if i else 6), ) if False else (150, y + 22 + k * 14), 112, 11, boxstyle="round,pad=0.3,rounding_size=5", fc=cols[j], ec="none", alpha=.9, zorder=3)); ax.text(206, y + 27.5 + k * 14, short[j], fontsize=7.6, color="white", ha="center", va="center", zorder=4, fontweight="bold")
            minus = ["", "minus the cube's position", "minus the cube's colour", "minus the light's colour", "minus the brightness"]
            if i == 0: ax.text(150, y + 8, "ENTANGLED VIDEO", fontsize=10, color="#8b5e83", fontweight="bold", va="center", zorder=4); ax.text(300, y + 8, "everything changes at once", fontsize=8.5, color="#8b5e83", va="center", zorder=4)
            else: ax.text(150, y + 8, minus[i], fontsize=9.5, color="#475569", fontweight="bold", va="center", zorder=4)
        if i == 5: continue
        col = cols[i]; nx = 490; n_ = np.array([nx, yc])
        ax.plot(*bez(np.array([290, yc]), np.array([nx - 100, yc]), np.array([nx - 50, yc]), n_).T, color="#8b5e83", lw=2.6, alpha=.8, zorder=3)
        ax.add_patch(Circle((nx, yc), 27, fc="#fdf1d6", ec="#e4c88b", lw=2, zorder=4)); ax.text(nx, yc - 4, "Sieve", fontsize=9, ha="center", va="center", fontweight="bold", color="#6b4f2a", zorder=5); ax.text(nx, yc + 9, f"rung {EXTR[i]+1}", fontsize=7.5, ha="center", va="center", color="#6b4f2a", zorder=5)
        up = bez(n_ + [27, -5], n_ + [100, -30], np.array([600, yc - 12]), np.array([647, yc - 6])); ax.plot(up[:, 0], up[:, 1], color=col, lw=2.6, alpha=.85, zorder=3)
        down = bez(n_ + [-8, 27], n_ + [-14, 62], np.array([372, y + DY - 6]), np.array([346, y + DY + 8])); ax.plot(down[:, 0], down[:, 1], color="#94a3b8", lw=2.6, alpha=.85, zorder=3)
        for path, c in ((up, col), (down, "#64748b")):
            for ph in (0, .5): p = path[int(((t / T * 3 + ph) % 1) * 59)]; ax.add_patch(Circle(p, 4.5, fc=c, ec="white", lw=1, zorder=6))
        xr = 650; g = EXTR[i]; HW, HH = 210, 80; Mk = coords[g]                                                 # the rung's own numbers over time, drawn as a strip
        ax.add_patch(FancyBboxPatch((xr - 3, y - 3), HW + 6, HH + 6, boxstyle="round,pad=0.5,rounding_size=6", fc="white", ec=col, lw=2.6, zorder=1))
        ax.imshow(Mk.T, extent=(xr, xr + HW, y + HH, y), cmap="coolwarm", vmin=-2, vmax=2, aspect="auto", interpolation="nearest", zorder=2)
        cxp = xr + (t + .5) / T * HW; ax.plot([cxp, cxp], [y, y + HH], color="#111827", lw=1.8, zorder=4)
        ax.text(xr, y + HH + 13, f"{ndim[g]} read-out{'s' if ndim[g] > 1 else ''}", fontsize=8.2, color="#475569", va="center", zorder=5); ax.annotate("", (xr + HW, y + HH + 13), (xr + HW - 52, y + HH + 13), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.8), zorder=5); ax.text(xr + HW - 56, y + HH + 13, "time", fontsize=8.2, color=col, fontweight="bold", ha="right", va="center", zorder=5)
        tx0, tw, th = 892, 340, 42; ax.text(tx0, y + 8, f"PATTERN {i+1}", fontsize=8, color=col, fontweight="bold", va="center", zorder=5); ax.text(tx0 + 74, y + 8, names[i], fontsize=11.5, color="#1e293b", fontweight="bold", va="center", zorder=5)
        tr, pr = true[g][:, 0], vals[g][:, 0]; lo, hi = tr.min(), tr.max(); sx = lambda a: tx0 + a * tw / (T - 1); sy = lambda v_: np.clip(y + 62 - (v_ - lo) / (hi - lo + 1e-9) * th, y + 20, y + 66)
        ax.plot(sx(np.arange(T)), sy(tr), color="#cbd5e1", lw=3, zorder=3); ax.plot(sx(np.arange(T)), sy(pr), color=col, lw=1.8, zorder=4); ax.scatter([sx(t)], [sy(pr[t])], color=col, s=24, zorder=5)
        ax.annotate("", (tx0 + tw, y + HH + 13), (tx0 + tw - 52, y + HH + 13), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.8), zorder=5); ax.text(tx0 + tw - 56, y + HH + 13, "time", fontsize=8.2, color=col, fontweight="bold", ha="right", va="center", zorder=5)
        ax.text(tx0, y + HH + 13, f"repeats about {cyc[g]}× in the clip", fontsize=8.6, color="#334155", va="center", zorder=5)
    ax.text(650, Y0 + 5 * DY + 26, "left strip: values read from the numbers the rung caught (blue low, red high; black line = now)\nright: grey = true value of the factor, colour = read from those numbers", fontsize=9, color="#64748b", va="center", zorder=5)
    ax.text(650, 672, "the two videos are decoded from the autoencoder's numbers (soft);\n'repeats' = strongest rhythm in the reading", fontsize=8.3, color="#64748b", va="center", zorder=5)
    b_ = io.BytesIO(); fig.savefig(b_, format="png", dpi=100); plt.close(fig); b_.seek(0); frames.append(Image.open(b_).convert("RGB").resize((960, 540), Image.LANCZOS))
Image.fromarray(np.concatenate([np.array(frames[i]) for i in (0, 12, 30)], 0)).save("/tmp/sieve_check.png")
frames[0].save("docs/img/video_sieve_flow.gif", save_all=True, append_images=frames[1:], duration=95, loop=0, optimize=True)
frames[24].save("docs/img/video_sieve_flow_strip.png"); print(len(frames), "frames")
