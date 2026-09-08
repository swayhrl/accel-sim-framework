#!/usr/bin/env python3
"""Future-only FAST64 Base/IO/OO triplet consistency validator.

It consumes already strict-parsed compact JSON only.  It launches, signals,
and reads no simulator process or raw output directory beyond the caller's
explicit JSON paths.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


MODES = {"base": "PAPER_BASE", "io": "PAPER_IO", "oo": "PAPER_OO"}
COMMON = ("workload_id", "workload_sha256", "core_sha", "framework_sha")


def read(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"cannot read summary {path}: {error}") from error


def require_metrics(label: str, metrics: dict, names: tuple[str, ...]) -> None:
    absent = [name for name in names if name not in metrics]
    if absent:
        raise SystemExit(f"{label} missing metrics: " + ", ".join(absent))


def equal(label: str, metrics: dict, names: tuple[str, ...]) -> None:
    require_metrics(label, metrics, names)
    values = {metrics[name] for name in names}
    if len(values) != 1:
        raise SystemExit(f"{label} conservation failure: " + ", ".join(names))


def zero(label: str, metrics: dict, names: tuple[str, ...]) -> None:
    require_metrics(label, metrics, names)
    bad = [name for name in names if metrics[name] != 0]
    if bad:
        raise SystemExit(f"{label} terminal state nonzero: " + ", ".join(bad))


def validate_row(label: str, row: dict) -> None:
    metrics = row.get("metrics", {})
    if metrics.get("DTC_L1_mode") != MODES[label]:
        raise SystemExit(f"{label} DTC mode mismatch")
    require_metrics(label, metrics, ("gpu_tot_sim_cycle", "gpu_tot_sim_insn"))
    if metrics["gpu_tot_sim_cycle"] <= 0 or metrics["gpu_tot_sim_insn"] <= 0:
        raise SystemExit(f"{label} lacks positive terminal progress")
    if label == "base":
        equal(label, metrics, ("DTC_L1_pib_admits", "DTC_L1_pib_retires"))
        equal(label, metrics, ("DTC_L1_lower_requests_acquired", "DTC_L1_lower_requests_released"))
        zero(label, metrics, ("DTC_L1_pib_occupancy", "DTC_L1_lower_outstanding"))
    elif label == "io":
        equal(label, metrics, ("DTC_L1_io_lower_created", "DTC_L1_io_lower_issued", "DTC_L1_io_lower_responses"))
        equal(label, metrics, ("DTC_L1_io_completion_dependency_count", "DTC_L1_io_completion_dependency_closed"))
        equal(label, metrics, ("DTC_L1_lower_credit_acquired", "DTC_L1_lower_credit_released"))
        zero(label, metrics, ("DTC_L1_io_inflight_current", "DTC_L1_io_pib_occupancy", "DTC_L1_lower_outstanding"))
    else:
        equal(label, metrics, ("DTC_L1_oo_lower_created", "DTC_L1_oo_lower_issued", "DTC_L1_oo_lower_responses"))
        equal(label, metrics, ("DTC_L1_oo_completion_dependency_count", "DTC_L1_oo_completion_dependency_closed"))
        equal(label, metrics, ("DTC_L1_lower_credit_acquired", "DTC_L1_lower_credit_released"))
        zero(label, metrics, ("DTC_L1_oo_inflight_current", "DTC_L1_oo_pib_occupancy", "DTC_L1_oo_active_refs", "DTC_L1_lower_outstanding"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--io", type=Path, required=True)
    parser.add_argument("--oo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-immutable", action="store_true")
    args = parser.parse_args()

    rows = {label: read(getattr(args, label)) for label in MODES}
    for label, row in rows.items():
        validate_row(label, row)
    provenance = {label: row.get("provenance", {}) for label, row in rows.items()}
    for field in COMMON:
        values = {p.get(field) for p in provenance.values()}
        if None in values or len(values) != 1:
            raise SystemExit("triplet provenance mismatch: " + field)
    trace_values = {row.get("external_artifacts", {}).get("trace_list_sha256") for row in rows.values()}
    if None in trace_values or len(trace_values) != 1:
        raise SystemExit("triplet trace-list identity mismatch")
    insns = {row["metrics"]["gpu_tot_sim_insn"] for row in rows.values()}
    if len(insns) != 1:
        raise SystemExit("triplet dynamic instruction-domain mismatch")

    if args.require_immutable:
        for label, row in rows.items():
            attempt = row.get("immutable_attempt", {})
            missing = [key for key in ("attempt_uuid", "runner_sha256", "start_receipt_sha256", "terminal_receipt_sha256") if not attempt.get(key)]
            if missing:
                raise SystemExit(f"{label} lacks immutable attempt evidence: " + ", ".join(missing))
            p = row["provenance"]
            for key in ("runtime_binary_sha256", "observer_overlay_sha256"):
                if not p.get(key):
                    raise SystemExit(f"{label} lacks formal {key}")
        for key in ("runtime_binary_sha256", "observer_overlay_sha256"):
            if len({p[key] for p in provenance.values()}) != 1:
                raise SystemExit("triplet provenance mismatch: " + key)

    result = {
        "schema": "FAST64_TRIPLET_VALIDATOR_V1",
        "status": "FAST64_TRIPLET_STRICT_VALID_PENDING_STAGE_ACCEPTANCE",
        "require_immutable": args.require_immutable,
        "provenance": provenance,
        "trace_list_sha256": trace_values.pop(),
        "instructions": insns.pop(),
        "cycles": {label: row["metrics"]["gpu_tot_sim_cycle"] for label, row in rows.items()},
        "source_json": {label: str(getattr(args, label)) for label in rows},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("FAST64_TRIPLET_VALIDATOR_V1_PASS output=" + str(args.output))


if __name__ == "__main__":
    main()
