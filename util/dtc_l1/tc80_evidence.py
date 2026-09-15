#!/usr/bin/env python3
"""Fail-closed evidence materializer for the TC80 capacity-matched campaign.

This program never launches a simulator.  It consumes immutable attempts
created by ``tc80_campaign.py`` and the frozen FAST12 authority, verifies the
receipts again, and emits compact CM2--CM5 evidence tables.  All numerical
ratios are derived from integer cycle counts at materialization time.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pathlib import Path


getcontext().prec = 80
PRIMARY_MEMBERS = {
    "ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree",
    "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q",
}
SMOKE_ORDER = ["NN", "Btree", "BICG"]
EXPECTED_BASE_SHA = "1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde"
EXPECTED_TRACE_SHA = "19dd14b3a4b6c1a1cb2833bd091f0dbd485ad79336ef7d4b0c9db1f7c46f504e"
EXPECTED_PRIMARY_OVERLAY_SHA = "92496d3664f24539df8ec4d17fe717b526a8eb5a1a391ef4a2db86e9a3ba44f4"
EXPECTED_CM5_OVERLAY_SHA = "f365018a72901d8d8aeda2088382014b9ddd5369b614da7101680cf6a63f9b93"
CM5_ORDER = ["BICG", "Btree", "2DConvolution"]
CM5_GEOMETRY = "128x5x128=640_lines=81920_bytes"


class EvidenceError(RuntimeError):
    """A materialization precondition failed; no PASS output is emitted."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tsv_read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def tsv_write(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def kv_read(path: Path) -> dict[str, str]:
    rows = tsv_read(path)
    if not rows or set(rows[0]) != {"key", "value"}:
        raise EvidenceError(f"expected key/value TSV: {path}")
    result: dict[str, str] = {}
    for row in rows:
        # RUN_MANIFEST appends terminal fields after its initial receipt.  A
        # repeated key is permitted only when its value is identical.
        key, value = row["key"], row["value"]
        if key in result and result[key] != value:
            raise EvidenceError(f"conflicting key {key!r} in {path}")
        result[key] = value
    return result


def parse_binding(value: str) -> tuple[str, Path]:
    workload, delimiter, location = value.partition("=")
    if delimiter != "=" or not workload or not location:
        raise EvidenceError(f"expected WORKLOAD=/absolute/run-dir binding, got {value!r}")
    path = Path(location)
    if not path.is_absolute():
        raise EvidenceError(f"run directory must be absolute: {location}")
    return workload, path


def load_authority(path: Path) -> dict[str, dict[str, str]]:
    rows = tsv_read(path)
    found = {row["workload"]: row for row in rows}
    if len(found) != len(rows) or set(found) != PRIMARY_MEMBERS:
        raise EvidenceError("frozen authority has duplicate/missing FAST12 workloads")
    if [int(row["ordinal"]) for row in rows] != list(range(1, 13)):
        raise EvidenceError("frozen authority does not carry a unique contiguous authoritative FAST12 order")
    return found


def primary_order(authority: dict[str, dict[str, str]]) -> list[str]:
    """Return the frozen FAST12 order recorded in the hash-bound authority."""
    return [workload for workload, _ in sorted(authority.items(), key=lambda item: int(item[1]["ordinal"]))]


def strict_run(authority: dict[str, dict[str, str]], workload: str, run_dir: Path,
               expected_stage: str, expected_geometry: str = "32x20x128=640_lines=81920_bytes",
               expected_overlay: str = EXPECTED_PRIMARY_OVERLAY_SHA) -> dict[str, object]:
    if workload not in authority:
        raise EvidenceError(f"unknown workload {workload}")
    if not run_dir.is_dir():
        raise EvidenceError(f"missing immutable attempt directory: {run_dir}")
    manifest = kv_read(run_dir / "RUN_MANIFEST.tsv")
    terminal = kv_read(run_dir / "RUN_TERMINAL.tsv")
    validation_path = run_dir / "VALIDATION.json"
    if not validation_path.is_file():
        raise EvidenceError(f"missing strict validation: {validation_path}")
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    expected = authority[workload]
    required_manifest = {
        "stage": expected_stage,
        "workload": workload,
        "ordinal": expected["ordinal"],
        "base_config_sha256": EXPECTED_BASE_SHA,
        "overlay_config_sha256": expected_overlay,
        "trace_config_sha256": EXPECTED_TRACE_SHA,
        "trace_list": expected["trace_list"],
        "trace_list_sha256": expected["trace_list_sha256"],
        "trace_member_count": expected["trace_member_count"],
        "trace_total_bytes": expected["trace_total_bytes"],
        "trace_member_manifest_sha256": expected["trace_member_manifest_sha256"],
        "simulator": expected["runtime_path"],
        "simulator_sha256": expected["runtime_sha256"],
        "core_source_head": expected["run_core_sha"],
        "expected_instructions": expected["instructions"],
        "geometry": expected_geometry,
        "effective_pib": "8",
        "effective_mshr": "32",
    }
    for key, required in required_manifest.items():
        if manifest.get(key) != required:
            raise EvidenceError(
                f"{workload}: immutable receipt mismatch for {key}: "
                f"expected={required!r}; actual={manifest.get(key)!r}"
            )
    if terminal.get("simulator_exit_status") != "0":
        raise EvidenceError(f"{workload}: non-natural simulator exit {terminal.get('simulator_exit_status')}")
    stdout, stderr = run_dir / "simulator.stdout", run_dir / "simulator.stderr"
    for path, receipt_key in ((stdout, "stdout_sha256"), (stderr, "stderr_sha256")):
        if not path.is_file() or terminal.get(receipt_key) != sha256(path):
            raise EvidenceError(f"{workload}: terminal receipt does not bind {path.name}")
    if validation.get("schema") != "TC80_STRICT_VALIDATION_V1" or validation.get("status") != "PASS":
        raise EvidenceError(f"{workload}: strict validator did not pass")
    if validation.get("workload") != workload or validation.get("run_dir") != str(run_dir):
        raise EvidenceError(f"{workload}: strict validation identity mismatch")
    if not validation.get("checks") or not all(validation["checks"].values()):
        raise EvidenceError(f"{workload}: at least one strict validator subcheck is false")
    if int(validation["instructions"]) != int(expected["instructions"]):
        raise EvidenceError(f"{workload}: instruction identity mismatch")
    for metric in ("cycles", "pib_admits", "pib_retires", "pib_occupancy"):
        if not isinstance(validation.get(metric), int):
            raise EvidenceError(f"{workload}: missing integer {metric} in strict validation")
    if validation["cycles"] <= 0 or validation["pib_admits"] != validation["pib_retires"] or validation["pib_occupancy"] != 0:
        raise EvidenceError(f"{workload}: invalid final metric/accounting closure")
    return {
        "workload": workload, "run_dir": str(run_dir), "manifest": manifest,
        "terminal": terminal, "validation": validation, "stdout_sha256": sha256(stdout),
        "stderr_sha256": sha256(stderr), "validation_sha256": sha256(validation_path),
        "manifest_sha256": sha256(run_dir / "RUN_MANIFEST.tsv"),
        "terminal_sha256": sha256(run_dir / "RUN_TERMINAL.tsv"),
    }


def parse_bindings(values: list[str], expected: list[str]) -> dict[str, Path]:
    bindings = dict(parse_binding(value) for value in values)
    if set(bindings) != set(expected) or len(bindings) != len(values):
        raise EvidenceError(f"bindings must be one each for {expected}; got {sorted(bindings)}")
    return bindings


def status_row(stage: str, status: str, authority: Path, artifacts: list[Path], detail: str) -> dict[str, object]:
    return {
        "stage": stage, "status": status, "input_commit_or_hash": f"authority_sha256={sha256(authority)}",
        "output_artifacts": ";".join(str(item) for item in artifacts), "blocking_reason": "NONE",
        "detail": detail,
    }


def emit_cm2(args: argparse.Namespace) -> None:
    authority_path, out_dir = Path(args.authority), Path(args.output_dir)
    authority = load_authority(authority_path)
    bindings = parse_bindings(args.accepted, SMOKE_ORDER)
    records = [strict_run(authority, workload, bindings[workload], "CM2") for workload in SMOKE_ORDER]
    fields = [
        "workload", "attempt_uuid", "prior_attempt_lineage", "run_dir", "runner_sha256", "runtime_sha256",
        "core_source_head", "trace_list_sha256", "trace_member_count", "trace_total_bytes",
        "trace_member_manifest_sha256", "tc80_overlay_sha256", "geometry", "effective_pib", "effective_mshr",
        "launch_utc", "terminal_utc", "simulator_exit_status", "instructions", "cycles", "pib_admits",
        "pib_retires", "pib_occupancy", "strict_validation_sha256", "disposition",
    ]
    failures = {
        "NN": "cm2_11_NN_5eece021-1378-482e-a3ae-4e52b4b31ec3:CONTROLLER_OR_PARSER_FAILURE:relative config path after cwd; preserved, no simulator result accepted",
        "Btree": "NONE",
        "BICG": "CLI_PREFLIGHT_REJECTION:no attempt directory/no simulator launch; omitted required --trace-config",
    }
    manifest_rows: list[dict[str, object]] = []
    validation_rows: list[dict[str, object]] = []
    provenance_rows: list[dict[str, object]] = []
    for record in records:
        m, v, t = record["manifest"], record["validation"], record["terminal"]
        shared = {
            "workload": record["workload"], "attempt_uuid": m["attempt_uuid"],
            "prior_attempt_lineage": failures[record["workload"]], "run_dir": record["run_dir"],
            "runner_sha256": m["runner_sha256"], "runtime_sha256": m["simulator_sha256"],
            "core_source_head": m["core_source_head"], "trace_list_sha256": m["trace_list_sha256"],
            "trace_member_count": m["trace_member_count"], "trace_total_bytes": m["trace_total_bytes"],
            "trace_member_manifest_sha256": m["trace_member_manifest_sha256"],
            "tc80_overlay_sha256": m["overlay_config_sha256"], "geometry": m["geometry"],
            "effective_pib": m["effective_pib"], "effective_mshr": m["effective_mshr"],
            "launch_utc": m["launch_utc"], "terminal_utc": t["terminal_utc"],
            "simulator_exit_status": t["simulator_exit_status"], "instructions": v["instructions"],
            "cycles": v["cycles"], "pib_admits": v["pib_admits"], "pib_retires": v["pib_retires"],
            "pib_occupancy": v["pib_occupancy"], "strict_validation_sha256": record["validation_sha256"],
            "disposition": "ACCEPTED_STRICT_PASS",
        }
        manifest_rows.append(shared)
        validation_rows.append({
            "workload": record["workload"], "attempt_uuid": m["attempt_uuid"], "strict_status": v["status"],
            "all_subchecks_pass": "YES", "natural_exit": "YES", "instruction_identity": "YES",
            "fatal_assert_deadlock_error_scan": "PASS", "terminal_accounting": "CLOSED",
            "cycles": v["cycles"], "instructions": v["instructions"], "validation_json_sha256": record["validation_sha256"],
        })
        provenance_rows.append({
            "workload": record["workload"], "attempt_uuid": m["attempt_uuid"], "run_dir": record["run_dir"],
            "run_manifest_sha256": record["manifest_sha256"], "run_terminal_sha256": record["terminal_sha256"],
            "simulator_stdout_sha256": record["stdout_sha256"], "simulator_stderr_sha256": record["stderr_sha256"],
            "strict_validation_sha256": record["validation_sha256"], "prior_attempt_lineage": failures[record["workload"]],
        })
    manifest_path = out_dir / "CM2_SMOKE_RUN_MANIFEST.tsv"
    validation_path = out_dir / "CM2_SMOKE_VALIDATION.tsv"
    provenance_path = out_dir / "CM2_RAW_PROVENANCE.tsv"
    tsv_write(manifest_path, fields, manifest_rows)
    tsv_write(validation_path, list(validation_rows[0]), validation_rows)
    tsv_write(provenance_path, list(provenance_rows[0]), provenance_rows)
    status_path = out_dir / "status" / "CM2_STATUS.tsv"
    tsv_write(status_path, ["stage", "status", "input_commit_or_hash", "output_artifacts", "blocking_reason", "detail"], [
        status_row("CM2", "PASS", authority_path, [manifest_path, validation_path, provenance_path],
                   "NN, Btree, and BICG each have one unique, natural, strict-accepted exact-TC80 attempt.")
    ])


def decimal_ratio(numerator: int, denominator: int) -> Decimal:
    if numerator <= 0 or denominator <= 0:
        raise EvidenceError("cycles must be positive integers")
    return Decimal(numerator) / Decimal(denominator)


def display_decimal(value: Decimal, places: int = 12) -> str:
    return str(value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def emit_cm3(args: argparse.Namespace) -> None:
    authority_path, out_dir = Path(args.authority), Path(args.output_dir)
    authority = load_authority(authority_path)
    order = primary_order(authority)
    bindings = parse_bindings(args.accepted, order)
    records = [strict_run(authority, workload, bindings[workload], "CM3") for workload in order]
    run_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    io_rows: list[dict[str, object]] = []
    for record in records:
        workload, m, v, t = record["workload"], record["manifest"], record["validation"], record["terminal"]
        frozen = authority[workload]
        run_rows.append({
            "ordinal": frozen["ordinal"], "workload": workload, "attempt_uuid": m["attempt_uuid"],
            "run_dir": record["run_dir"], "geometry": m["geometry"], "core_source_head": m["core_source_head"],
            "runner_sha256": m["runner_sha256"], "runtime_sha256": m["simulator_sha256"],
            "trace_list_sha256": m["trace_list_sha256"], "trace_member_manifest_sha256": m["trace_member_manifest_sha256"],
            "instructions": v["instructions"], "cycles": v["cycles"], "natural_exit": t["simulator_exit_status"],
            "strict_validation_sha256": record["validation_sha256"], "disposition": "ACCEPTED_STRICT_PASS",
        })
        b16, tc80, io, oo = (int(frozen["b16_cycles"]), int(v["cycles"]), int(frozen["io_cycles"]), int(frozen["oo_cycles"]))
        summary_rows.append({
            "workload": workload, "instructions": frozen["instructions"], "b16_cycles": b16, "tc80_cycles": tc80,
            "io_cycles": io, "oo_cycles": oo,
            "speedup_tc80_over_b16": display_decimal(decimal_ratio(b16, tc80)),
            "speedup_io_over_b16": display_decimal(decimal_ratio(b16, io)),
            "speedup_oo_over_b16": display_decimal(decimal_ratio(b16, oo)),
            "speedup_io_over_tc80": display_decimal(decimal_ratio(tc80, io)),
            "speedup_oo_over_tc80": display_decimal(decimal_ratio(tc80, oo)),
            "b16_source": frozen["b16_source_log"], "tc80_source": record["run_dir"],
            "io_source": frozen["io_source_log"], "oo_source": frozen["oo_source_log"],
        })
        io_rows.append({
            "workload": workload, "frozen_authority_sha256": sha256(authority_path),
            "b16_source_log": frozen["b16_source_log"], "b16_stdout_sha256": frozen["b16_source_stdout_sha256"],
            "io_source_log": frozen["io_source_log"], "io_stdout_sha256": frozen["io_source_stdout_sha256"],
            "oo_source_log": frozen["oo_source_log"], "oo_stdout_sha256": frozen["oo_source_stdout_sha256"],
            "tc80_run_dir": record["run_dir"], "tc80_stdout_sha256": record["stdout_sha256"],
            "tc80_validation_sha256": record["validation_sha256"],
        })
    manifest_path = out_dir / "CM3_TC80_FAST12_RUN_MANIFEST.tsv"
    summary_path = out_dir / "CM3_TC80_FAST12_SUMMARY.tsv"
    binding_path = out_dir / "CM3_TC80_INPUT_AND_OUTPUT_MANIFEST.tsv"
    tsv_write(manifest_path, list(run_rows[0]), run_rows)
    tsv_write(summary_path, list(summary_rows[0]), summary_rows)
    tsv_write(binding_path, list(io_rows[0]), io_rows)
    status_path = out_dir / "status" / "CM3_STATUS.tsv"
    tsv_write(status_path, ["stage", "status", "input_commit_or_hash", "output_artifacts", "blocking_reason", "detail"], [
        status_row("CM3", "PASS", authority_path, [manifest_path, summary_path, binding_path],
                   "Exactly 12 ordered TC80-only primary runs have unique strict-accepted immutable receipts; B16/IO/OO are frozen bindings.")
    ])


def gm(values: list[Decimal]) -> Decimal:
    if not values or any(value <= 0 for value in values):
        raise EvidenceError("geometric mean requires positive values")
    return (sum((value.ln() for value in values), Decimal(0)) / Decimal(len(values))).exp()


def classify(ratio: Decimal, numerator: str, denominator: str) -> str:
    if ratio > Decimal("1.01"):
        return f"{numerator}_BEATS_{denominator}"
    if ratio < Decimal("0.99"):
        return f"{denominator}_BEATS_{numerator}"
    return "NEAR_TIE"


def emit_cm4(args: argparse.Namespace) -> None:
    authority_path, summary_path, out_dir = Path(args.authority), Path(args.summary), Path(args.output_dir)
    authority = load_authority(authority_path)
    rows = tsv_read(summary_path)
    if [row.get("workload") for row in rows] != primary_order(authority) or len(rows) != 12:
        raise EvidenceError("CM4 requires exact ordered 12-row CM3 primary summary")
    comparison: list[dict[str, object]] = []
    tc80_ratios: list[Decimal] = []
    io_ratios: list[Decimal] = []
    oo_ratios: list[Decimal] = []
    io_tc80_ratios: list[Decimal] = []
    oo_tc80_ratios: list[Decimal] = []
    for row in rows:
        workload = row["workload"]
        frozen = authority[workload]
        b16, tc80, io, oo = (int(row["b16_cycles"]), int(row["tc80_cycles"]), int(row["io_cycles"]), int(row["oo_cycles"]))
        if (str(b16), str(io), str(oo)) != (frozen["b16_cycles"], frozen["io_cycles"], frozen["oo_cycles"]):
            raise EvidenceError(f"{workload}: summary frozen cycle values do not match authority")
        tc80_b16, io_b16, oo_b16 = decimal_ratio(b16, tc80), decimal_ratio(b16, io), decimal_ratio(b16, oo)
        io_tc80, oo_tc80 = decimal_ratio(tc80, io), decimal_ratio(tc80, oo)
        tc80_ratios.append(tc80_b16); io_ratios.append(io_b16); oo_ratios.append(oo_b16)
        io_tc80_ratios.append(io_tc80); oo_tc80_ratios.append(oo_tc80)
        comparison.append({
            "workload": workload, "b16_cycles": b16, "tc80_cycles": tc80, "io_cycles": io, "oo_cycles": oo,
            "tc80_over_b16": display_decimal(tc80_b16), "io_over_b16": display_decimal(io_b16),
            "oo_over_b16": display_decimal(oo_b16), "io_over_tc80": display_decimal(io_tc80),
            "oo_over_tc80": display_decimal(oo_tc80), "tc80_vs_io_classification": classify(io_tc80, "IO", "TC80"),
            "tc80_vs_oo_classification": classify(oo_tc80, "OO", "TC80"),
            "classification_tolerance": "symmetric_1_percent: ratio>1.01 numerator faster; 0.99<=ratio<=1.01 NEAR_TIE; ratio<0.99 denominator faster",
        })
    gms = {
        "GM_TC80_OVER_B16": gm(tc80_ratios), "GM_IO_OVER_B16": gm(io_ratios), "GM_OO_OVER_B16": gm(oo_ratios),
        "GM_IO_OVER_TC80": gm(io_tc80_ratios), "GM_OO_OVER_TC80": gm(oo_tc80_ratios),
    }
    expected = {"GM_IO_OVER_B16": Decimal("1.326143376"), "GM_OO_OVER_B16": Decimal("1.592062402")}
    for key, accepted in expected.items():
        if abs(gms[key] - accepted) > Decimal("0.0000000005"):
            raise EvidenceError(f"frozen {key} does not reproduce accepted value: {gms[key]} vs {accepted}")
    comparison.extend({
        "workload": key, "b16_cycles": "N/A", "tc80_cycles": "N/A", "io_cycles": "N/A", "oo_cycles": "N/A",
        "tc80_over_b16": display_decimal(gms["GM_TC80_OVER_B16"]) if key == "GM_TC80_OVER_B16" else "N/A",
        "io_over_b16": display_decimal(gms["GM_IO_OVER_B16"]) if key == "GM_IO_OVER_B16" else "N/A",
        "oo_over_b16": display_decimal(gms["GM_OO_OVER_B16"]) if key == "GM_OO_OVER_B16" else "N/A",
        "io_over_tc80": display_decimal(gms["GM_IO_OVER_TC80"]) if key == "GM_IO_OVER_TC80" else "N/A",
        "oo_over_tc80": display_decimal(gms["GM_OO_OVER_TC80"]) if key == "GM_OO_OVER_TC80" else "N/A",
        "tc80_vs_io_classification": "N/A", "tc80_vs_oo_classification": "N/A", "classification_tolerance": "N/A",
    } for key in gms)
    comparison_path = out_dir / "CM4_CAPACITY_MATCHED_COMPARISON.tsv"
    plot_path = out_dir / "CM4_PAPER_PLOT_READY.tsv"
    tsv_write(comparison_path, list(comparison[0]), comparison)
    plot_fields = ["workload", "tc80_over_b16", "io_over_b16", "oo_over_b16", "io_over_tc80", "oo_over_tc80"]
    plot_rows = [{field: row[field] for field in plot_fields} for row in comparison
                 if not row["workload"].startswith("GM_")]
    tsv_write(plot_path, plot_fields, plot_rows)
    analysis_path = out_dir / "CM4_CAPACITY_MATCHED_ANALYSIS.md"
    write_text(analysis_path, "# TC80 capacity-matched fairness analysis\n\n"
               "All ratios are regenerated from the exact 12 integer-cycle rows in CM3; displayed values are rounded only after the calculation. "
               "The classification columns use the declared symmetric 1% presentation window and never replace the numeric ratios.\n\n"
               "TC80 is an exact 80-KiB conventional cache: all 80 KiB are ordinary searchable locality capacity. DTC instead couples a 16-KiB logical searchable Tag capacity to an 80-KiB physical data pool. Thus the experiment tests ordinary locality capacity versus decoupled in-flight physical state under the same data-array byte budget. TC80 deliberately has more searchable Tag entries and is a strong conventional-capacity baseline.\n\n"
               "This is not a claim of equal total area, timing, power, metadata cost, or a causal attribution solely to Tag/Data decoupling. PIB and MSHR remain the frozen B16 values (8 and 32), so this experiment does not evaluate a large-PIB/large-MSHR conventional cache.\n\n"
               "## Geometric means\n\n" + "\n".join(f"- `{key}` = `{display_decimal(value)}`" for key, value in gms.items()) + "\n")
    status_path = out_dir / "status" / "CM4_STATUS.tsv"
    tsv_write(status_path, ["stage", "status", "input_commit_or_hash", "output_artifacts", "blocking_reason", "detail"], [
        status_row("CM4", "PASS", authority_path, [comparison_path, analysis_path, plot_path],
                   "Five geometric means regenerated from unrounded integer cycles; frozen IO/B16 and OO/B16 GMs reproduce accepted values.")
    ])


def primary_summary_by_workload(authority: dict[str, dict[str, str]], summary_path: Path) -> dict[str, dict[str, str]]:
    """Accept only the complete, ordered CM3 primary table and bind frozen fields."""
    rows = tsv_read(summary_path)
    order = primary_order(authority)
    if [row.get("workload") for row in rows] != order or len(rows) != len(order):
        raise EvidenceError("expected exact ordered 12-row CM3 primary summary")
    result = {row["workload"]: row for row in rows}
    for workload in order:
        frozen, row = authority[workload], result[workload]
        for field, frozen_field in (("instructions", "instructions"), ("b16_cycles", "b16_cycles"),
                                    ("io_cycles", "io_cycles"), ("oo_cycles", "oo_cycles")):
            if row.get(field) != frozen[frozen_field]:
                raise EvidenceError(f"{workload}: CM3 {field} does not bind frozen authority")
        if int(row["tc80_cycles"]) <= 0:
            raise EvidenceError(f"{workload}: nonpositive CM3 primary cycles")
    return result


def emit_cm5(args: argparse.Namespace) -> None:
    """Materialize the predeclared alternate-geometry diagnostic, never a primary row."""
    authority_path, summary_path, out_dir = Path(args.authority), Path(args.primary_summary), Path(args.output_dir)
    authority = load_authority(authority_path)
    primary = primary_summary_by_workload(authority, summary_path)
    bindings = parse_bindings(args.accepted, CM5_ORDER)
    records = [strict_run(authority, workload, bindings[workload], "CM5", CM5_GEOMETRY, EXPECTED_CM5_OVERLAY_SHA)
               for workload in CM5_ORDER]

    rows: list[dict[str, object]] = []
    analysis_rows: list[str] = []
    for record in records:
        workload, manifest, validation, terminal = (
            record["workload"], record["manifest"], record["validation"], record["terminal"])
        primary_cycles, alternate_cycles = int(primary[workload]["tc80_cycles"]), int(validation["cycles"])
        ratio = decimal_ratio(primary_cycles, alternate_cycles)
        rows.append({
            "workload": workload, "diagnostic_role": "CM5_EXACT80_GEOMETRY_ROBUSTNESS_ONLY",
            "primary_geometry": "32x20x128=640_lines=81920_bytes", "alternate_geometry": manifest["geometry"],
            "primary_tc80_cycles": primary_cycles, "alternate_tc80_cycles": alternate_cycles,
            "primary_over_alternate_speed_ratio": display_decimal(ratio),
            "attempt_uuid": manifest["attempt_uuid"], "run_dir": record["run_dir"],
            "runner_sha256": manifest["runner_sha256"], "runtime_sha256": manifest["simulator_sha256"],
            "core_source_head": manifest["core_source_head"], "trace_list_sha256": manifest["trace_list_sha256"],
            "trace_member_manifest_sha256": manifest["trace_member_manifest_sha256"],
            "alternate_overlay_sha256": manifest["overlay_config_sha256"], "effective_pib": manifest["effective_pib"],
            "effective_mshr": manifest["effective_mshr"], "instructions": validation["instructions"],
            "pib_admits": validation["pib_admits"], "pib_retires": validation["pib_retires"],
            "pib_occupancy": validation["pib_occupancy"], "natural_exit": terminal["simulator_exit_status"],
            "strict_validation_sha256": record["validation_sha256"],
            "primary_gm_membership": "EXCLUDED", "disposition": "ACCEPTED_STRICT_PASS_DIAGNOSTIC",
        })
        analysis_rows.append(
            f"- `{workload}`: primary 32x20 cycles = `{primary_cycles}`, alternate 128x5 cycles = "
            f"`{alternate_cycles}`, primary/alternate ratio = `{display_decimal(ratio)}`.")

    runs_path = out_dir / "CM5_GEOMETRY_ROBUSTNESS_RUNS.tsv"
    analysis_path = out_dir / "CM5_GEOMETRY_ROBUSTNESS_ANALYSIS.md"
    tsv_write(runs_path, list(rows[0]), rows)
    write_text(analysis_path, "# CM5 exact-80-KiB geometry robustness diagnostic\n\n"
               "CM5 was mandatory before CM3 results because the primary 32-set × 20-way geometry exceeds eight ways "
               "and CM0 proved multiple exact-80-KiB source-legal geometries. The alternate 128-set × 5-way overlay was "
               "predeclared before any primary TC80 result. It holds conventional data capacity at 640 lines / 81,920 B and "
               "holds line size, policies, PIB=8, MSHR=32, Base mode, and modeled L1 latency fixed; it changes only set/way geometry.\n\n"
               "Each row below naturally terminated and passed the same strict identity, runtime-echo, trace, error-scan, and "
               "terminal-PIB checks as CM3. These are diagnostics only: they are excluded from CM3, all five primary geometric means, "
               "and any performance-selected geometry choice. Different geometry performance is descriptive, not a failure condition "
               "or causal attribution.\n\n## Measured diagnostic ratios\n\n" + "\n".join(analysis_rows) + "\n\n"
               "The presence of a valid exact-capacity alternate result prevents treating the primary 20-way representation as the only "
               "available model. This bounded check does not establish total-area equality, timing/power equivalence, or the behavior "
               "of a large-PIB/large-MSHR conventional cache.\n")
    status_path = out_dir / "status" / "CM5_STATUS.tsv"
    tsv_write(status_path, ["stage", "status", "input_commit_or_hash", "output_artifacts", "blocking_reason", "detail"], [
        status_row("CM5", "PASS", authority_path, [runs_path, analysis_path],
                   "Predeclared 128x5 exact-80-KiB diagnostic completed for BICG, Btree, and 2DConvolution; all rows strict-pass and are excluded from CM3/primary GMs.")
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    cm2 = commands.add_parser("emit-cm2")
    cm2.add_argument("--authority", required=True)
    cm2.add_argument("--output-dir", required=True)
    cm2.add_argument("--accepted", action="append", required=True,
                     help="repeat NN=/absolute/run-dir, Btree=/..., BICG=/...")
    cm2.set_defaults(function=emit_cm2)
    cm3 = commands.add_parser("emit-cm3")
    cm3.add_argument("--authority", required=True)
    cm3.add_argument("--output-dir", required=True)
    cm3.add_argument("--accepted", action="append", required=True,
                     help="repeat WORKLOAD=/absolute/run-dir for all 12 exact FAST12 members")
    cm3.set_defaults(function=emit_cm3)
    cm4 = commands.add_parser("emit-cm4")
    cm4.add_argument("--authority", required=True)
    cm4.add_argument("--summary", required=True)
    cm4.add_argument("--output-dir", required=True)
    cm4.set_defaults(function=emit_cm4)
    cm5 = commands.add_parser("emit-cm5")
    cm5.add_argument("--authority", required=True)
    cm5.add_argument("--primary-summary", required=True)
    cm5.add_argument("--output-dir", required=True)
    cm5.add_argument("--accepted", action="append", required=True,
                     help="repeat BICG=/absolute/run-dir, Btree=/..., 2DConvolution=/...")
    cm5.set_defaults(function=emit_cm5)
    args = parser.parse_args()
    try:
        args.function(args)
    except (EvidenceError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"TC80 evidence materialization rejected: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
