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


def read_snapshot_shape(run_dir):
    """Return the final resolved (logical rows, total hashes) pair.

    The runner intentionally appends an m/k overlay after the base C2P config,
    so each option appears twice in the generated file.  The final occurrence
    is the hardware point actually parsed by Accel-Sim.
    """
    path = run_dir / "gpgpusim.config"
    if not path.is_file():
        return None
    values = {}
    prefixes = {
        "-c2p_cache_snapshot_bf_rows_per_bank": "bf_rows_per_bank",
        "-c2p_cache_bf_hashes": "bf_hashes",
    }
    for line in path.read_text().splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0] in prefixes:
            try:
                values[prefixes[fields[0]]] = int(fields[1])
            except ValueError:
                return None
    if set(values) != set(prefixes.values()):
        return None
    # 64 banks each contain 16 tag-mask rows plus the configured BF rows.
    return 64 * (16 + values["bf_rows_per_bank"]), 1 + values["bf_hashes"]


def read_provenance(run_dir):
    path = run_dir / "provenance.txt"
    if not path.is_file():
        return None
    values = {}
    for line in path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    required = ("gpgpusim_commit", "accelsim_commit", "sim_sha256")
    return values if all(values.get(key) for key in required) else None


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


def read_complete_point(run_dir, declared):
    """Return a usable point or the reason this directory cannot supply it."""
    shape = read_snapshot_shape(run_dir)
    if shape != declared:
        return None, f"resolved m/k {shape} != {declared}"
    provenance = read_provenance(run_dir)
    if provenance is None:
        return None, "missing sweep provenance"
    data = read_summary(run_dir / "summary.txt")
    needed = ("gpu_tot_sim_cycle", "c2p_snapshot_false_positive",
              "c2p_snapshot_false_negative", "c2p_snapshot_true_positive",
              "c2p_snapshot_true_negative")
    if any(key not in data for key in needed):
        return None, "missing C2P summary"
    classified = sum(data[key] for key in needed[1:])
    if not classified:
        return None, "zero classified misses"
    return (shape, provenance, data, classified), None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep-root", required=True, type=Path)
    parser.add_argument("--supplemental-sweep-root", action="append", type=Path,
                        default=[],
                        help="fallback roots for independently parallelized points")
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
    # A C2P sweep's executable identity is the linked GPGPU-Sim revision plus
    # the copied Accel-Sim frontend binary.  The Accel-Sim source revision is
    # still emitted per point, but may legitimately differ when only runner,
    # report, or plotting files were committed during a long replay campaign.
    # Requiring it to be byte-identical would reject one unchanged binary
    # family for source-control bookkeeping rather than a simulation change.
    binary_families = set()
    sweep_roots = [args.sweep_root, *args.supplemental_sweep_root]
    point_names = sorted({path.name for root in sweep_roots if root.is_dir()
                          for path in root.iterdir()
                          if path.is_dir() and re.fullmatch(r"m\d+-k\d+", path.name)})
    if not point_names:
        raise SystemExit("no m<rows>-k<encodings> sweep directories found")
    for point_name in point_names:
        declared = tuple(int(value) for value in re.fullmatch(
            r"m(\d+)-k(\d+)", point_name).groups())
        for case, base in sorted(classification.items()):
            selected = None
            reason = "missing C2P summary"
            for root in sweep_roots:
                run_dir = root / point_name / case / "c2p"
                point, candidate_reason = read_complete_point(run_dir, declared)
                if point is not None:
                    selected = (run_dir, *point)
                    break
                if root == args.sweep_root:
                    reason = candidate_reason
            if selected is None:
                missing.append(f"{point_name}/{case}: {reason}")
                continue
            run_dir, shape, provenance, data, classified = selected
            ratio = data["c2p_snapshot_false_positive"] / classified
            binary_family = tuple(provenance[key] for key in
                                  ("gpgpusim_commit", "sim_sha256"))
            binary_families.add(binary_family)
            points.append({
                "point": point_name,
                "case": case,
                "source_run": str(run_dir),
                "group": base["group"],
                "snapshot_rows": shape[0],
                "hash_count": shape[1],
                "gpgpusim_commit": provenance["gpgpusim_commit"],
                "accelsim_commit": provenance["accelsim_commit"],
                "sim_sha256": provenance["sim_sha256"],
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
              ["point", "case", "source_run", "group", "snapshot_rows", "hash_count",
               "gpgpusim_commit", "accelsim_commit", "sim_sha256",
               "fp_ratio", "fp_bin", "ipc_normalized"])
    write_csv(args.out_dir / "fp_sweep_binned.csv", binned,
              ["group", "fp_bin", "samples", "ipc_p25", "ipc_median", "ipc_p75"])
    report = ["# C2P Figure-13 FP sweep status", ""]
    if len(binary_families) > 1:
        missing.append("sweep results use more than one GPGPU-Sim/frontend binary family")
    if missing:
        report.extend(["## Missing evidence", ""])
        report.extend(f"- {item}" for item in missing)
    else:
        report.append("All canonical classified cases have every m/k point, and each "
                      "resolved configuration and executable provenance matches the "
                      "common sweep family.")
    (args.out_dir / "fp_sweep_status.md").write_text("\n".join(report) + "\n")
    if args.strict and missing:
        raise SystemExit("; ".join(missing))


if __name__ == "__main__":
    main()
