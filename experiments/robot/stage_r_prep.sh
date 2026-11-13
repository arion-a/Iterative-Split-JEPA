#!/bin/bash
# Stage R, step R0: rebuild the robot data on this machine (idempotent, resumable): 100 groups x 8 trajectories per task, then ResNet-50 features.
#   bash experiments/robot/stage_r_prep.sh        (needs /home/user/.venv-ms310 with mani_skill and torchvision, and the Vulkan software renderer)
cd "$(dirname "$0")/../.."
mkdir -p logs_supervisor
for p in 0 1 2 3; do bash experiments/robot/run_gen.sh $p 4 > logs_supervisor/gen_$p.log 2>&1 & done
wait
echo "generation finished"
. ${MS_VENV:-/home/user/.venv-ms310}/bin/activate
for T in PickCube PushCube; do python experiments/robot/extract_features.py --task $T --threads 2 > logs_supervisor/feat_$T.log 2>&1 & done
wait
echo "features finished"
echo stage-r-prep-DONE
