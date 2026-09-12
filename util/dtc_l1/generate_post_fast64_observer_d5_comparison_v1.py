#!/usr/bin/env python3
"""Join accepted Lane-C IO duplicate evidence with validated Lane-D OO rows."""

from __future__ import annotations

import argparse
import csv
import pathlib
import sys


SCHEMA = "POST_FAST64_D5_IO_OO_COMPARISON_V1"
CLASSIFICATION = "POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT"


def rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        result = list(csv.DictReader(handle, delimiter="\t"))
    if not result:
        raise ValueError(f"empty TSV: {path}")
    return result


def ratio(numerator: int, denominator: int, zero: str) -> str:
    return zero if denominator == 0 else f"{numerator / denominator:.12g}"


def write(path: pathlib.Path, data: list[dict[str, str]]) -> None:
    if path.exists():
        raise ValueError(f"refusing to overwrite: {path}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane-c-io", type=pathlib.Path, required=True)
    parser.add_argument("--d5-oo", type=pathlib.Path, required=True)
    parser.add_argument("--accepted-speedup", type=pathlib.Path, required=True)
    parser.add_argument("--output-comparison", type=pathlib.Path, required=True)
    parser.add_argument("--output-traffic", type=pathlib.Path, required=True)
    args = parser.parse_args()
    try:
        io = {row["workload"]: row for row in rows(args.lane_c_io)}
        oo = {row["workload"]: row for row in rows(args.d5_oo)}
        speedup = {
            row["workload"]: row
            for row in rows(args.accepted_speedup)
            if row["workload"] != "GM-FAST12"
        }
        if set(io) != set(oo) or set(io) != set(speedup) or len(io) != 12:
            raise ValueError("IO/OO/speedup workload coverage is not the exact FAST12 set")
        comparison: list[dict[str, str]] = []
        traffic: list[dict[str, str]] = []
        for workload in sorted(io, key=str.casefold):
            i, o, s = io[workload], oo[workload], speedup[workload]
            io_dup, io_lower = int(i["io_duplicate_after_eviction"]), int(i["io_lower_created"])
            oo_dup, oo_lower = int(o["duplicate_after_eviction"]), int(o["lower_created"])
            io_share = ratio(io_dup, io_lower, "NA_ZERO_LOWER_CREATED_DENOMINATOR")
            oo_share = ratio(oo_dup, oo_lower, "NA_ZERO_LOWER_CREATED_DENOMINATOR")
            comparison.append({
                "schema": SCHEMA,
                "classification": CLASSIFICATION,
                "workload": workload,
                "oo_source_row_kind": o["source_row_kind"],
                "io_evidence_status": i["acceptance_status"],
                "oo_evidence_status": "STRICT_TERMINAL_EXACT_PREEXISTING_METRIC_MATCH",
                "io_lower_created": str(io_lower),
                "io_pending_hits": i["io_pending_hits"],
                "io_tag_evictions": i["io_tag_evictions"],
                "io_duplicate_after_eviction": str(io_dup),
                "io_duplicate_share_of_lower": io_share,
                "io_lower_request_payload_inflation": ratio(io_dup, io_lower - io_dup, "NA_ZERO_NON_DUPLICATE_LOWER_DENOMINATOR"),
                "oo_lower_created": str(oo_lower),
                "oo_pending_hits": o["pending_hits"],
                "oo_tag_evictions": o["tag_evictions"],
                "oo_duplicate_after_eviction": str(oo_dup),
                "oo_duplicate_share_of_lower": oo_share,
                "oo_lower_request_payload_inflation": o["duplicate_traffic_inflation"],
                "oo_over_io_duplicate_share_ratio": (
                    "NA_BOTH_IO_AND_OO_ZERO" if io_dup == 0 and oo_dup == 0
                    else ratio(oo_dup * io_lower, oo_lower * io_dup, "NA_ZERO_IO_DUPLICATE_SHARE")
                ),
                "accepted_speedup_io": s["speedup_io"],
                "accepted_speedup_oo": s["speedup_oo"],
                "speedup_source": "ACCEPTED_FAST64_PRIMARY_BASE_IO_OO_CYCLES",
            })
            traffic.extend((
                {
                    "schema": SCHEMA,
                    "classification": CLASSIFICATION,
                    "workload": workload,
                    "mode": "IO",
                    "source_row_kind": "ACCEPTED_LANE_C_IO",
                    "lower_created": str(io_lower),
                    "duplicate_after_eviction": str(io_dup),
                    "duplicate_share_of_lower": io_share,
                    "lower_request_payload_inflation": ratio(io_dup, io_lower - io_dup, "NA_ZERO_NON_DUPLICATE_LOWER_DENOMINATOR"),
                    "duplicate_payload_bytes_128B_lower_request_only": str(io_dup * 128),
                    "payload_scope": "SOURCE_PROVEN_128B_LOWER_REQUEST_PAYLOAD_ONLY_NOT_TOTAL_LINK_OR_DRAM_TRAFFIC",
                },
                {
                    "schema": SCHEMA,
                    "classification": CLASSIFICATION,
                    "workload": workload,
                    "mode": "OO",
                    "source_row_kind": o["source_row_kind"],
                    "lower_created": str(oo_lower),
                    "duplicate_after_eviction": str(oo_dup),
                    "duplicate_share_of_lower": oo_share,
                    "lower_request_payload_inflation": o["duplicate_traffic_inflation"],
                    "duplicate_payload_bytes_128B_lower_request_only": o["duplicate_payload_bytes_128B_lower_request_only"],
                    "payload_scope": "SOURCE_PROVEN_128B_LOWER_REQUEST_PAYLOAD_ONLY_NOT_TOTAL_LINK_OR_DRAM_TRAFFIC",
                },
            ))
        write(args.output_comparison, comparison)
        write(args.output_traffic, traffic)
        print("POST_FAST64_D5_IO_OO_COMPARISON_PASS\tFAST12=12\ttraffic_rows=24")
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"POST_FAST64_D5_IO_OO_COMPARISON_ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
