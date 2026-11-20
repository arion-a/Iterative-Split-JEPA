#!/bin/bash
# ManiSkill3 on a rented pod for software-rendered scene videos (same recipe as experiments/robot/pod_pipeline.sh). Log: /workspace/logs/setup_ms.log
set -u; mkdir -p /workspace/logs; exec > /workspace/logs/setup_ms.log 2>&1
echo "[start] $(date +%H:%M:%S) nproc=$(nproc)"
(apt-get update -qq && apt-get install -y -qq libvulkan1 vulkan-tools mesa-vulkan-drivers libgl1 libglib2.0-0 curl) > /workspace/logs/apt.log 2>&1; echo "[apt] done $?"
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh > /workspace/logs/uv.log 2>&1; export PATH=$HOME/.local/bin:$PATH
uv venv --python 3.10 /workspace/venv_ms -q && . /workspace/venv_ms/bin/activate
uv pip install -q "numpy<2" "mani_skill==3.0.1" mplib==0.1.1 h5py pyyaml scipy pillow > /workspace/logs/pip1.log 2>&1; echo "[pip1] done $?"
(uv pip install -q torch --index-url https://download.pytorch.org/whl/cpu || uv pip install -q torch) > /workspace/logs/pip2.log 2>&1; echo "[pip2] done $?"
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json
python -c "import torch, mani_skill, sapien; print('[env] torch', torch.__version__, 'mani_skill', mani_skill.__version__, 'sapien', sapien.__version__)"
echo "[end] $(date +%H:%M:%S)"
