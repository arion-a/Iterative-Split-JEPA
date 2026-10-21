"""Supervisor check for the gap plan: steps done and open per gap (checkboxes in the plan), predictions unedited, log intact.
    python experiments/plan_status.py [docs/PLAN_GAPS_ONE_BY_ONE.md]"""
import re, subprocess, sys

from isj import explog

path = sys.argv[1] if len(sys.argv) > 1 else "docs/PLAN_GAPS_ONE_BY_ONE.md"
section, rows = "(top)", {}
for line in open(path):
    if line.startswith("### ") or line.startswith("## "):
        section = line.strip("# \n")[:70]
    m = re.match(r"\s*- \[( |x)\] (\S+)", line)
    if m:
        d = rows.setdefault(section, [0, 0, []]); d[0 if m.group(1) == "x" else 1] += 1
        if m.group(1) == " ": d[2].append(m.group(2))
print(f"{'Gap / phase':72s} done open  next open step")
for k, (done, op, nxt) in rows.items():
    print(f"{k:72s} {done:4d} {op:4d}  {nxt[0] if nxt else '-'}")
print("total: done", sum(v[0] for v in rows.values()), "open", sum(v[1] for v in rows.values()))
ev = subprocess.run(["python", "experiments/check_results.py", "evidence"], capture_output=True, text=True).stdout.strip()
print(ev[:90]); print("explog.verify:", explog.verify())
