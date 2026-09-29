#!/usr/bin/env python3
"""Bounded two-kernel diagnostic for the P1 L1-instance routing fix."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


STAGE = "AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_V1"
REPO = Path("/root/workspace/accel-sim-framework-awma-r101r4-local-service-path-localization-174-v1")
NODE = Path("/root/share/mnt164/huangrulin/awma_r101r4_local_service_path_localization_174_v1")
RUNTIME = Path("/root/awma_r101r4_p1_post_l1_local_service_174_v1_runtime")
BASE = Path("/root/awma_rtx4080_v1_baseline_promotion_v1_runtime/ai_T2_V1_10_80")
FORMAL = Path("/root/share/mnt164/huangrulin/awma_r101r2_context2_memory_service_174_v1/input/traces")
OUT = NODE / "raw/diagnostic/p1_l1_scope_repro"
BINARY = RUNTIME / "bin/unified_accel-sim.out"
CONFIG = REPO / "configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config"
CORE_LIB = RUNTIME / "src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def scalar(text: str, key: str) -> int:
    values = [line.split("=", 1)[1].strip() for line in text.splitlines()
              if line.strip().startswith(key + " =")]
    if not values:
        raise RuntimeError(f"missing scalar: {key}")
    return int(values[-1], 0)


def main() -> int:
    accepted = json.loads((BASE / "command.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    traces = OUT / "traces"
    if traces.exists():
        shutil.rmtree(traces)
    traces.mkdir()
    context = (BASE / "traces/kernel-17039-ctx_0x5ddb6907c160.traceg.xz").resolve()
    measured = (FORMAL / "kernel-3583-ctx_0x43c6c760.traceg.xz").resolve()
    (traces / context.name).symlink_to(context)
    (traces / measured.name).symlink_to(measured)
    (traces / "kernelslist.g").write_text(
        context.name + "\n" + context.name + "\n" + context.name + "\n"
        + measured.name + "\n" + context.name + "\n" + context.name + "\n"
    )
    sidecar = OUT / "transient_l2_runtime.tsv"
    sidecar.write_text("""AWMA_TRANSIENT_L2_RUNTIME_V1
LINE_SIZE 128
EXPECTED_KERNELS 6
EXPECTED_STREAM 0
CONTEXT_END 3
MEASURED_ROI_START 4
MEASURED_ROI_END 6
REGION 0 0x77cac1600000 0x77cac2c00000 1 0
REGION 1 0x77cac2c00000 0x77cac4200000 1 0
REGION 2 0x77ca9aa00000 0x77ca9c000000 1 1
REGION 3 0x77caa2000000 0x77caa3600000 1 0
PRE 1 0 1 1
PRE 2 1 1 1
PRE 3 3 1 1
PRE 4 0 2 1
PRE 5 1 2 1
PRE 6 2 2 1
POST 2 0 1 0
POST 3 1 1 0
POST 3 2 1 0
POST 5 0 2 0
POST 6 1 2 0
POST 6 3 1 0
""")

    command = list(accepted["argv"])
    command[0] = str(BINARY)
    command[2] = str(CONFIG)
    command[4] = str(traces / "kernelslist.g")
    env = os.environ.copy()
    for key in tuple(env):
        if key.startswith("AWMA_") or key.startswith("GPGPUSIM_"):
            env.pop(key)
    env.update({k: str(v) for k, v in accepted["environment"].items()
                if k.startswith("GPGPUSIM_")})
    env.update({
        "GPGPUSIM_ROOT": str(RUNTIME / "src/gpgpu-sim"),
        "GPGPUSIM_POWER_MODEL": str(RUNTIME / "src/gpgpu-sim/src/accelwattch") + "/",
        "GPGPUSIM_VM_COVERAGE_KERNEL_UID": "all",
        "AWMA_TRANSIENT_L2_MODE": "none",
        "AWMA_TRANSIENT_L2_DIAGNOSTICS": "1",
        "AWMA_TRANSIENT_L2_SIDECAR": str(sidecar),
        "AWMA_TRANSIENT_L2_DRAIN": "1",
        "AWMA_R101R2_TRANSIENT_SERVICE_MODE": "none",
        "AWMA_R101R3_SERVICE_MODE": "none",
        "AWMA_R101R4_SERVICE_MODE": "p1_post_l1_local",
        "AWMA_R101R3_DIAGNOSTICS": "0",
        "AWMA_R101R4_DIAGNOSTICS": "1",
    })
    env["LD_LIBRARY_PATH"] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    receipt = {
        "stage": STAGE,
        "role": "ENGINEERING_L1_INSTANCE_SCOPE_REPRO",
        "argv": command,
        "binary_sha256": sha256(BINARY),
        "core_library_sha256": sha256(CORE_LIB / "libcudart.so"),
        "context_trace_sha256": sha256(context),
        "measured_trace_sha256": sha256(measured),
        "sidecar_sha256": sha256(sidecar),
        "environment": {k: env[k] for k in sorted(env)
                        if k.startswith("AWMA_") or k.startswith("GPGPUSIM_")},
    }
    if os.environ.get("AWMA_REUSE_EXISTING") == "1":
        if json.loads((OUT / "command.json").read_text()) != receipt:
            raise RuntimeError("existing diagnostic receipt drift")
        rc = int((OUT / "rc.txt").read_text().strip())
    else:
        (OUT / "command.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        started = time.monotonic()
        with (OUT / "run.log").open("w") as stdout, (OUT / "run.stderr").open("w") as stderr:
            rc = subprocess.run(command, cwd=OUT, env=env, stdout=stdout,
                                stderr=stderr, timeout=3600).returncode
        (OUT / "rc.txt").write_text(f"{rc}\n")
        (OUT / "wall_seconds.txt").write_text(f"{time.monotonic() - started:.6f}\n")
    text = (OUT / "run.log").read_text(errors="strict")
    coverage = [line for line in text.splitlines() if line.startswith("AWMA_VM_COVERAGE ")]
    result = {
        "stage": STAGE,
        "status": "PASS" if (
            rc == 0 and (OUT / "run.stderr").stat().st_size == 0
            and len(coverage) == 6 and "deadlock detected" not in text
            and (scalar(text, "awma_r101r4_p1_admitted_reads")
                 + scalar(text, "awma_r101r4_p1_admitted_writes")) > 0
            and scalar(text, "awma_r101r4_p1_outstanding") == 0
            and scalar(text, "awma_r101r4_p1_duplicate") == 0
            and scalar(text, "awma_transient_l2_terminal_quiescent") == 1
        ) else "FAIL",
        "rc": rc,
        "coverage_kernels": len(coverage),
        "cycles": scalar(text, "gpu_tot_sim_cycle") if rc == 0 else None,
        "p1_admitted_reads": scalar(text, "awma_r101r4_p1_admitted_reads") if rc == 0 else None,
        "p1_admitted_writes": scalar(text, "awma_r101r4_p1_admitted_writes") if rc == 0 else None,
        "max_scheduled_depth": scalar(text, "awma_r101r4_p1_max_scheduled_depth") if rc == 0 else None,
        "max_ready_depth": scalar(text, "awma_r101r4_p1_max_ready_depth") if rc == 0 else None,
        "run_log_sha256": sha256(OUT / "run.log"),
    }
    (OUT / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
