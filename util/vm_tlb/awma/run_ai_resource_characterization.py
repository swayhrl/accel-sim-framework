#!/usr/bin/env python3
"""Run preregistered, single-domain AI resource diagnostics."""

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


STAGE = "AWMA_AI_GPU_RESOURCE_BOTTLENECK_CHARACTERIZATION_V1"
REPO = Path("/root/workspace/accel-sim-framework-awma-ai-gpu-resource-bottleneck-characterization-v1")
RUNTIME = Path("/root/awma_intrawarp_translation_baseline_residual_v1_runtime")
BINARY = RUNTIME / "bin/unified_accel-sim.out"
CORE_LIB = RUNTIME / "src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release"
CONFIG = REPO / "configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config"
TRACE_CONFIG = REPO / "gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config"
VALIDATOR = Path("/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/l2_grammar_audit/traceg_grammar_smoke")
DURABLE = Path("/root/share/mnt164/huangrulin/awma_ai_gpu_resource_bottleneck_characterization_v1/raw")

TARGETS = {
    "T0": ("PREFILL_FLASH", RUNTIME / "inputs/kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz", "d8fa338f82800f646c8501a6a1d1049afaae213fe0d7f70d4913fcfaa76ba67a"),
    "T1": ("PREFILL_GEMM", RUNTIME / "inputs/kernel-45-ctx_0x60d38cb72530.traceg.xz", "e36178f9a92033cd91f3c1ff4b165321b7958157c7deed2a9aaa4696e7c73e8c"),
    "T2": ("DECODE_GEMV", RUNTIME / "inputs/kernel-17039-ctx_0x5ddb6907c160.traceg.xz", "b87cd6cb6a2bc0f67e17616e26d1bf9091facad242d46a43f5f9c1ac274b6138"),
    "SPLITKV": ("DECODE_ATTENTION_SPLIT", RUNTIME / "inputs/kernel-17543-ctx_0x5be0856adcb0.traceg.xz", "282a9b18510bd0aaf54ec528c65bfb39d49b052902c6b87f3b85bb2973096371"),
    "L1": ("DECODE_GEMV_SCALE8", Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/ai_translation_native_atlas_capture_20260926/capture_L1/raw/kernel-7074-ctx_0x56ff7d1d7360.traceg.xz"), "28ace77d25a0f14ef1f5f3cd04f8334e64ac1b476ecb60c2e52abdb1d6ea3e7e"),
    "M1": ("DECODE_GEMV_SCALE1", Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/ai_translation_native_atlas_capture_20260926/capture_M1_r2/raw/kernel-88672-ctx_0x62924f24aee0.traceg.xz"), "38d08b64ced6a92ac773b6bc926471482162fea80dcec6aad897a84114387fd5"),
    "M2": ("DECODE_REDUCTION_CONTROL", Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/ai_translation_native_atlas_capture_20260926/capture_M2/raw/kernel-88632-ctx_0x64999f6df860.traceg.xz"), "77740c7dd8b1dcf401128b2edb530d50f6421b4cbc5758d1bf2b5ca5e6453334"),
    "L2": ("DECODE_ATTENTION_LIKE", Path("/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/L2_GRAMMAR_REPAIRED_DETERMINISTIC/kernel-7062-ctx_0x5c4fa771e8b0.traceg.xz"), "db391d6731d0568a0abf0283546c564d793adc0fbeecab7010831eb8329297e6"),
}

L1_BASE = "S:4:128:256,L:T:m:L:L,A:384:48,16:0,32"
L2_BASE = "S:2048:128:16,L:B:m:L:X,A:192:4,32:0,32"
ARMS = {
    "BASELINE": [],
    "SFU_2X": ["-gpgpu_num_sfu_units", "8"],
    "SFU_UB": ["-gpgpu_num_sfu_units", "16"],
    "TENSOR_2X": ["-specialized_unit_3", "1,8,32,4,4,TENSOR"],
    "TENSOR_UB": ["-specialized_unit_3", "1,16,32,4,4,TENSOR"],
    "L1_LAT_2X": ["-gpgpu_l1_latency", "16"],
    "L1_LAT_UB": ["-gpgpu_l1_latency", "1"],
    "L1_BANK_2X": ["-gpgpu_l1_banks", "8"],
    "L1_BANK_UB": ["-gpgpu_l1_banks", "16"],
    "L1_MSHR_2X": ["-gpgpu_cache:dl1", "S:4:128:256,L:T:m:L:L,A:768:48,16:0,32"],
    "L1_MSHR_UB": ["-gpgpu_cache:dl1", "S:4:128:256,L:T:m:L:L,A:1536:48,16:0,32"],
    "L2_CAP_2X": ["-gpgpu_cache:dl2", "S:4096:128:16,L:B:m:L:X,A:192:4,32:0,32"],
    "L2_CAP_UB": ["-gpgpu_cache:dl2", "S:8192:128:16,L:B:m:L:X,A:192:4,32:0,32"],
    "L2_MSHR_2X": ["-gpgpu_cache:dl2", "S:2048:128:16,L:B:m:L:X,A:384:4,32:0,32"],
    "L2_MSHR_UB": ["-gpgpu_cache:dl2", "S:2048:128:16,L:B:m:L:X,A:768:4,32:0,32"],
    "L2_PORT_2X": ["-gpgpu_cache:dl2", "S:2048:128:16,L:B:m:L:X,A:192:4,32:0,64"],
    "L2_PORT_UB": ["-gpgpu_cache:dl2", "S:2048:128:16,L:B:m:L:X,A:192:4,32:0,128"],
    "DRAM_2X": ["-dram_data_command_freq_ratio", "2"],
    "DRAM_UB": ["-dram_data_command_freq_ratio", "1"],
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_trace_args() -> list[str]:
    args: list[str] = []
    for raw in TRACE_CONFIG.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            args.extend(shlex.split(line))
    return args


def vm_overlay() -> list[str]:
    return [
        "-gpgpu_vm_mode", "2", "-gpgpu_vm_page_size", "65536",
        "-gpgpu_vm_l1_tlb_entries", "32", "-gpgpu_vm_l1_tlb_assoc", "32",
        "-gpgpu_vm_l1_tlb_ports", "1", "-gpgpu_vm_l1_tlb_lookup_latency", "10",
        "-gpgpu_vm_l2_tlb_entries", "768", "-gpgpu_vm_l2_tlb_assoc", "16",
        "-gpgpu_vm_l2_tlb_ports", "1", "-gpgpu_vm_l2_tlb_lookup_latency", "80",
        "-gpgpu_vm_translation_mshr_entries", "32", "-gpgpu_vm_pwq_entries", "32",
        "-gpgpu_vm_walkers", "16", "-gpgpu_vm_ptw_mode", "1",
        "-gpgpu_vm_pt_levels", "4", "-gpgpu_vm_virtual_address_bits", "49",
        "-gpgpu_vm_pwc_mode", "1", "-gpgpu_vm_pwc_entries", "128",
        "-gpgpu_vm_pwc_lookup_latency", "1",
    ]


def run_one(target: str, arm: str, timeout: int, overwrite: bool) -> dict[str, object]:
    family, payload, expected_sha = TARGETS[target]
    if digest(payload) != expected_sha:
        raise RuntimeError(f"{target}: trace SHA mismatch")
    validation = subprocess.run([str(VALIDATOR), str(payload)], text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if validation.returncode or json.loads(validation.stdout).get("status") != "TRACEG_GRAMMAR_PASS":
        raise RuntimeError(f"{target}: grammar validation failed: {validation.stderr}")
    out = DURABLE / f"{target}__{arm}"
    if not overwrite and (out / "rc.txt").is_file() and (out / "rc.txt").read_text().strip() == "0":
        return {"target": target, "arm": arm, "rc": 0, "status": "SKIPPED_EXISTING_PASS"}
    out.mkdir(parents=True, exist_ok=True)
    traces = out / "traces"
    if traces.exists():
        shutil.rmtree(traces)
    traces.mkdir()
    (traces / payload.name).symlink_to(payload)
    (traces / "kernelslist.g").write_text(payload.name + "\n")
    command = (["nice", "-n", "10", str(BINARY), "-config", str(CONFIG),
                "-trace", "traces/kernelslist.g"] + read_trace_args() + vm_overlay() + ARMS[arm])
    env = os.environ.copy()
    for key in tuple(env):
        if key.startswith("GPGPUSIM_AWMA_") or key == "GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH":
            env.pop(key, None)
    env["LD_LIBRARY_PATH"] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    env.update(
        GPGPUSIM_AWMA_TRANSLATION_CANDIDATE="warp_vpn_dedup_reference",
        GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH="1",
        GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER="0",
        GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS="1",
        GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS="1",
        GPGPUSIM_AWMA_BOTTLENECK_OBSERVATORY="1",
        GPGPUSIM_VM_COVERAGE_KERNEL_UID="1",
        GPGPUSIM_READY_APPLICATION_DIAGNOSTICS="1",
        GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS="1",
    )
    receipt = {
        "stage": STAGE, "target": target, "family": family, "arm": arm,
        "scientific_dimension": arm.rsplit("_", 1)[0] if arm != "BASELINE" else "BASELINE",
        "argv": command, "overrides": ARMS[arm],
        "environment": {k: env[k] for k in sorted(env) if k.startswith("GPGPUSIM_")},
        "binary_sha256": digest(BINARY), "config_sha256": digest(CONFIG),
        "trace_config_sha256": digest(TRACE_CONFIG), "trace_sha256": expected_sha,
        "coordination_authority": "5a1f6761641bbe8c24aef4128db87a9c57ae93a2",
        "strong_baseline_authority": "9efe8236e0c6338addfef5480e1da91bffb504eb",
        "observatory_authority": "b85d388abe98e5da70b749b52075c33fad7cede4",
    }
    (out / "command.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    (out / "start_utc.txt").write_text(utc() + "\n")
    started = time.monotonic()
    rc = 124
    with (out / "run.log").open("w") as stdout, (out / "run.stderr").open("w") as stderr:
        try:
            rc = subprocess.run(command, cwd=out, env=env, stdout=stdout,
                                stderr=stderr, timeout=timeout).returncode
        except subprocess.TimeoutExpired:
            pass
    (out / "rc.txt").write_text(f"{rc}\n")
    (out / "end_utc.txt").write_text(utc() + "\n")
    (out / "wall_seconds.txt").write_text(f"{time.monotonic() - started:.6f}\n")
    return {"target": target, "arm": arm, "rc": rc, "status": "PASS" if rc == 0 else "FAIL"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", nargs="+", required=True, metavar="TARGET:ARM")
    parser.add_argument("--workers", type=int, default=1, choices=range(1, 9))
    parser.add_argument("--timeout-seconds", type=int, default=14400)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    jobs: list[tuple[str, str]] = []
    for text in args.jobs:
        target, separator, arm = text.partition(":")
        if not separator or target not in TARGETS or arm not in ARMS:
            parser.error(f"invalid job {text}")
        if target == "M2" and arm != "BASELINE":
            parser.error("M2 is control-only")
        jobs.append((target, arm))
    DURABLE.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_one, target, arm, args.timeout_seconds, args.overwrite)
                   for target, arm in jobs]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    results.sort(key=lambda row: (str(row["target"]), str(row["arm"])))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (DURABLE / f"launcher_{stamp}.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    return 0 if all(result["rc"] == 0 for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
