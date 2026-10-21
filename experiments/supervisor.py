"""Plan supervisor: runs a phase-wise, step-wise plan (plans/*.yaml) in order, verifies every step, retries only transient failures, halts with a
diagnosis on a real failure, resumes where it stopped, and writes one chain entry per completed step.

    python experiments/supervisor.py plans/columbia_full.yaml            # run / resume
    python experiments/supervisor.py plans/columbia_full.yaml --status   # table of steps
    python experiments/supervisor.py plans/columbia_full.yaml --reset S3.1   # mark a step pending again

Plan format: name, state (json path), transient (substrings that mark an infrastructure failure), steps: [{id, phase, desc, run, check?, retries?}].
A step is DONE only if `run` exits 0 AND `check` (if given) exits 0. Exit code of the supervisor: 0 complete, 2 halted on a failed step.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys

import yaml

TAIL = 1500


def load(path):
    plan = yaml.safe_load(open(path))
    state_path = plan["state"]
    state = json.load(open(state_path)) if os.path.exists(state_path) else {"steps": {}}
    return plan, state_path, state


def save(state_path, state):
    os.makedirs(os.path.dirname(state_path) or ".", exist_ok=True)
    json.dump(state, open(state_path, "w"), indent=1)


def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)[-TAIL:]


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def log_chain(plan, step, status, tail):
    if not plan.get("chain"):                                       # only plans that opt in write to the experiment log (tests do not)
        return
    try:
        from isj import explog
        explog.append("note" if status == "done" else "blocked", f"[supervisor {plan['name']}] step {step['id']} {status}: {step['desc']}", stage="V", step=step["id"],
                      outputs={"phase": step.get("phase"), "output_tail": tail[-400:]}, verdict=status)
    except Exception as e:                                           # logging must never mask the step result
        print("chain log failed:", e)


def run(plan, state_path, state, start=None):
    steps = plan["steps"]
    skipping = start is not None
    for step in steps:
        sid = step["id"]
        if skipping and sid != start:
            continue
        skipping = False
        if state["steps"].get(sid, {}).get("status") == "done":
            continue
        attempts = 0
        while True:
            attempts += 1
            print(f"== {sid} (phase {step.get('phase')}) attempt {attempts}: {step['desc']}", flush=True)
            rc, out = sh(step["run"])
            ok = rc == 0
            if ok and step.get("check"):
                crc, cout = sh(step["check"])
                ok, out = crc == 0, out + "\n[check] " + cout
            rec = {"status": "done" if ok else "failed", "attempts": attempts, "rc": rc, "at": now(), "tail": out[-TAIL:]}
            if ok:
                state["steps"][sid] = rec; save(state_path, state); log_chain(plan, step, "done", out)
                print(f"   done {sid}", flush=True)
                break
            transient = any(p in out for p in plan.get("transient", []))
            if transient and attempts <= step.get("retries", 1):
                print(f"   transient failure, retrying {sid}", flush=True)
                continue
            rec["diagnosis"] = "transient failure, retries exhausted" if transient else "real failure: fix the cause, then rerun the supervisor (it resumes here)"
            state["steps"][sid] = rec; save(state_path, state); log_chain(plan, step, "failed", out)
            print(f"   HALT at {sid}: {rec['diagnosis']}\n{out[-800:]}", flush=True)
            return 2
    state["complete"] = now(); save(state_path, state)
    print("PLAN COMPLETE", flush=True)
    return 0


def status(plan, state):
    for s in plan["steps"]:
        st = state["steps"].get(s["id"], {}).get("status", "pending")
        print(f"{s['id']:7s} phase {s.get('phase')} {st:8s} {s['desc']}")
    print("complete:", state.get("complete", "no"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--status", action="store_true"); ap.add_argument("--reset"); ap.add_argument("--from", dest="start")
    a = ap.parse_args()
    plan, sp, st = load(a.plan)
    if a.reset:
        st["steps"].pop(a.reset, None); st.pop("complete", None); save(sp, st)
    if a.status:
        status(plan, st); sys.exit(0)
    sys.exit(run(plan, sp, st, a.start))
