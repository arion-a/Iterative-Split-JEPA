"""Verdicts for E68 and E71 (rules registered in docs/EVIDENCE.md, 'Owner instruction 2026-11-18' and its later entry). Every failed line states observed, required and the gap.
    python experiments/analyse_e68_e71.py ROOT       # ROOT holds results/nested/{e68,e71}/...   -> ROOT/REPORT_E68_E71.md"""
import glob, json, os, sys
PRES, LEAK, HEALTH, RES = 0.9, 0.1, 0.5, 0.05           # slice-clean thresholds (registered)
ANG, GAP, LPRES = 5.0, 10.0, 0.95                        # ladder-clean thresholds (E55 rule)
STORED_E55 = {"C": {1: 0, 2: 0, 4: 0, 8: 0}, "D": {1: 5, 2: 0, 4: 0, 8: 0}}   # ladder-clean seeds of 5, stored (E55)
def load(folder): return sorted((json.load(open(f)) for f in glob.glob(f"{folder}/main_seed*.json")), key=lambda r: r["seed"])
def slice_clean(r):
    s = r["slice"]; return all(p >= PRES for p in s["presence"]) and all(l <= LEAK for l in s["leakage_faster"]) and r["output_cov_min_eig"] >= HEALTH
def ladder_clean(r): return all(g["angle_deg"] < ANG and g["gap_ratio"] > GAP for g in r["rungs"]) and all(p >= LPRES for p in r["presence"]["mlp"])
def slice_dev(r):
    """deviation from the standard for a seed that fails slice-clean (empty string if it passes)"""
    s = r["slice"]; out = []
    lo = min(s["presence"]); hi = max(s["leakage_faster"]) if s["leakage_faster"] else 0.0
    if lo < PRES: out.append(f"min presence {lo:.3f} < {PRES} (short by {PRES - lo:.3f}, slice {s['presence'].index(lo) + 1})")
    if hi > LEAK: out.append(f"max leakage {hi:.3f} > {LEAK} (over by {hi - LEAK:.3f})")
    if r["output_cov_min_eig"] < HEALTH: out.append(f"health {r['output_cov_min_eig']:.3f} < {HEALTH} (short by {HEALTH - r['output_cov_min_eig']:.3f})")
    return "; ".join(out)
def rung_clean(r, k):
    """E71: rung k (1-based, k <= K-1) clean if presence_k >= 0.9, leakage_k <= 0.1 (k >= 2) and residual_k <= 0.05; returns (ok, deviation text)"""
    s = r["slice"]; dev = []
    if s["presence"][k - 1] < PRES: dev.append(f"presence {s['presence'][k - 1]:.3f} < {PRES} (short {PRES - s['presence'][k - 1]:.3f})")
    if k >= 2 and s["leakage_faster"][k - 2] > LEAK: dev.append(f"leakage {s['leakage_faster'][k - 2]:.3f} > {LEAK} (over {s['leakage_faster'][k - 2] - LEAK:.3f})")
    if s["invariance_residual"][k - 1] > RES: dev.append(f"residual {s['invariance_residual'][k - 1]:.3f} > {RES} (over {s['invariance_residual'][k - 1] - RES:.3f})")
    return not dev, "; ".join(dev)
def all_rungs_clean(r): return r["output_cov_min_eig"] >= HEALTH and all(rung_clean(r, k)[0] for k in range(1, len(r["slice"]["presence"])))
def w_status(root, exp, K, s):
    p = f"{root}/results/nested/{exp}/W_K{K}_s{s:g}.json"; return json.load(open(p))["W"] if os.path.exists(p) else "missing"
def e68(root):
    md, res, S = ["## E68 (nested loss in the hard world)", ""], {}, (1, 2, 4, 8)
    md += ["| Strength | W | A slice-clean | B slice-clean | A ladder-clean | B ladder-clean | C (stored, ladder) | D (stored, ladder) |", "|---|---|---|---|---|---|---|---|"]
    for s in S:
        R = {a: load(f"{root}/results/nested/e68/{a}/s{s:g}") for a in "AB"}
        res[s] = {a: (sum(slice_clean(r) for r in R[a]), len(R[a])) for a in "AB"}
        md.append(f"| {s} | {w_status(root, 'e68', 4, s)} | {res[s]['A'][0]} of {res[s]['A'][1]} | {res[s]['B'][0]} of {res[s]['B'][1]} | {sum(ladder_clean(r) for r in R['A'])} of {len(R['A'])} | {sum(ladder_clean(r) for r in R['B'])} of {len(R['B'])} | {STORED_E55['C'][s]} of 5 | {STORED_E55['D'][s]} of 5 |")
    complete = all(res[s][a][1] >= 5 for s in S for a in "AB")
    a_ = res[1]["A"][0]; b_ = max(res[4]["A"][0], res[4]["B"][0]); c_ = sum(res[s]["B"][0] - res[s]["A"][0] for s in (2, 4, 8))
    la = "met" if a_ >= 4 else f"NOT met: arm A slice-clean on {a_} of 5 at strength 1, required 4, short by {4 - a_} seed(s)"
    lb = "met" if b_ >= 3 else f"NOT met: better of A and B slice-clean on {b_} of 5 at strength 4, required 3, short by {3 - b_} seed(s)"
    lc = "met" if c_ >= 2 else f"NOT met: B minus A summed over strengths 2, 4, 8 is {c_}, required 2, short by {2 - c_}"
    verdict = "INCOMPLETE" if not complete else ("CONFIRMED" if (a_ >= 4 and b_ >= 3) else "REFUTED")
    md += ["", f"**E68 verdict (nested loss works where the paper objective does not): {verdict}.** (a) {la}. (b) {lb}. (c, separate verdict: curriculum helps) {lc}.", "", "Deviations of failing seeds (slice-clean rule):"]
    for s in S:
        for a in "AB":
            for r in load(f"{root}/results/nested/e68/{a}/s{s:g}"):
                if not slice_clean(r): md.append(f"- strength {s}, arm {a}, seed {r['seed']}: {slice_dev(r)}")
    return md, verdict, b_ >= 3, s9(res)
def s9(res):
    ok = [s for s in (2, 4, 8) if max(res[s]["A"][0], res[s]["B"][0]) >= 3]; return max(ok) if ok else None
def e71(root):
    md = ["## E71 (depth of the nested loss)", ""]; out = {}
    for tag, strength in (("E71a (mild, strength 0.5)", 0.5),):
        md += [f"### {tag}", "", "| K (rungs) | W | A all-rungs-clean | mean clean-rung fraction | U ladder-clean |", "|---|---|---|---|---|"]
        for K in (11, 13, 16):
            A = load(f"{root}/results/nested/e71/A/K{K}_s{strength:g}"); U = load(f"{root}/results/nested/e71/U/K{K}_s{strength:g}")
            frac = [sum(rung_clean(r, k)[0] for k in range(1, K)) / (K - 1) for r in A]
            out[K] = (sum(all_rungs_clean(r) for r in A), len(A), (sum(frac) / len(frac)) if frac else float("nan"))
            md.append(f"| {K} ({K - 1}) | {w_status(root, 'e71', K, strength)} | {out[K][0]} of {out[K][1]} | {out[K][2]:.3f} | {sum(ladder_clean(r) for r in U)} of {len(U)} |")
        complete = all(out[K][1] >= 5 for K in (11, 13, 16))
        fa = [K for K in (11, 13, 16) if out[K][0] < 3]; fb = out[16][2]
        la = "met" if not fa else "NOT met: " + "; ".join(f"K={K}: all-rungs-clean on {out[K][0]} of 5, required 3, short by {3 - out[K][0]}" for K in fa)
        lb = "met" if fb >= 0.9 else f"NOT met: clean-rung fraction at K=16 is {fb:.3f}, required 0.9, short by {0.9 - fb:.3f}"
        verdict = "INCOMPLETE" if not complete else ("CONFIRMED" if (not fa and fb >= 0.9) else "REFUTED")
        md += ["", f"**E71a verdict: {verdict}.** (a) {la}. (b) {lb}.", "", "Per-rung table (mean over seeds; clean fraction = share of seeds in which the rung is clean):", "", "| K | rung | clean fraction | mean presence | mean leakage | mean residual | typical deviation of failing seeds |", "|---|---|---|---|---|---|---|"]
        for K in (11, 13, 16):
            A = load(f"{root}/results/nested/e71/A/K{K}_s{strength:g}")
            for k in range(1, K):
                oks = [rung_clean(r, k) for r in A]; devs = [d for ok, d in oks if not ok]
                n = max(len(A), 1); pres = sum(r["slice"]["presence"][k - 1] for r in A) / n; res_ = sum(r["slice"]["invariance_residual"][k - 1] for r in A) / n
                leak = (sum(r["slice"]["leakage_faster"][k - 2] for r in A) / n) if k >= 2 else float("nan")
                md.append(f"| {K} | {k} | {sum(ok for ok, _ in oks)}/{len(A)} | {pres:.3f} | {leak:.3f} | {res_:.3f} | {devs[0] if devs else ''} |")
    return md, verdict
if __name__ == "__main__":
    root = sys.argv[1]; m1, v1, b_ok, s9v = e68(root); m2, v2 = e71(root)
    report = "\n".join(["# E68 / E71 report (generated by experiments/analyse_e68_e71.py)", ""] + m1 + ["", f"s9 (E68 rule) = {s9v}; E71b runs only if E68 (b) holds: {b_ok}", ""] + m2)
    open(f"{root}/REPORT_E68_E71.md", "w").write(report + "\n"); print(report)
