#!/bin/bash
# E54 chain (idempotent, resumable): 20 runs under the supervisor, then score.
cd "$(dirname "$0")/.."
export PATH=/home/user/.venv/bin:$PATH PYTHONPATH=src
SP=$PWD/logs_supervisor bash experiments/supervise_b1.sh logs_supervisor/inv_paper.txt
python experiments/analyse_inv_paper.py
echo inv-paper-ALL-DONE
