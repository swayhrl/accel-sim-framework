#!/usr/bin/env python3
"""Small integrated P1 OFF-equivalence and positive-path qualification."""

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


STAGE = "AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_V1"
BASE = Path("/root/awma_rtx4080_v1_baseline_promotion_v1_runtime/ai_T2_V1_10_80")
REPO = Path(
    "/root/workspace/accel-sim-framework-"
    "awma-r101r4-local-service-path-localization-174-v1"
)
RUNTIME = Path("/root/awma_r101r4_p1_post_l1_local_service_174_v1_runtime")
RAW = Path(
    "/root/share/mnt164/huangrulin/"
    "awma_r101r4_local_service_path_localization_174_v1/raw/smoke"
)
BINARY = RUNTIME / "bin/unified_accel-sim.out"
CORE_LIB = RUNTIME / "src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release"
NONE_SIDECAR = REPO / (
    "util/vm_tlb/awma/r101_transient_l2_arch_v1/"
    "directed_no_overlap_runtime.tsv"
)
POSITIVE_SIDECAR = REPO / (
    "util/vm_tlb/awma/r101r2_context2_memory_service_v1/"
    "directed_positive_runtime.tsv"
)
CONFIG = REPO / "configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config"
EXPECTED = {
    "cycles": 93079,
    "instructions": 43357696,
    "ctas": 1216,
    "unique": 411008,
    "positive_context_end_cycle": 203629,
}
ARMS = {
    "default_off": {"mode": None, "repetitions": 1},
    "explicit_none": {"mode": "none", "repetitions": 1},
    "p1_positive": {"mode": "p1_post_l1_local", "repetitions": 6},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def scalar(text: str, key: str) -> int:
    values = [
        line.split("=", 1)[1].strip()
        for line in text.splitlines()
        if line.strip().startswith(key + " =")
    ]
    if not values:
        raise RuntimeError(f"missing scalar {key}")
    return int(values[-1], 0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("arm", choices=tuple(ARMS))
    parser.add_argument("--reuse-existing", action="store_true")
    args = parser.parse_args()
    arm = ARMS[args.arm]
    mode = arm["mode"]
    repetitions = arm["repetitions"]

    accepted = json.loads((BASE / "command.json").read_text())
    accepted_config = Path(accepted["argv"][2])
    if sha256(accepted_config) != (
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
        key: str(value)
        for key, value in accepted["environment"].items()
        if key.startswith("GPGPUSIM_")
    })
    env["GPGPUSIM_ROOT"] = str(RUNTIME / "src/gpgpu-sim")
    env["GPGPUSIM_POWER_MODEL"] = str(
        RUNTIME / "src/gpgpu-sim/src/accelwattch"
    ) + "/"
    env["GPGPUSIM_VM_COVERAGE_KERNEL_UID"] = "all"
    env["LD_LIBRARY_PATH"] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"

    sidecar = POSITIVE_SIDECAR if mode == "p1_post_l1_local" else NONE_SIDECAR
    if mode is not None:
        env.update({
            "AWMA_TRANSIENT_L2_MODE": "none",
            "AWMA_TRANSIENT_L2_DIAGNOSTICS": "1",
            "AWMA_TRANSIENT_L2_SIDECAR": str(sidecar),
            "AWMA_TRANSIENT_L2_DRAIN": "1",
            "AWMA_R101R2_TRANSIENT_SERVICE_MODE": "none",
            "AWMA_R101R3_SERVICE_MODE": "none",
            "AWMA_R101R4_SERVICE_MODE": mode,
            "AWMA_R101R3_DIAGNOSTICS": "0",
            "AWMA_R101R4_DIAGNOSTICS": "1",
        })

    receipt = {
        "stage": STAGE,
        "arm": args.arm,
        "argv": command,
        "binary_sha256": sha256(BINARY),
        "core_library_sha256": sha256(CORE_LIB / "libcudart.so"),
        "config_sha256": sha256(CONFIG),
        "trace_sha256": sha256(payload),
        "sidecar_sha256": sha256(sidecar) if mode is not None else None,
        "environment": {
            key: env[key] for key in sorted(env)
            if key.startswith("AWMA_") or key.startswith("GPGPUSIM_")
        },
    }
    if args.reuse_existing:
        prior = json.loads((output / "command.json").read_text())
        for key in ("stage", "arm", "argv", "binary_sha256",
                    "core_library_sha256", "config_sha256",
                    "trace_sha256", "sidecar_sha256", "environment"):
            if prior.get(key) != receipt.get(key):
                raise RuntimeError(f"existing receipt drift: {key}")
        rc = int((output / "rc.txt").read_text().strip())
    else:
        (output / "command.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        )
        (output / "start_utc.txt").write_text(
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            + "\n"
        )
        started = time.monotonic()
        with (output / "run.log").open("w") as stdout, \
                (output / "run.stderr").open("w") as stderr:
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
        rc == 0
        and (output / "run.stderr").stat().st_size == 0
        and len(coverage) == repetitions
        and all(
            "untranslated=0" in line
            and "unobserved=0" in line
            and f"unique={EXPECTED['unique']}" in line
            for line in coverage
        )
    )
    cycles = scalar(text, "gpu_tot_sim_cycle")
    instructions = scalar(text, "gpu_tot_sim_insn")
    ctas = scalar(text, "gpu_tot_issued_cta")

    if mode is None or mode == "none":
        passed = (
            passed
            and cycles == EXPECTED["cycles"]
            and instructions == EXPECTED["instructions"]
            and ctas == EXPECTED["ctas"]
        )
    if mode is None:
        passed = (
            passed
            and "awma_r101r3_service_mode" not in text
            and "awma_transient_l2_mode" not in text
        )
    elif mode == "none":
        passed = (
            passed
            and "awma_r101r4_service_mode = none" in text
            and scalar(text, "awma_r101r2_service_qualified_reads") == 0
            and scalar(text, "awma_r101r2_service_qualified_writes") == 0
            and scalar(text, "awma_r101r2_service_duplicate_completions") == 0
            and scalar(text, "awma_transient_l2_terminal_quiescent") == 1
        )
    else:
        admitted_reads = scalar(text, "awma_r101r4_p1_admitted_reads")
        admitted_writes = scalar(text, "awma_r101r4_p1_admitted_writes")
        delivered = (
            scalar(text, "awma_r101r4_p1_delivered_reads")
            + scalar(text, "awma_r101r4_p1_delivered_writes")
        )
        l1_accesses = scalar(text, "L1D_total_cache_accesses")
        l1_misses = scalar(text, "L1D_total_cache_misses")
        passed = (
            passed
            and instructions == EXPECTED["instructions"] * repetitions
            and ctas == EXPECTED["ctas"] * repetitions
            and "awma_r101r4_service_mode = p1_post_l1_local" in text
            and scalar(text, "awma_r101r2_service_scheduled") == 0
            and admitted_reads > 0 and admitted_writes > 0
            and scalar(text, "awma_r101r4_p1_admitted_ldg_reads") > 0
            and scalar(text, "awma_r101r4_p1_admitted_ldgsts_reads") == 0
            and scalar(text, "awma_r101r4_p1_ready_eligible")
                == admitted_reads + admitted_writes
            and scalar(text, "awma_r101r4_p1_ready")
                == admitted_reads + admitted_writes
            and delivered == admitted_reads + admitted_writes
            and scalar(text, "awma_r101r4_p1_outstanding") == 0
            and scalar(text, "awma_r101r4_p1_duplicate") == 0
            and scalar(text, "awma_r101r4_p1_latency_violations") == 0
            and scalar(text, "awma_r101r4_p1_stale_violations") == 0
            and 0 < scalar(text, "awma_r101r4_p1_max_scheduled_depth") <= 1
            and 0 < scalar(text, "awma_r101r4_p1_max_ready_depth") <= 16
            and l1_accesses > l1_misses > 0
            and scalar(text, "awma_r101r2_context_end_cycle")
                == EXPECTED["positive_context_end_cycle"]
            and scalar(text, "awma_transient_l2_terminal_quiescent") == 1
            and "AWMA_TRANSIENT_L2_DRAIN enabled=1" in text
            and "gpu_active=0 l2_writeback_active=0 "
                "max_limit_hit=0 gpu_deadlock=0" in text
        )

    result = {
        "stage": STAGE,
        "status": "PASS" if passed else "FAIL",
        "arm": args.arm,
        "rc": rc,
        "cycles": cycles,
        "instructions": instructions,
        "ctas": ctas,
        "coverage_kernels": len(coverage),
        "run_log_sha256": sha256(output / "run.log"),
        "validation_mode": "REUSE_EXISTING" if args.reuse_existing else "SIMULATED",
    }
    if mode == "p1_post_l1_local":
        result.update({
            "context_end_cycle": scalar(text, "awma_r101r2_context_end_cycle"),
            "admitted_reads": scalar(text, "awma_r101r4_p1_admitted_reads"),
            "admitted_writes": scalar(text, "awma_r101r4_p1_admitted_writes"),
            "max_scheduled_depth": scalar(
                text, "awma_r101r4_p1_max_scheduled_depth"
            ),
            "max_ready_depth": scalar(
                text, "awma_r101r4_p1_max_ready_depth"
            ),
            "l1_accesses": scalar(text, "L1D_total_cache_accesses"),
            "l1_misses": scalar(text, "L1D_total_cache_misses"),
            "l1_pending_hits": scalar(text, "L1D_total_cache_pending_hits"),
        })

    (output / "P1_SMOKE.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
