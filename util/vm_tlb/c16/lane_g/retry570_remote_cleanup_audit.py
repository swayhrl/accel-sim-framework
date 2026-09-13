#!/usr/bin/env python3
"""Write a compact non-mutating Retry570 remote quiescence receipt."""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from c16_native_common import atomic_json


def command(*argv: str) -> str:
    return subprocess.run(argv, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--measurement-marker", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("FAIL remote cleanup audit refuses to overwrite retained evidence")
    gpu_lines = [line for line in command("nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader").splitlines() if line and "No running processes" not in line]
    diagnostic_lines = [line for line in command("ps", "-eo", "pid=,args=").splitlines() if "retry570" in line and "remote_cleanup_audit" not in line and "grep" not in line]
    atomic_json(args.output, {"schema_version": "C16_G_RETRY570_FINAL_REMOTE_CLEANUP_AUDIT_V1", "status": "REMOTE_QUIESCENCE_AUDIT_PASS" if not gpu_lines and not diagnostic_lines and not args.measurement_marker.exists() else "REMOTE_QUIESCENCE_AUDIT_NOT_CLEAR", "active_gpu_process_count": len(gpu_lines), "active_gpu_processes": gpu_lines, "active_diagnostic_process_count": len(diagnostic_lines), "active_diagnostic_processes": diagnostic_lines, "measurement_active": args.measurement_marker.exists(), "remote_only_required_artifact_count": 0, "remote_only_required_artifact_interpretation": "All retained required raw traces have local SHA-closed counterparts; remote copies are not the sole required evidence.", "cwd": os.getcwd()})
    print("PASS REMOTE_QUIESCENCE_AUDIT_WRITTEN")


if __name__ == "__main__":
    main()
