#!/usr/bin/env bash
set -euo pipefail
root=/data/c16/awma/r101_l2_lifetime_control_v1r1_20260927
worktree=/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-l2-lifetime-control-v1r1
python=/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927/env/bin/python
script="${1:?script basename required}"
shift
case "$script" in
    semantic.py|timing.py|profile_graph.py|ncu_target.py|arena_control.py|arena_timing.py|arena_ncu_target.py|holdout.py) ;;
    *) echo "unregistered R101R1 GPU script: $script" >&2; exit 2 ;;
esac
export HF_HOME="$root/cache/hf"
export TRITON_CACHE_DIR="$root/cache/triton"
export CUDA_CACHE_PATH="$root/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$root/cache/inductor"
export XDG_CACHE_HOME="$root/cache/xdg"
export TMPDIR="$root/tmp"
export PYTHONUNBUFFERED=1
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -x 9
"$python" "$worktree/util/vm_tlb/awma/r101_l2_lifetime_control_v1r1/$script" "$@"
