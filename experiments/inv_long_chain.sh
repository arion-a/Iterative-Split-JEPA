#!/bin/bash
# E53 chain: wait for E52 to finish, then 4 runs at 90,000 steps, then score.
cd "$(dirname "$0")/.."
export PATH=/home/user/.venv/bin:$PATH PYTHONPATH=src
until grep -q "inv-ALL-DONE" logs_supervisor/inv_chain.out 2>/dev/null; do sleep 60; done
SP=$PWD/logs_supervisor bash experiments/supervise_b1.sh logs_supervisor/inv_long.txt
python experiments/analyse_inv_long.py
echo inv-long-ALL-DONE
