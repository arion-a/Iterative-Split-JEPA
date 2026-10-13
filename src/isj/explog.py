"""Append-only, hash-chained experiment log.

Every entry commits to the previous entry's hash (`prev_hash`) and to its own content
(`hash = sha256(canonical(entry without 'hash'))`). Editing, deleting or reordering any past entry
breaks every later hash, which `verify` detects. A local chain is only *tamper-evident*: to make it
tamper-resistant, the head hash is recorded in git commits that are pushed (the remote is the anchor).

Entries record: what part of the experiment (stage / plan step), how it was implemented, what came
out (metrics + artifact digests), and how that bears on the programme's objectives
(`explog/objectives.yaml`).  The chain is JSONL (`explog/chain.jsonl`); `explog/LOG.md` is a
generated human-readable view.

    python -m isj.explog append --kind note --stage A --step "4.1" --what "..." [--outputs '{"k":1}']
    python -m isj.explog verify
    python -m isj.explog render
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
import subprocess
import sys

DEFAULT_PATH = os.path.join("explog", "chain.jsonl")
GENESIS_PREV = "0" * 64
KINDS = ("genesis", "plan", "implementation", "run", "result", "decision", "amendment",
         "blocked", "note")


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def entry_hash(body: dict) -> str:
    return hashlib.sha256(canonical({k: v for k, v in body.items() if k != "hash"}).encode()).hexdigest()


def file_digest(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def artifacts(paths) -> list[dict]:
    return [{"path": p, "sha256": file_digest(p)} for p in paths]


def git_state() -> dict:
    def run(*a):
        try:
            return subprocess.check_output(["git", *a], text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return None
    return {"commit": run("rev-parse", "--short", "HEAD"),
            "dirty": bool(run("status", "--porcelain"))}


def read_all(path: str = DEFAULT_PATH) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def append(kind: str, what: str, *, stage: str | None = None, step: str | None = None,
           objectives: list[str] | None = None, how: str | None = None,
           outputs: dict | None = None, artifact_paths: list[str] | None = None,
           interpretation: str | None = None, verdict: str | None = None,
           event_time: str | None = None, event_ref: str | None = None,
           retroactive: bool = False, plain: dict | None = None, restates: list[int] | None = None,
           known_stale: list[list] | None = None,
           path: str = DEFAULT_PATH) -> dict:
    """Atomically append one entry (safe for concurrent writers via an exclusive file lock).

    `plain` is the human-facing version shown on the log page:
    {"did": str, "output": [str, ...], "relevance": str, "stage": "A", "verdict": "pass|fail|info|blocked"}.
    `restates` lists earlier chain indices this entry re-explains in plain language.
    """
    assert kind in KINDS, kind
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a+", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            lines = [json.loads(l) for l in f if l.strip()]
            prev = lines[-1] if lines else None
            body = {
                "index": len(lines),
                "prev_hash": prev["hash"] if prev else GENESIS_PREV,
                "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "kind": kind, "stage": stage, "step": step, "objectives": objectives or [],
                "what": what, "how": how, "outputs": outputs or {},
                "artifacts": artifacts(artifact_paths or []),
                "interpretation": interpretation, "verdict": verdict,
                "event_time": event_time, "event_ref": event_ref,
                "retroactive": retroactive, "git": git_state(),
            }
            if plain is not None:
                body["plain"] = plain
            if restates:
                body["restates"] = restates
            if known_stale:
                body["known_stale"] = known_stale   # [[entry_index, path], ...] declared superseded
            body["hash"] = entry_hash(body)
            f.seek(0, os.SEEK_END)
            f.write(canonical(body) + "\n")
            f.flush()
            os.fsync(f.fileno())
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return body


def verify(path: str = DEFAULT_PATH, check_artifacts: bool = True) -> tuple[bool, str]:
    """Check the chain links, every entry hash, and (optionally) that logged artifacts still match."""
    entries = read_all(path)
    prev = GENESIS_PREV
    for i, e in enumerate(entries):
        if e["index"] != i:
            return False, f"entry {i}: index {e['index']} out of sequence"
        if e["prev_hash"] != prev:
            return False, f"entry {i}: prev_hash does not match entry {i - 1}"
        if entry_hash(e) != e["hash"]:
            return False, f"entry {i}: content hash mismatch (entry was altered)"
        prev = e["hash"]
    declared = {(i, p) for e in entries for i, p in e.get("known_stale", [])}
    n_declared = 0
    if check_artifacts:
        for e in entries:
            for a in e["artifacts"]:
                changed = (not os.path.exists(a["path"])) or file_digest(a["path"]) != a["sha256"]
                if changed and (e["index"], a["path"]) in declared:
                    n_declared += 1
                elif changed:
                    return False, f"entry {e['index']}: artifact changed or missing since logged: {a['path']}"
    extra = f", {n_declared} declared-superseded artifact references" if n_declared else ""
    return True, f"{len(entries)} entries, head {prev[:12]}{extra}"


def render(path: str = DEFAULT_PATH, out: str = os.path.join("explog", "LOG.md")) -> str:
    entries = read_all(path)
    ok, msg = verify(path, check_artifacts=False)
    lines = ["# Experiment log (generated from `explog/chain.jsonl`; do not edit)", "",
             f"Chain status at render time: **{'VALID' if ok else 'BROKEN'}** — {msg}", "",
             "Head hash anchors this file; the same hash is quoted in the most recent git commit.", ""]
    for e in entries:
        tag = " (retroactive)" if e["retroactive"] else ""
        lines += [f"## #{e['index']} · {e['kind']}{tag} · stage {e['stage'] or '—'} · plan §{e['step'] or '—'}",
                  f"`{e['hash'][:16]}` ← `{e['prev_hash'][:16]}` · recorded {e['recorded_at']}"
                  + (f" · event {e['event_time']}" if e['event_time'] else "")
                  + (f" · ref {e['event_ref']}" if e['event_ref'] else ""),
                  "", f"**What.** {e['what']}", ""]
        if e["how"]:
            lines += [f"**How.** {e['how']}", ""]
        if e["outputs"]:
            lines += ["**Output.**", "```json", json.dumps(e["outputs"], indent=1, ensure_ascii=False), "```", ""]
        if e["artifacts"]:
            lines += ["**Artifacts.** " + "; ".join(f"`{a['path']}` (sha256 {a['sha256'][:10]})"
                                                    for a in e["artifacts"][:6])
                      + (f" … +{len(e['artifacts']) - 6} more" if len(e["artifacts"]) > 6 else ""), ""]
        if e["interpretation"]:
            lines += [f"**Bearing on objectives {', '.join(e['objectives']) or '—'}.** {e['interpretation']}", ""]
        if e["verdict"]:
            lines += [f"**Verdict.** {e['verdict']}", ""]
        lines.append("---\n")
    text = "\n".join(lines)
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="isj.explog")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("append")
    a.add_argument("--kind", required=True, choices=KINDS)
    a.add_argument("--what", required=True)
    a.add_argument("--stage"); a.add_argument("--step"); a.add_argument("--how")
    a.add_argument("--objectives", nargs="*", default=[])
    a.add_argument("--outputs", default="{}"); a.add_argument("--artifacts", nargs="*", default=[])
    a.add_argument("--interpretation"); a.add_argument("--verdict")
    a.add_argument("--retroactive", action="store_true")
    sub.add_parser("verify"); sub.add_parser("render")
    s = sub.add_parser("show"); s.add_argument("-n", type=int, default=5)
    args = ap.parse_args(argv)
    if args.cmd == "append":
        e = append(args.kind, args.what, stage=args.stage, step=args.step, objectives=args.objectives,
                   how=args.how, outputs=json.loads(args.outputs), artifact_paths=args.artifacts,
                   interpretation=args.interpretation, verdict=args.verdict, retroactive=args.retroactive)
        print(f"#{e['index']} {e['hash'][:16]}")
    elif args.cmd == "verify":
        ok, msg = verify()
        print(("VALID: " if ok else "BROKEN: ") + msg)
        sys.exit(0 if ok else 1)
    elif args.cmd == "render":
        print(render())
    elif args.cmd == "show":
        for e in read_all()[-args.n:]:
            print(f"#{e['index']} {e['hash'][:12]} {e['kind']:14s} {e['stage'] or '-':2s} {e['what'][:90]}")


if __name__ == "__main__":
    main()
