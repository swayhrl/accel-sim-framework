#!/usr/bin/env python3
"""Validate R101R4 immutable formal outputs and publish compact results."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
from typing import Any


STAGE = "AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_V1"
REPO = Path("/root/workspace/accel-sim-framework-awma-r101r4-local-service-path-localization-174-v1")
PACK = REPO / "docs/vm_tlb/review_packs/AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_174_V1"
NODE = Path("/root/share/mnt164/huangrulin/awma_r101r4_local_service_path_localization_174_v1")
B0_ROI = 2_985_319
O2_ROI = 1_130_670
S1_ROI = 2_963_656
GATE = 5.0


class FinalizeError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
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


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def render_tsv(row: dict[str, Any]) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=list(row), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerow(row)
    return out.getvalue().encode()


def formal(arm: str) -> tuple[Path, dict[str, Any]]:
    root = NODE / "raw/formal" / arm
    summary = load(root / "RUN_SUMMARY.json")
    require(summary.get("stage") == STAGE, f"{arm} stage mismatch")
    require(summary.get("arm") == arm, f"{arm} identity mismatch")
    require(summary.get("status") == "PASS", f"{arm} status failed")
    require(summary.get("rc") == 0 and summary.get("stderr_bytes") == 0,
            f"{arm} process result failed")
    gates = summary.get("gates")
    require(isinstance(gates, dict) and gates and all(v is True for v in gates.values()),
            f"{arm} gates failed")
    require((root / "rc.txt").read_text().strip() == "0", f"{arm} rc.txt failed")
    require((root / "run.stderr").stat().st_size == 0, f"{arm} stderr nonempty")
    return root, summary


def delta(summary: dict[str, Any], key: str) -> int | str:
    if key not in summary["roi_end_snapshot"] or key not in summary["context_end_snapshot"]:
        return "NOT_AVAILABLE"
    return summary["roi_end_snapshot"][key] - summary["context_end_snapshot"][key]


def common(arm: str, root: Path, summary: dict[str, Any]) -> dict[str, Any]:
    snapshots = summary["per_kernel_snapshots"]
    improvement = (B0_ROI - summary["roi_cycles"]) * 100.0 / B0_ROI
    return {
        "stage": STAGE,
        "arm": arm,
        "mode": summary["mode"],
        "oracle_label": summary["oracle_label"],
        "status": "PASS",
        "full_context2_cycles": summary["full_context2_total_cycles"],
        "context_end_cycle": summary["context_end_snapshot"]["total_cycles"],
        "kernel4_end_cycle": snapshots[3]["total_cycles"],
        "kernel5_end_cycle": snapshots[4]["total_cycles"],
        "kernel6_end_cycle": snapshots[5]["total_cycles"],
        "roi_cycles": summary["roi_cycles"],
        "cycle_delta_vs_b0": summary["roi_cycles"] - B0_ROI,
        "improvement_percent_vs_b0": improvement,
        "survives_5_percent_gate": improvement >= GATE,
        "instructions": summary["instructions"],
        "ctas": summary["ctas"],
        "context_match": "PASS_EXACT_ACCEPTED_B0_CONTEXT",
        "roi_l1d_accesses": delta(summary, "l1d_accesses"),
        "roi_l1d_misses": delta(summary, "l1d_misses"),
        "roi_l1d_pending_hits": delta(summary, "l1d_pending_hits"),
        "roi_l1d_reservation_fails": delta(summary, "l1d_reservation_fails"),
        "roi_l2_accesses": delta(summary, "l2_accesses"),
        "roi_l2_misses": delta(summary, "l2_misses"),
        "roi_dram_reads": delta(summary, "dram_n_rd"),
        "roi_dram_writes": delta(summary, "dram_n_write"),
        "roi_dram_writebacks": delta(summary, "dram_n_wr_bk"),
        "gate_count": len(summary["gates"]),
        "all_gates_pass": True,
        "summary_sha256": sha256(root / "RUN_SUMMARY.json"),
        "run_log_sha256": sha256(root / "run.log"),
        "command_sha256": sha256(root / "command.json"),
    }


def main() -> int:
    p0_root, p0 = formal("P0")
    p1_root, p1 = formal("P1")
    p0_improvement = (B0_ROI - p0["roi_cycles"]) * 100.0 / B0_ROI
    p1_improvement = (B0_ROI - p1["roi_cycles"]) * 100.0 / B0_ROI
    require(p0_improvement >= GATE, "P1 exists although P0 did not survive")
    require(not (NODE / "raw/formal/FULL5").exists(), "FULL5 must not exist")
    require(not (NODE / "raw/formal/H1").exists(), "H1 must not exist")

    if p1_improvement >= GATE:
        decision = "R101R4_P0_AND_P1_MATERIAL_POST_L1_DOWNSTREAM_LOCALIZED"
        recommendation = "NATIVE_CHECK_WARRANTED_POST_L1_DOWNSTREAM"
        interpretation = (
            "material response survives normal L1 behavior but disappears at the "
            "accepted S1 partition-side placement"
        )
    else:
        decision = "R101R4_P0_MATERIAL_P1_BELOW_GATE_L1_FRONTEND_LOCALIZED"
        recommendation = "NATIVE_CHECK_WARRANTED_L1_FRONTEND"
        interpretation = (
            "the material finite pre-L1 response collapses when normal L1 miss "
            "behavior is restored"
        )

    p0c = p0["controller"]
    p0_row = common("P0", p0_root, p0)
    p0_row.update({
        "decision": decision,
        "qualified_reads": p0c["awma_r101r2_service_qualified_reads"],
        "qualified_ldg_reads": p0c["awma_r101r2_service_qualified_ldg_reads"],
        "qualified_ldgsts_reads": p0c["awma_r101r2_service_qualified_ldgsts_reads"],
        "qualified_writes": p0c["awma_r101r2_service_qualified_writes"],
        "scheduled_capacity": p0c["awma_r101r4_scheduled_capacity"],
        "ready_capacity": p0c["awma_r101r4_ready_capacity"],
        "max_scheduled_depth": p0c["awma_r101r2_service_max_scheduled_depth"],
        "max_ready_depth": p0c["awma_r101r2_service_max_ready_depth"],
        "scheduled_full_cycles": p0c["awma_r101r4_p0_scheduled_full_cycles"],
        "scheduled_full_events": p0c["awma_r101r4_p0_scheduled_full_events"],
        "ready_full_cycles": p0c["awma_r101r4_p0_ready_full_cycles"],
        "ready_full_events": p0c["awma_r101r4_p0_ready_full_events"],
        "ready_eligible": p0c["awma_r101r4_p0_ready_eligible"],
        "eligibility_violations": p0c["awma_r101r4_p0_ready_eligibility_violations"],
        "duplicate_completions": p0c["awma_r101r2_service_duplicate_completions"],
        "outstanding": p0c["awma_r101r2_service_outstanding"],
    })

    p1c = p1["controller"]
    p1_row = common("P1", p1_root, p1)
    p1_row.update({
        "decision": decision,
        "admitted_reads": p1c["awma_r101r4_p1_admitted_reads"],
        "admitted_ldg_reads": p1c["awma_r101r4_p1_admitted_ldg_reads"],
        "admitted_ldgsts_reads": p1c["awma_r101r4_p1_admitted_ldgsts_reads"],
        "admitted_writes": p1c["awma_r101r4_p1_admitted_writes"],
        "request_bytes": p1c["awma_r101r4_p1_request_bytes"],
        "active_bytes": p1c["awma_r101r4_p1_active_bytes"],
        "ready": p1c["awma_r101r4_p1_ready"],
        "delivered_reads": p1c["awma_r101r4_p1_delivered_reads"],
        "delivered_writes": p1c["awma_r101r4_p1_delivered_writes"],
        "max_scheduled_depth": p1c["awma_r101r4_p1_max_scheduled_depth"],
        "max_ready_depth": p1c["awma_r101r4_p1_max_ready_depth"],
        "scheduled_full_cycles": p1c["awma_r101r4_p1_scheduled_full_cycles"],
        "scheduled_full_events": p1c["awma_r101r4_p1_scheduled_full_events"],
        "ready_full_cycles": p1c["awma_r101r4_p1_ready_full_cycles"],
        "ready_full_events": p1c["awma_r101r4_p1_ready_full_events"],
        "latency_violations": p1c["awma_r101r4_p1_latency_violations"],
        "duplicate_completions": p1c["awma_r101r4_p1_duplicate"],
        "outstanding": p1c["awma_r101r4_p1_outstanding"],
    })

    receipts = {
        "stage": STAGE,
        "decision": {
            "label": decision,
            "native_recommendation": recommendation,
            "interpretation": interpretation,
            "gate_percent": GATE,
            "gate_operator": ">=",
            "b0_roi_cycles": B0_ROI,
            "o2_roi_cycles": O2_ROI,
            "s1_roi_cycles": S1_ROI,
            "p0_roi_cycles": p0["roi_cycles"],
            "p0_improvement_percent": p0_improvement,
            "p1_roi_cycles": p1["roi_cycles"],
            "p1_improvement_percent": p1_improvement,
            "nonadditive_warning": "O2/P0/P1/S1 differences are not runtime-component fractions",
        },
        "accepted_comparators": {
            "B0": {"roi_cycles": B0_ROI},
            "O2": {"roi_cycles": O2_ROI},
            "S1": {"roi_cycles": S1_ROI},
        },
        "formal": {
            arm: {
                "run_dir": str(root),
                "summary_sha256": sha256(root / "RUN_SUMMARY.json"),
                "run_log_sha256": sha256(root / "run.log"),
                "command_sha256": sha256(root / "command.json"),
                "recovery_receipt_sha256": (
                    sha256(root / "ORCHESTRATION_RECOVERY.json")
                    if (root / "ORCHESTRATION_RECOVERY.json").is_file()
                    else None
                ),
                "gate_count": len(summary["gates"]),
                "all_gates_pass": True,
                "rc": 0,
                "stderr_bytes": 0,
            }
            for arm, root, summary in (("P0", p0_root, p0), ("P1", p1_root, p1))
        },
        "forbidden_or_untriggered": {
            "FULL5": "NOT_RUN",
            "H1": "NOT_RUN",
            "Lane_F": "NOT_STARTED",
            "Lane_G": "NOT_STARTED",
            "new_109_capture": "NOT_RUN",
            "sweeps": "NOT_RUN",
        },
    }

    p0_blob = render_tsv(p0_row)
    p1_blob = render_tsv(p1_row)
    receipt_blob = (json.dumps(receipts, indent=2, sort_keys=True) + "\n").encode()
    atomic_write(PACK / "P0_CONTEXT2_RESULTS.tsv", p0_blob)
    atomic_write(PACK / "P1_CONTEXT2_RESULTS.tsv", p1_blob)
    atomic_write(PACK / "RUN_RECEIPTS.json", receipt_blob)
    print(json.dumps({
        "status": "PASS",
        "decision": decision,
        "native_recommendation": recommendation,
        "p0_results_sha256": hashlib.sha256(p0_blob).hexdigest(),
        "p1_results_sha256": hashlib.sha256(p1_blob).hexdigest(),
        "receipts_sha256": hashlib.sha256(receipt_blob).hexdigest(),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
