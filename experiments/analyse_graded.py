"""E57: graded table (angle, gap, presence per rung) for the two cells; applies the registered 'visible functionality' reading (angle < 20 and gap > 2 on >= 4 of 5 seeds).
    python experiments/analyse_graded.py -> results/minimal/GRADED_REPORT.md"""
import glob, json
md = []
for cell in ("b5_s2", "b4_s4"):
    R = sorted((json.load(open(f)) for f in glob.glob(f"results/minimal/e57/{cell}/main_seed*.json")), key=lambda r: r["seed"])
    ok = sum(all(g["angle_deg"] < 20 and g["gap_ratio"] > 2 for g in r["rungs"]) for r in R)
    md += [f"### {cell}: visible functionality on {ok} of {len(R)} seeds (every rung angle < 20, gap > 2)\n", "| Seed | Angles | Gaps | Presence (blocks) |", "|---|---|---|---|"]
    md += [f"| {r['seed']} | " + ", ".join(f"{g['angle_deg']:.1f}" for g in r["rungs"]) + " | " + ", ".join(f"{g['gap_ratio']:.1f}" for g in r["rungs"]) + " | " + ", ".join(f"{p:.2f}" for p in r["presence"]["mlp"]) + " |" for r in R] + [""]
open("results/minimal/GRADED_REPORT.md", "w").write("\n".join(md)); print("\n".join(md))
