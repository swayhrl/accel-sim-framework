#!/usr/bin/env python3
"""Fail-closed single-arm summarizer for the R101R3 S1 CONTEXT2 screen."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any


STAGE = "AWMA_R101R3_BOUNDED_SERVICE_HANDOFF_V1"
ORACLE_LABEL = "S1_PARTITION_HIT_SERVICE"
REPO = Path(
    "/root/workspace/accel-sim-framework-awma-r101r3-bounded-service-handoff-174-v1"
)
RUNTIME = Path("/root/awma_r101r3_bounded_service_handoff_174_v1_runtime")
INPUT = Path(
    "/root/share/mnt164/huangrulin/awma_r101r2_context2_memory_service_174_v1/input"
)
PACK = REPO / (
    "docs/vm_tlb/review_packs/"
    "AWMA_R101R3_BOUNDED_SERVICE_HANDOFF_174_V1"
)
CONFIG = REPO / "configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config"
TRACE_CONFIG = REPO / (
    "gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config"
)
RUNNER = REPO / (
    "util/vm_tlb/awma/r101r3_bounded_service_handoff_v1/"
    "run_s1_context2.py"
)
FORMAL_AT_RUN_RUNNER_SHA256 = (
    "52b4d37534257421eef37ec1e2138ff5a158731e441ec2eff3356870b55a21e6"
)
FORMAL_AT_RUN_SUMMARIZER_SHA256 = (
    "af69ab68e08a8f8ae871c162b4088ac332372ff6dbb6932c7a7cc7735d6427c3"
)
PATHS = {
    "binary": RUNTIME / "bin/unified_accel-sim.out",
    "core_library": (
        RUNTIME / "src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release/libcudart.so"
    ),
    "core_patch": PACK / "S1_CORE.patch",
    "config": CONFIG,
    "trace_config": TRACE_CONFIG,
    "framework": REPO / "gpu-simulator/accel-sim.cc",
    "derivation_receipt": INPUT / "CONTEXT2_DERIVATION_RECEIPT.json",
    "kernels_table": INPUT / "CONTEXT2_KERNELS.tsv",
    "sidecar": INPUT / "transient_l2_runtime.tsv",
    "kernelslist": INPUT / "traces/kernelslist.g",
}
EXPECTED_ARTIFACTS = {
    "binary": "ae3a71d8b75bb6e4b019b0f355801d5e529a3178085d9e8c9671dffee4f1cdfc",
    "core_library": "2abc6cdc694a245edf0a61606bad7a9ef487e16da07802cbc32f74e29ebc68fd",
    "core_patch": "768804050c22cb85168b2e73daa6414fcd6c519b429dd000ceaec84bfdf037a4",
    "config": "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8",
    "trace_config": "a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b",
    "framework": "c6a8e6315226c6d45ae93f2280999d5975328d306cb09f161f1d4d73f3ef4323",
    "derivation_receipt": "b560ee7a6947854f9123ce739af5befe788d2e17caa74292ca0a0b9a4597882d",
    "kernels_table": "a9cf4bdbc3d551e9e7fc0d41b84a65e89d148085ea92940f04366c2e71704a65",
    "sidecar": "67adc56216f25bfc88c98d86aabdf1eeaae87e9f2f8e102f675d5be8ec11e7b5",
    "kernelslist": "73f3d8c9546c06fb81aee209868c9e15e61b0bcfb900b5435c83d520e782748a",
}
EXPECTED_ARGV_SHA256 = "8062c4e7e56ccde05fd44576a22c67cc0acb4d587eea41e3c32d372356d02a12"
TRACE_AGGREGATE_SHA256 = (
    "4fee01b73c9076378aeb583ea65254c5d3882c71ab2d0f2aeac857bc25edf2ce"
)
MODES = {"S1": "s1_partition_hit"}
EXPECTED_NAMES = (
    "XXT_kernel", "ba_plus_cAA_kernel", "bmm_add_kernel",
    "XXT_kernel", "ba_plus_cAA_kernel", "bmm_add_kernel",
)
EXPECTED_MEMBERS = (
    ("kernel-3580-ctx_0x43c6c760.traceg.xz", "3ce2aaa2279de0ebdc1b022b39cdef453563620e123c45763c87d748f405ca74"),
    ("kernel-3581-ctx_0x43c6c760.traceg.xz", "d78ab55806f04a6788c32af0c577bfe8f4f1282aa5211df6b9506bb67aaa31b7"),
    ("kernel-3582-ctx_0x43c6c760.traceg.xz", "bab2f4d9e5ace8c1de25617b815b8426510429a19d6ac0e1c2d6b0c141ecc64d"),
    ("kernel-3583-ctx_0x43c6c760.traceg.xz", "22cfb5590fef79895139ffc4ac9db5102981a35baf991349c1ce605cde8ddbbd"),
    ("kernel-3584-ctx_0x43c6c760.traceg.xz", "d01f8c681eeb25fce7534f11db45dbb9dc79bc4c5229ee80b5719a19e8fee086"),
    ("kernel-3585-ctx_0x43c6c760.traceg.xz", "6cc3b8f455631135acfa727a9c4bb0329f65bb896ca3238fc9e4332bfce67a1e"),
)
EXPECTED_CUMULATIVE_INSTRUCTIONS = (
    318365440, 670072320, 1217463296,
    1535828736, 1887535616, 2434926592,
)
EXPECTED_CUMULATIVE_CTAS = (2816, 5632, 7040, 9856, 12672, 14080)

CONTROLLER_INT_KEYS = (
    "awma_transient_l2_expected_kernels",
    "awma_transient_l2_launched_kernels",
    "awma_transient_l2_completed_kernels",
    "awma_transient_l2_pre_transitions",
    "awma_transient_l2_post_transitions",
    "awma_transient_l2_descriptor_transitions",
    "awma_transient_l2_transient_accesses",
    "awma_transient_l2_transient_admissions",
    "awma_transient_l2_protected_victim_deflections",
    "awma_transient_l2_forced_live_evictions",
    "awma_transient_l2_dead_victim_selections",
    "awma_transient_l2_ordinary_victim_selections",
    "awma_transient_l2_fallback_count",
    "awma_transient_l2_l2_writebacks",
    "awma_transient_l2_l2_writeback_bytes",
    "awma_transient_l2_completed_l2_writebacks",
    "awma_transient_l2_outstanding_l2_writebacks",
    "awma_transient_l2_transient_writebacks",
    "awma_transient_l2_transient_writeback_bytes",
    "awma_transient_l2_dead_eviction_drops",
    "awma_transient_l2_dead_eviction_drop_bytes",
    "awma_transient_l2_oracle_drop_lines",
    "awma_transient_l2_oracle_drop_dirty_lines",
    "awma_transient_l2_oracle_drop_bytes",
    "awma_transient_l2_oracle_reserved_skips",
    "awma_r101r2_service_selector_explicit",
    "awma_r101r2_context_end_ordinal",
    "awma_r101r2_roi_start_ordinal",
    "awma_r101r2_roi_end_ordinal",
    "awma_r101r2_active_kernel_ordinal",
    "awma_r101r2_context_end_cycle_valid",
    "awma_r101r2_context_end_cycle",
    "awma_r101r2_roi_end_cycle_valid",
    "awma_r101r2_roi_end_cycle",
    "awma_r101r2_roi_cycles",
    "awma_r101r2_pre_roi_receipt_valid",
    "awma_r101r2_pre_roi_cycle",
    "awma_r101r2_service_inactive_intersections",
    "awma_r101r2_service_inactive_bytes",
    "awma_r101r2_service_dead_skips",
    "awma_r101r2_service_partial_skips",
    "awma_r101r2_service_multi_region_skips",
    "awma_r101r2_service_invalid_range_skips",
    "awma_r101r2_service_atomic_fail_closed",
    "awma_r101r2_service_unsupported_fail_closed",
    "awma_r101r2_service_fail_closed_bytes",
    "awma_r101r2_service_qualified_reads",
    "awma_r101r2_service_qualified_ldg_reads",
    "awma_r101r2_service_qualified_ldgsts_reads",
    "awma_r101r2_service_qualified_ldgsts_bytes",
    "awma_r101r2_service_qualified_read_bytes",
    "awma_r101r2_service_qualified_read_active_bytes",
    "awma_r101r2_service_qualified_writes",
    "awma_r101r2_service_qualified_write_bytes",
    "awma_r101r2_service_qualified_write_active_bytes",
    "awma_r101r2_service_scheduled",
    "awma_r101r2_service_one_cycle_ready",
    "awma_r101r2_service_retired_reads",
    "awma_r101r2_service_retired_ldg_reads",
    "awma_r101r2_service_retired_ldgsts_reads",
    "awma_r101r2_service_retired_writes",
    "awma_r101r2_service_outstanding",
    "awma_r101r2_service_duplicate_completions",
    "awma_r101r2_service_latency_violations",
    "awma_r101r2_service_stale_token_violations",
    "awma_r101r2_service_max_scheduled_depth",
    "awma_r101r2_service_max_ready_depth",
    "awma_r101r2_service_semantics_qualified",
    "awma_r101r3_selector_explicit",
    "awma_r101r3_diagnostics",
    "awma_r101r3_s1_inactive_intersections",
    "awma_r101r3_s1_head_qualified_cycles",
    "awma_r101r3_s1_dram_queue_full_cycles",
    "awma_r101r3_s1_return_queue_full_cycles",
    "awma_r101r3_s1_data_port_busy_cycles",
    "awma_r101r3_s1_max_ingress_depth",
    "awma_r101r3_s1_max_return_depth",
    "awma_r101r3_s1_fallback_requests",
    "awma_r101r3_s1_dead_fail_closed",
    "awma_r101r3_s1_partial_fail_closed",
    "awma_r101r3_s1_multi_region_fail_closed",
    "awma_r101r3_s1_invalid_range_fail_closed",
    "awma_r101r3_s1_atomic_fail_closed",
    "awma_r101r3_s1_unsupported_fail_closed",
    "awma_r101r3_s1_served_reads",
    "awma_r101r3_s1_served_ldg_reads",
    "awma_r101r3_s1_served_ldgsts_reads",
    "awma_r101r3_s1_served_writes",
    "awma_r101r3_s1_served_request_bytes",
    "awma_r101r3_s1_served_active_bytes",
    "awma_r101r3_s1_context_served",
    "awma_r101r3_s1_duplicate_completions",
    "awma_r101r3_s1_subpartition_mask",
    "awma_r101r3_s1_semantics_qualified",
    "awma_transient_l2_terminal_quiescent",
)
SERVICE_ACCOUNTING_KEYS = (
    "awma_r101r2_service_qualified_reads",
    "awma_r101r2_service_qualified_ldg_reads",
    "awma_r101r2_service_qualified_ldgsts_reads",
    "awma_r101r2_service_qualified_ldgsts_bytes",
    "awma_r101r2_service_qualified_read_bytes",
    "awma_r101r2_service_qualified_read_active_bytes",
    "awma_r101r2_service_qualified_writes",
    "awma_r101r2_service_qualified_write_bytes",
    "awma_r101r2_service_qualified_write_active_bytes",
    "awma_r101r2_service_scheduled",
    "awma_r101r2_service_one_cycle_ready",
    "awma_r101r2_service_retired_reads",
    "awma_r101r2_service_retired_ldg_reads",
    "awma_r101r2_service_retired_ldgsts_reads",
    "awma_r101r2_service_retired_writes",
    "awma_r101r2_service_outstanding",
    "awma_r101r2_service_duplicate_completions",
    "awma_r101r2_service_latency_violations",
    "awma_r101r2_service_stale_token_violations",
    "awma_r101r2_service_max_scheduled_depth",
    "awma_r101r2_service_max_ready_depth",
)
FAIL_CLOSED_KEYS = (
    "awma_r101r2_service_dead_skips",
    "awma_r101r2_service_partial_skips",
    "awma_r101r2_service_multi_region_skips",
    "awma_r101r2_service_invalid_range_skips",
    "awma_r101r2_service_atomic_fail_closed",
    "awma_r101r2_service_unsupported_fail_closed",
    "awma_r101r2_service_fail_closed_bytes",
    "awma_r101r2_service_stale_token_violations",
)
POLICY_EFFECT_KEYS = (
    "awma_transient_l2_protected_victim_deflections",
    "awma_transient_l2_forced_live_evictions",
    "awma_transient_l2_fallback_count",
    "awma_transient_l2_dead_eviction_drops",
    "awma_transient_l2_dead_eviction_drop_bytes",
    "awma_transient_l2_oracle_drop_lines",
    "awma_transient_l2_oracle_drop_dirty_lines",
    "awma_transient_l2_oracle_drop_bytes",
    "awma_transient_l2_oracle_reserved_skips",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def last_int(text: str, key: str) -> int | None:
    values = re.findall(
        rf"^{re.escape(key)}\s*=\s*(\d+)\s*$", text, re.MULTILINE
    )
    return int(values[-1]) if values else None


def last_float(text: str, key: str) -> float | None:
    values = re.findall(
        rf"^{re.escape(key)}\s*=\s*([0-9.eE+-]+)\s*$", text, re.MULTILINE
    )
    return float(values[-1]) if values else None


def last_token(text: str, key: str) -> str | None:
    values = re.findall(
        rf"^{re.escape(key)}\s*=\s*(\S+)\s*$", text, re.MULTILINE
    )
    return values[-1] if values else None


def last_hex(text: str, key: str) -> str | None:
    values = re.findall(
        rf"^{re.escape(key)}\s*=\s*([0-9a-fA-F]+)\s*$", text, re.MULTILINE
    )
    return values[-1].lower() if values else None


def expected_environment(arm: str) -> dict[str, str]:
    return {
        "AWMA_R101R2_TRANSIENT_SERVICE_MODE": "none",
        "AWMA_R101R3_SERVICE_MODE": MODES[arm],
        "AWMA_R101R3_DIAGNOSTICS": "1",
        "AWMA_TRANSIENT_L2_DIAGNOSTICS": "1",
        "AWMA_TRANSIENT_L2_DRAIN": "1",
        "AWMA_TRANSIENT_L2_MODE": "none",
        "AWMA_TRANSIENT_L2_SIDECAR": str(INPUT / "transient_l2_runtime.tsv"),
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
        "LD_LIBRARY_PATH": str(
            RUNTIME / "src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release"
        ),
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    }


def controller(text: str) -> dict[str, int | str | None]:
    result: dict[str, int | str | None] = {
        key: last_int(text, key) for key in CONTROLLER_INT_KEYS
    }
    result["awma_transient_l2_mode"] = last_token(
        text, "awma_transient_l2_mode"
    )
    result["awma_r101r2_transient_service_mode"] = last_token(
        text, "awma_r101r2_transient_service_mode"
    )
    result["awma_r101r3_service_mode"] = last_token(
        text, "awma_r101r3_service_mode"
    )
    result["awma_r101r2_pre_roi_lifecycle_hash"] = last_hex(
        text, "awma_r101r2_pre_roi_lifecycle_hash"
    )
    return result


def snapshot(block: str, ordinal: int) -> dict[str, Any]:
    name_match = re.search(
        r"^kernel_name[ \t]*=[ \t]*(.*?)[ \t]*$", block, re.MULTILINE
    )
    l1_rows = [
        tuple(map(int, row))
        for row in re.findall(
            r"L1D_cache_core\[\d+\]: Access = (\d+), Miss = (\d+),"
            r".*?Reservation_fails = (\d+)", block
        )
    ]
    dram_rows = [
        tuple(map(int, row))
        for row in re.findall(
            r"n_rd=(\d+) n_rd_L2_A=(\d+) n_write=(\d+) n_wr_bk=(\d+)",
            block,
        )
    ]
    return {
        "ordinal": ordinal,
        "role": "CONTEXT" if 1 <= ordinal <= 3 else "MEASURED_ROI",
        "kernel_name": name_match.group(1).strip() if name_match else None,
        "kernel_launch_uid": last_int(block, "kernel_launch_uid"),
        "kernel_cycles": last_int(block, "gpu_sim_cycle"),
        "total_cycles": last_int(block, "gpu_tot_sim_cycle"),
        "total_instructions": last_int(block, "gpu_tot_sim_insn"),
        "total_ctas": last_int(block, "gpu_tot_issued_cta"),
        "l1d_core_rows": len(l1_rows),
        "l1d_accesses": sum(row[0] for row in l1_rows),
        "l1d_misses": sum(row[1] for row in l1_rows),
        "l1d_reservation_fails": sum(row[2] for row in l1_rows),
        "l2_accesses": last_int(block, "L2_total_cache_accesses"),
        "l2_misses": last_int(block, "L2_total_cache_misses"),
        "l2_miss_rate": last_float(block, "L2_total_cache_miss_rate"),
        "l2_reservation_fails": last_int(
            block, "L2_total_cache_reservation_fails"
        ),
        "dram_rows": len(dram_rows),
        "dram_n_rd": sum(row[0] for row in dram_rows),
        "dram_n_rd_l2_a": sum(row[1] for row in dram_rows),
        "dram_n_write": sum(row[2] for row in dram_rows),
        "dram_n_wr_bk": sum(row[3] for row in dram_rows),
        "controller": controller(block),
    }


def actual_members() -> list[dict[str, Any]]:
    result = []
    for name, expected_hash in EXPECTED_MEMBERS:
        path = INPUT / "traces" / name
        result.append({
            "name": name,
            "path": str(path),
            "realpath": str(path.resolve()),
            "sha256": sha256(path),
            "expected_sha256": expected_hash,
            "is_symlink": path.is_symlink(),
        })
    return result


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def fail_closed(run_dir: Path, message: str) -> int:
    result = {
        "stage": STAGE,
        "status": "FAIL_CLOSED",
        "error": message,
        "run_dir": str(run_dir),
    }
    print(json.dumps(result, sort_keys=True))
    return 2


def summarize(run_dir: Path) -> dict[str, Any]:
    required = tuple(run_dir / name for name in (
        "command.json", "run.log", "run.stderr", "rc.txt",
    ))
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise ValueError("missing run artifacts: " + ", ".join(missing))

    command = json.loads((run_dir / "command.json").read_text())
    arm = command.get("arm")
    if arm not in MODES:
        raise ValueError(f"unknown command arm: {arm!r}")
    text = (run_dir / "run.log").read_text(errors="strict")
    rc = int((run_dir / "rc.txt").read_text().strip())
    stderr_bytes = (run_dir / "run.stderr").stat().st_size
    argv_sha = hashlib.sha256(
        json.dumps(command.get("argv"), separators=(",", ":")).encode()
    ).hexdigest()
    blocks = re.split(r"(?=^kernel_name\s*=)", text, flags=re.MULTILINE)[1:]
    snapshots = [snapshot(blocks[index], index + 1) for index in range(min(6, len(blocks)))]
    terminal = snapshot(blocks[-1], 0) if blocks else {}
    final_controller = controller(text)
    context = snapshots[2] if len(snapshots) >= 3 else {}
    roi_end = snapshots[5] if len(snapshots) >= 6 else {}

    coverage_lines = re.findall(r"^AWMA_VM_COVERAGE .*?$", text, re.MULTILINE)
    coverage_records = [
        {key: int(value) for key, value in re.findall(r"(\w+)=(\d+)", line)}
        for line in coverage_lines
    ]
    coverage_keys = (
        "admissions", "translated", "untranslated", "unobserved", "unique",
        "translated_unique", "untranslated_unique",
    )
    coverage = {
        key: sum(record.get(key, 0) for record in coverage_records)
        for key in coverage_keys
    }
    coverage["kernels"] = len(coverage_records)

    drain_matches = re.findall(
        r"AWMA_TRANSIENT_L2_DRAIN enabled=1 cycles=(\d+) gpu_active=(\d+) "
        r"l2_writeback_active=(\d+) max_limit_hit=(\d+) gpu_deadlock=(\d+)",
        text,
    )
    drain = (
        dict(zip(
            ("cycles", "gpu_active", "l2_writeback_active", "max_limit_hit", "gpu_deadlock"),
            map(int, drain_matches[-1]),
        )) if drain_matches else {}
    )
    marker = text.rfind("gpu_sim_cycle =")
    terminal_text = text[marker:] if marker >= 0 else ""
    dram_latency_queues = [
        int(value) for value in re.findall(
            r"In Dram Latency Queue \(total = (\d+)\):", terminal_text
        )
    ]

    artifact_receipt = {key: sha256(path) for key, path in PATHS.items()}
    members = actual_members()
    member_binding = "".join(
        f"{item['name']}\t{item['sha256']}\n" for item in members
    ).encode()
    trace_aggregate = hashlib.sha256(member_binding).hexdigest()
    command_input = command.get("input_receipt", {})
    command_members = command_input.get("trace_members", [])
    command_member_pairs = [
        (Path(item.get("path", "")).name, item.get("sha256"))
        for item in command_members if isinstance(item, dict)
    ]
    expected_pairs = list(EXPECTED_MEMBERS)

    snapshot_shape = len(snapshots) == 6 and all(
        item.get("l1d_core_rows") == 76 and item.get("dram_rows") == 8
        for item in snapshots
    )
    snapshot_names = tuple(item.get("kernel_name") for item in snapshots)
    snapshot_uids = tuple(item.get("kernel_launch_uid") for item in snapshots)
    snapshot_insn = tuple(item.get("total_instructions") for item in snapshots)
    snapshot_ctas = tuple(item.get("total_ctas") for item in snapshots)
    snapshot_cycles = [item.get("total_cycles") for item in snapshots]
    monotonic_cycles = (
        len(snapshot_cycles) == 6
        and all(type(value) is int for value in snapshot_cycles)
        and all(left < right for left, right in zip(snapshot_cycles, snapshot_cycles[1:]))
    )
    roi_cycles = (
        roi_end.get("total_cycles") - context.get("total_cycles")
        if type(roi_end.get("total_cycles")) is int
        and type(context.get("total_cycles")) is int
        else None
    )

    all_controller_present = all(
        type(final_controller.get(key)) is int for key in CONTROLLER_INT_KEYS
    ) and all(final_controller.get(key) is not None for key in (
        "awma_transient_l2_mode",
        "awma_r101r2_transient_service_mode",
        "awma_r101r3_service_mode",
        "awma_r101r2_pre_roi_lifecycle_hash",
    ))
    context_controller = context.get("controller", {})
    r2_service_zero = all(
        type(final_controller.get(key)) is int
        and final_controller[key] == 0
        for key in SERVICE_ACCOUNTING_KEYS
    ) and all(final_controller.get(key) == 0 for key in FAIL_CLOSED_KEYS)
    s1_accounting_keys = (
        "awma_r101r3_s1_served_reads",
        "awma_r101r3_s1_served_ldg_reads",
        "awma_r101r3_s1_served_ldgsts_reads",
        "awma_r101r3_s1_served_writes",
        "awma_r101r3_s1_served_request_bytes",
        "awma_r101r3_s1_served_active_bytes",
        "awma_r101r3_s1_context_served",
        "awma_r101r3_s1_duplicate_completions",
    )
    s1_fail_keys = (
        "awma_r101r3_s1_dead_fail_closed",
        "awma_r101r3_s1_partial_fail_closed",
        "awma_r101r3_s1_multi_region_fail_closed",
        "awma_r101r3_s1_invalid_range_fail_closed",
        "awma_r101r3_s1_atomic_fail_closed",
        "awma_r101r3_s1_unsupported_fail_closed",
    )
    s1_values_present = all(
        type(final_controller.get(key)) is int
        for key in s1_accounting_keys + s1_fail_keys
    )
    s1_equations = s1_values_present and (
        final_controller["awma_r101r3_s1_served_reads"]
        == final_controller["awma_r101r3_s1_served_ldg_reads"]
        + final_controller["awma_r101r3_s1_served_ldgsts_reads"]
    ) and (
        final_controller["awma_r101r3_s1_served_request_bytes"]
        >= final_controller["awma_r101r3_s1_served_active_bytes"]
    )
    s1_qualified = s1_equations and all(
        final_controller.get(key, 0) > 0 for key in (
            "awma_r101r3_s1_served_reads",
            "awma_r101r3_s1_served_ldg_reads",
            "awma_r101r3_s1_served_ldgsts_reads",
            "awma_r101r3_s1_served_writes",
            "awma_r101r3_s1_served_request_bytes",
            "awma_r101r3_s1_served_active_bytes",
        )
    )
    s1_semantics_clean = (
        all(final_controller.get(key) == 0 for key in s1_fail_keys)
        and final_controller.get("awma_r101r3_s1_semantics_qualified") == 1
        and final_controller.get("awma_r101r3_s1_duplicate_completions") == 0
    )
    s1_context_zero = all(
        context_controller.get(key) == 0 for key in (
            "awma_r101r3_s1_served_reads",
            "awma_r101r3_s1_served_writes",
            "awma_r101r3_s1_context_served",
            "awma_r101r3_s1_duplicate_completions",
        )
    )

    context_normal = all(
        type(context.get(key)) is int and context.get(key, 0) > 0
        for key in ("l1d_accesses", "l2_accesses", "dram_n_rd")
    )
    roi_normal = all(
        type(context.get(key)) is int
        and type(roi_end.get(key)) is int
        and roi_end[key] > context[key]
        for key in ("l1d_accesses", "l2_accesses", "dram_n_rd")
    )
    o2_normal_l2_delta = (
        type(context.get("l2_accesses")) is int
        and type(roi_end.get("l2_accesses")) is int
        and roi_end["l2_accesses"] > context["l2_accesses"]
    )
    coverage_exact = (
        len(coverage_records) == 6
        and [record.get("kernel_uid") for record in coverage_records] == list(range(1, 7))
        and all(
            record.get("translated") == record.get("admissions")
            and record.get("untranslated") == 0
            and record.get("unobserved") == 0
            and record.get("translated_unique") == record.get("unique")
            and record.get("untranslated_unique") == 0
            for record in coverage_records
        )
    )
    c = final_controller
    formal_tools = command.get("formal_tools", {})
    current_summarizer_sha256 = sha256(Path(__file__))
    current_runner_sha256 = sha256(RUNNER)
    legacy_postprocess_recovery = (
        formal_tools.get("runner_sha256") == FORMAL_AT_RUN_RUNNER_SHA256
        and formal_tools.get("summarizer_sha256")
        == FORMAL_AT_RUN_SUMMARIZER_SHA256
    )
    native_fixed_tool_pair = (
        formal_tools.get("runner_sha256") == current_runner_sha256
        and formal_tools.get("summarizer_sha256")
        == current_summarizer_sha256
    )
    postprocess_recovery = {
        "status": (
            "RECOVERED_FROM_FORMAL_POSTPROCESS_FAILURE"
            if legacy_postprocess_recovery else "NATIVE_FIXED_SUMMARIZER"
        ),
        "reason": (
            "formal-at-run S1 summarizer imposed non-preregistered "
            "telemetry-label and assumed-depth checks; simulator rc/log "
            "data were complete and immutable"
            if legacy_postprocess_recovery else "NONE"
        ),
        "formal_at_run_runner_sha256": formal_tools.get("runner_sha256"),
        "formal_at_run_summarizer_sha256": formal_tools.get(
            "summarizer_sha256"
        ),
        "legacy_formal_runner_sha256": FORMAL_AT_RUN_RUNNER_SHA256,
        "legacy_formal_summarizer_sha256": FORMAL_AT_RUN_SUMMARIZER_SHA256,
        "recovery_summarizer_path": str(Path(__file__).resolve()),
        "recovery_summarizer_sha256": current_summarizer_sha256,
        "current_fixed_runner_path": str(RUNNER),
        "current_fixed_runner_sha256": current_runner_sha256,
        "raw_command_log_rc_stderr_immutable": True,
        "simulator_rerun": False,
    }
    gates = {
        "stage_exact": command.get("stage") == STAGE,
        "arm_exact": command.get("arm") == arm,
        "mode_exact": command.get("mode") == MODES[arm],
        "oracle_label_exact": command.get("oracle_label") == ORACLE_LABEL,
        "argv_exact": argv_sha == EXPECTED_ARGV_SHA256 == command.get("argv_sha256"),
        "environment_whitelist_exact": command.get("environment") == expected_environment(arm),
        "frozen_artifacts_exact": (
            artifact_receipt == EXPECTED_ARTIFACTS
            and command.get("artifact_receipt") == EXPECTED_ARTIFACTS
        ),
        "summarizer_pinned": (
            legacy_postprocess_recovery or native_fixed_tool_pair
        ),
        "derived_input_identity": command_input.get("identity") == "R101_L512_NS_CONTEXT2_EXECORG_V1",
        "producer_commit_exact": command_input.get("producer_commit") == "bb902283b7ce9e1902b460383fbd3e0bedbd884d",
        "trace_members_exact": command_member_pairs == expected_pairs,
        "trace_members_current": (
            all(item["is_symlink"] and item["sha256"] == item["expected_sha256"] for item in members)
            and trace_aggregate == TRACE_AGGREGATE_SHA256
            and command_input.get("ordered_trace_aggregate_sha256") == TRACE_AGGREGATE_SHA256
        ),
        "rc_zero": rc == 0,
        "stderr_empty": stderr_bytes == 0,
        "exit_marker_present": "GPGPU-Sim: *** exit detected ***" in text,
        "stats_block_count_exact": len(blocks) == 7,
        "terminal_stats_block_blank": terminal.get("kernel_name") == "",
        "per_kernel_shape_exact": snapshot_shape,
        "kernel_identity_exact": snapshot_names == EXPECTED_NAMES and snapshot_uids == tuple(range(1, 7)),
        "instruction_count_exact": snapshot_insn == EXPECTED_CUMULATIVE_INSTRUCTIONS,
        "cta_count_exact": snapshot_ctas == EXPECTED_CUMULATIVE_CTAS,
        "kernel_cycles_strictly_increase": monotonic_cycles,
        "coverage_exact_6": coverage_exact,
        "duplicate_application_zero": last_int(text, "vm_ready_application_duplicate_attempts") == 0,
        "translation_quiescent_invariants": last_int(text, "vm_translation_quiescent_invariants_hold") == 1,
        "translation_mshr_empty": last_int(text, "vm_translation_mshr_active") == 0,
        "translation_pwq_empty": last_int(text, "vm_translation_pwq_occupancy") == 0,
        "translation_pwq_entries_empty": last_int(text, "vm_translation_pwq_entries_active") == 0,
        "translation_walkers_empty": last_int(text, "vm_translation_walkers_active") == 0,
        "controller_counters_present": all_controller_present,
        "selector_explicit": (
            c.get("awma_r101r2_service_selector_explicit") == 1
            and c.get("awma_r101r3_selector_explicit") == 1
            and c.get("awma_r101r3_diagnostics") == 1
        ),
        "l2_mechanism_off": c.get("awma_transient_l2_mode") == "none" and all(c.get(key) == 0 for key in POLICY_EFFECT_KEYS),
        "service_mode_exact": (
            command.get("environment", {}).get(
                "AWMA_R101R2_TRANSIENT_SERVICE_MODE"
            ) == "none"
            and c.get("awma_r101r2_transient_service_mode") == MODES[arm]
            and c.get("awma_r101r3_service_mode") == MODES[arm]
        ),
        "kernel_lifecycle_exact": (
            c.get("awma_transient_l2_expected_kernels") == 6
            and c.get("awma_transient_l2_launched_kernels") == 6
            and c.get("awma_transient_l2_completed_kernels") == 6
            and c.get("awma_transient_l2_pre_transitions") == 6
            and c.get("awma_transient_l2_post_transitions") == 6
            and c.get("awma_transient_l2_descriptor_transitions") == 12
        ),
        "roi_ordinals_exact": (
            c.get("awma_r101r2_context_end_ordinal") == 3
            and c.get("awma_r101r2_roi_start_ordinal") == 4
            and c.get("awma_r101r2_roi_end_ordinal") == 6
            and c.get("awma_r101r2_active_kernel_ordinal") == 0
        ),
        "context_snapshot_exact": (
            context_controller.get("awma_transient_l2_completed_kernels") == 3
            and context_controller.get("awma_transient_l2_pre_transitions") == 3
            and context_controller.get("awma_transient_l2_post_transitions") == 3
            and context_controller.get("awma_transient_l2_descriptor_transitions") == 6
        ),
        "boundary_receipts_valid": (
            c.get("awma_r101r2_context_end_cycle_valid") == 1
            and c.get("awma_r101r2_roi_end_cycle_valid") == 1
            and c.get("awma_r101r2_pre_roi_receipt_valid") == 1
            and c.get("awma_r101r2_pre_roi_lifecycle_hash") not in (None, "0000000000000000")
        ),
        "boundary_cycles_exact": (
            all(type(c.get(key)) is int for key in (
                "awma_r101r2_context_end_cycle", "awma_r101r2_pre_roi_cycle",
                "awma_r101r2_roi_end_cycle", "awma_r101r2_roi_cycles",
            ))
            and c["awma_r101r2_context_end_cycle"] + 1
            == context.get("total_cycles")
            and c["awma_r101r2_pre_roi_cycle"]
            == c["awma_r101r2_context_end_cycle"] + 1
            and c["awma_r101r2_roi_end_cycle"] + 1
            == roi_end.get("total_cycles")
            and c["awma_r101r2_roi_cycles"] == roi_cycles
            and type(roi_cycles) is int and roi_cycles > 0
        ),
        "context_normal_memory_service": context_normal,
        "s1_roi_normal_memory_service": roi_normal,
        "s1_normal_l2_hierarchy_delta_positive": o2_normal_l2_delta,
        "transient_scope_observed": c.get("awma_transient_l2_transient_accesses", 0) > 0,
        "r2_oracle_disabled_exact": r2_service_zero,
        "s1_context_service_disabled": s1_context_zero,
        "s1_context_signature_exact": (
            context.get("total_cycles") == 2976829
            and context.get("total_instructions") == 1217463296
            and context.get("total_ctas") == 7040
            and context.get("l1d_core_rows") == 76
            and context.get("l1d_accesses") == 3469312
            and context.get("l1d_misses") == 3347858
            and context.get("l1d_reservation_fails") == 38535562
            and context.get("l2_accesses") == 29964261
            and context.get("l2_misses") == 3582086
            and context.get("l2_reservation_fails") == 21787
            and context.get("dram_n_rd") == 1419398
            and context.get("dram_n_write") == 0
            and context.get("dram_n_wr_bk") == 392701
            and c.get("awma_r101r2_pre_roi_lifecycle_hash")
                == "c11eff45e7bbc37f"
        ),
        "s1_semantics_clean": s1_semantics_clean,
        "s1_equations_exact": s1_equations,
        "s1_qualified_nonzero": s1_qualified,
        "s1_finite_path_observed": (
            c.get("awma_r101r3_s1_head_qualified_cycles", 0)
                >= c.get("awma_r101r3_s1_served_reads", 0)
                + c.get("awma_r101r3_s1_served_writes", 0)
            and c.get("awma_r101r3_s1_max_ingress_depth", 0) > 0
            and c.get("awma_r101r3_s1_max_return_depth", 0) >= 0
            and c.get("awma_r101r3_s1_return_queue_full_cycles", 0) > 0
            and c.get("awma_r101r3_s1_data_port_busy_cycles", 0) > 0
            and c.get("awma_r101r3_s1_subpartition_mask", 0) > 0
        ),
        "exactly_once_completion": (
            c.get("awma_r101r3_s1_duplicate_completions") == 0
            and c.get("awma_r101r3_s1_context_served") == 0
            and c.get("awma_r101r2_service_duplicate_completions") == 0
            and c.get("awma_r101r2_service_outstanding") == 0
        ),
        "writeback_completion_exact": (
            c.get("awma_transient_l2_completed_l2_writebacks")
            == c.get("awma_transient_l2_l2_writebacks")
            and c.get("awma_transient_l2_outstanding_l2_writebacks") == 0
        ),
        "writeback_byte_accounting_exact": (
            terminal.get("dram_n_wr_bk") is not None
            and c.get("awma_transient_l2_l2_writeback_bytes")
            == terminal.get("dram_n_wr_bk") * 64
        ),
        "terminal_drain_receipt_exact": (
            len(drain_matches) == 1
            and drain.get("gpu_active") == 0
            and drain.get("l2_writeback_active") == 0
            and drain.get("max_limit_hit") == 0
            and drain.get("gpu_deadlock") == 0
        ),
        "dram_latency_queues_empty": len(dram_latency_queues) == 8 and not any(dram_latency_queues),
        "terminal_quiescent": c.get("awma_transient_l2_terminal_quiescent") == 1,
        "terminal_identity_preserved": (
            type(terminal.get("total_cycles")) is int
            and type(roi_end.get("total_cycles")) is int
            and terminal.get("total_instructions") == EXPECTED_CUMULATIVE_INSTRUCTIONS[-1]
            and terminal.get("total_ctas") == EXPECTED_CUMULATIVE_CTAS[-1]
            and terminal["total_cycles"] >= roi_end["total_cycles"]
        ),
    }
    summary = {
        "stage": STAGE,
        "status": "PASS" if all(gates.values()) else "FAIL",
        "arm": arm,
        "mode": MODES[arm],
        "oracle_label": ORACLE_LABEL,
        "run_dir": str(run_dir),
        "rc": rc,
        "stderr_bytes": stderr_bytes,
        "artifact_receipt": artifact_receipt,
        "ordered_trace_aggregate_sha256": trace_aggregate,
        "trace_members": members,
        "per_kernel_snapshots": snapshots,
        "context_end_snapshot": context,
        "roi_end_snapshot": roi_end,
        "terminal_snapshot": terminal,
        "full_context2_total_cycles": terminal.get("total_cycles"),
        "kernel6_end_cycle": roi_end.get("total_cycles"),
        "roi_cycles": roi_cycles,
        "instructions": roi_end.get("total_instructions"),
        "ctas": roi_end.get("total_ctas"),
        "coverage": coverage,
        "coverage_records": coverage_records,
        "coverage_uid_identity": [
            {key: record.get(key) for key in (
                "kernel_uid", "unique", "translated_unique", "untranslated_unique"
            )}
            for record in coverage_records
        ],
        "controller": final_controller,
        "drain": drain,
        "dram_latency_queues": dram_latency_queues,
        "POSTPROCESS_RECOVERY": postprocess_recovery,
        "gates": gates,
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    try:
        summary = summarize(run_dir)
        atomic_json(run_dir / "RUN_SUMMARY.json", summary)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        return fail_closed(run_dir, str(exc))
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
