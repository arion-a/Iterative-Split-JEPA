"""Builds docs/report/NESTED_LOSS.html (inline SVG, no external files) from results/nested_pod (E68, E71a).
    python experiments/make_nested_report.py
Every number in the page is computed here from the stored per-run JSON files."""
import glob, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import analyse_e68_e71 as A

ROOT = os.path.join(os.path.dirname(__file__), "..")
R = os.path.join(ROOT, "results/nested_pod/results/nested/")
OUT = os.path.join(ROOT, "docs/report/NESTED_LOSS.html")
KS = (11, 13, 16)
COL = {11: "#2563eb", 13: "#d97706", 16: "#dc2626", "U": "#94a3b8", "A": "#2563eb", "B": "#7c3aed"}

def rho_of(K): return 1 - np.geomspace(0.8, 0.04, K)
def ref_of(rho): return float(np.mean(1 - np.asarray(rho) ** 2))
RHO4 = np.array([0.2, 0.5, 0.75, 0.95])

# ---------------------------------------------------------------- data
e71 = {K: A.load(f"{R}e71/A/K{K}_s0.5") for K in KS}
e71u = {K: A.load(f"{R}e71/U/K{K}_s0.5") for K in KS}
e68 = {(arm, s): A.load(f"{R}e68/{arm}/s{s}") for arm in "AB" for s in (1, 2, 4, 8)}
for v in list(e71.values()) + list(e71u.values()) + list(e68.values()): assert len(v) == 5
def M(runs, f): return np.mean([f(r) for r in runs], axis=0)
pres71 = {K: M(e71[K], lambda r: r["slice"]["presence"]) for K in KS}
presU = {K: M(e71u[K], lambda r: r["slice"]["presence"]) for K in KS}
leak71 = {K: M(e71[K], lambda r: r["slice"]["leakage_faster"]) for K in KS}
res71 = {K: M(e71[K], lambda r: r["slice"]["invariance_residual"]) for K in KS}
clean71 = {K: [sum(A.rung_clean(r, k)[0] for r in e71[K]) for k in range(1, K)] for K in KS}
pred71 = {K: M(e71[K], lambda r: r["encoder_final"]["pred"]) for K in KS}
eig71 = {K: M(e71[K], lambda r: r["output_cov_min_eig"]) for K in KS}
glob71 = {K: M(e71[K], lambda r: r["global_r2"]) for K in KS}
globU = {K: M(e71u[K], lambda r: r["global_r2"]) for K in KS}
pres68 = {k: M(v, lambda r: r["slice"]["presence"]) for k, v in e68.items()}
res68 = {k: M(v, lambda r: r["slice"]["invariance_residual"]) for k, v in e68.items()}
leak68 = {k: M(v, lambda r: r["slice"]["leakage_faster"]) for k, v in e68.items()}
pred68 = {k: M(v, lambda r: r["encoder_final"]["pred"]) for k, v in e68.items()}
eig68 = {k: M(v, lambda r: r["output_cov_min_eig"]) for k, v in e68.items()}
REF4 = ref_of(RHO4)
first_clean = {K: next(k for k in range(1, K) if all(c == 5 for c in clean71[K][k - 1:])) for K in KS}
# predictive-loss excess over the reference vs mean slice presence, every A/B run
pts = []
for K in KS:
    for r in e71[K]: pts.append(("E71a", r["encoder_final"]["pred"] - ref_of(rho_of(K)), float(np.mean(r["slice"]["presence"]))))
for (arm, s), v in e68.items():
    for r in v: pts.append(("E68", r["encoder_final"]["pred"] - REF4, float(np.mean(r["slice"]["presence"]))))
rk = lambda v: np.argsort(np.argsort(v))
SPEAR = float(np.corrcoef(rk([p[1] for p in pts]), rk([p[2] for p in pts]))[0, 1])

# ---------------------------------------------------------------- svg helpers
def esc(s): return str(s).replace("&", "&amp;").replace("<", "&lt;")
class Ax:
    def __init__(self, w, h, xr, yr, ml=54, mr=16, mt=14, mb=44):
        self.w, self.h, self.xr, self.yr, self.ml, self.mr, self.mt, self.mb = w, h, xr, yr, ml, mr, mt, mb
        self.o = []
    def X(self, x): return self.ml + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * (self.w - self.ml - self.mr)
    def Y(self, y): return self.h - self.mb - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * (self.h - self.mb - self.mt)
    def add(self, s): self.o.append(s)
    def frame(self, xt, yt, xl, yl, grid=True):
        for y in yt:
            self.add(f'<line x1="{self.ml}" x2="{self.w - self.mr}" y1="{self.Y(y):.1f}" y2="{self.Y(y):.1f}" stroke="#e2e8f0"/>'
                     f'<text x="{self.ml - 6}" y="{self.Y(y) + 4:.1f}" text-anchor="end" font-size="11" fill="#475569">{y:g}</text>')
        for x, lab in xt:
            self.add(f'<line x1="{self.X(x):.1f}" x2="{self.X(x):.1f}" y1="{self.h - self.mb}" y2="{self.h - self.mb + 4}" stroke="#64748b"/>'
                     f'<text x="{self.X(x):.1f}" y="{self.h - self.mb + 16}" text-anchor="middle" font-size="11" fill="#475569">{esc(lab)}</text>')
        self.add(f'<line x1="{self.ml}" x2="{self.w - self.mr}" y1="{self.h - self.mb}" y2="{self.h - self.mb}" stroke="#64748b"/>'
                 f'<line x1="{self.ml}" x2="{self.ml}" y1="{self.mt}" y2="{self.h - self.mb}" stroke="#64748b"/>')
        self.add(f'<text x="{(self.ml + self.w - self.mr) / 2:.0f}" y="{self.h - 6}" text-anchor="middle" font-size="12" fill="#334155">{esc(xl)}</text>')
        self.add(f'<text transform="translate(13 {(self.mt + self.h - self.mb) / 2:.0f}) rotate(-90)" text-anchor="middle" font-size="12" fill="#334155">{esc(yl)}</text>')
    def line(self, xs, ys, col, dash="", w=2, dots=True, r=3.2):
        p = " ".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in zip(xs, ys))
        self.add(f'<polyline points="{p}" fill="none" stroke="{col}" stroke-width="{w}"' + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")
        if dots:
            for x, y in zip(xs, ys): self.add(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}" fill="{col}"/>')
    def hline(self, y, col, label="", dash="5 4"):
        self.add(f'<line x1="{self.ml}" x2="{self.w - self.mr}" y1="{self.Y(y):.1f}" y2="{self.Y(y):.1f}" stroke="{col}" stroke-dasharray="{dash}" stroke-width="1.5"/>')
        if label: self.add(f'<text x="{self.w - self.mr - 4}" y="{self.Y(y) - 5:.1f}" text-anchor="end" font-size="11" fill="{col}">{esc(label)}</text>')
    def vline(self, x, col, label="", dash="5 4"):
        self.add(f'<line x1="{self.X(x):.1f}" x2="{self.X(x):.1f}" y1="{self.mt}" y2="{self.h - self.mb}" stroke="{col}" stroke-dasharray="{dash}" stroke-width="1.5"/>')
        if label: self.add(f'<text x="{self.X(x) - 4:.1f}" y="{self.mt + 12}" text-anchor="end" font-size="11" fill="{col}">{esc(label)}</text>')
    def text(self, x, y, s, col="#334155", size=11, anchor="start", bold=False):
        self.add(f'<text x="{self.X(x):.1f}" y="{self.Y(y):.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}"' + (' font-weight="700"' if bold else "") + f'>{esc(s)}</text>')
    def svg(self): return f'<svg viewBox="0 0 {self.w} {self.h}" width="{self.w}" role="img">' + "".join(self.o) + "</svg>"
def legend(items, w=880):
    o, x = [], 8
    for lab, col, dash in items:
        o.append(f'<line x1="{x}" x2="{x + 24}" y1="10" y2="10" stroke="{col}" stroke-width="2.5"' + (f' stroke-dasharray="{dash}"' if dash else "") + f'/><circle cx="{x + 12}" cy="10" r="3.2" fill="{col}"/><text x="{x + 30}" y="14" font-size="12" fill="#334155">{esc(lab)}</text>')
        x += 36 + 7 * len(lab)
    return f'<svg viewBox="0 0 {w} 22" width="{w}">' + "".join(o) + "</svg>"
def heat_col(v):  # 0..1 -> red .. amber .. green
    v = max(0.0, min(1.0, v))
    a, b, c = (np.array(x) for x in ((254, 202, 202), (254, 240, 138), (134, 239, 172)))
    rgb = a + (b - a) * (v / 0.5) if v < 0.5 else b + (c - b) * ((v - 0.5) / 0.5)
    return "rgb({:.0f},{:.0f},{:.0f})".format(*rgb)

# ---------------------------------------------------------------- figures
def fig_concept():
    o = ['<svg viewBox="0 0 880 155" width="880"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0L8,4L0,8z" fill="#64748b"/></marker></defs>']
    cols = ["#fde68a", "#fed7aa", "#fecaca", "#d9f99d", "#bbf7d0", "#86efac"]
    labs = ["slice 1", "slice 2", "slice 3", "...", "slice K-1", "slice K (core)"]
    for i, (c, l) in enumerate(zip(cols, labs)):
        o.append(f'<rect x="{30 + i * 120}" y="30" width="116" height="44" rx="6" fill="{c}" stroke="#64748b"/><text x="{88 + i * 120}" y="57" text-anchor="middle" font-size="13">{l}</text>')
    o.append('<text x="30" y="20" font-size="12" fill="#b45309" font-weight="700">fastest layer (variant, to be dropped)</text>')
    o.append('<text x="750" y="20" text-anchor="end" font-size="12" fill="#15803d" font-weight="700">slowest layers (invariant, to be kept)</text>')
    o.append('<path d="M30 90H750" stroke="#64748b" stroke-width="2" marker-end="url(#ar)"/><text x="390" y="108" text-anchor="middle" font-size="12" fill="#475569">encoder output h = [slice 1 | slice 2 | ... | slice K], split by the loss, block sizes fixed in advance (4 numbers each)</text>')
    o.append('<text x="30" y="128" font-size="12.5" fill="#1e293b">Loss: (1) predict the next embedding;  (2) for a pair that shares every layer slower than k, the slices slower than k must agree;</text>')
    o.append('<text x="30" y="145" font-size="12.5" fill="#1e293b">(3) the slice-k difference across such a pair must stay spread out (whitening).</text>')
    return "".join(o) + "</svg>"

def fig_clean_heat():
    cw, ch, left, top = 44, 30, 120, 34
    n = 16
    o = [f'<svg viewBox="0 0 880 {top + 3 * ch + 44}" width="880">']
    o.append(f'<text x="{left}" y="14" font-size="12" fill="#334155" font-weight="700">rung (slice) number: 1 = fastest layer</text>')
    for j in range(1, n + 1): o.append(f'<text x="{left + (j - 1) * cw + cw / 2}" y="{top - 6}" text-anchor="middle" font-size="11" fill="#475569">{j}</text>')
    for i, K in enumerate(KS):
        y = top + i * ch
        o.append(f'<text x="{left - 8}" y="{y + 20}" text-anchor="end" font-size="12.5" fill="#1e293b" font-weight="700">K = {K} ({K - 1} rungs)</text>')
        for j in range(1, K):
            c = clean71[K][j - 1]
            o.append(f'<rect x="{left + (j - 1) * cw}" y="{y}" width="{cw - 2}" height="{ch - 2}" fill="{heat_col(c / 5)}" stroke="#fff"/><text x="{left + (j - 1) * cw + cw / 2 - 1}" y="{y + 19}" text-anchor="middle" font-size="12" fill="#1e293b">{c}</text>')
        o.append(f'<rect x="{left + (K - 1) * cw}" y="{y}" width="{cw - 2}" height="{ch - 2}" fill="#e2e8f0" stroke="#fff"/><text x="{left + (K - 1) * cw + cw / 2 - 1}" y="{y + 19}" text-anchor="middle" font-size="11" fill="#475569">core</text>')
    yb = top + 3 * ch + 14
    for c in range(6):
        o.append(f'<rect x="{left + c * 40}" y="{yb}" width="38" height="16" fill="{heat_col(c / 5)}" stroke="#fff"/><text x="{left + c * 40 + 19}" y="{yb + 12}" text-anchor="middle" font-size="11">{c}</text>')
    o.append(f'<text x="{left + 250}" y="{yb + 12}" font-size="12" fill="#334155">= number of the 5 seeds in which the rung is clean</text>')
    return "".join(o) + "</svg>"

def fig_presence_by_speed():
    a = Ax(880, 330, (0.1, 1.0), (0, 1.05))
    a.frame([(x, f"{x:g}") for x in (0.2, 0.4, 0.6, 0.8, 1.0)], [0, 0.25, 0.5, 0.75, 1.0], "layer speed rho (0 = fresh noise each step, 1 = never changes)", "presence (R-squared, layer from own slice)")
    a.hline(0.9, "#16a34a", "clean line 0.9")
    a.vline(0.86, "#475569", "all seeds clean from rho about 0.86")
    for K in KS: a.line(rho_of(K), pres71[K], COL[K])
    a.line(rho_of(16), presU[16], COL["U"], dash="6 4")
    return a.svg()

def fig_residual_leak():
    out = []
    a = Ax(430, 270, (1, 15), (0, 0.24), ml=58)
    a.frame([(x, str(x)) for x in (1, 3, 5, 7, 9, 11, 13, 15)], [0, 0.05, 0.1, 0.15, 0.2], "rung", "invariance residual")
    a.hline(0.05, "#16a34a", "limit 0.05")
    for K in KS: a.line(range(1, K), res71[K], COL[K], r=2.6)
    a.text(15, 0.225, "unmatched pairs would give 2", "#64748b", 11, "end")
    out.append(a.svg())
    b = Ax(430, 270, (2, 16), (0, 0.16), ml=58)
    b.frame([(x, str(x)) for x in (2, 4, 6, 8, 10, 12, 14, 16)], [0, 0.04, 0.08, 0.12, 0.16], "slice number", "leakage (max R-squared)")
    b.hline(0.1, "#16a34a", "limit 0.1")
    for K in KS: b.line(range(2, K + 1), np.clip(leak71[K], 0, None), COL[K], r=2.6)
    out.append(b.svg())
    return '<div class="two">' + "".join(out) + "</div>"

def fig_e68_heat():
    cw, ch, left, top = 110, 26, 225, 44
    rows = [(arm, s) for arm in "AB" for s in (1, 2, 4, 8)]
    o = [f'<svg viewBox="0 0 880 {top + len(rows) * ch + 30}" width="880">']
    for j, rho in enumerate(RHO4):
        o.append(f'<text x="{left + j * cw + cw / 2}" y="16" text-anchor="middle" font-size="12" fill="#334155" font-weight="700">slice {j + 1}</text><text x="{left + j * cw + cw / 2}" y="32" text-anchor="middle" font-size="11" fill="#64748b">rho = {rho:g}</text>')
    for i, (arm, s) in enumerate(rows):
        y = top + i * ch
        lab = ("arm A (joint)" if arm == "A" else "arm B (curriculum)") + f", strength {s}"
        o.append(f'<text x="{left - 8}" y="{y + 18}" text-anchor="end" font-size="12" fill="#1e293b">{lab}</text>')
        for j in range(4):
            v = pres68[(arm, s)][j]
            o.append(f'<rect x="{left + j * cw}" y="{y}" width="{cw - 2}" height="{ch - 2}" fill="{heat_col((v - 0.2) / 0.75)}" stroke="#fff"/><text x="{left + j * cw + cw / 2 - 1}" y="{y + 17}" text-anchor="middle" font-size="12.5">{v:.2f}</text>')
    o.append(f'<text x="{left}" y="{top + len(rows) * ch + 20}" font-size="12" fill="#334155">mean presence over 5 seeds; the clean line is 0.9. Only slice 4 at strength 1 is above it (0.95, both arms); slice 3 of arm A at strength 1 is 0.895, just below.</text>')
    return "".join(o) + "</svg>"

def fig_e68_lines():
    out = []
    a = Ax(430, 260, (0, 3.3), (0, 0.85), ml=58)
    xs = [np.log2(s) for s in (1, 2, 4, 8)]
    a.frame([(np.log2(s), str(s)) for s in (1, 2, 4, 8)], [0, 0.2, 0.4, 0.6, 0.8], "coupling strength", "invariance residual (mean of 3 rungs)")
    a.hline(0.05, "#16a34a", "limit 0.05")
    for arm in "AB": a.line(xs, [float(np.mean(res68[(arm, s)])) for s in (1, 2, 4, 8)], COL[arm])
    out.append(a.svg())
    b = Ax(430, 260, (0, 3.3), (0.5, 0.85), ml=58)
    b.frame([(np.log2(s), str(s)) for s in (1, 2, 4, 8)], [0.5, 0.6, 0.7, 0.8], "coupling strength", "final prediction loss")
    b.hline(REF4, "#16a34a", f"reference {REF4:.3f}")
    for arm in "AB": b.line(xs, [float(pred68[(arm, s)]) for s in (1, 2, 4, 8)], COL[arm])
    out.append(b.svg())
    return '<div class="two">' + "".join(out) + "</div>"

def fig_pred_scatter():
    a = Ax(880, 320, (0, 0.27), (0.2, 1.0))
    a.frame([(x, f"{x:g}") for x in (0, 0.05, 0.1, 0.15, 0.2, 0.25)], [0.2, 0.4, 0.6, 0.8, 1.0], "predictive loss above the reference (0 = as low as a faithful embedding allows)", "mean presence over all slices")
    for src, col in (("E68", "#7c3aed"), ("E71a", "#2563eb")):
        for s, x, y in pts:
            if s == src: a.add(f'<circle cx="{a.X(x):.1f}" cy="{a.Y(y):.1f}" r="4" fill="{col}" fill-opacity="0.65"/>')
    a.add(f'<text x="{a.X(0.265):.1f}" y="{a.Y(0.97):.1f}" text-anchor="end" font-size="12" fill="#7c3aed">E68 (hard world, 40 runs)</text>')
    a.add(f'<text x="{a.X(0.265):.1f}" y="{a.Y(0.92):.1f}" text-anchor="end" font-size="12" fill="#2563eb">E71a (depth, 15 runs)</text>')
    a.add(f'<text x="{a.X(0.265):.1f}" y="{a.Y(0.87):.1f}" text-anchor="end" font-size="12" fill="#334155">rank correlation {SPEAR:.2f} (55 runs)</text>')
    return a.svg()

# ---------------------------------------------------------------- page
def table(head, rows, cls=""):
    h = "".join(f"<th>{esc(x)}</th>" for x in head)
    def cell(c):
        x, k = c if isinstance(c, tuple) else (c, "")
        return f'<td class="{k}">{x}</td>'
    b = "".join("<tr>" + "".join(cell(c) for c in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><tr>{h}</tr>{b}</table>'

def verdict_rows():
    e68a1 = sum(A.slice_clean(r) for r in e68[("A", 1)])
    bb4 = max(sum(A.slice_clean(r) for r in e68[(arm, 4)]) for arm in "AB")
    diff = sum(A.slice_clean(r) for s in (2, 4, 8) for r in e68[("B", s)]) - sum(A.slice_clean(r) for s in (2, 4, 8) for r in e68[("A", s)])
    allc = {K: sum(A.all_rungs_clean(r) for r in e71[K]) for K in KS}
    frac16 = float(np.mean([np.mean([A.rung_clean(r, k)[0] for k in range(1, 16)]) for r in e71[16]]))
    no = "no"
    return [
        ("E68 (a)", "arm A slice-clean at strength 1", f"{e68a1} of 5", "at least 4", f"short by {4 - e68a1} seeds"),
        ("E68 (b)", "better arm slice-clean at strength 4", f"{bb4} of 5", "at least 3", f"short by {3 - bb4} seeds"),
        ("E68 (c)", "B minus A clean seeds, strengths 2, 4, 8", f"{diff}", "at least 2", f"short by {2 - diff}"),
        ("E71a (a)", "all-rungs-clean at K = 11, 13, 16", ", ".join(f"{allc[K]} of 5" for K in KS), "at least 3 of 5 at each K", "short by 3 seeds at each K"),
        ("E71a (b)", "clean-rung fraction at K = 16", f"{frac16:.3f}", "at least 0.9", f"short by {0.9 - frac16:.3f}"),
    ], e68a1, bb4, diff, allc, frac16

def build():
    vr, e68a1, bb4, diff, allc, frac16 = verdict_rows()
    assert (e68a1, bb4, diff) == (0, 0, 0) and all(v == 0 for v in allc.values())
    vt = table(["Line", "What was required", "Observed", "Required", "Gap"],
               [[(a, ""), (b, ""), (c, "no"), (d, ""), (e, "no")] for a, b, c, d, e in vr])
    rho = {K: rho_of(K) for K in KS}
    thr = "; ".join(f"K = {K}: rung {first_clean[K]} (rho = {rho[K][first_clean[K] - 1]:.3f})" for K in KS)
    before = "; ".join(f"K = {K}: rho = {rho[K][first_clean[K] - 2]:.3f} ({clean71[K][first_clean[K] - 2]} of 5 seeds)" for K in KS)
    rows71 = []
    for K in KS:
        rows71.append([(f"{K} ({K - 1})", ""), (f"{pres71[K][:first_clean[K] - 1].min():.2f} to {pres71[K][:first_clean[K] - 1].max():.2f}", "no"),
                       (f"{pres71[K][first_clean[K] - 1:].min():.2f} to {pres71[K][first_clean[K] - 1:].max():.2f}", "ok"),
                       (f"{presU[K].mean():.2f}", ""),
                       (f"{res71[K].min():.3f} to {res71[K].max():.3f}", ""), (f"{np.clip(leak71[K], 0, None).max():.3f}", ""),
                       (f"{eig71[K]:.2f}", ""), (f"{pred71[K]:.3f} vs {ref_of(rho[K]):.3f}", "")])
    t71 = table(["K (rungs)", "Presence, slices before the cut", "Presence, from the cut on", "Presence, untrained", "Residual range", "Worst leakage (mean)", "Health (min eigenvalue)", "Prediction loss vs reference"], rows71)
    s1 = pres71[16]
    rA1 = (min(res68[('A', 1)]), max(res68[('A', 1)])); rA8 = (min(res68[('A', 8)]), max(res68[('A', 8)]))
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Nested loss: what happened</title>
<style>
body{{font:15px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#1e293b;max-width:920px;margin:24px auto;padding:0 18px}}
h1{{font-size:27px;margin:0 0 4px}}h2{{font-size:20px;margin:30px 0 8px;border-bottom:2px solid #e2e8f0;padding-bottom:4px}}
.sub{{color:#475569;margin-bottom:12px}}table{{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0}}td,th{{border:1px solid #cbd5e1;padding:5px 8px;vertical-align:top;text-align:left}}th{{background:#f1f5f9}}
td.ok{{background:#ecfdf5}}td.no{{background:#fef2f2}}svg{{max-width:100%;height:auto}}.note{{color:#475569;font-size:13px}}
.box{{background:#f8fafc;border-left:4px solid #6366f1;padding:8px 14px;margin:10px 0}}.two{{display:flex;gap:10px;flex-wrap:wrap}}.two svg{{flex:1 1 400px}}
section{{break-inside:avoid}}ul{{margin:6px 0 6px 18px;padding:0}}
</style></head><body>
<h1>Nested loss: what happened</h1>
<div class="sub">E68 (hard world, 40 runs) and E71a (10, 12 and 15 rungs, 30 runs). All numbers come from the stored result files (<code>results/nested_pod</code>); 5 seeds per cell.</div>

<h2>Bottom line</h2>
<div class="box"><ul>
<li><b>Both registered tests failed.</b> The nested loss did not give a clean block at every rung in either test (gaps below).</li>
<li><b>But the loss does split, and it splits by speed.</b> In the mild world (E71a), the slow layers are recovered cleanly on all 5 seeds at all three depths, and the fast layers are not. The cut falls at about the same layer speed, rho about 0.86, whatever the depth.</li>
<li><b>The fast slices are not holding their layer and are not leaking into the slow ones</b> (leakage at most {max(np.clip(leak71[11],0,None).max(), np.clip(leak71[13],0,None).max()):.2f} at 10 and 12 rungs). Their content has not been inspected.</li>
<li><b>In the hard world (E68) it does not work, even for the slow slices.</b> Every slice gets worse as the coupling strength grows; the invariance itself is not achieved (residual {rA1[0]:.2f} to {rA1[1]:.2f} at strength 1, {rA8[0]:.2f} to {rA8[1]:.2f} at strength 8, limit 0.05).</li>
<li><b>The predictive loss tracks this:</b> the further it sits above what a faithful embedding allows, the worse the presence (rank correlation {SPEAR:.2f} over 55 runs).</li>
<li><b>Not measured:</b> whether the recovered blocks' <i>speeds</i> can be read back (nothing in these results does that).</li>
</ul></div>

<h2>1. What was tested</h2>
{fig_concept()}
<p class="note">E71a: K = 11, 13, 16 layers (10, 12, 15 rungs), speeds rho = 1 - geomspace(0.8, 0.04, K), mild coupling (0.5). E68: 4 layers with speeds 0.2, 0.5, 0.75, 0.95, coupling strength 1, 2, 4, 8; arm A has every invariance term on from step 0, arm B switches them on one rung at a time. Pairs are exact (oracle). A <b>rung is clean</b> if presence is at least 0.9 (the layer is readable from its own slice), leakage at most 0.1 (no faster layer readable from it) and invariance residual at most 0.05 (the slower slices agree across the pair; two unmatched pairs would give about 2).</p>

<h2>2. Registered verdicts and the gaps</h2>
{vt}
<p class="note">Both verdicts: <b>refuted</b>. E71b was not run (it needs E68 line (b)). The registered tests required every rung to be clean, including the fastest; the sections below show where the failure sits.</p>

<h2>3. E71a, rung by rung: what is recovered and what is lost</h2>
<p>Number of seeds (of 5) in which each rung is clean:</p>
{fig_clean_heat()}
<p>The same data against layer speed. Each line is a depth; the grey dashed line is the untrained encoder at K = 16. The three depths fall on one curve: presence is high only for layers slower than about 0.86.</p>
{legend([("K = 11", COL[11], ""), ("K = 13", COL[13], ""), ("K = 16", COL[16], ""), ("untrained encoder, K = 16", COL["U"], "6 4")])}
{fig_presence_by_speed()}
<p>First rung that is clean on all 5 seeds and stays clean: {thr}. The rung just before it is clean on only some seeds ({before}).</p>
<p><b>Is the loss doing the splitting?</b> Yes, in this world. The untrained encoder reads about {np.mean([presU[K].mean() for K in KS]):.2f} on every slice; the trained one reads {s1[first_clean[16] - 1:].min():.2f} to {s1[first_clean[16] - 1:].max():.2f} on the slices from the cut on at K = 16 (slices {first_clean[16]} to 16). <b>How far:</b> 4, 5 and 6 of the 10, 12 and 15 rungs are clean; the rest fail on presence.</p>
{t71}

<h2>4. Is the invariance achieved, and is anything leaking?</h2>
{legend([("K = 11", COL[11], ""), ("K = 13", COL[13], ""), ("K = 16", COL[16], "")])}
{fig_residual_leak()}
<p>At 10 and 12 rungs the slower slices agree across pairs almost everywhere (residual below about 0.09; most rungs below 0.05) and leakage stays at or below 0.04. At 15 rungs the first four rungs lose both: residual up to {res71[16][:4].max():.2f} against the 0.05 limit, and rungs 2 to 5 reach {np.clip(leak71[16][:4], 0, None).max():.2f} mean leakage (worst seeds above the 0.1 limit). So the fast end gets worse with depth.</p>

<h2>5. E68, the hard world: it does not work, even for the slow slices</h2>
<p>Mean presence by slice (red = low):</p>
{fig_e68_heat()}
<p>Left: the invariance residual (limit 0.05) and right the final prediction loss against the reference, by coupling strength. Blue = arm A, purple = arm B.</p>
{legend([("arm A (joint)", COL["A"], ""), ("arm B (curriculum)", COL["B"], "")])}
{fig_e68_lines()}
<p>Presence falls with strength for every slice, the slowest one included ({', '.join(f'{pres68[("A", s)][3]:.2f}' for s in (1, 2, 4, 8))} for arm A at strengths 1, 2, 4, 8). The residual (mean of the 3 rungs) rises from {np.mean(res68[('A', 1)]):.2f} to {np.mean(res68[('A', 8)]):.2f} for arm A. The curriculum (arm B) is not better: it is worse on slice 2 at every strength. Health stays at {min(eig68.values()):.2f} or above, so this is not a collapse; the loss simply does not find the nested structure as the coupling gets harder.</p>

<h2>6. How the predictive loss performs</h2>
<p>For a faithful embedding (every layer kept, outputs whitened) the best prediction loss is the mean of 1 - rho squared over the layers: <b>{REF4:.3f}</b> for the 4-layer world, {ref_of(rho[11]):.3f} / {ref_of(rho[13]):.3f} / {ref_of(rho[16]):.3f} for K = 11 / 13 / 16. The trained runs sit above it, by an amount that grows with hardness and depth:</p>
{table(["", "Strength 1", "Strength 2", "Strength 4", "Strength 8"], [[("E68 arm A", "")] + [(f"{pred68[('A', s)]:.3f} (+{pred68[('A', s)] - REF4:.3f})", "") for s in (1, 2, 4, 8)]])}
{table(["", "K = 11", "K = 13", "K = 16"], [[("E71a arm A", "")] + [(f"{pred71[K]:.3f} (+{pred71[K] - ref_of(rho[K]):.3f})", "") for K in KS]])}
{fig_pred_scatter()}
<p class="note">Each point is one trained run. The reference is a floor for an embedding that keeps every layer, so a larger excess means the run is further from a faithful embedding. This is a correlation across runs, not a proven cause.</p>

<h2>7. What this says about the idea (my reading, flagged)</h2>
<ul>
<li><b>Supported (mild world, 10 to 15 rungs):</b> minimizing the loss leaves the slow, consistent layers in the later slices, recovered cleanly on every seed, and the cut stays at the same speed as depth grows.</li>
<li><b>Not supported:</b> a clean block at every rung (the registered test), and any recovery in the hard world.</li>
<li><b>Not measured:</b> (i) whether a recovered block's rate (0.2, 0.6, ...) can be read back; (ii) what the discarded fast slices contain; (iii) whether the slow-rung result holds at a stronger coupling in the deep world (E71b was not run).</li>
</ul>
<p class="note"><b>Limits:</b> oracle nested pairs; block sizes given; one world family; 5 seeds; W = 1 in every world (the smaller candidate was healthy); steps 7,500 K (K = 11 to 16) and 30,000 (E68); the trained encoders were not saved, so these are summary measures only. The "reference" for the prediction loss assumes the outputs are whitened and every layer is kept.</p>
</body></html>"""
    return html

if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(build())
    print("wrote", OUT, f"spearman {SPEAR:.3f}", {K: first_clean[K] for K in KS})
