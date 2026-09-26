#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


STAGE = "AWMA_POST_CLASSIC_BASELINE_RESIDUAL_DISCOVERY_V1"
REPO = Path(
    "/root/workspace/accel-sim-framework-awma-post-classic-baseline-residual-discovery-v1"
)
LANE_B_RUNTIME = Path("/root/awma_intrawarp_translation_baseline_residual_v1_runtime")
LANE_B_RAW = Path(
    "/root/share/mnt164/huangrulin/awma_intrawarp_translation_baseline_residual_v1/raw"
)
DURABLE = Path(
    "/root/share/mnt164/huangrulin/awma_post_classic_baseline_residual_discovery_v1/raw"
)
BINARY = LANE_B_RUNTIME / "bin/unified_accel-sim.out"
INPUTS = LANE_B_RUNTIME / "inputs"
CORE_LIB = (
    LANE_B_RUNTIME
    / "src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release"
)
CONFIG = REPO / "configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config"
TRACE_CONFIG = REPO / "gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config"

TARGETS = {
    "T0": (
        "PREFILL_FLASH",
        "kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz",
        "d8fa338f82800f646c8501a6a1d1049afaae213fe0d7f70d4913fcfaa76ba67a",
        488559,
    ),
    "T1": (
        "PREFILL_GEMM",
        "kernel-45-ctx_0x60d38cb72530.traceg.xz",
        "e36178f9a92033cd91f3c1ff4b165321b7958157c7deed2a9aaa4696e7c73e8c",
        619514,
    ),
    "T2": (
        "DECODE_GEMV",
        "kernel-17039-ctx_0x5ddb6907c160.traceg.xz",
        "b87cd6cb6a2bc0f67e17616e26d1bf9091facad242d46a43f5f9c1ac274b6138",
        94034,
    ),
    "A2": (
        "DECODE_GEMV_PAIR_A_T8192",
        "kernel-16828-ctx_0x573505e282b0.traceg.xz",
        "c8135003bae105108707ab6b024ca56e50146df88d1692068d92e99511ada2ca",
        115700,
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def trace_args() -> list[str]:
    result: list[str] = []
    for raw in TRACE_CONFIG.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            result.extend(shlex.split(line))
    return result


def vm_overlay() -> list[str]:
    return [
        "-gpgpu_vm_mode", "2",
        "-gpgpu_vm_page_size", "65536",
        "-gpgpu_vm_l1_tlb_entries", "32",
        "-gpgpu_vm_l1_tlb_assoc", "32",
        "-gpgpu_vm_l1_tlb_ports", "1",
        "-gpgpu_vm_l1_tlb_lookup_latency", "0",
        "-gpgpu_vm_l2_tlb_entries", "768",
        "-gpgpu_vm_l2_tlb_assoc", "16",
        "-gpgpu_vm_l2_tlb_ports", "1",
        "-gpgpu_vm_l2_tlb_lookup_latency", "80",
        "-gpgpu_vm_translation_mshr_entries", "32",
        "-gpgpu_vm_pwq_entries", "32",
        "-gpgpu_vm_walkers", "16",
        "-gpgpu_vm_ptw_mode", "1",
        "-gpgpu_vm_pt_levels", "4",
        "-gpgpu_vm_virtual_address_bits", "49",
        "-gpgpu_vm_pwc_mode", "1",
        "-gpgpu_vm_pwc_entries", "128",
        "-gpgpu_vm_pwc_lookup_latency", "1",
    ]


def run(target: str, timeout_seconds: int, overwrite: bool) -> dict[str, object]:
    family, filename, trace_sha, reference_cycles = TARGETS[target]
    payload = INPUTS / filename
    if sha256(payload) != trace_sha:
        raise RuntimeError(f"{target}: trace SHA mismatch")
    out = DURABLE / f"{target}_REFERENCE_L1_0_L2_80_DIAGNOSTIC"
    rc_path = out / "rc.txt"
    if not overwrite and rc_path.is_file() and rc_path.read_text().strip() == "0":
        return {"target": target, "rc": 0, "status": "SKIPPED_EXISTING_PASS"}
    out.mkdir(parents=True, exist_ok=True)
    traces = out / "traces"
    if traces.exists():
        shutil.rmtree(traces)
    traces.mkdir()
    (traces / filename).symlink_to(payload)
    (traces / "kernelslist.g").write_text(filename + "\n")

    environment = os.environ.copy()
    for key in tuple(environment):
        if key.startswith("GPGPUSIM_AWMA_") or key in (
            "GPGPUSIM_READY_APPLICATION_V2",
            "GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH",
        ):
            environment.pop(key, None)
    environment["LD_LIBRARY_PATH"] = (
        f"{CORE_LIB}:{environment.get('LD_LIBRARY_PATH', '')}"
    )
    environment.update(
        GPGPUSIM_AWMA_TRANSLATION_CANDIDATE="warp_vpn_dedup_reference",
        GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH="1",
        GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER="0",
        GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS="1",
        GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS="1",
        GPGPUSIM_VM_COVERAGE_KERNEL_UID="1",
        GPGPUSIM_READY_APPLICATION_DIAGNOSTICS="1",
        GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS="1",
    )
    command = [
        "nice", "-n", "10", str(BINARY),
        "-config", str(CONFIG),
        "-trace", "traces/kernelslist.g",
    ] + trace_args() + vm_overlay()
    receipt = {
        "stage": STAGE,
        "target": target,
        "family": family,
        "arm": "REFERENCE_L1_0_L2_80_DIAGNOSTIC",
        "scientific_role": "CAUSAL_DIAGNOSTIC_NOT_MECHANISM_OR_UPPER_BOUND",
        "accepted_reference_cycles_10_80": reference_cycles,
        "lane_b_authority": "9efe8236e0c6338addfef5480e1da91bffb504eb",
        "argv": command,
        "environment": {
            key: environment[key]
            for key in sorted(environment)
            if key.startswith("GPGPUSIM_")
        },
        "binary_sha256": sha256(BINARY),
        "config_sha256": sha256(CONFIG),
        "trace_config_sha256": sha256(TRACE_CONFIG),
        "trace_sha256": trace_sha,
    }
    (out / "command.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    (out / "start_utc.txt").write_text(utc() + "\n")
    started = time.monotonic()
    with (out / "run.log").open("w") as stdout, (out / "run.stderr").open(
        "w"
    ) as stderr:
        try:
            rc = subprocess.run(
                command,
                cwd=out,
                env=environment,
                stdout=stdout,
                stderr=stderr,
                timeout=timeout_seconds,
            ).returncode
        except subprocess.TimeoutExpired:
            rc = 124
    rc_path.write_text(f"{rc}\n")
    (out / "end_utc.txt").write_text(utc() + "\n")
    (out / "wall_seconds.txt").write_text(f"{time.monotonic() - started:.6f}\n")
    return {"target": target, "rc": rc, "status": "PASS" if rc == 0 else "FAIL"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=2, choices=(1, 2))
    parser.add_argument("--timeout-seconds", type=int, default=21600)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    DURABLE.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(run, target, args.timeout_seconds, args.overwrite)
            for target in TARGETS
        ]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    results.sort(key=lambda row: str(row["target"]))
    (DURABLE / "launcher_results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n"
    )
    return 0 if all(row["rc"] == 0 for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
