#!/usr/bin/env python3
"""Aggregate M1F stable-selection distribution without reading any trace."""
from __future__ import annotations

import argparse
import bisect
import csv
import gzip
import hashlib
import json
import math
import re
import statistics
import struct
from itertools import zip_longest
from pathlib import Path


SIDECAR_SHA = "6c60839714d136b9f6f596218588e658e245e0b7cc6f8e8550cce8d683ce13c6"
HASH_VERSION = "C16_M1F_STABLE_ADMISSION_HASH_V1"
SEED_HEX = "0x6a09e667f3bcc908"
THRESHOLD_HEX = "0x0484baf3b723b966"
FAMILY_LINES = 7_426_048
REGION_LINES = 265_216
GLOBAL_QUOTA_LINES = 131_072
SUBPARTITIONS = 16
SETS = 2048
CLASSES = 28
U64 = struct.Struct("<Q")


class AnalysisError(RuntimeError):
    pass


def need(value: bool, message: str) -> None:
    if not value:
        raise AnalysisError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def percentile(sorted_values: list[int], fraction: float) -> int:
    if not sorted_values:
        return 0
    return sorted_values[min(len(sorted_values) - 1,
                             int((len(sorted_values) - 1) * fraction))]


def gini(values: list[int]) -> float:
    ordered = sorted(values)
    total = sum(ordered)
    if not ordered or total == 0:
        return 0.0
    weighted = sum((index + 1) * value for index, value in enumerate(ordered))
    return (2 * weighted) / (len(ordered) * total) - (len(ordered) + 1) / len(ordered)


def distribution(values: list[int]) -> dict:
    need(bool(values), "empty distribution")
    ordered = sorted(values)
    mean = statistics.mean(values)
    stdev = statistics.pstdev(values)
    return {
        "count": len(values),
        "sum": sum(values),
        "min": ordered[0],
        "mean": mean,
        "median": statistics.median(values),
        "p90": percentile(ordered, .90),
        "p99": percentile(ordered, .99),
        "max": ordered[-1],
        "standard_deviation": stdev,
        "coefficient_of_variation": stdev / mean if mean else 0.0,
        "max_over_mean": ordered[-1] / mean if mean else 0.0,
        "zero_fraction": sum(value == 0 for value in values) / len(values),
        "gini": gini(values),
    }


def read_sidecar(path: Path) -> tuple[list[dict], list[int]]:
    need(sha256(path) == SIDECAR_SHA, "sidecar SHA drift")
    regions = []
    with path.open(encoding="utf-8") as stream:
        need(stream.readline().rstrip("\n") ==
             "ORACLE_ELASTIC_QWEIGHT_RESIDENCY_V1\t1\tMODELED_L2_GET_ADDR",
             "sidecar header drift")
        for raw in stream:
            if not raw.strip():
                continue
            begin, end, name, target_class = raw.rstrip("\n").split("\t")
            regions.append({"begin": int(begin, 0), "end": int(end, 0),
                            "name": name, "target_class": int(target_class)})
    need(len(regions) == CLASSES, "requires exact 28 regions")
    need({row["target_class"] for row in regions} == set(range(1, CLASSES + 1)),
         "target class identity drift")
    need(regions == sorted(regions, key=lambda row: row["begin"]),
         "regions not address sorted")
    for row in regions:
        need(row["end"] - row["begin"] == REGION_LINES * 128,
             "region span drift")
    return regions, [row["begin"] for row in regions]


def read_u64(path: Path):
    previous = None
    with path.open("rb") as stream:
        while block := stream.read(1 << 20):
            need(len(block) % 8 == 0, "selected line file truncated")
            for (value,) in struct.iter_unpack("<Q", block):
                need(previous is None or value > previous,
                     "selected lines not strictly sorted")
                need(value % 128 == 0, "selected line not 128B aligned")
                previous = value
                yield value


def parse_toy(path: Path) -> dict:
    match = re.search(r"^M1F_TOY_SURVIVAL_PASS\s+(.+)$",
                      path.read_text(encoding="utf-8"), re.MULTILINE)
    need(match is not None, "toy result absent from Core test log")
    fields = {}
    for item in match.group(1).split():
        key, value = item.split("=", 1)
        fields[key] = int(value)
    required = {
        "m1_occupancy", "class_quota_occupancy", "m1f_occupancy",
        "m1_next_round_hits", "class_quota_next_round_hits",
        "m1f_next_round_hits", "m1_old_address_survived",
        "class_quota_old_address_survived", "m1f_old_address_survived",
        "old_address_class", "old_address_line",
    }
    need(required <= set(fields), "toy result field drift")
    return {
        "schema": "C16_E1_M1F_TOY_SURVIVAL_COMPARISON_V1",
        "status": "PASS",
        "claim_boundary": "CPU_ONLY_PROTECTED_POOL_REFERENCE_NOT_FULL_CACHE_OR_TIMING",
        "workload": "two classes, eight lines/class, two sequential rounds",
        "protected_capacity_lines": 4,
        "policies": {
            "M1_GLOBAL_FULL_ADMISSION": {
                "final_occupancy": fields["m1_occupancy"],
                "old_address_survived_after_round_one":
                    bool(fields["m1_old_address_survived"]),
                "next_round_old_address_hits": fields["m1_next_round_hits"],
            },
            "EQUAL_CLASS_CAPACITY_CLASS_INTERNAL_LRU": {
                "final_occupancy": fields["class_quota_occupancy"],
                "old_address_survived_after_round_one":
                    bool(fields["class_quota_old_address_survived"]),
                "next_round_old_address_hits": fields["class_quota_next_round_hits"],
            },
            "M1F_STABLE_ADDRESS_SUBSET": {
                "final_occupancy": fields["m1f_occupancy"],
                "old_address_survived_after_round_one":
                    bool(fields["m1f_old_address_survived"]),
                "next_round_old_address_hits": fields["m1f_next_round_hits"],
            },
        },
        "tracked_old_address": {"target_class": fields["old_address_class"],
                                "region_line_index": fields["old_address_line"]},
        "interpretation": "Equal occupancy does not imply old-address survival; the stable subset survives in this toy. This does not predict C16 L2 behavior.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sidecar", type=Path, required=True)
    parser.add_argument("--selector-summary", type=Path, required=True)
    parser.add_argument("--selected-lines", type=Path, required=True)
    parser.add_argument("--mapped-lines", type=Path, required=True)
    parser.add_argument("--core-test-log", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    need(not args.output_dir.exists(), "output directory must be fresh")
    regions, starts = read_sidecar(args.sidecar)
    selector = json.loads(args.selector_summary.read_text(encoding="utf-8"))
    need(selector.get("status") == "PASS", "selector summary not PASS")
    need(selector.get("hash_version") == HASH_VERSION, "hash version drift")
    need(selector.get("seed_hex") == SEED_HEX, "seed drift")
    need(selector.get("threshold_hex") == THRESHOLD_HEX, "threshold drift")
    need(selector.get("total_lines") == FAMILY_LINES, "family line closure failed")

    class_set = [[0] * (SUBPARTITIONS * SETS) for _ in range(CLASSES)]
    class_sp = [[0] * SUBPARTITIONS for _ in range(CLASSES)]
    total_set = [0] * (SUBPARTITIONS * SETS)
    total_sp = [0] * SUBPARTITIONS
    selected_count = 0
    with args.mapped_lines.open(newline="", encoding="utf-8") as stream:
        mapped = csv.DictReader(stream, delimiter="\t")
        for address, row in zip_longest(read_u64(args.selected_lines), mapped):
            need(address is not None and row is not None,
                 "selected/mapped line count mismatch")
            mapped_address = int(row["line_address_hex"], 0)
            need(mapped_address == address, "mapper address order drift")
            sp, set_index = int(row["subpartition"]), int(row["set_index"])
            need(0 <= sp < SUBPARTITIONS and 0 <= set_index < SETS,
                 "mapper coordinate out of range")
            region_index = bisect.bisect_right(starts, address) - 1
            need(region_index >= 0 and address < regions[region_index]["end"],
                 "selected address outside target regions")
            target_class = regions[region_index]["target_class"]
            slot = sp * SETS + set_index
            class_set[target_class - 1][slot] += 1
            class_sp[target_class - 1][sp] += 1
            total_set[slot] += 1
            total_sp[sp] += 1
            selected_count += 1
    need(selected_count == selector["selected_lines"], "selector total drift")
    selector_by_class = {int(row["target_class"]): int(row["selected_lines"])
                         for row in selector["classes"]}
    need(len(selector_by_class) == CLASSES, "selector class rows drift")

    expected_class = GLOBAL_QUOTA_LINES / CLASSES
    expected_class_sp = GLOBAL_QUOTA_LINES / (CLASSES * SUBPARTITIONS)
    class_sp_cells = [value for row in class_sp for value in row]
    class_set_cells = [value for row in class_set for value in row]
    class_rows = []
    for target_class in range(1, CLASSES + 1):
        count = sum(class_sp[target_class - 1])
        need(count == selector_by_class[target_class], "class count drift")
        class_rows.append({
            "target_class": target_class,
            "layer_index": target_class - 1,
            "selected_lines": count,
            "expected_lines": expected_class,
            "deviation_lines": count - expected_class,
            "relative_deviation": (count - expected_class) / expected_class,
            "selected_fraction_of_region": count / REGION_LINES,
            "subpartition_distribution": distribution(class_sp[target_class - 1]),
            "set_distribution": distribution(class_set[target_class - 1]),
        })

    args.output_dir.mkdir(parents=True)
    result = {
        "schema": "C16_E1_M1F_STATIC_SELECTION_DISTRIBUTION_V1",
        "status": "PASS",
        "claim_boundary": "STATIC_SELECTION_ELIGIBILITY_NOT_OCCUPANCY_ADMISSION_OR_SURVIVAL",
        "hash_contract": {
            "version": HASH_VERSION,
            "seed_hex": SEED_HEX,
            "threshold_hex": THRESHOLD_HEX,
            "eligible_fraction": GLOBAL_QUOTA_LINES / FAMILY_LINES,
            "key": "target_class || region_relative_128B_line_index",
        },
        "geometry": {"classes": CLASSES, "subpartitions": SUBPARTITIONS,
                     "sets_per_subpartition": SETS, "line_bytes": 128},
        "quota": {"global_lines": GLOBAL_QUOTA_LINES,
                  "per_subpartition_lines": GLOBAL_QUOTA_LINES // SUBPARTITIONS},
        "selected_lines": selected_count,
        "selected_minus_global_quota_lines": selected_count - GLOBAL_QUOTA_LINES,
        "selected_relative_to_global_quota": selected_count / GLOBAL_QUOTA_LINES,
        "class_selected_distribution": distribution([row["selected_lines"]
                                                       for row in class_rows]),
        "class_subpartition_cell_distribution": distribution(class_sp_cells),
        "class_set_cell_distribution": distribution(class_set_cells),
        "subpartition_total_distribution": distribution(total_sp),
        "subpartitions_detail": [
            {"subpartition": sp, "selected_lines": count,
             "quota_lines": GLOBAL_QUOTA_LINES // SUBPARTITIONS,
             "selected_minus_quota_lines":
                 count - GLOBAL_QUOTA_LINES // SUBPARTITIONS}
            for sp, count in enumerate(total_sp)
        ],
        "set_total_distribution": distribution(total_set),
        "sets_above_even_four_line_reference": sum(value > 4 for value in total_set),
        "sets_below_even_four_line_reference": sum(value < 4 for value in total_set),
        "sets_at_even_four_line_reference": sum(value == 4 for value in total_set),
        "sets_at_or_above_16_way_associativity": sum(value >= 16 for value in total_set),
        "expected_lines_per_class": expected_class,
        "expected_lines_per_class_subpartition": expected_class_sp,
        "expected_lines_per_global_set": GLOBAL_QUOTA_LINES / (SUBPARTITIONS * SETS),
        "expected_lines_per_class_set": GLOBAL_QUOTA_LINES /
            (CLASSES * SUBPARTITIONS * SETS),
        "classes_detail": class_rows,
        "hard_admission_note": "The static selector may over- or undershoot the requested quota. Existing M1 hard admission remains authoritative; no quota is changed here.",
        "provenance": {
            "sidecar_path": str(args.sidecar.resolve()),
            "sidecar_sha256": sha256(args.sidecar),
            "selector_summary_path": str(args.selector_summary.resolve()),
            "selector_summary_sha256": sha256(args.selector_summary),
            "selected_lines_path": str(args.selected_lines.resolve()),
            "selected_lines_sha256": sha256(args.selected_lines),
            "mapped_lines_path": str(args.mapped_lines.resolve()),
            "mapped_lines_sha256": sha256(args.mapped_lines),
        },
    }
    dump(args.output_dir / "M1F_STATIC_SELECTION_DISTRIBUTION.json", result)
    dump(args.output_dir / "M1F_TOY_SURVIVAL_COMPARISON.json",
         parse_toy(args.core_test_log))

    with (args.output_dir / "M1F_CLASS_DISTRIBUTION.tsv").open(
            "w", newline="", encoding="utf-8") as stream:
        fields = ["target_class", "layer_index", "selected_lines",
                  "expected_lines", "deviation_lines", "relative_deviation",
                  "selected_fraction_of_region"]
        writer = csv.DictWriter(stream, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in class_rows:
            writer.writerow({field: row[field] for field in fields})

    with (args.output_dir / "M1F_CLASS_SUBPARTITION_DISTRIBUTION.tsv").open(
            "w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(["target_class", "layer_index", "subpartition",
                         "selected_lines", "expected_lines", "deviation_lines"])
        for target_class in range(1, CLASSES + 1):
            for sp, count in enumerate(class_sp[target_class - 1]):
                writer.writerow([target_class, target_class - 1, sp, count,
                                 expected_class_sp, count - expected_class_sp])

    with gzip.open(args.output_dir / "M1F_CLASS_SET_SELECTED_COUNTS.tsv.gz",
                   "wt", newline="", encoding="utf-8", compresslevel=9) as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(["target_class", "layer_index", "subpartition",
                         "set_index", "selected_lines"])
        for target_class in range(1, CLASSES + 1):
            for slot, count in enumerate(class_set[target_class - 1]):
                writer.writerow([target_class, target_class - 1,
                                 slot // SETS, slot % SETS, count])

    outputs = sorted(path for path in args.output_dir.iterdir()
                     if path.name != "ANALYSIS_SHA256SUMS")
    with (args.output_dir / "ANALYSIS_SHA256SUMS").open("w", encoding="utf-8") as stream:
        for path in outputs:
            stream.write(f"{sha256(path)}  {path.name}\n")
    print(json.dumps({"status": "PASS", "selected_lines": selected_count,
                      "quota_lines": GLOBAL_QUOTA_LINES,
                      "output_dir": str(args.output_dir)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
