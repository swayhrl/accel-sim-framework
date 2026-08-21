#!/usr/bin/env python3
"""Aggregate the C2P m/k sweep into paper Figure-13 FP-ratio bins."""

import argparse
import csv
import math
import re
from pathlib import Path


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def read_summary(path):
    values = {}
    if not path.is_file():
        return values
    for line in path.read_text().splitlines():
        if " = " not in line:
            continue
        key, value = line.split(" = ", 1)
        try:
            values[key] = int(value)
        except ValueError:
            pass
    return values


def quantile(values, fraction):
    values = sorted(values)
    if not values:
        return ""
    position = (len(values) - 1) * fraction
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def fp_bin(value):
    # Paper Fig. 13 labels intervals by their upper endpoint: 0.25, 0.50,
    # 0.75, and (only if needed) 1.00.  The raw ratio remains in the CSV.
    return min(1.0, math.ceil(value * 4.0) / 4.0)


def write_csv(path, rows, fields):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep-root", required=True, type=Path)
    parser.add_argument("--paper16-analysis", required=True, type=Path,
                        help="completed analyze_c2p_paper16.py output")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    classification = {
        row["case"]: row
        for row in read_csv(args.paper16_analysis / "paper16_cases.csv")
        if row["group"] != "unknown" and row["baseline_cycles"]
    }
    points, missing = [], []
    point_dirs = sorted(path for path in args.sweep_root.iterdir()
                        if path.is_dir() and re.fullmatch(r"m\d+-k\d+", path.name))
    if not point_dirs:
        raise SystemExit("no m<rows>-k<encodings> sweep directories found")
    for point_dir in point_dirs:
        for case, base in sorted(classification.items()):
            data = read_summary(point_dir / case / "c2p" / "summary.txt")
            needed = ("gpu_tot_sim_cycle", "c2p_snapshot_false_positive",
                      "c2p_snapshot_false_negative", "c2p_snapshot_true_positive",
                      "c2p_snapshot_true_negative")
            if any(key not in data for key in needed):
                missing.append(f"{point_dir.name}/{case}: missing C2P summary")
                continue
            classified = sum(data[key] for key in needed[1:])
            if not classified:
                missing.append(f"{point_dir.name}/{case}: zero classified misses")
                continue
            ratio = data["c2p_snapshot_false_positive"] / classified
            points.append({
                "point": point_dir.name,
                "case": case,
                "group": base["group"],
                "fp_ratio": ratio,
                "fp_bin": fp_bin(ratio),
                "ipc_normalized": int(base["baseline_cycles"]) /
                                  data["gpu_tot_sim_cycle"],
            })

    binned = []
    for group in ("R0S0", "R1S0", "R0S1", "R1S1"):
        for bucket in (0.25, 0.50, 0.75, 1.00):
            values = [row["ipc_normalized"] for row in points
                      if row["group"] == group and row["fp_bin"] == bucket]
            if values:
                binned.append({"group": group, "fp_bin": bucket,
                               "samples": len(values), "ipc_p25": quantile(values, .25),
                               "ipc_median": quantile(values, .50),
                               "ipc_p75": quantile(values, .75)})
    write_csv(args.out_dir / "fp_sweep_points.csv", points,
              ["point", "case", "group", "fp_ratio", "fp_bin", "ipc_normalized"])
    write_csv(args.out_dir / "fp_sweep_binned.csv", binned,
              ["group", "fp_bin", "samples", "ipc_p25", "ipc_median", "ipc_p75"])
    report = ["# C2P Figure-13 FP sweep status", ""]
    if missing:
        report.extend(["## Missing evidence", ""])
        report.extend(f"- {item}" for item in missing)
    else:
        report.append("All canonical classified cases have every m/k point.")
    (args.out_dir / "fp_sweep_status.md").write_text("\n".join(report) + "\n")
    if args.strict and missing:
        raise SystemExit("; ".join(missing))


if __name__ == "__main__":
    main()
