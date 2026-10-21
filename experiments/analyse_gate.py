"""E33 (Gap 2): the rung gate. Rules from configs/gate.criteria.yaml, frozen by hash before any run.
    python experiments/analyse_gate.py -> results/stage_b1_e33/GATE_REPORT.md"""
import glob, hashlib, json
import yaml
from isj.stage_b1 import CRITERIA_KEYS, seed_checks

C = yaml.safe_load(open("configs/gate.criteria.yaml"))
assert hashlib.sha256(json.dumps(C, sort_keys=True).encode()).hexdigest() == open("configs/gate.criteria.sha256").read().strip(), "criteria changed after freezing"
crit = yaml.safe_load(open("configs/stage_b1.yaml"))["criteria"]
load = lambda cell: sorted((json.load(open(f)) for f in glob.glob(f"results/stage_b1_e33/{cell}/main_seed*.json")), key=lambda r: r["seed"])
B, K = load("B"), load("clean")
cb, cc = C["cell_B"], C["clean"]
na = sum(not r["rungs"][0]["applied"] for r in B)
sp = sum(all(seed_checks(r, crit)[k] for k in cb["split_keys"]) for r in B)
okB = len(B) >= 10 and na >= cb["rung1_not_applied_min_runs"] and sp >= cb["rung2_split_min_runs"]
per = []
for r in K:
    c = seed_checks(r, crit)
    c["leakage"] = max(abs(x) for rg in r["rungs"] for k, x in rg["leak_r2"].items() if k in ("rest->own", "own->rest")) < cc["leakage_floor"]
    per.append(c)
passes = {k: sum(p[k] for p in per) for k in CRITERIA_KEYS}
applied = sum(all(rg["applied"] for rg in r["rungs"]) for r in K)
okK = len(K) >= 10 and applied >= cc["rungs_applied_min_runs"] and all(v >= cc["each_b1_criterion_min_runs"] for v in passes.values())
v = "CONFIRMED" if okB and okK else "REFUTED"
md = [f"# E33 (Gap 2): the rung gate; frozen criteria `configs/gate.criteria.yaml`\n",
      f"**E33: {v}.** Cell B ({len(B)} runs): rung 1 not applied on {na} of {len(B)} (needs {cb['rung1_not_applied_min_runs']}); rung 2 split by the existing criteria on {sp} of {len(B)} (needs {cb['rung2_split_min_runs']}; without the gate, E30: 3 of 10). "
      f"Clean control ({len(K)} runs): rungs all applied on {applied} of {len(K)} (needs {cc['rungs_applied_min_runs']}); every B1 criterion on at least {cc['each_b1_criterion_min_runs']} of 10: {'yes' if all(x >= cc['each_b1_criterion_min_runs'] for x in passes.values()) else 'NO'}.\n",
      "| Cell B seed | rung 1 applied | rung 1 gap | rung 2 angle (deg) | rung 2 gap | rung 2 variant R2 | rung 2 split |", "|---|---|---|---|---|---|---|"]
for r in B:
    c = seed_checks(r, crit); g = r["rungs"]
    md.append(f"| {r['seed']} | {'yes' if g[0]['applied'] else 'no'} | {g[0]['gap_ratio']:.1f} | {g[1]['angle_deg']:.1f} | {g[1]['gap_ratio']:.1f} | {g[1]['variant_r2']:.3f} | {'yes' if all(c[k] for k in cb['split_keys']) else 'no'} |")
md += ["", "| Clean criterion | Seeds passing |", "|---|---|"] + [f"| {k} | {n} of {len(K)} |" for k, n in passes.items()]
open("results/stage_b1_e33/GATE_REPORT.md", "w").write("\n".join(md) + "\n"); print("\n".join(md[:3]))
