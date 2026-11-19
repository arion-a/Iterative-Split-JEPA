"""E55: coupling-strength sweep, untrained against trained invertible encoder. Rules from configs/sweep.criteria.yaml, frozen by hash before any run.
    python experiments/analyse_sweep.py -> results/minimal/SWEEP_REPORT.md"""
import glob, hashlib, json
import yaml

C = yaml.safe_load(open("configs/sweep.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/sweep.criteria.sha256").read().strip(), "criteria changed after freezing"
T = C["thresholds"]
load = lambda arm, s: sorted((json.load(open(f)) for f in glob.glob(f"{C['folder']}/{arm}/s{s}/main_seed*.json")), key=lambda r: r["seed"])
clean = lambda r: all(g["angle_deg"] < T["angle_max_deg"] and g["gap_ratio"] > T["gap_min"] for g in r["rungs"]) and all(p >= T["presence_min"] for p in r["presence"]["mlp"])
tab, n_clean, complete = {}, {}, True
for arm in ("u", "t"):
    for s in C["strengths"]:
        R = load(arm, s); complete &= len(R) >= len(C["seeds"]); n_clean[(arm, s)] = sum(clean(r) for r in R); tab[(arm, s)] = R
s_star = next((s for s in C["strengths"] if n_clean[("u", s)] <= 2), None)
if not complete: v = "INCOMPLETE"
elif s_star is None: v = "NOT INFORMATIVE (the untrained encoder passes at every tested strength)"
else: v = "CONFIRMED (training repairs it at s* = %s)" % s_star if n_clean[("t", s_star)] >= 4 else "REFUTED (the untrained encoder fails at s* = %s and training does not repair it)" % s_star
md = [f"# E55: coupling-strength sweep; frozen criteria `configs/sweep.criteria.yaml`\n", f"**E55: {v}.** Seeds clean (every rung and block) out of {len(C['seeds'])}:\n", "| Strength | Untrained encoder | Trained encoder (paper objective) |", "|---|---|---|", "| 0.5 (reference) | 6 of 6 (3 seeds x 2 depths) | 20 of 20 (E54) |"]
md += [f"| {s} | {n_clean[('u', s)]} of {len(tab[('u', s)])} | {n_clean[('t', s)]} of {len(tab[('t', s)])} |" for s in C["strengths"]]
md += ["", "| Arm | Strength | Seed | Angles | Gaps | Min presence |", "|---|---|---|---|---|---|"]
for arm in ("u", "t"):
    for s in C["strengths"]:
        md += [f"| {'untrained' if arm == 'u' else 'trained'} | {s} | {r['seed']} | " + ", ".join(f"{g['angle_deg']:.1f}" for g in r["rungs"]) + " | " + ", ".join(f"{g['gap_ratio']:.0f}" for g in r["rungs"]) + f" | {min(r['presence']['mlp']):.2f} |" for r in tab[(arm, s)]]
open("results/minimal/SWEEP_REPORT.md", "w").write("\n".join(md) + "\n"); print(f"E55: {v}")
