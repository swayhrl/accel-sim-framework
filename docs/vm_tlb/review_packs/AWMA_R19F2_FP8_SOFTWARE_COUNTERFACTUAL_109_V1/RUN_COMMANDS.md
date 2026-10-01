# Exact command contract and chronology

All commands ran on node109. Times below are receipt/report file modification times in `+0800`; they are not substituted for measured GPU latency. `PYTHONUNBUFFERED=1`, isolated `TMPDIR`, and the shared lock were used for all actual CUDA/NSYS/JIT. The scripts themselves assert `R19F2_GPU_LOCK_HELD=1`. Large stdout/stderr remain in node164 raw.

CPU-only payload freeze (receipt `2026-10-01 13:21:48 +0800`):

```sh
/data/c16/awma/r19_fp8_readiness_20261001/env/bin/python /home/huangrulin/workspace/worktrees/accel-sim-awma-r19f2-fp8-software-counterfactual-109-v1/util/vm_tlb/awma/r19f2_fp8/freeze_payload.py
```

Stage-A numerical/representation identity (receipt `13:25:24 +0800`):

```sh
flock -x -w 3600 /data/c16/locks/c16_gpu_campaign.lock env R19F2_GPU_LOCK_HELD=1 TMPDIR=/data/c16/awma/r19f2_fp8_software_counterfactual_20261001/tmp PYTHONUNBUFFERED=1 /data/c16/awma/r19_fp8_readiness_20261001/env/bin/python /home/huangrulin/workspace/worktrees/accel-sim-awma-r19f2-fp8-software-counterfactual-109-v1/util/vm_tlb/awma/r19f2_fp8/stage_a_identity.py
```

Sole new NSYS (report `13:28:30 +0800`):

```sh
flock -x -w 3600 /data/c16/locks/c16_gpu_campaign.lock env R19F2_GPU_LOCK_HELD=1 TMPDIR=/data/c16/awma/r19f2_fp8_software_counterfactual_20261001/tmp PYTHONUNBUFFERED=1 /usr/local/bin/nsys profile --trace=cuda,nvtx --sample=none --cpuctxsw=none --force-overwrite=true -o /data/c16/awma/r19f2_fp8_software_counterfactual_20261001/raw/NSYS_R19F2_STAGE_A_CONSUMERS /data/c16/awma/r19_fp8_readiness_20261001/env/bin/python /home/huangrulin/workspace/worktrees/accel-sim-awma-r19f2-fp8-software-counterfactual-109-v1/util/vm_tlb/awma/r19f2_fp8/stage_a_nsys.py
```

NSYS SQLite export and `parse_nsys.py` were CPU-only postprocessing. Stage-A formal timing (summary `13:33:02 +0800`):

```sh
flock -x -w 3600 /data/c16/locks/c16_gpu_campaign.lock env R19F2_GPU_LOCK_HELD=1 TMPDIR=/data/c16/awma/r19f2_fp8_software_counterfactual_20261001/tmp PYTHONUNBUFFERED=1 /data/c16/awma/r19_fp8_readiness_20261001/env/bin/python /home/huangrulin/workspace/worktrees/accel-sim-awma-r19f2-fp8-software-counterfactual-109-v1/util/vm_tlb/awma/r19f2_fp8/stage_a_timing.py
```

Stage-B source audit was CPU/read-only; current-main exact source checkout `a16bce3a647e4277b78c6426e70b9c6d4a1135dd` was not installed. One bounded fused extension build/exactness canary (receipt `13:45:39 +0800`):

```sh
flock -x -w 3600 /data/c16/locks/c16_gpu_campaign.lock env R19F2_GPU_LOCK_HELD=1 TMPDIR=/data/c16/awma/r19f2_fp8_software_counterfactual_20261001/tmp TORCH_EXTENSIONS_DIR=/data/c16/awma/r19f2_fp8_software_counterfactual_20261001/build/cache CUDA_HOME=/usr/local/cuda-12.8 TORCH_CUDA_ARCH_LIST=8.9 MAX_JOBS=2 PYTHONUNBUFFERED=1 /data/c16/awma/r19_fp8_readiness_20261001/env/bin/python /home/huangrulin/workspace/worktrees/accel-sim-awma-r19f2-fp8-software-counterfactual-109-v1/util/vm_tlb/awma/r19f2_fp8/stage_b_canary.py
```

Stage-B formal timing (summary `13:47:58 +0800`):

```sh
flock -x -w 3600 /data/c16/locks/c16_gpu_campaign.lock env R19F2_GPU_LOCK_HELD=1 TMPDIR=/data/c16/awma/r19f2_fp8_software_counterfactual_20261001/tmp TORCH_EXTENSIONS_DIR=/data/c16/awma/r19f2_fp8_software_counterfactual_20261001/build/cache CUDA_HOME=/usr/local/cuda-12.8 TORCH_CUDA_ARCH_LIST=8.9 MAX_JOBS=2 PYTHONUNBUFFERED=1 /data/c16/awma/r19_fp8_readiness_20261001/env/bin/python /home/huangrulin/workspace/worktrees/accel-sim-awma-r19f2-fp8-software-counterfactual-109-v1/util/vm_tlb/awma/r19f2_fp8/stage_b_timing.py
```

Both formal jobs were unprofiled. No additional GPU run, NSYS, NCU, NVBit, SASS inspection or node174 computation followed the Stage-B gate.
