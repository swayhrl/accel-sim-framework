#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


STAGE = "AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_V1"
REPO = Path("/root/workspace/accel-sim-framework-awma-r101-transient-l2-arch-174-v1")
RUNTIME = Path("/root/awma_r101_transient_l2_arch_174_v1_runtime")
BINARY = RUNTIME / "bin/unified_accel-sim.out"
CORE_LIB = RUNTIME / "src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release"
CONFIG = REPO / "configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config"
TRACE_CONFIG = REPO / "gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config"
INPUT = Path("/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/input")
RAW = Path("/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/raw/formal")
MODES = {"B0": "none", "O1": "oracle_dead_drop",
         "M1": "bounded_live_retention"}


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def trace_args() -> list[str]:
    result = []
    for raw in TRACE_CONFIG.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            result.extend(shlex.split(line))
    return result


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


def run(arm: str, timeout: int, overwrite: bool) -> dict[str, object]:
    admission = json.loads((INPUT / "ADMISSION_RECEIPT.json").read_text())
    if admission.get("status") != "PASS":
        raise RuntimeError("formal input is not admitted")
    sidecar = INPUT / "transient_l2_runtime.tsv"
    kernelslist = INPUT / "traces/kernelslist.g"
    if sha(sidecar) != admission["runtime_sidecar_sha256"] or sha(kernelslist) != admission["kernelslist_sha256"]:
        raise RuntimeError("admitted input changed")
    out = RAW / arm
    if not overwrite and (out / "rc.txt").is_file() and (out / "rc.txt").read_text().strip() == "0":
        return {"arm": arm, "rc": 0, "status": "SKIPPED_EXISTING_PASS"}
    out.mkdir(parents=True, exist_ok=True)
    command = (["nice", "-n", "10", str(BINARY), "-config", str(CONFIG),
                "-trace", str(kernelslist)] + trace_args() + vm_overlay())
    env = os.environ.copy()
    for key in tuple(env):
        if key.startswith("AWMA_TRANSIENT_L2") or key.startswith("GPGPUSIM_AWMA_") or key in {
            "GPGPUSIM_READY_APPLICATION_V2", "GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH"}:
            env.pop(key, None)
    env["LD_LIBRARY_PATH"] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    env.update(
        AWMA_TRANSIENT_L2_MODE=MODES[arm],
        AWMA_TRANSIENT_L2_DIAGNOSTICS="1",
        AWMA_TRANSIENT_L2_SIDECAR=str(sidecar),
        GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH="1",
        GPGPUSIM_READY_APPLICATION_V2="0",
        GPGPUSIM_VM_COVERAGE_KERNEL_UID="1",
        GPGPUSIM_READY_APPLICATION_DIAGNOSTICS="1",
        GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS="1",
    )
    receipt = {
        "stage": STAGE, "arm": arm, "mode": MODES[arm], "argv": command,
        "environment": {key: env[key] for key in sorted(env)
                        if key.startswith("AWMA_TRANSIENT_L2") or key.startswith("GPGPUSIM_")},
        "binary_sha256": sha(BINARY), "config_sha256": sha(CONFIG),
        "trace_config_sha256": sha(TRACE_CONFIG), "admission": admission,
        "source_authority": "335df4d36e7dc4939bd95fe1035a96c9d23ac7ff",
    }
    (out / "command.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    (out / "start_utc.txt").write_text(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + "\n")
    started = time.monotonic(); rc = 124
    with (out / "run.log").open("w") as stdout, (out / "run.stderr").open("w") as stderr:
        try:
            rc = subprocess.run(command, cwd=out, env=env, stdout=stdout, stderr=stderr,
                                timeout=timeout).returncode
        except subprocess.TimeoutExpired:
            pass
    (out / "rc.txt").write_text(f"{rc}\n")
    (out / "wall_seconds.txt").write_text(f"{time.monotonic()-started:.6f}\n")
    return {"arm": arm, "rc": rc, "status": "PASS" if rc == 0 else "FAIL"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("arm", choices=tuple(MODES))
    parser.add_argument("--timeout-seconds", type=int, default=86400)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    result = run(args.arm, args.timeout_seconds, args.overwrite)
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0 if result["rc"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
