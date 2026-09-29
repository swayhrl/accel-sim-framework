#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


STAGE = "AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_V1"
REPO = Path("/root/workspace/accel-sim-framework-awma-r101-transient-l2-arch-174-v1")
RUNTIME = Path("/root/awma_r101_transient_l2_arch_174_v1_runtime")
BINARY = RUNTIME / "bin/unified_accel-sim.out"
CORE_LIB = RUNTIME / "src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release"
CORE_LIBRARY = CORE_LIB / "libcudart.so"
CONFIG = REPO / "configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config"
TRACE_CONFIG = REPO / "gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config"
INPUT = Path("/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/input")
LOCAL_RAW = RUNTIME / "raw/formal"
DURABLE_RAW = Path("/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/raw/formal")
CORE_PATCH = REPO / "docs/vm_tlb/review_packs/AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_174_V1/TRANSIENT_L2_CORE.patch"
MODES = {"B0": "none", "O1": "oracle_dead_drop",
         "M1": "bounded_live_retention"}
SUMMARIZER = REPO / "util/vm_tlb/awma/r101_transient_l2_arch_v1/summarize_r101_transient_run.py"
EXPECTED = {
    "binary": "32b38a66ba6b9eee5a9047873992fec42fcc4dbbff6adf247d425aec2b650c5d",
    "core_library": "f18cd8d4c2dd8927d6ad454295e434b902032042e83bbab03afcbd02b23921bf",
    "core_patch": "aa2637f3379f1c0b6184db98a41f276dcdd6bcef86cb72331b18c52cf6232676",
    "config": "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8",
    "trace_config": "a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b",
    "sidecar": "740820a195ae2bb9966a91b1e6d3423f4ded520bd91d1819aac8e78ce104b77d",
    "kernelslist": "9fce012939496008814786a0c12d32c1f97a10c07c62cdd08f1fddcee5d86588",
    "framework": "c6a8e6315226c6d45ae93f2280999d5975328d306cb09f161f1d4d73f3ef4323",
}

SCIENCE = {
    "producer_commit": "bb902283b7ce9e1902b460383fbd3e0bedbd884d",
    "accepted_payload_sha256": "1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234",
    "accepted_output_sha256": "36aaed3f8360aa099301ae1d705bc2e6ab5ba61586adaf7ead93ecab808dc1b0",
    "trace_aggregate_sha256": "34031eebe1e25b375d9ee058328f678e4734790c40e67284bb6511130e4fec0e",
}
EXPECTED_ARGV_SHA256 = "c42a372308798498f12402918eab1424957af811b86534c26fa33d98d1dc034d"
EXPECTED_ADMISSION_RECEIPT_SHA256 = "a6c66cb41c1ffb77f6af805534d47ccb8a8641dbe4aa3b206850be8e478f1e7a"
EXPECTED_SUMMARIZER_SHA256 = "05eda1f021336bba4ebed018ba8657492a0df0b1318c00eecd2c1378b161a1d4"


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def file_hashes(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): sha(path)
        for path in sorted(root.rglob("*")) if path.is_file()
    }


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
    admission_path = INPUT / "ADMISSION_RECEIPT.json"
    if sha(admission_path) != EXPECTED_ADMISSION_RECEIPT_SHA256:
        raise RuntimeError("formal admission receipt drift")
    admission = json.loads(admission_path.read_text())
    if admission.get("status") != "PASS":
        raise RuntimeError("formal input is not admitted")
    sidecar = INPUT / "transient_l2_runtime.tsv"
    kernelslist = INPUT / "traces/kernelslist.g"
    if sha(sidecar) != admission["runtime_sidecar_sha256"] or sha(kernelslist) != admission["kernelslist_sha256"]:
        raise RuntimeError("admitted input changed")
    members = admission.get("trace_members", [])
    frozen = {
        "binary": sha(BINARY),
        "core_library": sha(CORE_LIBRARY),
        "core_patch": sha(CORE_PATCH),
        "trace_config": sha(TRACE_CONFIG),
        "config": sha(CONFIG),
        "sidecar": sha(sidecar),
        "kernelslist": sha(kernelslist),
        "framework": sha(REPO / "gpu-simulator/accel-sim.cc"),
    }
    if frozen != EXPECTED:
        raise RuntimeError(f"frozen formal artifact drift: {frozen}")
    if sha(SUMMARIZER) != EXPECTED_SUMMARIZER_SHA256:
        raise RuntimeError("formal summarizer drift")
    if len(members) != 18:
        raise RuntimeError("admitted trace member count changed")
    ordered_trace_binding = "".join(
        f"{Path(member['path']).name}\t{member['sha256']}\n"
        for member in members
    ).encode()
    science = {
        "producer_commit": admission.get("producer_commit"),
        "accepted_payload_sha256": admission.get("accepted_payload_sha256"),
        "accepted_output_sha256": admission.get("accepted_output_sha256"),
        "trace_aggregate_sha256": hashlib.sha256(ordered_trace_binding).hexdigest(),
    }
    if science != SCIENCE:
        raise RuntimeError(f"scientific input authority drift: {science}")
    for member in members:
        source = Path(member["path"]).resolve()
        consumer = INPUT / "traces" / source.name
        if consumer.resolve() != source or sha(consumer) != member["sha256"]:
            raise RuntimeError(f"admitted consumer trace changed: {consumer}")
    durable = DURABLE_RAW / arm
    if arm != "B0":
        b0_lock = RUNTIME / "locks/B0.lock"
        b0_summary_path = DURABLE_RAW / "B0/RUN_SUMMARY.json"
        if b0_lock.exists() or not b0_summary_path.is_file():
            raise RuntimeError("formal B0 is not complete/published")
        b0_summary = json.loads(b0_summary_path.read_text())
        if b0_summary.get("status") != "PASS" or not all(
                b0_summary.get("gates", {}).values()):
            raise RuntimeError("formal B0 summary is not fully qualified")
    if durable.exists() and not overwrite:
        raise RuntimeError(f"durable arm already exists; inspect before overwrite: {durable}")
    out = LOCAL_RAW / arm
    if out.exists() and not overwrite:
        raise RuntimeError(f"local arm already exists; inspect before overwrite: {out}")
    lock = RUNTIME / "locks" / f"{arm}.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise RuntimeError(f"active/stale arm lock requires inspection: {lock}") from exc
    (lock / "owner.json").write_text(json.dumps({
        "pid": os.getpid(), "arm": arm,
        "start_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }, sort_keys=True) + "\n")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    command = (["nice", "-n", "10", str(BINARY), "-config", str(CONFIG),
                "-trace", str(kernelslist)] + trace_args() + vm_overlay())
    env = os.environ.copy()
    argv_sha256 = hashlib.sha256(
        json.dumps(command, separators=(",", ":")).encode()).hexdigest()
    if argv_sha256 != EXPECTED_ARGV_SHA256:
        raise RuntimeError(f"formal argv drift: {argv_sha256}")
    for key in tuple(env):
        if key.startswith("AWMA_TRANSIENT_L2") or key.startswith("GPGPUSIM_"):
            env.pop(key, None)
    env["LD_LIBRARY_PATH"] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    env.update(
        AWMA_TRANSIENT_L2_MODE=MODES[arm],
        AWMA_TRANSIENT_L2_DIAGNOSTICS="1",
        AWMA_TRANSIENT_L2_DRAIN="1",
        AWMA_TRANSIENT_L2_SIDECAR=str(sidecar),
        GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH="1",
        GPGPUSIM_READY_APPLICATION_V2="0",
        GPGPUSIM_VM_COVERAGE_KERNEL_UID="all",
        GPGPUSIM_READY_APPLICATION_DIAGNOSTICS="1",
        GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS="1",
    )
    receipt = {
        "stage": STAGE,
        "arm": arm,
        "mode": MODES[arm],
        "argv": command,
        "argv_sha256": argv_sha256,
        "environment": {
            key: env[key] for key in sorted(env)
            if key.startswith("AWMA_TRANSIENT_L2") or key.startswith("GPGPUSIM_")
        },
        "binary_sha256": sha(BINARY),
        "config_sha256": sha(CONFIG),
        "core_library_path": str(CORE_LIBRARY),
        "core_library_sha256": sha(CORE_LIBRARY),
        "trace_config_sha256": sha(TRACE_CONFIG),
        "framework_source_sha256": sha(REPO / "gpu-simulator/accel-sim.cc"),
        "admission": admission,
        "admission_receipt_sha256": sha(admission_path),
        "summarizer_sha256": sha(SUMMARIZER),
        "source_authority": {
            "checkpoint": "f9ecc837e0b7e770135ff52859fdc7fc4de512d2",
            "core_patch_sha256": sha(CORE_PATCH),
        },
    }
    (out / "command.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    (out / "start_utc.txt").write_text(
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + "\n")
    started = time.monotonic()
    rc = 124
    with (out / "run.log").open("w") as stdout, (out / "run.stderr").open("w") as stderr:
        try:
            rc = subprocess.run(command, cwd=out, env=env, stdout=stdout,
                                stderr=stderr, timeout=timeout).returncode
        except subprocess.TimeoutExpired:
            pass
    (out / "rc.txt").write_text(f"{rc}\n")
    (out / "wall_seconds.txt").write_text(f"{time.monotonic()-started:.6f}\n")
    if sha(SUMMARIZER) != EXPECTED_SUMMARIZER_SHA256:
        raise RuntimeError("formal summarizer changed during run")
    summary_rc = subprocess.run(
        ["python3", str(SUMMARIZER), str(out)], cwd=REPO).returncode
    passed = rc == 0 and summary_rc == 0
    if passed:
        publish = durable
    else:
        failure_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        publish = DURABLE_RAW / "failed" / f"{arm}_{failure_stamp}_{os.getpid()}"
    publish.parent.mkdir(parents=True, exist_ok=True)
    temporary = publish.parent / f".{publish.name}.tmp.{os.getpid()}"
    backup = durable.parent / f".{arm}.backup.{os.getpid()}"
    for path in (temporary, backup):
        if path.exists():
            shutil.rmtree(path)
    shutil.copytree(out, temporary)
    if file_hashes(out) != file_hashes(temporary):
        raise RuntimeError("temporary durable copy hash mismatch")
    if passed and durable.exists():
        os.replace(durable, backup)
    try:
        os.replace(temporary, publish)
    except Exception:
        if backup.exists() and not durable.exists():
            os.replace(backup, durable)
        raise
    if backup.exists():
        shutil.rmtree(backup)
    (lock / "owner.json").unlink()
    lock.rmdir()
    return {"arm": arm, "rc": rc, "summary_rc": summary_rc,
            "published": str(publish),
            "status": "PASS" if passed else "FAIL"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("arm", choices=tuple(MODES))
    parser.add_argument("--timeout-seconds", type=int, default=86400)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    result = run(args.arm, args.timeout_seconds, args.overwrite)
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
