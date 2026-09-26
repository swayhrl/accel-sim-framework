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


STAGE = "AWMA_AI_TRANSLATION_NATIVE_RESIDUAL_174NEW_V1"
REPO = Path(
    "/root/workspace/accel-sim-framework-awma-ai-translation-native-residual-174new-v1"
)
RUNTIME = Path("/root/awma_intrawarp_translation_baseline_residual_v1_runtime")
BINARY = RUNTIME / "bin/unified_accel-sim.out"
CORE_LIB = RUNTIME / "src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release"
CONFIG = REPO / "configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config"
TRACE_CONFIG = REPO / "gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config"
VALIDATOR = Path(
    "/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/"
    "l2_grammar_audit/traceg_grammar_smoke"
)
DURABLE = Path(
    "/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/raw"
)

TARGETS = {
    "L1": {
        "family": "LLAMA32_1B_GEMV",
        "payload": Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/ai_translation_native_atlas_capture_20260926/capture_L1/raw/kernel-7074-ctx_0x56ff7d1d7360.traceg.xz"),
        "sha256": "28ace77d25a0f14ef1f5f3cd04f8334e64ac1b476ecb60c2e52abdb1d6ea3e7e",
        "function_sha256": "e52f28ddc664202dcf583dfef5266a7d06e21d90dcaf3c98eb3b6c993036ea9d",
        "grid": "2048,1,1", "block": "16,4,1",
    },
    "M1": {
        "family": "OLMOE_GEMV",
        "payload": Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/ai_translation_native_atlas_capture_20260926/capture_M1_r2/raw/kernel-88672-ctx_0x62924f24aee0.traceg.xz"),
        "sha256": "38d08b64ced6a92ac773b6bc926471482162fea80dcec6aad897a84114387fd5",
        "function_sha256": "e52f28ddc664202dcf583dfef5266a7d06e21d90dcaf3c98eb3b6c993036ea9d",
        "grid": "256,1,1", "block": "16,4,1",
    },
    "M2": {
        "family": "OLMOE_REDUCTION_CONTROL",
        "payload": Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/ai_translation_native_atlas_capture_20260926/capture_M2/raw/kernel-88632-ctx_0x64999f6df860.traceg.xz"),
        "sha256": "77740c7dd8b1dcf401128b2edb530d50f6421b4cbc5758d1bf2b5ca5e6453334",
        "function_sha256": "6ad9926a5d68a14461329c938238552973df147d6fffb04afeafd4270ad83427",
        "grid": "1,1,1", "block": "256,1,1",
    },
    "L2": {
        "family": "LLAMA32_1B_ATTENTION_LIKE",
        "payload": Path("/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/L2_GRAMMAR_REPAIRED_DETERMINISTIC/kernel-7062-ctx_0x5c4fa771e8b0.traceg.xz"),
        "sha256": "db391d6731d0568a0abf0283546c564d793adc0fbeecab7010831eb8329297e6",
        "function_sha256": "f161786ce964fe9303a4c7f1d0fdc76f21713ac6db25151f371fca82d3622f10",
        "grid": "1,2,32", "block": "128,1,1",
    },
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def trace_args() -> list[str]:
    result: list[str] = []
    for raw in TRACE_CONFIG.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            result.extend(shlex.split(line))
    return result


def vm_overlay(l1_latency: int) -> list[str]:
    return [
        "-gpgpu_vm_mode", "2", "-gpgpu_vm_page_size", "65536",
        "-gpgpu_vm_l1_tlb_entries", "32", "-gpgpu_vm_l1_tlb_assoc", "32",
        "-gpgpu_vm_l1_tlb_ports", "1",
        "-gpgpu_vm_l1_tlb_lookup_latency", str(l1_latency),
        "-gpgpu_vm_l2_tlb_entries", "768", "-gpgpu_vm_l2_tlb_assoc", "16",
        "-gpgpu_vm_l2_tlb_ports", "1", "-gpgpu_vm_l2_tlb_lookup_latency", "80",
        "-gpgpu_vm_translation_mshr_entries", "32", "-gpgpu_vm_pwq_entries", "32",
        "-gpgpu_vm_walkers", "16", "-gpgpu_vm_ptw_mode", "1",
        "-gpgpu_vm_pt_levels", "4", "-gpgpu_vm_virtual_address_bits", "49",
        "-gpgpu_vm_pwc_mode", "1", "-gpgpu_vm_pwc_entries", "128",
        "-gpgpu_vm_pwc_lookup_latency", "1",
    ]


def run(target: str, arm: str, timeout_seconds: int, overwrite: bool) -> dict[str, object]:
    spec = TARGETS[target]
    payload = spec["payload"]
    if digest(payload) != spec["sha256"]:
        raise RuntimeError(f"{target}: payload SHA mismatch")
    validation = subprocess.run(
        [str(VALIDATOR), str(payload)], text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if validation.returncode != 0:
        raise RuntimeError(f"{target}: grammar reject: {validation.stderr}")
    grammar = json.loads(validation.stdout)
    if grammar.get("status") != "TRACEG_GRAMMAR_PASS":
        raise RuntimeError(f"{target}: grammar status mismatch")
    latency = 10 if arm == "B0" else 0
    label = "WARP_REFERENCE_10_80" if arm == "B0" else "VIPT_LIKE_B1_0_80"
    out = DURABLE / f"{target}_{label}"
    rc_path = out / "rc.txt"
    if not overwrite and rc_path.is_file() and rc_path.read_text().strip() == "0":
        return {"target": target, "arm": arm, "rc": 0, "status": "SKIPPED_EXISTING_PASS"}
    out.mkdir(parents=True, exist_ok=True)
    traces = out / "traces"
    if traces.exists(): shutil.rmtree(traces)
    traces.mkdir()
    link = traces / payload.name
    link.symlink_to(payload)
    (traces / "kernelslist.g").write_text(payload.name + "\n")
    (out / "grammar.json").write_text(json.dumps(grammar, indent=2, sort_keys=True) + "\n")

    environment = os.environ.copy()
    for key in tuple(environment):
        if key.startswith("GPGPUSIM_AWMA_") or key in (
            "GPGPUSIM_READY_APPLICATION_V2",
            "GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH",
        ):
            environment.pop(key, None)
    environment["LD_LIBRARY_PATH"] = f"{CORE_LIB}:{environment.get('LD_LIBRARY_PATH', '')}"
    environment.update(
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
    command = [
        "nice", "-n", "10", str(BINARY), "-config", str(CONFIG),
        "-trace", "traces/kernelslist.g",
    ] + trace_args() + vm_overlay(latency)
    receipt = {
        "stage": STAGE, "target": target, "family": spec["family"],
        "arm": arm, "path_model": "CURRENT_SEQUENTIAL" if arm == "B0" else "VIPT_LIKE_PARALLEL_L1_DIAGNOSTIC",
        "scientific_role": "STRONG_BASELINE_QUALIFICATION" if arm == "B0" else "BOUNDED_PATH_DIAGNOSTIC",
        "native_authority": "39548abdd83bf5058abc5ffedd9513286ddab271",
        "strong_reference_authority": "9efe8236e0c6338addfef5480e1da91bffb504eb",
        "function_sha256": spec["function_sha256"], "grid": spec["grid"], "block": spec["block"],
        "argv": command,
        "environment": {key: environment[key] for key in sorted(environment) if key.startswith("GPGPUSIM_")},
        "binary_sha256": digest(BINARY), "config_sha256": digest(CONFIG),
        "trace_config_sha256": digest(TRACE_CONFIG), "trace_sha256": digest(payload),
        "grammar": grammar,
    }
    (out / "command.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    (out / "start_utc.txt").write_text(utc() + "\n")
    started = time.monotonic()
    with (out / "run.log").open("w") as stdout, (out / "run.stderr").open("w") as stderr:
        try:
            rc = subprocess.run(command, cwd=out, env=environment, stdout=stdout,
                                stderr=stderr, timeout=timeout_seconds).returncode
        except subprocess.TimeoutExpired:
            rc = 124
    rc_path.write_text(f"{rc}\n")
    (out / "end_utc.txt").write_text(utc() + "\n")
    (out / "wall_seconds.txt").write_text(f"{time.monotonic() - started:.6f}\n")
    return {"target": target, "arm": arm, "rc": rc, "status": "PASS" if rc == 0 else "FAIL"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("arm", choices=("B0", "B1"))
    parser.add_argument("--targets", nargs="+", required=True)
    parser.add_argument("--workers", type=int, default=1, choices=(1, 2))
    parser.add_argument("--timeout-seconds", type=int, default=21600)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if any(target not in TARGETS for target in args.targets):
        parser.error("unknown target")
    if args.arm == "B1" and "M2" in args.targets:
        parser.error("M2 is a B0-only control unless separately authorized")
    DURABLE.mkdir(parents=True, exist_ok=True)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run, target, args.arm, args.timeout_seconds, args.overwrite)
                   for target in args.targets]
        for future in concurrent.futures.as_completed(futures):
            result = future.result(); results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    results.sort(key=lambda row: str(row["target"]))
    (DURABLE / f"{args.arm}_launcher_results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n"
    )
    return 0 if all(row["rc"] == 0 for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
