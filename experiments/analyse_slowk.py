"""E31 (slow-subspace cluster count, controls) and E32 (boundary sweep): rules from configs/slowk.criteria.yaml, frozen by hash before any run.
    python experiments/analyse_slowk.py -> results/stage_b2_slowk/SLOWK_REPORT.md"""
import glob, hashlib, json, os, statistics as st
import yaml

C = yaml.safe_load(open("configs/slowk.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/slowk.criteria.sha256").read().strip(), "criteria changed after freezing"
K6, SEEDS = C["E31"]["k_true"], C["seeds"]
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def runs(folder, sg):
    out = []
    for s in SEEDS:
        p = f"{folder}/sigma_cat_{sg}/{s}.json"
        if os.path.exists(p): out.append(json.load(open(p)))
    return out


def d14(r, arm):
    g0 = r["arms"]["label_pairs"]["gap_ratio"]
    if arm not in r["arms"] or g0 < C["d14"]["min_perfect_gap"]: return None
    return r["arms"][arm]["gap_ratio"] >= C["d14"]["fraction_of_perfect_gap"] * g0


frac = lambda xs: f"{sum(1 for x in xs if x)}/{len(xs)}"
md = ["# G4-K: cluster count in the slow subspace (E31) and its boundary (E32); frozen criteria `configs/slowk.criteria.yaml`\n"]
ok_all, rows31, rows32, ceil_ok = [], [], [], True
E = C["E31"]
for sg in E["sigmas"]:
    R = runs("results/stage_b2_slowk", sg)
    n = len(R)
    k_slow = [r["quality"]["slowk"]["k"] for r in R]; k_sp = [r["quality"]["spectral"]["k"] for r in R]; k_sil = [r["quality"]["k_discovered"] for r in R]
    k6 = sum(k == K6 for k in k_slow)
    pur = [r["quality"]["slowk"].get("purity") for r in R]
    ctl = sum(r["quality"]["slowk"]["control_shuffled_time"]["k"] == K6 for r in R)
    ang = [r["quality"]["slowk"].get("subspace_angle_deg") for r in R if r["quality"]["slowk"].get("subspace_angle_deg") is not None]
    a_ok = n >= 10 and k6 >= E["a_k6_min_runs_per_sigma"]
    b_ok = None if sg not in E["b_sigmas"] else (n >= 10 and sum(p is not None and p >= E["b_purity_min"] for p in pur) >= E["b_purity_min_runs_per_sigma"])
    c_ok = n >= 10 and ctl <= E["c_control_k6_max_runs_per_sigma"]
    ok_all += [a_ok, c_ok] + ([b_ok] if b_ok is not None else [])
    rows31.append([sg, n, f"{k6}/{n}", f"{sum(k == K6 for k in k_sp)}/{n}", f"{sum(k == K6 for k in k_sil)}/{n}", ("n/a" if b_ok is None else ("yes" if b_ok else "NO")) + f" (mean purity {st.mean(p for p in pur if p is not None):.3f})" if any(p is not None for p in pur) else "n/a",
                   f"{ctl}/{n}", f"{ms(ang) if False else (f'{st.median(ang):.1f}' if ang else 'n/a')}",
                   f"{frac([d14(r, 'b2_slowk_purified') for r in R if d14(r, 'b2_slowk_purified') is not None])} / {frac([d14(r, 'b2_kmeans_purified') for r in R if d14(r, 'b2_kmeans_purified') is not None])} / {frac([d14(r, 'b2_spectral_purified') for r in R if d14(r, 'b2_spectral_purified') is not None])}",
                   "yes" if a_ok else "NO"])
RE = runs("results/stage_b2_slowk_equal", E["d_sigma"])
d_ok = len(RE) >= 10 and sum(r["quality"]["slowk"]["abstained"] for r in RE) >= E["d_equal_speed_abstain_min_runs"]
ok_all.append(d_ok)
v31 = "CONFIRMED" if all(ok_all) else "REFUTED"
md += [f"## E31: **{v31}** (a: K = 6 in at least {E['a_k6_min_runs_per_sigma']} of 10 runs at each sigma_cat; b: purity at least {E['b_purity_min']} in at least {E['b_purity_min_runs_per_sigma']} of 10 at sigma_cat {E['b_sigmas']}; c: shuffled-time control K = 6 in at most {E['c_control_k6_max_runs_per_sigma']} of 10; d: equal-speed control abstains in at least {E['d_equal_speed_abstain_min_runs']} of 10)\n",
       tab(["sigma_cat", "runs", "K = 6, slow-subspace (a)", "K = 6, E18 spectral (full space)", "K = 6, silhouette", "purity condition (b)", "control K = 6 (c)", "median subspace angle to category (deg)", "D14 criterion met after Tier 1: slow / silhouette / E18 spectral", "(a) held"], rows31),
       f"\n**Control d, equal speeds (sigma_cat {E['d_sigma']}):** the selector abstained in {sum(r['quality']['slowk']['abstained'] for r in RE)} of {len(RE)} runs ({'held' if d_ok else 'did not hold'}).\n"]
E2 = C["E32"]; ok32, bound = [], None
for sg in [0.1, 0.4, 0.6] + E2["sigmas"]:
    R = runs("results/stage_b2_slowk", sg); n = len(R)
    k6 = sum(r["quality"]["slowk"]["k"] == K6 for r in R)
    pur = [r["quality"]["slowk"].get("purity") for r in R if r["quality"]["slowk"].get("purity") is not None]
    if k6 >= 8 and n >= 10: bound = sg
    if sg in E2["sigmas"]:
        need = E2["k6_min_runs"][str(sg)]
        ceil = E2["purity_ceiling"][str(sg)] + E2["purity_ceiling_slack"]
        ok32 += [n >= 10 and k6 >= need, all(p <= ceil for p in pur)]
    rows32.append([sg, n, f"{k6}/{n}", f"{st.mean(pur):.3f}" if pur else "n/a", f"{sum(r['quality']['slowk']['abstained'] for r in R)}/{n}"])
v32 = "CONFIRMED" if all(ok32) and ok32 else "REFUTED"
md += [f"## E32: **{v32}** (K = 6 in at least {E2['k6_min_runs']['0.8']} of 10 at sigma_cat 0.8 and {E2['k6_min_runs']['1.0']} of 10 at 1.0; purity never above the ceiling plus {E2['purity_ceiling_slack']})\n",
       tab(["sigma_cat", "runs", "K = 6", "mean purity, slow-subspace clusters", "abstained"], rows32),
       f"\n**Located boundary ({E2['boundary_rule']}):** sigma_cat = {bound}.\n"]
open("results/stage_b2_slowk/SLOWK_REPORT.md", "w").write("\n".join(md)); print("\n".join(md))
