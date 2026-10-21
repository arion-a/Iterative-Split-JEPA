"""Plan-alignment check for the C2 plan: nothing drifted. Every earlier step done, registration intact, every prediction has an outcome, every raw JSON logged."""
import glob, hashlib, json, sys

import yaml

from isj import explog

plan = yaml.safe_load(open("plans/columbia_full.yaml")); st = json.load(open(plan["state"]))["steps"]
mine = "S4.2"
problems = [f"step {s['id']} not done" for s in plan["steps"] if s["id"] != mine and st.get(s["id"], {}).get("status") != "done"]
cfg = yaml.safe_load(open("configs/columbia_full.yaml"))
if hashlib.sha256(json.dumps(cfg["criteria"], sort_keys=True).encode()).hexdigest() != open("configs/columbia_full.criteria.sha256").read().strip():
    problems.append("criteria hash changed since registration")
ev = open("docs/EVIDENCE.md").read()
if ev.find("## C2 Columbia full experiment (registered") < 0 or ev.find("### C2 outcome") < ev.find("## C2 Columbia full experiment (registered"):
    problems.append("C2 outcome missing or not after its registration")
logged = {a["path"] for e in explog.read_all() for a in e["artifacts"]}
problems += [f"unlogged result {p}" for p in glob.glob("results/columbia_full/[0-9].json") if p not in logged]
if len(glob.glob("results/columbia_full/[0-9].json")) != len(cfg["seeds"]):
    problems.append("not all seeds have results")
print("ALIGNMENT", "OK" if not problems else problems)
sys.exit(1 if problems else 0)
