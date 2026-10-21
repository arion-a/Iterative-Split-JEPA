"""E34 (Gap 3): depth 4 and 5 and pair-count scaling. Rules from configs/depth.criteria.yaml, frozen by hash before any run.
    python experiments/analyse_depth.py -> results/stage_b1_e34/DEPTH_REPORT.md"""
import glob, hashlib, json
import numpy as np, yaml
from isj.stage_b1 import criteria_keys, seed_checks

C = yaml.safe_load(open("configs/depth.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/depth.criteria.sha256").read().strip(), "criteria changed after freezing"
crit = yaml.safe_load(open("configs/stage_b1.yaml"))["criteria"]
load = lambda d: sorted((json.load(open(f)) for f in glob.glob(f"results/stage_b1_e34/{d}/main_seed*.json")), key=lambda r: r["seed"])
md, ok = [], True
md += ["| Depth | Check | Seeds passing |", "|---|---|---|"]
for K in C["depths"]:
    runs = load(f"depth{K}"); n = len(runs); keys = criteria_keys(K - 1)
    per = [seed_checks(r, crit) for r in runs]
    cnt = {k: sum(p[k] for p in per) for k in keys}
    bad = [k for k in keys if cnt[k] < C["check_min_seeds"]]
    ok &= n >= len(C["depth_seeds"]) and not bad
    md += [f"| {K} blocks ({K-1} rungs) | {k} | {cnt[k]} of {n} |" for k in keys]
    md.append(f"| {K} blocks | **first violated** | {bad[0] if bad else 'none'} |")
rng = np.random.default_rng(C["bootstrap"]["rng_seed"]); ns = C["scaling_pairs"]
ang = {n: np.array([np.mean([g["angle_deg"] for g in r["rungs"]]) for r in load(f"scale_{n}")]) for n in ns}
fit = lambda a: np.polyfit(np.log10(ns), np.log10([a[n].mean() for n in ns]), 1)[0]
slope = fit(ang)
bs = [fit({n: rng.choice(ang[n], len(ang[n])) for n in ns}) for _ in range(C["bootstrap"]["resamples"])]
lo, hi = np.percentile(bs, [2.5, 97.5])
okS = all(len(ang[n]) >= len(C["scaling_seeds"]) for n in ns) and lo <= C["scaling_target_slope"] <= hi
v = "CONFIRMED" if ok and okS else "REFUTED"
head = [f"# E34 (Gap 3): depth and scaling; frozen criteria `configs/depth.criteria.yaml`\n",
        f"**E34: {v}.** Depth checks (each check on at least {C['check_min_seeds']} of 5 seeds, at depth 4 and 5): {'held' if ok else 'NOT held'}. "
        f"Scaling slope of mean rung angle against pairs per rung: {slope:.2f}, 95% bootstrap interval [{lo:.2f}, {hi:.2f}]; contains {C['scaling_target_slope']}: {'yes' if okS else 'NO'}.\n",
        "| Pairs per rung | Mean rung angle (deg) over seeds |", "|---|---|"] + [f"| {n} | {ang[n].mean():.2f} (n={len(ang[n])}) |" for n in ns] + [""]
open("results/stage_b1_e34/DEPTH_REPORT.md", "w").write("\n".join(head + md) + "\n"); print("\n".join(head))
