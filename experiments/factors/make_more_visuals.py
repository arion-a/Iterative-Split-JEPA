"""Three more ways to see the result: (A) change the pair, change the layer; (B) peeling the motion out of a video; (C) messy coordinates -> organised blocks.
    PYTHONPATH=src:experiments/factors python make_more_visuals.py -> docs/img/{pair_changes_layer,peel_motion,messy_to_blocks}.png"""
import json, numpy as np, torch, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from train_ae import AE
OFF = np.cumsum([0, 1, 2, 1, 2, 3, 2, 1, 2, 1]); RED, ORG, BLU = "#c2410c", "#d97706", "#1d4ed8"
# ---------------- (A) change the pair, change the layer (exact toy, 3 layers hidden by a rotation)
rng = np.random.default_rng(11); N = 220; Q, _ = np.linalg.qr(rng.normal(size=(3, 3))); A = rng.normal(size=(N, 3)); X = A @ Q.T
fig = plt.figure(figsize=(14, 5.4)); fig.patch.set_facecolor("white")
cases = [("pairs that share the middle and slow layers\n(they differ only in the fast one)", [0], RED, "fast layer"), ("pairs that share the fast and slow layers\n(they differ only in the middle one)", [1], ORG, "middle layer"), ("pairs that share the fast and middle layers\n(they differ only in the slow one)", [2], BLU, "slow layer")]
for c, (ttl, diff, col, lab) in enumerate(cases):
    ax = fig.add_subplot(1, 3, c + 1, projection="3d"); B2 = A.copy(); B2[:, diff] = rng.normal(size=(N, len(diff))); Y = B2 @ Q.T
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], color="#cbd5e1", s=14, depthshade=False)
    for i in range(45): ax.plot([X[i, 0], Y[i, 0]], [X[i, 1], Y[i, 1]], [X[i, 2], Y[i, 2]], color="#334155", lw=1.1)
    v = Q[:, diff[0]]; ax.plot([-3.2 * v[0], 3.2 * v[0]], [-3.2 * v[1], 3.2 * v[1]], [-3.2 * v[2], 3.2 * v[2]], color=col, lw=4); ax.text(*(2.6 * v), "found: " + lab, color=col, fontsize=10.5, fontweight="bold", ha="center")
    ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_zlim(-3, 3); ax.set_axis_off(); ax.view_init(18, 35); ax.set_title(ttl, fontsize=11.5, loc="center")
fig.suptitle("The only knob is the pair: the same cloud gives a different layer for a different kind of pair", fontsize=15, fontweight="bold", y=1.02)
fig.savefig("docs/img/pair_changes_layer.png", dpi=140, bbox_inches="tight", facecolor="white"); plt.close(fig)
# ---------------- shared: load E62 pieces
Bk = torch.load("results/e62/blocks.pt"); ae = AE(); ae.load_state_dict(Bk["ae"]); ae.eval(); mean, mat = Bk["mean"].double(), Bk["matrix"].double(); inv = torch.linalg.inv(mat)
enc = lambda x: ae.encode(torch.from_numpy(x).permute(0, 3, 1, 2).float() / 255).detach().double()
dec = lambda z: ae.decode(z.float()).permute(0, 2, 3, 1).detach().numpy()
blocks = [b.double() for b in Bk["blocks"]]; D = 48
# ---------------- (B) peeling the motion out of a video
C = np.load("data/e62/clip.npz"); Xc = C["x"]; T = len(Xc); Zc = enc(Xc); Wc = (Zc - mean) @ mat; wbar, zbar = Wc.mean(0), Zc.mean(0)
comps = [(Wc - wbar) @ b @ b.T for b in blocks]; EXTR = [3, 4, 5, 6, 7]
core_c = (Wc - wbar) - sum(comps)
def rem_vid(n):
    w = (Wc - wbar) - sum(comps[k] for k in EXTR[:min(n, 5)]) - (core_c if n == 6 else 0); return dec(zbar + w @ inv)
vids = [rem_vid(n) for n in range(7)]
motion = [float(np.abs(v - v.mean(0, keepdims=True)).mean()) for v in vids]; motion = [m / motion[0] for m in motion]
labs = ["the video", "− cube position", "− cube colour", "− light colour", "− brightness", "− camera dist/elev", "− camera sideways"]
fig = plt.figure(figsize=(13.5, 6.6)); fig.patch.set_facecolor("white")
ax = fig.add_axes([.05, .30, .42, .50]); ax.bar(range(7), motion, color=["#64748b"] + ["#15803d", "#0e7490", "#3b5bdb", "#7c3aed", "#a21caf", "#475569"]); ax.set_xticks(range(7)); ax.set_xticklabels(labs, rotation=20, ha="right", fontsize=9.5)
for i, m in enumerate(motion): ax.text(i, m + .02, f"{100 * m:.0f}%", ha="center", fontsize=10)
ax.set_ylim(0, 1.15); ax.set_ylabel("amount of change left in the video"); ax.spines[["top", "right"]].set_visible(False); ax.set_title("Each rung removes a pattern, and the video gets calmer", fontsize=12.5, loc="left", fontweight="bold")
fig.text(.05, .985, "Peeling the motion out of a video", fontsize=18, fontweight="bold", va="top")
ts = [4, 16, 28, 40]
for r_, n in enumerate((0, 6)):
    for c, t in enumerate(ts):
        a = fig.add_axes([.52 + c * .115, .58 - r_ * .32, .105, .22]); a.imshow(vids[n][t], interpolation="bilinear"); a.set_xticks([]); a.set_yticks([])
fig.text(.52, .83, "the video (everything changing): frames 5, 17, 29, 41", fontsize=10.5, color="#334155", fontweight="bold"); fig.text(.52, .51, "after all six patterns are taken out", fontsize=10.5, color="#334155", fontweight="bold")
fig.text(.05, .07, "Measured on the 48-frame clip: average difference of each frame from the clip's average picture, decoded from the autoencoder's numbers (so everything looks soft).\nWhat remains after all six cuts is the small detail the encoder does not keep (gripper, arm pose, cube yaw).", fontsize=9.5, color="#64748b")
fig.savefig("docs/img/peel_motion.png", dpi=140, bbox_inches="tight", facecolor="white"); plt.close(fig); print("motion", [round(m, 2) for m in motion])
# ---------------- (C) messy coordinates -> organised blocks
Pz = np.load("data/e62/probe.npz"); Zp = torch.cat([enc(Pz["x"][i:i + 500]) for i in range(0, len(Pz["x"]), 500)]); Wp = ((Zp - mean) @ mat); Fp = Pz["f"]
Pcore = torch.eye(D, dtype=torch.double) - sum(b @ b.T for b in blocks); ec, vc = torch.linalg.eigh(Pcore); Qcore = vc[:, ec > .5]; Vall = torch.cat(blocks + [Qcore], 1)
names = ["cube position", "cube colour", "light tint", "brightness", "cam. dist/elev", "cam. azimuth"]; groups = [3, 4, 5, 6, 7, 8]
def corrmat(coords):
    cm = np.zeros((coords.shape[1], 6)); c = coords.numpy()
    for gi, g in enumerate(groups):
        cm[:, gi] = max_ = np.max([np.abs([np.corrcoef(c[:, i], Fp[:, j])[0, 1] for i in range(coords.shape[1])]) for j in range(OFF[g], OFF[g + 1])], 0)
    return cm
Mraw = corrmat(Wp); Mrot = corrmat(Wp @ Vall)
order = np.argsort(-Mraw.max(1)); Mraw_s = Mraw[order]
sizes = [x.shape[1] for x in blocks] + [Qcore.shape[1]]; edges = np.cumsum([0] + sizes)
fig, axs = plt.subplots(1, 2, figsize=(11.5, 8.2)); fig.patch.set_facecolor("white")
for ax_, M_, ttl in ((axs[0], Mraw_s, "Before: the 48 numbers of the representation\neach number mixes several factors"), (axs[1], Mrot, "After: the same 48 numbers, rotated into rung blocks\neach block follows one factor")):
    ax_.imshow(M_, cmap="Blues", vmin=0, vmax=1, aspect="auto"); ax_.set_xticks(range(6)); ax_.set_xticklabels(names, rotation=35, ha="right", fontsize=9.5); ax_.set_title(ttl, fontsize=12.5, loc="left", fontweight="bold"); ax_.set_ylabel("coordinate (48)")
for e_ in edges[1:-1]: axs[1].axhline(e_ - .5, color="#475569", lw=.8)
for k in range(9):
    lab = "rungs 1–3" if k < 3 else (["rung 4", "rung 5", "rung 6", "rung 7", "rung 8", "left over"][k - 3])
    if k >= 3 or k == 0: axs[1].text(6.1, (edges[k] + edges[k + 1]) / 2 - .5 if k >= 3 else (edges[0] + edges[3]) / 2 - .5, lab, fontsize=9.5, va="center", color="#334155")
fig.text(.03, .985, "From a tangle to a staircase", fontsize=18, fontweight="bold", va="top"); fig.text(.03, .945, "shade = how strongly a coordinate follows a factor (absolute correlation, 0 to 1); rungs 1–3 are the three factors the encoder does not keep", fontsize=10, color="#64748b", va="top")
fig.tight_layout(rect=[0, 0, .93, .93]); fig.savefig("docs/img/messy_to_blocks.png", dpi=140, bbox_inches="tight", facecolor="white"); print("raw mean max", Mraw.max(1).mean().round(2), "rot mean max (rungs4-8)", Mrot[edges[3]:edges[8]].max(1).mean().round(2))
