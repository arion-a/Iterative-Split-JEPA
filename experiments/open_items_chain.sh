#!/bin/bash
# E48-E51 chain (idempotent, resumable). Part A (E48 rate, E50/E51 Stage D) starts now at low priority; part B (E49, 20 runs) waits for the Stage R chain to finish.
cd "$(dirname "$0")/.."
export PATH=/home/user/.venv/bin:$PATH PYTHONPATH=src
SP=$PWD/logs_supervisor SP=$SP bash experiments/supervise_b1.sh logs_supervisor/open_a.txt
until grep -q "stage-r-ALL-DONE" logs_supervisor/stage_r_chain.out 2>/dev/null; do sleep 60; done
SP=$SP bash experiments/supervise_b1.sh logs_supervisor/open_b.txt
python experiments/analyse_open_items.py | head -8
echo open-items-ALL-DONE
