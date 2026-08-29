#!/usr/bin/env python3
"""Create the analysis-ready EP-L2 Target Baseline table and review archive."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import tarfile

from run_target_baseline import ROSTER, VARIANTS


ROOT = Path(__file__).resolve().parents[2]


def integer(row: dict[str, str], field: str) -> int:
    try:
        return int(row.get(field, "0"))
    except ValueError:
        return 0


def weighted(rows: list[dict[str, str]], field: str) -> int:
    total = sum(integer(row, "samples") for row in rows)
    return sum(integer(row, field) * integer(row, "samples") for row in rows) // total if total else 0


def maximum(rows: list[dict[str, str]], field: str) -> int:
    return max((integer(row, field) for row in rows), default=0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "docs/ep_l2/target_baseline_results")
    parser.add_argument("--package", action="store_true")
    args = parser.parse_args()
    expected = [(name, variant) for name, _ in ROSTER for variant, _ in VARIANTS]
    statuses, slices = {}, {}
    for name, variant in expected:
        directory = args.out / variant / name
        try:
            status = json.loads((directory / "run_status.json").read_text())
            if status.get("status") != "COMPLETE_VALID":
                raise ValueError(status.get("status"))
            statuses[name, variant] = status
            with (directory / "target_slice.csv").open(newline="") as source:
                slices[name, variant] = list(csv.DictReader(source))
        except (OSError, json.JSONDecodeError, ValueError) as error:
            raise SystemExit("incomplete or invalid Target Baseline run %s/%s: %s" %
                             (variant, name, error))
    fields = [
        "workload", "variant", "cycles", "speed_vs_legacy", "l1_block_events",
        "tag_set_block_events", "line_mshr_avg", "line_mshr_p95_max", "line_mshr_max",
        "line_mshr_full_events", "descriptor_avg", "descriptor_p95_max", "descriptor_max",
        "descriptor_pool_full_events", "descriptor_per_address_cap_events", "wad_avg",
        "wad_p95_max", "wad_max", "wad_full_events", "wad_hazard_wait_events",
        "resident_payload_avg", "resident_payload_p95_max", "resident_payload_max",
        "resident_valid_events", "resident_pending_events", "bypass_payload_avg",
        "payload_alloc_block_events", "bank_requests", "bank_grants", "bank_conflicts",
        "bank_conflict_rate", "bank_wait_cycles", "missq_avg", "missq_max", "lowerq_avg",
        "lowerq_max", "l2_to_dram_events", "dram_to_l2_events", "scheduler_block_events",
        "dram_bandwidth_util", "telemetry_note",
    ]
    rows = []
    unavailable = "NOT_EMITTED_BY_EPL2B0V1"
    for name, variant in expected:
        records = slices[name, variant]
        cycle = int(statuses[name, variant]["terminal_gpu_tot_sim_cycle"])
        legacy_cycle = int(statuses[name, "B0-Legacy"]["terminal_gpu_tot_sim_cycle"])
        bank_requests = sum(integer(row, "bank_requests") for row in records)
        bank_conflicts = sum(integer(row, "bank_conflicts") for row in records)
        rows.append({
            "workload": name, "variant": variant, "cycles": cycle,
            "speed_vs_legacy": "%.6f" % (legacy_cycle / cycle),
            "l1_block_events": sum(integer(row, "block_l1") for row in records),
            "tag_set_block_events": unavailable,
            "line_mshr_avg": weighted(records, "line_mshr_avg"),
            "line_mshr_p95_max": maximum(records, "line_mshr_p95"),
            "line_mshr_max": maximum(records, "line_mshr_max"),
            "line_mshr_full_events": unavailable,
            "descriptor_avg": weighted(records, "descriptor_avg"),
            "descriptor_p95_max": maximum(records, "descriptor_p95"),
            "descriptor_max": maximum(records, "descriptor_max"),
            "descriptor_pool_full_events": sum(integer(row, "block_descriptor") for row in records),
            "descriptor_per_address_cap_events": unavailable,
            "wad_avg": weighted(records, "wad_avg"), "wad_p95_max": maximum(records, "wad_p95"),
            "wad_max": maximum(records, "wad_max"), "wad_full_events": sum(integer(row, "block_wad") for row in records),
            "wad_hazard_wait_events": unavailable,
            "resident_payload_avg": weighted(records, "resident_payload_avg"),
            "resident_payload_p95_max": maximum(records, "resident_payload_p95"),
            "resident_payload_max": maximum(records, "resident_payload_max"),
            "resident_valid_events": unavailable, "resident_pending_events": unavailable,
            "bypass_payload_avg": weighted(records, "bypass_payload_avg"),
            "payload_alloc_block_events": sum(integer(row, "block_payload") for row in records),
            "bank_requests": bank_requests, "bank_grants": sum(integer(row, "bank_grants") for row in records),
            "bank_conflicts": bank_conflicts,
            "bank_conflict_rate": "%.6f" % (bank_conflicts / bank_requests) if bank_requests else "0.000000",
            "bank_wait_cycles": unavailable, "missq_avg": weighted(records, "missq_avg"),
            "missq_max": maximum(records, "missq_max"), "lowerq_avg": weighted(records, "lowerq_avg"),
            "lowerq_max": maximum(records, "lowerq_max"), "l2_to_dram_events": unavailable,
            "dram_to_l2_events": unavailable,
            "scheduler_block_events": sum(integer(row, "block_lower") for row in records),
            "dram_bandwidth_util": unavailable,
            "telemetry_note": "EPL2B0V1 emitted fields; NOT_EMITTED values are intentionally not inferred",
        })
    table = args.out / "target_baseline_comparison.csv"
    with table.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    summary = {"runs": len(rows), "frequency_mhz": 850, "variants": [v[0] for v in VARIANTS],
               "workloads": [name for name, _ in ROSTER], "comparison": table.name,
               "all_runs_complete_valid": True,
               "telemetry_contract": "NOT_EMITTED_BY_EPL2B0V1 values were not reconstructed from unrelated counters"}
    (args.out / "target_baseline_analysis_manifest.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    if args.package:
        pack_dir = ROOT / "docs/ep_l2/review_packs"
        pack_dir.mkdir(parents=True, exist_ok=True)
        archive = pack_dir / "EP_L2_TARGET_BASELINE_850MHZ_r1.tar.gz"
        with tarfile.open(archive, "w:gz") as bundle:
            for path in sorted(args.out.rglob("*")):
                if path.is_file() and path.name != "raw.log":
                    bundle.add(path, arcname=Path("EP_L2_TARGET_BASELINE_850MHZ_r1") / path.relative_to(args.out))
        print(archive)
    print(table)


if __name__ == "__main__":
    main()
