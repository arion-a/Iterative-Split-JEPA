#!/bin/bash
# E55 chain (idempotent, resumable): 40 runs under the supervisor (untrained first, then trained), then score.
cd "$(dirname "$0")/.."
export PATH=/home/user/.venv/bin:$PATH PYTHONPATH=src
SP=$PWD/logs_supervisor bash experiments/supervise_b1.sh logs_supervisor/sweep.txt
python experiments/analyse_sweep.py
echo sweep-ALL-DONE
