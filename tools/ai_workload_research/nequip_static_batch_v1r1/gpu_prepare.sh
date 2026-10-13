#!/bin/bash
set -euo pipefail
export TORCHINDUCTOR_COMPILE_THREADS=8
export CUDA_HOME=/usr/local/cuda-12.6 PATH="$TASK_DATA/venv/bin:/usr/local/cuda-12.6/bin:$PATH"
export PIP_CACHE_DIR="$TASK_DATA/cache/pip" CMAKE_ARGS="-DFETCHCONTENT_SOURCE_DIR_LIBTORCH=$OLD_TASK_DATA/cache/libtorch_download/libtorch"
export TORCH_EXTENSIONS_DIR="$TASK_DATA/cache/torch_extensions" TORCHINDUCTOR_CACHE_DIR="$TASK_DATA/cache/torchinductor" WARP_CACHE_PATH="$TASK_DATA/cache/warp" XDG_CACHE_HOME="$TASK_DATA/cache/xdg" NEQUIP_CACHE_DIR="$TASK_DATA/cache/nequip" TMPDIR="$TASK_DATA/cache/tmp"
mkdir -p "$TORCH_EXTENSIONS_DIR" "$TORCHINDUCTOR_CACHE_DIR" "$WARP_CACHE_PATH" "$XDG_CACHE_HOME" "$NEQUIP_CACHE_DIR"
# All three original approved source builds are under the existing GPU shared lock.
if [ "${V1R1_RESUME_INSTALLED_CORE:-0}" != 1 ]; then
python -m pip install --no-deps --no-build-isolation --no-index "$TASK_DATA/sources/nequip-27d9d2182da918ab7be0017d8300e53278f5e00e" "$TASK_DATA/sources/nvalchemi-toolkit-ops-32445c5f00e83fccd475589f1a6f5ac9e81e6b02" "$TASK_DATA/sources/OpenEquivariance-62aacc47557e9cdfc6dd370f410b684be1ee0a3f/openequivariance" --report "$TASK_DATA/raw/CORE_SOURCE_INSTALL_REPORT.json" > "$TASK_DATA/raw/CORE_SOURCE_BUILD.log" 2>&1
python -m pip check > "$TASK_DATA/raw/FULL_ENV_PIP_CHECK.log" 2>&1
else
 python -m pip check > "$TASK_DATA/raw/FULL_ENV_PIP_CHECK_RESUME.log" 2>&1
fi
python tools/ai_workload_research/nequip_static_batch_v1r1/identity_canary.py > "$TASK_DATA/raw/IDENTITY_CANARY.log" 2>&1
nequip-compile "$TASK_DATA/inputs/NequIP-OAM-S-0.1.nequip.zip" "$TASK_DATA/OAM-S.nequip.pt2" --mode aotinductor --target batch --device cuda --modifiers enable_OpenEquivariance --no-tf32 --num-frames 2,8 --num-nodes 128,512 --num-edges 2,65536 --data-path "$TASK_DATA/canary_tensor_container.pt" > "$TASK_DATA/raw/OFFICIAL_COMPILE.log" 2>&1
python tools/ai_workload_research/nequip_static_batch_v1r1/observe.py compiled_canary > "$TASK_DATA/raw/COMPILED_CANARY.log" 2>&1
