#!/usr/bin/env python3
"""Fail-closed parser for the additive EPL2M0AV1 observability stream."""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

SCHEMA = "EPL2M0AV1"
REQUIRED = {
    "scope", "interval", "slice", "kernel_uid", "start_cycle",
    "completion_cycle", "resident_samples",
    "m0_resident_payload_occupied_sum", "m0_resident_payload_free_sum",
    "m0_resident_payload_occupied_avg", "m0_resident_payload_free_avg",
    "m0_frontend_head_observed_cycles", "m0_frontend_head_any_blocked_cycles",
    "m0_frontend_head_blocked_cycles_tag_way",
    "m0_frontend_head_blocked_cycles_wad_full",
    "m0_frontend_head_blocked_cycles_wad_hazard",
    "m0_frontend_head_blocked_cycles_line_mshr",
    "m0_frontend_head_blocked_cycles_descriptor",
    "m0_frontend_head_blocked_cycles_per_address",
    "m0_frontend_head_blocked_cycles_missq",
    "m0_frontend_head_blocked_cycles_payload_service",
    "m0_frontend_head_blocked_cycles_payload_capacity",
    "m0_frontend_head_blocked_cycles_lowerq",
    "m0_frontend_head_blocked_cycles_responseq",
    "m0_useful_frontend_admit", "m0_useful_response_enqueue",
}


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def parse(line):
    parts = line.rstrip().split("|")
    if not parts or parts[0] != SCHEMA:
        return None
    row = {}
    for item in parts[1:]:
        if "=" not in item:
            raise ValueError("malformed EPL2M0AV1 field: " + item)
        key, raw = item.split("=", 1)
        if key in row:
            raise ValueError("duplicate EPL2M0AV1 field: " + key)
        try:
            row[key] = int(raw)
        except ValueError:
            row[key] = raw
    missing = REQUIRED - set(row)
    if missing:
        raise ValueError("missing EPL2M0AV1 fields: " + ",".join(sorted(missing)))
    if row["scope"] not in ("application", "kernel", "window"):
        raise ValueError("unknown M0a scope: " + str(row["scope"]))
    if row["scope"] == "window" and row["interval"] != "5000_cycle":
        raise ValueError("M0a window has non-5K interval")
    if row["m0_frontend_head_any_blocked_cycles"] > row["m0_frontend_head_observed_cycles"]:
        raise ValueError("M0a any-blocked exceeds observed")
    for key in REQUIRED - {"scope", "interval"}:
        if not isinstance(row[key], int):
            raise ValueError("non-integer M0a field: " + key)
    row["schema_version"] = SCHEMA
    return row


def write_csv(path, rows):
    keys = sorted({key for row in rows for key in row})
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--framework-commit", default="NA")
    parser.add_argument("--core-commit", default="NA")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rows = [row for line in args.log.read_text(encoding="utf-8", errors="replace").splitlines()
            if (row := parse(line)) is not None]
    if not rows:
        raise ValueError("M0a enabled but no EPL2M0AV1 records were emitted")
    application = {}
    kernels, windows = [], []
    for row in rows:
        if row["scope"] == "application":
            prior = application.get(row["slice"])
            if prior is None or row["completion_cycle"] >= prior["completion_cycle"]:
                application[row["slice"]] = row
        elif row["scope"] == "kernel":
            kernels.append(row)
        else:
            windows.append(row)
    application_rows = [application[key] for key in sorted(application)]
    if len(application_rows) != 64:
        raise ValueError("expected exactly 64 terminal M0a application slices, found %d" % len(application_rows))
    groups = defaultdict(list)
    for row in windows:
        groups[(row["start_cycle"], row["completion_cycle"])].append(row)
    for key, group in groups.items():
        if len(group) != 64 or len({row["slice"] for row in group}) != 64:
            raise ValueError("incomplete M0a 5K physical-slice window %s" % (key,))
    if not groups:
        raise ValueError("no complete M0a 5K window groups")
    write_csv(args.out / "m0a_application.csv", application_rows)
    write_csv(args.out / "m0a_kernel.csv", kernels)
    write_csv(args.out / "m0a_window.csv", windows)
    summary = {
        "schema_version": SCHEMA, "application_slice_count": len(application_rows),
        "kernel_record_count": len(kernels), "window_record_count": len(windows),
        "complete_5k_window_groups": len(groups),
    }
    for field in sorted(REQUIRED):
        if field.startswith("m0_"):
            summary[field] = sum(row[field] for row in application_rows)
    write_csv(args.out / "m0a_summary.csv", [summary])
    (args.out / "m0a_manifest.json").write_text(json.dumps({
        "schema_version": SCHEMA, "framework_commit": args.framework_commit,
        "core_commit": args.core_commit, "source_log_sha256": digest(args.log),
        "application_slice_count": len(application_rows),
        "complete_5k_window_groups": len(groups),
    }, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit("EPL2M0AV1 parser error: %s" % error)
