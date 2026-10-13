#!/bin/bash
set -euo pipefail
export MAX_JOBS=8 CMAKE_BUILD_PARALLEL_LEVEL=8 OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
export CMAKE_ARGS="-DFETCHCONTENT_SOURCE_DIR_LIBTORCH=$TASK_DATA/cache/libtorch_download/libtorch"
export CUDA_HOME=/usr/local/cuda-12.6
export PATH="$TASK_DATA/venv/bin:$CUDA_HOME/bin:$PATH"
export TORCH_EXTENSIONS_DIR="$TASK_DATA/cache/torch_extensions" TORCHINDUCTOR_CACHE_DIR="$TASK_DATA/cache/torchinductor" WARP_CACHE_PATH="$TASK_DATA/cache/warp" XDG_CACHE_HOME="$TASK_DATA/cache/xdg" NEQUIP_CACHE_DIR="$TASK_DATA/cache/nequip" TMPDIR="$TASK_DATA/cache/tmp"
mkdir -p "$TORCH_EXTENSIONS_DIR" "$TORCHINDUCTOR_CACHE_DIR" "$WARP_CACHE_PATH" "$XDG_CACHE_HOME" "$NEQUIP_CACHE_DIR"
# All source builds run after the existing GPU lock has been acquired.
python -m pip install --no-deps --no-build-isolation "$TASK_DATA/sources/nequip-27d9d2182da918ab7be0017d8300e53278f5e00e" "$TASK_DATA/sources/nvalchemi-toolkit-ops-32445c5f00e83fccd475589f1a6f5ac9e81e6b02" "$TASK_DATA/sources/OpenEquivariance-62aacc47557e9cdfc6dd370f410b684be1ee0a3f/openequivariance" > "$TASK_DATA/raw/source_build.log" 2>&1
python -m pip check > "$TASK_DATA/raw/pip_check.log" 2>&1
python tools/ai_workload_research/nequip_static_batch_v1/identity_canary.py > "$TASK_DATA/raw/identity_canary.log" 2>&1
nequip-compile "$TASK_DATA/inputs/NequIP-OAM-S-0.1.nequip.zip" "$TASK_DATA/OAM-S.nequip.pt2" --mode aotinductor --target batch --device cuda --modifiers enable_OpenEquivariance --no-tf32 --num-frames 2,8 --num-nodes 128,512 --num-edges 2,65536 --data-path "$TASK_DATA/canary_tensor_container.pt" > "$TASK_DATA/raw/official_compile.log" 2>&1
