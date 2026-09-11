#!/usr/bin/env python3
"""Fail-closed FAST64.7 synthesis of already accepted stage artifacts.

This future-only tool deliberately does not derive a scientific conclusion.
It verifies the prerequisite PASS states and exact source packages, then
materializes a review pack with immutable input hashes for the later handoff.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import shutil
import tempfile
from pathlib import Path

NEEDED = tuple(f"FAST64.{number}" for number in range(7))
STAGE5 = ("fast12_summary.csv", "fast12_stalls.csv", "fast12_live_misses.csv",
          "fast12_traffic.csv", "fast12_io_oo.csv",
          "fast64_5_causal_classification.tsv", "FAST64_5_CAUSAL_ANALYSIS_STATUS.tsv")
STAGE6 = ("fast64_6_cells.tsv", "fast64_6_logical_plot.tsv",
          "fast64_6_physical_plot.tsv", "fast64_6_pib_plot.tsv",
          "fast64_6_raw_manifest.tsv", "fast64_6_expected_deadlocks.tsv",
          "fast64_6_collector_status.tsv")


def fail(message: str) -> None:
    raise RuntimeError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv(path: Path, prefix: str) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    index = next((i for i, line in enumerate(lines) if line.startswith(prefix)), None)
    if index is None:
        fail(f"TSV_SCHEMA_INVALID={path}")
    return list(csv.DictReader(lines[index:], delimiter="\t"))


def require_ledger(path: Path) -> None:
    states = {row.get("stage"): row.get("current_state", row.get("status"))
              for row in tsv(path, "stage\t")}
    missing = [stage for stage in NEEDED if states.get(stage) != "PASS"]
    if missing:
        fail("FAST64_7_PRIOR_PASS_REQUIRED=" + ",".join(missing))


def require_files(directory: Path, names: tuple[str, ...], label: str) -> None:
    missing = [name for name in names if not (directory / name).is_file()]
    if missing:
        fail(f"FAST64_7_{label}_FILES_MISSING=" + ",".join(missing))


def require_fast12(stage5: Path) -> None:
    rows = list(csv.DictReader((stage5 / "fast12_summary.csv").open(encoding="utf-8", newline="")))
    members = {row.get("workload") for row in rows}
    if len(rows) != 13 or "GM-FAST12" not in members or len(members - {"GM-FAST12"}) != 12:
        fail("FAST64_7_STAGE5_EXACT_FAST12_SUMMARY_REQUIRED")
    classes = tsv(stage5 / "fast64_5_causal_classification.tsv", "workload\t")
    if len(classes) != 12 or len({row.get("workload") for row in classes}) != 12:
        fail("FAST64_7_STAGE5_EXACT_CLASSIFICATION_REQUIRED")
    status = {row.get("item"): row.get("value")
              for row in tsv(stage5 / "FAST64_5_CAUSAL_ANALYSIS_STATUS.tsv", "item\t")}
    if status.get("classification_policy") != "SUPPLIED_EVIDENCE_BACKED_NO_AUTOMATIC_CAUSAL_INFERENCE":
        fail("FAST64_7_STAGE5_CLASSIFICATION_POLICY_INVALID")


def copy(source: Path, output: Path, name: str) -> None:
    shutil.copy2(source, output / name)


def csv_as_tsv(source: Path, output: Path, name: str) -> None:
    with source.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            fail(f"CSV_SCHEMA_INVALID={source}")
        records = list(reader)
    write_tsv(output / name, tuple(reader.fieldnames),
              [tuple(record.get(field, "") for field in reader.fieldnames) for record in records])


def write_tsv(path: Path, headings: tuple[str, ...], rows: list[tuple[object, ...]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(headings)
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage-ledger", type=Path, required=True)
    parser.add_argument("--stage3-dir", type=Path, required=True)
    parser.add_argument("--stage4-dir", type=Path, required=True)
    parser.add_argument("--stage5-dir", type=Path, required=True)
    parser.add_argument("--stage6-dir", type=Path, required=True)
    parser.add_argument("--limitations-boundary", type=Path, required=True)
    parser.add_argument("--tier-a-index", type=Path, required=True)
    parser.add_argument("--tier-c-index", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        fail("OUTPUT_DIRECTORY_ALREADY_EXISTS")
    require_ledger(args.stage_ledger)
    require_files(args.stage3_dir, ("fast64_3_structural_pressure.tsv", "fast64_3_live_misses.tsv", "fast64_3_identity_manifest.tsv"), "STAGE3")
    require_files(args.stage4_dir, ("fast64_4_triplets.tsv", "fast64_4_speedup.tsv", "fast64_4_accounting.tsv", "fast64_4_identity_manifest.tsv", "fast64_4_raw_log_index.tsv"), "STAGE4")
    require_files(args.stage5_dir, STAGE5, "STAGE5")
    require_files(args.stage6_dir, STAGE6, "STAGE6")
    for path, label in ((args.limitations_boundary, "LIMITATIONS"), (args.tier_a_index, "TIER_A"), (args.tier_c_index, "TIER_C")):
        if not path.is_file():
            fail(f"FAST64_7_{label}_INPUT_MISSING")
    require_fast12(args.stage5_dir)
    args.output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{args.output_dir.name}.tmp.", dir=args.output_dir.parent))
    try:
        csv_as_tsv(args.stage5_dir / "fast12_summary.csv", temporary, "FAST12_summary.tsv")
        csv_as_tsv(args.stage5_dir / "fast12_stalls.csv", temporary, "structural_pressure.tsv")
        csv_as_tsv(args.stage5_dir / "fast12_live_misses.csv", temporary, "live_misses.tsv")
        csv_as_tsv(args.stage5_dir / "fast12_traffic.csv", temporary, "traffic_pressure.tsv")
        csv_as_tsv(args.stage5_dir / "fast12_io_oo.csv", temporary, "io_oo_mechanism.tsv")
        for name in ("fast64_6_logical_plot.tsv", "fast64_6_physical_plot.tsv", "fast64_6_pib_plot.tsv", "fast64_6_expected_deadlocks.tsv"):
            copy(args.stage6_dir / name, temporary, name)
        copy(args.stage5_dir / "fast64_5_causal_classification.tsv", temporary, "causal_classification.tsv")
        copy(args.limitations_boundary, temporary, "limitations_boundary.md")
        copy(args.tier_a_index, temporary, "tier_a_evidence_index.tsv")
        copy(args.tier_c_index, temporary, "tier_c_auxiliary_evidence_index.tsv")
        copy(args.stage4_dir / "fast64_4_raw_log_index.tsv", temporary, "raw_log_result_manifest.tsv")
        write_tsv(temporary / "aggregate_membership.tsv", ("aggregate", "membership", "source"),
                  [("GM-FAST12", "EXACT_12_ACCEPTED_PRIMARY_MEMBERS", "FAST64.5/fast12_summary.csv")])
        input_paths = [args.stage_ledger, *(args.stage3_dir / name for name in ("fast64_3_structural_pressure.tsv", "fast64_3_live_misses.tsv", "fast64_3_identity_manifest.tsv")), *(args.stage4_dir / name for name in ("fast64_4_triplets.tsv", "fast64_4_speedup.tsv", "fast64_4_accounting.tsv", "fast64_4_identity_manifest.tsv", "fast64_4_raw_log_index.tsv")), *(args.stage5_dir / name for name in STAGE5), *(args.stage6_dir / name for name in STAGE6), args.limitations_boundary, args.tier_a_index, args.tier_c_index]
        write_tsv(temporary / "FAST64_7_INPUT_MANIFEST.tsv", ("input_path", "sha256"), [(str(path), digest(path)) for path in input_paths])
        write_tsv(temporary / "FAST64_7_REVIEW_PACK_STATUS.tsv", ("item", "value"),
                  [("status", "CANDIDATE_REQUIRES_FAST64_7_HANDOFF"), ("prior_stages", "FAST64.0_THROUGH_FAST64.6_PASS"), ("conclusion_policy", "NO_AUTOMATIC_SCIENTIFIC_CONCLUSION"), ("promotion", "NONE")])
        os.chmod(temporary, 0o555)
        os.replace(temporary, args.output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    print(f"FAST64_7_REVIEW_PACK_V2_CANDIDATE_PASS output={args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
