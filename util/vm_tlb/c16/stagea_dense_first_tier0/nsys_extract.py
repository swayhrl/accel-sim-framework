#!/usr/bin/env python3
"""Recover semantic↔CUDA chronology and legal interval unions from one NSYS trace."""

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import subprocess
from collections import defaultdict
from pathlib import Path


SEMANTIC_RE = re.compile(r"^C16_STAGEA_(\d+)_(.+)$")


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def union(intervals):
    merged = []
    for start, end in sorted((int(a), int(b)) for a, b in intervals if b is not None and b > a):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return merged


def duration(intervals):
    return sum(end - start for start, end in union(intervals))


def family(module):
    if module.endswith(".self_attn"):
        return "ATTENTION"
    if module.endswith(".mlp.gate_up_proj"):
        return "GATE_UP_PROJECTION"
    if module.endswith(".mlp.act_fn"):
        return "ACTIVATION"
    if module.endswith(".mlp.down_proj"):
        return "DOWN_PROJECTION"
    return "OTHER"


def write_tsv(path, rows, fields):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--point", required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--sqlite-input", type=Path)
    parser.add_argument("--observed-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    sqlite_path = args.sqlite_input or args.trace.with_suffix(".sqlite")
    if args.sqlite_input is None:
        subprocess.run(["nsys", "export", "--type", "sqlite", "--force-overwrite=true",
                        "--output", str(sqlite_path), str(args.trace)], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    observed = json.loads(args.observed_json.read_text())
    instrumentation = observed["samples"][0]["instrumentation"]
    shape_by_ordinal = {int(row["ordinal"]): row for row in instrumentation["semantic_order"]}
    batch = int(observed["batch_size"])

    con = sqlite3.connect(sqlite_path)
    tables = {row[0] for row in con.execute("select name from sqlite_master where type='table'")}
    needed = {"StringIds", "NVTX_EVENTS", "CUPTI_ACTIVITY_KIND_RUNTIME", "CUPTI_ACTIVITY_KIND_KERNEL"}
    if not needed.issubset(tables):
        raise RuntimeError(f"missing NSYS tables: {sorted(needed - tables)}")
    strings = {int(row[0]): row[1] for row in con.execute("select id,value from StringIds")}

    nvtx_cols = [row[1] for row in con.execute("pragma table_info(NVTX_EVENTS)")]
    nvtx = []
    for values in con.execute("select * from NVTX_EVENTS"):
        row = dict(zip(nvtx_cols, values))
        text = row.get("text") or strings.get(row.get("textId"))
        if text:
            row["decoded_text"] = text
            nvtx.append(row)
    outer_label = f"C16_TIER0_{args.point}_GRAPH_OFF_OBSERVED"
    parents = [row for row in nvtx if row["decoded_text"] == outer_label and row.get("end")]
    if len(parents) != 1:
        raise RuntimeError(f"expected exactly one parent range, got {len(parents)}")
    parent = parents[0]

    semantics = []
    for row in nvtx:
        match = SEMANTIC_RE.match(row["decoded_text"])
        if match and row.get("end"):
            ordinal = int(match.group(1))
            module = match.group(2)
            shape = shape_by_ordinal.get(ordinal)
            if shape is None or shape["module"] != module:
                raise RuntimeError(f"NVTX/host semantic mismatch at ordinal {ordinal}")
            row.update({"ordinal": ordinal, "module": module, "shape": shape})
            semantics.append(row)
    semantics.sort(key=lambda row: row["ordinal"])
    if [row["ordinal"] for row in semantics] != list(range(len(semantics))):
        raise RuntimeError("semantic ordinals are not contiguous from zero")

    runtime_cols = [row[1] for row in con.execute("pragma table_info(CUPTI_ACTIVITY_KIND_RUNTIME)")]
    runtimes = []
    for values in con.execute("select * from CUPTI_ACTIVITY_KIND_RUNTIME"):
        row = dict(zip(runtime_cols, values))
        if row.get("correlationId") is None:
            continue
        row["api_name"] = strings.get(row.get("nameId"), str(row.get("nameId")))
        if parent["start"] <= row["start"] <= parent["end"]:
            runtimes.append(row)

    kernel_cols = [row[1] for row in con.execute("pragma table_info(CUPTI_ACTIVITY_KIND_KERNEL)")]
    kernels_by_corr = defaultdict(list)
    for values in con.execute("select * from CUPTI_ACTIVITY_KIND_KERNEL"):
        row = dict(zip(kernel_cols, values))
        row["kernel_name"] = strings.get(row.get("demangledName")) or strings.get(row.get("shortName")) or str(row.get("demangledName"))
        kernels_by_corr[int(row["correlationId"])].append(row)
    con.close()

    # Assign each CUDA runtime launch to the narrowest semantic range containing
    # its host timestamp. This prevents nested ranges from double counting.
    runtime_semantic = {}
    for runtime in runtimes:
        candidates = [row for row in semantics
                      if row["start"] <= runtime["start"] <= row["end"]
                      and (row.get("globalTid") is None or runtime.get("globalTid") == row.get("globalTid"))]
        if candidates:
            selected = min(candidates, key=lambda row: row["end"] - row["start"])
            runtime_semantic[int(runtime["correlationId"])] = selected["ordinal"]

    cuda_rows = []
    semantic_kernel_intervals = defaultdict(list)
    parent_kernel_intervals = []
    kernel_names = []
    runtime_by_corr = {int(row["correlationId"]): row for row in runtimes}
    for corr, runtime in runtime_by_corr.items():
        for kernel in kernels_by_corr.get(corr, []):
            ordinal = runtime_semantic.get(corr)
            semantic = shape_by_ordinal.get(ordinal) if ordinal is not None else None
            parent_kernel_intervals.append((kernel["start"], kernel["end"]))
            kernel_names.append(kernel["kernel_name"])
            if ordinal is not None:
                semantic_kernel_intervals[ordinal].append((kernel["start"], kernel["end"]))
            cuda_rows.append({
                "point": args.point,
                "correlation_id": corr,
                "runtime_api": runtime["api_name"],
                "runtime_start_ns": runtime["start"],
                "runtime_end_ns": runtime["end"],
                "semantic_ordinal": "" if ordinal is None else ordinal,
                "semantic_module": "" if semantic is None else semantic["module"],
                "semantic_family": "" if semantic is None else family(semantic["module"]),
                "kernel_name": kernel["kernel_name"],
                "kernel_start_ns": kernel["start"],
                "kernel_end_ns": kernel["end"],
                "kernel_duration_ns": kernel["end"] - kernel["start"],
                "stream_id": kernel.get("streamId"),
                "grid": f"{kernel.get('gridX')}x{kernel.get('gridY')}x{kernel.get('gridZ')}",
                "block": f"{kernel.get('blockX')}x{kernel.get('blockY')}x{kernel.get('blockZ')}",
            })

    parent_merged = union(parent_kernel_intervals)
    parent_union_ns = duration(parent_kernel_intervals)
    semantic_rows = []
    for semantic in semantics:
        ordinal = semantic["ordinal"]
        shape = semantic["shape"]
        intervals = semantic_kernel_intervals.get(ordinal, [])
        merged = union(intervals)
        input_shape = shape.get("input_shape")
        output_shape = shape.get("output_shape")
        effective_m = input_shape[0] if input_shape else (output_shape[0] if output_shape else None)
        phase = "PREFILL" if effective_m is not None and effective_m > batch else "DECODE"
        semantic_rows.append({
            "point": args.point,
            "ordinal": ordinal,
            "module": semantic["module"],
            "family": family(semantic["module"]),
            "phase": phase,
            "effective_m": effective_m,
            "input_shape": json.dumps(input_shape, separators=(",", ":")),
            "output_shape": json.dumps(output_shape, separators=(",", ":")),
            "host_nvtx_start_ns": semantic["start"],
            "host_nvtx_end_ns": semantic["end"],
            "cuda_kernel_count": len(intervals),
            "cuda_interval_union_ns": duration(intervals),
            "cuda_first_start_ns": merged[0][0] if merged else "",
            "cuda_last_end_ns": merged[-1][1] if merged else "",
            "parent_cuda_union_fraction": (duration(intervals) / parent_union_ns) if parent_union_ns else 0.0,
        })

    gap_rows = []
    for index in range(len(parent_merged) - 1):
        left, right = parent_merged[index], parent_merged[index + 1]
        gap = right[0] - left[1]
        if gap > 0:
            gap_rows.append({
                "point": args.point,
                "gap_index": len(gap_rows),
                "previous_covered_end_ns": left[1],
                "next_covered_start_ns": right[0],
                "gap_ns": gap,
                "parent_cuda_union_fraction": gap / parent_union_ns if parent_union_ns else 0.0,
            })

    write_tsv(args.output_dir / f"{args.point}_SEMANTIC_INTERVALS.tsv", semantic_rows,
              ["point", "ordinal", "module", "family", "phase", "effective_m", "input_shape", "output_shape",
               "host_nvtx_start_ns", "host_nvtx_end_ns", "cuda_kernel_count", "cuda_interval_union_ns",
               "cuda_first_start_ns", "cuda_last_end_ns", "parent_cuda_union_fraction"])
    write_tsv(args.output_dir / f"{args.point}_CUDA_INTERVALS.tsv", cuda_rows,
              ["point", "correlation_id", "runtime_api", "runtime_start_ns", "runtime_end_ns", "semantic_ordinal",
               "semantic_module", "semantic_family", "kernel_name", "kernel_start_ns", "kernel_end_ns",
               "kernel_duration_ns", "stream_id", "grid", "block"])
    write_tsv(args.output_dir / f"{args.point}_LAUNCH_GAPS.tsv", gap_rows,
              ["point", "gap_index", "previous_covered_end_ns", "next_covered_start_ns", "gap_ns", "parent_cuda_union_fraction"])
    receipt = {
        "point": args.point,
        "status": "PASS" if semantics and cuda_rows and parent_union_ns else "FAIL",
        "trace": str(args.trace),
        "trace_bytes": args.trace.stat().st_size,
        "trace_sha256": sha(args.trace),
        "sqlite": str(sqlite_path),
        "sqlite_bytes": sqlite_path.stat().st_size,
        "sqlite_sha256": sha(sqlite_path),
        "parent_label": outer_label,
        "parent_nvtx_start_ns": parent["start"],
        "parent_nvtx_end_ns": parent["end"],
        "semantic_range_count": len(semantics),
        "runtime_call_count_in_parent": len(runtimes),
        "kernel_count_in_parent": len(cuda_rows),
        "kernel_inventory_sha256": sha_json(dict(sorted(__import__('collections').Counter(kernel_names).items()))),
        "parent_cuda_interval_union_ns": parent_union_ns,
        "parent_cuda_merged_interval_count": len(parent_merged),
        "positive_launch_gap_count": len(gap_rows),
        "positive_launch_gap_union_ns": sum(row["gap_ns"] for row in gap_rows),
        "host_nvtx_duration_used_as_gpu_work": False,
        "overlap_handling": "INTERVAL_UNION_NOT_SUM",
    }
    (args.output_dir / f"{args.point}_NSYS_PARSE_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    if receipt["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
