#!/usr/bin/env python3
"""Summarize provenance-gated Decoupled-L2 capacity sensitivity points.

Each point is a three-arm ``optimized_bank_observability.csv`` from the bank
diagnosis runner.  The default Decoupled-L2 arm and the optimized arm are the
only pair used for the capacity delta; the baseline arm remains recorded in
the sibling three-arm summary.  Do not use this tool to merge unrelated
workloads or rebuilt binaries.
"""

import argparse
import csv
import sys
from pathlib import Path


DEFAULT_LOWER_READ_ENTRIES = 32


def fail(message):
    raise RuntimeError(message)


def read_kv(path):
    if not path.is_file():
        fail("missing file: %s" % path)
    result = {}
    for line in path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key] = value
    return result


def lower_read_entries(run_dir):
    config = Path(run_dir) / "gpgpusim.config"
    entries = DEFAULT_LOWER_READ_ENTRIES
    for line in config.read_text().splitlines():
        fields = line.split()
        if len(fields) == 2 and fields[0] == "-gpgpu_decoupled_l2_lower_read_entries":
            try:
                entries = int(fields[1])
            except ValueError as error:
                raise RuntimeError("bad lower-read capacity in %s" % config) from error
    return entries


def as_int(row, key):
    try:
        return int(row[key])
    except (KeyError, ValueError) as error:
        raise RuntimeError("missing integer %s" % key) from error


def as_float(row, key):
    try:
        return float(row[key])
    except (KeyError, ValueError) as error:
        raise RuntimeError("missing number %s" % key) from error


def value_or_na(value):
    return "n/a" if value in (None, "") else str(value)


def read_point(expected_entries, csv_path):
    with csv_path.open(newline="") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != 1:
        fail("%s must contain exactly one workload row" % csv_path)
    row = rows[0]
    default_dir = Path(row["default_dir"])
    optimized_dir = Path(row["optimized_dir"])
    if lower_read_entries(default_dir) != DEFAULT_LOWER_READ_ENTRIES:
        fail("%s default arm is not lower-read=%d" %
             (default_dir, DEFAULT_LOWER_READ_ENTRIES))
    actual_entries = lower_read_entries(optimized_dir)
    if actual_entries != expected_entries:
        fail("%s requested lower-read=%d but config has %d" %
             (csv_path, expected_entries, actual_entries))

    default_meta = read_kv(default_dir / "simulator_provenance.txt")
    optimized_meta = read_kv(optimized_dir / "simulator_provenance.txt")
    for key in ("sim_bin_sha256", "gpgpusim_source_commit",
                "gpgpusim_source_dirty", "gpgpusim_source_diff_sha256",
                "trace_kernelslist_sha256"):
        if default_meta.get(key) != optimized_meta.get(key):
            fail("%s default/optimized provenance mismatches %s" %
                 (csv_path, key))
    if default_meta.get("backend") != "decoupled" or \
       optimized_meta.get("backend") != "decoupled":
        fail("%s does not compare two Decoupled-L2 arms" % csv_path)

    result = {
        "case": row["case"],
        "entries": actual_entries,
        "trace_kernelslist_sha256": default_meta.get("trace_kernelslist_sha256"),
        "sim_bin_sha256": default_meta.get("sim_bin_sha256"),
        "gpgpusim_source_commit": default_meta.get("gpgpusim_source_commit"),
        "gpgpusim_source_dirty": default_meta.get("gpgpusim_source_dirty"),
        "gpgpusim_source_diff_sha256": default_meta.get("gpgpusim_source_diff_sha256"),
        "default_cycles": as_int(row, "default_cycles"),
        "capacity_cycles": as_int(row, "optimized_cycles"),
        "default_ipc": as_float(row, "default_ipc"),
        "capacity_ipc": as_float(row, "optimized_ipc"),
        "default_fill_max": as_int(row, "default_fill_max"),
        "capacity_fill_max": as_int(row, "optimized_fill_max"),
        "default_read_credit_stall": as_int(row, "default_read_credit_stall"),
        "capacity_read_credit_stall": as_int(row, "optimized_read_credit_stall"),
        "default_wbq_max": as_int(row, "default_wbq_max"),
        "capacity_wbq_max": as_int(row, "optimized_wbq_max"),
        "default_wbq_stall": row.get("default_wbq_stall"),
        "capacity_wbq_stall": row.get("optimized_wbq_stall"),
        "default_dir": str(default_dir),
        "capacity_dir": str(optimized_dir),
    }
    result["speedup"] = result["default_cycles"] / result["capacity_cycles"]
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--point", action="append", nargs=2,
                        metavar=("ENTRIES", "OPTIMIZED_CSV"), required=True)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--markdown", required=True)
    args = parser.parse_args()

    points = []
    for entries_text, path_text in args.point:
        try:
            entries = int(entries_text)
        except ValueError as error:
            raise RuntimeError("capacity must be an integer: %s" % entries_text) from error
        if entries <= DEFAULT_LOWER_READ_ENTRIES:
            fail("capacity point must exceed the default %d" % DEFAULT_LOWER_READ_ENTRIES)
        points.append(read_point(entries, Path(path_text)))
    points.sort(key=lambda row: row["entries"])
    if len({row["entries"] for row in points}) != len(points):
        fail("duplicate capacity point")
    if len({row["case"] for row in points}) != 1:
        fail("capacity points mix workloads")
    for key in ("trace_kernelslist_sha256", "sim_bin_sha256",
                "gpgpusim_source_commit", "gpgpusim_source_dirty",
                "gpgpusim_source_diff_sha256"):
        if len({row[key] for row in points}) != 1:
            fail("capacity points mismatch %s" % key)

    fields = ["case", "entries", "default_cycles", "capacity_cycles",
              "default_ipc", "capacity_ipc", "speedup", "default_fill_max",
              "capacity_fill_max", "default_read_credit_stall",
              "capacity_read_credit_stall", "default_wbq_max",
              "capacity_wbq_max", "default_wbq_stall", "capacity_wbq_stall",
              "trace_kernelslist_sha256", "sim_bin_sha256",
              "gpgpusim_source_commit", "gpgpusim_source_dirty",
              "gpgpusim_source_diff_sha256", "default_dir", "capacity_dir"]
    with Path(args.csv).open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(points)
    with Path(args.markdown).open("w") as output:
        output.write("# Decoupled-L2 lower-read/fill capacity sensitivity\\n\\n")
        output.write("Every point compares the default `lower_read_entries=32` "
                     "Decoupled-L2 arm with one capacity-only Decoupled-L2 arm. "
                     "Trace, binary, source-tree identity, and workload must match "
                     "across all points.\\n\\n")
        output.write("| Capacity per slice | Default / capacity IPC | Default / capacity cycles | "
                     "Speedup | Fill peak | Read-credit stalls | WBQ peak | WBQ stalls |\\n")
        output.write("|---:|---:|---:|---:|---:|---:|---:|---:|\\n")
        for row in points:
            output.write("| {entries} | {default_ipc:.4f} / {capacity_ipc:.4f} | "
                         "{default_cycles} / {capacity_cycles} | {speedup:.4f}x | "
                         "{default_fill_max} / {capacity_fill_max} | "
                         "{default_read_credit_stall} / {capacity_read_credit_stall} | "
                         "{default_wbq_max} / {capacity_wbq_max} | {default_wbq} / {capacity_wbq} |\\n".format(
                             default_wbq=value_or_na(row["default_wbq_stall"]),
                             capacity_wbq=value_or_na(row["capacity_wbq_stall"]),
                             **row))


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print("error: %s" % error, file=sys.stderr)
        sys.exit(1)
