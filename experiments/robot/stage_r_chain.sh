#!/bin/bash
# Stage R chain (idempotent, resumable): wait for the data rebuild (R0), run the 12 head runs (E46 baseline, E47 treated) under the supervisor, then score.
cd "$(dirname "$0")/../.."
until grep -q "stage-r-prep-DONE" logs_supervisor/stage_r_prep.out 2>/dev/null; do sleep 30; done
bash experiments/robot/supervise_stage_r.sh experiments/robot/stage_r_jobs.txt
. ${MS_VENV:-/home/user/.venv-ms310}/bin/activate; export PYTHONPATH=src
python experiments/robot/analyse_stage_r.py | head -8
echo stage-r-ALL-DONE
