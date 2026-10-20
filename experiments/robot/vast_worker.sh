#!/bin/bash
# Stage C (E24) worker for a rented GPU box (Vast.ai or any Linux box with an NVIDIA GPU). Run it IN THE INSTANCE'S TERMINAL:
#     export GITHUB_TOKEN=<fine-grained token, repo Contents: read+write>      # type it there; never paste it into any chat
#     bash vast_worker.sh                       # or: curl-free: git clone the repo first, then run this file
# Does: system libs + Python 3.10 env (ManiSkill3, mplib, CUDA PyTorch), clones the branch, generates the robot data (many processes),
# extracts frozen ResNet-50 features on the GPU, runs Stage C for 3 split seeds on both tasks, and pushes ONLY small result files
# (JSON, report, figure, logs) to the branch  claude/vast-results . Big arrays stay on the box. Safe to re-run: every stage resumes.
set -u
REPO_PATH="arion-a/Iterative-Split-JEPA"; BRANCH="claude/blissful-turing-7cdrv0"; OUTBR="claude/vast-results"
GROUPS_PER_TASK=${GROUPS_PER_TASK:-100}; NPROC=${NPROC:-$(( $(nproc) > 32 ? 32 : $(nproc) ))}
: "${GITHUB_TOKEN:?export GITHUB_TOKEN first (in this terminal only)}"
W=$HOME/isj_work; mkdir -p $W && cd $W
log() { echo "[$(date +%H:%M:%S)] $*"; }
# ---- 1. system libraries (Vulkan for rendering; software fallback if the NVIDIA Vulkan driver is not exposed)
if ! command -v vulkaninfo >/dev/null; then (apt-get update -qq && apt-get install -y -qq git curl libvulkan1 vulkan-tools mesa-vulkan-drivers libgl1 libglib2.0-0) >/dev/null 2>&1; fi
ICD=""; ls /usr/share/vulkan/icd.d/nvidia_icd.json >/dev/null 2>&1 && ICD=/usr/share/vulkan/icd.d/nvidia_icd.json
if [ -z "$ICD" ] || ! VK_ICD_FILENAMES=$ICD vulkaninfo --summary 2>/dev/null | grep -qi nvidia; then ICD=/usr/share/vulkan/icd.d/lvp_icd.json; log "NVIDIA Vulkan not available: rendering on CPU (lavapipe), $NPROC parallel processes"; else log "rendering on the NVIDIA GPU via Vulkan"; fi
export VK_ICD_FILENAMES=$ICD OMP_NUM_THREADS=1
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null | head -1 | sed 's/^/[gpu] /'
# ---- 2. Python 3.10 env
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; export PATH=$HOME/.local/bin:$PATH
[ -d $W/venv ] || { uv venv --python 3.10 $W/venv -q; . $W/venv/bin/activate; uv pip install -q "numpy<2" "mani_skill==3.0.1" mplib==0.1.1 h5py pyyaml scipy pillow; uv pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu128 || uv pip install -q torch torchvision; }
. $W/venv/bin/activate
# the box image's own CUDA/NCCL libraries on LD_LIBRARY_PATH shadow the ones torch ships (ImportError: undefined symbol ncclCommResume)
export LD_LIBRARY_PATH=
# ---- 3. code (private repo: token used only in the remote URL, never printed)
[ -d repo ] || git clone -q https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO_PATH}.git repo
cd repo && git fetch -q origin $BRANCH && git checkout -q $BRANCH && git pull -q origin $BRANCH && git config user.email "worker@vast" && git config user.name "vast worker"
python - <<'PY'
import torch; print("[torch]", torch.__version__, "cuda available:", torch.cuda.is_available())
PY
mkdir -p logs_vast
# ---- 4. data generation, many processes (groups g % NPROC == i, PickCube and PushCube alternately)
log "generating $GROUPS_PER_TASK groups per task with $NPROC processes"
for i in $(seq 0 $((NPROC-1))); do
  ( for T in PickCube PushCube; do G=""; for g in $(seq 0 $((GROUPS_PER_TASK-1))); do [ $((g % NPROC)) -eq $i ] && G="$G $g"; done
      [ -n "$G" ] && python experiments/robot/gen_robot_data.py --task $T --groups $G --out data/robot; done ) > logs_vast/gen_$i.log 2>&1 &
done; wait
log "data: $(ls data/robot/PickCube | wc -l) PickCube groups, $(ls data/robot/PushCube | wc -l) PushCube groups"
# ---- 5. features on the GPU, then Stage C (head trained on the GPU is not needed: it is a small MLP; CPU is fine)
for T in PickCube PushCube; do python experiments/robot/extract_features.py --task $T --threads 4 > logs_vast/feat_$T.log 2>&1; done
log "features done"
for T in PickCube PushCube; do for S in 0 1 2; do PYTHONPATH=src python experiments/robot/run_stage_c.py --task $T --split-seed $S --out results/stage_c --head-steps 6000 > logs_vast/stagec_${T}_$S.log 2>&1; done; done
PYTHONPATH=src python experiments/robot/build_stage_c_report.py > logs_vast/report.log 2>&1
# ---- 6. push only small files
git checkout -q -B $OUTBR; git add -f results/stage_c logs_vast 2>/dev/null; git commit -qm "Stage C results from the GPU box (groups: Pick $(ls data/robot/PickCube | wc -l), Push $(ls data/robot/PushCube | wc -l))" && git push -q -f origin $OUTBR && log "pushed results to branch $OUTBR" || log "nothing to push or push failed (check the token's permissions)"
