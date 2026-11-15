"""E58 table: median angle, median gap and (k-means arms) median purity per arm and rung over seeds 250-254, plus seeds with angle < 30 degrees.
    python experiments/analyse_nested.py -> results/minimal/NESTED_REPORT.md"""
import glob, json, statistics as st
R = [json.load(open(f)) for f in sorted(glob.glob("results/minimal/e58/seed*.json"))]
md = [f"E58: {len(R)} seeds. Per arm and rung: median angle (degrees; unrelated about 80), seeds with angle < 30, median gap, median cluster purity.\n", "| Arm | Rung | Median angle | Seeds angle<30 | Median gap | Median purity |", "|---|---|---|---|---|---|"]
for arm in ("generator", "label", "kmeans_slow", "kmeans_all", "random"):
    for k in range(1, 6):
        rs = [next(x for x in r["arms"][arm] if x["k"] == k) for r in R]
        pur = [x["purity"] for x in rs if "purity" in x]
        md.append(f"| {arm} | {k} | {st.median(x['angle_deg'] for x in rs):.1f} | {sum(x['angle_deg'] < 30 for x in rs)} of {len(rs)} | {st.median(x['gap_ratio'] for x in rs):.1f} | {st.median(pur):.2f} |" if pur else
                  f"| {arm} | {k} | {st.median(x['angle_deg'] for x in rs):.1f} | {sum(x['angle_deg'] < 30 for x in rs)} of {len(rs)} | {st.median(x['gap_ratio'] for x in rs):.1f} | - |")
open("results/minimal/NESTED_REPORT.md", "w").write("\n".join(md) + "\n"); print("\n".join(md))
