#!/bin/bash
# Supervisor for the Stage R head runs. JOBFILE lines: "task split_seed arm" (arm = baseline | treated). At most 4 at a time, detached, resumable.
#   bash experiments/robot/supervise_stage_r.sh JOBFILE
cd "$(dirname "$0")/../.."
mkdir -p logs_supervisor
. ${MS_VENV:-/home/user/.venv-ms310}/bin/activate; export PYTHONPATH=src OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
JOBS=$1; TAG=$(basename "$JOBS" .txt); total=$(grep -c . "$JOBS"); last=""
while true; do
  done_n=0
  while read -r task seed arm; do
    out=results/stage_r/$arm; f=$out/$task/split$seed.json
    if [ -f "$f" ]; then done_n=$((done_n+1)); continue; fi
    pgrep -f "run_stage_c.py --task $task --split-seed $seed .*--out $out" > /dev/null && continue
    [ "$(pgrep -fc 'python experiments/robot/run_stage_c.py')" -ge 4 ] && continue
    if [ "$task" = PickCube ]; then d1=64; pca=128; else d1=128; pca=256; fi
    extra=""; [ "$arm" = treated ] && extra="--inv-weight 1.0 --whiten-weight 1.0"
    setsid nohup python experiments/robot/run_stage_c.py --task $task --split-seed $seed --fixed-d1 $d1 --pca $pca --holdout-groups 20 $extra --out $out > logs_supervisor/${TAG}_${arm}_${task}_$seed.log 2>&1 &
    sleep 2
  done < "$JOBS"
  cur="$TAG done=$done_n/$total"; [ "$cur" != "$last" ] && { echo "$cur"; last="$cur"; }
  [ "$done_n" -ge "$total" ] && { echo "$TAG-DONE"; exit 0; }
  sleep 60
done
