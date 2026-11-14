"""E56: strength 2, trained encoder, rung gate off (configs/sweep/t_s2_nogate.yaml), seeds 250-254. Thresholds from the frozen configs/sweep.criteria.yaml.
    python experiments/analyse_nogate.py -> results/minimal/NOGATE_REPORT.md"""
import glob, hashlib, json, yaml
C = yaml.safe_load(open("configs/sweep.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/sweep.criteria.sha256").read().strip()
T = C["thresholds"]
R = sorted((json.load(open(f)) for f in glob.glob("results/minimal/e56/main_seed*.json")), key=lambda r: r["seed"])
pres = lambda r: all(p >= T["presence_min"] for p in r["presence"]["mlp"])
ang = lambda r: all(g["angle_deg"] < T["angle_max_deg"] for g in r["rungs"])
clean = lambda r: ang(r) and all(g["gap_ratio"] > T["gap_min"] for g in r["rungs"]) and pres(r)
nc, na = sum(clean(r) for r in R), sum(ang(r) and pres(r) for r in R)
v = "INCOMPLETE" if len(R) < 5 else ("CONFIRMED" if nc <= 1 and na < 4 else "REFUTED")
md = [f"**E56: {v}.** Clean (frozen rule) {nc} of {len(R)}; angle and presence only (gap ignored) {na} of {len(R)}.\n", "| Seed | Angles | Gaps | Min presence |", "|---|---|---|---|"]
md += [f"| {r['seed']} | " + ", ".join(f"{g['angle_deg']:.1f}" for g in r["rungs"]) + " | " + ", ".join(f"{g['gap_ratio']:.1f}" for g in r["rungs"]) + f" | {min(r['presence']['mlp']):.2f} |" for r in R]
open("results/minimal/NOGATE_REPORT.md", "w").write("\n".join(md) + "\n"); print(f"E56: {v}")
