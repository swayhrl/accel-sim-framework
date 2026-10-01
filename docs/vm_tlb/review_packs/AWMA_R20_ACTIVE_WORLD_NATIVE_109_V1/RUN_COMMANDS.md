# R20 command and lock contract

All commands ran on node109. `+0800` receipt completion times and exact scripts are in `RUN_RECEIPTS.json`; large stdout/stderr are in node164 raw. The three B16 invocations were engineering canaries only; the first two failed during receipt formatting after graph execution, not at physics admission. All actual CUDA initialization/JIT/capture/replay occurred *inside* the same `flock -x -w 3600 /data/c16/locks/c16_gpu_campaign.lock` process, with an asserted `R20_GPU_LOCK_HELD=1`. No GPU process from this Goal remains active.

CPU-only source/asset and environment commands:

```sh
git -C /home/huangrulin/workspace/accel-sim-framework fetch origin hrl/awma-r20-active-world-native-109-v1
git -C /data/c16/awma/r20_active_world_native_v1/source/mujoco_warp checkout --detach 3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5
git -C /data/c16/awma/r20_active_world_native_v1/source/mujoco_menagerie checkout --detach affef0836947b64cc06c4ab1cbf0152835693374
UV_PROJECT_ENVIRONMENT=/data/c16/awma/r20_active_world_native_v1/env UV_CACHE_DIR=/data/c16/awma/r20_active_world_native_v1/cache/uv UV_NO_PROGRESS=1 /data/c16/awma/r20_active_world_native_v1/toolenv/bin/uv sync --locked --no-dev --no-install-project --python /usr/bin/python3
/data/c16/awma/r19_fp8_readiness_20261001/env/bin/python /home/huangrulin/workspace/worktrees/accel-sim-awma-r20-active-world-native-109-v1/util/vm_tlb/awma/r20_active_world/audit_source_assets.py
/data/c16/awma/r20_active_world_native_v1/env/bin/python /home/huangrulin/workspace/worktrees/accel-sim-awma-r20-active-world-native-109-v1/util/vm_tlb/awma/r20_active_world/prepare_scene.py
```

The `uv sync` command executed with working directory `/data/c16/awma/r20_active_world_native_v1/source/mujoco_warp`. CPU-only package/source receipt, offline baseline-difference analysis and publication are separate from GPU commands.

Every GPU command used this exact prefix (one process per bounded job):

```sh
flock -x -w 3600 /data/c16/locks/c16_gpu_campaign.lock env R20_GPU_LOCK_HELD=1 PYTHONPATH=/data/c16/awma/r20_active_world_native_v1/source/mujoco_warp TMPDIR=/data/c16/awma/r20_active_world_native_v1/tmp PYTHONUNBUFFERED=1 /data/c16/awma/r20_active_world_native_v1/env/bin/python
```

The Python argument was exactly one of:

```text
.../util/vm_tlb/awma/r20_active_world/b16_graph_canary.py      (three engineering invocations)
.../util/vm_tlb/awma/r20_active_world/batch_admission.py --batch 1024
.../util/vm_tlb/awma/r20_active_world/ctrl_driver_compare.py
.../util/vm_tlb/awma/r20_active_world/discovery_baseline.py
.../util/vm_tlb/awma/r20_active_world/one_step_diagnostic.py
.../util/vm_tlb/awma/r20_active_world/capacity_pointer_audit.py
```

Here `...` expands to `/home/huangrulin/workspace/worktrees/accel-sim-awma-r20-active-world-native-109-v1`. Each invocation redirected stdout/stderr to its same-named node109 `raw/*.log`, published and hashed on node164. No B512/B256, candidate, formal timing, NSYS, NCU or holdout invocation occurred.
