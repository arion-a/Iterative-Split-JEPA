"""Render the plain-language experiment log page from the hash-chained log.

    python experiments/build_log_page.py [--out explog/log_page.html]

Rows come from chain entries that carry a `plain` block, so every row on the page is covered by
the chain's fingerprints. Edit stage status in explog/stages.json at the end of each stage.
"""
import argparse
import datetime as dt
import html
import json

from isj import explog as L

CSS = """
:root{--bg:#f6f7f9;--surface:#fff;--fg:#1c2330;--muted:#5d6676;--line:#dde1e8;--accent:#1f5fbf;--accent-soft:#e6eefb;
--pass:#13703b;--pass-bg:#e1f3e8;--fail:#b3261e;--fail-bg:#fbe5e3;--info:#4a5568;--info-bg:#e9ecf1;--wait:#8a5a00;--wait-bg:#fbefd2;
--sans:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#10141b;--surface:#171c26;--fg:#e6e9ef;--muted:#9aa4b5;--line:#2a3140;--accent:#7fb0ff;--accent-soft:#1c2a45;
--pass:#6fd397;--pass-bg:#15301f;--fail:#ff8f87;--fail-bg:#3a1b19;--info:#b4bccb;--info-bg:#232a37;--wait:#f0c15a;--wait-bg:#3a2d10;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#10141b;--surface:#171c26;--fg:#e6e9ef;--muted:#9aa4b5;--line:#2a3140;--accent:#7fb0ff;--accent-soft:#1c2a45;
--pass:#6fd397;--pass-bg:#15301f;--fail:#ff8f87;--fail-bg:#3a1b19;--info:#b4bccb;--info-bg:#232a37;--wait:#f0c15a;--wait-bg:#3a2d10;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font:15px/1.55 var(--sans)}
.wrap{max-width:1180px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:1.7rem;margin:0 0 4px;letter-spacing:-.01em;text-wrap:balance}
h2{font-size:1.05rem;margin:32px 0 10px;text-wrap:balance}
.sub{color:var(--muted);margin:0 0 4px}
.meta{font:12.5px var(--mono);color:var(--muted)}
.stages{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px;margin-top:18px}
.stage{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:12px 14px;min-width:0}
.stage .tag{font:600 11px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.stage h3{font-size:.98rem;margin:3px 0 4px}
.stage p{margin:0 0 6px;font-size:.88rem;color:var(--muted)}
.stage.done{border-color:var(--pass)}.stage.next{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent) inset}
.chip{display:inline-block;font:600 11px var(--mono);letter-spacing:.04em;text-transform:uppercase;padding:2px 8px;border-radius:99px;white-space:nowrap}
.chip.pass,.chip.done{background:var(--pass-bg);color:var(--pass)}.chip.fail{background:var(--fail-bg);color:var(--fail)}
.chip.info,.chip.later{background:var(--info-bg);color:var(--info)}.chip.blocked{background:var(--wait-bg);color:var(--wait)}
.chip.next{background:var(--accent-soft);color:var(--accent)}
.scroll{overflow-x:auto}
table.cmp{border-collapse:collapse;width:100%;font-size:.9rem;background:var(--surface);border:1px solid var(--line)}
table.cmp th,table.cmp td{padding:7px 12px;border-bottom:1px solid var(--line);text-align:left;font-variant-numeric:tabular-nums}
table.cmp th{font-size:.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
td.n,th.n{text-align:right}.mono{font-family:var(--mono)}
.bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:26px 0 8px}
.bar h2{margin:0;flex:1}
button{font:inherit;font-size:.85rem;color:var(--accent);background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:5px 12px;cursor:pointer}
button:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.log{background:var(--surface);border:1px solid var(--line);border-radius:6px}
.head,.row{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.35fr) minmax(0,1fr);gap:0}
.head>div{padding:9px 14px;font:600 12px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--line);background:var(--bg)}
.row>div{padding:14px;border-bottom:1px solid var(--line);min-width:0}
.row:last-child>div{border-bottom:0}
.row .t{font-weight:600;margin:0 0 4px}
.row .ref{font:12px var(--mono);color:var(--muted);margin-top:8px}
.row ul{margin:6px 0 0;padding-left:18px}.row li{margin:2px 0}
.row .lbl{display:none;font:600 11px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:4px}
.row:target>div{background:var(--accent-soft)}
details{margin-top:28px;background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:10px 14px}
summary{cursor:pointer;font-weight:600}
dl{display:grid;grid-template-columns:max-content minmax(0,1fr);gap:6px 16px;margin:12px 0 0}
dt{font-family:var(--mono);font-size:.85rem}dd{margin:0;color:var(--muted)}
.foot{margin-top:28px;font:12px/1.6 var(--mono);color:var(--muted);overflow-wrap:anywhere}
@media (max-width:760px){.head{display:none}.row{display:block;border-bottom:1px solid var(--line)}.row:last-child{border-bottom:0}
.row>div{border-bottom:0;padding:8px 14px}.row .lbl{display:block}}
"""

PAPER = [  # (paper metric, plain meaning, paper's value)
    ("invariant_r2", "How well the true invariant numbers can be read back from the invariant block (1 = perfectly).", "about 0.998"),
    ("variant_r2", "Same, for the variant block.", "about 0.997"),
    ("global_r2", "How well the whole representation is explained by the true hidden numbers.", "about 0.998"),
    ("a12_fro / a21_fro", "Cross-block leakage: how much the invariant block depends on the variant numbers, and the reverse. Smaller is better.", "0.003 / 0.024"),
    ("block_purity", "Share of the learned map that stays inside the right blocks (1 = no mixing).", "about 0.99993"),
]
EXTRA = [
    ("angle", "Plan metric. How far the learned invariant direction is from the true one (0 degrees = exact)."),
    ("gap ratio", "Plan metric. How sharply 'changes a lot' separates from 'barely changes' in the matched-pair spectrum. About 1 = no split; above 10 = clean."),
    ("seed", "One repeat with different random numbers. 5 seeds means it is not luck."),
    ("control", "A run that is supposed to fail, to prove a pass means something."),
]
CHIP = {"pass": "Pass", "fail": "Failed", "info": "Note", "blocked": "Waiting on you"}


def esc(s):
    return html.escape(str(s), quote=True)


def build() -> str:
    entries = [e for e in L.read_all() if "plain" in e]
    ok, msg = L.verify(check_artifacts=False)
    allentries = L.read_all()
    stages = json.load(open("explog/stages.json"))["stages"]
    now = dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y, %H:%M UTC")

    stage_html = "".join(
        f'<div class="stage {s["status"]}"><div class="tag">Stage {esc(s["id"])}</div><h3>{esc(s["name"])}</h3>'
        f'<p>{esc(s["question"])}</p><p>{esc(s["result"])}</p>'
        f'<span class="chip {s["status"]}">{ {"done": "Done", "next": "Up next", "later": "Later"}[s["status"]] }</span></div>'
        for s in stages)

    rows = []
    for i, e in enumerate(entries, 1):
        p = e["plain"]
        outs = p["output"] if isinstance(p["output"], list) else [p["output"]]
        li = "".join(f"<li>{esc(o)}</li>" for o in outs)
        chip = f'<span class="chip {p.get("verdict", "info")}">{CHIP.get(p.get("verdict", "info"), "Note")}</span>'
        when = (e.get("event_time") or e["recorded_at"])[:10]
        rows.append(
            f'<div class="row" id="r{i}" data-i="{i}">'
            f'<div><div class="lbl">What I did</div><p class="t">{esc(p.get("title", ""))}</p><div>{esc(p["did"])}</div>'
            f'<div class="ref">Step {i} · Stage {esc(p.get("stage", "-"))} · {esc(when)}</div></div>'
            f'<div><div class="lbl">What came out</div>{chip}<ul>{li}</ul></div>'
            f'<div><div class="lbl">Why it matters for the whole experiment</div>{esc(p["relevance"])}'
            f'<div class="ref">record #{e["index"]} · {esc(e["hash"][:10])}</div></div></div>')

    paper_rows = "".join(f"<dt>{esc(a)}</dt><dd>{esc(b)} <span class='mono'>Paper: {esc(c)}</span></dd>" for a, b, c in PAPER)
    extra_rows = "".join(f"<dt>{esc(a)}</dt><dd>{esc(b)}</dd>" for a, b in EXTRA)
    head = allentries[-1]["hash"][:12] if allentries else "-"

    return f"""<title>Iterative SplitJEPA Log</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>{CSS}</style>
<div class="wrap">
<h1>Iterative SplitJEPA experiment log</h1>
<p class="sub">What was done, what came out, and why it matters for the whole experiment. Newest step first.</p>
<p class="meta">Updated {esc(now)} · {len(entries)} steps shown · record {'intact' if ok else 'BROKEN'} ({len(allentries)} entries)</p>
<div class="stages">{stage_html}</div>
<div class="bar"><h2>Log</h2><button id="flip" type="button" aria-pressed="false">Show oldest first</button></div>
<div class="log" id="log"><div class="head"><div>What I did</div><div>What came out</div><div>Why it matters for the whole experiment</div></div>
{''.join(reversed(rows))}</div>
<details><summary>What the numbers mean (using the paper's names)</summary><dl>{paper_rows}{extra_rows}</dl></details>
<p class="foot">Each step is a hash-chained entry in explog/chain.jsonl; the step's fingerprint is shown beside it. Changing any past entry breaks every later fingerprint (checked: {esc(msg)}). Latest fingerprint: {esc(head)}. Steps marked with an earlier date were written up afterwards from the saved files and git history.</p>
</div>
<script>
(function(){{var log=document.getElementById('log'),btn=document.getElementById('flip'),newest=true;
btn.addEventListener('click',function(){{var rows=[].slice.call(log.querySelectorAll('.row'));rows.reverse().forEach(function(r){{log.appendChild(r)}});
newest=!newest;btn.textContent=newest?'Show oldest first':'Show newest first';btn.setAttribute('aria-pressed',String(!newest))}});}})();
</script>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="explog/log_page.html")
    a = ap.parse_args()
    open(a.out, "w", encoding="utf-8").write(build())
    print("wrote", a.out)
