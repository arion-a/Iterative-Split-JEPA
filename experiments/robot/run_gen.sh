#!/bin/bash
# usage: run_gen.sh <proc 0|1|2> <n_procs> ; generates groups g with g % n_procs == proc, 10 groups per block, alternating PickCube / PushCube
SP=/tmp/claude-0/-home-user-Iterative-Split-JEPA/ffc71dc7-784d-5fc4-8b99-fbaa739ed6c2/scratchpad
. $SP/ms310/bin/activate
cd /home/user/Iterative-Split-JEPA
export OMP_NUM_THREADS=1 VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json
P=$1; N=$2
for b in 0 1 2 3 4 5 6 7 8 9; do
  G=""; for g in $(seq $((b*10)) $((b*10+9))); do if [ $((g % N)) -eq $P ]; then G="$G $g"; fi; done
  for T in PickCube PushCube; do python experiments/robot/gen_robot_data.py --task $T --groups $G --out data/robot; done
done
