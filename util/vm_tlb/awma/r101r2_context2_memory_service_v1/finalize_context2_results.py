#!/usr/bin/env python3
"""Validate B0/O2 CONTEXT2 arms and optionally publish result tables.

Without ``--write`` this command is read-only.  The write path is enabled only
after both independently summarized arms and every cross-arm invariant pass.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
from typing import Any


STAGE = "AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_V1"
ORACLE_LABEL = "ORACLE_ONE_CYCLE_UNBOUNDED_SERVICE"
REPO = Path(
    "/root/workspace/accel-sim-framework-awma-r101r2-context2-memory-service-174-v1"
)
DURABLE = Path(
    "/root/share/mnt164/huangrulin/awma_r101r2_context2_memory_service_174_v1"
)
DEFAULT_ROOT = DURABLE / "raw/formal"
DEFAULT_PACK = REPO / (
    "docs/vm_tlb/review_packs/"
    "AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_174_V1"
)
INPUT = DURABLE / "input"
TOOLS = REPO / "util/vm_tlb/awma/r101r2_context2_memory_service_v1"
RUNNER = TOOLS / "run_context2_matrix.py"
SUMMARIZER = TOOLS / "summarize_context2_run.py"
FINALIZER = TOOLS / "finalize_context2_results.py"
ARMS = ("B0", "O2")
MODES = {"B0": "none", "O2": "oracle_1c"}
DECISION_PRESENT = "R101R2_O2_MEMORY_SERVICE_HEADROOM_PRESENT"
DECISION_LOW = "R101R2_O2_MEMORY_SERVICE_HEADROOM_LOW"
THRESHOLD_PERCENT = 5.0
REPEAT_LOW_PERCENT = 3.0
REPEAT_HIGH_PERCENT = 7.0
FORMAL_AT_RUN_RUNNER_SHA256 = (
    "1b55fd7e325dd63496bdb45285bc3f10a63740e2a502873a6c9217aef3305158"
)
FORMAL_AT_RUN_SUMMARIZER_SHA256 = (
    "cb012f08d7f8ea1c099bb3c4b86e4a13e184ad28f5e2ce20df1c2a4aaa6f8949"
)

CONTEXT_MATCH_KEYS = (
    "total_cycles",
    "total_instructions",
    "total_ctas",
    "l1d_core_rows",
    "l1d_accesses",
    "l1d_misses",
    "l1d_reservation_fails",
    "l2_accesses",
    "l2_misses",
    "l2_reservation_fails",
    "dram_rows",
    "dram_n_rd",
    "dram_n_rd_l2_a",
    "dram_n_write",
    "dram_n_wr_bk",
)
RESULT_CONTROLLER_KEYS = (
    "awma_transient_l2_transient_accesses",
    "awma_transient_l2_transient_admissions",
    "awma_transient_l2_l2_writebacks",
    "awma_transient_l2_l2_writeback_bytes",
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
    "awma_r101r2_service_qualified_read_bytes",
    "awma_r101r2_service_qualified_writes",
    "awma_r101r2_service_qualified_write_bytes",
    "awma_r101r2_service_scheduled",
    "awma_r101r2_service_one_cycle_ready",
    "awma_r101r2_service_retired_reads",
    "awma_r101r2_service_retired_writes",
    "awma_r101r2_service_outstanding",
    "awma_r101r2_service_duplicate_completions",
    "awma_r101r2_service_latency_violations",
    "awma_r101r2_service_stale_token_violations",
    "awma_r101r2_service_semantics_qualified",
    "awma_transient_l2_terminal_quiescent",
)


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def require_int(mapping: dict[str, Any], key: str, arm: str) -> int:
    value = mapping.get(key)
    require(type(value) is int, f"{arm}: {key} is not an integer")
    return value


def read_arm(root: Path, arm: str) -> dict[str, Any]:
    run_dir = root / arm
    required = tuple(run_dir / name for name in (
        "command.json", "start_utc.txt", "end_utc.txt", "rc.txt",
        "wall_seconds.txt", "run.log", "run.stderr", "RUN_SUMMARY.json",
    ))
    missing = [str(path) for path in required if not path.is_file()]
    require(not missing, f"{arm}: missing durable files: {', '.join(missing)}")
    summary = json.loads((run_dir / "RUN_SUMMARY.json").read_text())
    command = json.loads((run_dir / "command.json").read_text())
    require(isinstance(summary, dict), f"{arm}: summary root is not an object")
    require(summary.get("stage") == STAGE, f"{arm}: stage mismatch")
    require(summary.get("arm") == arm, f"{arm}: arm mismatch")
    require(summary.get("mode") == MODES[arm], f"{arm}: mode mismatch")
    require(summary.get("oracle_label") == ORACLE_LABEL, f"{arm}: oracle label mismatch")
    require(summary.get("status") == "PASS", f"{arm}: summary status is not PASS")
    require(summary.get("rc") == 0, f"{arm}: summary rc is not zero")
    require((run_dir / "rc.txt").read_text().strip() == "0", f"{arm}: rc.txt is not zero")
    require(summary.get("stderr_bytes") == 0, f"{arm}: summary stderr nonempty")
    require((run_dir / "run.stderr").stat().st_size == 0, f"{arm}: durable stderr nonempty")
    gates = summary.get("gates")
    require(isinstance(gates, dict) and gates, f"{arm}: gates missing")
    require(all(type(value) is bool for value in gates.values()), f"{arm}: non-boolean gate")
    failed = sorted(key for key, value in gates.items() if value is not True)
    require(not failed, f"{arm}: failed gates: {failed}")
    for key in (
        "coverage_exact_6", "instruction_count_exact", "cta_count_exact",
        "boundary_cycles_exact", "exactly_once_completion",
        "terminal_drain_receipt_exact", "dram_latency_queues_empty",
        "terminal_quiescent",
    ):
        require(gates.get(key) is True, f"{arm}: required gate absent/false: {key}")
    snapshots = summary.get("per_kernel_snapshots")
    require(isinstance(snapshots, list) and len(snapshots) == 6,
            f"{arm}: per-kernel snapshot count is not six")
    context = summary.get("context_end_snapshot")
    roi_end = summary.get("roi_end_snapshot")
    controller = summary.get("controller")
    require(isinstance(context, dict), f"{arm}: context snapshot missing")
    require(isinstance(roi_end, dict), f"{arm}: ROI end snapshot missing")
    require(isinstance(controller, dict), f"{arm}: controller counters missing")
    for key in CONTEXT_MATCH_KEYS:
        require_int(context, key, arm)
    for key in ("full_context2_total_cycles", "kernel6_end_cycle", "roi_cycles", "instructions", "ctas"):
        require_int(summary, key, arm)
    for key in RESULT_CONTROLLER_KEYS:
        require_int(controller, key, arm)
    require(
        summary["roi_cycles"]
        == roi_end.get("total_cycles") - context.get("total_cycles"),
        f"{arm}: ROI cycle equation mismatch",
    )
    require(command.get("stage") == STAGE and command.get("arm") == arm,
            f"{arm}: command identity mismatch")
    formal_tools = command.get("formal_tools", {})
    postprocess = summary.get("POSTPROCESS_RECOVERY")
    require(isinstance(postprocess, dict),
            f"{arm}: POSTPROCESS_RECOVERY receipt missing")
    require(
        postprocess.get("formal_at_run_runner_sha256")
        == formal_tools.get("runner_sha256")
        and postprocess.get("formal_at_run_summarizer_sha256")
        == formal_tools.get("summarizer_sha256"),
        f"{arm}: formal-at-run tool receipt mismatch",
    )
    legacy_recovery = (
        formal_tools.get("runner_sha256") == FORMAL_AT_RUN_RUNNER_SHA256
        and formal_tools.get("summarizer_sha256")
        == FORMAL_AT_RUN_SUMMARIZER_SHA256
    )
    native_fixed = (
        formal_tools.get("runner_sha256") == sha256(RUNNER)
        and formal_tools.get("summarizer_sha256") == sha256(SUMMARIZER)
    )
    require(legacy_recovery or native_fixed,
            f"{arm}: unrecognized formal tool pair")
    require(
        postprocess.get("recovery_summarizer_sha256") == sha256(SUMMARIZER),
        f"{arm}: recovery summarizer SHA mismatch",
    )
    if legacy_recovery:
        require(
            postprocess.get("status")
            == "RECOVERED_FROM_FORMAL_POSTPROCESS_FAILURE"
            and postprocess.get("simulator_rerun") is False
            and postprocess.get("raw_command_log_rc_stderr_immutable") is True,
            f"{arm}: legacy postprocess recovery receipt invalid",
        )
        recovery_path = run_dir / "ORCHESTRATION_RECOVERY.json"
        require(recovery_path.is_file(),
                f"{arm}: ORCHESTRATION_RECOVERY.json missing")
        recovery = json.loads(recovery_path.read_text())
        require(recovery.get("status") == "PASS" and recovery.get("arm") == arm,
                f"{arm}: orchestration recovery status/identity mismatch")
        require(
            recovery.get("simulator_rerun") is False
            and recovery.get("atomic_promote") is True
            and recovery.get("destination") == str(run_dir)
            and recovery.get("run_summary_sha256")
            == sha256(run_dir / "RUN_SUMMARY.json"),
            f"{arm}: orchestration recovery action receipt mismatch",
        )
        require(
            recovery.get("formal_at_run", {}).get("runner_sha256")
            == FORMAL_AT_RUN_RUNNER_SHA256
            and recovery.get("formal_at_run", {}).get("summarizer_sha256")
            == FORMAL_AT_RUN_SUMMARIZER_SHA256
            and recovery.get("recovery", {}).get("summarizer_sha256")
            == sha256(SUMMARIZER),
            f"{arm}: orchestration recovery tool hashes mismatch",
        )
        immutable = recovery.get("immutable_raw_artifacts", {})
        for name in ("command.json", "run.log", "run.stderr", "rc.txt"):
            item = immutable.get(name, {})
            actual = sha256(run_dir / name)
            require(
                item.get("sha256_before") == actual
                == item.get("sha256_after")
                and item.get("size_bytes_before")
                == (run_dir / name).stat().st_size
                == item.get("size_bytes_after"),
                f"{arm}: recovered immutable artifact drift: {name}",
            )
    else:
        require(postprocess.get("status") == "NATIVE_FIXED_SUMMARIZER",
                f"{arm}: native fixed summarizer receipt invalid")
    summary["_run_dir"] = str(run_dir)
    summary["_summary_sha256"] = sha256(run_dir / "RUN_SUMMARY.json")
    summary["_command"] = command
    return summary


def cross_arm_receipt(summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    b0 = summaries["B0"]
    o2 = summaries["O2"]
    mismatches = {
        key: {"B0": b0["context_end_snapshot"].get(key),
              "O2": o2["context_end_snapshot"].get(key)}
        for key in CONTEXT_MATCH_KEYS
        if b0["context_end_snapshot"].get(key) != o2["context_end_snapshot"].get(key)
    }
    b0_hash = b0["controller"].get("awma_r101r2_pre_roi_lifecycle_hash")
    o2_hash = o2["controller"].get("awma_r101r2_pre_roi_lifecycle_hash")
    if b0_hash != o2_hash:
        mismatches["controller_pre_roi_lifecycle_hash"] = {"B0": b0_hash, "O2": o2_hash}
    if b0["controller"].get("awma_r101r2_pre_roi_cycle") != o2["controller"].get("awma_r101r2_pre_roi_cycle"):
        mismatches["controller_pre_roi_cycle"] = {
            "B0": b0["controller"].get("awma_r101r2_pre_roi_cycle"),
            "O2": o2["controller"].get("awma_r101r2_pre_roi_cycle"),
        }
    require(not mismatches, f"R101R2_CONTEXT_NOT_MATCHED: {mismatches}")
    require(b0["instructions"] == o2["instructions"], "O2: total instruction identity differs")
    require(b0["ctas"] == o2["ctas"], "O2: total CTA identity differs")
    require(b0["coverage_uid_identity"] == o2["coverage_uid_identity"],
            "O2: coverage identity differs")
    require(b0["artifact_receipt"] == o2["artifact_receipt"],
            "O2: frozen artifact receipt differs")
    require(b0["ordered_trace_aggregate_sha256"] == o2["ordered_trace_aggregate_sha256"],
            "O2: ordered trace binding differs")
    require(b0["controller"]["awma_r101r2_service_scheduled"] == 0,
            "B0: service oracle unexpectedly active")
    require(o2["controller"]["awma_r101r2_service_scheduled"] > 0,
            "O2: service oracle qualified no transaction")
    return {
        "status": "PASS",
        "matched_fields": list(CONTEXT_MATCH_KEYS),
        "context_end_cycle": b0["context_end_snapshot"]["total_cycles"],
        "pre_roi_cycle": b0["controller"]["awma_r101r2_pre_roi_cycle"],
        "context_end_instructions": b0["context_end_snapshot"]["total_instructions"],
        "context_end_ctas": b0["context_end_snapshot"]["total_ctas"],
        "pre_roi_lifecycle_hash": b0_hash,
        "mismatches": {},
    }


def decision(summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    b0_cycles = summaries["B0"]["roi_cycles"]
    o2_cycles = summaries["O2"]["roi_cycles"]
    require(b0_cycles > 0 and o2_cycles > 0, "ROI cycle count must be positive")
    improvement = (b0_cycles - o2_cycles) * 100.0 / b0_cycles
    label = DECISION_PRESENT if improvement >= THRESHOLD_PERCENT else DECISION_LOW
    repeat_allowed = REPEAT_LOW_PERCENT <= improvement <= REPEAT_HIGH_PERCENT
    return {
        "label": label,
        "b0_roi_cycles": b0_cycles,
        "o2_roi_cycles": o2_cycles,
        "roi_cycle_delta": o2_cycles - b0_cycles,
        "o2_roi_improvement_percent": improvement,
        "threshold_percent": THRESHOLD_PERCENT,
        "threshold_operator": ">=",
        "repeat_band_low_percent": REPEAT_LOW_PERCENT,
        "repeat_band_high_percent": REPEAT_HIGH_PERCENT,
        "exact_repeat_allowed_once": repeat_allowed,
        "repeat_disposition": (
            "ONE_EXACT_REPEAT_ALLOWED" if repeat_allowed
            else "NO_REPEAT_OUTSIDE_3_TO_7_PERCENT_BAND"
        ),
        "full5_disposition": "FORBIDDEN_NOT_RUN",
        "o3_disposition": "FORBIDDEN_NOT_RUN",
        "interpretation": "TRANSIENT_MEMORY_SERVICE_UPPER_BOUND_ONLY",
        "oracle_label": ORACLE_LABEL,
    }


def result_row(summary: dict[str, Any]) -> dict[str, Any]:
    context = summary["context_end_snapshot"]
    end = summary["roi_end_snapshot"]
    terminal = summary["terminal_snapshot"]
    ctrl = summary["controller"]
    row: dict[str, Any] = {
        "stage": STAGE,
        "arm": summary["arm"],
        "mode": summary["mode"],
        "status": summary["status"],
        "oracle_label": ORACLE_LABEL,
        "full_context2_total_cycles": summary["full_context2_total_cycles"],
        "context_end_cycle": context["total_cycles"],
        "kernel6_end_cycle": summary["kernel6_end_cycle"],
        "roi_cycles_end6_minus_end3": summary["roi_cycles"],
        "instructions": summary["instructions"],
        "ctas": summary["ctas"],
        "context_instructions": context["total_instructions"],
        "context_ctas": context["total_ctas"],
        "context_l1d_accesses": context["l1d_accesses"],
        "context_l1d_misses": context["l1d_misses"],
        "context_l2_accesses": context["l2_accesses"],
        "context_l2_misses": context["l2_misses"],
        "context_dram_reads": context["dram_n_rd"],
        "context_dram_writes": context["dram_n_write"],
        "context_dram_writebacks": context["dram_n_wr_bk"],
        "end_l1d_accesses": end["l1d_accesses"],
        "end_l1d_misses": end["l1d_misses"],
        "end_l2_accesses": end["l2_accesses"],
        "end_l2_misses": end["l2_misses"],
        "end_dram_reads": end["dram_n_rd"],
        "end_dram_writes": end["dram_n_write"],
        "end_dram_writebacks": end["dram_n_wr_bk"],
        "terminal_dram_reads": terminal["dram_n_rd"],
        "terminal_dram_writes": terminal["dram_n_write"],
        "terminal_dram_writebacks": terminal["dram_n_wr_bk"],
        "pre_roi_lifecycle_hash": ctrl["awma_r101r2_pre_roi_lifecycle_hash"],
        "coverage_kernels": summary["coverage"]["kernels"],
        "coverage_admissions": summary["coverage"]["admissions"],
        "coverage_untranslated": summary["coverage"]["untranslated"],
        "coverage_unobserved": summary["coverage"]["unobserved"],
        "all_gates_pass": all(summary["gates"].values()),
        "run_summary_sha256": summary["_summary_sha256"],
        "postprocess_recovery_status": summary["POSTPROCESS_RECOVERY"]["status"],
        "formal_at_run_runner_sha256": summary["POSTPROCESS_RECOVERY"]["formal_at_run_runner_sha256"],
        "formal_at_run_summarizer_sha256": summary["POSTPROCESS_RECOVERY"]["formal_at_run_summarizer_sha256"],
        "recovery_summarizer_sha256": summary["POSTPROCESS_RECOVERY"]["recovery_summarizer_sha256"],
    }
    row.update({key: ctrl[key] for key in RESULT_CONTROLLER_KEYS})
    return row


def comparison_row(
    summaries: dict[str, dict[str, Any]],
    cross: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    b0, o2 = summaries["B0"], summaries["O2"]
    return {
        "comparison": "O2_CONTEXT2_VS_B0_CONTEXT2",
        "context_match_status": cross["status"],
        "context_end_cycle": cross["context_end_cycle"],
        "pre_roi_cycle": cross["pre_roi_cycle"],
        "context_end_instructions": cross["context_end_instructions"],
        "context_end_ctas": cross["context_end_ctas"],
        "pre_roi_lifecycle_hash": cross["pre_roi_lifecycle_hash"],
        "b0_full_context2_total_cycles": b0["full_context2_total_cycles"],
        "o2_full_context2_total_cycles": o2["full_context2_total_cycles"],
        "b0_roi_cycles": result["b0_roi_cycles"],
        "o2_roi_cycles": result["o2_roi_cycles"],
        "roi_cycle_delta": result["roi_cycle_delta"],
        "o2_roi_improvement_percent": result["o2_roi_improvement_percent"],
        "gate_operator": result["threshold_operator"],
        "gate_percent": result["threshold_percent"],
        "decision": result["label"],
        "exact_repeat_allowed_once": result["exact_repeat_allowed_once"],
        "repeat_disposition": result["repeat_disposition"],
        "oracle_label": ORACLE_LABEL,
        "full5_disposition": result["full5_disposition"],
    }


def file_receipts(run_dir: Path) -> list[dict[str, Any]]:
    result = []
    for path in sorted(item for item in run_dir.iterdir() if item.is_file()):
        result.append({
            "artifact": path.name,
            "path": str(path),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    return result


def receipts(
    root: Path,
    summaries: dict[str, dict[str, Any]],
    cross: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    for path in (RUNNER, SUMMARIZER, FINALIZER, INPUT / "CONTEXT2_DERIVATION_RECEIPT.json",
                 INPUT / "CONTEXT2_KERNELS.tsv", INPUT / "transient_l2_runtime.tsv",
                 INPUT / "traces/kernelslist.g"):
        require(path.is_file(), f"receipt authority missing: {path}")
    return {
        "stage": STAGE,
        "execution_branch": "hrl/awma-r101r2-context2-memory-service-174-v1",
        "coordination_handoff_commit": "8542a4d37372d586591ff9911929e523645e88f5",
        "durable_root": str(root),
        "oracle_label": ORACLE_LABEL,
        "formal_tools": {
            "runner": {"path": str(RUNNER), "sha256": sha256(RUNNER)},
            "summarizer": {"path": str(SUMMARIZER), "sha256": sha256(SUMMARIZER)},
            "finalizer": {"path": str(FINALIZER), "sha256": sha256(FINALIZER)},
        },
        "input_authority": {
            "identity": "R101_L512_NS_CONTEXT2_EXECORG_V1",
            "producer_commit": "bb902283b7ce9e1902b460383fbd3e0bedbd884d",
            "derivation_receipt_sha256": sha256(INPUT / "CONTEXT2_DERIVATION_RECEIPT.json"),
            "kernels_table_sha256": sha256(INPUT / "CONTEXT2_KERNELS.tsv"),
            "runtime_sidecar_sha256": sha256(INPUT / "transient_l2_runtime.tsv"),
            "kernelslist_sha256": sha256(INPUT / "traces/kernelslist.g"),
            "ordered_trace_aggregate_sha256": summaries["B0"]["ordered_trace_aggregate_sha256"],
            "trace_bytes_copied": False,
        },
        "frozen_artifacts": summaries["B0"]["artifact_receipt"],
        "validation": {
            "status": "PASS",
            "required_arms": list(ARMS),
            "all_single_arm_gates_pass_after_postprocess_recovery": True,
            "formal_at_run_summarizer_execution": (
                "FAIL_CLOSED_ARM_DIRECTORY_IDENTITY_BUG_RECOVERED_WITHOUT_SIMULATOR_RERUN"
            ),
            "six_kernel_coverage": True,
            "identity_instruction_cta_exact": True,
            "translation_exactly_once_full_drain": True,
            "b0_normal_service": True,
            "o2_semantics_and_equations": True,
            "cross_arm_context_exact": cross,
        },
        "arms": {
            arm: {
                "mode": summaries[arm]["mode"],
                "full_context2_total_cycles": summaries[arm]["full_context2_total_cycles"],
                "context_end_cycle": summaries[arm]["context_end_snapshot"]["total_cycles"],
                "roi_cycles": summaries[arm]["roi_cycles"],
                "instructions": summaries[arm]["instructions"],
                "ctas": summaries[arm]["ctas"],
                "summary_sha256": summaries[arm]["_summary_sha256"],
                "formal_at_run_tools": summaries[arm]["_command"]["formal_tools"],
                "postprocess_recovery": summaries[arm]["POSTPROCESS_RECOVERY"],
                "artifacts": file_receipts(root / arm),
            }
            for arm in ARMS
        },
        "decision": result,
        "forbidden_scope": {
            "FULL5": "NOT_RUN",
            "O3": "NOT_RUN",
            "scratchpad_or_dsmem": "NOT_RUN",
            "sweeps": "NOT_RUN",
            "holdout": "NOT_RUN",
            "new_109_capture": "NOT_RUN",
        },
    }


def tsv_text(rows: list[dict[str, Any]]) -> str:
    require(bool(rows), "cannot render empty TSV")
    output = io.StringIO()
    writer = csv.DictWriter(
        output, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def atomic_write(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    temporary.write_text(content)
    os.replace(temporary, path)


def write_outputs(
    pack: Path,
    summaries: dict[str, dict[str, Any]],
    comparison: dict[str, Any],
    run_receipts: dict[str, Any],
) -> list[str]:
    require(pack.is_dir(), f"review-pack directory does not exist: {pack}")
    payloads = {
        pack / "B0_CONTEXT2_RESULTS.tsv": tsv_text([result_row(summaries["B0"])]),
        pack / "O2_CONTEXT2_RESULTS.tsv": tsv_text([result_row(summaries["O2"])]),
        pack / "ROI_COMPARISON.tsv": tsv_text([comparison]),
        pack / "RUN_RECEIPTS.json": json.dumps(run_receipts, indent=2, sort_keys=True) + "\n",
    }
    for path, content in payloads.items():
        atomic_write(path, content)
    return [str(path) for path in payloads]


def fail_closed(message: str, missing_arms: list[str] | None = None) -> int:
    print(json.dumps({
        "stage": STAGE,
        "status": "FAIL_CLOSED",
        "error": message,
        "missing_arms": missing_arms or [],
        "write_performed": False,
    }, sort_keys=True))
    return 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--durable-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = args.durable_root.resolve()
    missing = [arm for arm in ARMS if not (root / arm / "RUN_SUMMARY.json").is_file()]
    if missing:
        return fail_closed("required durable formal arm(s) missing", missing)
    try:
        summaries = {arm: read_arm(root, arm) for arm in ARMS}
        cross = cross_arm_receipt(summaries)
        result = decision(summaries)
        comparison = comparison_row(summaries, cross, result)
        run_receipts = receipts(root, summaries, cross, result)
        written = (
            write_outputs(args.pack.resolve(), summaries, comparison, run_receipts)
            if args.write else []
        )
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError, ValidationError) as exc:
        return fail_closed(str(exc))
    print(json.dumps({
        "stage": STAGE,
        "status": "PASS",
        "decision": result,
        "context_match": cross,
        "summary_sha256": {
            arm: summaries[arm]["_summary_sha256"] for arm in ARMS
        },
        "write_performed": args.write,
        "written_files": written,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
