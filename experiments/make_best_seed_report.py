"""Detail page for the best single E71a run: docs/report/BEST_SEED.html (inline SVG).
Best = largest share of clean rungs (E71 rung rule) among the 15 E71a arm-A runs; ties broken by mean slice presence.
    python experiments/make_best_seed_report.py"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import make_nested_report as M
import analyse_e68_e71 as A
from make_nested_report import Ax, esc, table, heat_col, rho_of, ref_of
from report_equations import equations_html, CSS as EQ_CSS

OUT = os.path.join(M.ROOT, "docs/report/BEST_SEED.html")

cands = []
for K in M.KS:
    for r in M.e71[K]:
        nc = sum(A.rung_clean(r, k)[0] for k in range(1, K))
        cands.append((nc / (K - 1), float(np.mean(r["slice"]["presence"])), K, r["seed"], nc))
cands.sort(reverse=True)
_, meanpres, K, seed, ncl = cands[0]
run = next(r for r in M.e71[K] if r["seed"] == seed)
unt = next(r for r in M.e71u[K] if r["seed"] == seed)
rho = rho_of(K)
S = run["slice"]; Su = unt["slice"]
pres, leak, res = S["presence"], S["leakage_faster"], S["invariance_residual"]
lin, mlp = run["presence"]["linear"], run["presence"]["mlp"]

def bars():
    w, h, ml, mt, mb = 880, 300, 56, 24, 56
    a = Ax(w, h, (0, K), (0, 1.05), ml=ml, mt=mt, mb=mb)
    a.frame([], [0, 0.25, 0.5, 0.75, 1.0], "", "presence (R-squared)")
    bw = (w - ml - 16) / K
    for i in range(K):
        x0 = a.X(i)
        ok = (i == K - 1 and pres[i] >= 0.9) or (i < K - 1 and A.rung_clean(run, i + 1)[0])
        a.add(f'<rect x="{x0 + 4:.1f}" y="{a.Y(pres[i]):.1f}" width="{bw * 0.44:.1f}" height="{a.Y(0) - a.Y(pres[i]):.1f}" fill="{"#22c55e" if ok else "#f87171"}"/>')
        a.add(f'<rect x="{x0 + 4 + bw * 0.46:.1f}" y="{a.Y(Su["presence"][i]):.1f}" width="{bw * 0.3:.1f}" height="{a.Y(0) - a.Y(Su["presence"][i]):.1f}" fill="#cbd5e1"/>')
        a.add(f'<text x="{x0 + 4 + bw * 0.22:.1f}" y="{a.Y(pres[i]) - 4:.1f}" text-anchor="middle" font-size="11" fill="#1e293b">{pres[i]:.2f}</text>')
        lab = f"slice {i + 1}" + (" (core)" if i == K - 1 else "")
        a.add(f'<text x="{x0 + bw * 0.4:.1f}" y="{h - mb + 15}" text-anchor="middle" font-size="11" fill="#334155">{i + 1 if i < K - 1 else "core"}</text>')
        a.add(f'<text x="{x0 + bw * 0.4:.1f}" y="{h - mb + 30}" text-anchor="middle" font-size="10.5" fill="#64748b">{rho[i]:.2f}</text>')
    a.add(f'<text x="{ml - 4}" y="{h - mb + 30}" text-anchor="end" font-size="10.5" fill="#64748b">rho:</text>')
    a.add(f'<text x="{ml - 4}" y="{h - mb + 15}" text-anchor="end" font-size="11" fill="#334155">slice:</text>')
    a.hline(0.9, "#16a34a", "clean line 0.9")
    a.add(f'<rect x="{ml + 6}" y="4" width="12" height="12" fill="#22c55e"/><text x="{ml + 22}" y="14" font-size="12">clean rung</text>'
          f'<rect x="{ml + 110}" y="4" width="12" height="12" fill="#f87171"/><text x="{ml + 126}" y="14" font-size="12">not clean</text>'
          f'<rect x="{ml + 210}" y="4" width="12" height="12" fill="#cbd5e1"/><text x="{ml + 226}" y="14" font-size="12">same seed, untrained encoder</text>')
    return a.svg()

def small_charts():
    out = []
    a = Ax(430, 250, (0.5, K - 0.5), (0, 0.1), ml=58)
    a.frame([(i, str(i)) for i in range(1, K)], [0, 0.025, 0.05, 0.075, 0.1], "rung", "invariance residual")
    a.hline(0.05, "#16a34a", "limit 0.05")
    a.line(range(1, K), res, "#2563eb")
    out.append(a.svg())
    b = Ax(430, 250, (1.5, K + 0.5), (0, 0.12), ml=58)
    b.frame([(i, str(i)) for i in range(2, K + 1)], [0, 0.04, 0.08, 0.12], "slice", "leakage of faster layers")
    b.hline(0.1, "#16a34a", "limit 0.1")
    b.line(range(2, K + 1), np.clip(leak, 0, None), "#2563eb")
    out.append(b.svg())
    return '<div class="two">' + "".join(out) + "</div>"

def spectra():
    picks = [1, 3, 5, 7, 10]
    cols = ["#f59e0b", "#ef4444", "#8b5cf6", "#2563eb", "#16a34a"]
    a = Ax(880, 330, (1, 44), (np.log10(0.002), np.log10(4.5)))
    a.frame([(i, str(i)) for i in (1, 5, 10, 15, 20, 25, 30, 35, 40, 44)], [], "eigenvalue number (largest first)", "eigenvalue of the pair-difference matrix (log scale)")
    for e in (0.01, 0.1, 1.0):
        y = np.log10(e)
        a.add(f'<line x1="{a.ml}" x2="{a.w - a.mr}" y1="{a.Y(y):.1f}" y2="{a.Y(y):.1f}" stroke="#e2e8f0"/><text x="{a.ml - 6}" y="{a.Y(y) + 4:.1f}" text-anchor="end" font-size="11" fill="#475569">{e:g}</text>')
    for k, c in zip(picks, cols):
        ev = np.array(run["rungs"][k - 1]["eigvals"])
        a.line(range(1, len(ev) + 1), np.log10(ev), c, r=2.2, w=1.6)
        big = int((ev > 1).sum())
        a.add(f'<text x="{a.X(big) + 4:.1f}" y="{a.Y(np.log10(3.0)) + 2:.1f}" font-size="11.5" fill="{c}" font-weight="700">rung {k}</text>')
    return a.svg()

def counts_table():
    rows = []
    for k in range(1, K):
        ev = np.array(run["rungs"][k - 1]["eigvals"]); big = int((ev > 1).sum())
        rows.append([(str(k), ""), (f"{rho[k - 1]:.2f}", ""), (f"{big}", ""), (f"{4 * k}", ""),
                     (f"{ev[big - 1]:.2f} / {ev[big]:.3f}", ""), (f"{ev[big - 1] / ev[big]:.0f}", "ok")])
    return table(["Rung k", "Layer speed", "Large eigenvalues (above 1)", "Expected 4k", "Last large / first small", "Ratio"], rows)

def slice_table():
    rows = []
    for i in range(K):
        ok = (i == K - 1 and pres[i] >= 0.9) or (i < K - 1 and A.rung_clean(run, i + 1)[0])
        rows.append([(f"{i + 1}" + (" (core)" if i == K - 1 else ""), ""), (f"{rho[i]:.2f}", ""), (f"{pres[i]:.3f}", "ok" if pres[i] >= 0.9 else "no"), (f"{lin[i]:.2f}", ""),
                     ("-" if i == 0 else f"{leak[i - 1]:.3f}", "ok" if i == 0 or leak[i - 1] <= 0.1 else "no"),
                     ("-" if i == K - 1 else f"{res[i]:.3f}", "" if i == K - 1 else ("ok" if res[i] <= 0.05 else "no")),
                     (f"{Su['presence'][i]:.3f}", ""), ("yes" if ok else "no", "ok" if ok else "no")])
    return table(["Slice", "Layer speed", "Presence (MLP readout)", "Presence (linear)", "Leakage of faster layers", "Invariance residual", "Presence, untrained", "Clean?"], rows)

def seeds_table():
    rows = []
    for r in M.e71[K]:
        nc = sum(A.rung_clean(r, k)[0] for k in range(1, K))
        rows.append([(str(r["seed"]) + (" (shown)" if r["seed"] == seed else ""), ""), (f"{nc} of {K - 1}", ""), (f"{np.mean(r['slice']['presence']):.2f}", ""), (f"{r['output_cov_min_eig']:.2f}", "")])
    return table(["Seed", "Clean rungs", "Mean slice presence", "Health"], rows)

def build():
    ref = ref_of(rho)
    fast = [i for i in range(K) if rho[i] < 0.86]
    slow = [i for i in range(K) if rho[i] >= 0.86]
    slow_ok = all((i == K - 1 and pres[i] >= 0.9) or (i < K - 1 and A.rung_clean(run, i + 1)[0]) for i in slow)
    ladder = [g for g in run["rungs"]]
    okf = lambda i: (i == K - 1 and pres[i] >= 0.9) or (i < K - 1 and A.rung_clean(run, i + 1)[0])
    cleanset = [i for i in range(K) if okf(i)]; notclean = [i for i in range(K) if not okf(i)]
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Best seed in detail</title>
<style>
body{{font:15px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#1e293b;max-width:920px;margin:24px auto;padding:0 18px}}
h1{{font-size:27px;margin:0 0 4px}}h2{{font-size:20px;margin:28px 0 8px;border-bottom:2px solid #e2e8f0;padding-bottom:4px}}
.sub{{color:#475569;margin-bottom:12px}}table{{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0}}td,th{{border:1px solid #cbd5e1;padding:4px 8px;text-align:left}}th{{background:#f1f5f9}}
td.ok{{background:#ecfdf5}}td.no{{background:#fef2f2}}svg{{max-width:100%;height:auto}}.note{{color:#475569;font-size:13px}}
.box{{background:#f8fafc;border-left:4px solid #6366f1;padding:8px 14px;margin:10px 0}}.two{{display:flex;gap:10px;flex-wrap:wrap}}.two svg{{flex:1 1 400px}}ul{{margin:6px 0 6px 18px;padding:0}}
{EQ_CSS}</style></head><body>
<h1>The best seed, in detail</h1>
<div class="sub">E71a, K = {K} layers ({K - 1} rungs), coupling strength 0.5, arm A (joint nested loss), seed {seed}. W = {run['W']}, {run['encoder_final']['step'] + 1:,} steps, {run['seconds'] / 3600:.1f} h on the GPU.</div>
<div class="box"><b>How it was chosen, and what that means.</b> Best = the run with the largest share of clean rungs among the 15 E71a runs: {ncl} of {K - 1} rungs clean (next best: {cands[1][4]} of {cands[1][2] - 1}, K = {cands[1][2]}, seed {cands[1][3]}). It was picked after looking at all runs, so it is the most favourable one, not a typical one; the other four seeds at this K are in the last table. Even this run does not pass the registered test (all rungs clean).</div>

<h2>Summary of this run</h2>
<ul>
<li><b>Clean slices:</b> {", ".join(str(i + 1) for i in cleanset)} (speeds {rho[cleanset[0]]:.2f} to {rho[-1]:.2f}): presence {min(pres[i] for i in cleanset):.2f} to {max(pres[i] for i in cleanset):.2f}, no leakage, residual at most {max(res[i] for i in cleanset if i < K - 1):.3f}. Slice {cleanset[0] + 1} (speed {rho[cleanset[0]]:.2f}) only just passes: presence {pres[cleanset[0]]:.3f}.</li>
<li><b>Not clean:</b> slices {", ".join(str(i + 1) for i in notclean)} (speeds {rho[0]:.2f} to {rho[notclean[-1]]:.2f}): presence {min(pres[i] for i in notclean):.2f} to {max(pres[i] for i in notclean):.2f}, short of the 0.9 line by {0.9 - max(pres[i] for i in notclean):.2f} to {0.9 - min(pres[i] for i in notclean):.2f}. Slice 1 also has residual {res[0]:.3f} against the 0.05 limit.</li>
<li><b>Health:</b> smallest output-covariance eigenvalue {run['output_cov_min_eig']:.2f} (needs 0.5): not collapsed.</li>
<li><b>Prediction loss:</b> {run['encoder_final']['pred']:.3f}, against {ref:.3f} for a faithful embedding (excess {run['encoder_final']['pred'] - ref:+.3f}).</li>
<li><b>Whole-latent readout:</b> global R-squared {run['global_r2']:.3f} (untrained, same seed: {unt['global_r2']:.3f}).</li>
</ul>

<h2>1. Every slice: trained against untrained</h2>
{bars()}
<p class="note">Green/red bars = this trained run; grey = the untrained encoder on the same seed. Number below each bar = the layer's speed rho.</p>
{slice_table()}

<h2>2. Invariance and leakage</h2>
{small_charts()}
<p class="note">Residual: how far the slices slower than rung k differ between the two members of a rung-k pair (0 = identical, about 2 = unrelated). Leakage: the largest R-squared with which any faster layer can be read from the slice.</p>

<h2>3. The pair-difference spectrum at each rung</h2>
<p>For rung k, the matrix of pair differences has directions the pairs change in (eigenvalue about 2) and directions they leave alone (eigenvalue near 0). A clean nested split would show exactly 4k large eigenvalues at rung k (layers 1 to k, 4 numbers each).</p>
{spectra()}
{counts_table()}
<p>The counts match the expected 4k at rungs 2 to 10, and are 5 at rung 1 (one more than 4). The drop from the large to the small group is a factor of {min(float(np.array(g['eigvals'])[(np.array(g['eigvals']) > 1).sum() - 1] / np.array(g['eigvals'])[(np.array(g['eigvals']) > 1).sum()]) for g in ladder):.0f} to {max(float(np.array(g['eigvals'])[(np.array(g['eigvals']) > 1).sum() - 1] / np.array(g['eigvals'])[(np.array(g['eigvals']) > 1).sum()]) for g in ladder):.0f} at every rung. <b>So the geometry of the pair differences is nested as intended, even for the fast layers whose slices are not readable.</b> A caution: the stored ladder measure for the same embedding (eigen-split angle to the true block, a linear comparison) reads {ladder[0]['angle_deg']:.0f} to {max(g['angle_deg'] for g in ladder):.0f} degrees and gap ratio about 1.0 at every rung, i.e. it reports no recovered block. I have not reconciled the two readings; the angle compares linear subspaces of a nonlinear embedding, so it is the likelier one to understate recovery, but that is a guess, not a result.</p>

<h2>4. The other seeds at this depth</h2>
{seeds_table()}
<p class="note">Limits: one run picked as the best of 15 by the rung rule; the measures are those of the registered E71 rule; the trained encoder was not saved, so nothing beyond these stored numbers can be shown for this run.</p>
{equations_html()}
</body></html>"""
    return html

if __name__ == "__main__":
    open(OUT, "w").write(build())
    print("wrote", OUT, "K", K, "seed", seed, "clean", ncl)
