#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


STAGE = "AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_V1"
BASE = Path("/root/awma_rtx4080_v1_baseline_promotion_v1_runtime/ai_T2_V1_10_80")
REPO = Path(
    "/root/workspace/accel-sim-framework-awma-r101r2-context2-memory-service-174-v1"
)
RUNTIME = Path("/root/awma_r101r2_context2_memory_service_174_v1_runtime")
RAW = Path(
    "/root/share/mnt164/huangrulin/"
    "awma_r101r2_context2_memory_service_174_v1/raw/smoke"
)
BINARY = RUNTIME / "bin/unified_accel-sim.out"
CORE_LIB = RUNTIME / "src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release"
SIDECAR = REPO / (
    "util/vm_tlb/awma/r101_transient_l2_arch_v1/"
    "directed_no_overlap_runtime.tsv"
)
POSITIVE_SIDECAR = REPO / (
    "util/vm_tlb/awma/r101r2_context2_memory_service_v1/"
    "directed_positive_runtime.tsv"
)
CONFIG = REPO / "configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config"
EXPECTED = {
    "cycles": 93079, "instructions": 43357696, "ctas": 1216,
    "unique": 411008,
}
ARMS = {
    "default_off": None,
    "explicit_none": "none",
    "oracle_positive": "oracle_1c",
}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def scalar(text: str, key: str) -> int:
    values = []
    for line in text.splitlines():
        if line.strip().startswith(key + " ="):
            values.append(int(line.split("=", 1)[1].strip()))
    if not values:
        raise RuntimeError(f"missing scalar {key}")
    return values[-1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("arm", choices=tuple(ARMS))
    args = parser.parse_args()
    service_mode = ARMS[args.arm]
    accepted = json.loads((BASE / "command.json").read_text())
    if sha(Path(accepted["argv"][2])) != (
        "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8"
    ):
        raise RuntimeError("accepted config drift")
    output = RAW / args.arm
    output.mkdir(parents=True, exist_ok=True)
    traces = output / "traces"
    if traces.exists():
        shutil.rmtree(traces)
    traces.mkdir()
    payload = (
        BASE / "traces/kernel-17039-ctx_0x5ddb6907c160.traceg.xz"
    ).resolve()
    (traces / payload.name).symlink_to(payload)
    positive = args.arm == "oracle_positive"
    repetitions = 6 if positive else 1
    (traces / "kernelslist.g").write_text(
        "".join(payload.name + "\n" for _ in range(repetitions))
    )

    command = list(accepted["argv"])
    command[0] = str(BINARY)
    command[2] = str(CONFIG)
    command[4] = str(traces / "kernelslist.g")
    env = os.environ.copy()
    for key in tuple(env):
        if key.startswith("AWMA_") or key.startswith("GPGPUSIM_"):
            env.pop(key)
    env.update({
        key: str(value) for key, value in accepted["environment"].items()
        if key.startswith("GPGPUSIM_")
    })
    env["GPGPUSIM_ROOT"] = str(RUNTIME / "src/gpgpu-sim")
    env["GPGPUSIM_POWER_MODEL"] = str(
        RUNTIME / "src/gpgpu-sim/src/accelwattch"
    ) + "/"
    env["GPGPUSIM_VM_COVERAGE_KERNEL_UID"] = "all"
    env["LD_LIBRARY_PATH"] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    selected_sidecar = POSITIVE_SIDECAR if positive else SIDECAR
    if service_mode is not None:
        env.update({
            "AWMA_TRANSIENT_L2_MODE": "none",
            "AWMA_TRANSIENT_L2_DIAGNOSTICS": "1",
            "AWMA_TRANSIENT_L2_SIDECAR": str(selected_sidecar),
            "AWMA_TRANSIENT_L2_DRAIN": "1",
            "AWMA_R101R2_TRANSIENT_SERVICE_MODE": service_mode,
        })
    receipt = {
        "stage": STAGE,
        "arm": args.arm,
        "argv": command,
        "binary_sha256": sha(BINARY),
        "core_library_sha256": sha(CORE_LIB / "libcudart.so"),
        "config_sha256": sha(CONFIG),
        "trace_sha256": sha(payload),
        "sidecar_sha256": sha(selected_sidecar) if service_mode is not None else None,
        "environment": {
            key: env[key] for key in sorted(env)
            if key.startswith("AWMA_") or key.startswith("GPGPUSIM_")
        },
    }
    (output / "command.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    (output / "start_utc.txt").write_text(
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + "\n"
    )
    started = time.monotonic()
    with (output / "run.log").open("w") as stdout,             (output / "run.stderr").open("w") as stderr:
        rc = subprocess.run(
            command, cwd=output, env=env, stdout=stdout, stderr=stderr,
            timeout=7200,
        ).returncode
    (output / "rc.txt").write_text(f"{rc}\n")
    (output / "wall_seconds.txt").write_text(
        f"{time.monotonic() - started:.6f}\n"
    )
    text = (output / "run.log").read_text(errors="strict")
    coverage = [
        line for line in text.splitlines()
        if line.startswith("AWMA_VM_COVERAGE ")
    ]
    passed = (
        rc == 0 and (output / "run.stderr").stat().st_size == 0
        and len(coverage) == repetitions
        and all("untranslated=0" in line and "unobserved=0" in line
                and f"unique={EXPECTED['unique']}" in line
                for line in coverage)
    )
    if not positive:
        passed = (
            passed
            and scalar(text, "gpu_tot_sim_cycle") == EXPECTED["cycles"]
            and scalar(text, "gpu_tot_sim_insn") == EXPECTED["instructions"]
            and scalar(text, "gpu_tot_issued_cta") == EXPECTED["ctas"]
        )
    else:
        qualified_reads = scalar(text, "awma_r101r2_service_qualified_reads")
        qualified_writes = scalar(text, "awma_r101r2_service_qualified_writes")
        scheduled = scalar(text, "awma_r101r2_service_scheduled")
        ready = scalar(text, "awma_r101r2_service_one_cycle_ready")
        retired = (
            scalar(text, "awma_r101r2_service_retired_reads")
            + scalar(text, "awma_r101r2_service_retired_writes")
        )
        passed = (
            passed
            and scalar(text, "gpu_tot_sim_insn")
                == EXPECTED["instructions"] * repetitions
            and scalar(text, "gpu_tot_issued_cta")
                == EXPECTED["ctas"] * repetitions
            and qualified_reads > 0 and qualified_writes > 0
            and scalar(text, "awma_r101r2_service_qualified_ldg_reads") > 0
            and scalar(text, "awma_r101r2_service_qualified_ldgsts_reads") == 0
            and qualified_reads + qualified_writes == scheduled == ready == retired
            and scalar(text, "awma_r101r2_service_inactive_intersections") > 0
            and scalar(text, "awma_r101r2_service_atomic_fail_closed") == 0
            and scalar(text, "awma_r101r2_service_unsupported_fail_closed") == 0
            and scalar(text, "awma_r101r2_service_partial_skips") == 0
            and scalar(text, "awma_r101r2_service_multi_region_skips") == 0
            and scalar(text, "awma_r101r2_service_invalid_range_skips") == 0
            and scalar(text, "awma_r101r2_service_duplicate_completions") == 0
            and scalar(text, "awma_r101r2_service_latency_violations") == 0
            and scalar(text, "awma_r101r2_service_stale_token_violations") == 0
            and scalar(text, "awma_r101r2_service_outstanding") == 0
            and scalar(text, "awma_r101r2_service_semantics_qualified") == 1
            and scalar(text, "awma_r101r2_context_end_cycle_valid") == 1
            and scalar(text, "awma_r101r2_roi_end_cycle_valid") == 1
            and scalar(text, "awma_r101r2_roi_cycles") > 0
            and scalar(text, "L2_total_cache_accesses") > 0
        )
    if service_mode is None:
        passed = (
            passed
            and "awma_r101r2_transient_service_mode" not in text
            and "awma_transient_l2_mode" not in text
        )
    elif not positive:
        passed = (
            passed
            and "awma_transient_l2_mode = none" in text
            and "awma_r101r2_transient_service_mode = none" in text
            and "awma_r101r2_service_qualified_reads = 0" in text
            and "awma_r101r2_service_qualified_writes = 0" in text
            and "awma_r101r2_service_outstanding = 0" in text
            and "awma_r101r2_service_duplicate_completions = 0" in text
            and "awma_transient_l2_terminal_quiescent = 1" in text
        )
    else:
        passed = (
            passed
            and "awma_transient_l2_mode = none" in text
            and "awma_r101r2_transient_service_mode = oracle_1c" in text
            and "awma_transient_l2_terminal_quiescent = 1" in text
        )
    if service_mode is not None:
        passed = (
            passed
            and "AWMA_TRANSIENT_L2_DRAIN enabled=1" in text
            and "gpu_active=0 l2_writeback_active=0 "
                "max_limit_hit=0 gpu_deadlock=0" in text
        )
    result = {
        "status": "PASS" if passed else "FAIL",
        "arm": args.arm,
        "rc": rc,
        "cycles": scalar(text, "gpu_tot_sim_cycle"),
        "instructions": scalar(text, "gpu_tot_sim_insn"),
        "ctas": scalar(text, "gpu_tot_issued_cta"),
        "coverage": coverage,
        "run_log_sha256": sha(output / "run.log"),
    }
    (output / "OFF_EQUIVALENCE.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
