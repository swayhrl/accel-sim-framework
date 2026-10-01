# Execution commands and receipt times

All paths below are on node109. Each complete GPU command was submitted as a single `flock -x -w 3600 /data/c16/locks/c16_gpu_campaign.lock` process; the lock was held until its Python/NSYS child exited. The scripts also assert `R19F1_GPU_LOCK_HELD=1`. Raw stdout/stderr are retained on node164. Receipt times are node-local `+0800`, not a claim about uninterrupted elapsed runtime.

```sh
flock -x -w 3600 /data/c16/locks/c16_gpu_campaign.lock env R19F1_GPU_LOCK_HELD=1 TMPDIR=/data/c16/awma/r19f1_fp8_numeric_decomposition_20261001/tmp PYTHONUNBUFFERED=1 /data/c16/awma/r19_fp8_readiness_20261001/env/bin/python /home/huangrulin/workspace/worktrees/accel-sim-awma-r19f1-fp8-readiness-109-v1/util/vm_tlb/awma/r19f1_fp8/numeric_canary.py
```

Final numeric receipt mtime: `2026-10-01 12:38:22 +0800`. Two earlier invocations of this same command failed on Python object-interface assumptions (`Float8TensorStorage.dtype`, then attempting to pass internal storage directly to public `te.Linear`); their logs are preserved as engineering repairs, not scientific observations or timed arms. The final tracked script uses the documented public `Float8CurrentScalingQuantizer` and exact bit/scale checks.

```sh
flock -x -w 3600 /data/c16/locks/c16_gpu_campaign.lock env R19F1_GPU_LOCK_HELD=1 TMPDIR=/data/c16/awma/r19f1_fp8_numeric_decomposition_20261001/tmp PYTHONUNBUFFERED=1 /usr/local/bin/nsys profile --trace=cuda,nvtx --sample=none --cpuctxsw=none --force-overwrite=true -o /data/c16/awma/r19f1_fp8_numeric_decomposition_20261001/raw/NSYS_R19F1_FP8_CONSUMER_V1 /data/c16/awma/r19_fp8_readiness_20261001/env/bin/python /home/huangrulin/workspace/worktrees/accel-sim-awma-r19f1-fp8-readiness-109-v1/util/vm_tlb/awma/r19f1_fp8/nsys_identity.py
```

Sole NSYS report mtime: `2026-10-01 12:40:23 +0800`. `nsys export --type sqlite` and `parse_nsys.py` were subsequent CPU-only postprocessing, not second captures.

```sh
flock -x -w 3600 /data/c16/locks/c16_gpu_campaign.lock env R19F1_GPU_LOCK_HELD=1 TMPDIR=/data/c16/awma/r19f1_fp8_numeric_decomposition_20261001/tmp PYTHONUNBUFFERED=1 /data/c16/awma/r19_fp8_readiness_20261001/env/bin/python /home/huangrulin/workspace/worktrees/accel-sim-awma-r19f1-fp8-readiness-109-v1/util/vm_tlb/awma/r19f1_fp8/formal_timing.py
```

Sole formal summary mtime: `2026-10-01 12:45:28 +0800`. Formal calls were not profiled. No NCU or further GPU work followed. The common input payload SHA256 is `5ac9e6eb35ec2676926481d563628b80d528dac3dbdbe87bece26d21f4c54b48`; TE source checkout SHA is `5e52befd5262c06289106338c308079d6adb391f`.
