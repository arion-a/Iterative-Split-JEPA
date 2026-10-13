"""Small inline-SVG chart helpers. Colours come from CSS tokens (--s1.. --mut ...) so one chart works in
light and dark themes; `standalone()` bakes literal light-theme colours for files that render on GitHub."""

from __future__ import annotations

import html
import math

E = html.escape
W = 720
PALETTE = ["--s1", "--s2", "--s3", "--s4", "--s5", "--s6"]          # blue, orange, aqua, yellow, magenta, green
LIGHT = {"--s1": "#2a78d6", "--s2": "#eb6834", "--s3": "#1baf7a", "--s4": "#eda100", "--s5": "#e87ba4", "--s6": "#008300",
         "--mut": "#898781", "--ink": "#0b0b0b", "--ink2": "#52514e", "--grid": "#e1e0d9", "--axis": "#c3c2b7", "--surf": "#fcfcfb"}
STYLE = (".grid{stroke:%(--grid)s;stroke-width:1}.axis{stroke:%(--axis)s;stroke-width:1}.limit{stroke:%(--ink2)s;stroke-width:1}"
         ".tick{fill:%(--mut)s;font:11.5px system-ui,sans-serif}.lab{fill:%(--ink2)s;font:12.5px system-ui,sans-serif}"
         ".val{fill:%(--ink)s;font:600 12.5px system-ui,sans-serif}.dot{stroke:%(--surf)s;stroke-width:2}")


def standalone(svg: str) -> str:
    for k, v in LIGHT.items():
        svg = svg.replace(f"var({k})", v)
    css = STYLE % LIGHT
    head, rest = svg.split(">", 1)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" {head[4:]}><rect width="100%" height="100%" fill="{LIGHT["--surf"]}"/>'
            f"<style>{css}</style>{rest}")


def _open(h, note, w=W):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{E(note)}" class="chart">'


def tip(s):
    return f'data-tip="{E(s)}"'


def log_lines(series, vline=None, vline_label="", ymin=1e-4, ymax=10, note="", xlabel="direction number, largest first", annotations=()):
    """Log-y line chart. series = [(label, [values], colvar)]. annotations = [(x_index, text, y_value)]"""
    L, R, T, B, H = 54, 20, 18, 44, 300
    n = max(len(s[1]) for s in series)
    px = lambda i: L + (i - 0.5) / n * (W - L - R)
    lo, hi = math.log10(ymin), math.log10(ymax)
    py = lambda v: T + (1 - (math.log10(max(v, ymin)) - lo) / (hi - lo)) * (H - T - B)
    o = [_open(H, note)]
    for e in range(int(lo), int(hi) + 1):
        o.append(f'<line x1="{L}" x2="{W-R}" y1="{py(10**e):.1f}" y2="{py(10**e):.1f}" class="grid"/>'
                 f'<text x="{L-8}" y="{py(10**e)+4:.1f}" class="tick" text-anchor="end">10{"".join("⁻⁰¹²³⁴⁵⁶⁷⁸⁹"[int(c)+1] if c.isdigit() else ("⁻" if c == "-" else "") for c in str(e))}</text>')
    for i in range(1, n + 1):
        o.append(f'<text x="{px(i):.1f}" y="{H-B+16}" class="tick" text-anchor="middle">{i}</text>')
    o.append(f'<text x="{(L+W-R)/2:.1f}" y="{H-8}" class="tick" text-anchor="middle">{E(xlabel)}</text>')
    if vline is not None:
        x = L + vline / n * (W - L - R)
        o.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{T}" y2="{H-B}" class="limit"/><text x="{x+6:.1f}" y="{T+12}" class="lab">{E(vline_label)}</text>')
    for label, ys, col in series:
        pts = " ".join(f"{px(i+1):.1f},{py(v):.1f}" for i, v in enumerate(ys))
        o.append(f'<polyline points="{pts}" fill="none" style="stroke:var({col})" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        for i, v in enumerate(ys):
            o.append(f'<circle cx="{px(i+1):.1f}" cy="{py(v):.1f}" r="4" class="dot" style="fill:var({col})" tabindex="0" {tip(f"{label}, direction {i+1}: {v:.4f}")}/>')
    for xi, text, yv in annotations:
        o.append(f'<text x="{px(xi)+8:.1f}" y="{py(yv)-8:.1f}" class="val">{E(text)}</text>')
    o.append(f'<line x1="{L}" x2="{W-R}" y1="{H-B}" y2="{H-B}" class="axis"/></svg>')
    return "".join(o)


SHAPES = ["circle", "diamond"]


def _mark(shape, x, y, r, col, t):
    if shape == "diamond":
        return (f'<path d="M{x:.1f},{y-r*1.3:.1f} L{x+r*1.3:.1f},{y:.1f} L{x:.1f},{y+r*1.3:.1f} L{x-r*1.3:.1f},{y:.1f} Z" class="dot" '
                f'style="fill:var({col})" {tip(t)}/>')
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="dot" style="fill:var({col})" {tip(t)}/>'


def scatter_pair(x, y, true_cat, cluster, note=""):
    """P7: two panels, same points. Left coloured by true category, right by discovered cluster (matched to categories)."""
    cats = sorted(set(true_cat))
    # match each cluster to the true category it overlaps most (greedy, each category used once); unmatched -> grey
    clusters = sorted(set(cluster))
    counts = {(c, k): 0 for c in cats for k in clusters}
    for c, k in zip(true_cat, cluster):
        counts[(c, k)] += 1
    match, used = {}, set()
    for (c, k), v in sorted(counts.items(), key=lambda kv: -kv[1]):
        if k not in match and c not in used and v > 0:
            match[k] = c; used.add(c)
    H, pw = 330, (W - 20) / 2
    xs, ys = min(x), max(x)
    xmin, xmax, ymin, ymax = xs, xs + (max(x) - xs), min(y), max(y)
    o = [_open(H, note)]
    for p, (title, col_of, shape_of) in enumerate([("True category", lambda i: PALETTE[true_cat[i] % 6], lambda i: SHAPES[true_cat[i] % 2]),
                                                  ("Discovered cluster", lambda i: PALETTE[match[cluster[i]] % 6] if cluster[i] in match else "--mut",
                                                   lambda i: SHAPES[match[cluster[i]] % 2] if cluster[i] in match else "circle")]):
        x0 = 10 + p * (pw + 0)
        px = lambda v: x0 + 14 + (v - xmin) / (xmax - xmin) * (pw - 28)
        py = lambda v: 34 + (1 - (v - ymin) / (ymax - ymin)) * (H - 52)
        o.append(f'<text x="{x0 + pw/2:.1f}" y="20" class="lab" text-anchor="middle">{title}</text>'
                 f'<rect x="{x0+4}" y="30" width="{pw-8}" height="{H-44}" fill="none" class="axis"/>')
        for i in range(len(x)):
            o.append(_mark(shape_of(i), px(x[i]), py(y[i]), 3, col_of(i), f"category {true_cat[i]+1}, cluster {cluster[i]+1}"))
    o.append("</svg>")
    return "".join(o)


def degradation(points, bound_a21_rung1, gen_a21, note=""):
    """P8: left rung-2 angle vs purity; right ||A21|| vs purity with the contamination-bound lines.
    points = [(purity, angle_deg, a21, sigma, seed)]"""
    H, L, T, B = 300, 50, 26, 44
    pw = (W - 30) / 2
    xmin, xmax = 0.3, 1.0
    o = [_open(H, note)]

    def panel(p, title, ymax, yticks, ylab, valf, lines, limit=None, limit_label=""):
        x0 = 10 + p * (pw + 10)
        px = lambda v: x0 + L + (xmax - v) / (xmax - xmin) * (pw - L - 12)          # purity 1.0 on the left
        py = lambda v: T + (1 - min(v, ymax) / ymax) * (H - T - B)
        out = [f'<text x="{x0 + pw/2:.1f}" y="16" class="lab" text-anchor="middle">{E(title)}</text>']
        for t in yticks:
            out.append(f'<line x1="{x0+L}" x2="{x0+pw-12}" y1="{py(t):.1f}" y2="{py(t):.1f}" class="grid"/><text x="{x0+L-6}" y="{py(t)+4:.1f}" class="tick" text-anchor="end">{t:g}</text>')
        for t in (1.0, 0.8, 0.6, 0.4):
            out.append(f'<text x="{px(t):.1f}" y="{H-B+16}" class="tick" text-anchor="middle">{t:g}</text>')
        out.append(f'<text x="{x0 + (L+pw-12)/2:.1f}" y="{H-8}" class="tick" text-anchor="middle">cluster purity (1.0 = perfect)</text>')
        out.append(f'<line x1="{px(0.7):.1f}" x2="{px(0.7):.1f}" y1="{T}" y2="{H-B}" class="limit"/><text x="{px(0.7)-4:.1f}" y="{T+12}" class="tick" text-anchor="end">purity 0.7</text>')
        if limit is not None:
            out.append(f'<line x1="{x0+L}" x2="{x0+pw-12}" y1="{py(limit):.1f}" y2="{py(limit):.1f}" class="limit"/><text x="{x0+pw-14}" y="{py(limit)-5:.1f}" class="tick" text-anchor="end">{E(limit_label)}</text>')
        for label, f, col in lines:
            pts = " ".join(f"{px(pu):.1f},{py(f(pu)):.1f}" for pu in [1.0 - i * 0.01 for i in range(71)])
            out.append(f'<polyline points="{pts}" fill="none" style="stroke:var({col})" stroke-width="2"/>')
            out.append(f'<text x="{px(0.45):.1f}" y="{py(f(0.45))-6:.1f}" class="tick" text-anchor="middle">{E(label)}</text>')
        for pt in points:
            out.append(f'<circle cx="{px(pt[0]):.1f}" cy="{py(valf(pt)):.1f}" r="4.5" class="dot" style="fill:var(--s1)" tabindex="0" '
                       f'{tip(f"spread {pt[3]}, seed {pt[4]}: purity {pt[0]:.2f}, {ylab} {valf(pt):.3f}")}/>')
        out.append(f'<line x1="{x0+L}" x2="{x0+pw-12}" y1="{H-B}" y2="{H-B}" class="axis"/>')
        return "".join(out)

    amax = max([p[1] for p in points] + [6]) * 1.15
    o.append(panel(0, "Rung-2 angle (degrees)", amax, [0, 5, 10, 20, 40, 80][:max(3, 1 + sum(1 for t in [5, 10, 20, 40, 80] if t < amax))], "angle",
                   lambda p: p[1], [], limit=5, limit_label="limit 5°"))
    amax2 = max([p[2] for p in points] + [bound_a21_rung1 * 2.5]) * 1.1
    step = 0.02 if amax2 < 0.15 else 0.05
    ticks = [round(i * step, 3) for i in range(int(amax2 / step) + 1)]
    o.append(panel(1, "Leakage ||A21|| at rung 2", amax2, ticks, "||A21||", lambda p: p[2],
                   [("bound", lambda pu: bound_a21_rung1 * (1 + 2 * (1 - pu)), "--s2"), ("bound (square-root form)", lambda pu: bound_a21_rung1 * math.sqrt(1 + 2 * (1 - pu)), "--s3")]))
    o.append("</svg>")
    return "".join(o)


def ladder(b1, b2, core_r2_b1, core_r2_b2, note=""):
    """P5: the nested subspaces with B1 and B2 angles side by side."""
    H = 250
    o = [_open(H, note)]
    bx = [60, 270, 480]
    names = [("Rung 1 variant", "texture"), ("Rung 2 variant", "identity"), ("Invariant core", "category")]
    labs = [f"angle B1 {b1[0]:.1f}°  B2 {b2[0]:.1f}°", f"angle B1 {b1[1]:.1f}°  B2 {b2[1]:.1f}°", f"R² B1 {core_r2_b1:.3f}  B2 {core_r2_b2:.3f}"]
    cols = ["--s1", "--s2", "--s3"]
    for i, x in enumerate(bx):
        o.append(f'<rect x="{x}" y="50" width="190" height="70" rx="4" style="fill:var({cols[i]});fill-opacity:.16;stroke:var({cols[i]})" stroke-width="2"/>'
                 f'<text x="{x+95}" y="78" class="val" text-anchor="middle">{names[i][0]}</text><text x="{x+95}" y="96" class="lab" text-anchor="middle">{names[i][1]} (4 directions)</text>'
                 f'<text x="{x+95}" y="114" class="tick" text-anchor="middle">{labs[i]}</text>')
    o.append(f'<line x1="270" x2="670" y1="150" y2="150" class="axis"/><text x="270" y="168" class="lab">kept by rung 1: 8 directions (identity + category)</text>'
             f'<line x1="480" x2="670" y1="190" y2="190" class="axis"/><text x="480" y="208" class="lab">kept by rung 2: 4 directions (category)</text>'
             f'<text x="60" y="30" class="lab">12 directions in all. Limit: every angle below 5°.</text></svg>')
    return "".join(o)
