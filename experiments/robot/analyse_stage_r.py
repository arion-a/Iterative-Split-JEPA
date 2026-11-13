"""Stage R: E46 (head diagnostic) and E47 (invariance + whitening terms on the robot head). Rules from configs/stage_r.criteria.yaml, frozen by hash before any run.
    python experiments/robot/analyse_stage_r.py -> results/stage_r/STAGE_R_REPORT.md"""
import glob, hashlib, json
import yaml

C = yaml.safe_load(open("configs/stage_r.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/stage_r.criteria.sha256").read().strip(), "criteria changed after freezing"
load = lambda arm, t: sorted((json.load(open(f)) for f in glob.glob(f"{C['folders'][arm]}/{t}/split*.json")), key=lambda r: r["split_seed"])
def p14(r):
    return {"P1": r["ratios"]["P1_view_V1_over_Q1"] >= 3, "P2": r["ratios"]["P2_traj_V2_over_Q2"] >= 1.5,
            "P3": r["controls"]["shuffled_pairs_rung1"]["gap_ratio_at_d1"] < 2 and r["controls"]["random_split_view_ratio"] < 1.5 and r["controls"]["random_split_traj_ratio"] < 1.5,
            "P4": r["probes"]["camera_acc_from_V1"] >= 0.9 and r["probes"]["camera_acc_from_Q1"] <= 0.65}
dead = lambda r: r["head_cov_min_eig"] < 0.01 * (sum(r["head_cov_eigs"]) / len(r["head_cov_eigs"]))   # eigenvalues are sampled evenly; the minimum is exact
md, out = [], {}
B = [(t, r) for t in C["tasks"] for r in load("baseline", t)]
nd = sum(dead(r) for _, r in B); v46 = "INCOMPLETE" if len(B) < 6 else ("CONFIRMED" if nd >= 4 else "REFUTED")
md += [f"## E46 (does the baseline robot head have dead output directions): {v46}", f"Dead direction (eigenvalue under 1% of the mean) on {nd} of {len(B)} baseline runs (prediction: at least 4 of 6).\n",
       "| Task | Seed | Min eigenvalue | Effective rank (of embedding size) | Dead | P1 ratio | Rung-1 gap |", "|---|---|---|---|---|---|---|"]
md += [f"| {t} | {r['split_seed']} | {r['head_cov_min_eig']:.4g} | {r['head_eff_rank']:.1f} of {r['pca']} | {'yes' if dead(r) else 'no'} | {r['ratios']['P1_view_V1_over_Q1']:.2f} | {r['rung1']['gap_ratio']:.2f} |" for t, r in B]
ver = {}
md += ["", "## E47 (invariance and whitening terms on the robot head)", "| Task | Arm | Seed | P1 | P2 | P3 | P4 | P1 ratio | Rung-1 gap | Held-out P1 | Held-out layout R2 (core / all) | Held-out progress R2 (core / all) |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for t in C["tasks"]:
    for arm in ("baseline", "treated"):
        for r in load(arm, t):
            p = p14(r); h = r.get("heldout", {})
            md.append(f"| {t} | {arm} | {r['split_seed']} | " + " | ".join("yes" if p[k] else "no" for k in ("P1", "P2", "P3", "P4")) + f" | {r['ratios']['P1_view_V1_over_Q1']:.2f} | {r['rung1']['gap_ratio']:.2f} | {h.get('P1_view_V1_over_Q1', float('nan')):.2f} | {h.get('layout_r2_from_core_Q2', float('nan')):.2f} / {h.get('layout_r2_from_all_features', float('nan')):.2f} | {h.get('progress_r2_from_core_Q2', float('nan')):.2f} / {h.get('progress_r2_from_all_features', float('nan')):.2f} |")
    T = load("treated", t)
    ver[t] = "INCOMPLETE" if len(T) < 3 else ("CONFIRMED" if all(all(p14(r).values()) for r in T) else "REFUTED")
head = ["# Stage R: the robot head with the theory's terms; frozen criteria `configs/stage_r.criteria.yaml`\n", "| Item | Verdict |", "|---|---|", f"| E46 diagnostic | {v46} |"] + [f"| E47 {t} | {v} |" for t, v in ver.items()] + [""]
open("results/stage_r/STAGE_R_REPORT.md", "w").write("\n".join(head + md) + "\n"); print("\n".join(head))
