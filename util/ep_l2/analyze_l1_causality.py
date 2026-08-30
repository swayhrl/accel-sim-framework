#!/usr/bin/env python3
"""Create Lane-C causal comparison and 5K temporal summaries from valid runs."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean, median


WORKLOADS = ("vectorAdd_4M", "scan", "spmv", "convolutionSeparable", "btree", "sad", "FWT_7_21")
SUMMARY_FIELDS = ("c7d_descriptor_pool_full_block", "c7d_line_mshr_full_block",
                  "c7d_l2_to_dram_full_block", "c7d_dram_scheduler_full_block",
                  "c7d_wad_full_events", "c7d_wad_hazard_events",
                  "c7d_per_address_cap_block", "c7d_tag_set_all_reserved_block")
L1_FIELDS = ("accesses", "misses", "line_alloc_fail", "miss_queue_full", "mshr_entry_fail",
             "mshr_merge_fail", "mshr_rw_pending", "bank_latency_queue_conflict")


def number(value: str | None) -> float:
    return float(value or 0)


def row(path: Path, scope: str | None = None) -> dict[str, str]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source))
    if scope:
        rows = [item for item in rows if item.get("scope") == scope]
    if not rows:
        raise ValueError("no matching row in " + str(path))
    return rows[-1]


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * p)]


def temporal(directory: Path) -> dict[str, float]:
    with (directory / "target_window.csv").open(newline="") as source:
        l2 = [item for item in csv.DictReader(source) if item.get("scope") == "window"]
    with (directory / "target_dram.csv").open(newline="") as source:
        dram = [item for item in csv.DictReader(source) if item.get("scope") == "window" and item.get("interval") == "5000_cycle"]
    def values(rows: list[dict[str, str]], field: str) -> list[float]:
        return [number(item.get(field)) for item in rows]
    descriptor = values(l2, "descriptor_avg")
    line_mshr = values(l2, "line_mshr_avg")
    lowerq = values(l2, "lowerq_avg")
    sched = values(dram, "scheduler_occ_avg")
    bw = values(dram, "bandwidth_util")
    by_channel: dict[str, list[float]] = {}
    for item in dram:
        by_channel.setdefault(item.get("channel", "?"), []).append(number(item.get("scheduler_full_cycles")))
    channel_pressure = [sum(items) for items in by_channel.values()]
    return {
        "l2_window_rows": len(l2), "dram_window_rows": len(dram),
        "descriptor_window_p50": median(descriptor) if descriptor else 0, "descriptor_window_p95": percentile(descriptor, .95),
        "descriptor_window_max": max(descriptor, default=0), "descriptor_near_full_fraction": sum(v >= 0.95 * 256 for v in descriptor) / len(descriptor) if descriptor else 0,
        "line_mshr_window_p50": median(line_mshr) if line_mshr else 0, "line_mshr_window_p95": percentile(line_mshr, .95), "line_mshr_window_max": max(line_mshr, default=0),
        "lowerq_window_p50": median(lowerq) if lowerq else 0, "lowerq_window_p95": percentile(lowerq, .95), "lowerq_window_max": max(lowerq, default=0),
        "scheduler_window_p50": median(sched) if sched else 0, "scheduler_window_p95": percentile(sched, .95), "scheduler_window_max": max(sched, default=0),
        "scheduler_active_window_fraction": sum(v > 0 for v in values(dram, "scheduler_full_cycles")) / len(dram) if dram else 0,
        "bw_window_p50": median(bw) if bw else 0, "bw_window_p95": percentile(bw, .95), "bw_window_max": max(bw, default=0),
        "scheduler_channel_max_over_mean": max(channel_pressure, default=0) / mean(channel_pressure) if channel_pressure and mean(channel_pressure) else 0,
    }


def record(directory: Path) -> dict[str, float]:
    status = json.loads((directory / "run_status.json").read_text())
    if status.get("status") != "COMPLETE_VALID":
        raise ValueError("invalid run: " + str(directory))
    result = {"cycles": number(status.get("terminal_gpu_tot_sim_cycle")), "instructions": number(status.get("terminal_gpu_tot_sim_insn"))}
    result.update({key: number(value) for key, value in row(directory / "target_summary.csv").items() if key in SUMMARY_FIELDS})
    result.update({"l1_" + key: number(value) for key, value in row(directory / "target_l1.csv", "application").items() if key in L1_FIELDS})
    dram = row(directory / "target_dram.csv", "application")
    result.update({"dram_" + key: number(dram.get(key)) for key in ("successful_read_bytes", "successful_write_bytes", "scheduler_full_cycles", "bandwidth_util")})
    result.update(temporal(directory))
    return result


def relative(base: float, value: float) -> float:
    return (value - base) / base if base else (0.0 if value == 0 else float("inf"))


def classify(speedup_pct: float, desc_delta_pct: float, lower_delta_pct: float, sched_delta_pct: float,
             bw_delta_pct: float) -> str:
    downstream = max(desc_delta_pct, lower_delta_pct, sched_delta_pct)
    if speedup_pct < 2 and downstream < 10:
        return "L1_NOT_CAUSAL"
    if speedup_pct >= 2 and downstream < 10:
        return "L1_LOCAL_BOTTLENECK"
    if speedup_pct >= 2 and max(desc_delta_pct, lower_delta_pct) >= 10:
        return "L1_MASKS_L2"
    if speedup_pct < 2 and max(sched_delta_pct, bw_delta_pct) >= 10:
        return "BOTTLENECK_MOVES_DOWNSTREAM"
    return "MIXED_OR_INSUFFICIENT"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    columns = sorted({key for item in rows for key in item})
    with path.open("w", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=columns)
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cells", nargs="+", default=["META-HR", "BANK-HR"])
    args = parser.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    comparisons: list[dict[str, object]] = []
    temporal_rows: list[dict[str, object]] = []
    classifications: list[dict[str, object]] = []
    for workload in WORKLOADS:
        base_dir = args.base / "B0-Banked" / workload
        if not (base_dir / "run_status.json").is_file():
            continue
        base = record(base_dir)
        temporal_rows.append({"descriptor_capacity": 256, "cell": "BASE", "workload": workload, **temporal(base_dir)})
        for cell in args.cells:
            directory = args.results / cell / workload
            if not (directory / "run_status.json").is_file():
                continue
            current = record(directory)
            temporal_rows.append({"descriptor_capacity": 256, "cell": cell, "workload": workload, **temporal(directory)})
            comparison: dict[str, object] = {"descriptor_capacity": 256, "cell": cell, "workload": workload,
                                             "base_cycles": base["cycles"], "cell_cycles": current["cycles"],
                                             "speedup_pct": (base["cycles"] / current["cycles"] - 1) * 100}
            for key in ("l1_mshr_entry_fail", "l1_mshr_merge_fail", "l1_miss_queue_full", "l1_bank_latency_queue_conflict",
                        "c7d_descriptor_pool_full_block", "c7d_line_mshr_full_block", "c7d_l2_to_dram_full_block",
                        "c7d_dram_scheduler_full_block", "dram_bandwidth_util"):
                comparison["base_" + key] = base[key]; comparison["cell_" + key] = current[key]
                comparison[key + "_delta_pct"] = relative(base[key], current[key]) * 100
            comparisons.append(comparison)
            classifications.append({"descriptor_capacity": 256, "cell": cell, "workload": workload,
                                    "speedup_pct": comparison["speedup_pct"],
                                    "classification": classify(comparison["speedup_pct"], comparison["c7d_descriptor_pool_full_block_delta_pct"],
                                                               comparison["c7d_l2_to_dram_full_block_delta_pct"], comparison["c7d_dram_scheduler_full_block_delta_pct"],
                                                               comparison["dram_bandwidth_util_delta_pct"]),
                                    "automation_note": "heuristic; final interpretation requires joint review of counters and 5K temporal movement"})
    write_csv(args.out / "L1_CAUSALITY_COMPARISON.csv", comparisons)
    write_csv(args.out / "TEMPORAL_SUMMARY.csv", temporal_rows)
    write_csv(args.out / "CAUSAL_CLASSIFICATION.csv", classifications)


if __name__ == "__main__":
    main()
