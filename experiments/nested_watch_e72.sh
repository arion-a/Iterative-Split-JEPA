#!/bin/bash
# Local supervisor of the pod batch: reports progress changes, relaunches the pod supervisor if it died, syncs results here every ~12 min.
cd /home/user/Iterative-Split-JEPA/experiments/robot/paper_baseline
D=/home/user/Iterative-Split-JEPA/results/nested_pod_e72; mkdir -p $D
last=""; fails=0; tick=0
while true; do
  s=$(python3 pod_ctl.py exec "cd /workspace/n; cat status.json 2>/dev/null; echo; ps -eo cmd | grep -c '[n]ested_sup.py'; nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader 2>/dev/null" 2>/dev/null | tr '\n' ' ')
  if [ -z "$s" ]; then fails=$((fails+1)); echo "POD-UNREACHABLE x$fails"; [ $fails -ge 10 ] && { echo "POD-LOST: recreate and resume"; exit 1; }; sleep 60; continue; fi
  fails=0
  sup=$(echo "$s" | grep -o '} [0-9]' | tr -dc '0-9')
  fin=$(echo "$s" | grep -c '"phase": "finished"')
  if [ "$fin" = "1" ]; then echo "BATCH-FINISHED $s"; python3 pod_ctl.py exec "cd /workspace && tar czf res.tgz -C n results status.json logs 2>/dev/null; ls -la res.tgz" >/dev/null 2>&1; python3 pod_ctl.py download res.tgz $D/res.tgz >/dev/null 2>&1; tar xzf $D/res.tgz -C $D; exit 0; fi
  if [ "$sup" = "0" ]; then echo "SUPERVISOR-DEAD: relaunching"; python3 pod_ctl.py exec "cd /workspace/n && nohup bash -c 'PYTHONPATH=src python3 experiments/nested_sup.py e72 >> sup.log 2>&1' >/dev/null 2>&1 &" bg logs/relaunch.log >/dev/null 2>&1; fi
  short=$(echo "$s" | grep -o '"done": [0-9]*\|"phase": "[a-z]*"\|"running": [0-9]*\|"failed": \[[^]]*\]*' | tr '\n' ' ')
  [ "$short" != "$last" ] && { echo "$(date +%H:%M) $short"; last="$short"; }
  tick=$((tick+1))
  if [ $((tick % 12)) -eq 0 ]; then python3 pod_ctl.py exec "cd /workspace && tar czf res.tgz -C n results status.json 2>/dev/null" >/dev/null 2>&1; python3 pod_ctl.py download res.tgz $D/res.tgz >/dev/null 2>&1 && tar xzf $D/res.tgz -C $D 2>/dev/null; echo "synced"; fi
  sleep 60
done
