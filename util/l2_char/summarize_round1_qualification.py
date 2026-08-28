#!/usr/bin/env python3
"""Build a review table for a completed Round-1 application-level wave.

The table deliberately does not decide which completed workload belongs in a
paper figure.  It makes the required evidence visible: simulator completion,
runtime/RSS, terminal performance, L2 traffic, resource pressure, blocking,
and output shape.  A missing field stays ``NA``.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]


def final_stat(log: Path, key: str) -> str:
    value = "NA"
    try:
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith(key) and "=" in line:
                value = line.split("=", 1)[1].strip()
    except OSError:
        pass
    return value


def csv_row(path: Path) -> dict[str, str]:
    try:
        with path.open(newline="") as source:
            return next(csv.DictReader(source))
    except (OSError, StopIteration):
        return {}


def csv_count(path: Path) -> int | str:
    try:
        with path.open(newline="") as source:
            return sum(1 for _ in csv.DictReader(source))
    except OSError:
        return "NA"


def number(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "docs/l2_char_v1/round1_results")
    parser.add_argument("--wave", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    fields = [
        "suite", "workload", "input", "wave", "status", "detail", "wall_seconds", "peak_rss_kib",
        "gpu_tot_sim_cycle", "gpu_tot_sim_insn", "sim_insn_per_cycle",
        "l2_total_accesses", "l2_total_misses", "l2_total_miss_rate", "l2_pending_hits",
        "slice_rows", "window_rows", "invariant_records", "invariants_pass",
        "mshr_util_avg", "missq_util_avg", "missq_wb_util_avg", "draml2q_util_avg", "l2dramq_util_avg",
        "data_busy_ratio", "fill_busy_ratio", "reserved_util_avg", "set_reserved_full_ratio",
        "block_set_blocking_ratio", "block_mshr_new_blocking_ratio", "block_mshr_merge_blocking_ratio",
        "block_missq_blocking_ratio", "block_dataport_blocking_ratio", "block_respq_blocking_ratio",
        "wb_request_fraction", "wb_byte_fraction", "trace_tree_sha256", "qualification_state",
    ]
    rows = []
    for status_path in sorted(args.results.rglob("run_status.json")):
        status = json.loads(status_path.read_text())
        if status.get("wave") != args.wave:
            continue
        run_dir = status_path.parent
        summary = csv_row(run_dir / "summary.csv")
        log = run_dir / "raw.log"
        cycles = status.get("terminal_gpu_tot_sim_cycle") or summary.get("gpu_tot_sim_cycle", "NA")
        insn = status.get("terminal_gpu_tot_sim_insn") or summary.get("gpu_tot_sim_insn", "NA")
        cycles_n, insn_n = number(cycles), number(insn)
        row = {key: "NA" for key in fields}
        row.update({key: status.get(key, "NA") for key in ("suite", "workload", "input", "wave", "status", "detail", "wall_seconds", "peak_rss_kib", "trace_tree_sha256")})
        row.update({
            "gpu_tot_sim_cycle": cycles, "gpu_tot_sim_insn": insn,
            "sim_insn_per_cycle": insn_n / cycles_n if cycles_n else "NA",
            "l2_total_accesses": final_stat(log, "L2_total_cache_accesses"),
            "l2_total_misses": final_stat(log, "L2_total_cache_misses"),
            "l2_total_miss_rate": final_stat(log, "L2_total_cache_miss_rate"),
            "l2_pending_hits": final_stat(log, "L2_total_cache_pending_hits"),
            "slice_rows": csv_count(run_dir / "slice.csv"), "window_rows": csv_count(run_dir / "window.csv"),
            "qualification_state": "UNREVIEWED_COMPLETE" if status.get("status") == "COMPLETE_VALID" else status.get("status", "UNKNOWN"),
        })
        for key in fields:
            if key in summary:
                row[key] = summary[key]
        rows.append(row)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} {args.wave} qualification rows to {args.out}")


if __name__ == "__main__":
    main()
