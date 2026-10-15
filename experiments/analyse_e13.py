"""E13 analysis (protocol fixed in docs/EVIDENCE.md before the run): contamination-model fit, purified-above-curve, rho-hat, blind E14, Tier 4 comparability.
    python experiments/analyse_e13.py results/stage_b2_gapfix_sweep    -> <dir>/E13_REPORT.md and <dir>/figures/E13_gap_vs_contamination.svg"""
import glob, json, math, os, statistics as st, sys
import torch
from isj.audits import principal_angles_deg

D = sys.argv[1] if len(sys.argv) > 1 else "results/stage_b2_gapfix_sweep"
runs = sorted((json.load(open(f)) for f in glob.glob(f"{D}/sigma_cat_*/[0-9]*.json")), key=lambda r: (r["sigma_cat"], r["seed"]))
n = len(runs)
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
A = lambda r, arm, k: r["arms"][arm][k]
rho = [1 - r["construction"]["b2_kmeans"]["pair_validity"] for r in runs]
lam4 = [A(r, "b1_generator", "eigvals")[3] for r in runs]; lam5 = [A(r, "b1_generator", "eigvals")[4] for r in runs]
gap_u = [A(r, "b2_kmeans", "gap_ratio") for r in runs]; gap_t1 = [A(r, "b2_kmeans_purified", "gap_ratio") for r in runs]
gap_t14 = [A(r, "b2_kmeans_purified_whitened", "gap_ratio") for r in runs]; gap_b1 = [A(r, "b1_generator", "gap_ratio") for r in runs]
pred = lambda v, i: lam4[i] / (lam5[i] + rho[i] * v)
def sse(v): return sum((math.log(gap_u[i]) - math.log(pred(v, i))) ** 2 for i in range(n))
grid = [10 ** (x / 200) for x in range(-600, 400)]                      # v_cat from 1e-3 to 1e2
v_cat = min(grid, key=sse)
lg = [math.log(g) for g in gap_u]; mean_lg = st.mean(lg)
r2 = 1 - sse(v_cat) / sum((x - mean_lg) ** 2 for x in lg)
rel = [abs(pred(v_cat, i) - gap_u[i]) / gap_u[i] for i in range(n)]
fits = r2 >= 0.8 and st.median(rel) <= 0.25
mask = [i for i in range(n) if rho[i] > 0.05]
above = sum(gap_t1[i] > pred(v_cat, i) for i in mask)
above_ok = len(mask) > 0 and above / len(mask) >= 0.9
# rho-hat
rhohat = [(1 - r["purify"]["kept_fraction"]) - r["noop_control"]["trimmed_fraction"] for r in runs]
# blind E14
METRICS = [("angle_deg", 1), ("variant_r2", -1), ("core_invariant_r2", -1), ("nesting_perp_deg", 1), ("nesting_angle_deg", 1), ("block_purity", -1), ("a12_fro", 1)]
sd = {k: st.stdev([A(r, "b2_kmeans", k) for r in runs]) for k, _ in METRICS}
nodmg = [all((A(r, "b2_kmeans_purified", k) - A(r, "b2_kmeans", k)) * bad <= sd[k] for k, bad in METRICS) for r in runs]
V = lambda r, a: torch.tensor(r["arms"][a]["V"]).T
closer = [principal_angles_deg(V(r, "b2_kmeans_purified"), V(r, "b1_generator")).max() <= principal_angles_deg(V(r, "b2_kmeans"), V(r, "b1_generator")).max() for r in runs]
cv = lambda x: st.stdev(x) / st.mean(x)
cv1, cv14 = cv(gap_t1), cv(gap_t14); t4_case = cv14 <= 0.75 * cv1

rows = [[r["sigma_cat"], r["seed"], f"{r['quality']['cluster_purity']:.3f}", r["quality"]["k_discovered"], f"{rho[i]:.3f}", f"{gap_b1[i]:.1f}", f"{gap_u[i]:.1f}", f"{pred(v_cat, i):.1f}",
         f"{gap_t1[i]:.1f}", f"{gap_t14[i]:.1f}", f"{rhohat[i]:.3f}", "yes" if nodmg[i] else "**NO**", "yes" if closer[i] else "**NO**"] for i, r in enumerate(runs)]
md = [f"# E13 report: contamination model across the noise sweep ({n} runs), blind E14 check, Tier 4 comparability\n",
      f"**Model fit:** v_cat = {v_cat:.4g}; log-gap R² = {r2:.3f} (needs ≥ 0.8); median absolute relative error = {st.median(rel):.2f} (needs ≤ 0.25) -> **{'FITS' if fits else 'DOES NOT FIT'}**.\n",
      f"**Purified above the curve:** Tier 1 gap exceeds the predicted untreated gap in {above} of {len(mask)} runs with ρ > 0.05 (needs ≥ 90%) -> **{'YES' if above_ok else 'NO'}**.\n",
      f"**Blind E14:** no metric damaged in {sum(nodmg)} of {n} runs; treated subspace no farther from the B1-arm subspace in {sum(closer)} of {n} runs -> **{'CONFIRMED' if all(nodmg) and all(closer) else 'NOT CONFIRMED in every run'}**.\n",
      f"**Tier 4 comparability:** coefficient of variation of the rung-2 gap across runs, Tier 1 {cv1:.3f}, Tier 1 + Tier 4 {cv14:.3f} (Tier 4 keeps a case only if ≤ 75% of Tier 1's) -> **{'keeps a case' if t4_case else 'no case'}**.\n",
      f"**ρ-hat vs true ρ:** correlation {st.correlation(rhohat, rho):.3f}; mean ρ-hat {st.mean(rhohat):.3f} vs mean ρ {st.mean(rho):.3f}.\n",
      tab(["σ_cat", "seed", "Cluster purity", "K found", "True ρ", "Gap B1", "Gap B2 untreated", "Gap predicted (model)", "Gap Tier 1", "Gap Tier 1+4", "ρ-hat", "No damage (E14)", "Closer to B1 subspace (E14)"], rows)]
# exploratory refit (POST HOC, not the registered test): add a within-category term c * sigma_cat^2 to the "clean" floor, fitted jointly with v_cat
sig2 = [r["sigma_cat"] ** 2 for r in runs]
def sse2(c, v): return sum((math.log(gap_u[i]) - math.log(lam4[i] / (lam5[i] + c * sig2[i] + rho[i] * v))) ** 2 for i in range(n))
best = min(((c, v) for c in [x / 10 for x in range(0, 61)] for v in [10 ** (x / 40) for x in range(-120, 80)]), key=lambda t: sse2(*t))
r2b = 1 - sse2(*best) / sum((x - mean_lg) ** 2 for x in lg)
rel2 = [abs(lam4[i] / (lam5[i] + best[0] * sig2[i] + rho[i] * best[1]) - gap_u[i]) / gap_u[i] for i in range(n)]
b2_eig5 = [A(r, "b2_kmeans", "eigvals")[4] for r in runs]
valid_only = [(r["sigma_cat"], A(r, "b1_generator", "eigvals")[4], A(r, "b2_kmeans", "eigvals")[4], 2 * r["sigma_cat"] ** 2, 1 - r["construction"]["b2_kmeans"]["pair_validity"]) for r in runs if 1 - r["construction"]["b2_kmeans"]["pair_validity"] < 0.03]
# figure
W, H, L, B = 640, 380, 60, 40
xs = lambda x: L + (W - L - 20) * x / 0.7
ys = lambda y: H - B - (H - B - 20) * math.log10(max(y, 1)) / math.log10(80)
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="sans-serif" font-size="11"><rect width="100%" height="100%" fill="white"/>',
     f'<line x1="{L}" y1="{H-B}" x2="{W-20}" y2="{H-B}" stroke="#444"/><line x1="{L}" y1="20" x2="{L}" y2="{H-B}" stroke="#444"/>',
     f'<text x="{W/2}" y="{H-8}" text-anchor="middle">true mis-grouped fraction ρ</text><text x="14" y="{H/2}" transform="rotate(-90 14 {H/2})" text-anchor="middle">rung-2 gap ratio (log)</text>']
for g in (1, 3, 10, 30):
    o.append(f'<line x1="{L}" y1="{ys(g):.1f}" x2="{W-20}" y2="{ys(g):.1f}" stroke="#ddd"/><text x="{L-6}" y="{ys(g)+4:.1f}" text-anchor="end">{g}</text>')
for x in (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
    o.append(f'<text x="{xs(x):.1f}" y="{H-B+14}" text-anchor="middle">{x}</text>')
l4, l5 = st.median(lam4), st.median(lam5)
pts = " ".join(f"{xs(x/100):.1f},{ys(l4 / (l5 + x/100 * v_cat)):.1f}" for x in range(0, 70, 2))
o.append(f'<polyline points="{pts}" fill="none" stroke="#c0392b" stroke-width="2"/>')
o.append(f'<line x1="{L}" y1="{ys(10):.1f}" x2="{W-20}" y2="{ys(10):.1f}" stroke="#888" stroke-dasharray="4"/><text x="{W-24}" y="{ys(10)-4:.1f}" text-anchor="end" fill="#888">gate 10</text>')
for arm, col, lab in ((gap_b1, "#888", "B1 arm"), (gap_u, "#1f77b4", "B2 untreated"), (gap_t1, "#2ca02c", "B2 + Tier 1")):
    for i in range(n):
        o.append(f'<circle cx="{xs(rho[i]):.1f}" cy="{ys(arm[i]):.1f}" r="4" fill="{col}" fill-opacity="0.75"/>')
for k, (col, lab) in enumerate((("#888", "B1 arm"), ("#1f77b4", "B2 untreated"), ("#2ca02c", "B2 + Tier 1"), ("#c0392b", "model (median λ)"))):
    o.append(f'<rect x="{L+10+k*130}" y="26" width="10" height="10" fill="{col}"/><text x="{L+24+k*130}" y="35">{lab}</text>')
o.append("</svg>")
os.makedirs(f"{D}/figures", exist_ok=True)
open(f"{D}/figures/E13_gap_vs_contamination.svg", "w").write("".join(o))
md += ["\n## Exploratory (post hoc, NOT the registered test): a within-category floor\n",
       "Pairs built from clusters share the category label but not the category jitter, so even perfectly valid cluster pairs carry energy of about 2 sigma_cat^2 in the category directions; the B1 twins share the jitter exactly, so the B1 eigenvalue understates the floor for cluster pairs. Runs with almost no invalid pairs (rho < 0.03), fifth eigenvalue of the B1 arm vs the untreated B2 arm vs 2 sigma_cat^2: " + "; ".join(f"sigma {a:.1f}: {b:.3f} vs {c:.3f} vs {d:.3f} (rho {e:.3f})" for a, b, c, d, e in valid_only) + ".\n",
       f"Refit with a free within-category coefficient c: gap = lambda_d2 / (lambda_d2+1^B1 + c sigma_cat^2 + rho v_cat), best c = {best[0]:.1f}, v_cat = {best[1]:.3g}: log-gap R² = {r2b:.3f}, median relative error {st.median(rel2):.2f}. Two free parameters instead of one and fitted after seeing the data, so it is a lead, not a confirmation.\n",
       "\n![E13](figures/E13_gap_vs_contamination.svg)\n"]
open(f"{D}/E13_REPORT.md", "w").write("\n".join(md))
print("exploratory refit c,v,R2:", best, round(r2b, 3)); print("runs", n, "| fit", fits, f"R2={r2:.3f} medrel={st.median(rel):.2f} v_cat={v_cat:.3g}", "| above", above, "/", len(mask), "| E14 nodmg", sum(nodmg), "closer", sum(closer), "| CV", round(cv1, 3), round(cv14, 3))
