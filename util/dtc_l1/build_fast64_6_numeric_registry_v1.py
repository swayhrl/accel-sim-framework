#!/usr/bin/env python3
"""Build the 74 numeric FAST64.6 cells without touching live run state.

The four source-defined physical-16.5-KiB deadlocks are intentionally excluded:
they are consumed through the separately validated nonnumeric registry.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

import collect_fast64_6_sensitivity_v1 as tool
import collect_fast64_6_sensitivity_v2 as reuse

ROOT = Path(__file__).resolve().parents[2]
DEADLOCK_KEYS = {(w, "physical", "16.5", m) for w in ("BICG", "GESUMMV") for m in tool.MODES}
ALLOWED = {tool.CLASS, "PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE", "STRICT_TERMINAL_ACCEPTED"}


def fail(message: str) -> None:
    raise RuntimeError(message)


def candidate_records() -> list[tuple[Path, dict]]:
    records = []
    root = ROOT / "docs/dtc_l1/fast64/generated"
    for path in root.rglob("*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if record.get("schema") == "dtc_l1_summary_v1":
            records.append((path, record))
    return records


def primary_reuse_sources(path: Path) -> dict[tuple[str, str, str], Path]:
    """Map an exact config identity to its accepted Stage4 evidence path."""
    sources: dict[tuple[str, str, str], Path] = {}
    for row in reuse.read_tsv(path, "workload\t"):
        if row.get("acceptance_status") != "STRICT_TERMINAL_ACCEPTED":
            continue
        evidence = Path(row["evidence_path"])
        if not evidence.is_absolute():
            evidence = ROOT / "docs/dtc_l1/fast64/generated" / evidence
        try:
            record = json.loads(evidence.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            fail(f"PRIMARY_REUSE_SOURCE_UNREADABLE={evidence}: {error}")
        config_sha = record.get("provenance", {}).get("config_sha256", "")
        key = (row["workload"].casefold(), row["mode"], config_sha)
        if not config_sha:
            fail(f"PRIMARY_REUSE_SOURCE_CONFIG_SHA_MISSING={evidence}")
        if key in sources:
            fail(f"PRIMARY_REUSE_SOURCE_DUPLICATE={key}")
        sources[key] = evidence.resolve()
    return sources


def match(path: Path, record: dict, key: tuple[str, str, str, str], spec: dict[str, str], meta: dict[str, str]) -> str | None:
    workload, dimension, point, mode = key
    provenance, metrics = record.get("provenance", {}), record.get("metrics", {})
    if provenance.get("workload_id", "").casefold() != workload.casefold() or provenance.get("config_sha256") != spec["config_sha256"]:
        return None
    if metrics.get("DTC_L1_mode") != f"PAPER_{mode}":
        return None
    for field, expected in (("core_sha", meta["formal_core_sha"]), ("runtime_binary_sha256", meta["formal_runtime_sha256"]),
                            ("observer_overlay_sha256", meta["observer_sha256"]), ("framework_sha", meta["scientific_framework_sha"])):
        if provenance.get(field) != expected:
            return None
    if record.get("external_artifacts", {}).get("trace_list_sha256") != spec["payload_sha256"]:
        return None
    if provenance.get("result_classification") not in ALLOWED:
        return None
    expected_id = tool.expected_config_id({"dimension": dimension, "point": point, "mode": mode})
    return "STRICT_TERMINAL_SENSITIVITY" if provenance.get("config_id") == expected_id else "EXACT_FAST64_4_PRIMARY_REUSE"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--stage4-primary-matrix", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if bool(args.output) == args.dry_run:
        fail("CHOOSE_EXACTLY_ONE_OF_OUTPUT_OR_DRY_RUN")
    meta, matrix = tool.read_matrix(args.matrix)
    records = candidate_records()
    primary = primary_reuse_sources(args.stage4_primary_matrix)
    rows, missing, duplicate = [], [], []
    for key, spec in sorted(matrix.items()):
        if key in DEADLOCK_KEYS:
            continue
        workload, _dimension, _point, mode = key
        found = [(path, origin) for path, record in records if (origin := match(path, record, key, spec, meta))]
        strict_stage6 = [item for item in found
                         if item[1] == "STRICT_TERMINAL_SENSITIVITY" and "fast64_6_" in str(item[0])]
        if strict_stage6:
            # A dedicated Stage6 result remains the literal source for a
            # point that was actually acquired as Stage6.
            found = strict_stage6
        elif any(origin == "EXACT_FAST64_4_PRIMARY_REUSE" for _, origin in found):
            primary_path = primary.get((workload.casefold(), mode, spec["config_sha256"]))
            if primary_path is None:
                fail("PRIMARY_REUSE_ACCEPTED_SOURCE_MISSING=" + "/".join(key))
            primary_record = json.loads(primary_path.read_text(encoding="utf-8"))
            origin = match(primary_path, primary_record, key, spec, meta)
            if origin != "EXACT_FAST64_4_PRIMARY_REUSE":
                fail("PRIMARY_REUSE_ACCEPTED_SOURCE_IDENTITY_MISMATCH=" + "/".join(key))
            found = [(primary_path, origin)]
        # Prefer a dedicated Stage6 record only after exact-primary reuse has
        # been resolved to its accepted source above.
        if found and not strict_stage6:
            preferred = [item for item in found if "fast64_6_" in str(item[0])]
            found = preferred or found
        if len(found) == 1:
            path, origin = found[0]
            rows.append((*key, str(path.relative_to(ROOT)), origin))
        elif not found:
            missing.append("/".join(key))
        else:
            duplicate.append("/".join(key) + "=" + ",".join(str(path.relative_to(ROOT)) for path, _ in found))
    if missing or duplicate:
        print(f"FAST64_6_NUMERIC_REGISTRY_V1_INCOMPLETE found={len(rows)} missing={len(missing)} duplicate={len(duplicate)}")
        if missing:
            print("MISSING=" + ";".join(missing))
        if duplicate:
            print("DUPLICATE=" + ";".join(duplicate))
        return 2
    if len(rows) != 74:
        fail("FAST64_6_NUMERIC_REGISTRY_CARDINALITY_INVALID")
    if args.dry_run:
        print("FAST64_6_NUMERIC_REGISTRY_V1_DRY_RUN_PASS rows=74")
        return 0
    if args.output.exists():
        fail("OUTPUT_ALREADY_EXISTS")
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("workload", "dimension", "point", "mode", "summary", "origin"))
        writer.writerows(rows)
    os.chmod(args.output, 0o444)
    print(f"FAST64_6_NUMERIC_REGISTRY_V1_PASS output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
