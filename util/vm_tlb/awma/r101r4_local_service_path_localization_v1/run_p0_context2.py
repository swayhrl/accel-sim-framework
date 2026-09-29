#!/usr/bin/env python3
"""Frozen single-arm launcher for the R101R4 P0 CONTEXT2 screen."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import platform
import shlex
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STAGE = "AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_V1"
ORACLE_LABEL = "P0_FINITE_PREL1_SERVICE"
REPO = Path(
    "/root/workspace/accel-sim-framework-awma-r101r4-local-service-path-localization-174-v1"
)
RUNTIME = Path("/root/awma_r101r4_local_service_path_localization_174_v1_runtime")
DURABLE = Path(
    "/root/share/mnt164/huangrulin/awma_r101r4_local_service_path_localization_174_v1"
)
INPUT = Path(
    "/root/share/mnt164/huangrulin/"
    "awma_r101r2_context2_memory_service_174_v1/input"
)
RAW = DURABLE / "raw/formal"
PACK = REPO / (
    "docs/vm_tlb/review_packs/"
    "AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_174_V1"
)
BINARY = RUNTIME / "bin/unified_accel-sim.out"
CORE_LIB = RUNTIME / "src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release"
CORE_LIBRARY = CORE_LIB / "libcudart.so"
CONFIG = REPO / "configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config"
TRACE_CONFIG = REPO / (
    "gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config"
)
SIDECAR = INPUT / "transient_l2_runtime.tsv"
KERNELSLIST = INPUT / "traces/kernelslist.g"
DERIVATION = INPUT / "CONTEXT2_DERIVATION_RECEIPT.json"
KERNELS_TABLE = INPUT / "CONTEXT2_KERNELS.tsv"
CORE_PATCH = PACK / "P0_CORE.patch"
SUMMARIZER = REPO / (
    "util/vm_tlb/awma/r101r4_local_service_path_localization_v1/"
    "summarize_p0_context2.py"
)
MODES = {"P0": "p0_finite_prel1"}
EXPECTED = {
    "binary": "58bbf36b806019a9d8a3cfca1fc20ab53025108b7e0bc8c6f1598140cea7da81",
    "core_library": "2e92547b9de11414888fc5a56adcde7b692138af2e906d7c8e8f9a2368b85ec4",
    "core_patch": "d8a07ee16f25372cb39460c530d509801961d739f7f409226388043b157536bb",
    "config": "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8",
    "trace_config": "a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b",
    "framework": "c6a8e6315226c6d45ae93f2280999d5975328d306cb09f161f1d4d73f3ef4323",
    "derivation_receipt": "b560ee7a6947854f9123ce739af5befe788d2e17caa74292ca0a0b9a4597882d",
    "kernels_table": "a9cf4bdbc3d551e9e7fc0d41b84a65e89d148085ea92940f04366c2e71704a65",
    "sidecar": "67adc56216f25bfc88c98d86aabdf1eeaae87e9f2f8e102f675d5be8ec11e7b5",
    "kernelslist": "73f3d8c9546c06fb81aee209868c9e15e61b0bcfb900b5435c83d520e782748a",
}
EXPECTED_ARGV_SHA256 = "94dc628b9944860bf48464565bd43fdf69e357b2efab171171c7e354e6c9c1b9"
EXPECTED_SUMMARIZER_SHA256 = "28cd178d737979e747b84a414cd3efc3f1844d3cc6ed0514d8a9cdb9e464ccee"
TRACE_AGGREGATE_SHA256 = (
    "4fee01b73c9076378aeb583ea65254c5d3882c71ab2d0f2aeac857bc25edf2ce"
)
EXPECTED_MEMBERS = (
    ("kernel-3580-ctx_0x43c6c760.traceg.xz", "3ce2aaa2279de0ebdc1b022b39cdef453563620e123c45763c87d748f405ca74"),
    ("kernel-3581-ctx_0x43c6c760.traceg.xz", "d78ab55806f04a6788c32af0c577bfe8f4f1282aa5211df6b9506bb67aaa31b7"),
    ("kernel-3582-ctx_0x43c6c760.traceg.xz", "bab2f4d9e5ace8c1de25617b815b8426510429a19d6ac0e1c2d6b0c141ecc64d"),
    ("kernel-3583-ctx_0x43c6c760.traceg.xz", "22cfb5590fef79895139ffc4ac9db5102981a35baf991349c1ce605cde8ddbbd"),
    ("kernel-3584-ctx_0x43c6c760.traceg.xz", "d01f8c681eeb25fce7534f11db45dbb9dc79bc4c5229ee80b5719a19e8fee086"),
    ("kernel-3585-ctx_0x43c6c760.traceg.xz", "6cc3b8f455631135acfa727a9c4bb0329f65bb896ca3238fc9e4332bfce67a1e"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def artifact_hashes() -> dict[str, str]:
    paths = {
        "binary": BINARY,
        "core_library": CORE_LIBRARY,
        "core_patch": CORE_PATCH,
        "config": CONFIG,
        "trace_config": TRACE_CONFIG,
        "framework": REPO / "gpu-simulator/accel-sim.cc",
        "derivation_receipt": DERIVATION,
        "kernels_table": KERNELS_TABLE,
        "sidecar": SIDECAR,
        "kernelslist": KERNELSLIST,
    }
    return {key: sha256(path) for key, path in paths.items()}


def trace_args() -> list[str]:
    result: list[str] = []
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


def command() -> list[str]:
    return [
        "/usr/bin/nice", "-n", "10", str(BINARY),
        "-config", str(CONFIG), "-trace", str(KERNELSLIST),
    ] + trace_args() + vm_overlay()


def formal_environment(arm: str) -> dict[str, str]:
    return {
        "AWMA_R101R2_TRANSIENT_SERVICE_MODE": "none",
        "AWMA_R101R3_SERVICE_MODE": "none",
        "AWMA_R101R3_DIAGNOSTICS": "0",
        "AWMA_R101R4_SERVICE_MODE": MODES[arm],
        "AWMA_R101R4_DIAGNOSTICS": "1",
        "AWMA_TRANSIENT_L2_DIAGNOSTICS": "1",
        "AWMA_TRANSIENT_L2_DRAIN": "1",
        "AWMA_TRANSIENT_L2_MODE": "none",
        "AWMA_TRANSIENT_L2_SIDECAR": str(SIDECAR),
        "CUDA_INSTALL_PATH": (
            "/root/workspace/accel-sim-framework-awma-174-translation-frontend-"
            "pipelining-v1/.awma_runtime/candidate/toolchains/"
            "cuda-12.4.131-combined"
        ),
        "GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH": "1",
        "GPGPUSIM_READY_APPLICATION_DIAGNOSTICS": "1",
        "GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS": "1",
        "GPGPUSIM_READY_APPLICATION_V2": "0",
        "GPGPUSIM_ROOT": str(RUNTIME / "src/gpgpu-sim"),
        "GPGPUSIM_VM_COVERAGE_KERNEL_UID": "all",
        "LANG": "C",
        "LC_ALL": "C",
        "LD_LIBRARY_PATH": str(CORE_LIB),
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    }


def input_receipt() -> dict[str, Any]:
    receipt = json.loads(DERIVATION.read_text())
    if receipt.get("schema_version") != "AWMA_R101R2_CONTEXT2_DERIVATION_RECEIPT_V1":
        raise RuntimeError("derived input receipt schema drift")
    if receipt.get("derived_input_identity") != "R101_L512_NS_CONTEXT2_EXECORG_V1":
        raise RuntimeError("derived input identity drift")
    authorities = receipt.get("authorities", {})
    if authorities.get("producer_commit") != "bb902283b7ce9e1902b460383fbd3e0bedbd884d":
        raise RuntimeError("producer authority drift")
    if authorities.get("coordination_handoff_commit") != "8542a4d37372d586591ff9911929e523645e88f5":
        raise RuntimeError("handoff authority drift")
    selection = receipt.get("selection", [])
    pairs = [(item.get("member"), item.get("sha256")) for item in selection]
    if pairs != list(EXPECTED_MEMBERS):
        raise RuntimeError("selected trace identity/order drift")
    if [item.get("source_launch_index") for item in selection] != list(range(3, 9)):
        raise RuntimeError("source launch selection is not exact 3..8")
    if [item.get("derived_ordinal") for item in selection] != list(range(1, 7)):
        raise RuntimeError("derived ordinal sequence drift")
    if [item.get("l512_tile_count") for item in selection] != [44] * 6:
        raise RuntimeError("L512 tile identity drift")
    members = []
    binding = bytearray()
    for item, (name, expected_hash) in zip(selection, EXPECTED_MEMBERS):
        consumer = INPUT / "traces" / name
        source = Path(item["source_realpath"])
        if not consumer.is_symlink() or not consumer.samefile(source):
            raise RuntimeError(f"trace is not zero-copy samefile: {consumer}")
        actual_hash = sha256(consumer)
        if actual_hash != expected_hash:
            raise RuntimeError(f"trace member drift: {consumer}")
        binding.extend(f"{name}\t{actual_hash}\n".encode())
        members.append({
            "path": str(consumer),
            "realpath": str(consumer.resolve()),
            "sha256": actual_hash,
            "source_launch_index": item["source_launch_index"],
            "derived_ordinal": item["derived_ordinal"],
            "function": item["function"],
            "role": item["role"],
        })
    aggregate = hashlib.sha256(binding).hexdigest()
    if aggregate != TRACE_AGGREGATE_SHA256:
        raise RuntimeError("ordered trace aggregate drift")
    derived = receipt.get("derived_artifacts", {})
    if (
        derived.get("kernelslist_sha256") != EXPECTED["kernelslist"]
        or derived.get("runtime_sidecar_sha256") != EXPECTED["sidecar"]
        or derived.get("kernels_table_sha256") != EXPECTED["kernels_table"]
    ):
        raise RuntimeError("derived artifact binding drift")
    roi = receipt.get("roi_contract", {})
    if (
        roi.get("context_members") != [1, 2, 3]
        or roi.get("measured_members") != [4, 5, 6]
        or "cycle_after_derived_ordinal_6_BMM-cycle_after_derived_ordinal_3_BMM"
        not in roi.get("formula", "")
    ):
        raise RuntimeError("ROI boundary contract drift")
    return {
        "identity": receipt["derived_input_identity"],
        "producer_commit": authorities["producer_commit"],
        "coordination_handoff_commit": authorities["coordination_handoff_commit"],
        "accepted_payload_sha256": authorities.get("accepted_payload_sha256"),
        "accepted_output_sha256": authorities.get("accepted_output_sha256"),
        "derivation_receipt_sha256": sha256(DERIVATION),
        "kernels_table_sha256": sha256(KERNELS_TABLE),
        "kernelslist_sha256": sha256(KERNELSLIST),
        "runtime_sidecar_sha256": sha256(SIDECAR),
        "ordered_trace_aggregate_sha256": aggregate,
        "trace_members": members,
        "context_ordinals": [1, 2, 3],
        "measured_roi_ordinals": [4, 5, 6],
        "roi_formula": "end_cycle_ordinal_6-end_cycle_ordinal_3",
        "zero_copy": True,
    }


def memory_available_bytes() -> int:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) * 1024
    raise RuntimeError("MemAvailable is unavailable")


def resource_audit(workers: int, min_mem_gib: int, min_durable_gib: int) -> dict[str, Any]:
    memory = memory_available_bytes()
    durable_free = shutil.disk_usage(DURABLE).free
    runtime_free = shutil.disk_usage(RUNTIME).free
    required_memory = workers * min_mem_gib * (1 << 30)
    required_durable = min_durable_gib * (1 << 30)
    cpu_count = os.cpu_count() or 0
    gates = {
        "worker_limit_at_most_2": 1 <= workers <= 2,
        "cpu_capacity": cpu_count >= workers,
        "memory_capacity": memory >= required_memory,
        "durable_capacity": durable_free >= required_durable,
        "runtime_lock_capacity": runtime_free >= 2 * (1 << 30),
    }
    audit = {
        "host": platform.node(),
        "workers": workers,
        "cpu_count": cpu_count,
        "memory_available_bytes": memory,
        "memory_required_bytes": required_memory,
        "durable_free_bytes": durable_free,
        "durable_required_bytes": required_durable,
        "runtime_free_bytes": runtime_free,
        "gates": gates,
        "status": "PASS" if all(gates.values()) else "FAIL",
    }
    if audit["status"] != "PASS":
        raise RuntimeError(f"host resource audit failed: {audit}")
    return audit


def preflight() -> dict[str, Any]:
    frozen = artifact_hashes()
    if frozen != EXPECTED:
        raise RuntimeError(f"frozen artifact drift: {frozen}")
    summarizer_hash = sha256(SUMMARIZER)
    if summarizer_hash != EXPECTED_SUMMARIZER_SHA256:
        raise RuntimeError(f"formal summarizer drift: {summarizer_hash}")
    argv = command()
    argv_hash = hashlib.sha256(
        json.dumps(argv, separators=(",", ":")).encode()
    ).hexdigest()
    if argv_hash != EXPECTED_ARGV_SHA256:
        raise RuntimeError(f"formal argv drift: {argv_hash}")
    return {
        "artifact_receipt": frozen,
        "input_receipt": input_receipt(),
        "argv": argv,
        "argv_sha256": argv_hash,
        "summarizer_sha256": summarizer_hash,
        "runner_sha256": sha256(Path(__file__)),
    }


def acquire_lock(arm: str) -> tuple[Path, str]:
    lock = RUNTIME / "locks" / f"formal_{arm}.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise RuntimeError(f"active/stale lock requires inspection: {lock}") from exc
    atomic_json(lock / "owner.json", {
        "arm": arm,
        "host": platform.node(),
        "pid": os.getpid(),
        "token": token,
        "start_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
    return lock, token


def release_lock(lock: Path, token: str) -> None:
    owner = json.loads((lock / "owner.json").read_text())
    if owner.get("token") != token:
        raise RuntimeError(f"refusing to release foreign lock: {lock}")
    (lock / "owner.json").unlink()
    lock.rmdir()


def publish_directory(source: Path, destination: Path, overwrite: bool) -> None:
    backup = destination.parent / f".{destination.name}.backup.{os.getpid()}.{uuid.uuid4().hex}"
    if destination.exists():
        if not overwrite:
            raise RuntimeError(f"durable arm already exists: {destination}")
        os.replace(destination, backup)
    try:
        os.replace(source, destination)
    except Exception:
        if backup.exists() and not destination.exists():
            os.replace(backup, destination)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def run_arm(
    arm: str,
    timeout: int,
    overwrite: bool,
    host_audit: dict[str, Any],
) -> dict[str, Any]:
    lock, token = acquire_lock(arm)
    out = RAW / f".inflight.{arm}.{os.getpid()}.{uuid.uuid4().hex}"
    started_simulation = False
    published = False
    try:
        frozen = preflight()
        destination = RAW / arm
        if destination.exists() and not overwrite:
            raise RuntimeError(f"durable arm already exists: {destination}")
        RAW.mkdir(parents=True, exist_ok=True)
        out.mkdir()
        argv = frozen["argv"]
        environment = formal_environment(arm)
        receipt = {
            "stage": STAGE,
            "arm": arm,
            "mode": MODES[arm],
            "oracle_label": ORACLE_LABEL,
            "argv": argv,
            "argv_sha256": frozen["argv_sha256"],
            "environment": environment,
            "artifact_receipt": frozen["artifact_receipt"],
            "input_receipt": frozen["input_receipt"],
            "host_resource_audit": host_audit,
            "formal_tools": {
                "runner_path": str(Path(__file__).resolve()),
                "runner_sha256": frozen["runner_sha256"],
                "summarizer_path": str(SUMMARIZER),
                "summarizer_sha256": frozen["summarizer_sha256"],
            },
            "output_contract": {
                "working_directory": str(out),
                "durable_destination": str(destination),
                "atomic_publish": True,
                "large_raw_local_staging": False,
            },
        }
        atomic_json(out / "command.json", receipt)
        (out / "start_utc.txt").write_text(
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + "\n"
        )
        started = time.monotonic()
        rc = 124
        with (out / "run.log").open("w") as stdout, (out / "run.stderr").open("w") as stderr:
            started_simulation = True
            try:
                rc = subprocess.run(
                    argv, cwd=out, env=environment, stdout=stdout, stderr=stderr,
                    timeout=timeout, check=False,
                ).returncode
            except subprocess.TimeoutExpired:
                pass
        (out / "rc.txt").write_text(f"{rc}\n")
        (out / "wall_seconds.txt").write_text(f"{time.monotonic() - started:.6f}\n")
        (out / "end_utc.txt").write_text(
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + "\n"
        )
        after = preflight()
        if after["runner_sha256"] != frozen["runner_sha256"]:
            raise RuntimeError("formal runner changed during arm execution")
        summary_rc = subprocess.run(
            ["/usr/bin/python3", str(SUMMARIZER), str(out)],
            cwd=REPO, check=False,
        ).returncode
        passed = rc == 0 and summary_rc == 0
        if passed:
            publish = destination
        else:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            publish = RAW / "failed" / f"{arm}_{stamp}_{os.getpid()}_{uuid.uuid4().hex[:8]}"
            publish.parent.mkdir(parents=True, exist_ok=True)
        publish_directory(out, publish, overwrite if passed else False)
        published = True
        return {
            "arm": arm,
            "rc": rc,
            "summary_rc": summary_rc,
            "published": str(publish),
            "status": "PASS" if passed else "FAIL",
        }
    except Exception as exc:
        if out.exists() and not published:
            try:
                atomic_json(out / "ORCHESTRATION_ERROR.json", {
                    "arm": arm,
                    "error": str(exc),
                    "simulation_started": started_simulation,
                })
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                failure = RAW / "failed" / f"{arm}_{stamp}_{os.getpid()}_{uuid.uuid4().hex[:8]}"
                failure.parent.mkdir(parents=True, exist_ok=True)
                os.replace(out, failure)
            except Exception:
                pass
        raise
    finally:
        release_lock(lock, token)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("arms", nargs="+", choices=tuple(MODES))
    parser.add_argument("--max-workers", type=int, choices=(1, 2), default=1)
    parser.add_argument("--timeout-seconds", type=int, default=86400)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--min-mem-gib-per-worker", type=int, default=32)
    parser.add_argument("--min-durable-free-gib", type=int, default=10)
    args = parser.parse_args()
    if len(set(args.arms)) != len(args.arms):
        raise SystemExit("duplicate arm requested")
    workers = min(args.max_workers, len(args.arms))
    try:
        host_audit = resource_audit(
            workers, args.min_mem_gib_per_worker, args.min_durable_free_gib
        )
        frozen = preflight()
    except (OSError, ValueError, KeyError, json.JSONDecodeError, RuntimeError) as exc:
        print(json.dumps({
            "stage": STAGE,
            "status": "FAIL_CLOSED",
            "error": str(exc),
            "simulation_started": False,
        }, sort_keys=True))
        return 2
    if args.preflight_only:
        print(json.dumps({
            "stage": STAGE,
            "status": "PREFLIGHT_PASS",
            "arms": args.arms,
            "workers": workers,
            "host_resource_audit": host_audit,
            "artifact_receipt": frozen["artifact_receipt"],
            "input_receipt": frozen["input_receipt"],
            "argv_sha256": frozen["argv_sha256"],
            "summarizer_sha256": frozen["summarizer_sha256"],
            "simulation_started": False,
        }, sort_keys=True))
        return 0

    results: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                run_arm, arm, args.timeout_seconds, args.overwrite, host_audit
            ): arm
            for arm in args.arms
        }
        for future in concurrent.futures.as_completed(futures):
            arm = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                failures.append({"arm": arm, "error": str(exc)})
    results.sort(key=lambda item: args.arms.index(str(item["arm"])))
    status = (
        "PASS" if not failures and all(item["status"] == "PASS" for item in results)
        else "FAIL"
    )
    print(json.dumps({
        "stage": STAGE,
        "status": status,
        "workers": workers,
        "results": results,
        "failures": failures,
    }, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
