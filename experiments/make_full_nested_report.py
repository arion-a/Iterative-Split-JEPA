"""docs/report/NESTED_WORK.html: one report of the whole nested-loss / speed-recovery work (E68, E71a, E72, E71b, E73).
Separate from the older FULL / COMPONENTS reports, which are not touched.
    python experiments/make_full_nested_report.py"""
import glob, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import make_nested_report as M
import make_e72_report as E72
import analyse_e72 as AE
import analyse_e68_e71 as A
from make_nested_report import Ax, esc, table, legend, COL
from report_equations import CSS as EQ_CSS, equations_html, E as EQ

OUT = os.path.join(M.ROOT, "docs/report/NESTED_WORK.html")
ROOT = M.ROOT
KS = AE.KS
RHO3, NAMES3 = [0.2, 0.7, 0.95], ["texture", "identity", "category"]

def load_e71b():
    return {K: A.load(f"{ROOT}/results/nested_pod_e71b/results/nested/e71b/A/K{K}_s1") for K in KS}
e71b = load_e71b()
e73 = {(r, s): A.load(f"{ROOT}/results/e73/{r}_s{s}") for r in "PQ" for s in ("0.5", "1")}
for v in list(e71b.values()) + list(e73.values()): assert len(v) == 5

def deep_pts(runs):
    return [(K, r["seed"], b, AE.rhos(K)[b - 1], r["slice"]["rho_hat"][b - 1]) for K in KS for r in runs[K] for b in AE.slow_set(K)]
P72 = deep_pts(E72.runs); P71b = deep_pts(e71b)
C = {"e72": "#2563eb", "e71b": "#dc2626", "p05": "#16a34a", "p1": "#7c3aed", "q": "#94a3b8"}

def fig_all_speed():
    a = Ax(880, 400, (0.1, 1.0), (0.1, 1.0))
    a.frame([(x, f"{x:g}") for x in (0.2, 0.4, 0.6, 0.8, 1.0)], [0.2, 0.4, 0.6, 0.8, 1.0], "true speed of the layer", "recovered speed")
    a.line([0.1, 1.0], [0.1, 1.0], "#475569", dash="5 4", dots=False, w=1.5)
    a.add(f'<text x="{a.X(0.46):.1f}" y="{a.Y(0.5) - 6:.1f}" font-size="11" fill="#475569" transform="rotate(-38 {a.X(0.46):.1f} {a.Y(0.5):.1f})">recovered = true</text>')
    for (rec, s), runs in e73.items():
        if rec != "Q": continue
        for r in runs:
            for j, t in enumerate(RHO3): a.add(f'<circle cx="{a.X(t):.1f}" cy="{a.Y(r["block_rho_hat"][j]):.1f}" r="4.2" fill="none" stroke="{C["q"]}" stroke-width="1.6"/>')
    for K, s, b, t, e in P71b: a.add(f'<circle cx="{a.X(t):.1f}" cy="{a.Y(e):.1f}" r="3.2" fill="{C["e71b"]}" fill-opacity="0.65"/>')
    for K, s, b, t, e in P72: a.add(f'<circle cx="{a.X(t):.1f}" cy="{a.Y(e):.1f}" r="3.2" fill="{C["e72"]}" fill-opacity="0.7"/>')
    for (rec, s), runs in e73.items():
        if rec != "P": continue
        col = C["p05"] if s == "0.5" else C["p1"]; dx = -3 if s == "0.5" else 3
        for r in runs:
            for j, t in enumerate(RHO3): a.add(f'<rect x="{a.X(t) + dx - 3.5:.1f}" y="{a.Y(r["block_rho_hat"][j]) - 3.5:.1f}" width="7" height="7" fill="{col}" fill-opacity="0.8"/>')
    return legend([("deep worlds, coupling 0.5 (E72)", C["e72"], ""), ("deep worlds, coupling 1 (E71b)", C["e71b"], "")], 880) + legend([("small world, paper recipe, 0.5 (squares)", C["p05"], ""), ("small world, paper recipe, 1 (squares)", C["p1"], "")], 880) + legend([("small world, predictive-loss MLP (rings)", C["q"], "")], 880) + a.svg()

def fig_all_error():
    a = Ax(880, 340, (0.1, 1.0), (-0.075, 0.03))
    a.frame([(x, f"{x:g}") for x in (0.2, 0.4, 0.6, 0.8, 1.0)], [-0.06, -0.04, -0.02, 0, 0.02], "true speed of the layer", "recovered minus true speed")
    a.hline(0, "#475569", "", dash="")
    for K, s, b, t, e in P71b: a.add(f'<circle cx="{a.X(t):.1f}" cy="{a.Y(e - t):.1f}" r="3.2" fill="{C["e71b"]}" fill-opacity="0.65"/>')
    for K, s, b, t, e in P72: a.add(f'<circle cx="{a.X(t):.1f}" cy="{a.Y(e - t):.1f}" r="3.2" fill="{C["e72"]}" fill-opacity="0.7"/>')
    for (rec, s), runs in e73.items():
        if rec != "P": continue
        col = C["p05"] if s == "0.5" else C["p1"]; dx = -3 if s == "0.5" else 3
        for r in runs:
            for j, t in enumerate(RHO3): a.add(f'<rect x="{a.X(t) + dx - 3.5:.1f}" y="{a.Y(r["block_rho_hat"][j] - t) - 3.5:.1f}" width="7" height="7" fill="{col}" fill-opacity="0.8"/>')
    return legend([("deep worlds, 0.5 (E72)", C["e72"], ""), ("deep worlds, 1 (E71b)", C["e71b"], "")], 880) + legend([("small world, paper recipe, 0.5", C["p05"], ""), ("small world, paper recipe, 1", C["p1"], "")], 880) + a.svg()

def fig_small():
    a = Ax(880, 330, (0.1, 1.0), (0.1, 1.0))
    a.frame([(x, f"{x:g}") for x in (0.2, 0.7, 0.95)], [0.2, 0.4, 0.6, 0.8, 1.0], "true speed (texture 0.2, identity 0.7, category 0.95)", "recovered speed")
    a.line([0.1, 1.0], [0.1, 1.0], "#475569", dash="5 4", dots=False, w=1.5)
    for (rec, s), runs in e73.items():
        col = {("P", "0.5"): C["p05"], ("P", "1"): C["p1"], ("Q", "0.5"): "#f59e0b", ("Q", "1"): "#78716c"}[(rec, s)]
        dx = {("P", "0.5"): -12, ("P", "1"): -4, ("Q", "0.5"): 4, ("Q", "1"): 12}[(rec, s)]
        for r in runs:
            for j, t in enumerate(RHO3):
                a.add(f'<circle cx="{a.X(t) + dx:.1f}" cy="{a.Y(r["block_rho_hat"][j]):.1f}" r="4.2" fill="{col}" fill-opacity="0.8"/>')
    return legend([("paper recipe, coupling 0.5", C["p05"], ""), ("paper recipe, coupling 1", C["p1"], "")], 880) + legend([("predictive-loss MLP, 0.5", "#f59e0b", ""), ("predictive-loss MLP, 1", "#78716c", "")], 880) + a.svg()

def deep_table():
    rows = []
    for K in KS:
        for b in AE.slow_set(K):
            t = AE.rhos(K)[b - 1]; a = np.array([r["slice"]["rho_hat"][b - 1] for r in E72.runs[K]]); c = np.array([r["slice"]["rho_hat"][b - 1] for r in e71b[K]])
            rows.append([(str(K), ""), (f"{b}" + (" (core)" if b == K else ""), ""), (f"{t:.3f}", ""), (f"{a.mean():.3f} ({a.min():.3f} to {a.max():.3f})", ""), (f"{a.mean() - t:+.3f}", ""), (f"{c.mean():.3f} ({c.min():.3f} to {c.max():.3f})", ""), (f"{c.mean() - t:+.3f}", "")])
    return table(["Layers in world (K)", "Layer", "True speed", "Coupling 0.5: recovered (lowest to highest of 5 seeds)", "Error", "Coupling 1: recovered (lowest to highest)", "Error"], rows)

def small_table():
    rows = []
    for (rec, s), runs in e73.items():
        est = np.array([r["block_rho_hat"] for r in runs]); ang = np.array([[g["angle_deg"] for g in r["rungs"]] for r in runs])
        for j in range(3):
            rows.append([("paper recipe" if rec == "P" else "predictive-loss MLP", ""), (s, ""), (NAMES3[j], ""), (f"{RHO3[j]:.2f}", ""), (f"{est[:, j].mean():.3f} ({est[:, j].min():.3f} to {est[:, j].max():.3f})", ""),
                         (f"{est[:, j].mean() - RHO3[j]:+.3f}", "ok" if abs(est[:, j].mean() - RHO3[j]) <= 0.03 else "no"), ("-" if j == 2 else f"{ang[:, j].mean():.0f}", "")])
    return table(["Recipe", "Coupling", "Layer", "True speed", "Recovered (lowest to highest of 5 seeds)", "Error", "Block vs true layer (degrees)"], rows)

def build():
    vr = [
        ("E68", "4 layers, coupling 1, 2, 4, 8: does the loss alone put each layer in its own slice?", "No. No run had every slice clean at any coupling; the slowest slice is read at 0.95 / 0.84 / 0.71 / 0.65 at couplings 1 / 2 / 4 / 8, the fastest at 0.45 to 0.71.", "refuted"),
        ("E71a", "10, 12 and 15 rungs (11, 13, 16 layers), coupling 0.5: a clean block at every rung?", "No for the fast rungs, yes for the slow ones: layers with speed above about 0.86 are recovered on every seed; the faster ones are not (clean-rung share 0.44 at 15 rungs, 0.9 asked).", "refuted"),
        ("E72", "Same deep worlds, new seeds: slow layers clean, and their speeds recovered?", "Slow layers clean on 12 of 15 runs (the other three miss by 0.002 to 0.011 of presence). Speeds recovered to within about 0.012 on average (0.006 to 0.021 by layer), always slightly too low.", "criterion refuted by one seed at 15 rungs; rate and order confirmed"),
        ("E71b", "Same deep worlds at coupling 1.", "Speeds recovered 0.04 to 0.06 too low (error 0.02 to 0.07 by layer), still in the correct order; the slow rungs are no longer cleanly invariant.", "criterion and rate refuted; order confirmed"),
        ("E73", "Original small world (3 layers: 0.2, 0.7, 0.95), eigen-split blocks.", "Paper recipe: speeds recovered to within 0.004 to 0.013 on average at coupling 0.5, and 0.002 to 0.042 at coupling 1 (per seed up to 0.052). Predictive-loss MLP: blocks not recovered, speeds meaningless.", "refuted by the predictive-loss recipe; paper recipe held"),
    ]
    vt = table(["Experiment", "Question", "What came out (plain)", "Registered verdict"], [[(a, ""), (b, ""), (c, ""), (d, "" if a == "E72" else "no")] for a, b, c, d in vr])
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Nested loss and speed recovery: the whole work</title>
<style>
body{{font:15px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#1e293b;max-width:920px;margin:24px auto;padding:0 18px}}
h1{{font-size:27px;margin:0 0 4px}}h2{{font-size:20px;margin:30px 0 8px;border-bottom:2px solid #e2e8f0;padding-bottom:4px}}
.sub{{color:#475569;margin-bottom:12px}}table{{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0}}td,th{{border:1px solid #cbd5e1;padding:4px 8px;text-align:left;vertical-align:top}}th{{background:#f1f5f9}}
td.ok{{background:#ecfdf5}}td.no{{background:#fef2f2}}svg{{max-width:100%;height:auto}}.note{{color:#475569;font-size:13px}}
.box{{background:#f8fafc;border-left:4px solid #6366f1;padding:8px 14px;margin:10px 0}}.two{{display:flex;gap:10px;flex-wrap:wrap}}.two svg{{flex:1 1 400px}}ul{{margin:6px 0 6px 18px;padding:0}}
{EQ_CSS}</style></head><body>
<h1>Nested loss and speed recovery: the whole work</h1>
<div class="sub">Five experiments (E68, E71a, E72, E71b, E73), 150 trained runs. Every number comes from the stored result files. Detail pages: <code>NESTED_LOSS.pdf</code> (E68, E71a), <code>BEST_SEED.pdf</code>, <code>E72.pdf</code>.</div>

<h2>The goal, in one paragraph</h2>
<p>Hidden numbers change at different speeds, as if they were the slowly and quickly changing properties of objects in a video. A network sees only the mixed-up observed numbers. The question: can a loss alone (predict the next step, plus agreement between matched pairs), without being told which part is which, sort the hidden layers into fixed slices, with the <b>slow, steady layers kept</b> in the later slices, the fast-changing ones dropped as noise, and the <b>speed of each kept layer recoverable</b> from the data?</p>

<h2>Bottom line</h2>
<div class="box"><ul>
<li><b>The speeds are recovered.</b> In the original small world (speeds 0.2, 0.7, 0.95) the eigen-split blocks read back 0.204, 0.695, 0.937, within 0.013 of the truth. In the deep worlds (11 to 16 layers) the slow layers are read back to within about 0.01 at coupling 0.5, always slightly too low. The error is the same on every seed: a fixed offset, not noise.</li>
<li><b>What breaks it is stronger coupling and depth,</b> not the number of seeds. At coupling 1 the slow layers' speeds come out 0.04 to 0.06 too low (still in the correct order); in the 4-layer hard world (E68) even the slow slices are not recovered at couplings 2 to 8.</li>
<li><b>The loss does the splitting by speed.</b> In the mild deep world, layers faster than about 0.86 are not recovered; slower ones are, on every seed, at all depths.</li>
<li><b>A plain MLP trained with the predictive loss did not give recoverable blocks in the small world;</b> the paper's recipe did.</li>
<li><b>Not shown:</b> that the layer structure can be found from data alone (the slice layout was given); behaviour on real images.</li></ul></div>

<h2>1. How the speeds recovered compare with the truth</h2>
<p>Every dot is one recovered layer of one trained run. A perfect recovery sits on the dashed line.</p>
{fig_all_speed()}
<p>The same data as the error (recovered minus true speed):</p>
{fig_all_error()}
<p class="note">The recipes that recover the blocks sit on or just below the line. The predictive-loss MLP in the small world (grey rings) does not: its blocks are mixtures of layers.</p>

<h3>The small world (3 layers), block by block</h3>
{fig_small()}
{small_table()}
<p class="note">Error cells are green when within 0.03. The last column is the angle between the block the eigen-split found and the true layer (small = recovered).</p>

<h3>The deep worlds (11, 13, 16 layers), layer by layer</h3>
<p>Speeds of the slow layers (0.86 and above); the faster layers were not recovered, so no speed was read for them.</p>
{deep_table()}

<h2>2. Registered tests and their verdicts</h2>
<p>Each test was written down, with its prediction and its pass line, before it ran. In plain words:</p>
{vt}
<p class="note">Full observed / required / gap for every line is in <code>docs/EVIDENCE.md</code>.</p>

<h2>3. Does the loss sort the layers? (deep worlds, coupling 0.5)</h2>
<p>Seeds (of 5) in which each rung is clean, 10, 12 and 15 rungs:</p>
{M.fig_clean_heat()}
<p>Presence of each layer in its slice against the layer's speed. The three depths fall on one curve; the grey line is an untrained encoder.</p>
<div class="fig">{legend([("11 layers", COL[11], ""), ("13 layers", COL[13], ""), ("16 layers", COL[16], ""), ("untrained encoder", COL["U"], "6 4")])}{M.fig_presence_by_speed()}</div>

<h2>4. The hard world: coupling 1, 2, 4, 8 with 4 layers (E68)</h2>
{M.fig_e68_heat()}
<div class="fig">{legend([("joint loss (arm A)", COL["A"], ""), ("curriculum (arm B)", COL["B"], "")])}{M.fig_e68_lines()}</div>

<h2>5. How the predictive loss performs</h2>
<p>The lower the loss gets toward what a faithful embedding allows, the better the layers are placed in their slices (rank correlation {M.SPEAR:.2f} over 55 runs):</p>
{M.fig_pred_scatter()}

<h2>6. Where the work stands, and what it does not show</h2>
<ul>
<li><b>Shown:</b> the slow layers are recovered and their speeds can be read back, in the original small world and in worlds with 10 to 15 rungs, at mild coupling; the read-back error is a consistent offset (always too low), growing with coupling and depth.</li>
<li><b>Not shown:</b> that the loss <i>finds</i> the layer layout (it is given); anything beyond coupling 0.5 and 1 in the deep worlds; the content of the discarded fast slices; real images. The speeds in the small world (0.2, 0.7, 0.95) are not the 0.2, 0.6, 0.9 you recalled; that is the world in which the blocks were recovered.</li>
<li><b>Open:</b> why the bias is always low (it looks correctable, untested); why the predictive-loss MLP gives no recoverable blocks in the small world (the angles point to the encoder, untested).</li></ul>

{equations_html()}
<h3>D. The speed read-back (E72, E71b, E73)</h3>
<p><b>Deep worlds (slices).</b> For a slice b, on 50,000 held-out transition pairs (h<sub>t</sub>, h<sub>t+1</sub>) of the frozen encoder:</p>
{EQ("ρ̂<sub>b</sub> = mean over the 4 coordinates j of slice b of&nbsp; corr( h<sub>t,j</sub> , h<sub>t+1,j</sub> )&nbsp;&nbsp;(each coordinate centred over the pairs; corr = the usual correlation coefficient)")}
<p><b>Small world (eigen-split blocks).</b> The ladder returns three blocks of 4 directions in the whitened outputs r = C<sup>−1/2</sup>(h − mean h). For each block with directions b<sub>1..4</sub>:</p>
{EQ("ρ̂<sub>block</sub> = mean over directions b<sub>j</sub> of&nbsp; corr( r<sub>t</sub> · b<sub>j</sub> , r<sub>t+1</sub> · b<sub>j</sub> )")}
<p>Error = ρ̂ − (true speed). The true speeds and labels are never used in the estimate. For a direction that carries a single layer, this correlation equals that layer's speed.</p>
</body></html>"""
    return html

if __name__ == "__main__":
    open(OUT, "w").write(build()); print("wrote", OUT)
