#!/usr/bin/env python3
"""Read-only R19F2 Stage A CUPTI->runtime->NVTX consumer qualification."""

import csv
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path("/data/c16/awma/r19f2_fp8_software_counterfactual_20261001/raw")
DB = ROOT / "NSYS_R19F2_STAGE_A_CONSUMERS.sqlite"
conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
strings = dict(conn.execute("select id,value from StringIds"))
range_names = ("R19F2_B0_DUPLICATE_P", "R19F2_S1_SHARED_P", "R19F2_D0_READY_PAIR_P")
ranges = list(conn.execute(
    "select start,end,text,globalTid from NVTX_EVENTS where text in (?,?,?) order by start", range_names
))
runtimes = list(conn.execute(
    "select start,end,globalTid,correlationId,nameId from CUPTI_ACTIVITY_KIND_RUNTIME order by start"
))
kernels = list(conn.execute(
    "select start,end,correlationId,demangledName,shortName,gridX,gridY,gridZ,blockX,blockY,blockZ,streamId "
    "from CUPTI_ACTIVITY_KIND_KERNEL order by start"
))
by_corr = defaultdict(list)
for kernel in kernels:
    by_corr[kernel[2]].append(kernel)
rows = []
for ri, (begin, end, name, tid) in enumerate(ranges):
    arm = name.removeprefix("R19F2_").removesuffix("_P")
    for launch_begin, launch_end, launch_tid, corr, api_id in runtimes:
        if launch_tid != tid or not begin <= launch_begin <= end:
            continue
        for kernel in by_corr.get(corr, []):
            kb, ke, _, fn_id, short_id, gx, gy, gz, bx, by, bz, stream = kernel
            rows.append({
                "range_index": ri,
                "arm": arm,
                "phase": "P",
                "nvtx_begin_ns": begin,
                "nvtx_end_ns": end,
                "runtime_begin_ns": launch_begin,
                "runtime_end_ns": launch_end,
                "runtime_api": strings.get(api_id, "UNKNOWN"),
                "correlation_id": corr,
                "kernel_begin_ns": kb,
                "kernel_end_ns": ke,
                "kernel_duration_ns": ke - kb,
                "function": strings.get(fn_id, "UNKNOWN"),
                "short_function": strings.get(short_id, "UNKNOWN"),
                "grid": f"{gx},{gy},{gz}",
                "block": f"{bx},{by},{bz}",
                "stream_id": stream,
                "consumer_occurrence": "",
            })
if len(ranges) != 9 or not rows:
    raise RuntimeError(f"Expected 9 ranges and attributed kernels, saw {len(ranges)} / {len(rows)}")

per_range = []
gemm_identity = None
for ri, (begin, end, name, _) in enumerate(ranges):
    arm = name.removeprefix("R19F2_").removesuffix("_P")
    current = sorted((r for r in rows if r["range_index"] == ri), key=lambda r: r["kernel_begin_ns"])
    gemms = [r for r in current if "sm89_xmma_gemm_e4m3" in r["function"]]
    if len(gemms) != 2:
        raise RuntimeError(f"Expected two native SM89 E4M3 GEMMs in range {ri}, got {len(gemms)}")
    for occurrence, row in enumerate(gemms, start=1):
        row["consumer_occurrence"] = occurrence
        identity = (row["function"], row["grid"], row["block"])
        if gemm_identity is None:
            gemm_identity = identity
        elif identity != gemm_identity:
            raise RuntimeError(f"Consumer changed: {identity} != {gemm_identity}")
    expected = {"B0_DUPLICATE": 10, "S1_SHARED": 6, "D0_READY_PAIR": 2}[arm]
    if len(current) != expected:
        raise RuntimeError(f"Unexpected kernel count in {arm}: {len(current)} != {expected}")
    service = sum(r["kernel_duration_ns"] for r in current)
    span = current[-1]["kernel_end_ns"] - current[0]["kernel_begin_ns"]
    gemm_service = sum(r["kernel_duration_ns"] for r in gemms)
    per_range.append({
        "range_index": ri,
        "arm": arm,
        "nvtx_wall_ns_not_primary": end - begin,
        "kernel_count": len(current),
        "input_quantizer_invocations": (len(current) - 2) // 4,
        "consumer_gemm_count": len(gemms),
        "kernel_service_ns": service,
        "gemm_service_ns": gemm_service,
        "prep_kernel_service_ns": service - gemm_service,
        "gpu_first_to_last_span_ns": span,
        "gpu_inter_kernel_gap_ns": span - service,
    })
with (ROOT / "NSYS_KERNEL_IDENTITY.tsv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
with (ROOT / "PROFILE_SUMMARY.tsv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(per_range[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(per_range)
summary = {
    "method": "CUPTI kernel correlationId -> CPU runtime launch -> same-thread NVTX range",
    "range_count": len(ranges),
    "attributed_kernel_count": len(rows),
    "total_kernel_records": len(kernels),
    "consumer_function": gemm_identity[0],
    "consumer_grid": gemm_identity[1],
    "consumer_block": gemm_identity[2],
    "consumer_occurrence_order": ["gate", "up"],
    "per_range": per_range,
    "per_arm_strata": {},
}
for arm in ("B0_DUPLICATE", "S1_SHARED", "D0_READY_PAIR"):
    stratum = Counter((r["function"], r["grid"], r["block"]) for r in rows if r["arm"] == arm)
    summary["per_arm_strata"][arm] = [
        {"function": fn, "grid": grid, "block": block, "count": count}
        for (fn, grid, block), count in stratum.items()
    ]
(ROOT / "NSYS_CONSUMER_SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps({"range_count": len(ranges), "attributed_kernel_count": len(rows), "consumer_function": gemm_identity[0], "consumer_grid": gemm_identity[1], "consumer_block": gemm_identity[2], "per_range": per_range}, sort_keys=True))
