"""docs/report/E72.html: report with figures for E72 (slow-rung criterion and rate recovery), from results/nested_pod_e72.
    python experiments/make_e72_report.py"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import make_nested_report as M
import analyse_e72 as E
import analyse_e68_e71 as A
from make_nested_report import Ax, esc, table, COL, rho_of
from report_equations import CSS as EQ_CSS, E as EQ

R = os.path.join(M.ROOT, "results/nested_pod_e72/results/nested/e72/")
OUT = os.path.join(M.ROOT, "docs/report/E72.html")
KS = E.KS
runs = {K: A.load(f"{R}A/K{K}_s0.5") for K in KS}
unt = {K: A.load(f"{R}U/K{K}_s0.5") for K in KS}
assert all(len(v) == 5 for v in list(runs.values()) + list(unt.values()))
slow = {K: E.slow_set(K) for K in KS}
rho = {K: E.rhos(K) for K in KS}
pts = [(K, r["seed"], b, rho[K][b - 1], r["slice"]["rho_hat"][b - 1]) for K in KS for r in runs[K] for b in slow[K]]
upts = [(K, r["seed"], b, rho[K][b - 1], r["slice"]["rho_hat"][b - 1]) for K in KS for r in unt[K] for b in slow[K]]
signed = np.array([p[4] - p[3] for p in pts])

def fig_scatter():
    a = Ax(880, 360, (0.84, 0.975), (0.6, 1.0))
    a.frame([(x, f"{x:g}") for x in (0.85, 0.88, 0.91, 0.94, 0.97)], [0.6, 0.7, 0.8, 0.9, 1.0], "true speed rho of the layer", "estimated speed from the slice")
    a.line([0.84, 0.975], [0.84, 0.975], "#16a34a", dash="5 4", dots=False, w=1.6)
    a.add(f'<text x="{a.X(0.94):.1f}" y="{a.Y(0.985) - 4:.1f}" font-size="11" fill="#16a34a" transform="rotate(-10 {a.X(0.94):.1f} {a.Y(0.985):.1f})">estimate = true</text>')
    for K, s, b, t, e in upts: a.add(f'<circle cx="{a.X(t):.1f}" cy="{a.Y(e):.1f}" r="3" fill="#94a3b8" fill-opacity="0.6"/>')
    for K, s, b, t, e in pts: a.add(f'<circle cx="{a.X(t):.1f}" cy="{a.Y(e):.1f}" r="3.6" fill="{COL[K]}" fill-opacity="0.75"/>')
    a.add(f'<text x="{a.X(0.845):.1f}" y="{a.Y(0.745):.1f}" font-size="12" fill="#64748b">untrained encoder: 0.61 to 0.70 whatever the layer</text>')
    return a.svg()

def fig_error():
    a = Ax(880, 340, (0.84, 0.975), (-0.045, 0.02))
    a.frame([(x, f"{x:g}") for x in (0.85, 0.88, 0.91, 0.94, 0.97)], [-0.04, -0.02, 0, 0.02], "true speed rho of the layer", "estimate minus true speed")
    a.add(f'<rect x="{a.ml}" y="{a.Y(0.02):.1f}" width="{a.w - a.ml - a.mr}" height="{a.Y(-0.02) - a.Y(0.02):.1f}" fill="#dcfce7" fill-opacity="0.55"/>')
    a.hline(0, "#475569", "", dash="")
    a.hline(-0.02, "#16a34a", "limit: error 0.02", dash="5 4")
    for K, s, b, t, e in pts: a.add(f'<circle cx="{a.X(t):.1f}" cy="{a.Y(e - t):.1f}" r="3.6" fill="{COL[K]}" fill-opacity="0.75"/>')
    mean_by = {}
    for K, s, b, t, e in pts: mean_by.setdefault(round(t, 3), []).append(e - t)
    xs = sorted(mean_by); a.line(xs, [np.mean(mean_by[x]) for x in xs], "#0f172a", dash="2 3", dots=False, w=1.8)
    a.add(f'<text x="{a.X(0.845):.1f}" y="{a.Y(-0.042):.1f}" font-size="11" fill="#0f172a">dotted line: mean error at each speed</text>')
    return a.svg()

def fig_presence():
    a = Ax(880, 330, (0.15, 0.975), (-0.05, 1.04))
    a.frame([(x, f"{x:g}") for x in (0.2, 0.4, 0.6, 0.8, 0.86, 0.95)], [0, 0.25, 0.5, 0.75, 0.9, 1.0], "layer speed rho", "presence of the layer in its own slice")
    a.hline(0.9, "#16a34a", "clean line 0.9"); a.vline(0.86, "#475569", "0.86 cut")
    for K in KS:
        for r in runs[K]:
            idx = list(range(K))
            a.line([rho[K][b] for b in idx], [r["slice"]["presence"][b] for b in idx], COL[K], w=1.1, dots=False)
    return a.svg()

def fig_grid():
    cw, ch, left, top = 118, 21, 150, 40
    rows = [(K, r) for K in KS for r in runs[K]]
    o = [f'<svg viewBox="0 0 880 {top + len(rows) * ch + 56}" width="880">']
    heads = ["Criterion S", "min presence (slow)", "Rate R", "largest error", "Order"]
    for j, h in enumerate(heads): o.append(f'<text x="{left + j * cw + cw / 2}" y="26" text-anchor="middle" font-size="12" fill="#334155" font-weight="700">{h}</text>')
    for i, (K, r) in enumerate(rows):
        y = top + i * ch + (6 if i >= 5 else 0) + (6 if i >= 10 else 0)
        if i % 5 == 0: o.append(f'<text x="{left - 78}" y="{y + 15}" text-anchor="end" font-size="12" fill="{COL[K]}" font-weight="700">K = {K}</text>')
        o.append(f'<text x="{left - 50}" y="{y + 15}" text-anchor="end" font-size="11" fill="#64748b"></text>')
        pm = min(r["slice"]["presence"][b - 1] for b in slow[K]); em = max(E.errs(r, K)); S, Rr, O = E.passes_S(r, K), E.passes_R(r, K), E.passes_order(r, K)
        cells = [("pass" if S else "fail", S), (f"{pm:.3f}", pm >= 0.9), ("pass" if Rr else "fail", Rr), (f"{em:.3f}", em <= 0.02), ("pass" if O else "fail", O)]
        o.append(f'<text x="{left + 34}" y="{y + 15}" text-anchor="end" font-size="11" fill="#64748b">seed {r["seed"]}</text>')
        for j, (t, ok) in enumerate(cells):
            o.append(f'<rect x="{left + j * cw + 40}" y="{y}" width="{cw - 42}" height="{ch - 2}" fill="{"#bbf7d0" if ok else "#fecaca"}" stroke="#fff"/><text x="{left + j * cw + 40 + (cw - 42) / 2}" y="{y + 14}" text-anchor="middle" font-size="12">{t}</text>')
    yb = top + len(rows) * ch + 26
    o.append(f'<text x="{left - 100}" y="{yb}" font-size="12" fill="#334155">S: every slow rung clean and the core presence at least 0.9.   R: every slow slice within 0.02 of its true speed.</text>')
    o.append(f'<text x="{left - 100}" y="{yb + 16}" font-size="12" fill="#334155">Order: the estimated speeds rise with the layer number.</text>')
    return "".join(o) + "</svg>"

def build():
    n = {K: (sum(E.passes_S(r, K) for r in runs[K]), sum(E.passes_R(r, K) for r in runs[K]), sum(E.passes_order(r, K) for r in runs[K])) for K in KS}
    vt = table(["Line", "Registered requirement", "Observed (K = 11 / 13 / 16)", "Result", "Gap"], [
        [("(a) slow-rung criterion S", ""), ("at least 4 of 5 seeds at each K", ""), (" / ".join(f"{n[K][0]}" for K in KS), ""), ("refuted at K = 16", "no"), ("K = 16: 3 of 5, short by 1 seed", "no")],
        [("(b) rate recovery R", ""), ("at least 3 of 5 seeds at each K", ""), (" / ".join(f"{n[K][1]}" for K in KS), ""), ("met", "ok"), ("none (K = 13 is exactly at the bound)", "ok")],
        [("(c) order of the speeds", ""), ("at least 3 of 5 seeds at each K", ""), (" / ".join(f"{n[K][2]}" for K in KS), ""), ("met", "ok"), ("none", "ok")]])
    per = []
    for K in KS:
        for b in slow[K]:
            e = [r["slice"]["rho_hat"][b - 1] for r in runs[K]]; t = rho[K][b - 1]
            per.append([(str(K), ""), (f"{b}" + (" (core)" if b == K else ""), ""), (f"{t:.3f}", ""), (f"{np.mean(e):.3f}", ""), (f"{np.mean(e) - t:+.3f}", ""), (f"{np.max(np.abs(np.array(e) - t)):.3f}", "no" if np.max(np.abs(np.array(e) - t)) > 0.02 else "ok")])
    pt = table(["K", "Layer", "True speed", "Mean estimate (5 seeds)", "Mean error", "Largest error"], per)
    fails = "".join(f"<li>{esc(x.lstrip('- '))}</li>" for x in open(os.path.join(M.ROOT, "results/nested_pod_e72/REPORT_E72.md")).read().split("Deviations of failing seeds:")[1].split("## Per slow slice")[0].strip().splitlines())
    eq = EQ("ρ̂<sub>b</sub> = mean over the 4 coordinates j of slice b of&nbsp; Σ ( h<sub>t,j</sub> − h̄<sub>t,j</sub> )( h<sub>t+1,j</sub> − h̄<sub>t+1,j</sub> ) / √[ Σ ( h<sub>t,j</sub> − h̄<sub>t,j</sub> )<sup>2</sup> · Σ ( h<sub>t+1,j</sub> − h̄<sub>t+1,j</sub> )<sup>2</sup> ]")
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>E72 results</title>
<style>
body{{font:15px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#1e293b;max-width:920px;margin:24px auto;padding:0 18px}}
h1{{font-size:27px;margin:0 0 4px}}h2{{font-size:20px;margin:28px 0 8px;border-bottom:2px solid #e2e8f0;padding-bottom:4px}}
.sub{{color:#475569;margin-bottom:12px}}table{{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0}}td,th{{border:1px solid #cbd5e1;padding:4px 8px;text-align:left}}th{{background:#f1f5f9}}
td.ok{{background:#ecfdf5}}td.no{{background:#fef2f2}}svg{{max-width:100%;height:auto}}.note{{color:#475569;font-size:13px}}
.box{{background:#f8fafc;border-left:4px solid #6366f1;padding:8px 14px;margin:10px 0}}ul{{margin:6px 0 6px 18px;padding:0}}
{EQ_CSS}</style></head><body>
<h1>E72: slow layers and their speeds</h1>
<div class="sub">30 new runs (seeds 290 to 294) at K = 11, 13, 16 layers, coupling strength 0.5, nested loss (arm A) and an untrained control; all numbers from <code>results/nested_pod_e72</code>. Test registered before the run in <code>docs/EVIDENCE.md</code>.</div>
<div class="box"><ul>
<li><b>The slow layers are recovered again on new seeds,</b> in 12 of 15 trained runs. The registered line needed 4 of 5 at every depth; K = 16 got 3 of 5, <b>short by one seed</b>, and the misses are by 0.003 to 0.011 of presence.</li>
<li><b>The speed of each recovered slice can be read back from the data alone,</b> to within 0.006 to 0.021 on average (largest single error 0.030), and in the right order on all 15 runs. The untrained encoder reads about 0.66 on every slice: no speed information.</li>
<li><b>The estimate is biased low:</b> all 90 slow-slice estimates are below the true speed (mean error {signed.mean():+.4f}), more so at the fast end of the slow set.</li>
<li><b>Limits:</b> the slice layout was given, the 0.86 cut came from the earlier E71a runs, one world family, mild coupling.</li></ul></div>

<h2>1. Registered lines and the gaps</h2>
{vt}

<h2>2. Estimated speed against true speed</h2>
<p>Each dot is one slow slice of one trained run (blue K = 11, orange K = 13, red K = 16; 90 dots). Grey dots: the untrained encoder. The green dashed line is a perfect estimate.</p>
{fig_scatter()}
<p>How the speed is estimated, from held-out transition pairs (h<sub>t</sub>, h<sub>t+1</sub>), no labels:</p>
{eq}

<h2>3. The error, speed by speed</h2>
<p>Estimate minus true speed. The green band is the registered limit of 0.02. Every dot is below zero; the error is largest for the layers at the edge of the slow set.</p>
{fig_error()}
{pt}

<h2>4. Is the cut the same on new seeds?</h2>
<p>Presence of each layer in its own slice against the layer's speed, one thin line per run (blue K = 11, orange K = 13, red K = 16). The lines rise through the 0.9 line near speed 0.82 to 0.86, as in E71a.</p>
{fig_presence()}

<h2>5. Seed by seed</h2>
{fig_grid()}
<p>Failing seeds, with the deviation:</p><ul>{fails}</ul>
<p class="note"><b>Limits as registered:</b> the slices are read at fixed positions (the layout is given), so this shows a recovered slice's speed can be read back, not that the layer structure was found from data alone; oracle nested pairs; block sizes given; the 0.86 cut was taken from E71a; one world family and mild coupling; 5 seeds per cell; lag-1 correlation equals the speed only for a linear readout of an AR(1) layer.</p>
</body></html>"""
    return html

if __name__ == "__main__":
    open(OUT, "w").write(build()); print("wrote", OUT, f"mean signed error {signed.mean():+.4f}")
