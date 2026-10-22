"""E38-E41: the four minimal claims. Rules from configs/minimal.criteria.yaml, frozen by hash before any run.
    python experiments/analyse_minimal.py -> results/minimal/MINIMAL_REPORT.md"""
import glob, hashlib, json
import yaml

C = yaml.safe_load(open("configs/minimal.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/minimal.criteria.sha256").read().strip(), "criteria changed after freezing"
T = C["thresholds"]
load = lambda folder, arm="main": sorted((json.load(open(f)) for f in glob.glob(f"{folder}/{arm}_seed*.json")), key=lambda r: r["seed"])
clean = lambda g: g["angle_deg"] < T["angle_max_deg"]
md, verdicts, rungs = [], {}, []
def rows(R, tag):
    for r in R:
        for k, g in enumerate(r["rungs"], 1):
            rungs.append((tag, r["seed"], k, r["presence"]["mlp"][k - 1] >= T["presence_min"], g["gap_ratio"] > T["gap_min"], clean(g)))

# E38 equal speeds: the ladder works and the single-shot split does not
c = C["E38"]; R = load(c["folder"]); rows(R, "E38")
lad = [max(r["payoff"]["ladder_angles_deg"]) for r in R]; ss = [max(r["payoff"]["single_shot_angles_deg"]) for r in R]
n1 = sum(a < c["ladder_below_deg"] for a in lad); n2 = sum(a >= c["single_shot_at_least_deg"] for a in ss)
verdicts["E38"] = "CONFIRMED" if len(R) >= c["min_seeds"] and n1 >= c["min_seeds"] and n2 >= c["min_seeds"] else "REFUTED"
sep = load(c["separated_reference"])
md += [f"## E38 (equal speeds, correspondence against speed): {verdicts['E38']}", f"Ladder worst angle under {c['ladder_below_deg']:.0f} on {n1} of {len(R)} seeds; single-shot worst angle {c['single_shot_at_least_deg']:.0f} or more on {n2} of {len(R)}.\n",
       "| Seed | Ladder worst angle (deg) | Single-shot worst angle (deg) |", "|---|---|---|"] + [f"| {r['seed']} | {a:.1f} | {b:.1f} |" for r, a, b in zip(R, lad, ss)]
md += [f"\nSeparated-speed cell (E37, seeds {', '.join(str(r['seed']) for r in sep)}): ladder " + ", ".join(f"{max(r['payoff']['ladder_angles_deg']):.1f}" for r in sep) + "; single-shot " + ", ".join(f"{max(r['payoff']['single_shot_angles_deg']):.1f}" for r in sep) + "\n"]

# E39 depth 5
c = C["E39"]; R = load(c["folder"]); K = load(c["folder"], c["control_arm"]); rows(R, "E39")
chk = {"angle": lambda r: all(clean(g) for g in r["rungs"]), "gap": lambda r: all(g["gap_ratio"] > T["gap_min"] for g in r["rungs"]),
       "presence": lambda r: all(p >= T["presence_min"] for p in r["presence"]["mlp"]), "rho": lambda r: all(p["rho"] <= T["rho_max"] for p in r["predictive"])}
cnt = {k: sum(f(r) for r in R) for k, f in chk.items()}
ctl = sum(r["rungs"][1]["gap_ratio"] < c["control_rung2_gap_below"] for r in K), sum(r["predictive"][1]["rho"] > c["control_rho2_above"] for r in K)
rho_ok = ctl[1] >= c["control_min_seeds"]
need = [k for k in cnt if k != "rho" or rho_ok]
ok = len(R) >= len(c["seeds"]) and all(cnt[k] >= c["each_check_min_seeds"] for k in need) and ctl[0] >= c["control_min_seeds"]
verdicts["E39"] = "CONFIRMED" if ok else "REFUTED"
md += [f"## E39 (depth 5, predictively sufficient): {verdicts['E39']}", "Seeds passing each check at every rung (needs " + str(c["each_check_min_seeds"]) + f" of {len(R)}): " + ", ".join(f"{k} {v}" for k, v in cnt.items()) + f". Control (shuffled rung 2, {len(K)} seeds): rung-2 gap under {c['control_rung2_gap_below']:.0f} on {ctl[0]}, rho_2 over {c['control_rho2_above']} on {ctl[1]}" + ("" if rho_ok else "; **rho_k not informative (control did not exceed the line), dropped from the verdict**") + ".\n",
       "| Seed | Angles per rung | Gap ratios | rho_k per rung |", "|---|---|---|---|"] + [f"| {r['seed']} | " + ", ".join(f"{g['angle_deg']:.1f}" for g in r["rungs"]) + " | " + ", ".join(f"{g['gap_ratio']:.0f}" for g in r["rungs"]) + " | " + ", ".join(f"{p['rho']:.3f}" for p in r["predictive"]) + " |" for r in R]
md += ["", "Control rho_2: " + ", ".join(f"{r['predictive'][1]['rho']:.3f}" for r in K) + "\n"]

# E40 encoder objective
c = C["E40"]; B = load(c["baseline"]); X = load(c["treated"]); rows(B, "E40 baseline"); rows(X, "E40 treated")
good = lambda r: all(p >= T["presence_min"] for p in r["presence"]["mlp"]) and all(clean(g) and g["gap_ratio"] > T["gap_min"] for g in r["rungs"])
nt = sum(good(r) for r in X); nb = sum(r["presence"]["mlp"][0] < c["baseline_texture_presence_below"] for r in B)
if len(B) < len(c["seeds"]) or len(X) < len(c["seeds"]): v = "INCOMPLETE"
elif nb < c["baseline_min_seeds"]: v = "NOT INFORMATIVE (baseline did not fail)"
else: v = "CONFIRMED" if nt >= c["treated_min_seeds"] else "REFUTED"
verdicts["E40"] = v
md += [f"## E40 (the theory's invariance term, generic MLP): {v}", f"Treated: all presences at least {T['presence_min']} and both rungs clean with gap over {T['gap_min']:.0f} on {nt} of {len(X)} seeds (needs {c['treated_min_seeds']}). Baseline: texture presence under {c['baseline_texture_presence_below']} on {nb} of {len(B)} (needs {c['baseline_min_seeds']}).\n",
       "| Arm | Seed | Presence (b1, b2, b3) | Angles | Gap ratios |", "|---|---|---|---|---|"]
for tag, S in (("baseline", B), ("treated", X)):
    md += [f"| {tag} | {r['seed']} | " + ", ".join(f"{p:.2f}" for p in r["presence"]["mlp"]) + " | " + ", ".join(f"{g['angle_deg']:.1f}" for g in r["rungs"]) + " | " + ", ".join(f"{g['gap_ratio']:.1f}" for g in r["rungs"]) + " |" for r in S]

# E41 detectors
c = C["E41"]
a = [x for x in rungs if x[4] and x[3]]; b = [x for x in rungs if not x[4]]
fa = sum(x[5] for x in a) / max(len(a), 1); fb = sum(x[5] for x in b) / max(len(b), 1)
if len(a) < c["min_rungs_per_cell"] or len(b) < c["min_rungs_per_cell"]: v = "NOT INFORMATIVE (a cell has too few rungs)"
else: v = "CONFIRMED" if fa >= c["gap_over_10_and_present_clean_fraction_min"] and fb <= c["gap_10_or_less_clean_fraction_max"] else "REFUTED"
verdicts["E41"] = v
md += [f"\n## E41 (a violated hypothesis shows in the gap): {v}", f"Rungs with gap over {T['gap_min']:.0f} and block present: {sum(x[5] for x in a)} of {len(a)} clean ({fa:.0%}; needs {c['gap_over_10_and_present_clean_fraction_min']:.0%}). Rungs with gap {T['gap_min']:.0f} or less: {sum(x[5] for x in b)} of {len(b)} clean ({fb:.0%}; at most {c['gap_10_or_less_clean_fraction_max']:.0%}). All main-arm runs of E38-E40 ({len(rungs)} rungs).\n"]
head = ["# Minimal claims (E38-E41); frozen criteria `configs/minimal.criteria.yaml`\n", "| Claim | Verdict |", "|---|---|"] + [f"| {k} | {v} |" for k, v in verdicts.items()] + [""]
open("results/minimal/MINIMAL_REPORT.md", "w").write("\n".join(head + md) + "\n"); print("\n".join(head))
