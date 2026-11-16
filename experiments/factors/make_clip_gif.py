"""Intuitive clip: one video where several things change at once is split by the ladder into one 'layer video' per rung.
Each layer video decodes only that block's part of the change (everything else held at the clip average).
    PYTHONPATH=src:experiments/factors python make_clip_gif.py -> docs/img/video_split.gif"""
import json, io, numpy as np, torch, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from PIL import Image
from isj import audits
from train_ae import AE
r = json.load(open("results/e62/e62.json")); B = torch.load("results/e62/blocks.pt"); OFF = np.cumsum([0, 1, 2, 1, 2, 3, 2, 1, 2, 1])
ae = AE(); ae.load_state_dict(B["ae"]); ae.eval(); mean, mat = B["mean"].double(), B["matrix"].double(); inv = torch.linalg.inv(mat)
enc = lambda x: ae.encode(torch.from_numpy(x).permute(0, 3, 1, 2).float() / 255).detach().double()
C = np.load("data/e62/clip.npz"); Xc, Fc = C["x"], C["f"]; T = len(Xc); Zc = enc(Xc); Wc = (Zc - mean) @ mat
P = np.load("data/e62/probe.npz"); Zp = torch.cat([enc(P["x"][i:i + 500]) for i in range(0, len(P["x"]), 500)]); Wp = (Zp - mean) @ mat; Fp = torch.from_numpy(P["f"]).double()
D = Wc.shape[1]; blocks = [b.double() for b in B["blocks"]]
Pcore = torch.eye(D, dtype=torch.double) - sum(b @ b.T for b in blocks); ecore, vcore = torch.linalg.eigh(Pcore); Qcore = vcore[:, ecore > .5]
layers = [(3, blocks[3], "Rung 4 · cube position", "#15803d", 3), (4, blocks[4], "Rung 5 · cube colour", "#0e7490", 4), (5, blocks[5], "Rung 6 · light tint", "#1d4ed8", 5),
          (6, blocks[6], "Rung 7 · brightness", "#7c3aed", 6), (7, blocks[7], "Rung 8 · camera distance / elevation", "#a21caf", 7), (8, Qcore, "Left over · camera sideways angle", "#475569", 8)]
zbar = Zc.mean(0); wbar = Wc.mean(0)
def decode(zw):                                  # whitened -> latent -> image
    z = (zbar + (zw - 0) @ inv).float()
    with torch.no_grad(): return ae.decode(z)[:, :, :, :].permute(0, 2, 3, 1).numpy()
GAIN = 3.0; vids, traces = [], []
for k, V, name, col, g in layers:
    comp = (Wc - wbar) @ V @ V.T; vids.append(decode(comp + 0 * wbar + (zbar - zbar) @ inv * 0 + 0)) if False else None
    zlay = zbar + comp @ inv; 
    with torch.no_grad(): v_ = ae.decode(zlay.float()).permute(0, 2, 3, 1).numpy(); base = ae.decode(zbar.float()[None]).permute(0, 2, 3, 1).numpy()
    vids.append(np.clip(base + GAIN * (v_ - base), 0, 1))
    j = OFF[g]; y = (Fp[:, j] - Fp[:, j].mean()) / Fp[:, j].std(); X = Wp @ V; w_ = audits.ridge_fit(X[:6000], y[:6000, None]); pred = (torch.cat([Wc @ V, torch.ones(T, 1, dtype=torch.double)], 1) @ w_).squeeze(1)
    ytrue = (torch.from_numpy(Fc[:, j]) - Fp[:, j].mean()) / Fp[:, j].std(); traces.append((ytrue.numpy(), pred.numpy()))
    print(name, "corr(true, recovered) =", round(float(np.corrcoef(ytrue.numpy(), pred.numpy())[0, 1]), 2))
frames = []
for t in range(T):
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100); fig.patch.set_facecolor("white")
    fig.text(.03, .955, "One video, split into the patterns hiding inside it", fontsize=22, fontweight="bold", va="top")
    fig.text(.03, .905, "left: everything changes at once · right: what each rung's block recovered, the rest of the scene frozen (change shown ×3)", fontsize=11.5, color="#475569", va="top")
    a = fig.add_axes([.03, .12, .27, .70]); a.imshow(Xc[t], interpolation="bilinear"); a.set_xticks([]); a.set_yticks([]); a.set_title("the video (all changing together)", fontsize=11.5, loc="left")
    fig.text(.165, .075, "frame %02d / %d" % (t + 1, T), ha="center", fontsize=10, color="#64748b")
    for i, (k, V, name, col, g) in enumerate(layers):
        row, c = divmod(i, 3); x0 = .34 + c * .22; y0 = .50 - row * .43
        a = fig.add_axes([x0, y0 + .10, .19, .25]); a.imshow(vids[i][t], interpolation="bilinear"); a.set_xticks([]); a.set_yticks([])
        for s_ in a.spines.values(): s_.set_edgecolor(col); s_.set_linewidth(3)
        fig.text(x0 + .095, y0 + .365, name, ha="center", fontsize=9.6, color=col, fontweight="bold")
        b = fig.add_axes([x0 + .01, y0 - .005, .18, .085]); yt, yp = traces[i]; b.plot(yt, color="#cbd5e1", lw=2.2); b.plot(yp, color=col, lw=1.4); b.scatter([t], [yp[t]], color=col, s=18, zorder=3); b.set_xticks([]); b.set_yticks([]); b.set_xlim(0, T - 1)
        for s_ in ("top", "right", "left", "bottom"): b.spines[s_].set_visible(False)
    fig.text(.34, .035, "grey line = the true value of that factor over time · coloured line = what the block's numbers say", fontsize=9.5, color="#64748b")
    b_ = io.BytesIO(); fig.savefig(b_, format="png", dpi=100); plt.close(fig); b_.seek(0); frames.append(Image.open(b_).convert("RGB").resize((960, 540), Image.LANCZOS))
Image.fromarray(np.concatenate([np.array(frames[i]) for i in (0, 12)], 0)[::2, ::2]).save("/tmp/clip_check.png")
frames[0].save("docs/img/video_split.gif", save_all=True, append_images=frames[1:], duration=95, loop=0, optimize=True); print(len(frames), "frames", T * .095, "s")
