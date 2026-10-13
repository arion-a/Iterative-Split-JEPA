"""Build the B2 report (docs/B2.md format) from results/B2/: REPORT.md (+ standalone figures) and the HTML page."""
import glob
import html
import json
import os
import statistics as st

import yaml

from isj import svgplots as sv
from isj.stage_b1 import seed_checks

E = html.escape
cfg = yaml.safe_load(open("configs/stage_b2_spec.yaml"))
crit = yaml.safe_load(open("configs/stage_b1.yaml"))["criteria"]
T = cfg["targets"]
runs = {}
for f in glob.glob("results/B2/sigma_cat_*/[0-9]*.json"):
    r = json.load(open(f)); runs.setdefault(r["sigma_cat"], {})[r["seed"]] = r
sigmas = sorted(runs)
clean = cfg["sweep"]["clean_sigma_cat"]
seeds = sorted(runs[clean]) if clean in runs else []
N_RUNS = sum(len(v) for v in runs.values())
fm = lambda v, nd=3: f"{v:.{nd}f}"


def ms(vals, nd=3):
    return f"{st.mean(vals):.{nd}f} ± {st.stdev(vals):.{nd}f}" if len(vals) > 1 else f"{vals[0]:.{nd}f}"


def as_b1(r, arm):
    """B1-shaped result so the frozen B1 gate function can judge any arm of a run."""
    a = r["arms"][arm]
    return {"rungs": [r["rung1"], a], "nesting_angle_deg": a["nesting_angle_deg"], "core_invariant_r2": a["core_invariant_r2"]}


def gates(r, arm):
    return seed_checks(as_b1(r, arm), crit)


GATE_ROWS = [("Rung 1 angle (texture)", "Angle between the recovered texture block and the true one", "below 5°", lambda r, a: r["rung1"]["angle_deg"], "rung1_angle", 2),
             ("Rung 2 angle (identity)", "Same, for the identity block recovered inside what rung 1 kept", "below 5°", lambda r, a: a["angle_deg"], "rung2_angle", 2),
             ("Texture R² (variant R², rung 1)", "How well the true texture can be read from its block", "above 0.9", lambda r, a: r["rung1"]["variant_r2"], "rung1_variant_r2", 3),
             ("Identity R² (variant R², rung 2)", "How well the true identity can be read from its block", "above 0.9", lambda r, a: a["variant_r2"], "rung2_variant_r2", 3),
             ("Category core R² (invariant R²)", "How well the true category can be read from the last 4 directions", "above 0.9", lambda r, a: a["core_invariant_r2"], "core_invariant_r2", 3),
             ("Nesting angle", "How far rung 2's block lies outside the true span of what rung 1 kept", "below 5°", lambda r, a: a["nesting_angle_deg"], "nesting", 2),
             ("Gap ratio, rung 1", "How sharply 'changes a lot' separates from 'barely changes'", "above 10", lambda r, a: r["rung1"]["gap_ratio"], "rung1_gap", 1),
             ("Gap ratio, rung 2", "Same at rung 2", "above 10", lambda r, a: a["gap_ratio"], "rung2_gap", 1),
             ("Leakage, largest |R²| (amended rule)", "Worst off-diagonal leakage at rung 1 or 2; B1's floor, decided after seeing B1 data", "below 0.01", lambda r, a: max(r["rung1"]["max_leak_abs_r2"], a["max_leak_abs_r2"]), "leakage", 4),
             ("Rank check", "Pair differences vary every variant direction (rung 1 and 2)", "passes", lambda r, a: float(not (r["rung1"]["rank_deficient"] or a["rank_deficient"])), "rank_test", 0)]


def gate_table(arm, sig):
    rs = [runs[sig][s] for s in sorted(runs[sig])]
    rows = []
    for label, plain, need, f, key, nd in GATE_ROWS:
        vals = [f(r, r["arms"][arm]) for r in rs]
        ok = all(gates(r, arm)[key] for r in rs)
        meas = f"{sum(vals):.0f} of {len(vals)} seeds pass" if key == "rank_test" else ms(vals, nd)
        rows.append([label, plain, need, meas, "yes" if ok else "**NO**"])
    return rows


def md_table(head, rows):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def html_table(head, rows, num_from=3):
    h = "".join(f"<th{' class=n' if i >= num_from else ''}>{E(str(c))}</th>" for i, c in enumerate(head))
    b = "".join("<tr>" + "".join(f"<td{' class=n' if i >= num_from else ''}>{E(str(c)).replace('**NO**', '<b>NO</b>')}</td>" for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="scroll"><table><tr>{h}</tr>{b}</table></div>'


# ------------------------------------------------------------------ tables (clean world unless stated)
tables = {}
if seeds:
    c0 = [runs[clean][s] for s in seeds]
    tables["A_b2"] = (["Criterion", "Plain meaning", "Threshold", f"B2 measured (mean ± std, {len(seeds)} seeds)", "Pass?"], gate_table("b2_kmeans", clean))
    tables["A_b1"] = (["Criterion", "Plain meaning", "Threshold", f"B1 on the same world and encoders (mean ± std)", "Pass?"], gate_table("b1_generator", clean))
    six = []
    for name, arm in (("B1 (generator twins)", "b1_generator"), ("B2 (discovered clusters)", "b2_kmeans")):
        rs = [r["arms"][arm] for r in c0]
        six.append([name, ms([a["global_r2"] for a in rs]), ms([a["invariant_r2"] for a in rs]), ms([a["variant_r2"] for a in rs]),
                    f"{ms([a['a12_fro'] for a in rs], 4)} ({ms([a['a12_norm'] for a in rs], 4)})", f"{ms([a['a21_fro'] for a in rs], 4)} ({ms([a['a21_norm'] for a in rs], 4)})",
                    ms([a["block_purity"] for a in rs], 5)])
    six.append(["Paper (single split, 8 numbers)", "0.9977 ± 0.0016", "0.9980 ± 0.0014", "0.9974 ± 0.0018", "0.0034 raw", "0.0233 raw", "about 0.99993"])
    tables["B"] = (["Rung 2 split", "Global R²", "Invariant R² (category core)", "Variant R² (identity)", "a12 raw (normalized)", "a21 raw (normalized)", "Block purity"], six)
    tables["C"] = (["Seed", "Cluster purity", "Pair validity", "Clusters found (true 6)", "Misgroup rate", "Pair distance in category space (B2 / perfect labels / random)"],
                   [[s, fm(runs[clean][s]["quality"]["cluster_purity"], 3), fm(runs[clean][s]["construction"]["b2_kmeans"]["pair_validity"], 3),
                     runs[clean][s]["quality"]["k_discovered"], fm(runs[clean][s]["quality"]["misgroup_rate"], 3),
                     f"{runs[clean][s]['construction']['b2_kmeans']['category_pair_distance']:.2f} / {runs[clean][s]['construction']['label_pairs']['category_pair_distance']:.2f} / n/a"] for s in seeds])
    hd = ["Metric"] + [f"seed {s}: B1 / B2 / Δ" for s in seeds]
    hl = []
    for label, f, nd in (("Rung-2 angle (°)", lambda r, a: a["angle_deg"], 2), ("Identity R²", lambda r, a: a["variant_r2"], 3),
                         ("Category core R²", lambda r, a: a["core_invariant_r2"], 3), ("Nesting angle (°)", lambda r, a: a["nesting_angle_deg"], 2),
                         ("Gap ratio, rung 2", lambda r, a: a["gap_ratio"], 1), ("a12 normalized", lambda r, a: a["a12_norm"], 4),
                         ("a21 normalized", lambda r, a: a["a21_norm"], 4), ("Block purity", lambda r, a: a["block_purity"], 5)):
        row = [label]
        for s in seeds:
            r = runs[clean][s]; b1, b2 = f(r, r["arms"]["b1_generator"]), f(r, r["arms"]["b2_kmeans"])
            row.append(f"{b1:.{nd}f} / {b2:.{nd}f} / {b2-b1:+.{nd}f}")
        hl.append(row)
    tables["D"] = (hd, hl)
    # targets
    t1 = [(s, runs[clean][s]["arms"]["b2_kmeans"]["angle_deg"], runs[clean][s]["arms"]["b1_generator"]["angle_deg"]) for s in seeds]
    t1_ok = all(b2 <= T["T1_construction_cost"]["max_ratio"] * b1 for _, b2, b1 in t1)
    t2_runs = [(sg, s, r) for sg in sigmas for s, r in runs[sg].items()
               if r["quality"]["cluster_purity"] >= T["T2_purity_threshold"]["purity_min"] and r["construction"]["b2_kmeans"]["pair_validity"] >= T["T2_purity_threshold"]["pair_validity_min"]]
    t2_pass = [all(gates(r, "b2_kmeans").values()) for _, _, r in t2_runs]
    t2_gate_fail = {}
    for (_, _, r) in t2_runs:
        for k, v in gates(r, "b2_kmeans").items():
            if not v: t2_gate_fail[k] = t2_gate_fail.get(k, 0) + 1
    pts = [(r["quality"]["cluster_purity"], r["arms"]["b2_kmeans"]["angle_deg"], r["arms"]["b2_kmeans"]["a21_fro"], sg, s) for sg in sigmas for s, r in runs[sg].items()]
    b_rung1 = st.mean(r["bound"]["a21_rung1"] for sg in sigmas for r in runs[sg].values())
    b_gen = st.mean(r["bound"]["a21_generator_rung2"] for sg in sigmas for r in runs[sg].values())
    under_norm = sum(p[2] <= b_rung1 * (1 + 2 * (1 - p[0])) for p in pts); under_sqrt = sum(p[2] <= b_rung1 * (1 + 2 * (1 - p[0])) ** 0.5 for p in pts)
    lim = T["T3_graceful_degradation"]["angle_limit_deg"]
    b1_angle = {(sg, s): r["arms"]["b1_generator"]["angle_deg"] for sg in sigmas for s, r in runs[sg].items()}
    cliff_abs = [p for p in pts if p[0] >= T["T3_graceful_degradation"]["purity_floor_for_no_cliff"] and p[1] > lim]
    # relative reading: above the limit AND more than twice what B1 gets on the same encoder (B1 itself can exceed the limit in this world)
    cliff = [p for p in pts if p[0] >= T["T3_graceful_degradation"]["purity_floor_for_no_cliff"] and p[1] > max(lim, 2 * b1_angle[(p[3], p[4])])]
    by_sig = []
    for sg in sigmas:
        rs = list(runs[sg].values())
        by_sig.append([sg, ms([r["quality"]["cluster_purity"] for r in rs], 2), ms([r["quality"]["misgroup_rate"] for r in rs], 2),
                       ms([r["arms"]["b1_generator"]["angle_deg"] for r in rs], 1), ms([r["arms"]["b2_kmeans"]["angle_deg"] for r in rs], 1),
                       ms([r["arms"]["b2_kmeans"]["a21_fro"] for r in rs], 4), f"{b_rung1 * (1 + 2 * st.mean(r['quality']['misgroup_rate'] for r in rs)):.4f}",
                       f"{sum(all(gates(r, 'b2_kmeans').values()) for r in rs)} of {len(rs)}"])
    tables["T3"] = (["Spread σ_cat", "Purity", "Misgroup rate", "Rung-2 angle B1 (°)", "Rung-2 angle B2 (°)", "||A21|| B2", "Bound on ||A21||", "Runs passing all gates"], by_sig)
    ctl = []
    cr = [runs[clean][s] for s in seeds]
    mean_a = lambda arm: st.mean(r["arms"][arm]["angle_deg"] for r in cr)
    ctl_ok = {"C1": mean_a("c1_cross_cluster") > T["T4_loud_failure"]["C1_cross_cluster"]["angle_min_deg"] and st.mean(r["construction"]["c1_cross_cluster"]["pair_validity"] for r in cr) < 0.95,
              "C2": mean_a("c2_variant_clusters") > T["T4_loud_failure"]["C2_variant_clusters"]["angle_min_deg"],
              "C3": all(r["construction"]["c3_singleton"]["n_pairs"] == 0 for r in cr)}
    ctl = [["C1 cross-cluster pairs", "angle above 10° and pair validity below 0.95", f"angle {mean_a('c1_cross_cluster'):.1f}°, validity {st.mean(r['construction']['c1_cross_cluster']['pair_validity'] for r in cr):.3f}", "failed as required" if ctl_ok["C1"] else "DID NOT FAIL"],
           ["C2 clusters from the variant block", "angle above 10°", f"angle {mean_a('c2_variant_clusters'):.1f}°, cluster purity vs true category {st.mean(r['quality']['variant_cluster_purity'] for r in cr):.2f}", "failed as required" if ctl_ok["C2"] else "DID NOT FAIL"],
           ["C3 singleton clusters", "no valid pairs, so the rank check fires", f"{st.mean(r['construction']['c3_singleton']['n_pairs'] for r in cr):.0f} pairs", "failed as required" if ctl_ok["C3"] else "DID NOT FAIL"],
           ["C4 shuffled membership (recorded)", "no required outcome", f"angle {mean_a('c4_shuffled'):.1f}°, validity {st.mean(r['construction']['c4_shuffled']['pair_validity'] for r in cr):.2f}", "recorded"]]
    tables["controls"] = (["Control", "Required outcome", "Observed (clean world)", "Result"], ctl)
    gate_pass_clean = all(all(gates(r, "b2_kmeans").values()) for r in cr)
    deltas = {k: st.mean(f(r["arms"]["b2_kmeans"]) - f(r["arms"]["b1_generator"]) for r in cr) for k, f in
              {"rung-2 angle (°)": lambda a: a["angle_deg"], "identity R²": lambda a: a["variant_r2"], "category core R²": lambda a: a["core_invariant_r2"]}.items()}
    purity_clean = st.mean(r["quality"]["cluster_purity"] for r in cr)
    b1_gate_pass_clean = all(all(gates(r, "b1_generator").values()) for r in cr)
    if gate_pass_clean and t1_ok and all(ctl_ok.values()):
        vflag = "PASSED"
    elif (not b1_gate_pass_clean) and t1_ok and all(ctl_ok.values()):
        vflag = "MATCHES B1, BUT THE GATES ARE NOT MET IN THIS WORLD (B1 misses them too)"
    else:
        vflag = "FAILED"
    plural = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"
    t2_state = "could not be tested (no run reached purity 0.9 and pair validity 0.95 with the discovered cluster count)" if not t2_runs else ("met" if all(t2_pass) else "not met")
    t3_met = (not cliff) and under_norm == len(pts)
    verdict = (f"B2 {vflag} (clean world, {len(seeds)} seeds). Construction cost against B1: rung-2 angle {deltas['rung-2 angle (°)']:+.2f}°, identity R² {deltas['identity R²']:+.3f}, "
               f"category core R² {deltas['category core R²']:+.3f}; cluster purity {purity_clean:.2f}. "
               f"T1 {'met' if t1_ok else 'not met'}; T2 {t2_state}; "
               f"T3 {'met' if t3_met else 'not met'}: leakage ||A21|| was {'under' if under_norm == len(pts) else 'over'} the contamination bound in {plural(len(pts) - under_norm if under_norm != len(pts) else under_norm, 'run')} of {len(pts)} and "
               f"{'there was no cliff above purity 0.7' if not cliff else 'a cliff appears above purity 0.7 in ' + plural(len(cliff), 'run')} (measured against B1); "
               f"T4 {'met' if all(ctl_ok.values()) else 'not met'} (controls C1-C3 {'failed as required' if all(ctl_ok.values()) else 'did not all fail'}). "
               f"Gates: B2 {'passes them all' if gate_pass_clean else 'misses some (table A)'}; B1 on the same encoders {'passes them all' if b1_gate_pass_clean else 'also misses some, so the shortfall comes from the world and encoder, not from building the pairs'}.")
    tgt = [["T1 construction cost: B2 angle within 2x of B1, per seed", "; ".join(f"seed {s}: {b2:.2f}° vs {b1:.2f}° (ratio {b2/b1:.2f})" for s, b2, b1 in t1), "met" if t1_ok else "NOT met"],
           ["T2 purity ≥ 0.9 and pair validity ≥ 0.95 imply all gates pass", f"{len(t2_runs)} runs qualify; {sum(t2_pass)} pass every gate" + (f"; gates failing: {t2_gate_fail}" if t2_gate_fail else ""), "met" if t2_runs and all(t2_pass) else ("no qualifying run" if not t2_runs else "NOT met")],
           ["T3 smooth degradation, no cliff above purity 0.7, leakage under the bound", f"{len(cliff_abs)} runs above purity 0.7 have angle > 5° (absolute), {len(cliff)} are also more than twice B1's angle (relative); ||A21|| under the bound in {under_norm} of {len(pts)} runs (square-root form: {under_sqrt})", "met" if not cliff and under_norm == len(pts) else "see figure P8"],
           ["T4 controls C1-C3 fail as required", ", ".join(f"{k} {'yes' if v else 'NO'}" for k, v in ctl_ok.items()), "met" if all(ctl_ok.values()) else "NOT met"]]
    tables["targets"] = (["Target", "Observed", "Result"], tgt)

# ------------------------------------------------------------------ figures
figs = {}
if seeds:
    e_b1 = [st.mean(runs[clean][s]["arms"]["b1_generator"]["eigvals"][i] for s in seeds) for i in range(8)]
    e_b2 = [st.mean(runs[clean][s]["arms"]["b2_kmeans"]["eigvals"][i] for s in seeds) for i in range(8)]
    figs["P2prime"] = sv.log_lines([("B1 (generator twins)", e_b1, "--s1"), ("B2 (discovered clusters)", e_b2, "--s2")], vline=4, vline_label="selected boundary: 4 | 4",
                                   ymin=1e-3, ymax=10, note="Pair-difference spectrum at rung 2, B1 against B2",
                                   annotations=[(5, f"B1 gap ratio {e_b1[3]/e_b1[4]:.0f}", e_b1[4] * 0.32), (5, f"B2 gap ratio {e_b2[3]/e_b2[4]:.1f}", e_b2[4] * 2.6)])
    r0 = runs[clean][seeds[0]]; p7 = r0["p7"]
    figs["P7"] = sv.scatter_pair(p7["x"], p7["y"], p7["true_cat"], p7["cluster"], note="Rung-1 invariant content, coloured by true category and by cluster")
    figs["P8"] = sv.degradation(pts, b_rung1, b_gen, note="Rung-2 angle and leakage against cluster purity")
    a1 = [st.mean(runs[clean][s]["rung1"]["angle_deg"] for s in seeds), st.mean(runs[clean][s]["arms"]["b1_generator"]["angle_deg"] for s in seeds)]
    a2 = [st.mean(runs[clean][s]["rung1"]["angle_deg"] for s in seeds), st.mean(runs[clean][s]["arms"]["b2_kmeans"]["angle_deg"] for s in seeds)]
    figs["P5"] = sv.ladder(a1, a2, st.mean(runs[clean][s]["arms"]["b1_generator"]["core_invariant_r2"] for s in seeds),
                           st.mean(runs[clean][s]["arms"]["b2_kmeans"]["core_invariant_r2"] for s in seeds), note="Ladder with B1 and B2 angles")

# ------------------------------------------------------------------ REPORT.md
os.makedirs("results/B2/figures", exist_ok=True)
for k, v in figs.items():
    open(f"results/B2/figures/{k}.svg", "w").write(sv.standalone(v))
CAP = {"P2prime": "P2′. Pair-difference spectrum at rung 2 (log scale): B1 against B2, mean over seeds, clean world.",
       "P7": "P7. Rung-1 invariant content projected to 2-D (seed 0, clean world). Left: true category. Right: discovered cluster, coloured to match its best-overlapping category. The projection uses the true categories, so it is for the picture only.",
       "P8": "P8. Degradation: rung-2 angle and ||A21|| against cluster purity, every run of the sweep. Lines: the contamination bound from the monograph, drawn two ways.",
       "P5": "P5. The ladder: nested blocks with B1 and B2 angles side by side (mean, clean world)."}
if seeds:
    md = [f"# B2 report (docs/B2.md format)\n", f"**Verdict.** {verdict}\n",
          f"Runs: {N_RUNS} (spread values {sigmas}, seeds {sorted({s for v in runs.values() for s in v})}). Spec: `docs/B2.md`. Clean world: spread {clean}. B1 here means the generator twins on the same encoder and seed. Gates are B1's frozen criteria, including B1's leakage floor that was decided after seeing B1 data.\n",
          "## A. Gate table (B2, clean world)\n", md_table(*tables["A_b2"]), "\nFor reference, B1 on the same world and encoders:\n", md_table(*tables["A_b1"]),
          "\n## B. Paper-standard metrics (rung-2 split; leakage raw, normalized by √block size in brackets)\n", md_table(*tables["B"]),
          "\n## C. Construction quality (clean world)\n", md_table(*tables["C"]),
          "\n## D. Headline: what did construction cost us? (B1 / B2 / Δ per seed, clean world)\n", md_table(*tables["D"]),
          "\n## Targets\n", md_table(*tables["targets"]), "\n### Degradation across the spread sweep (all runs)\n", md_table(*tables["T3"]),
          "\n## Controls\n", md_table(*tables["controls"]), "\n## Figures\n"]
    for k in ("P2prime", "P7", "P8", "P5"):
        md += [f"![{k}](figures/{k}.svg)\n", f"*{CAP[k]}*\n"]
    md.append("\nWhat success does and does not establish (from the spec): the pipeline is viable without ground truth on synthetic worlds, at a measurable cost relative to B1. It does not establish real-world viability.\n")
    open("results/B2/REPORT.md", "w").write("\n".join(md))

# ------------------------------------------------------------------ HTML page
TIP_JS = """<div id="tip"></div>
<script>
(function(){var t=document.getElementById('tip');
function show(e){var s=e.target.getAttribute&&e.target.getAttribute('data-tip');if(!s)return;t.textContent=s;t.style.opacity=1;move(e)}
function move(e){var x=e.clientX||0,y=e.clientY||0;if(e.type==='focusin'){var r=e.target.getBoundingClientRect();x=r.left+r.width/2;y=r.top}
t.style.left=Math.min(x+12,window.innerWidth-270)+'px';t.style.top=(y-34)+'px'}
function hide(){t.style.opacity=0}
document.addEventListener('pointerover',show);document.addEventListener('pointermove',function(e){if(t.style.opacity==1)move(e)});
document.addEventListener('pointerout',hide);document.addEventListener('focusin',function(e){show(e);move(e)});document.addEventListener('focusout',hide)})();
</script>"""
CSS = open("experiments/build_b1_report.py").read().split('CSS = """')[1].split('"""')[0]
CSS += ".key2{font-size:.85rem;color:var(--ink2)}.verdict{background:var(--surf);border:1px solid var(--line);border-left:4px solid var(--s1);border-radius:6px;padding:12px 16px;margin:14px 0;max-width:80ch}"
CSS = CSS.replace("--s3:#1baf7a;", "--s3:#1baf7a;--s4:#eda100;--s5:#e87ba4;--s6:#008300;").replace("--s3:#199e70;", "--s3:#199e70;--s4:#c98500;--s5:#d55181;--s6:#008300;")
if seeds:
    sec = lambda t, body: f"<h2>{E(t)}</h2>{body}"
    fig = lambda k: f'<div class="card"><p class="sub">{E(CAP[k])}</p><div class="cscroll">{figs[k]}</div></div>'
    page = (f"<title>Stage B2 Results</title>\n<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\"><link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>"
            f"<link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&display=swap\"><style>{CSS}</style><div class=\"wrap\">"
            f"<h1>Stage B2: can the second split's pairs be built from the data?</h1><div class=\"verdict\"><b>Verdict.</b> {E(verdict)}</div>"
            f"<p class=\"sub\">{N_RUNS} runs: within-category spread {E(str(sigmas))}, seeds {E(str(sorted({s for v in runs.values() for s in v})))}. The clean world is spread {clean}. “B1” means the generator's own twin pairs on the same encoder and seed. Gates are B1's frozen criteria, including B1's leakage floor that was decided after seeing B1 data. Spec: docs/B2.md.</p>"
            + sec("A. Gate table (B2, clean world)", html_table(*tables["A_b2"], num_from=3)) + "<p class=\"sub\">B1 on the same world and encoders, for reference:</p>" + html_table(*tables["A_b1"], num_from=3)
            + sec("B. The paper's six metrics (rung-2 split)", html_table(*tables["B"], num_from=1) + "<p class=\"sub\">Leakage is shown raw, with the value normalized by the square root of the block size in brackets. The paper's numbers are for one split in an 8-number world.</p>")
            + sec("C. Construction quality (clean world)", html_table(*tables["C"], num_from=1))
            + sec("D. Headline: what did construction cost us?", html_table(*tables["D"], num_from=1) + "<p class=\"sub\">Each cell: B1 / B2 / difference (B2 minus B1).</p>")
            + sec("Targets", html_table(*tables["targets"], num_from=9)) + sec("Degradation across the spread sweep", html_table(*tables["T3"], num_from=1))
            + sec("Controls", html_table(*tables["controls"], num_from=9))
            + sec("Figures", fig("P2prime") + fig("P7") + fig("P8") + fig("P5"))
            + "<p class=\"sub\">What success establishes (from the spec): the pipeline is viable without ground truth on synthetic worlds, at a measurable cost relative to B1. It does not establish real-world viability.</p></div>"
            + TIP_JS)
    open("docs/b2_results.html", "w").write(page)
print("report built from", N_RUNS, "runs; clean-world seeds:", seeds)
