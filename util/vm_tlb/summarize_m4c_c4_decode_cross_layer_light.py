#!/usr/bin/env python3
"""Low-I/O decode1 generic/paper cross-layer and L2-queue summary."""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def write(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="") as target:
        writer = csv.writer(target, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    cross: defaultdict[tuple[str, str, str, str, str], int] = defaultdict(int)
    queue_sum: defaultdict[tuple[str, str], int] = defaultdict(int)
    queue_hwm: defaultdict[tuple[str, str], int] = defaultdict(int)
    native_count: defaultdict[str, int] = defaultdict(int)
    for profile in ("generic", "paper"):
        directory = args.export_root / f"decode1-{profile}"
        with (directory / "CROSS_LAYER_OUTCOME_MATRIX.tsv").open(newline="") as source:
            for row in csv.DictReader(source, delimiter="\t"):
                if row["scope"] != "KERNEL":
                    continue
                parts = row["payload"].split("\t")
                if row["record_type"] == "m4c_telemetry_cross_l1_l2" and len(parts) == 5:
                    klass, translation, l1, l2, count = parts
                    cross[(profile, klass, translation, l1, l2)] += int(count)
                elif row["record_type"] == "m4c_telemetry_cross_l1" and len(parts) == 4:
                    klass, translation, l1, count = parts
                    cross[(profile, klass, translation, l1, "NOT_OBSERVED")] += int(count)
        with (directory / "L2_QUEUE_PRESSURE.tsv").open(newline="") as source:
            for row in csv.DictReader(source, delimiter="\t"):
                if row["scope"] != "KERNEL":
                    continue
                for field in ("samples", "icnt_to_l2_total", "l2_to_dram_total", "dram_to_l2_total", "l2_to_icnt_total"):
                    queue_sum[(profile, field)] += int(row[field])
                for field in ("icnt_to_l2_hwm", "l2_to_dram_hwm", "dram_to_l2_hwm", "l2_to_icnt_hwm"):
                    queue_hwm[(profile, field)] = max(queue_hwm[(profile, field)], int(row[field]))
        with (directory / "NATIVE_MEMORY_SYSTEM_STATS.tsv").open(newline="") as source:
            for _ in csv.DictReader(source, delimiter="\t"):
                native_count[profile] += 1
    write(output / "DECODE1_CROSS_LAYER_LIGHTWEIGHT.tsv", ["profile", "object_class", "translation_source", "l1d_outcome", "l2_outcome", "count"],
          [[*key, str(value)] for key, value in sorted(cross.items())])
    queue_rows = [[profile, metric, str(value), "sum_over_kernel_records"] for (profile, metric), value in sorted(queue_sum.items())]
    queue_rows += [[profile, metric, str(value), "max_over_kernel_high_water"] for (profile, metric), value in sorted(queue_hwm.items())]
    write(output / "DECODE1_L2_QUEUE_LIGHTWEIGHT.tsv", ["profile", "metric", "value", "aggregation"], queue_rows)
    write(output / "DECODE1_NATIVE_MEMORY_COVERAGE.tsv", ["profile", "native_stat_records"], [[profile, str(native_count[profile])] for profile in ("generic", "paper")])
    print(f"PASS decode_cross_layer_light={output}")


if __name__ == "__main__":
    main()
