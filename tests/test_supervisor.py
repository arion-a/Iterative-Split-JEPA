"""Supervisor behaviour: done / check-fails-halts / transient retry / resume / reset."""
import json
import subprocess
import sys

import yaml


def _plan(tmp_path, steps):
    p = tmp_path / "plan.yaml"
    yaml.safe_dump({"name": "t", "state": str(tmp_path / "state.json"), "transient": ["TRANSIENT"], "steps": steps}, open(p, "w"))
    return str(p)


def _run(plan, *extra):
    return subprocess.run([sys.executable, "experiments/supervisor.py", plan, *extra], capture_output=True, text=True)


def test_runs_all_steps_and_marks_complete(tmp_path):
    plan = _plan(tmp_path, [{"id": "A", "phase": 0, "desc": "a", "run": "true"}, {"id": "B", "phase": 0, "desc": "b", "run": "true", "check": "true"}])
    r = _run(plan)
    assert r.returncode == 0 and "PLAN COMPLETE" in r.stdout
    assert "complete" in json.load(open(tmp_path / "state.json"))


def test_failed_check_halts_and_later_steps_do_not_run(tmp_path):
    marker = tmp_path / "ran_c"
    plan = _plan(tmp_path, [{"id": "A", "phase": 0, "desc": "a", "run": "true", "check": "false"}, {"id": "C", "phase": 0, "desc": "c", "run": f"touch {marker}"}])
    r = _run(plan)
    assert r.returncode == 2 and not marker.exists()
    assert json.load(open(tmp_path / "state.json"))["steps"]["A"]["status"] == "failed"


def test_transient_failure_is_retried_real_failure_is_not(tmp_path):
    flag = tmp_path / "flag"
    cmd = f"if [ -f {flag} ]; then exit 0; else touch {flag}; echo TRANSIENT; exit 1; fi"
    plan = _plan(tmp_path, [{"id": "A", "phase": 0, "desc": "flaky", "run": cmd, "retries": 1}])
    r = _run(plan)
    assert r.returncode == 0 and json.load(open(tmp_path / "state.json"))["steps"]["A"]["attempts"] == 2
    plan2 = _plan(tmp_path / ".." / tmp_path.name, [{"id": "X", "phase": 0, "desc": "real", "run": "echo boom; exit 3", "retries": 5}])
    # a non-transient failure halts at once, whatever `retries` says
    import os
    os.remove(tmp_path / "state.json")
    r2 = _run(plan2)
    assert r2.returncode == 2 and json.load(open(tmp_path / "state.json"))["steps"]["X"]["attempts"] == 1


def test_resume_skips_done_steps_and_reset_reruns(tmp_path):
    log = tmp_path / "log"
    plan = _plan(tmp_path, [{"id": "A", "phase": 0, "desc": "a", "run": f"echo a >> {log}"}, {"id": "B", "phase": 0, "desc": "b", "run": f"echo b >> {log}"}])
    _run(plan); _run(plan)
    assert open(log).read().split() == ["a", "b"]                 # second invocation re-ran nothing
    _run(plan, "--reset", "B")
    assert open(log).read().split() == ["a", "b", "b"]
