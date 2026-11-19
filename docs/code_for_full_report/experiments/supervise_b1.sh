#!/bin/bash
# Supervisor for B1-style runs. JOBFILE lines: "config out seed [arm]". Runs at most 4 detached runners at a time, is resumable
# (a finished run file is skipped), prints a line when the count of finished runs changes, and ends when every file exists.
#   bash experiments/supervise_b1.sh JOBFILE        (logs go to $SP/logs, default: ./logs_supervisor)
cd "$(dirname "$0")/.."
SP=${SP:-$PWD/logs_supervisor}; mkdir -p "$SP/logs"
export PATH=/home/user/.venv/bin:$PATH PYTHONPATH=src OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
JOBS=$1; TAG=$(basename "$JOBS" .txt)
total=$(grep -c . "$JOBS"); last=""
while true; do
  done_n=0
  while read -r cfg out seed arms; do
    arms=${arms:-main}; f=$out/${arms%% *}_seed$seed.json
    if [ -f "$f" ]; then done_n=$((done_n+1)); continue; fi
    pgrep -f "run_stage_b1.py --config $cfg --out $out --seeds $seed " >/dev/null && continue
    [ "$(pgrep -fc 'python experiments/run_stage_b1.py')" -ge 4 ] && continue
    setsid nohup python experiments/run_stage_b1.py --config "$cfg" --out "$out" --seeds "$seed" --arms $arms --criteria-sha configs/stage_b1.criteria.sha256 > "$SP/logs/${TAG}_$(basename "$out")_$seed.log" 2>&1 &
    sleep 2
  done < "$JOBS"
  cur="$TAG done=$done_n/$total"; [ "$cur" != "$last" ] && { echo "$cur"; last="$cur"; }
  [ "$done_n" -ge "$total" ] && { echo "$TAG-DONE"; exit 0; }
  sleep 30
done
