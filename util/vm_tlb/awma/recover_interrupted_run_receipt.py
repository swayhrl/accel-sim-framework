#!/usr/bin/env python3
"""Recover the sole completed run whose launcher was stopped after child spawn."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


RUN = Path("/root/share/mnt164/huangrulin/awma_ai_gpu_resource_bottleneck_characterization_v1/raw/T1__L2_CAP_2X")


def main() -> int:
    log = RUN / "run.log"
    text = log.read_text(errors="strict")
    required = [
        "gpu_sim_cycle = 619514",
        "gpu_sim_insn = 369131520",
        "gpu_tot_issued_cta = 384",
        "vm_ready_application_duplicate_attempts = 0",
        "AWMA_VM_COVERAGE admissions=7311380 translated=7311380 untranslated=0 unobserved=0 unique=7159808 translated_unique=7159808 untranslated_unique=0",
        "awma_intrawarp_terminal_quiescent = 1",
        "vm_translation_quiescent_invariants_hold = 1",
        "GPGPU-Sim: *** simulation thread exiting ***",
        "GPGPU-Sim: *** exit detected ***",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"cannot recover incomplete run: {missing}")
    command = json.loads((RUN / "command.json").read_text())
    if command.get("target") != "T1" or command.get("arm") != "L2_CAP_2X":
        raise RuntimeError("command identity mismatch")
    if command.get("overrides") != [
        "-gpgpu_cache:dl2", "S:4096:128:16,L:B:m:L:X,A:192:4,32:0,32"
    ]:
        raise RuntimeError("resource override mismatch")
    start = datetime.fromisoformat((RUN / "start_utc.txt").read_text().strip().replace("Z", "+00:00"))
    end = datetime.fromtimestamp(log.stat().st_mtime, timezone.utc)
    if end <= start:
        raise RuntimeError("invalid timestamps")
    (RUN / "rc.txt").write_text("0\n")
    (RUN / "end_utc.txt").write_text(end.strftime("%Y-%m-%dT%H:%M:%SZ") + "\n")
    (RUN / "wall_seconds.txt").write_text(f"{(end - start).total_seconds():.6f}\n")
    receipt = {
        "status": "RECOVERED_COMPLETED_CHILD_AFTER_LAUNCHER_TERMINATION",
        "recovery_basis": required,
        "run": "T1__L2_CAP_2X",
        "return_code": 0,
        "end_time_source": "run.log mtime after terminal markers",
    }
    (RUN / "RECEIPT_RECOVERY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
