"""Phase gate for stage V: one command, minimal checks. Exit code 0 only if every check passes.

    python experiments/audit_stage_v.py [--no-tests]

1. test suite  2. chain links and artifact digests  3. every stage-V config's criteria hash  4. every result JSON is referenced by a chain entry
5. every registered prediction ID in the roadmap registry has an outcome line in docs/EVIDENCE.md
"""
from __future__ import annotations

import glob
import hashlib
import json
import re
import subprocess
import sys

import yaml

from isj import explog

ok = True


def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail else ""))


if "--no-tests" not in sys.argv:
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x"], capture_output=True, text=True)
    check("test suite", r.returncode == 0, r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr[-200:])

v, msg = explog.verify()
check("chain links + artifact digests", v, msg)

for cfg in [f"configs/{n}.yaml" for n in ("handshake", "hier", "followup", "e36", "scaling", "live", "columbia", "columbia_controls", "columbia_full", "columbia_confound", "gaps", "other_data", "nus", "nus_t") if glob.glob(f"configs/{n}.yaml")]:
    sha = cfg.replace(".yaml", ".criteria.sha256")
    c = yaml.safe_load(open(cfg))
    if "criteria" in c:
        try:
            want = open(sha).read().strip()
        except FileNotFoundError:
            check(f"criteria hash {cfg}", False, "hash file missing")
            continue
        got = hashlib.sha256(json.dumps(c["criteria"], sort_keys=True).encode()).hexdigest()
        check(f"criteria hash {cfg}", got == want)

logged = {a["path"] for e in explog.read_all() for a in e["artifacts"]}
raw = [p for d in ("hf_pendulum", "robot", "system_single_pendulum", "system_elastic_pendulum", "depth", "handshake/main", "hier/ladder", "hier/shuffled", "followup", "e36", "real", "scaling", "live", "columbia", "columbia_controls", "columbia_full", "columbia_confound", "nus", "nus_t/S0", "nus_t/SH", "nus_t/SL", "nus_t/C0", "nus_t/CL") for p in glob.glob(f"results/{d}/*.json") if not p.endswith("supervisor_state.json")]
missing = [p for p in raw if p not in logged]
check("every raw result JSON is in the chain", not missing, str(missing[:3]))

ev = open("docs/EVIDENCE.md").read()
for ident, marker in (("E31c′", "E31c′: CONFIRMED"), ("E31d", "E31d: REFUTED"), ("E35", "E35: REFUTED"), ("F1", "F1 outcome"), ("E36", "E36 outcome"), ("B1", "B1 outcome"), ("C1", "C1 outcome"), ("C1b", "C1b outcome")):
    check(f"EVIDENCE has an outcome for {ident}", marker in ev)
if glob.glob("results/columbia_full/[0-9].json"):                    # C2 outcome is required once C2 has results
    check("EVIDENCE has an outcome for C2", "C2 outcome" in ev)
if glob.glob("results/depth/[0-9].json"):
    check("EVIDENCE has an outcome for the G study", "G outcome" in ev)
if glob.glob("results/robot/[0-9].json"):
    check("EVIDENCE has an outcome for H1/R1", "H1/R1 outcome" in ev)
if glob.glob("results/nus/[0-9].json"):
    check("EVIDENCE has an outcome for N", "N outcome" in ev)
if glob.glob("results/nus_t/*/[0-9].json"):
    check("EVIDENCE has an outcome for T1-T3", "T outcome" in ev)
if glob.glob("results/columbia_confound/[0-9].json"):
    check("EVIDENCE has an outcome for C3", "C3 outcome" in ev)

print("AUDIT", "PASSED" if ok else "FAILED")
sys.exit(0 if ok else 1)
