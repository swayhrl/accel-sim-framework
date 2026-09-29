#!/usr/bin/env python3
"""Validate and publish the final S1-below-gate result tables."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
from typing import Any


STAGE = "AWMA_R101R3_BOUNDED_SERVICE_HANDOFF_V1"
DECISION = "R101R3_S1_BELOW_5_PERCENT_H1_NOT_TRIGGERED"
REPO = Path(
    "/root/workspace/accel-sim-framework-"
    "awma-r101r3-bounded-service-handoff-174-v1"
)
PACK = REPO / (
    "docs/vm_tlb/review_packs/"
    "AWMA_R101R3_BOUNDED_SERVICE_HANDOFF_174_V1"
)
NODE = Path(
    "/root/share/mnt164/huangrulin/"
    "awma_r101r3_bounded_service_handoff_174_v1"
)
S1_DIR = NODE / "raw/formal/S1"
R2_NODE = Path(
    "/root/share/mnt164/huangrulin/"
    "awma_r101r2_context2_memory_service_174_v1"
)
B0_SUMMARY = R2_NODE / "raw/formal/B0/RUN_SUMMARY.json"
O2_SUMMARY = R2_NODE / "raw/formal/O2/RUN_SUMMARY.json"
EXPECTED = {
    "b0_summary": "2c7e2cac39d0cbc1d0b1a1bf6eb4a0ec43c571b4595b4c282e93e9d4e966f24b",
    "o2_summary": "d8aba6635e29b920266964fc6e8b2c5cda70cc5ccc1b80985de32420cdc8857f",
    "s1_summary": "586440d438a26a193a664e7fd355be09f18cd81abdafe568db41dd67f9205674",
    "recovery": "09366400625b238ee2bdd773f4a25587d4574e527a428b594d0ab9fc61d0c0ab",
}
B0_ROI = 2_985_319
O2_ROI = 1_130_670
GATE_PERCENT = 5.0


class FinalizeError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FinalizeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    require(isinstance(value, dict), f"JSON root is not object: {path}")
    return value


def tsv(header: tuple[str, ...], row: tuple[Any, ...]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
    writer.writerow(header)
    writer.writerow(row)
    return stream.getvalue().encode()


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def validate() -> tuple[dict[str, Any], dict[str, Any]]:
    require(sha256(B0_SUMMARY) == EXPECTED["b0_summary"], "B0 summary drift")
    require(sha256(O2_SUMMARY) == EXPECTED["o2_summary"], "O2 summary drift")
    require(sha256(S1_DIR / "RUN_SUMMARY.json") == EXPECTED["s1_summary"],
            "S1 summary drift")
    require(sha256(S1_DIR / "ORCHESTRATION_RECOVERY.json")
            == EXPECTED["recovery"], "S1 recovery receipt drift")
    b0 = load(B0_SUMMARY)
    o2 = load(O2_SUMMARY)
    s1 = load(S1_DIR / "RUN_SUMMARY.json")
    require(b0.get("roi_cycles") == B0_ROI, "accepted B0 ROI drift")
    require(o2.get("roi_cycles") == O2_ROI, "accepted O2 ROI drift")
    require(s1.get("stage") == STAGE and s1.get("status") == "PASS",
            "S1 summary identity/status failed")
    require(s1.get("rc") == 0 and s1.get("stderr_bytes") == 0,
            "S1 process result failed")
    gates = s1.get("gates")
    require(isinstance(gates, dict) and len(gates) == 56,
            "S1 gate count drift")
    require(all(value is True for value in gates.values()),
            "S1 contains a failed/nonboolean gate")
    require((S1_DIR / "rc.txt").read_text().strip() == "0", "rc.txt drift")
    require((S1_DIR / "run.stderr").stat().st_size == 0, "stderr nonempty")
    require(not (NODE / "raw/formal/H1").exists(), "H1 was improperly run")
    require(not (NODE / "raw/formal/FULL5").exists(), "FULL5 was improperly run")
    s1_roi = s1.get("roi_cycles")
    require(type(s1_roi) is int and s1_roi > 0, "invalid S1 ROI")
    improvement = (B0_ROI - s1_roi) * 100.0 / B0_ROI
    require(improvement < GATE_PERCENT, "S1 unexpectedly meets survivor gate")
    decision = {
        "label": DECISION,
        "b0_roi_cycles": B0_ROI,
        "o2_roi_cycles": O2_ROI,
        "s1_roi_cycles": s1_roi,
        "s1_cycle_delta_vs_b0": s1_roi - B0_ROI,
        "s1_improvement_percent": improvement,
        "gate_operator": ">=",
        "gate_percent": GATE_PERCENT,
        "s1_survives": False,
        "h1_disposition": "NOT_TRIGGERED_S1_BELOW_5_PERCENT",
        "l3_disposition": "NOT_TRIGGERED_H1_NOT_RUN",
        "interpretation": (
            "the large pre-L1 O2 headroom does not survive bounded "
            "partition-side hit placement strongly enough in this CONTEXT2"
        ),
        "nonadditive_warning": (
            "O2/S1/B0 percentage differences are not runtime-component "
            "fractions"
        ),
    }
    return s1, decision


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    s1, decision = validate()
    snapshots = s1["per_kernel_snapshots"]
    context = s1["context_end_snapshot"]
    roi = s1["roi_end_snapshot"]
    controller = s1["controller"]
    header = (
        "stage", "arm", "mode", "status", "decision",
        "full_context2_cycles", "context_end_cycle", "kernel4_end_cycle",
        "kernel5_end_cycle", "kernel6_end_cycle", "roi_cycles",
        "cycle_delta_vs_b0", "improvement_percent_vs_b0",
        "instructions", "ctas", "context_match",
        "roi_l1d_accesses", "roi_l1d_misses",
        "roi_l2_accesses", "roi_l2_misses",
        "roi_dram_reads", "roi_dram_writes", "roi_dram_writebacks",
        "s1_served_reads", "s1_served_ldg", "s1_served_ldgsts",
        "s1_served_writes", "s1_served_request_bytes",
        "s1_served_active_bytes", "s1_fallback_requests",
        "s1_head_qualified_cycles", "s1_data_port_busy_cycles",
        "s1_return_queue_full_cycles", "s1_dram_queue_full_cycles",
        "s1_max_ingress_depth", "s1_max_return_depth",
        "s1_subpartition_mask", "duplicate_completions",
        "context_served", "semantics_qualified", "all_56_gates_pass",
        "summary_sha256", "recovery_receipt_sha256",
    )
    row = (
        STAGE, "S1", "s1_partition_hit", "PASS", DECISION,
        s1["full_context2_total_cycles"], context["total_cycles"],
        snapshots[3]["total_cycles"], snapshots[4]["total_cycles"],
        snapshots[5]["total_cycles"], s1["roi_cycles"],
        decision["s1_cycle_delta_vs_b0"],
        decision["s1_improvement_percent"], s1["instructions"], s1["ctas"],
        "PASS_EXACT_ACCEPTED_B0_CONTEXT",
        roi["l1d_accesses"] - context["l1d_accesses"],
        roi["l1d_misses"] - context["l1d_misses"],
        roi["l2_accesses"] - context["l2_accesses"],
        roi["l2_misses"] - context["l2_misses"],
        roi["dram_n_rd"] - context["dram_n_rd"],
        roi["dram_n_write"] - context["dram_n_write"],
        roi["dram_n_wr_bk"] - context["dram_n_wr_bk"],
        controller["awma_r101r3_s1_served_reads"],
        controller["awma_r101r3_s1_served_ldg_reads"],
        controller["awma_r101r3_s1_served_ldgsts_reads"],
        controller["awma_r101r3_s1_served_writes"],
        controller["awma_r101r3_s1_served_request_bytes"],
        controller["awma_r101r3_s1_served_active_bytes"],
        controller["awma_r101r3_s1_fallback_requests"],
        controller["awma_r101r3_s1_head_qualified_cycles"],
        controller["awma_r101r3_s1_data_port_busy_cycles"],
        controller["awma_r101r3_s1_return_queue_full_cycles"],
        controller["awma_r101r3_s1_dram_queue_full_cycles"],
        controller["awma_r101r3_s1_max_ingress_depth"],
        controller["awma_r101r3_s1_max_return_depth"],
        controller["awma_r101r3_s1_subpartition_mask"],
        controller["awma_r101r3_s1_duplicate_completions"],
        controller["awma_r101r3_s1_context_served"],
        controller["awma_r101r3_s1_semantics_qualified"], True,
        EXPECTED["s1_summary"], EXPECTED["recovery"],
    )
    result_blob = tsv(header, row)
    receipts = {
        "stage": STAGE,
        "decision": decision,
        "accepted_comparators": {
            "B0": {"roi_cycles": B0_ROI,
                   "summary_sha256": EXPECTED["b0_summary"]},
            "O2": {"roi_cycles": O2_ROI,
                   "summary_sha256": EXPECTED["o2_summary"]},
        },
        "S1": {
            "run_dir": str(S1_DIR),
            "summary_sha256": EXPECTED["s1_summary"],
            "recovery_receipt_sha256": EXPECTED["recovery"],
            "run_log_sha256": sha256(S1_DIR / "run.log"),
            "command_sha256": sha256(S1_DIR / "command.json"),
            "rc": 0,
            "stderr_bytes": 0,
            "all_gates_pass": True,
            "gate_count": 56,
        },
        "forbidden_or_untriggered": {
            "H1": "NOT_RUN",
            "L3": "NOT_RUN",
            "FULL5": "NOT_RUN",
            "new_109_capture": "NOT_RUN",
            "sweeps": "NOT_RUN",
        },
    }
    receipt_blob = (
        json.dumps(receipts, indent=2, sort_keys=True) + "\n"
    ).encode()
    if args.write:
        atomic_write(PACK / "S1_CONTEXT2_RESULTS.tsv", result_blob)
        atomic_write(PACK / "RUN_RECEIPTS.json", receipt_blob)
    print(json.dumps({
        "stage": STAGE,
        "status": "PASS",
        "decision": decision,
        "write_performed": args.write,
        "s1_results_sha256": hashlib.sha256(result_blob).hexdigest(),
        "run_receipts_sha256": hashlib.sha256(receipt_blob).hexdigest(),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
