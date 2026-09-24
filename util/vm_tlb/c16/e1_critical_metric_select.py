#!/usr/bin/env python3
"""Resolve the bounded critical-path metric set from the installed NCU query."""

import json
from pathlib import Path


ROOT = Path("/data/c16/e1_operator_family_expansion_v1/metric_query")
QUERY = ROOT / "NCU_QUERY_METRICS_ALL.txt"
SELECTED = {
    "kernel_duration": "gpu__time_duration.sum",
    "l2_read_lookup_hit_sectors": "lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum",
    "l2_read_lookup_miss_sectors": "lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum",
    "dram_read_bytes": "dram__bytes_read.sum",
    "long_scoreboard_stall": "smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct",
    "lsu_memory_pipe_utilization": "smsp__inst_executed_pipe_lsu.avg.pct_of_peak_sustained_active",
    "active_warps_secondary": "sm__warps_active.avg.pct_of_peak_sustained_active",
}
BASE = ["l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum"]


def main():
    lines = QUERY.read_text(encoding="utf-8").splitlines()
    by_name = {}
    for line in lines:
        if not line or line.startswith("Device "):
            continue
        parts = line.split()
        if len(parts) >= 3 and "__" in parts[0]:
            by_name[parts[0]] = {"metric_type": parts[1], "unit": parts[2], "query_line": line.rstrip()}
    rows = []
    for category, metric in SELECTED.items():
        available = metric in by_name
        rows.append({"category": category, "metric_name": metric if available else "UNAVAILABLE", "available": available, **(by_name.get(metric) or {"metric_type": "UNAVAILABLE", "unit": "UNAVAILABLE", "query_line": "UNAVAILABLE"})})
    for metric in BASE:
        if metric not in by_name:
            raise RuntimeError(f"required base metric unavailable: {metric}")
    if not all(row["available"] for row in rows):
        unavailable = [row["category"] for row in rows if not row["available"]]
        print(json.dumps({"warning": "some categories unavailable", "categories": unavailable}))
    result = {
        "status": "PASS",
        "ncu_version": (ROOT / "NCU_VERSION.txt").read_text().strip(),
        "query_command": "/usr/local/cuda-12.8/bin/ncu --query-metrics --query-metrics-mode all",
        "query_receipt_path": str(QUERY),
        "query_line_count": len(lines),
        "base_metrics": BASE,
        "critical_metrics": rows,
        "profile_metric_list": BASE + [row["metric_name"] for row in rows if row["available"]],
        "aggregation": {
            "semantic_sum": ["l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum", "gpu__time_duration.sum", "lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum", "lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum", "dram__bytes_read.sum"],
            "per_kernel_only": ["smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct", "smsp__inst_executed_pipe_lsu.avg.pct_of_peak_sustained_active", "sm__warps_active.avg.pct_of_peak_sustained_active"],
        },
    }
    (ROOT / "METRIC_SELECTION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "profile_metrics": result["profile_metric_list"]}, sort_keys=True))


if __name__ == "__main__":
    main()
