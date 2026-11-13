"""E48-E51 (the open Stage C and Stage D items). Rules from configs/open_items.criteria.yaml, frozen by hash before any run.
    python experiments/analyse_open_items.py -> results/minimal/OPEN_ITEMS_REPORT.md"""
import glob, hashlib, json
import numpy as np, yaml

C = yaml.safe_load(open("configs/open_items.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/open_items.criteria.sha256").read().strip(), "criteria changed after freezing"
load = lambda folder: sorted((json.load(open(f)) for f in glob.glob(f"{folder}/main_seed*.json")), key=lambda r: r["seed"])
md, ver = [], {}
# E48 rate
c = C["E48"]; R = load(c["folder"]); rng = np.random.default_rng(c["bootstrap"]["rng_seed"]); ns = c["ns"]
rows = []
for k in (0, 1):
    A = np.array([[r["rate"][str(n)][k] for n in ns] for r in R])                          # seeds x ns
    slope = lambda M: np.polyfit(np.log10(ns), np.log10(M.mean(0)), 1)[0]
    s0 = slope(A); bs = [slope(A[rng.integers(0, len(A), len(A))]) for _ in range(c["bootstrap"]["resamples"])] if len(A) else [0]
    lo, hi = np.percentile(bs, [2.5, 97.5]); rows.append((k + 1, s0, lo, hi, A.mean(0), lo <= c["target_slope"] <= hi))
ver["E48"] = "INCOMPLETE" if len(R) < len(c["seeds"]) else ("CONFIRMED" if all(x[5] for x in rows) else "REFUTED")
md += [f"## E48 (the 1/sqrt(n) rate with a learned encoder, against the encoder's own eigenspace): {ver['E48']}", "| Rung | Slope | 95% interval | Mean angle (deg) at n = " + ", ".join(str(n) for n in ns) + " |", "|---|---|---|---|"]
md += [f"| {k} | {s:.2f} | [{lo:.2f}, {hi:.2f}] | " + ", ".join(f"{a:.3f}" for a in m) + " |" for k, s, lo, hi, m, _ in rows]
# E49 confirmatory
c = C["E49"]; ok49, lines = True, []
for K, folder in c["folders"].items():
    R = load(folder); n = len(R)
    ok = lambda g: g["angle_deg"] < c["angle_max_deg"] and g["gap_ratio"] > c["gap_min"]
    rung = [sum(ok(r["rungs"][i]) for r in R) for i in range(int(K) - 1)]
    health = sum(r["output_cov_min_eig"] >= c["health_min_eig"] for r in R); core = sum(r["presence"]["mlp"][-1] >= c["core_presence_min"] for r in R)
    good = n >= len(c["seeds"]) and all(x >= c["rung_min_seeds"] for x in rung) and health >= c["health_min_seeds"] and core >= c["core_min_seeds"]
    ok49 &= good; lines.append(f"{K} blocks ({n} seeds): clean rungs by rung {rung} (needs {c['rung_min_seeds']}), no dead direction {health} (needs {c['health_min_seeds']}), core present {core} (needs {c['core_min_seeds']}): {'met' if good else 'NOT met'}")
ver["E49"] = "INCOMPLETE" if any(len(load(f)) < 10 for f in c["folders"].values()) else ("CONFIRMED" if ok49 else "REFUTED")
md += ["", f"## E49 (the E45 recipe on fresh seeds): {ver['E49']}"] + [f"- {x}" for x in lines]
# E50 / E51
R = load(C["E50"]["folder"]); c = C["E50"]; n = len(R)
pa = sum(max(r["stage_d"]["pooled_one_shot"]["angles_deg"]) < c["pooled_angle_below_deg"] for r in R)
pg = sum(r["stage_d"]["pooled_one_shot"]["gap_b1_b2"] < c["pooled_gap_b1_b2_below"] for r in R); lg = sum(min(r["stage_d"]["ladder_gaps"]) > c["ladder_min_gap_above"] for r in R)
ver["E50"] = "INCOMPLETE" if n < len(c["seeds"]) else ("CONFIRMED" if pa >= c["pooled_angle_min_seeds"] and pg >= c["gap_min_seeds"] and lg >= c["gap_min_seeds"] else "REFUTED")
md += ["", f"## E50 (a flat one-shot split from the pooled correspondence families, equal speeds): {ver['E50']}", f"Pooled one-shot worst angle under {c['pooled_angle_below_deg']:.0f} on {pa} of {n} (needs {c['pooled_angle_min_seeds']}); its block-1 / block-2 gap under {c['pooled_gap_b1_b2_below']:.0f} on {pg} of {n}; the ladder's smallest rung gap over {c['ladder_min_gap_above']:.0f} on {lg} of {n} (both need {c['gap_min_seeds']}).\n",
       "| Seed | Pooled angles (deg) | Pooled gaps (b1/b2, b2/core) | Ladder rung gaps |", "|---|---|---|---|"]
md += [f"| {r['seed']} | " + ", ".join(f"{x:.1f}" for x in r["stage_d"]["pooled_one_shot"]["angles_deg"]) + f" | {r['stage_d']['pooled_one_shot']['gap_b1_b2']:.2f}, {r['stage_d']['pooled_one_shot']['gap_b2_core']:.1f} | " + ", ".join(f"{g:.0f}" for g in r["stage_d"]["ladder_gaps"]) + " |" for r in R]
c = C["E51"]
core_ok = sum(r["stage_d"]["robust"]["core"]["test_shifted_r2"] >= c["core_shifted_r2_min"] for r in R)
adv = sum(r["stage_d"]["robust"]["core"]["test_shifted_r2"] - r["stage_d"]["robust"]["whole"]["test_shifted_r2"] >= c["advantage_min"] for r in R)
ctl = sum(abs(r["stage_d"]["robust"]["core"]["test_correlated_r2"] - r["stage_d"]["robust"]["whole"]["test_correlated_r2"]) < c["control_max_difference"] for r in R)
ver["E51"] = "INCOMPLETE" if n < 5 else ("CONFIRMED" if min(core_ok, adv, ctl) >= c["min_seeds"] else "REFUTED")
md += ["", f"## E51 (does the invariant core pay under a nuisance shift): {ver['E51']}", f"Core-only readout shifted R2 at least {c['core_shifted_r2_min']} on {core_ok} of {n}; beats the whole-embedding readout by at least {c['advantage_min']} on {adv}; without the shift the two differ by under {c['control_max_difference']} on {ctl} (each needs {c['min_seeds']}).\n",
       "| Seed | Whole: correlated / shifted R2 | Core only: correlated / shifted R2 |", "|---|---|---|"]
md += [f"| {r['seed']} | {r['stage_d']['robust']['whole']['test_correlated_r2']:.2f} / {r['stage_d']['robust']['whole']['test_shifted_r2']:.2f} | {r['stage_d']['robust']['core']['test_correlated_r2']:.2f} / {r['stage_d']['robust']['core']['test_shifted_r2']:.2f} |" for r in R]
head = ["# The open Stage C and Stage D items (E48-E51); frozen criteria `configs/open_items.criteria.yaml`\n", "| Item | Verdict |", "|---|---|"] + [f"| {k} | {v} |" for k, v in ver.items()] + [""]
open("results/minimal/OPEN_ITEMS_REPORT.md", "w").write("\n".join(head + md) + "\n"); print("\n".join(head))
