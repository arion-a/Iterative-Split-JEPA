"""E36 (Gap 5): P1-P4 of E24 with the paper's rung-1 block sizes. Rules from configs/fixed_sizes.criteria.yaml, frozen by hash before any run.
    python experiments/robot/analyse_fixed.py -> results/stage_c_fixed/FIXED_REPORT.md"""
import glob, hashlib, json
import yaml

C = yaml.safe_load(open("configs/fixed_sizes.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/fixed_sizes.criteria.sha256").read().strip(), "criteria changed after freezing"
md, out = [], {}
for t in C["tasks"]:
    R = sorted((json.load(open(f)) for f in glob.glob(f"{C['out']}/{t}/split*.json")), key=lambda r: r["split_seed"])
    P1 = [r["ratios"]["P1_view_V1_over_Q1"] for r in R]; P2 = [r["ratios"]["P2_traj_V2_over_Q2"] for r in R]
    P3 = [r["controls"]["shuffled_pairs_rung1"]["gap_ratio_at_d1"] < 2 and r["controls"]["random_split_view_ratio"] < 1.5 and r["controls"]["random_split_traj_ratio"] < 1.5 for r in R]
    P4 = [r["probes"]["camera_acc_from_V1"] >= 0.9 and r["probes"]["camera_acc_from_Q1"] <= 0.65 for r in R]
    p = {"P1": all(x >= 3 for x in P1), "P2": all(x >= 1.5 for x in P2), "P3": all(P3), "P4": all(P4)}
    out[t] = len(R) == len(C["split_seeds"]) and all(p.values())
    for r, a, b, c3, c4 in zip(R, P1, P2, P3, P4):
        md.append(f"| {t} | {r['split_seed']} | {r['rung1']['d']} | {r['rung1']['gap_ratio']:.2f} | {a:.2f} | {b:.2f} | {'yes' if c3 else 'no'} | {r['probes']['camera_acc_from_V1']:.3f} / {r['probes']['camera_acc_from_Q1']:.3f} |")
    md.append(f"| {t} | verdict | | | P1 {'yes' if p['P1'] else 'NO'} | P2 {'yes' if p['P2'] else 'NO'} | P3 {'yes' if p['P3'] else 'NO'} | P4 {'yes' if p['P4'] else 'NO'} |")
head = [f"# E36 (Gap 5): paper block sizes on the E24 pipeline; frozen criteria `configs/fixed_sizes.criteria.yaml`\n",
        "**E36: " + ("CONFIRMED" if all(out.values()) else "REFUTED") + ".** " + "; ".join(f"{t}: {'P1-P4 all hold' if v else 'not all hold'}" for t, v in out.items()) + ".\n",
        "| Task | Split seed | d1 | Rung-1 gap | P1 V1/Q1 (>=3) | P2 V2/Q2 (>=1.5) | P3 controls | Camera acc V1 / Q1 |", "|---|---|---|---|---|---|---|---|"]
open(f"{C['out']}/FIXED_REPORT.md", "w").write("\n".join(head + md) + "\n"); print("\n".join(head))
