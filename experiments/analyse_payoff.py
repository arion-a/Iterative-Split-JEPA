"""E37 (Gap 6): hierarchy (ladder vs single-shot) and payoff (readout under identity shift). Rules from configs/payoff.criteria.yaml, frozen by hash before any run.
    python experiments/analyse_payoff.py -> results/stage_b1_e37/PAYOFF_REPORT.md"""
import glob, hashlib, json
import yaml

C = yaml.safe_load(open("configs/payoff.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/payoff.criteria.sha256").read().strip(), "criteria changed after freezing"
R = sorted((json.load(open(f)) for f in glob.glob("results/stage_b1_e37/main_seed*.json")), key=lambda r: r["seed"])
rows, h_ok, p_ok = [], 0, 0
for r in R:
    p = r["payoff"]; lad, ss, sh = p["ladder_angles_deg"], p["single_shot_angles_deg"], p["shift_readout"]
    lad_ok, ss_fail, pay = max(lad) < 5, max(ss) >= 5, sh[1]["loss"] < sh[0]["loss"]
    h_ok += lad_ok and ss_fail; p_ok += pay
    rows.append(f"| {r['seed']} | {lad[0]:.1f} / {lad[1]:.1f} | {ss[0]:.1f} / {ss[1]:.1f} | {'yes' if lad_ok and ss_fail else 'no'} | {sh[0]['loss']:.3f} | {sh[1]['loss']:.3f} | {'yes' if pay else 'no'} |")
n, ok = len(R), len(R) >= len(C["seeds"])
head = [f"# E37 (Gap 6): hierarchy and payoff in the synthetic world; frozen criteria `configs/payoff.criteria.yaml`\n",
        f"**E37a (hierarchy is real): {'CONFIRMED' if ok and h_ok >= 4 else 'REFUTED'}** ({h_ok} of {n} seeds: ladder below 5 deg at both rungs and single-shot 5 deg or more). "
        f"**E37b (it pays): {'CONFIRMED' if ok and p_ok >= 4 else 'REFUTED'}** (readout R2 loss under the identity shift smaller after rung 2 on {p_ok} of {n} seeds).\n",
        "| Seed | Ladder angles r1 / r2 (deg) | Single-shot angles b1 / b2 (deg) | Hierarchy | R2 loss after rung 1 | R2 loss after rung 2 | Smaller after rung 2 |", "|---|---|---|---|---|---|---|"]
open("results/stage_b1_e37/PAYOFF_REPORT.md", "w").write("\n".join(head + rows) + "\n"); print("\n".join(head))
