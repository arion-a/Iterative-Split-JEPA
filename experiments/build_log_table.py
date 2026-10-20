"""Render docs/EXPERIMENT_TABLE.md: one row per chain entry that is a plan, result, decision or amendment (runs are summarised by the
result entries that analyse them). Columns: idea (objective), what happened, record (chain hash + artifacts), contribution
(verdict + interpretation), relevance (plain-language relevance when the entry has one). Everything comes from explog/chain.jsonl,
so every row is covered by the chain's fingerprints.

    python experiments/build_log_table.py
"""
import json

import yaml

from isj import explog

KINDS = ("plan", "result", "decision", "amendment", "blocked")


def cell(x, n):
    x = " ".join(str(x or "").split()).replace("|", "/")
    return x if len(x) <= n else x[: n - 1] + "…"


def main():
    chain = [json.loads(l) for l in open(explog.DEFAULT_PATH)]
    obj = yaml.safe_load(open("explog/objectives.yaml"))
    ok = explog.verify()[0]
    rows = [e for e in chain if e["kind"] in KINDS]
    out = ["# Experiment table (generated from `explog/chain.jsonl`; do not edit)", "",
           f"Chain: {len(chain)} entries, head `{chain[-1]['hash'][:12]}`, verify = {ok}. Rows: {len(rows)} (plans, results, decisions, amendments, blockers).", "",
           "| # | Date | Kind | Idea (objective) | What happened | Record (hash; artifacts) | Contribution (verdict; reading) | Relevance |",
           "|---|---|---|---|---|---|---|---|"]
    for e in rows:
        ids = e.get("objectives") or []
        idea = "; ".join(f"{i} {obj.get(i, {}).get('name', '')}" for i in ids)
        pl = e.get("plain") or {}
        out.append("| {} | {} | {} | {} | {} | `{}`; {} | {} | {} |".format(
            e["index"], (e.get("recorded_at") or "")[:10], e["kind"], cell(idea, 60), cell(e["what"], 220), e["hash"][:12],
            len(e.get("artifacts") or []), cell(" ".join(filter(None, [e.get("verdict"), "-", e.get("interpretation")])), 260),
            cell(pl.get("relevance"), 160)))
    open("docs/EXPERIMENT_TABLE.md", "w").write("\n".join(out) + "\n")
    print(f"wrote docs/EXPERIMENT_TABLE.md ({len(rows)} rows), verify = {ok}")


if __name__ == "__main__":
    main()
