"""Stage C report (E24; REPORTING.md-style) from results/stage_c/<task>/split*.json. Thresholds as frozen in docs/EVIDENCE.md (E24)."""
import glob, json, os, statistics as st
from isj import svgplots as sv

OUT = "results/stage_c"
PAPER = {"PickCube": {"view": 8.4, "traj": 2.1}, "PushCube": {"view": 14.0, "traj": 3.1}}
tab = lambda h, rows: "\n".join(["| " + " | ".join(h) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])
ms = lambda v, nd=2: f"{st.mean(v):.{nd}f} ± {st.stdev(v):.{nd}f}" if len(v) > 1 else f"{v[0]:.{nd}f}"
data = {t: sorted((json.load(open(f)) for f in glob.glob(f"{OUT}/{t}/split*.json")), key=lambda r: r["split_seed"]) for t in ("PickCube", "PushCube")}
md = ["# Stage C report: the iterated spectral ladder on ManiSkill3 robot data (E24)\n",
      "Design and limits: `docs/stage_c_design.md`. Encoder: frozen ImageNet-initialized ResNet-50 features (2048-d) plus an MLP head trained with the JEPA recipe (adjacent-frame prediction, variance and covariance regulariser, no viewpoint-invariance term), 128-d output, then the engine's whitening and spectral ladder. Rung 1 = viewpoint pairs (base vs side camera), rung 2 = trajectory pairs. Block sizes by the absolute-gap rule γ = 0.1 λ₁ (Stage A); if no gap qualifies the largest gap ratio among the first 32 is used and flagged.\n"]
verdict = {}
for t, R in data.items():
    if not R: continue
    n = len(R); g = R[0]["groups"]
    P1 = [r["ratios"]["P1_view_V1_over_Q1"] for r in R]; P2 = [r["ratios"]["P2_traj_V2_over_Q2"] for r in R]
    c_ok = [r["controls"]["shuffled_pairs_rung1"]["gap_ratio_at_d1"] < 2 and r["controls"]["random_split_view_ratio"] < 1.5 and r["controls"]["random_split_traj_ratio"] < 1.5 for r in R]
    cam_ok = [r["probes"]["camera_acc_from_V1"] >= 0.9 and r["probes"]["camera_acc_from_Q1"] <= 0.65 for r in R]
    p = {"P1": all(x >= 3 for x in P1), "P2": all(x >= 1.5 for x in P2), "P3": all(c_ok), "P4": all(cam_ok)}; verdict[t] = p
    md += [f"## {t}: {g} groups × 8 trajectories (6 train / 2 validation per group), {n} split seeds\n",
           f"**E24 for {t}: {'CONFIRMED' if all(p.values()) else 'NOT confirmed'}** (P1 viewpoint ratio ≥ 3: {'yes' if p['P1'] else 'NO'}; P2 trajectory ratio ≥ 1.5: {'yes' if p['P2'] else 'NO'}; P3 controls: {'yes' if p['P3'] else 'NO'}; P4 camera decoding: {'yes' if p['P4'] else 'NO'}; each must hold on every split seed).\n",
           tab(["Quantity", "Value (mean ± std over split seeds)"],
               [["Block sizes chosen: rung 1 variant (viewpoint) / rung 2 variant (execution)", " / ".join(f"{r['rung1']['d']} / {r['rung2']['d']}" for r in R) + " (one pair per split seed)"],
                ["Fallback used (no gap met the rule): rung 1 / rung 2", " / ".join(f"{r['rung1']['no_cliff_fallback']} / {r['rung2']['no_cliff_fallback']}" for r in R)],
                ["Gap ratio at the chosen d: rung 1 / rung 2", f"{ms([r['rung1']['gap_ratio'] for r in R])} / {ms([r['rung2']['gap_ratio'] for r in R])}"],
                ["Rank monitor passes: rung 1 / rung 2", f"{sum(r['rung1']['rank_monitor']['pass'] for r in R)}/{n} / {sum(r['rung2']['rank_monitor']['pass'] for r in R)}/{n}"],
                ["P1: viewpoint pairs, response V1 / Q1 (paper two-block analogue " + str(PAPER[t]['view']) + "×)", ms(P1)],
                ["P2: trajectory pairs, response V2 / Q2 (paper analogue " + str(PAPER[t]['traj']) + "×)", ms(P2)],
                ["Paper-style two-block ratio (V1+V2 against Q2): viewpoint pairs / trajectory pairs", f"{ms([r['ratios']['paper_analogue_view_(V1+V2)_over_Q2'] for r in R])} / {ms([r['ratios']['paper_analogue_traj_(V1+V2)_over_Q2'] for r in R])}"],
                ["Control: random split of the same sizes, viewpoint / trajectory ratio", f"{ms([r['controls']['random_split_view_ratio'] for r in R])} / {ms([r['controls']['random_split_traj_ratio'] for r in R])}"],
                ["Control: shuffled pairs, rung-1 gap ratio at d = 1", ms([r["controls"]["shuffled_pairs_rung1"]["gap_ratio_at_d1"] for r in R])],
                ["P4: camera decoded from V1 / from Q1 (chance 0.5)", f"{ms([r['probes']['camera_acc_from_V1'] for r in R], 3)} / {ms([r['probes']['camera_acc_from_Q1'] for r in R], 3)}"],
                ["Layout (initial cube xy + goal xyz) R² from core Q2 / from V1 / from V2 / from all features", " / ".join(ms([r["probes"][k] for r in R], 3) for k in ("layout_r2_from_core_Q2", "layout_r2_from_V1", "layout_r2_from_V2", "layout_r2_from_all_features"))],
                ["Progress R² from core Q2 / from V2", f"{ms([r['probes']['progress_r2_from_core_Q2'] for r in R], 3)} / {ms([r['probes']['progress_r2_from_V2'] for r in R], 3)}"],
                ["Current cube position R² from core Q2", ms([r["probes"]["cube_pos_r2_from_core_Q2"] for r in R], 3)]]), ""]
os.makedirs(f"{OUT}/figures", exist_ok=True)
series = []
for t, R in data.items():
    if R:
        series += [(f"{t} rung 1", R[0]["rung1"]["eigvals_full"][:60], "--s1" if t == "PickCube" else "--s3"), (f"{t} rung 2", R[0]["rung2"]["eigvals_full"][:60], "--s2" if t == "PickCube" else "--s4")]
if series:
    open(f"{OUT}/figures/P2_spectra.svg", "w").write(sv.standalone(sv.log_lines(series, ymin=0.02, ymax=8, note="Pair-difference spectra, robot data, split seed 0", xlabel="direction number, largest first")))
    md.append("![P2](figures/P2_spectra.svg)\n\n*P2. Pair-difference spectra on the robot data, split seed 0. A cliff would show as a sharp drop; a smooth decay means no clean block boundary.*\n")
md += ["## Limits\nSimulated robot data generated here (ManiSkill motion-planning solutions with perturbed waypoints and speed; the paper's own way of generating trajectories is not stated); frozen ImageNet ResNet-50 plus a small trained head, not the paper's fine-tuned encoder; group count and frames per trajectory as stated per task above; the paper's behaviour-cloning and closed-loop results are out of scope."]
open(f"{OUT}/REPORT.md", "w").write("\n".join(md)); print("\n".join(md[:12]))
