#!/bin/bash
# E52 chain (idempotent, resumable): 20 runs under the supervisor, then score.
cd "$(dirname "$0")/.."
export PATH=/home/user/.venv/bin:$PATH PYTHONPATH=src
SP=$PWD/logs_supervisor bash experiments/supervise_b1.sh logs_supervisor/inv.txt
python experiments/analyse_inv.py
echo inv-ALL-DONE
