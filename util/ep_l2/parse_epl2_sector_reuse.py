#!/usr/bin/env python3
"""Streaming, fail-closed aggregation for EPL2SRV1 terminal slice records."""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

SCHEMA = "EPL2SRV1"
BINS = ("<=8", "9-16", "17-32", "33-64", "65-128", "129-256",
        "257-512", "513-1024", "1025-2048", "2049-4096", ">4096")
BIN_KEYS = ("sector_reuse_le8", "sector_reuse_9_16", "sector_reuse_17_32",
            "sector_reuse_33_64", "sector_reuse_65_128",
            "sector_reuse_129_256", "sector_reuse_257_512",
            "sector_reuse_513_1024", "sector_reuse_1025_2048",
            "sector_reuse_2049_4096", "sector_reuse_gt4096")
REQUIRED = {"scope", "slice", "kernel_uid", "total_sector_reference_events",
            "excluded_writeback_requests", "new_sector_on_new_line_events",
            "new_sector_on_seen_line_events", "temporal_sector_reuse_instances",
            "unique_sector_identities", "unique_sectors_reused_at_least_once",
            "one_touch_unique_sectors", *BIN_KEYS}

def parse(line):
    fields = line.rstrip("\n").split("|")
    if not fields or fields[0] != SCHEMA:
        return None
    row = {}
    for item in fields[1:]:
        if "=" not in item:
            raise ValueError("malformed EPL2SRV1 field: " + item)
        key, value = item.split("=", 1)
        if key in row:
            raise ValueError("duplicate EPL2SRV1 field: " + key)
        row[key] = value if key == "scope" else int(value)
    missing = REQUIRED.difference(row)
    if missing:
        raise ValueError("missing EPL2SRV1 fields: " + ",".join(sorted(missing)))
    unknown = set(row).difference(REQUIRED)
    if unknown:
        raise ValueError("unexpected EPL2SRV1 fields: " + ",".join(sorted(unknown)))
    return row

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def write(path, rows):
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def ratio(numerator, denominator):
    return numerator / denominator if denominator else "NA"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--workload", required=True)
    parser.add_argument("--framework-commit", required=True)
    parser.add_argument("--core-commit", required=True)
    parser.add_argument("--config-sha256", required=True)
    parser.add_argument("--trace-id", required=True)
    parser.add_argument("--expected-slices", type=int, default=64)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    apps, application_records_seen, superseded_snapshots = {}, 0, 0
    # Deliberately process one line at a time; simulator logs may be multi-GB.
    with args.log.open("r", encoding="utf-8", errors="replace") as source:
        for line in source:
            row = parse(line)
            if row is None or row["scope"] != "application":
                continue
            slice_id = row["slice"]
            application_records_seen += 1
            if slice_id in apps:
                # Application records are cumulative snapshots emitted at every
                # kernel boundary.  Select the final log-order snapshot, but
                # fail closed if any counter goes backwards on the way there.
                previous = apps[slice_id]
                for key, value in row.items():
                    if isinstance(value, int) and key not in ("slice", "kernel_uid"):
                        if value < previous[key]:
                            raise ValueError("non-monotonic application snapshot for slice %d field %s" %
                                             (slice_id, key))
                superseded_snapshots += 1
            apps[slice_id] = row
    if len(apps) != args.expected_slices:
        raise ValueError("expected exactly %d application slice records, found %d" %
                         (args.expected_slices, len(apps)))

    total = defaultdict(int)
    for row in apps.values():
        for key, value in row.items():
            if isinstance(value, int) and key not in ("slice", "kernel_uid"):
                total[key] += value
    classified = (total["new_sector_on_new_line_events"] +
                  total["new_sector_on_seen_line_events"] +
                  total["temporal_sector_reuse_instances"])
    if classified != total["total_sector_reference_events"]:
        raise ValueError("sector classification conservation failed")
    if (total["unique_sectors_reused_at_least_once"] +
            total["one_touch_unique_sectors"] != total["unique_sector_identities"]):
        raise ValueError("sector coverage conservation failed")
    if sum(total[key] for key in BIN_KEYS) != total["temporal_sector_reuse_instances"]:
        raise ValueError("sector reuse-distance closure failed")

    summary = dict(workload=args.workload, **total)
    summary.update({
        "sector_temporal_reuse_fraction": ratio(total["temporal_sector_reuse_instances"], total["total_sector_reference_events"]),
        "spatial_new_sector_fraction": ratio(total["new_sector_on_seen_line_events"], total["total_sector_reference_events"]),
        "cold_new_line_sector_fraction": ratio(total["new_sector_on_new_line_events"], total["total_sector_reference_events"]),
        "one_touch_sector_fraction": ratio(total["one_touch_unique_sectors"], total["unique_sector_identities"]),
        "far_sector_reuse_share_gt1024": ratio(total["sector_reuse_1025_2048"] + total["sector_reuse_2049_4096"] + total["sector_reuse_gt4096"], total["temporal_sector_reuse_instances"]),
        "far_sector_reuse_share_gt4096": ratio(total["sector_reuse_gt4096"], total["temporal_sector_reuse_instances"]),
    })
    distance = {"workload": args.workload, "temporal_sector_reuse_instances": total["temporal_sector_reuse_instances"]}
    for label, key in zip(BINS, BIN_KEYS):
        distance[label] = ratio(total[key], total["temporal_sector_reuse_instances"])
        distance[key] = total[key]
    coverage = {
        "workload": args.workload,
        "total_sector_reference_events": total["total_sector_reference_events"],
        "unique_sector_identities": total["unique_sector_identities"],
        "unique_sectors_reused_at_least_once": total["unique_sectors_reused_at_least_once"],
        "one_touch_unique_sectors": total["one_touch_unique_sectors"],
        "one_touch_sector_fraction": summary["one_touch_sector_fraction"],
    }
    write(args.out / "sector_reuse_summary.csv", [summary])
    write(args.out / "sector_reuse_distance.csv", [distance])
    write(args.out / "sector_reuse_coverage.csv", [coverage])
    manifest = {
        "schema_version": SCHEMA,
        "workload": args.workload,
        "framework_commit": args.framework_commit,
        "core_commit": args.core_commit,
        "config_sha256": args.config_sha256,
        "trace_id": args.trace_id,
        "source_log_sha256": digest(args.log),
        "expected_application_slices": args.expected_slices,
        "terminal_record_policy": "select final log-order cumulative application snapshot per slice; prior snapshots must be non-decreasing for every counter",
        "application_records_seen": application_records_seen,
        "application_snapshot_records_superseded": superseded_snapshots,
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit("EPL2SRV1 parser error: %s" % error)
