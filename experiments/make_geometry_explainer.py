"""One-page geometric explainer of the splitting equations, using a hand-checkable 2-number example."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
RED, BLUE, GREY, GRN = "#c2410c", "#1d4ed8", "#64748b", "#15803d"
t = np.array([.8, .6]); s = np.array([-.6, .8])                      # fast direction t, slow direction s (orthonormal)
delta = np.array([2., -1., 1., -2.]); a = delta / 2 + .3; b = a - delta; sig = np.array([-1.2, -.3, .5, 1.1])
U = a[:, None] * t + sig[:, None] * s; V = b[:, None] * t + sig[:, None] * s; Dm = U - V
M = Dm.T @ Dm / 4; lam, vec = np.linalg.eigh(M); lam, vec = lam[::-1], vec[:, ::-1]
rng = np.random.default_rng(2); dl = rng.normal(0, 1.58, 400); Dn = dl[:, None] * t + rng.normal(0, .15, 400)[:, None] * s
Mn = Dn.T @ Dn / 400; ln, vn = np.linalg.eigh(Mn); ln, vn = ln[::-1], vn[:, ::-1]
fig, axs = plt.subplots(2, 3, figsize=(14, 8.6)); ax = axs.ravel()
def setup(a_, ttl):
    a_.set_xlim(-3.2, 3.2); a_.set_ylim(-3.2, 3.2); a_.set_aspect("equal"); a_.axhline(0, color="#e2e8f0", lw=1); a_.axvline(0, color="#e2e8f0", lw=1); a_.set_title(ttl, fontsize=10.5, loc="left")
setup(ax[0], "① Pairs (u, v): same slow coordinate,\nfresh fast coordinate")
ax[0].annotate("", t * 2.6, -t * 2.6, arrowprops=dict(arrowstyle="<->", color=RED, lw=1)); ax[0].text(*(t * 2.7), "fast axis", color=RED, fontsize=8.5)
ax[0].annotate("", s * 2.2, -s * 2.2, arrowprops=dict(arrowstyle="<->", color=BLUE, lw=1)); ax[0].text(*(s * 2.3 + [-.2, 0]), "slow axis", color=BLUE, fontsize=8.5, ha="right")
for i in range(4): ax[0].plot([U[i, 0], V[i, 0]], [U[i, 1], V[i, 1]], color=GREY, lw=1.2); ax[0].scatter(*U[i], color=BLUE, s=36, zorder=3); ax[0].scatter(*V[i], color=RED, s=36, zorder=3); ax[0].text(*(U[i] + [.08, .1]), f"u{i+1}", fontsize=8); ax[0].text(*(V[i] + [.08, .1]), f"v{i+1}", fontsize=8)
setup(ax[1], "② Subtract: D = u − v\n(every D lies along the fast axis)")
for i in range(4): ax[1].annotate("", Dm[i], (0, 0), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.8)); ax[1].text(*(Dm[i] * 1.06 + [.1, 0]), f"D{i+1}=({Dm[i,0]:.1f}, {Dm[i,1]:.1f})", fontsize=8)
setup(ax[2], "③ M = mean of D·Dᵀ: the shape of the D cloud\n(more realistic: 400 pairs with a little noise)")
ax[2].scatter(Dn[:, 0], Dn[:, 1], s=5, color=GREY, alpha=.5); th = np.linspace(0, 2 * np.pi, 200)
for k, c in ((0, RED), (1, BLUE)): ax[2].annotate("", vn[:, k] * np.sqrt(ln[k]) * 1.9, (0, 0), arrowprops=dict(arrowstyle="-|>", color=c, lw=2.4)); ax[2].text(*(vn[:, k] * np.sqrt(ln[k]) * 1.9 * 1.1 + [.1, .1]), f"v{k+1}, λ{k+1}={ln[k]:.2f}", color=c, fontsize=9)
ell = (vn * np.sqrt(ln)) @ np.stack([np.cos(th), np.sin(th)]) * 1.9; ax[2].plot(ell[0], ell[1], color=GREY, lw=1, ls="--")
ax[3].set_title("④ Why the minimum is the short axis:\naverage squared length of D along direction q(φ)", fontsize=10.5, loc="left")
ph = np.linspace(0, 360, 361); q = np.stack([np.cos(np.deg2rad(ph)), np.sin(np.deg2rad(ph))]); f = ((Dm @ q) ** 2).mean(0)
ax[3].plot(ph, f, color=RED, lw=2); th0 = np.rad2deg(np.arctan2(.6, .8)); ax[3].axvline(th0 + 90, color=GRN, ls=":"); ax[3].axvline(th0, color=RED, ls=":")
ax[3].text(th0 + 6, 2.05, f"fast axis\n{th0:.0f}°: max = λ1 = 2.5", color=RED, fontsize=8.5); ax[3].text(th0 + 98, 1.2, f"slow axis {th0+90:.0f}°:\nmin = λ2 = 0", color=GRN, fontsize=8.5)
ax[3].set_xlabel("direction φ (degrees)"); ax[3].set_ylabel("mean (qᵀD)²"); ax[3].spines[["top", "right"]].set_visible(False)
ax[4].set_title("⑤ Gap: how sharp the cut is", fontsize=10.5, loc="left"); ax[4].bar(["λ1", "λ2"], ln, color=[RED, BLUE]); ax[4].set_ylabel("eigenvalue (noisy example)")
for i, v in enumerate(ln): ax[4].text(i, v + .05, f"{v:.3f}", ha="center", fontsize=9)
ax[4].text(1.0, 1.4, f"gap = λ1 / λ2\n= {ln[0]/ln[1]:.0f}", ha="center", fontsize=12, color=GRN); ax[4].spines[["top", "right"]].set_visible(False)
setup(ax[5], "⑥ Angle: found block vs true block\n(here the true fast axis is the x-axis)")
tr = np.array([1., 0]); fo = vn[:, 0] * np.sign(vn[0, 0]); ang = np.rad2deg(np.arccos(abs(tr @ fo)))
ax[5].annotate("", tr * 2.6, (0, 0), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=2.4)); ax[5].annotate("", fo * 2.6, (0, 0), arrowprops=dict(arrowstyle="-|>", color=RED, lw=2.4))
ax[5].text(2.7, -.35, "true", color=BLUE, fontsize=9); ax[5].text(*(fo * 2.7 + [.05, .1]), "found V", color=RED, fontsize=9)
tt = np.linspace(0, np.deg2rad(ang), 30); ax[5].plot(1.1 * np.cos(tt), 1.1 * np.sin(tt), color="k", lw=1); ax[5].text(1.2, .35, f"θ = {ang:.0f}°\ncos θ = |tᵀV| = {abs(tr@fo):.2f}", fontsize=9.5)
fig.tight_layout(); fig.savefig("docs/img/geometry_explainer.png", dpi=150, bbox_inches="tight", facecolor="white")
print("M =", np.round(M, 3).tolist(), "eig", np.round(lam, 3), "vec1", np.round(vec[:, 0], 3), "noisy eig", np.round(ln, 3), "angle", round(ang, 1))
