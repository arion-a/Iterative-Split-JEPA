"""Figures for docs/MATH_EXPLAINED.md: a 2-D toy (group a fast, group b slow, one number each) pushed through the real operations."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
rng = np.random.default_rng(4)
def obs(z, s):                      # two alternating additive tanh couplings, as in CouplingMap
    x = z.copy(); x[:, 0] = z[:, 0] + s * np.tanh(1.5 * z[:, 1]); x[:, 1] = z[:, 1] + s * np.tanh(1.5 * x[:, 0]); return x
def bend(z, s, th=0.6):             # observation, then a fixed rotation (the encoder is some invertible map)
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]]); return obs(z, s) @ R.T
def whiten(r, ref):
    mu = ref.mean(0); C = np.cov((ref - mu).T); ev, V = np.linalg.eigh(C); W = V @ np.diag(ev ** -0.5) @ V.T; return lambda q: (q - mu) @ W
N = 6000
z = rng.standard_normal((N, 2))                      # columns: a (fast), b (slow)
def pairs_rung1(n):                                  # agree on b, redraw a
    u = rng.standard_normal((n, 2)); v = u.copy(); v[:, 0] = rng.standard_normal(n); return u, v
c = {"a": "#d9480f", "b": "#1c7ed6", "g": "#868e96"}
def grid(ax, f, lim, title):
    for t in np.linspace(-2.5, 2.5, 11):
        s = np.linspace(-2.5, 2.5, 80)
        for line in (np.c_[s, np.full_like(s, t)], np.c_[np.full_like(s, t), s]):
            p = f(line); ax.plot(p[:, 0], p[:, 1], color="#cbd2d9", lw=.8)
    p = f(z[:600]); ax.scatter(p[:, 0], p[:, 1], s=4, color=c["g"], alpha=.5)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal"); ax.set_title(title, fontsize=10); ax.set_xticks([]); ax.set_yticks([])
# ---------- Figure 1: transformations (strength 1.2 bend)
s = 1.2; ref = bend(z, s); wh = whiten(ref, ref)
fig, axs = plt.subplots(1, 4, figsize=(15, 4.2))
grid(axs[0], lambda q: q, 3.2, "1. hidden values  $z=(z_a,z_b)$\ngrid = lines of constant $z_a$ or $z_b$")
grid(axs[1], lambda q: obs(q, s), 3.8, "2. observation  $x=f(z)$\nnonlinear bend (tanh coupling)")
grid(axs[2], lambda q: bend(q, s), 3.8, "3. embedding  $r=g(x)$\n(here: a bend then a turn)")
grid(axs[3], lambda q: wh(bend(q, s)), 3.2, r"4. whitened  $\tilde r=C^{-1/2}(r-\mu)$" + "\ncovariance becomes the identity (bend remains)")
axs[0].annotate("", xy=(2.6, 0), xytext=(-2.6, 0), arrowprops=dict(arrowstyle="<->", color=c["a"])); axs[0].text(0, -.35, "$z_a$ fast", color=c["a"], ha="center", fontsize=9)
axs[0].annotate("", xy=(0, 2.6), xytext=(0, -2.6), arrowprops=dict(arrowstyle="<->", color=c["b"])); axs[0].text(.15, 2.2, "$z_b$ slow", color=c["b"], fontsize=9)
fig.suptitle("What happens to the dots before the splitter sees them (2-number toy; real runs: 4 numbers per group)", fontsize=11); fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig("docs/img/math_fig1.png", dpi=170); plt.close(fig)
# ---------- Figure 2: one rung, mild bend (0.3) vs strong bend (2.0)
def rung(s, ax_row, label):
    ref = bend(z, s); wh = whiten(ref, ref); u, v = pairs_rung1(20000); ru, rv = wh(bend(u, s)), wh(bend(v, s)); D = ru - rv
    M = D.T @ D / len(D); lam, E = np.linalg.eigh(M); lam, E = lam[::-1], E[:, ::-1]
    p = wh(bend(z[:700], s)); ax_row[0].scatter(p[:, 0], p[:, 1], s=4, color=c["g"], alpha=.4)
    for i in range(5):
        ax_row[0].plot([ru[i, 0], rv[i, 0]], [ru[i, 1], rv[i, 1]], "-o", color=c["a"], ms=4)
    ax_row[0].set_title(f"{label}\nmatched pairs (orange): same $z_b$, different $z_a$", fontsize=9)
    ax_row[1].scatter(D[:1500, 0], D[:1500, 1], s=3, color=c["a"], alpha=.4)
    for j, col in zip(range(2), ("#000", "#555")):
        ax_row[1].annotate("", xy=E[:, j] * 3.2 * np.sqrt(max(lam[j], 0) / lam[0]) * 1.0, xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=col, lw=2))
    ax_row[1].set_title(f"differences $D=\\tilde r_u-\\tilde r_v$;  eigenvalues $\\lambda_1$={lam[0]:.2f}, $\\lambda_2$={lam[1]:.2f}\ngap $\\lambda_1/\\lambda_2$ = {lam[0]/lam[1]:.1f}", fontsize=9)
    h = E[:, 1]; proj = (p @ h)[:, None] * h[None, :]
    ax_row[2].scatter(p[:, 0], p[:, 1], s=3, color="#e9ecef"); ax_row[2].scatter(proj[:, 0], proj[:, 1], s=5, color=c["b"], alpha=.6)
    ax_row[2].annotate("", xy=E[:, 0] * 2.5, xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=c["a"], lw=2)); ax_row[2].text(*(E[:, 0] * 2.7), "$V_1$ removed", color=c["a"], fontsize=9)
    ax_row[2].set_title("keep the short axis: $H_1=e_2$\n(dots projected onto it, blue)", fontsize=9)
    for a in ax_row: a.set_xlim(-3.5, 3.5); a.set_ylim(-3.5, 3.5); a.set_aspect("equal"); a.axhline(0, color="#dee2e6", lw=.6); a.axvline(0, color="#dee2e6", lw=.6); a.set_xticks([]); a.set_yticks([])
    return lam
fig, axs = plt.subplots(2, 3, figsize=(12.5, 8.4))
l1 = rung(0.3, axs[0], "MILD bend (strength 0.3)"); l2 = rung(2.0, axs[1], "STRONG bend (strength 2.0)")
fig.suptitle("One rung: pairs → differences → eigen-directions → cut", fontsize=12); fig.tight_layout(); fig.savefig("docs/img/math_fig2.png", dpi=170); plt.close(fig)
# ---------- Figure 3: eigenvalue spectra: ideal vs measured (strength 2, rung 2, trained encoder, seed 250)
fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
ideal = [2, 2, 2, 2, 0, 0, 0, 0]; real = [1.998, 1.977, 1.955, 1.938, .527, .465, .414, .397]
for ax, vals, t in ((axs[0], ideal, "ideal: exact pairs, linear bend\n$\\lambda$ = 2 (changed) or 0 (unchanged): gap infinite"), (axs[1], real, "measured: strength 2, rung 2 (inside $H_1$)\n$\\lambda_4/\\lambda_5$ = 1.94/0.53 → gap 3.7")):
    ax.bar(range(1, 9), vals, color=[c["a"]] * 4 + [c["b"]] * 4); ax.set_xticks(range(1, 9)); ax.set_xlabel("eigenvalue index $j$ (sorted)"); ax.set_ylabel("$\\lambda_j$"); ax.set_title(t, fontsize=10); ax.axvline(4.5, color="#868e96", ls="--"); ax.set_ylim(0, 2.4)
axs[0].text(2.5, 2.15, "variant block $V_k$ ($d_k=4$)", ha="center", fontsize=9, color=c["a"]); axs[0].text(6.5, 0.15, "invariant $H_k$", ha="center", fontsize=9, color=c["b"])
fig.tight_layout(); fig.savefig("docs/img/math_fig3.png", dpi=170); plt.close(fig)
print(l1, l2)
