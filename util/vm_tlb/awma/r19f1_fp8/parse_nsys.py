#!/usr/bin/env python3
"""CUPTI correlation -> runtime launch -> NVTX A1/D0 range kernel identity."""

import csv
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path("/data/c16/awma/r19f1_fp8_numeric_decomposition_20261001/raw")
DB = ROOT / "NSYS_R19F1_FP8_CONSUMER_V1.sqlite"
CONN = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
STRINGS = dict(CONN.execute("select id,value from StringIds"))
RANGES = list(CONN.execute(
    "select start,end,text,globalTid from NVTX_EVENTS "
    "where text in ('R19F1_A1_ONLINE','R19F1_D0_READY') order by start"
))
RUNTIMES = list(CONN.execute(
    "select start,end,globalTid,correlationId,nameId "
    "from CUPTI_ACTIVITY_KIND_RUNTIME order by start"
))
KERNELS = list(CONN.execute(
    "select start,end,correlationId,demangledName,shortName,gridX,gridY,gridZ,"
    "blockX,blockY,blockZ,streamId from CUPTI_ACTIVITY_KIND_KERNEL order by start"
))
BY_CORRELATION = defaultdict(list)
for kernel in KERNELS:
    BY_CORRELATION[kernel[2]].append(kernel)

ROWS = []
for ri, (begin, end, phase, tid) in enumerate(RANGES):
    for launch_begin, launch_end, launch_tid, corr, runtime_name_id in RUNTIMES:
        if launch_tid != tid or not begin <= launch_begin <= end:
            continue
        for kernel in BY_CORRELATION.get(corr, []):
            kbegin, kend, _, demangled_id, short_id, gx, gy, gz, bx, by, bz, stream = kernel
            ROWS.append({
                "nvtx_range_index": ri,
                "phase": phase,
                "range_start_ns": begin,
                "range_end_ns": end,
                "runtime_start_ns": launch_begin,
                "runtime_end_ns": launch_end,
                "runtime_api": STRINGS.get(runtime_name_id, "UNKNOWN"),
                "correlation_id": corr,
                "kernel_start_ns": kbegin,
                "kernel_end_ns": kend,
                "kernel_duration_ns": kend - kbegin,
                "demangled_function": STRINGS.get(demangled_id, "UNKNOWN"),
                "short_function": STRINGS.get(short_id, "UNKNOWN"),
                "grid": f"{gx},{gy},{gz}",
                "block": f"{bx},{by},{bz}",
                "stream_id": stream,
            })

if len(RANGES) != 6 or not ROWS:
    raise RuntimeError(f"Expected six A1/D0 ranges and attributed launches; ranges={len(RANGES)} rows={len(ROWS)}")

tsv = ROOT / "NSYS_KERNEL_IDENTITY.tsv"
with tsv.open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(ROWS[0]), delimiter="\t")
    writer.writeheader()
    writer.writerows(ROWS)

by_phase = defaultdict(list)
for row in ROWS:
    by_phase[row["phase"]].append(row)
summary = {
    "nsys_source": str(DB),
    "method": "kernel correlationId -> CPU runtime launch -> same-thread NVTX range",
    "range_count": len(RANGES),
    "attributed_kernel_launches": len(ROWS),
    "total_kernel_records": len(KERNELS),
    "phases": {},
}
profile_rows = []
for ri, (begin, end, phase, _) in enumerate(RANGES):
    in_range = sorted((r for r in ROWS if r["nvtx_range_index"] == ri), key=lambda r: r["kernel_start_ns"])
    service = sum(r["kernel_duration_ns"] for r in in_range)
    span = in_range[-1]["kernel_end_ns"] - in_range[0]["kernel_start_ns"]
    gemms = [r for r in in_range if "sm89_xmma_gemm_e4m3" in r["demangled_function"]]
    if len(gemms) != 1:
        raise RuntimeError(f"Expected one SM89 FP8 GEMM in range {ri}, got {len(gemms)}")
    profile_rows.append({
        "range_index": ri,
        "phase": phase,
        "nvtx_wall_ns_not_primary": end - begin,
        "kernel_count": len(in_range),
        "kernel_service_ns": service,
        "gpu_first_to_last_span_ns": span,
        "gpu_inter_kernel_gap_ns": span - service,
        "consumer_gemm_ns": gemms[0]["kernel_duration_ns"],
        "representation_kernel_service_ns": service - gemms[0]["kernel_duration_ns"],
    })
with (ROOT / "PROFILE_SUMMARY.tsv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(profile_rows[0]), delimiter="\t")
    writer.writeheader()
    writer.writerows(profile_rows)
summary["per_range"] = profile_rows
for phase, rows in by_phase.items():
    strata = Counter((r["demangled_function"], r["grid"], r["block"]) for r in rows)
    summary["phases"][phase] = {
        "range_count": sum(text == phase for _, _, text, _ in RANGES),
        "kernel_count": len(rows),
        "total_gpu_kernel_time_ns": sum(r["kernel_duration_ns"] for r in rows),
        "strata": [
            {"function": fn, "grid": grid, "block": block, "count": count}
            for (fn, grid, block), count in strata.items()
        ],
    }
summary_path = ROOT / "NSYS_KERNEL_IDENTITY_SUMMARY.json"
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps(summary, sort_keys=True))
