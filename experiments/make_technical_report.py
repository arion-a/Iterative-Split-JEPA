"""docs/report/NESTED_TECHNICAL.html: technical documentation and report of the nested-loss / speed-recovery experiments (E68, E71a, E72, E71b, E73).
Numbers are computed from the stored results; equations are the ones the code runs.
    python experiments/make_technical_report.py"""
import glob, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import make_full_nested_report as F
import make_nested_report as M
import analyse_e72 as AE
import analyse_e68_e71 as A
from make_nested_report import Ax, table, legend, COL
from report_equations import CSS as EQ_CSS, E as EQ

OUT = os.path.join(M.ROOT, "docs/report/NESTED_TECHNICAL.html")
ROOT = M.ROOT
def sec(pattern):
    v = [json.load(open(f)).get("seconds") for f in glob.glob(f"{ROOT}/{pattern}")]; v = [x for x in v if x]; return float(np.mean(v)), len(v)

# ------------------------------------------------------------------ diagrams (hand-built SVG)
DEFS = '<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0L8,4L0,8z" fill="#64748b"/></marker></defs>'
def box(x, y, w, h, fill, stroke, lines, fs=12.5, bold_first=True):
    o = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}"/>'
    n = len(lines); y0 = y + h / 2 - (n - 1) * 8 + 4
    for i, t in enumerate(lines):
        o += f'<text x="{x + w / 2}" y="{y0 + i * 16}" text-anchor="middle" font-size="{fs}" fill="#1e293b"' + (' font-weight="700"' if i == 0 and bold_first else "") + f'>{t}</text>'
    return o
def arrow(x1, y1, x2, y2): return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="#64748b" stroke-width="2" marker-end="url(#ar)"/>'

def d_pipeline():
    o = [f'<svg viewBox="0 0 880 250" width="880">{DEFS}']
    o.append(box(10, 30, 120, 70, "#e0e7ff", "#6366f1", ["hidden z", "4K numbers", "K layers of 4"]))
    o.append(box(170, 30, 130, 70, "#e0e7ff", "#6366f1", ["observation C", "4 tanh coupling", "layers (fixed)"]))
    o.append(box(340, 30, 120, 70, "#e0e7ff", "#6366f1", ["observed x", "4K numbers"]))
    o.append(box(500, 30, 130, 70, "#fef9c3", "#ca8a04", ["encoder g", "MLP 4K-16K-16K-4K"]))
    o.append(box(670, 30, 200, 70, "#dcfce7", "#16a34a", ["output h", "K slices of 4 numbers"]))
    for x1, x2 in ((130, 170), (300, 340), (460, 500), (630, 670)): o.append(arrow(x1, 65, x2, 65))
    for x, t in ((70, "(1), (3)"), (235, "(2)"), (565, "(4)"), (770, "(4)")): o.append(f'<text x="{x}" y="22" text-anchor="middle" font-size="12" fill="#6366f1" font-weight="700">{t}</text>')
    o.append('<text x="10" y="124" font-size="11.5" fill="#475569">z changes with time at a speed rho per layer (1); matched pairs share the slower layers (3)</text>')
    o.append(arrow(710, 100, 330, 150)); o.append(arrow(810, 100, 690, 150))
    o.append(box(130, 150, 400, 76, "#fee2e2", "#dc2626", ["training: loss L on the slices (5)", "predict next h; slower slices agree across a pair;", "slice k still varies; outputs spread"], fs=12))
    o.append(box(560, 150, 310, 76, "#dbeafe", "#2563eb", ["after training: read-outs (7) to (11)", "presence, leakage, residual, health, speed;", "eigen-split blocks (small world)"], fs=12))
    return "".join(o) + "</svg>"

def d_pairs():
    K, k = 6, 3; cw = 74; x0 = 130
    o = [f'<svg viewBox="0 0 880 190" width="880">{DEFS}']
    o.append(f'<text x="10" y="22" font-size="13" font-weight="700">A rung-k pair (u, v), example K = {K}, k = {k}</text>')
    for r, name, y in ((0, "u", 40), (1, "v", 100)):
        o.append(f'<text x="{x0 - 14}" y="{y + 32}" text-anchor="end" font-size="14" font-weight="700">{name}</text>')
        for b in range(1, K + 1):
            shared = b > k
            fill = "#bbf7d0" if shared else ("#fde68a" if r == 0 else "#fdba74")
            o.append(f'<rect x="{x0 + (b - 1) * cw}" y="{y}" width="{cw - 4}" height="46" rx="6" fill="{fill}" stroke="#64748b"/><text x="{x0 + (b - 1) * cw + (cw - 4) / 2}" y="{y + 28}" text-anchor="middle" font-size="12.5">layer {b}</text>')
    o.append(f'<text x="{x0 + (k * cw) / 2 - 2}" y="168" text-anchor="middle" font-size="12" fill="#b45309">layers 1 to {k}: redrawn independently</text>')
    o.append(f'<text x="{x0 + k * cw + ((K - k) * cw) / 2 - 2}" y="168" text-anchor="middle" font-size="12" fill="#15803d">layers {k + 1} to {K}: identical in u and v</text>')
    return "".join(o) + "</svg>"

def d_lossmap():
    K = 6; cw, ch, left, top = 70, 26, 230, 44
    rows = [("L_pred (predict next h)", set(range(1, K + 1)), "#fecaca", "all slices"),
            ("L_inv,2 (agree across pair)", set(range(3, K + 1)), "#bbf7d0", "slices 3 to 6 equal"),
            ("L_wd,2 (still varies)", {2}, "#fde68a", "slice 2 differs, cov 2I"),
            ("L_inv,4 (agree across pair)", set(range(5, K + 1)), "#bbf7d0", "slices 5, 6 equal"),
            ("L_wd,4 (still varies)", {4}, "#fde68a", "slice 4 differs, cov 2I"),
            ("L_wh, L_var, L_cov", set(range(1, K + 1)), "#e0e7ff", "outputs spread")]
    o = [f'<svg viewBox="0 0 880 {top + len(rows) * ch + 28}" width="880">']
    for b in range(1, K + 1): o.append(f'<text x="{left + (b - 1) * cw + cw / 2}" y="30" text-anchor="middle" font-size="12.5" font-weight="700">slice {b}</text>')
    for i, (name, act, col, note) in enumerate(rows):
        y = top + i * ch
        o.append(f'<text x="{left - 8}" y="{y + 17}" text-anchor="end" font-size="12" fill="#1e293b">{name}</text>')
        for b in range(1, K + 1):
            on = b in act
            o.append(f'<rect x="{left + (b - 1) * cw}" y="{y}" width="{cw - 2}" height="{ch - 2}" fill="{col if on else "#f1f5f9"}" stroke="#fff"/>')
        o.append(f'<text x="{left + K * cw + 6}" y="{y + 17}" font-size="11" fill="#64748b">{note}</text>')
    return "".join(o) + "</svg>"

def d_readouts():
    o = [f'<svg viewBox="0 0 880 250" width="880">{DEFS}']
    panels = [("presence_b", "#dcfce7", "#16a34a", ["slice b", "small net", "z_b", "R2 near 1: layer b is in slice b"]),
              ("leakage_b", "#fee2e2", "#dc2626", ["slice b", "small net", "z_c (c < b)", "R2 near 0: no faster layer in slice b"]),
              ("residual_k", "#fef9c3", "#ca8a04", ["h(u), h(v)", "slices k+1..K", "mean sq. difference", "near 0: slower slices agree"]),
              ("speed", "#dbeafe", "#2563eb", ["h_t, h_t+1", "one slice", "lag-1 correlation", "equals the layer's speed"])]
    for i, (title, fill, stroke, t) in enumerate(panels):
        x = 10 + i * 218
        o.append(f'<text x="{x + 100}" y="22" text-anchor="middle" font-size="13" font-weight="700">{title}</text>')
        o.append(box(x, 34, 200, 38, fill, stroke, [t[0]], bold_first=False)); o.append(arrow(x + 100, 72, x + 100, 92))
        o.append(box(x, 94, 200, 38, "#f8fafc", "#94a3b8", [t[1]], bold_first=False)); o.append(arrow(x + 100, 132, x + 100, 152))
        o.append(box(x, 154, 200, 38, fill, stroke, [t[2]], bold_first=False))
        o.append(f'<text x="{x + 100}" y="216" text-anchor="middle" font-size="11.5" fill="#475569">{t[3]}</text>')
    return "".join(o) + "</svg>"

def d_spectrum():
    d = json.load(open(f"{ROOT}/results/e73/P_s0.5/main_seed310.json"))
    out = []
    for k, nm in ((0, "rung 1 (texture split off)"), (1, "rung 2 (identity split off)")):
        ev = np.array(d["rungs"][k]["eigvals"]); n = len(ev)
        a = Ax(430, 270, (0.4, 12.6), (np.log10(0.004), np.log10(14)), ml=58, mt=22)
        a.frame([(i, str(i)) for i in range(1, n + 1)], [], "eigenvalue number (largest first)", "eigenvalue (log scale)")
        for e in (0.01, 0.1, 1.0):
            y = np.log10(e); a.add(f'<line x1="{a.ml}" x2="{a.w - a.mr}" y1="{a.Y(y):.1f}" y2="{a.Y(y):.1f}" stroke="#e2e8f0"/><text x="{a.ml - 6}" y="{a.Y(y) + 4:.1f}" text-anchor="end" font-size="11" fill="#475569">{e:g}</text>')
        for i, v in enumerate(ev):
            big = i < 4
            a.add(f'<rect x="{a.X(i + 1) - 9:.1f}" y="{a.Y(np.log10(v)):.1f}" width="18" height="{a.Y(np.log10(0.004)) - a.Y(np.log10(v)):.1f}" fill="{"#f59e0b" if big else "#94a3b8"}"/>')
        a.add(f'<text x="{a.X(2.5):.1f}" y="{a.Y(np.log10(5.0)):.1f}" text-anchor="middle" font-size="11.5" fill="#b45309" font-weight="700">variant block V{k + 1}</text>')
        a.add(f'<text x="{a.X(8.5):.1f}" y="{a.Y(np.log10(0.3)):.1f}" text-anchor="middle" font-size="11.5" fill="#64748b">left over (invariant)</text>')
        a.add(f'<text x="{a.w / 2:.0f}" y="12" text-anchor="middle" font-size="12" font-weight="700" fill="#1e293b">{nm}</text>')
        out.append(a.svg())
    return '<div class="two">' + "".join(out) + "</div>"

def step(num, title, eq, shapes, code):
    return f'<div class="step"><div class="sh"><b>({num}) {title}</b><span class="code">{code}</span></div>{EQ(eq)}<div class="sh2">{shapes}</div></div>'

# ------------------------------------------------------------------ numbers
def counts():
    e68 = {(a, s): sum(A.slice_clean(r) for r in F.M.e68[(a, s)]) for a in "AB" for s in (1, 2, 4, 8)}
    return e68
e68c = counts()
E72runs, E71b = F.E72.runs, F.e71b
def n_pass(runs, K, f): return sum(f(r, K) for r in runs[K])
S72, R72, O72 = [n_pass(E72runs, K, AE.passes_S) for K in AE.KS], [n_pass(E72runs, K, AE.passes_R) for K in AE.KS], [n_pass(E72runs, K, AE.passes_order) for K in AE.KS]
S71b, R71b, O71b = [n_pass(E71b, K, AE.passes_S) for K in AE.KS], [n_pass(E71b, K, AE.passes_R) for K in AE.KS], [n_pass(E71b, K, AE.passes_order) for K in AE.KS]
assert S72 == [5, 4, 3] and R72 == [5, 3, 4] and O72 == [5, 5, 5] and S71b == [0, 0, 0] and R71b == [0, 0, 0] and O71b == [5, 5, 5]
sg72 = np.mean([r["slice"]["rho_hat"][b - 1] - AE.rhos(K)[b - 1] for K in AE.KS for r in E72runs[K] for b in AE.slow_set(K)])
sg71b = np.mean([r["slice"]["rho_hat"][b - 1] - AE.rhos(K)[b - 1] for K in AE.KS for r in E71b[K] for b in AE.slow_set(K)])
P05 = np.array([r["block_rho_hat"] for r in F.e73[("P", "0.5")]]); P1 = np.array([r["block_rho_hat"] for r in F.e73[("P", "1")]])
Q05 = np.array([r["block_rho_hat"] for r in F.e73[("Q", "0.5")]]); Q1 = np.array([r["block_rho_hat"] for r in F.e73[("Q", "1")]])
T = np.array(F.RHO3)
def hrs(s): return f"{s / 3600:.1f} h"

def build():
    s68 = sec("results/nested_pod/results/nested/e68/A/s*/main_seed*.json")[0]; s71 = [sec(f"results/nested_pod/results/nested/e71/A/K{K}_s0.5/main_seed*.json")[0] for K in AE.KS]
    s72 = [sec(f"results/nested_pod_e72/results/nested/e72/A/K{K}_s0.5/main_seed*.json")[0] for K in AE.KS]; s71b = [sec(f"results/nested_pod_e71b/results/nested/e71b/A/K{K}_s1/main_seed*.json")[0] for K in AE.KS]
    s73p, s73q = sec("results/e73/P_s*/main_seed*.json")[0], sec("results/e73/Q_s*/main_seed*.json")[0]
    comp = table(["Component", "File", "What it does"], [
        ["Nested-loss training", "<code>src/isj/encoder.py</code> (<code>train_encoder</code>)", "Joint loss (5); option <code>corr_inv_schedule</code> (arm B curriculum), option <code>device</code> (GPU). Old behaviour unchanged (gate G1)."],
        ["Slice read-outs", "<code>src/isj/stage_b1.py</code> (<code>slice_measures</code>, <code>invariance_residual</code>)", "Presence, leakage, duplication, invariance residual, health (equations 7 to 9)."],
        ["Speed read-outs", "<code>src/isj/stage_b1.py</code> (<code>rho_hat</code>, <code>block_rho_hat</code>)", "Slice speed (deep worlds) and eigen-split block speed (small world), equation 10; options <code>rate_readout</code>, <code>save_encoder</code>."],
        ["Runners", "<code>experiments/run_nested_loss.py</code>, <code>run_e73.py</code>", "One process per cell and seed; W chosen by a pilot; results as JSON."],
        ["Pod supervisor and watcher", "<code>experiments/nested_sup.py</code>, <code>nested_watch*.sh</code>", "Queue of jobs with retries, resumable; local loop that syncs results and relaunches the supervisor."],
        ["Analysis (registered verdicts)", "<code>experiments/analyse_e68_e71.py</code>, <code>analyse_e72.py</code>, <code>analyse_e73.py</code>", "Applies the pre-registered rules; every failed line prints observed, required and gap."],
        ["Reports", "<code>experiments/make_*report*.py</code>", "Build the HTML and PDF reports from the stored results."],
        ["Tests", "<code>tests/test_nested_loss.py</code>, <code>test_analyse_nested.py</code>, <code>test_rate_readout.py</code>, <code>test_analyse_e72.py</code>, <code>test_block_rate.py</code>", "15 new tests; the full suite is 73 tests, all pass."],
        ["Registration and plan", "<code>docs/EVIDENCE.md</code> (E66 to E73), <code>docs/DESIGN_NESTED_LOSS.md</code>, <code>docs/PLAN_NESTED_LOSS_STEPS.md</code>", "Predictions written before each run (additions only; checked by <code>experiments/check_results.py</code>)."]])
    exp = table(["Exp.", "World", "Arms and setting", "Seeds", "Runs", "Hardware; mean time per run", "Results folder"], [
        ["E68", "4 layers, speeds 0.2, 0.5, 0.75, 0.95", "coupling 1, 2, 4, 8; joint loss (A) and curriculum (B); W = 1", "250-254", "40", f"RTX 3090 pod; {hrs(s68)} (A; many runs share the GPU)", "<code>results/nested_pod/results/nested/e68</code>"],
        ["E71a", "11, 13, 16 layers (10, 12, 15 rungs), speeds 0.2 to 0.96", "coupling 0.5; arm A; untrained control U; W = 1", "280-284", "30", f"RTX 3090 pod; {hrs(s71[0])} / {hrs(s71[1])} / {hrs(s71[2])} (A, K = 11 / 13 / 16)", "<code>.../nested/e71</code>"],
        ["E72", "as E71a", "coupling 0.5; A and U; speed read-out; encoders saved", "290-294", "30", f"RTX 3090 pod; {hrs(s72[0])} / {hrs(s72[1])} / {hrs(s72[2])}", "<code>results/nested_pod_e72/.../e72</code>"],
        ["E71b", "as E71a", "coupling 1; A and U; speed read-out; encoders saved", "300-304", "30", f"RTX 4090 pod; {hrs(s71b[0])} / {hrs(s71b[1])} / {hrs(s71b[2])}", "<code>results/nested_pod_e71b/.../e71b</code>"],
        ["E73", "3 layers, speeds 0.2, 0.7, 0.95 (texture, identity, category)", "coupling 0.5 and 1; recipe P (paper: mirror encoder, alignment + SIGReg) and Q (MLP, predictive loss); eigen-split blocks", "310-314", "20", f"local CPU; {s73p:.0f} s (P), {s73q:.0f} s (Q)", "<code>results/e73</code>"]])
    ver = table(["Check", "Result"], [
        ["Full test suite (<code>PYTHONPATH=src python -m pytest tests</code>)", "73 passed (58 earlier + 15 new)."],
        ["G1: encoder edits leave old behaviour unchanged", "300-step training log and embedding bit-for-bit identical to the code before the edits."],
        ["G2: runner reproduces a stored result", "E45 seed 160 reproduced exactly (angles 0.94, 1.66, 1.8 degrees; gaps 83.2, 62.5, 97.4; health 0.92)."],
        ["Unit tests of the measures", "Presence about 1 and leakage about 0 on an embedding equal to the hidden numbers; presence about 0 on noise; residual 0 for an invariant tail; rate estimators recover known AR(1) speeds within 0.01 (also after a rotation inside a block, and 0 for time-shuffled pairs); verdict logic checked on made-up results before any real result existed."],
        ["Pre-registration check", "<code>experiments/check_results.py evidence</code>: 0 lines of <code>EVIDENCE.md</code> deleted or changed since the baseline (additions only)."],
        ["Smoke runs", "Each new runner mode (e72, e71b, e73) run for 200 to 300 steps before the batch; result files, saved encoder and speed read-outs written."]])
    res = table(["Exp.", "Registered line", "Observed", "Required", "Gap"], [
        ["E68", "(a) arm A slice-clean, coupling 1", f"{e68c[('A', 1)]} of 5", "at least 4", "short by 4 seeds"],
        ["E68", "(b) better arm slice-clean, coupling 4", f"{max(e68c[('A', 4)], e68c[('B', 4)])} of 5", "at least 3", "short by 3 seeds"],
        ["E68", "(c) curriculum minus joint, couplings 2, 4, 8", "0", "at least 2", "short by 2"],
        ["E71a", "(a) all rungs clean, 10 / 12 / 15 rungs", "0 / 0 / 0 of 5", "at least 3 of 5 each", "short by 3 seeds each"],
        ["E71a", "(b) clean-rung share at 15 rungs", "0.440", "at least 0.9", "short by 0.460"],
        ["E72", "(a) slow-rung criterion, K = 11 / 13 / 16", " / ".join(f"{x}" for x in S72) + " of 5", "at least 4 each", "K = 16: short by 1 seed (presence 0.897, 0.889 vs 0.9)"],
        ["E72", "(b) speeds within 0.02", " / ".join(f"{x}" for x in R72) + " of 5", "at least 3 each", "met"],
        ["E72", "(c) order of the speeds", " / ".join(f"{x}" for x in O72) + " of 5", "at least 3 each", "met"],
        ["E71b", "(a) slow-rung criterion, K = 11 / 13 / 16", " / ".join(f"{x}" for x in S71b) + " of 5", "at least 3 each", "short by 3 seeds each (residual 0.07 to 0.18 vs 0.05)"],
        ["E71b", "(b) speeds within 0.02", " / ".join(f"{x}" for x in R71b) + " of 5", "at least 3 each", "short by 3 seeds each (largest error 0.061 / 0.063 / 0.074)"],
        ["E71b", "(c) order of the speeds", " / ".join(f"{x}" for x in O71b) + " of 5", "at least 3 each", "met"],
        ["E73", "(a) recipe P, coupling 0.5, every block within 0.03", "5 of 5", "at least 4", "met (largest error 0.015)"],
        ["E73", "(b) recipe Q, coupling 1, every block within 0.03", "0 of 5", "at least 3", "short by 3 seeds (largest error 0.441)"]])
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Nested loss and speed recovery: technical report</title>
<style>
body{{font:15px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#1e293b;max-width:940px;margin:24px auto;padding:0 18px}}
h1{{font-size:27px;margin:0 0 4px}}h2{{font-size:20px;margin:30px 0 8px;border-bottom:2px solid #e2e8f0;padding-bottom:4px}}h3{{font-size:16px;margin:18px 0 4px}}
.sub{{color:#475569;margin-bottom:12px}}table{{border-collapse:collapse;width:100%;font-size:13px;margin:8px 0}}td,th{{border:1px solid #cbd5e1;padding:4px 8px;text-align:left;vertical-align:top}}th{{background:#f1f5f9}}
td.ok{{background:#ecfdf5}}td.no{{background:#fef2f2}}svg{{max-width:100%;height:auto}}.note{{color:#475569;font-size:13px}}code{{font-size:12.5px}}
.box{{background:#f8fafc;border-left:4px solid #6366f1;padding:8px 14px;margin:10px 0}}.two{{display:flex;gap:10px;flex-wrap:wrap}}.two svg{{flex:1 1 400px}}ul{{margin:6px 0 6px 18px;padding:0}}
.step{{margin:12px 0;break-inside:avoid}}.sh{{display:flex;justify-content:space-between;gap:12px;font-size:14.5px}}.sh .code{{color:#64748b;font-size:12px}}.sh2{{font-size:13px;color:#475569;margin:2px 0 0 4px}}
{EQ_CSS}</style></head><body>
<h1>Nested loss and speed recovery: technical report</h1>
<div class="sub">Scope: what was built for the experiments E68, E71a, E72, E71b and E73, how every number is computed from the input data, what was run, and what came out. Synthetic worlds only. 150 trained runs. All numbers are taken from the stored result files.</div>

<h2>1. Summary</h2>
<div class="box"><ul>
<li><b>Question.</b> Can a loss alone, without being told which part is which, place hidden layers that change at different speeds into fixed slices of the encoder output, so that the slow layers are kept and their speeds can be read back?</li>
<li><b>Speeds are recovered where the layers are recovered.</b> Small world (true speeds 0.2, 0.7, 0.95), paper recipe: recovered {P05[:, 0].mean():.3f}, {P05[:, 1].mean():.3f}, {P05[:, 2].mean():.3f} at coupling 0.5 (errors {P05[:, 0].mean() - 0.2:+.3f}, {P05[:, 1].mean() - 0.7:+.3f}, {P05[:, 2].mean() - 0.95:+.3f}) and {P1[:, 0].mean():.3f}, {P1[:, 1].mean():.3f}, {P1[:, 2].mean():.3f} at coupling 1. Deep worlds (slow layers, speed at least 0.86): mean error {sg72:+.4f} at coupling 0.5 and {sg71b:+.4f} at coupling 1; always below the true speed; order always correct.</li>
<li><b>The loss splits by speed.</b> With 10 to 15 rungs at coupling 0.5, layers slower than about 0.86 are recovered on every seed; faster ones are not.</li>
<li><b>It fails with stronger coupling</b> (the 4-layer hard world at couplings 2 to 8; the speeds at coupling 1 in deep worlds read 0.04 to 0.06 too low) <b>and with a plain MLP trained on the predictive loss alone</b> (small world: blocks not recovered).</li>
<li><b>Registered verdicts:</b> E68 refuted; E71a refuted; E72 criterion refuted by one seed at 15 rungs, speeds and order confirmed; E71b criterion and speeds refuted, order confirmed; E73 refuted by the predictive-loss recipe, paper recipe held (section 5).</li></ul></div>

<h2>2. What was built</h2>
{comp}

<h2>3. The method: from input data to every reported number</h2>
<p class="note">Notation: K layers of 4 numbers each; d = 4K; z = [z<sub>1</sub> | ... | z<sub>K</sub>] the hidden numbers (layer 1 fastest); N = 256 is the batch size. Each equation names the function that computes it.</p>
{d_pipeline()}

<h3>3.1 Data</h3>
{step(1, "Hidden numbers over time", "z<sub>t+1,b</sub> = ρ<sub>b</sub> z<sub>t,b</sub> + √(1 − ρ<sub>b</sub><sup>2</sup>) ε<sub>t,b</sub>,&nbsp; ε ~ N(0, I<sub>4</sub>),&nbsp; z<sub>t,b</sub> ~ N(0, I<sub>4</sub>)", "z ∈ R<sup>4K</sup>. Speeds: E68 0.2, 0.5, 0.75, 0.95; E73 0.2, 0.7, 0.95; E71a/E72/E71b 1 − ρ<sub>b</sub> = 0.8 · 0.05<sup>(b−1)/(K−1)</sup> (0.2 to 0.96).", "<code>worlds.py: BlockWorld.transition_pairs</code>")}
{step(2, "Observation (fixed, not trained)", "four layers i = 1..4 alternating:&nbsp; z<sub>R</sub> := z<sub>R</sub> + tanh(z<sub>L</sub> W<sub>i</sub>) (i odd),&nbsp; z<sub>L</sub> := z<sub>L</sub> + tanh(z<sub>R</sub> W<sub>i</sub>) (i even);&nbsp; W<sub>i</sub> = s Q<sub>i</sub>", "x = C<sub>s</sub>(z) ∈ R<sup>d</sup> (E73 recipe Q: lifted to 16 numbers). z<sub>L</sub>, z<sub>R</sub> = halves of z; Q<sub>i</sub> fixed random orthogonal; s = coupling strength.", "<code>worlds.py: CouplingMap</code>")}
{step(3, "Matched pair of rung k", "u ~ N(0, I<sub>d</sub>);&nbsp; v<sub>b</sub> = u<sub>b</sub> for b &gt; k;&nbsp; v<sub>b</sub> ~ N(0, I<sub>4</sub>) fresh for b ≤ k", "Layers slower than k are shared exactly; layers 1 to k are redrawn.", "<code>worlds.py: BlockWorld.correspondence_pairs</code>")}
{d_pairs()}

<h3>3.2 Encoder and loss</h3>
{step(4, "Encoder", "h = g(x) = W<sub>3</sub> GELU(W<sub>2</sub> GELU(W<sub>1</sub> x)),&nbsp; h = [h<sub>1</sub> | ... | h<sub>K</sub>]", "R<sup>d</sup> → R<sup>16K</sup> → R<sup>16K</sup> → R<sup>d</sup>; slice b = coordinates 4(b−1) to 4b−1 is meant to hold layer b. Predictor f: same shape.", "<code>encoder.py: mlp</code>")}
{step(5, "Training loss (one step)", "L = L<sub>pred</sub> + Σ<sub>k=1</sub><sup>K−1</sup> [ 1·L<sub>inv,k</sub> + W·L<sub>wd,k</sub> ] + W·L<sub>wh</sub> + 0.01·L<sub>var</sub> + 0.04·L<sub>cov</sub>", "Terms below. W = 1 in every world (smaller of {1, 10} whose 10,000-step pilot keeps λ<sub>min</sub>(Cov h) ≥ 0.5). AdamW, learning rate 3·10<sup>−3</sup>, cosine decay in the second half; 7,500 K steps (E71a, E72, E71b), 30,000 (E68). Arm B switches the k-term on at step 5,000 (k−1).", "<code>encoder.py: train_encoder</code>")}
{EQ("L<sub>pred</sub> = (1/N d) Σ ‖ f(h<sub>t</sub>) − sg(h<sub>t+1</sub>) ‖<sup>2</sup>&nbsp;&nbsp;(sg = stop-gradient)")}
{EQ("L<sub>inv,k</sub> = mean ( h<sup>u</sup><sub>T</sub> − h<sup>v</sup><sub>T</sub> )<sup>2</sup>, T = slices k+1..K;&nbsp;&nbsp; L<sub>wd,k</sub> = ‖ Cov(h<sup>u</sup><sub>k</sub> − h<sup>v</sup><sub>k</sub>) − 2 I<sub>4</sub> ‖<sub>F</sub><sup>2</sup>")}
{EQ("L<sub>wh</sub> = ‖ Cov(h) − I<sub>d</sub> ‖<sub>F</sub><sup>2</sup>;&nbsp;&nbsp; L<sub>var</sub> = Σ<sub>j</sub> max(0, 1 − √(Var h<sub>j</sub> + 10<sup>−4</sup>));&nbsp;&nbsp; L<sub>cov</sub> = (1/d) Σ<sub>i≠j</sub> Cov(h)<sub>ij</sub><sup>2</sup>")}
{d_lossmap()}
<p class="note">Which slices each term acts on (example K = 6, k = 2 and 4). L<sub>inv,k</sub> is what makes the slower slices agree across a pair; L<sub>wd,k</sub> keeps slice k from collapsing; the others spread the whole output.</p>
<p class="note"><b>Which experiments use (5).</b> E68, E71a, E72 and E71b train with (5). E73 does not: recipe P (the paper recipe, mirror encoder) trains with an alignment loss (mean squared distance of h<sub>t</sub> and h<sub>t+1</sub> from their mean) plus 10<sup>−6</sup>·SIGReg; recipe Q (generic MLP) trains with L<sub>pred</sub> + 0.01·L<sub>var</sub> + 0.04·L<sub>cov</sub> only (no pair terms). In E73 the blocks come from the closed-form eigen-split (11), not from slices.</p>
{step(6, "Reference value of the predictive loss", "L<sub>pred</sub><sup>ref</sup> = (1/K) Σ<sub>b</sub> ( 1 − ρ<sub>b</sub><sup>2</sup> )", "Best one-step prediction when every layer is kept and outputs have unit variance: 0.561 (E68 speeds); 0.412, 0.410, 0.408 for K = 11, 13, 16. Approximate floor.", "<code>report only</code>")}

<h3>3.3 Read-outs on fresh data (encoder frozen)</h3>
<p class="note">20,000 fresh z (15,000 to fit read-outs, 5,000 to score), raw output h without whitening.</p>
{step(7, "Presence and leakage", "R<sup>2</sup>(z<sub>c</sub> from h<sub>a</sub>) = 1 − Σ(z<sub>c</sub> − ẑ<sub>c</sub>)<sup>2</sup> / Σ(z<sub>c</sub> − mean z<sub>c</sub>)<sup>2</sup>;&nbsp; presence<sub>b</sub> = R<sup>2</sup>(z<sub>b</sub> from h<sub>b</sub>);&nbsp; leakage<sub>b</sub> = max<sub>c&lt;b</sub> R<sup>2</sup>(z<sub>c</sub> from h<sub>b</sub>)", "ẑ from a tanh network (64 units, 800 Adam steps, batch 1,024, standardized inputs and targets).", "<code>stage_b1.py: slice_measures; audits.py: mlp_r2</code>")}
{step(8, "Invariance residual", "r<sub>k</sub> = mean ( h<sup>u</sup><sub>T</sub> − h<sup>v</sup><sub>T</sub> )<sup>2</sup> / mean<sub>j∈T</sub> Var(h<sup>u</sup><sub>j</sub>)", "5,000 fresh rung-k pairs. 0 = identical; two unrelated points give 2.", "<code>stage_b1.py: invariance_residual</code>")}
{step(9, "Health and the clean rules", "health = λ<sub>min</sub>( Cov(h) ).&nbsp; Rung k clean: presence<sub>k</sub> ≥ 0.9, leakage<sub>k</sub> ≤ 0.1 (k ≥ 2), r<sub>k</sub> ≤ 0.05.", "Seed all-rungs-clean: every rung clean, health ≥ 0.5 (core slice K: presence only). Slow-rung criterion (E72, E71b): the same for layers with ρ ≥ 0.86 only.", "<code>analyse_e68_e71.py: rung_clean; analyse_e72.py</code>")}
{d_readouts()}
{step(10, "Speed read-back", "ρ̂<sub>b</sub> = mean over the 4 coordinates j of slice b of corr( h<sub>t,j</sub>, h<sub>t+1,j</sub> )&nbsp;&nbsp;(each coordinate centred over the pairs)", "50,000 held-out transition pairs. Error = ρ̂ − ρ. Deep worlds: read from the slice b. Small world: read from the eigen-split blocks: ρ̂<sub>block</sub> = mean over the block's directions β of corr( r<sub>t</sub>·β, r<sub>t+1</sub>·β ), r = C<sup>−1/2</sup>(h − mean h).", "<code>stage_b1.py: rho_hat, block_rho_hat</code>")}

<h3>3.4 The closed-form eigen-split (small world, E73)</h3>
{step(11, "Pair-difference moment and blocks", "D = r(u) − r(v);&nbsp; M<sub>k</sub> = H<sub>k−1</sub><sup>T</sup> [ (1/n) Σ D D<sup>T</sup> ] H<sub>k−1</sub>;&nbsp; V<sub>k</sub> = top d<sub>k</sub> eigenvectors of M<sub>k</sub>,&nbsp; H<sub>k</sub> = the rest", "30,000 rung-k pairs, ZCA whitening from 30,000 points; H<sub>0</sub> = I. Directions the pair changes in have eigenvalue about 2; directions it leaves alone near 0. The last H is the core block.", "<code>engine.py: fit_whitener, difference_moment, fit_rung</code>")}
{d_spectrum()}
<p class="note">Real spectra (paper recipe, coupling 0.5, seed 310). At rung 1 four eigenvalues near 2 (texture), then values 0.009 to 0.047; at rung 2, inside what is left, again four (identity).</p>

<h2>4. What was run</h2>
{exp}

<h2>5. Results</h2>
<h3>5.1 Speeds against the truth</h3>
{F.fig_all_speed()}
<p class="note">Squares and circles: small world; blue and red dots: slow layers of the deep worlds. Per-layer tables with the lowest and highest of the 5 seeds are in <code>NESTED_WORK.pdf</code> and in <code>results/e73/REPORT_E73.md</code>, <code>results/nested_pod_e72/REPORT_E72.md</code>, <code>results/nested_pod_e71b/REPORT_E71B.md</code>.</p>
<table><tr><th></th><th>Texture 0.20</th><th>Identity 0.70</th><th>Category 0.95</th></tr>
<tr><td>Paper recipe, coupling 0.5: recovered (sd)</td><td>{P05[:, 0].mean():.3f} ({P05[:, 0].std(ddof=1):.3f})</td><td>{P05[:, 1].mean():.3f} ({P05[:, 1].std(ddof=1):.3f})</td><td>{P05[:, 2].mean():.3f} ({P05[:, 2].std(ddof=1):.3f})</td></tr>
<tr><td>Paper recipe, coupling 1</td><td>{P1[:, 0].mean():.3f} ({P1[:, 0].std(ddof=1):.3f})</td><td>{P1[:, 1].mean():.3f} ({P1[:, 1].std(ddof=1):.3f})</td><td>{P1[:, 2].mean():.3f} ({P1[:, 2].std(ddof=1):.3f})</td></tr>
<tr><td>Predictive-loss MLP, coupling 0.5</td><td>{Q05[:, 0].mean():.3f} ({Q05[:, 0].std(ddof=1):.3f})</td><td>{Q05[:, 1].mean():.3f} ({Q05[:, 1].std(ddof=1):.3f})</td><td>{Q05[:, 2].mean():.3f} ({Q05[:, 2].std(ddof=1):.3f})</td></tr>
<tr><td>Predictive-loss MLP, coupling 1</td><td>{Q1[:, 0].mean():.3f} ({Q1[:, 0].std(ddof=1):.3f})</td><td>{Q1[:, 1].mean():.3f} ({Q1[:, 1].std(ddof=1):.3f})</td><td>{Q1[:, 2].mean():.3f} ({Q1[:, 2].std(ddof=1):.3f})</td></tr></table>
<h3>5.2 Which layers are recovered (deep worlds, coupling 0.5, E71a)</h3>
<div class="fig">{legend([("11 layers", COL[11], ""), ("13 layers", COL[13], ""), ("16 layers", COL[16], ""), ("untrained encoder", COL["U"], "6 4")])}{M.fig_presence_by_speed()}</div>
<p class="note">Presence of each layer in its slice against its speed. First speed at which all 5 seeds are clean: 0.867 (K = 11), 0.861 (K = 13), 0.867 (K = 16); the layer just before is clean on only some seeds.</p>
<h3>5.3 Registered tests: observed, required, gap</h3>
{res}

<h2>6. Verification of the implementation</h2>
{ver}

<h2>7. Reproduction</h2>
<ul>
<li>Setup: <code>PYTHONPATH=src</code>; seeds as in section 4; one thread per process (<code>OMP_NUM_THREADS=1</code>).</li>
<li>Deep and hard worlds: <code>python experiments/run_nested_loss.py e68|e71|e72|e71b --arm A|B|U --strength S --depth K --seeds ... --device cuda</code>; the pod queue is <code>experiments/nested_sup.py [e72|e71b]</code>.</li>
<li>Small world: <code>python experiments/run_e73.py --recipe P|Q --strength 0.5|1</code>.</li>
<li>Verdicts: <code>python experiments/analyse_e68_e71.py ROOT</code>, <code>analyse_e72.py ROOT [e71b 1]</code>, <code>analyse_e73.py results/e73</code>. Reports: <code>experiments/make_technical_report.py</code>.</li>
<li>Trained encoders were saved for E72, E71b and E73 (<code>enc_seed*.pt</code>); not for E68 and E71a.</li></ul>

<h2>8. Limits, corrections and open points</h2>
<ul>
<li><b>Oracle and given structure:</b> matched pairs are exact (generator-made); block sizes are given; slices are read at fixed positions, so the speed test shows that a recovered slice's speed can be read back, not that the layout was found from data alone.</li>
<li><b>Thresholds are mine:</b> 0.9, 0.1, 0.05, the 0.86 speed cut (taken from E71a and reused in E72, E71b), 0.02 and 0.03 error limits, and the prediction levels; they were written before each run, but are not derived.</li>
<li><b>Scope:</b> one world family; 5 seeds per cell; coupling 0.5 and 1 in the deep worlds (two points, not a map); real images not tested.</li>
<li><b>Overrides and corrections on record:</b> E71b ran at the owner's request although its original condition (E68 line (b)) failed, at the owner-chosen coupling 1; the E73 outcome entry's "0.002 to 0.013" mixed a per-seed minimum with a mean (corrected by an appended erratum); E72 and E71b read the 0.86 cut from E71a.</li>
<li><b>Open:</b> why the speed read-back is always low (it looks like a consistent offset; a correction was not tested); why the predictive-loss MLP gives no recoverable blocks in the small world (the angles point to the encoder, not tested); in the best E71a seed the pair-difference spectrum shows the expected 4k large eigenvalues at every rung while the stored linear-subspace angle reads 56 to 90 degrees (not reconciled).</li></ul>
</body></html>"""
    return html

if __name__ == "__main__":
    open(OUT, "w").write(build()); print("wrote", OUT)
