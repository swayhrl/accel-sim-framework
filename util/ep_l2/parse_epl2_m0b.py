#!/usr/bin/env python3
"""Fail-closed parser for the observation-only EPL2M0BV1 stream."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

SCHEMA = "EPL2M0BV1"
REQUIRED = {
    "scope", "slice", "completion_cycle", "mshr_instance_epoch",
    "mshr_allocations", "ro_candidate_uncertified", "ro_excluded_write",
    "ro_excluded_atomic", "ro_excluded_writeback",
    "allocation_to_first_lower_issue_count",
    "allocation_to_first_lower_issue_sum", "allocation_to_last_lower_issue",
    "allocation_to_first_fill_count", "allocation_to_first_fill_sum",
    "allocation_to_all_required_sectors_ready_count",
    "allocation_to_all_required_sectors_ready_sum",
    "allocation_to_final_retirement", "last_lower_issue_to_final_retirement",
    "all_ready_to_final_retirement", "wad_dirty_victim_events",
    "wad_old_handle_valid", "wad_old_handle_live_after_reassign",
    "wad_old_handle_not_live_after_reassign", "resident_payload_allocations",
    "nonresident_payload_allocations", "shared_payload_opportunity",
}
TEXT = {"scope", "mshr_instance_epoch", "allocation_to_last_lower_issue",
        "allocation_to_final_retirement", "last_lower_issue_to_final_retirement",
        "all_ready_to_final_retirement", "shared_payload_opportunity"}


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def parse(line):
    bits = line.rstrip().split("|")
    if not bits or bits[0] != SCHEMA:
        return None
    row = {}
    for bit in bits[1:]:
        if "=" not in bit:
            raise ValueError("malformed M0b field: " + bit)
        key, value = bit.split("=", 1)
        if key in row:
            raise ValueError("duplicate M0b field: " + key)
        row[key] = value if key in TEXT else int(value)
    missing = REQUIRED - set(row)
    if missing:
        raise ValueError("missing M0b fields: " + ",".join(sorted(missing)))
    if row["scope"] != "application_cumulative":
        raise ValueError("unexpected M0b scope")
    if row["mshr_instance_epoch"] != "MONOTONIC_ADDRESS_REUSE_SAFE":
        raise ValueError("M0b epoch contract missing")
    if any(row[field] != "NOT_EMITTED" for field in
           ("allocation_to_last_lower_issue", "allocation_to_final_retirement",
            "last_lower_issue_to_final_retirement", "all_ready_to_final_retirement")):
        raise ValueError("M0b unsupported milestone was inferred")
    if row["shared_payload_opportunity"] != "NO_REAL_CONSUMER_YET":
        raise ValueError("unexpected shared-payload classification")
    row["schema_version"] = SCHEMA
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("log", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--framework-commit", default="NA")
    ap.add_argument("--core-commit", default="NA")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rows = [item for line in args.log.read_text(errors="replace").splitlines()
            if (item := parse(line)) is not None]
    if not rows:
        raise ValueError("M0b enabled but no EPL2M0BV1 records were emitted")
    latest = {}
    for row in rows:
        old = latest.get(row["slice"])
        if old is None or row["completion_cycle"] >= old["completion_cycle"]:
            latest[row["slice"]] = row
    rows = [latest[key] for key in sorted(latest)]
    if len(rows) != 64:
        raise ValueError("expected 64 terminal M0b application slices, found %d" % len(rows))
    fields = sorted({key for row in rows for key in row})
    with (args.out / "m0b_application.csv").open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
    summary = {"schema_version": SCHEMA, "application_slice_count": len(rows)}
    for field in REQUIRED - TEXT:
        if field not in {"slice", "completion_cycle"}:
            summary[field] = sum(row[field] for row in rows)
    with (args.out / "m0b_summary.csv").open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=sorted(summary))
        writer.writeheader(); writer.writerow(summary)
    (args.out / "m0b_manifest.json").write_text(json.dumps({
        "schema_version": SCHEMA, "framework_commit": args.framework_commit,
        "core_commit": args.core_commit, "source_log_sha256": digest(args.log),
        "application_slice_count": len(rows),
        "unsupported_milestones": "NOT_EMITTED",
    }, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit("EPL2M0BV1 parser error: %s" % error)
