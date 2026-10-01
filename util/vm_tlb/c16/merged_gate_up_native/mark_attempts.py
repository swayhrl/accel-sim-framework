#!/usr/bin/env python3
import json
from pathlib import Path

root = Path("/data/c16/merged_gate_up_native_v1/raw")
attempts = [
    ("C16R_merged-gate-up-native-strong-baseline_20261001T030535Z", 1,
     "ABORTED_ENGINEERING_FRONTEND_PREFILL_OUTPUT_ASSUMPTION", "no B2 result JSON; formal not started"),
    ("C16R_merged-gate-up-native-strong-baseline_20261001T030819Z", 2,
     "ABORTED_ENGINEERING_BATCH_QUEUE_PREFILL_DECODE_BOUNDARY", "trace established inactive execute counts [2048,1]; formal not started"),
    ("C16R_merged-gate-up-native-strong-baseline_20261001T031026Z", 3,
     "ABORTED_ENGINEERING_TENSOR_SNAPSHOT_ALIAS", "detach-only snapshots were vulnerable to later in-place runtime mutation; superseded by canary-only clones"),
]
for name, attempt, status, reason in attempts:
    path = root / name
    receipt = json.loads((path / "GPU_LOCK_RECEIPT.json").read_text())
    value = {"status": status, "attempt": attempt, "reason": reason,
             "scientific_result": "NONE", "formal_started": False,
             "gpu_lock_released": receipt["released"], "gpu_wall_seconds": receipt["gpu_wall_seconds"]}
    (path / "ABORTED_ENGINEERING.json").write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
