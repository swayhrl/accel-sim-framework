#!/usr/bin/env python3
"""Generate the all-distinct-function, pre-outcome Llama S0 Route-B V2 batch."""
from __future__ import annotations

import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--v1", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    catalog_bytes = args.catalog.read_bytes()
    catalog_sha = sha256(catalog_bytes).hexdigest()
    rows = [row for row in csv.DictReader(catalog_bytes.decode().splitlines(), delimiter="\t") if row["phase"] in {"PREFILL", "DECODE"}]
    v1 = json.loads(args.v1.read_text())
    v1_ids = {row["exact_full_function"]: row["request_id"] for row in v1["requests"]}
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["kernel_name"], []).append(row)
    requests = []
    for function, members in grouped.items():
        by_phase: dict[str, dict[str, object]] = {}
        for phase in sorted({row["phase"] for row in members}):
            phase_rows = [row for row in members if row["phase"] == phase]
            geometry_groups: dict[tuple[str, str, str, str], dict[str, int]] = {}
            for row in phase_rows:
                key = (row["grid"], row["block"], row["shape_key"], row["dtype_key"])
                aggregate = geometry_groups.setdefault(key, {"launch_count": 0, "duration_ns": 0})
                aggregate["launch_count"] += 1
                aggregate["duration_ns"] += int(row["duration_ns"])
            geometries = sorted(geometry_groups.items())
            by_phase[phase] = {
                "launch_count": len(phase_rows),
                "phase_duration_ns": sum(int(row["duration_ns"]) for row in phase_rows),
                "geometries": [
                    {"grid": grid, "block": block, "shape_key": shape, "dtype_key": dtype,
                     "launch_count": aggregate["launch_count"], "duration_ns": aggregate["duration_ns"]}
                    for (grid, block, shape, dtype), aggregate in geometries
                ],
            }
        total = sum(int(row["duration_ns"]) for row in members)
        request_id = "LLAMA_S0_G1_V2_" + sha256(function.encode()).hexdigest()[:16]
        requests.append({
            "request_id": request_id,
            "exact_full_function": function,
            "known_mangled_name": "MAP_DISCOVERY_REQUIRED",
            "code_object_sha256": "MAP_DISCOVERY_REQUIRED",
            "code_object_identity_note": "The published S0 G1 catalog does not carry a code-object SHA. GPU map discovery must resolve it; no code-object identity is inferred.",
            "phase_observations": by_phase,
            "all_phase_duration_ns": total,
            "selection_reason": "V2_ALL_UNMAPPED_DISTINCT_EXACT_FUNCTIONS",
            "source_catalog_sha": catalog_sha,
            "supersedes_v1_request_id": v1_ids.get(function),
        })
    requests.sort(key=lambda row: (-row["all_phase_duration_ns"], row["exact_full_function"]))
    output = {
        "schema_version": "C16_ROUTE_B_MAP_REQUESTS_V2",
        "status": "FROZEN_PRE_OUTCOME_ALL_DISTINCT_FUNCTION_MAP_BATCH",
        "scope": "all unmapped distinct catalog full functions across PREFILL and DECODE; deduplication key is exact full function + discovered code-object SHA",
        "source_catalog_sha256": catalog_sha,
        "catalog_source_commit": "8d1bd2a3fff5b8fe079d9e738740eafa50720b43",
        "map_result_status_at_freeze": "NO_LANE_A_MAP_SUMMARY_PUBLISHED",
        "forbidden_selection_inputs": ["GPU_VA", "address locality", "cache outcome", "TLB outcome", "Route-B address outcome"],
        "requests": requests,
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
