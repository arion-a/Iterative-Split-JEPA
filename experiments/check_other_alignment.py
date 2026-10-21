import glob, hashlib, json, sys

import yaml

from isj import explog

plan = yaml.safe_load(open("plans/other_data.yaml")); st = json.load(open(plan["state"]))["steps"]
problems = [f"step {s['id']} not done" for s in plan["steps"] if s["id"] != "S4.2" and st.get(s["id"], {}).get("status") != "done"]
cfg = yaml.safe_load(open("configs/other_data.yaml"))
if hashlib.sha256(json.dumps(cfg["criteria"], sort_keys=True).encode()).hexdigest() != open("configs/other_data.criteria.sha256").read().strip():
    problems.append("criteria hash changed since registration")
ev = open("docs/EVIDENCE.md").read()
if ev.find("### H1/R1 outcome") < 0 or ev.find("### H1/R1 outcome") < ev.find("## H1 and R1: other controlled data (registered"):
    problems.append("outcome missing or not after registration")
logged = {a["path"] for e in explog.read_all() for a in e["artifacts"]}
problems += [f"missing or unlogged {p}" for p in [f"results/{d}/{s}.json" for d in ("hf_pendulum", "robot") for s in cfg["seeds"]] if p not in logged]
print("ALIGNMENT", "OK" if not problems else problems); sys.exit(1 if problems else 0)
