#!/bin/bash
cd "$(dirname "$0")/.."
export PATH=/home/user/.venv/bin:$PATH PYTHONPATH=src
SP=$PWD/logs_supervisor bash experiments/supervise_b1.sh logs_supervisor/e56.txt
python experiments/analyse_nogate.py
echo nogate-ALL-DONE
