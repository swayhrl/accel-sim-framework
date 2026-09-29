#!/usr/bin/env python3
"""Validate and summarize the frozen R101 B0/O1/M1 formal matrix.

The default mode is read-only and prints one JSON record to stdout.  ``--write``
is fail-closed: it writes the three final review-pack data products only after
all three durable arms and all cross-arm invariants validate.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
from pathlib import Path
from typing import Any


STAGE = "AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_V1"
DEFAULT_DURABLE_ROOT = Path(
    "/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/raw/formal"
)
REPO_ROOT = Path(
    "/root/workspace/accel-sim-framework-awma-r101-transient-l2-arch-174-v1"
)
DEFAULT_PACK = REPO_ROOT / (
    "docs/vm_tlb/review_packs/"
    "AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_174_V1"
)
INPUT_ROOT = Path(
    "/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/input"
)
RUNNER = REPO_ROOT / (
    "util/vm_tlb/awma/r101_transient_l2_arch_v1/"
    "run_r101_transient_matrix.py"
)
SUMMARIZER = REPO_ROOT / (
    "util/vm_tlb/awma/r101_transient_l2_arch_v1/"
    "summarize_r101_transient_run.py"
)
PRODUCER_COMMIT = "bb902283b7ce9e1902b460383fbd3e0bedbd884d"
ACCEPTED_PAYLOAD_SHA256 = (
    "1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234"
)
ACCEPTED_OUTPUT_SHA256 = (
    "36aaed3f8360aa099301ae1d705bc2e6ab5ba61586adaf7ead93ecab808dc1b0"
)
TRACE_AGGREGATE_SHA256 = (
    "34031eebe1e25b375d9ee058328f678e4734790c40e67284bb6511130e4fec0e"
)
ADMISSION_RECEIPT_SHA256 = (
    "a6c66cb41c1ffb77f6af805534d47ccb8a8641dbe4aa3b206850be8e478f1e7a"
)
ARMS = ("B0", "O1", "M1")
MODES = {
    "B0": "none",
    "O1": "oracle_dead_drop",
    "M1": "bounded_live_retention",
}
PERFORMANCE_THRESHOLD_PERCENT = 5.0

AWMA_KEYS = (
    "awma_transient_l2_l2_writebacks",
    "awma_transient_l2_l2_writeback_bytes",
    "awma_transient_l2_transient_writebacks",
    "awma_transient_l2_transient_writeback_bytes",
    "awma_transient_l2_dead_eviction_drops",
    "awma_transient_l2_dead_eviction_drop_bytes",
    "awma_transient_l2_oracle_drop_lines",
    "awma_transient_l2_oracle_drop_dirty_lines",
    "awma_transient_l2_oracle_drop_bytes",
    "awma_transient_l2_protected_victim_deflections",
    "awma_transient_l2_forced_live_evictions",
    "awma_transient_l2_dead_victim_selections",
    "awma_transient_l2_ordinary_victim_selections",
    "awma_transient_l2_fallback_count",
    "awma_transient_l2_completed_l2_writebacks",
    "awma_transient_l2_outstanding_l2_writebacks",
    "awma_transient_l2_descriptor_transitions",
    "awma_transient_l2_pre_transitions",
    "awma_transient_l2_post_transitions",
    "awma_transient_l2_terminal_quiescent",
)


class ValidationError(RuntimeError):
    """A durable result is absent, malformed, or scientifically inadmissible."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def require_int(mapping: dict[str, Any], key: str, arm: str) -> int:
    value = mapping.get(key)
    require(type(value) is int, f"{arm}: {key} is not an integer")
    return value


def read_arm(root: Path, arm: str) -> dict[str, Any]:
    run_dir = root / arm
    summary_path = run_dir / "RUN_SUMMARY.json"
    rc_path = run_dir / "rc.txt"
    stderr_path = run_dir / "run.stderr"
    missing = [
        str(path) for path in (summary_path, rc_path, stderr_path)
        if not path.is_file()
    ]
    require(not missing, f"{arm}: missing durable files: {', '.join(missing)}")
    try:
        summary = json.loads(summary_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"{arm}: invalid RUN_SUMMARY.json: {exc}") from exc

    require(isinstance(summary, dict), f"{arm}: summary root is not an object")
    require(summary.get("arm") == arm, f"{arm}: arm identity mismatch")
    require(summary.get("mode") == MODES[arm], f"{arm}: mode mismatch")
    require(summary.get("status") == "PASS", f"{arm}: status is not PASS")
    require(summary.get("rc") == 0, f"{arm}: summary rc is not zero")
    require(rc_path.read_text().strip() == "0", f"{arm}: durable rc.txt is not zero")
    require(summary.get("stderr_bytes") == 0, f"{arm}: summary stderr is nonempty")
    require(stderr_path.stat().st_size == 0, f"{arm}: durable run.stderr is nonempty")

    gates = summary.get("gates")
    require(isinstance(gates, dict) and gates, f"{arm}: gates missing or empty")
    non_boolean = sorted(key for key, value in gates.items() if type(value) is not bool)
    failed = sorted(key for key, value in gates.items() if value is not True)
    require(not non_boolean, f"{arm}: non-boolean gates: {non_boolean}")
    require(not failed, f"{arm}: failed gates: {failed}")
    for key in (
        "coverage_records_exact",
        "cross_arm_identity",
        "terminal_memory_drain_receipt",
        "dram_latency_queues_empty",
        "writeback_completion_exact",
        "translation_quiescent_invariants",
        "kernel_count_exact",
        "terminal_quiescent",
        "writeback_byte_accounting_exact",
    ):
        require(gates.get(key) is True, f"{arm}: required gate absent/false: {key}")

    coverage = summary.get("coverage")
    require(isinstance(coverage, dict), f"{arm}: coverage missing")
    require(coverage.get("kernels") == 18, f"{arm}: coverage kernel count is not 18")
    require(
        coverage.get("translated") == coverage.get("admissions"),
        f"{arm}: translated/admissions mismatch",
    )
    require(
        coverage.get("translated_unique") == coverage.get("unique"),
        f"{arm}: translated_unique/unique mismatch",
    )
    require(coverage.get("untranslated") == 0, f"{arm}: untranslated is nonzero")
    require(coverage.get("untranslated_unique") == 0,
            f"{arm}: untranslated_unique is nonzero")
    require(coverage.get("unobserved") == 0, f"{arm}: unobserved is nonzero")
    uid_identity = summary.get("coverage_uid_identity")
    require(isinstance(uid_identity, list) and len(uid_identity) == 18,
            f"{arm}: coverage UID identity is not 18 records")

    require(summary.get("drain_gpu_active") == 0,
            f"{arm}: drain ended with GPU active")
    require(summary.get("drain_l2_writeback_active") == 0,
            f"{arm}: drain ended with L2 writeback active")
    require(summary.get("drain_max_limit_hit") == 0,
            f"{arm}: drain hit maximum limit")
    require(summary.get("drain_gpu_deadlock") == 0,
            f"{arm}: drain reported deadlock")
    queues = summary.get("dram_latency_queues")
    require(isinstance(queues, list) and len(queues) == 8 and not any(queues),
            f"{arm}: DRAM latency queues did not fully drain")

    awma = summary.get("awma")
    require(isinstance(awma, dict), f"{arm}: AWMA counters missing")
    for key in AWMA_KEYS:
        require_int(awma, key, arm)
    require(awma["awma_transient_l2_terminal_quiescent"] == 1,
            f"{arm}: transient controller not quiescent")
    require(awma["awma_transient_l2_outstanding_l2_writebacks"] == 0,
            f"{arm}: outstanding writebacks remain")
    require(
        awma["awma_transient_l2_completed_l2_writebacks"]
        == awma["awma_transient_l2_l2_writebacks"],
        f"{arm}: completed/generated writeback mismatch",
    )
    require(awma["awma_transient_l2_descriptor_transitions"] == 31,
            f"{arm}: descriptor transition count mismatch")
    require(awma["awma_transient_l2_pre_transitions"] == 16,
            f"{arm}: PRE transition count mismatch")
    require(awma["awma_transient_l2_post_transitions"] == 15,
            f"{arm}: POST transition count mismatch")

    for key in (
        "cycles", "instructions", "ctas", "l2_accesses", "l2_misses",
        "l2_reservation_fails", "dram_n_rd", "dram_n_rd_l2_a",
        "dram_n_write", "dram_n_wr_bk", "dram_read_bytes_64B",
        "dram_regular_write_bytes_64B", "dram_writeback_bytes_64B",
        "drain_cycles",
    ):
        require_int(summary, key, arm)
    require(isinstance(summary.get("artifact_receipt"), dict),
            f"{arm}: artifact receipt missing")

    summary["_summary_path"] = str(summary_path)
    summary["_summary_sha256"] = sha256(summary_path)
    return summary


def validate_cross_arm(summaries: dict[str, dict[str, Any]]) -> None:
    baseline = summaries["B0"]
    for arm in ("O1", "M1"):
        current = summaries[arm]
        require(current["instructions"] == baseline["instructions"],
                f"{arm}: instruction identity differs from B0")
        require(current["ctas"] == baseline["ctas"],
                f"{arm}: CTA identity differs from B0")
        require(current["coverage_uid_identity"] == baseline["coverage_uid_identity"],
                f"{arm}: UID identity differs from B0")
        require(current["artifact_receipt"] == baseline["artifact_receipt"],
                f"{arm}: frozen artifact receipt differs from B0")
        require(current["gates"].get("cross_arm_identity") is True,
                f"{arm}: summarizer cross-arm gate is false")


def delta(candidate: int | float, baseline: int | float) -> int | float:
    return candidate - baseline


def reduction(candidate: int | float, baseline: int | float) -> int | float:
    return baseline - candidate


def percent_change(candidate: int | float, baseline: int | float) -> float:
    require(baseline != 0, "cannot compute percentage against zero baseline")
    return (candidate - baseline) * 100.0 / baseline


def percent_reduction(candidate: int | float, baseline: int | float) -> float:
    return -percent_change(candidate, baseline)


def metrics(summary: dict[str, Any]) -> dict[str, Any]:
    awma = summary["awma"]
    return {
        "cycles": summary["cycles"],
        "l2_accesses": summary["l2_accesses"],
        "l2_misses": summary["l2_misses"],
        "l2_miss_rate": summary["l2_miss_rate"],
        "l2_reservation_fails": summary["l2_reservation_fails"],
        "l2_writeback_transactions": awma["awma_transient_l2_l2_writebacks"],
        "l2_writeback_bytes": awma["awma_transient_l2_l2_writeback_bytes"],
        "transient_writeback_transactions": (
            awma["awma_transient_l2_transient_writebacks"]
        ),
        "transient_writeback_bytes": (
            awma["awma_transient_l2_transient_writeback_bytes"]
        ),
        "dram_read_transactions": summary["dram_n_rd"],
        "dram_read_bytes_64B": summary["dram_read_bytes_64B"],
        "dram_regular_write_transactions": summary["dram_n_write"],
        "dram_regular_write_bytes_64B": summary["dram_regular_write_bytes_64B"],
        "dram_writeback_transactions": summary["dram_n_wr_bk"],
        "dram_writeback_bytes_64B": summary["dram_writeback_bytes_64B"],
        "dead_eviction_drops": awma["awma_transient_l2_dead_eviction_drops"],
        "dead_eviction_drop_bytes": (
            awma["awma_transient_l2_dead_eviction_drop_bytes"]
        ),
        "oracle_drop_dirty_lines": (
            awma["awma_transient_l2_oracle_drop_dirty_lines"]
        ),
        "oracle_drop_bytes": awma["awma_transient_l2_oracle_drop_bytes"],
        "protected_victim_deflections": (
            awma["awma_transient_l2_protected_victim_deflections"]
        ),
        "forced_live_evictions": awma["awma_transient_l2_forced_live_evictions"],
        "fallback_count": awma["awma_transient_l2_fallback_count"],
        "drain_cycles": summary["drain_cycles"],
    }


def comparison(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    base = metrics(baseline)
    cand = metrics(candidate)
    return {
        "cycle_delta": delta(cand["cycles"], base["cycles"]),
        "cycle_change_percent": percent_change(cand["cycles"], base["cycles"]),
        "cycle_improvement_percent": percent_reduction(cand["cycles"], base["cycles"]),
        "l2_access_delta": delta(cand["l2_accesses"], base["l2_accesses"]),
        "l2_miss_delta": delta(cand["l2_misses"], base["l2_misses"]),
        "l2_miss_reduction_percent": percent_reduction(
            cand["l2_misses"], base["l2_misses"]
        ),
        "l2_writeback_reduction_transactions": reduction(
            cand["l2_writeback_transactions"], base["l2_writeback_transactions"]
        ),
        "l2_writeback_reduction_bytes": reduction(
            cand["l2_writeback_bytes"], base["l2_writeback_bytes"]
        ),
        "l2_writeback_reduction_percent": percent_reduction(
            cand["l2_writeback_bytes"], base["l2_writeback_bytes"]
        ),
        "transient_writeback_reduction_bytes": reduction(
            cand["transient_writeback_bytes"], base["transient_writeback_bytes"]
        ),
        "transient_writeback_reduction_percent": percent_reduction(
            cand["transient_writeback_bytes"], base["transient_writeback_bytes"]
        ),
        "dram_read_delta_transactions": delta(
            cand["dram_read_transactions"], base["dram_read_transactions"]
        ),
        "dram_read_delta_bytes_64B": delta(
            cand["dram_read_bytes_64B"], base["dram_read_bytes_64B"]
        ),
        "dram_writeback_reduction_transactions": reduction(
            cand["dram_writeback_transactions"], base["dram_writeback_transactions"]
        ),
        "dram_writeback_reduction_bytes_64B": reduction(
            cand["dram_writeback_bytes_64B"], base["dram_writeback_bytes_64B"]
        ),
        "dram_writeback_reduction_percent": percent_reduction(
            cand["dram_writeback_bytes_64B"], base["dram_writeback_bytes_64B"]
        ),
    }


def decide(summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    b0, o1, m1 = (summaries[arm] for arm in ARMS)
    o1_cmp = comparison(b0, o1)
    m1_cmp = comparison(b0, m1)
    o1_aligned = (
        o1_cmp["transient_writeback_reduction_bytes"] > 0
        and o1_cmp["l2_writeback_reduction_bytes"] > 0
        and o1_cmp["dram_writeback_reduction_bytes_64B"] > 0
        and metrics(o1)["oracle_drop_bytes"] > 0
    )
    # The Goal predeclares 5% only for performance.  It does not define an
    # arbitrary traffic percentage.  "Material traffic" is therefore a strict,
    # mechanism-mediated, directionally concordant reduction across target,
    # controller, and DRAM writeback accounting.
    m1_material_traffic = (
        m1_cmp["transient_writeback_reduction_bytes"] > 0
        and m1_cmp["l2_writeback_reduction_bytes"] > 0
        and m1_cmp["dram_writeback_reduction_bytes_64B"] > 0
        and metrics(m1)["dead_eviction_drop_bytes"] > 0
    )
    performance_flag = abs(m1_cmp["cycle_change_percent"]) >= PERFORMANCE_THRESHOLD_PERCENT
    cycle_gain = m1_cmp["cycle_improvement_percent"] >= PERFORMANCE_THRESHOLD_PERCENT

    if not o1_aligned:
        label = "R101_TRANSIENT_L2_ORACLE_NOT_ALIGNED_WITH_NATIVE"
    elif not m1_material_traffic:
        label = "R101_TRANSIENT_L2_REGION_POLICY_NO_MATERIAL_EFFECT"
    elif cycle_gain:
        label = "R101_TRANSIENT_L2_FIRST_PASS_PROMISING"
    else:
        label = "R101_TRANSIENT_L2_TRAFFIC_RESPONSE_NO_CYCLE_GAIN"

    promising = label == "R101_TRANSIENT_L2_FIRST_PASS_PROMISING"
    return {
        "label": label,
        "o1_mapping_aligned": o1_aligned,
        "m1_material_traffic_reduction": m1_material_traffic,
        "material_traffic_definition": (
            "positive mechanism-mediated target/controller/DRAM writeback-byte "
            "reduction; no unregistered traffic-percent threshold"
        ),
        "performance_threshold_percent": PERFORMANCE_THRESHOLD_PERCENT,
        "m1_material_performance_flag": performance_flag,
        "m1_cycle_gain_at_least_5_percent": cycle_gain,
        "c0_disposition": (
            "REQUIRED_NOT_RUN_FREEZE_M1_FIRST" if promising
            else "NOT_TRIGGERED_M1_NOT_PROMISING"
        ),
        "pre_registered_holdout_available": False,
        "h0_disposition": (
            "HOLDOUT_INPUT_NOT_AVAILABLE" if promising
            else "NOT_TRIGGERED_M1_NOT_PROMISING_NO_PRE_REGISTERED_INPUT"
        ),
    }


def exploration_rows(summaries: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    baseline = summaries["B0"]
    rows = []
    for arm in ARMS:
        summary = summaries[arm]
        item = metrics(summary)
        cmp = comparison(baseline, summary)
        rows.append({
            "arm": arm,
            "mode": summary["mode"],
            "status": summary["status"],
            **item,
            **cmp,
            "coverage_kernels": summary["coverage"]["kernels"],
            "coverage_admissions": summary["coverage"]["admissions"],
            "coverage_untranslated": summary["coverage"]["untranslated"],
            "coverage_unobserved": summary["coverage"]["unobserved"],
            "all_gates_pass": all(summary["gates"].values()),
            "terminal_quiescent": (
                summary["awma"]["awma_transient_l2_terminal_quiescent"]
            ),
            "run_summary_sha256": summary["_summary_sha256"],
        })
    return rows


def traffic_rows(summaries: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    baseline = summaries["B0"]
    rows = []
    for arm in ("O1", "M1"):
        candidate = summaries[arm]
        rows.append({
            "comparison": f"{arm}_VS_B0",
            "baseline_arm": "B0",
            "candidate_arm": arm,
            "baseline_cycles": baseline["cycles"],
            "candidate_cycles": candidate["cycles"],
            **comparison(baseline, candidate),
            "candidate_dead_eviction_drop_bytes": metrics(candidate)[
                "dead_eviction_drop_bytes"
            ],
            "candidate_oracle_drop_bytes": metrics(candidate)["oracle_drop_bytes"],
            "candidate_l2_misses": candidate["l2_misses"],
            "candidate_dram_reads": candidate["dram_n_rd"],
        })
    return rows


def tsv_text(rows: list[dict[str, Any]]) -> str:
    require(bool(rows), "cannot render empty TSV")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), delimiter="\t",
                            lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def file_receipts(run_dir: Path) -> list[dict[str, Any]]:
    receipts = []
    for name in (
        "command.json", "start_utc.txt", "rc.txt", "wall_seconds.txt",
        "run.log", "run.stderr", "gpgpu_inst_stats.txt", "RUN_SUMMARY.json",
    ):
        path = run_dir / name
        require(path.is_file(), f"missing receipt artifact: {path}")
        receipts.append({
            "artifact": name,
            "path": str(path),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    return receipts


def run_receipts(root: Path, summaries: dict[str, dict[str, Any]],
                 decision: dict[str, Any]) -> dict[str, Any]:
    admission = INPUT_ROOT / "ADMISSION_RECEIPT.json"
    sidecar = INPUT_ROOT / "transient_l2_runtime.tsv"
    kernelslist = INPUT_ROOT / "traces/kernelslist.g"
    for path in (RUNNER, SUMMARIZER, admission, sidecar, kernelslist):
        require(path.is_file(), f"receipt input missing: {path}")
    require(sha256(admission) == ADMISSION_RECEIPT_SHA256,
            "formal admission receipt drift during finalization")
    return {
        "stage": STAGE,
        "execution_branch": "hrl/awma-r101-transient-l2-arch-174-v1",
        "source_checkpoint": "f9ecc837e0b7e770135ff52859fdc7fc4de512d2",
        "durable_root": str(root),
        "science_binding": {
            "producer_commit": PRODUCER_COMMIT,
            "accepted_payload_sha256": ACCEPTED_PAYLOAD_SHA256,
            "accepted_output_sha256": ACCEPTED_OUTPUT_SHA256,
            "ordered_trace_aggregate_sha256": TRACE_AGGREGATE_SHA256,
            "admission_receipt_path": str(admission),
            "admission_receipt_sha256": sha256(admission),
            "runtime_sidecar_path": str(sidecar),
            "runtime_sidecar_sha256": sha256(sidecar),
            "kernelslist_path": str(kernelslist),
            "kernelslist_sha256": sha256(kernelslist),
        },
        "frozen_artifacts": summaries["B0"]["artifact_receipt"],
        "formal_tools": {
            "runner_path": str(RUNNER),
            "runner_sha256": sha256(RUNNER),
            "summarizer_path": str(SUMMARIZER),
            "summarizer_sha256": sha256(SUMMARIZER),
        },
        "validation": {
            "status": "PASS",
            "required_arms": list(ARMS),
            "all_summary_status_pass": True,
            "all_summary_gates_pass": True,
            "all_rc_zero": True,
            "all_stderr_empty": True,
            "coverage_kernel_count": 18,
            "full_drain": True,
            "cross_arm_identity": True,
        },
        "arms": {
            arm: {
                "mode": summaries[arm]["mode"],
                "cycles": summaries[arm]["cycles"],
                "instructions": summaries[arm]["instructions"],
                "ctas": summaries[arm]["ctas"],
                "summary_sha256": summaries[arm]["_summary_sha256"],
                "artifacts": file_receipts(root / arm),
            }
            for arm in ARMS
        },
        "comparisons": {
            "O1_VS_B0": comparison(summaries["B0"], summaries["O1"]),
            "M1_VS_B0": comparison(summaries["B0"], summaries["M1"]),
        },
        "decision": decision,
        "engineering_exclusions": [
            {
                "identity": "B0_WB_ONLY_DRAIN_20260928",
                "role": "ENGINEERING_ONLY_EXCLUDED_FROM_FORMAL_MATRIX",
                "path": (
                    "/root/share/mnt164/huangrulin/"
                    "awma_r101_transient_l2_arch_174_v1/raw/engineering/"
                    "B0_WB_ONLY_DRAIN_20260928"
                ),
            },
            {
                "identity": "B0_UID1_COVERAGE_20260927",
                "role": "NONFORMAL_SCOPE_PILOT_ONLY",
                "path": (
                    "/root/share/mnt164/huangrulin/"
                    "awma_r101_transient_l2_arch_174_v1/raw/pilot/"
                    "B0_UID1_COVERAGE_20260927"
                ),
            },
        ],
    }


def atomic_write(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    temporary.write_text(content)
    os.replace(temporary, path)


def write_outputs(pack: Path, matrix: list[dict[str, Any]],
                  traffic: list[dict[str, Any]], receipts: dict[str, Any]) -> None:
    require(pack.is_dir(), f"review-pack directory does not exist: {pack}")
    payloads = {
        pack / "EXPLORATION_MATRIX.tsv": tsv_text(matrix),
        pack / "TRAFFIC_AND_CYCLE_RESULTS.tsv": tsv_text(traffic),
        pack / "RUN_RECEIPTS.json": json.dumps(receipts, indent=2, sort_keys=True) + "\n",
    }
    for path, content in payloads.items():
        atomic_write(path, content)


def fail_closed(message: str, missing_arms: list[str] | None = None) -> int:
    result = {
        "stage": STAGE,
        "status": "FAIL_CLOSED",
        "error": message,
        "missing_arms": missing_arms or [],
        "write_performed": False,
    }
    print(json.dumps(result, sort_keys=True))
    return 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--durable-root", type=Path, default=DEFAULT_DURABLE_ROOT)
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = args.durable_root.resolve()
    missing = [arm for arm in ARMS if not (root / arm / "RUN_SUMMARY.json").is_file()]
    if missing:
        return fail_closed(
            "required durable formal arm(s) missing; no decision or output files produced",
            missing,
        )
    try:
        summaries = {arm: read_arm(root, arm) for arm in ARMS}
        validate_cross_arm(summaries)
        matrix = exploration_rows(summaries)
        traffic = traffic_rows(summaries)
        decision = decide(summaries)
        receipts = run_receipts(root, summaries, decision)
        if args.write:
            write_outputs(args.pack.resolve(), matrix, traffic, receipts)
    except (OSError, ValueError, ValidationError) as exc:
        return fail_closed(str(exc))

    result = {
        "stage": STAGE,
        "status": "PASS",
        "decision": decision,
        "comparisons": receipts["comparisons"],
        "summary_sha256": {
            arm: summaries[arm]["_summary_sha256"] for arm in ARMS
        },
        "write_performed": args.write,
        "written_files": (
            [
                str(args.pack.resolve() / "EXPLORATION_MATRIX.tsv"),
                str(args.pack.resolve() / "TRAFFIC_AND_CYCLE_RESULTS.tsv"),
                str(args.pack.resolve() / "RUN_RECEIPTS.json"),
            ] if args.write else []
        ),
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
