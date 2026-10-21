import glob, hashlib, json, sys

import yaml

from isj import explog

plan = yaml.safe_load(open("plans/close_gaps.yaml")); st = json.load(open(plan["state"]))["steps"]
problems = [f"step {s['id']} not done" for s in plan["steps"] if s["id"] != "S4.2" and st.get(s["id"], {}).get("status") != "done"]
cfg = yaml.safe_load(open("configs/gaps.yaml"))
if hashlib.sha256(json.dumps(cfg["criteria"], sort_keys=True).encode()).hexdigest() != open("configs/gaps.criteria.sha256").read().strip():
    problems.append("criteria hash changed since registration")
ev = open("docs/EVIDENCE.md").read()
if ev.find("### G outcome") < ev.find("## G1-G3 gap-closing study (registered") or ev.find("### G outcome") < 0:
    problems.append("G outcome missing or not after its registration")
logged = {a["path"] for e in explog.read_all() for a in e["artifacts"]}
want = [f"results/system_{n}/{s}.json" for n in cfg["systems"] for s in cfg["seeds"]] + [f"results/depth/{s}.json" for s in cfg["seeds"]]
problems += [f"missing or unlogged {p}" for p in want if p not in logged]
print("ALIGNMENT", "OK" if not problems else problems); sys.exit(1 if problems else 0)
