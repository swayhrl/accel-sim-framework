#!/usr/bin/env python3
"""Extract correlation-authoritative D0-D3 FFN timeline tables from NSYS SQLite."""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from nsys_tools import (DECODE_WALL, connect, file_sha, kernel_rows, nvtx_ranges,
                        parse_semantic, read_json, runtime_by_correlation)


def write_tsv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sqlite", type=Path, required=True)
    p.add_argument("--runner-json", type=Path, required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    run = read_json(args.runner_json)
    conn = connect(args.sqlite)
    try:
        kernels = kernel_rows(conn); runtimes = runtime_by_correlation(conn); nvtx = nvtx_ranges(conn)
    finally:
        conn.close()
    walls = [r for r in nvtx if r["label"] == DECODE_WALL]
    if len(walls) != 1:
        raise RuntimeError(f"decode wall count {len(walls)} != 1")
    wall = walls[0]
    semantic = []
    for r in nvtx:
        parsed = parse_semantic(r["label"])
        if parsed:
            semantic.append({**r, **parsed})
    expected = {(d,l,role) for d in range(4) for l in range(28)
                for role in ("gate_proj","up_proj","activation","multiply","down_proj")}
    observed = {(r["decode_step"],r["layer"],r["role"]) for r in semantic}
    if observed != expected or len(semantic) != 560:
        raise RuntimeError(f"semantic range closure missing={len(expected-observed)} extra={len(observed-expected)} rows={len(semantic)}")
    activity = []
    correlations = []
    range_activities = defaultdict(list)
    uncorrelated = 0
    for k in kernels:
        rt = runtimes.get(k["correlation_id"])
        if rt is None:
            continue
        inside_wall = rt["global_tid"] == wall["global_tid"] and wall["start"] <= rt["start"] and rt["end"] <= wall["end"]
        if not inside_wall:
            continue
        candidates = [r for r in semantic if r["global_tid"] == rt["global_tid"] and r["start"] <= rt["start"] and rt["end"] <= r["end"]]
        candidates.sort(key=lambda r: r["end"] - r["start"])
        chosen = candidates[0] if candidates else None
        if chosen is None:
            uncorrelated += 1
            layer, role, step, label, status = -1, "NON_FFN_WITHIN_DECODE", -1, "", "OUTSIDE_FFN_SEMANTIC_RANGE"
        else:
            layer, role, step, label, status = chosen["layer"], chosen["role"], chosen["decode_step"], chosen["label"], "CORRELATION_AUTHORITY"
            range_activities[chosen["rowid"]].append(k)
        common = {"run_id": args.run_id, "decode_step": step, "layer": layer, "semantic_role": role,
                  "nvtx_range": label, "cuda_api_launch": rt["api_name"], "correlation_id": k["correlation_id"],
                  "stream": k["stream"], "kernel_name": k["kernel_name"], "gpu_start": k["start"], "gpu_end": k["end"],
                  "grid": k["grid"], "block": k["block"], "attribution_status": status}
        activity.append(common)
        correlations.append({**common, "cpu_launch_start": rt["start"], "cpu_launch_end": rt["end"],
                             "runtime_rowid": rt["rowid"], "kernel_rowid": k["rowid"]})
    range_rows=[]; layer_rows=[]; projection_missing=[]
    for r in semantic:
        acts=range_activities[r["rowid"]]
        status="CORRELATED_GPU_ACTIVITY" if acts else "NO_DISTINCT_GPU_ACTIVITY"
        if r["role"] in ("gate_proj","up_proj","down_proj") and not acts:
            projection_missing.append(r["label"])
        range_rows.append({"run_id":args.run_id,"decode_step":r["decode_step"],"layer":r["layer"],"semantic_role":r["role"],
                           "nvtx_range":r["label"],"cpu_start":r["start"],"cpu_end":r["end"],"global_tid":r["global_tid"],
                           "gpu_activity_count":len(acts),"status":status})
        layer_rows.append({"run_id":args.run_id,"decode_step":r["decode_step"],"layer":r["layer"],"semantic_role":r["role"],
                           "nvtx_range":r["label"],"cpu_range_start":r["start"],"cpu_range_end":r["end"],
                           "earliest_gpu_start":min((x["start"] for x in acts),default=""),"last_gpu_end":max((x["end"] for x in acts),default=""),
                           "gpu_activity_count":len(acts),"kernel_names":"|".join(x["kernel_name"] for x in acts),"status":status})
    if projection_missing:
        raise RuntimeError(f"projection ranges missing correlated GPU activity: {projection_missing[:5]} count={len(projection_missing)}")
    gpu_inside=[x for x in activity]
    wall_rows=[{"run_id":args.run_id,"nvtx_range":DECODE_WALL,"cpu_start":wall["start"],"cpu_end":wall["end"],
                "gpu_start":min(x["gpu_start"] for x in gpu_inside),"gpu_end":max(x["gpu_end"] for x in gpu_inside),
                "gpu_activity_count":len(gpu_inside)}]
    write_tsv(args.output_dir/"SEMANTIC_RANGE_MAP.tsv", tuple(range_rows[0]), range_rows)
    write_tsv(args.output_dir/"CUDA_CORRELATION.tsv", tuple(correlations[0]), correlations)
    write_tsv(args.output_dir/"GPU_ACTIVITY.tsv", tuple(activity[0]), activity)
    write_tsv(args.output_dir/"FFN_LAYER_ACTIVITY.tsv", tuple(layer_rows[0]), layer_rows)
    write_tsv(args.output_dir/"DECODE_WALL_INTERVAL.tsv", tuple(wall_rows[0]), wall_rows)
    output_checks=[{"run_id":args.run_id,"generated_token_ids":json.dumps(run["generated_token_ids_D0_D3"]),
                    "runner_json_sha256":file_sha(args.runner_json),"sqlite_sha256":file_sha(args.sqlite),
                    "call_order_count":len(run["call_order"]),"occurrence_count":len(run["occurrences"]),"status":"PASS"}]
    write_tsv(args.output_dir/"OUTPUT_CHECKS.tsv", tuple(output_checks[0]), output_checks)
    assertions={"status":"PASS","run_id":args.run_id,"semantic_range_count":len(semantic),"projection_ranges":336,
                "activation_ranges":112,"multiply_ranges":112,"decode_wall_count":1,"projection_missing_activity":0,
                "decode_gpu_activity_count":len(activity),"non_ffn_within_decode_activity_count":uncorrelated,
                "correlation_authority":"NVTX launch scope + CUDA runtime correlationId -> GPU kernel"}
    (args.output_dir/"RAW_ASSERTIONS.json").write_text(json.dumps(assertions,indent=2,sort_keys=True)+"\n")
    print(json.dumps(assertions,sort_keys=True))


if __name__ == "__main__": main()
