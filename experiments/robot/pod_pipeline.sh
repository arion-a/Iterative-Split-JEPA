#!/bin/bash
# Fixed-purpose Stage C pipeline for a rented GPU pod. Started once as the container's command; there is NO inbound command channel.
# Progress and results are served read-only over HTTP on port 8000 (directory /work/serve). When finished it writes /work/serve/DONE and exits after a grace period.
set -u
W=/work; mkdir -p $W/serve/logs; cd $W/repo
( python3 -m http.server 8000 --directory $W/serve > $W/http.log 2>&1 & )
exec > $W/serve/pipeline.log 2>&1
log() { echo "[$(date +%H:%M:%S)] $*"; }
log "start; nproc=$(nproc); gpu: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null | head -1)"
(apt-get update -qq && apt-get install -y -qq libvulkan1 vulkan-tools mesa-vulkan-drivers libgl1 libglib2.0-0 curl) > $W/serve/logs/apt.log 2>&1
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh > $W/serve/logs/uv.log 2>&1; export PATH=$HOME/.local/bin:$PATH
uv venv --python 3.10 $W/venv -q && . $W/venv/bin/activate
uv pip install -q "numpy<2" "mani_skill==3.0.1" mplib==0.1.1 h5py pyyaml scipy pillow > $W/serve/logs/pip1.log 2>&1
(uv pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu128 || uv pip install -q torch torchvision) > $W/serve/logs/pip2.log 2>&1
python - <<'PY'
import torch, mani_skill; print("[env] torch", torch.__version__, "cuda", torch.cuda.is_available(), "mani_skill", mani_skill.__version__)
PY
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json OMP_NUM_THREADS=1 LP_NUM_THREADS=1
N=$(nproc); [ $N -gt 24 ] && N=24; GROUPS_PER_TASK=${GROUPS_PER_TASK:-100}
log "generating $GROUPS_PER_TASK groups per task with $N processes (software rendering)"
for i in $(seq 0 $((N-1))); do
  ( for T in PickCube PushCube; do G=""; for g in $(seq 0 $((GROUPS_PER_TASK-1))); do [ $((g % N)) -eq $i ] && G="$G $g"; done
      [ -n "$G" ] && python experiments/robot/gen_robot_data.py --task $T --groups $G --out data/robot; done ) > $W/serve/logs/gen_$i.log 2>&1 &
done; wait
log "data: $(ls data/robot/PickCube | wc -l) PickCube groups, $(ls data/robot/PushCube | wc -l) PushCube groups"
for T in PickCube PushCube; do python experiments/robot/extract_features.py --task $T --threads 4 > $W/serve/logs/feat_$T.log 2>&1; done
log "features done"
mkdir -p results; ln -sfn $W/repo/results $W/serve/results
for T in PickCube PushCube; do for S in 0 1 2; do PYTHONPATH=src python experiments/robot/run_stage_c.py --task $T --split-seed $S --out results/stage_c --head-steps 6000 > $W/serve/logs/stagec_${T}_$S.log 2>&1; log "stage C $T split $S done"; done; done
PYTHONPATH=src python experiments/robot/build_stage_c_report.py > $W/serve/logs/report.log 2>&1
log "ALL DONE"; touch $W/serve/DONE
sleep 7200   # grace period for downloading results; then the container exits and the pod stops billing the GPU
