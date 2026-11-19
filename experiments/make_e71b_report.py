"""docs/report/E71B.html: report of E71b (deep worlds at coupling strength 1) with pictures and the transformation maths.
    python experiments/make_e71b_report.py"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import make_technical_report as T
import make_full_nested_report as F
import make_nested_report as M
import analyse_e72 as AE
import analyse_e68_e71 as A
from make_nested_report import Ax, table, legend, esc, heat_col, COL, rho_of, ref_of
from report_equations import CSS as EQ_CSS, E as EQ

OUT = os.path.join(M.ROOT, "docs/report/E71B.html")
ROOT = M.ROOT
KS = AE.KS
B = F.e71b                                    # E71b arm A runs, by K
U = {K: A.load(f"{ROOT}/results/nested_pod_e71b/results/nested/e71b/U/K{K}_s1") for K in KS}
M72 = F.E72.runs                              # E72 (coupling 0.5) for comparison
CB, C72, CU = "#dc2626", "#2563eb", "#94a3b8"
slow = {K: AE.slow_set(K) for K in KS}
W = {K: json.load(open(f"{ROOT}/results/nested_pod_e71b/results/nested/e71b/W_K{K}_s1.json")) for K in KS}
for K in KS: assert W[K]["W"] == 1

def pts(runs, key="rho_hat"):
    return [(K, r["seed"], b, AE.rhos(K)[b - 1], r["slice"]["rho_hat"][b - 1]) for K in KS for r in runs[K] for b in slow[K]]
PB, P72 = pts(B), pts(M72)
PU = pts(U)

def fig_scatter():
    a = Ax(880, 380, (0.84, 0.975), (0.55, 1.0))
    a.frame([(x, f"{x:g}") for x in (0.85, 0.88, 0.91, 0.94, 0.97)], [0.6, 0.7, 0.8, 0.9, 1.0], "true speed of the layer", "recovered speed")
    a.line([0.84, 0.975], [0.84, 0.975], "#16a34a", dash="5 4", dots=False, w=1.6)
    for K, s, b, t, e in PU: a.add(f'<circle cx="{a.X(t):.1f}" cy="{a.Y(e):.1f}" r="3" fill="{CU}" fill-opacity="0.55"/>')
    for K, s, b, t, e in P72: a.add(f'<circle cx="{a.X(t):.1f}" cy="{a.Y(e):.1f}" r="3.2" fill="{C72}" fill-opacity="0.5"/>')
    for K, s, b, t, e in PB: a.add(f'<circle cx="{a.X(t):.1f}" cy="{a.Y(e):.1f}" r="3.6" fill="{CB}" fill-opacity="0.75"/>')
    a.add(f'<text x="{a.X(0.845):.1f}" y="{a.Y(0.69):.1f}" font-size="12" fill="#64748b">untrained encoder: {min(p[4] for p in PU):.2f} to {max(p[4] for p in PU):.2f} whatever the layer</text>')
    return legend([("E71b, coupling 1 (trained)", CB, ""), ("E72, coupling 0.5 (trained, for comparison)", C72, ""), ("untrained encoder (E71b worlds)", CU, "")], 880) + a.svg()

def fig_error():
    a = Ax(880, 330, (0.84, 0.975), (-0.085, 0.03))
    a.frame([(x, f"{x:g}") for x in (0.85, 0.88, 0.91, 0.94, 0.97)], [-0.08, -0.06, -0.04, -0.02, 0, 0.02], "true speed of the layer", "recovered minus true speed")
    a.add(f'<rect x="{a.ml}" y="{a.Y(0.02):.1f}" width="{a.w - a.ml - a.mr}" height="{a.Y(-0.02) - a.Y(0.02):.1f}" fill="#dcfce7" fill-opacity="0.55"/>')
    a.hline(0, "#475569", "", dash="")
    for src, col in ((P72, C72), (PB, CB)):
        for K, s, b, t, e in src: a.add(f'<circle cx="{a.X(t):.1f}" cy="{a.Y(e - t):.1f}" r="3.2" fill="{col}" fill-opacity="0.6"/>')
    a.add(f'<text x="{a.X(0.845):.1f}" y="{a.Y(0.012):.1f}" font-size="11" fill="#16a34a">green band: registered limit, error 0.02</text>')
    return legend([("E71b, coupling 1", CB, ""), ("E72, coupling 0.5", C72, "")], 880) + a.svg()

def fig_resid():
    out = []
    for K in KS:
        n = K - 1
        a = Ax(290, 260, (1, 15.5), (0, 0.2), ml=46, mr=8, mb=38)
        a.frame([(x, str(x)) for x in (1, 5, 10, 15) if x <= n], [0, 0.05, 0.1, 0.15, 0.2], "rung", "invariance residual" if K == KS[0] else "")
        a.hline(0.05, "#16a34a", "limit 0.05" if K == KS[0] else "")
        a.line(range(1, n + 1), np.mean([r["slice"]["invariance_residual"] for r in M72[K]], axis=0), C72, r=2, w=1.5)
        a.line(range(1, n + 1), np.mean([r["slice"]["invariance_residual"] for r in B[K]], axis=0), CB, r=2, w=1.8)
        a.add(f'<text x="{a.w / 2:.0f}" y="12" text-anchor="middle" font-size="12" font-weight="700">{K} layers ({n} rungs)</text>')
        out.append(a.svg())
    return legend([("E71b, coupling 1", CB, ""), ("E72, coupling 0.5", C72, "")], 880) + '<div class="two">' + "".join(out) + "</div>"

def fig_presence():
    a = Ax(880, 330, (0.15, 0.975), (-0.05, 1.04))
    a.frame([(x, f"{x:g}") for x in (0.2, 0.4, 0.6, 0.8, 0.86, 0.95)], [0, 0.25, 0.5, 0.75, 0.9, 1.0], "layer speed rho", "presence of the layer in its own slice")
    a.hline(0.9, "#16a34a", "clean line 0.9"); a.vline(0.86, "#475569", "0.86 cut")
    for K in KS:
        t = AE.rhos(K)
        a.line(t, np.mean([r["slice"]["presence"] for r in M72[K]], axis=0), C72, dash="4 3", dots=False, w=1.5)
        for r in B[K]: a.line(t, r["slice"]["presence"], CB, w=1.0, dots=False)
    return legend([("E71b runs, coupling 1 (one line each)", CB, ""), ("E72 mean per depth, coupling 0.5", C72, "4 3")], 880) + a.svg()

def fig_clean():
    cw, ch, left, top = 44, 30, 120, 34
    o = [f'<svg viewBox="0 0 880 {top + 3 * ch + 44}" width="880">']
    o.append(f'<text x="{left}" y="14" font-size="12" fill="#334155" font-weight="700">rung number: 1 = fastest layer</text>')
    for j in range(1, 16): o.append(f'<text x="{left + (j - 1) * cw + cw / 2}" y="{top - 6}" text-anchor="middle" font-size="11" fill="#475569">{j}</text>')
    for i, K in enumerate(KS):
        y = top + i * ch
        o.append(f'<text x="{left - 8}" y="{y + 20}" text-anchor="end" font-size="12.5" font-weight="700">K = {K}</text>')
        for j in range(1, K):
            c = sum(A.rung_clean(r, j)[0] for r in B[K])
            o.append(f'<rect x="{left + (j - 1) * cw}" y="{y}" width="{cw - 2}" height="{ch - 2}" fill="{heat_col(c / 5)}" stroke="#fff"/><text x="{left + (j - 1) * cw + cw / 2 - 1}" y="{y + 19}" text-anchor="middle" font-size="12">{c}</text>')
        o.append(f'<rect x="{left + (K - 1) * cw}" y="{y}" width="{cw - 2}" height="{ch - 2}" fill="#e2e8f0" stroke="#fff"/><text x="{left + (K - 1) * cw + cw / 2 - 1}" y="{y + 19}" text-anchor="middle" font-size="11" fill="#475569">core</text>')
    yb = top + 3 * ch + 14
    for c in range(6): o.append(f'<rect x="{left + c * 40}" y="{yb}" width="38" height="16" fill="{heat_col(c / 5)}" stroke="#fff"/><text x="{left + c * 40 + 19}" y="{yb + 12}" text-anchor="middle" font-size="11">{c}</text>')
    o.append(f'<text x="{left + 250}" y="{yb + 12}" font-size="12" fill="#334155">= seeds (of 5) in which the rung is clean</text>')
    return "".join(o) + "</svg>"

def seed_grid():
    cw, ch, left, top = 100, 21, 150, 40
    rows = [(K, r) for K in KS for r in B[K]]
    o = [f'<svg viewBox="0 0 880 {top + len(rows) * ch + 40}" width="880">']
    heads = ["Criterion S", "min presence", "max residual", "Speed R", "largest error", "Order"]
    for j, h in enumerate(heads): o.append(f'<text x="{left + j * cw + cw / 2}" y="26" text-anchor="middle" font-size="11.5" fill="#334155" font-weight="700">{h}</text>')
    for i, (K, r) in enumerate(rows):
        y = top + i * ch + (6 if i >= 5 else 0) + (6 if i >= 10 else 0)
        if i % 5 == 0: o.append(f'<text x="{left - 78}" y="{y + 15}" text-anchor="end" font-size="12" font-weight="700" fill="{CB}">K = {K}</text>')
        o.append(f'<text x="{left + 34}" y="{y + 15}" text-anchor="end" font-size="11" fill="#64748b">seed {r["seed"]}</text>')
        pm = min(r["slice"]["presence"][b - 1] for b in slow[K]); rm = max(r["slice"]["invariance_residual"][b - 1] for b in slow[K] if b < K); em = max(AE.errs(r, K))
        S, Rr, O = AE.passes_S(r, K), AE.passes_R(r, K), AE.passes_order(r, K)
        cells = [("pass" if S else "fail", S), (f"{pm:.3f}", pm >= 0.9), (f"{rm:.3f}", rm <= 0.05), ("pass" if Rr else "fail", Rr), (f"{em:.3f}", em <= 0.02), ("pass" if O else "fail", O)]
        for j, (t, ok) in enumerate(cells):
            o.append(f'<rect x="{left + j * cw + 40}" y="{y}" width="{cw - 42}" height="{ch - 2}" fill="{"#bbf7d0" if ok else "#fecaca"}" stroke="#fff"/><text x="{left + j * cw + 40 + (cw - 42) / 2}" y="{y + 14}" text-anchor="middle" font-size="12">{t}</text>')
    return "".join(o) + "</svg>"

def build():
    n_pass = {k: [sum(f(r, K) for r in B[K]) for K in KS] for k, f in (("S", AE.passes_S), ("R", AE.passes_R), ("O", AE.passes_order))}
    assert n_pass["S"] == [0, 0, 0] and n_pass["R"] == [0, 0, 0] and n_pass["O"] == [5, 5, 5]
    allc = [sum(A.all_rungs_clean(r) for r in B[K]) for K in KS]
    st = {}
    for K in KS:
        sl = slow[K]; sg = np.array([[r["slice"]["rho_hat"][b - 1] - AE.rhos(K)[b - 1] for b in sl] for r in B[K]])
        st[K] = dict(mp=min(r["slice"]["presence"][b - 1] for r in B[K] for b in sl), mr=max(r["slice"]["invariance_residual"][b - 1] for r in B[K] for b in sl if b < K),
                     me=np.abs(sg).max(), sg=sg.mean(), sd=sg.std(0, ddof=1).mean(), sg72=np.mean([[r["slice"]["rho_hat"][b - 1] - AE.rhos(K)[b - 1] for b in sl] for r in M72[K]]),
                     health=np.mean([r["output_cov_min_eig"] for r in B[K]]), pred=np.mean([r["encoder_final"]["pred"] for r in B[K]]), ref=ref_of(AE.rhos(K)),
                     sec=np.mean([r["seconds"] for r in B[K]]), mrel=np.mean(np.abs(sg) / (1 - np.array([AE.rhos(K)[b - 1] for b in sl]))))
    res = table(["Line", "Registered requirement", "Observed (K = 11 / 13 / 16)", "Gap"], [
        [("(a) slow-rung criterion S", ""), ("at least 3 of 5 seeds at each K", ""), (" / ".join(str(x) for x in n_pass["S"]) + " of 5", "no"), ("short by 3 seeds at every K", "no")],
        [("(b) speeds within 0.02 (every slow slice)", ""), ("at least 3 of 5 seeds at each K", ""), (" / ".join(str(x) for x in n_pass["R"]) + " of 5", "no"), ("short by 3 seeds at every K; largest error " + " / ".join(f"{st[K]['me']:.3f}" for K in KS) + " vs 0.02", "no")],
        [("(c) order of the speeds", ""), ("at least 3 of 5 seeds at each K", ""), (" / ".join(str(x) for x in n_pass["O"]) + " of 5", "ok"), ("none", "ok")],
        [("reported, not judged: every rung clean", ""), ("-", ""), (" / ".join(str(x) for x in allc) + " of 5", ""), ("-", "")]])
    layer = []
    for K in KS:
        for b in slow[K]:
            t = AE.rhos(K)[b - 1]; e = np.array([r["slice"]["rho_hat"][b - 1] for r in B[K]]); e2 = np.array([r["slice"]["rho_hat"][b - 1] for r in M72[K]])
            layer.append([(str(K), ""), (f"{b}" + (" (core)" if b == K else ""), ""), (f"{t:.3f}", ""), (f"{e.mean():.3f}", ""), (f"{e.min():.3f} to {e.max():.3f}", ""), (f"{e.std(ddof=1):.3f}", ""),
                          (f"{e.mean() - t:+.3f}", "no"), (f"{e2.mean() - t:+.3f}", "")])
    lt = table(["K", "Layer", "True speed", "Recovered (mean of 5)", "Lowest to highest", "Seed sd", "Error, coupling 1", "Error, coupling 0.5 (E72)"], layer)
    def first90(runs):
        K = 16; m = np.mean([r['slice']['presence'] for r in runs[K]], axis=0); return next(AE.rhos(K)[b - 1] for b in slow[K] if m[b - 1] >= 0.9)
    f16b, f16a = first90(B), first90(M72)
    pilot = " / ".join(f"{W[K]['pilot_min_eig']['1']:.3f}" for K in KS)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>E71b report</title>
<style>
body{{font:15px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#1e293b;max-width:940px;margin:24px auto;padding:0 18px}}
h1{{font-size:27px;margin:0 0 4px}}h2{{font-size:20px;margin:30px 0 8px;border-bottom:2px solid #e2e8f0;padding-bottom:4px}}h3{{font-size:16px;margin:18px 0 4px}}
.sub{{color:#475569;margin-bottom:12px}}table{{border-collapse:collapse;width:100%;font-size:13px;margin:8px 0}}td,th{{border:1px solid #cbd5e1;padding:4px 8px;text-align:left;vertical-align:top}}th{{background:#f1f5f9}}
td.ok{{background:#ecfdf5}}td.no{{background:#fef2f2}}svg{{max-width:100%;height:auto}}.note{{color:#475569;font-size:13px}}code{{font-size:12.5px}}
.box{{background:#f8fafc;border-left:4px solid #6366f1;padding:8px 14px;margin:10px 0}}.two{{display:flex;gap:8px;flex-wrap:wrap}}.two svg{{flex:1 1 280px}}ul{{margin:6px 0 6px 18px;padding:0}}
.step{{margin:12px 0;break-inside:avoid}}.sh{{display:flex;justify-content:space-between;gap:12px;font-size:14.5px}}.sh .code{{color:#64748b;font-size:12px}}.sh2{{font-size:13px;color:#475569;margin:2px 0 0 4px}}
{EQ_CSS}</style></head><body>
<h1>E71b: deep worlds at the stronger coupling (strength 1)</h1>
<div class="sub">30 runs: 11, 13 and 16 layers (10, 12, 15 rungs), nested loss (arm A) and an untrained control, 5 new seeds (300 to 304). Run on an RTX 4090 pod, mean time per trained run {st[11]['sec'] / 3600:.1f} h / {st[13]['sec'] / 3600:.1f} h / {st[16]['sec'] / 3600:.1f} h. All numbers come from <code>results/nested_pod_e71b</code>. Registered in <code>docs/EVIDENCE.md</code> before any run (owner override of the original condition; coupling chosen by the owner).</div>

<h2>1. Result in plain words</h2>
<div class="box"><ul>
<li><b>Speeds are recovered in the right order, but read too low.</b> For the slow layers (speed 0.86 and above) the recovered speed is below the true one on every seed: mean error {st[11]['sg']:+.3f} / {st[13]['sg']:+.3f} / {st[16]['sg']:+.3f} at 11 / 13 / 16 layers (at coupling 0.5, E72: {st[11]['sg72']:+.3f} / {st[13]['sg72']:+.3f} / {st[16]['sg72']:+.3f}). The seeds agree with each other (standard deviation about {np.mean([st[K]['sd'] for K in KS]):.3f}), so the error is a consistent offset, not noise.</li>
<li><b>In terms of how fast the layer changes (1 − speed)</b> the recovered rate is {100 * st[11]['mrel']:.0f}% / {100 * st[13]['mrel']:.0f}% / {100 * st[16]['mrel']:.0f}% too large (E72: about 15%).</li>
<li><b>The slow rungs are no longer cleanly invariant:</b> the invariance residual of the slow rungs reaches {st[11]['mr']:.3f} / {st[13]['mr']:.3f} / {st[16]['mr']:.3f} (limit 0.05) and slow-layer presence falls to {st[11]['mp']:.3f} / {st[13]['mp']:.3f} / {st[16]['mp']:.3f} (needs 0.9).</li>
<li><b>Both registered accuracy lines fail on every seed</b> (table below); the order line holds on every seed.</li></ul></div>
{res}

<h2>2. Recovered speed against true speed</h2>
<p>Each dot is one slow layer of one trained run (15 runs). The green dashed line is a perfect recovery.</p>
{fig_scatter()}
<p>Error (recovered minus true) against the true speed. The error is largest for the layers at the edge of the slow set and grows with depth.</p>
{fig_error()}
<h3>Layer by layer</h3>
{lt}

<h2>3. Why the slow-rung criterion fails</h2>
<p>Invariance residual by rung (mean over 5 seeds). At coupling 0.5 the slow rungs stay near 0.02; at coupling 1 they rise to 0.07 to 0.18, above the 0.05 limit, most at 16 layers.</p>
{fig_resid()}
<p>Presence of each layer in its own slice against its speed. At 16 layers the mean presence of the slow layers stays below 0.9 until speed {f16b:.2f} at coupling 1, against {f16a:.2f} at coupling 0.5 (dashed).</p>
{fig_presence()}
<p>Seeds (of 5) in which each rung is clean at coupling 1:</p>
{fig_clean()}
<p class="note">Health (smallest eigenvalue of the output covariance) is {st[11]['health']:.2f} / {st[13]['health']:.2f} / {st[16]['health']:.2f} (needs 0.5); no slow slice shows leakage (largest {max(np.max(r['slice']['leakage_faster'][b - 2]) for K in KS for r in B[K] for b in slow[K] if b >= 2):.3f}). The failure is the residual and, at 13 and 16 layers, part of the presence.</p>
<h3>Seed by seed</h3>
{seed_grid()}

<h2>4. The transformations, with equations</h2>
<p class="note">Notation: K layers of 4 numbers, d = 4K = 44 / 52 / 64; z = [z<sub>1</sub> | ... | z<sub>K</sub>] hidden numbers (layer 1 fastest); coupling strength s = 1; batch N = 256. Equation numbers refer to <code>NESTED_TECHNICAL.pdf</code>.</p>
{T.d_pipeline()}
{T.step(1, "Hidden numbers over time", "z<sub>t+1,b</sub> = ρ<sub>b</sub> z<sub>t,b</sub> + √(1 − ρ<sub>b</sub><sup>2</sup>) ε<sub>t,b</sub>,&nbsp; ε ~ N(0, I<sub>4</sub>)", "Speeds: 1 − ρ<sub>b</sub> = 0.8 · 0.05<sup>(b−1)/(K−1)</sup>, from ρ<sub>1</sub> = 0.2 to ρ<sub>K</sub> = 0.96. Layers with ρ ≥ 0.86 are the 'slow' layers judged here (layers 7 to 11, 8 to 13, 10 to 16).", "<code>worlds.py: BlockWorld</code>")}
{T.step(2, "Observation (strength s = 1)", "z<sub>R</sub> := z<sub>R</sub> + tanh(z<sub>L</sub> W<sub>i</sub>) (i odd);&nbsp; z<sub>L</sub> := z<sub>L</sub> + tanh(z<sub>R</sub> W<sub>i</sub>) (i even);&nbsp; W<sub>i</sub> = 1 · Q<sub>i</sub>", "x = C<sub>1</sub>(z) ∈ R<sup>d</sup>; twice the coupling of E72 (s = 0.5), so each tanh term moves the numbers twice as far.", "<code>worlds.py: CouplingMap</code>")}
{T.step(3, "Matched pair of rung k", "v<sub>b</sub> = u<sub>b</sub> for b &gt; k;&nbsp; v<sub>b</sub> ~ N(0, I<sub>4</sub>) fresh for b ≤ k", "Layers slower than k identical in u and v.", "<code>worlds.py: correspondence_pairs</code>")}
{T.d_pairs()}
{T.step(4, "Encoder", "h = W<sub>3</sub> GELU(W<sub>2</sub> GELU(W<sub>1</sub> x)),&nbsp; h = [h<sub>1</sub> | ... | h<sub>K</sub>]", "d → 16K → 16K → d (hidden width 176 / 208 / 256).", "<code>encoder.py</code>")}
{T.step(5, "Loss for one step", "L = L<sub>pred</sub> + Σ<sub>k=1</sub><sup>K−1</sup> [ L<sub>inv,k</sub> + W L<sub>wd,k</sub> ] + W L<sub>wh</sub> + 0.01 L<sub>var</sub> + 0.04 L<sub>cov</sub>", f"W = 1 (pilot of 10,000 steps: smallest output-covariance eigenvalue {pilot} at 11 / 13 / 16 layers, all at least 0.5). 7,500 K steps = 82,500 / 97,500 / 120,000; AdamW, learning rate 3·10<sup>−3</sup>, cosine decay in the second half. Terms:", "<code>encoder.py: train_encoder</code>")}
{EQ("L<sub>pred</sub> = (1/N d) Σ ‖ f(h<sub>t</sub>) − sg(h<sub>t+1</sub>) ‖<sup>2</sup>;&nbsp; L<sub>inv,k</sub> = mean ( h<sup>u</sup><sub>T</sub> − h<sup>v</sup><sub>T</sub> )<sup>2</sup>, T = slices k+1..K;&nbsp; L<sub>wd,k</sub> = ‖ Cov(h<sup>u</sup><sub>k</sub> − h<sup>v</sup><sub>k</sub>) − 2 I<sub>4</sub> ‖<sub>F</sub><sup>2</sup>")}
{EQ("L<sub>wh</sub> = ‖ Cov(h) − I<sub>d</sub> ‖<sub>F</sub><sup>2</sup>;&nbsp; L<sub>var</sub> = Σ<sub>j</sub> max(0, 1 − √(Var h<sub>j</sub> + 10<sup>−4</sup>));&nbsp; L<sub>cov</sub> = (1/d) Σ<sub>i≠j</sub> Cov(h)<sub>ij</sub><sup>2</sup>")}
{T.d_lossmap()}
<p class="note">Final predictive loss (mean of 5 seeds, last training step) {st[11]['pred']:.3f} / {st[13]['pred']:.3f} / {st[16]['pred']:.3f}, against the reference (1/K) Σ(1 − ρ<sub>b</sub><sup>2</sup>) = {st[11]['ref']:.3f} / {st[13]['ref']:.3f} / {st[16]['ref']:.3f} for a faithful embedding.</p>
{T.step(7, "Presence, leakage, health", "presence<sub>b</sub> = R<sup>2</sup>(z<sub>b</sub> from h<sub>b</sub>);&nbsp; leakage<sub>b</sub> = max<sub>c&lt;b</sub> R<sup>2</sup>(z<sub>c</sub> from h<sub>b</sub>);&nbsp; health = λ<sub>min</sub>(Cov h)", "R<sup>2</sup> = 1 − Σ(z − ẑ)<sup>2</sup> / Σ(z − z̄)<sup>2</sup> from a tanh network (64 units, 800 steps), fitted on 15,000 and scored on 5,000 fresh points.", "<code>stage_b1.py: slice_measures</code>")}
{T.step(8, "Invariance residual", "r<sub>k</sub> = mean ( h<sup>u</sup><sub>T</sub> − h<sup>v</sup><sub>T</sub> )<sup>2</sup> / mean<sub>j∈T</sub> Var(h<sup>u</sup><sub>j</sub>)", "5,000 fresh rung-k pairs; 0 = identical, 2 = unrelated. Clean rung: presence ≥ 0.9, leakage ≤ 0.1, r ≤ 0.05.", "<code>stage_b1.py: invariance_residual</code>")}
{T.d_readouts()}
{T.step(10, "Speed read-back", "ρ̂<sub>b</sub> = mean over the 4 coordinates j of slice b of corr( h<sub>t,j</sub>, h<sub>t+1,j</sub> );&nbsp; error = ρ̂<sub>b</sub> − ρ<sub>b</sub>", "50,000 held-out transition pairs (z<sub>t</sub>, z<sub>t+1</sub>) from equation (1), pushed through (2) and (4); each coordinate centred over the pairs; no labels used. For a coordinate that carries one layer, the correlation equals the layer's speed; a coordinate that also mixes in faster layers would read lower, which could explain the low bias (not tested).", "<code>stage_b1.py: rho_hat</code>")}
{EQ("Slow-rung criterion S:&nbsp; health ≥ 0.5,&nbsp; every slow rung k &lt; K clean,&nbsp; core presence ≥ 0.9.&nbsp;&nbsp; Speed line R:&nbsp; max<sub>slow b</sub> |ρ̂<sub>b</sub> − ρ<sub>b</sub>| ≤ 0.02.&nbsp;&nbsp; Order:&nbsp; ρ̂<sub>b</sub> increasing in b over the slow layers.")}

<h2>5. Limits</h2>
<ul>
<li>One new coupling (1); with E72 (0.5) that is two points, not a map of the dependence.</li>
<li>Slices are read at fixed positions (layout given); the 0.86 cut was taken from E71a; oracle nested pairs; block sizes given; 5 seeds per cell; synthetic worlds.</li>
<li>The possible reason for the low bias given in step 10 (a slice that also mixes in faster layers reads lower) is a reading of the numbers, not tested.</li>
<li>Trained encoders were saved: <code>results/nested_pod_e71b/results/nested/e71b/A/K*_s1/enc_seed*.pt</code>.</li></ul>
</body></html>"""
    return html

if __name__ == "__main__":
    open(OUT, "w").write(build()); print("wrote", OUT)
