#!/usr/bin/env python3
"""Deterministic CPU-only Stage A Tier0 producer postprocess."""

import argparse
import csv
import hashlib
import json
import math
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


POINTS = ("MP01", "MP02", "MP03", "MP05")
ATOL = 0.05
RTOL = 0.01


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_tsv(path, rows, fields):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def append_tsv(paths, output):
    rows, fields = [], None
    for path in paths:
        if not path.is_file():
            continue
        current = read_tsv(path)
        if current:
            fields = fields or list(current[0])
            if list(current[0]) != fields:
                raise RuntimeError(f"TSV schema mismatch: {path}")
            rows.extend(current)
    if fields is None:
        raise RuntimeError(f"no TSV rows for {output.name}")
    write_tsv(output, rows, fields)


def union(intervals):
    merged = []
    for start, end in sorted((int(a), int(b)) for a, b in intervals if int(b) > int(a)):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return merged


def union_duration(intervals):
    return sum(end - start for start, end in union(intervals))


def sampled_logprobs(completion):
    values = []
    for token, row in zip(completion["tokens"], completion.get("logprobs", [])):
        mapping = {int(item["token_id"]): float(item["logprob"]) for item in row}
        values.append(mapping.get(int(token)))
    return values


def compare_rows(reference, other):
    checks = []
    if len(reference) != len(other):
        return {"pass": False, "row_count_exact": False, "tokens_exact": False,
                "logprobs_within_tolerance": False, "max_logprob_abs": None}
    max_abs = 0.0
    row_identity = tokens_exact = numeric = True
    for left, right in zip(reference, other):
        row_identity &= left["batch_row"] == right["batch_row"] and left["source_id"] == right["source_id"]
        a, b = left["completion"], right["completion"]
        tokens_exact &= a["tokens"] == b["tokens"]
        la, lb = sampled_logprobs(a), sampled_logprobs(b)
        if len(la) != len(lb) or any(x is None or y is None for x, y in zip(la, lb)):
            numeric = False
            continue
        for x, y in zip(la, lb):
            delta = abs(x - y)
            max_abs = max(max_abs, delta)
            numeric &= delta <= ATOL + RTOL * abs(x)
    return {"pass": row_identity and tokens_exact and numeric,
            "row_count_exact": True, "row_identity_exact": row_identity,
            "tokens_exact": tokens_exact, "logprobs_within_tolerance": numeric,
            "max_logprob_abs": max_abs, "atol": ATOL, "rtol": RTOL}


def backend_signature(result):
    modules = sorted([
        row["module_class"], row["quant_method_class"], row["kernel_backend_class"],
        json.dumps(row["parameter_shapes"], sort_keys=True)
    ] for row in result["module_census"])
    attention = sorted([row["module_class"], row["impl_class"]]
                       for row in result["attention_backend"]["modules"])
    groups = sorted([row["group_class"], row["backend_class"]]
                    for row in result["attention_backend"]["runner_groups"])
    return {"modules": modules, "attention": attention, "groups": groups}


def cv(values):
    return statistics.stdev(values) / statistics.mean(values) if len(values) > 1 and statistics.mean(values) else 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo, raw, out = args.repo.resolve(), args.raw.resolve(), args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    config = json.loads(args.config.read_text())
    execution = json.loads((raw / "POINT_EXECUTION_RAW.json").read_text())

    point_identity = []
    token_rows = []
    sample_rows = []
    summary_rows = []
    correctness_rows = []
    backend_rows = []
    observer_rows = []
    capture_rows = []
    status_rows = []
    parsed_points = []
    point_results = {}

    for point in POINTS:
        cfg = config["points"][point]
        point_identity.append({
            "point": point, "model_kind": cfg["model_kind"], "model_revision": cfg["model_revision"],
            "phase": cfg["phase"], "batch": cfg["batch_size"], "prompt_tokens_per_row": 512,
            "decode_tokens": cfg["decode_tokens"], "native_timing_endpoint": cfg["native_timing_endpoint"],
            "observer_identity": cfg["observer_identity"], "gpu_cap_seconds": cfg["gpu_active_cap_seconds"],
        })
        for item in cfg["inputs"]:
            token_rows.append({"point": point, **item})
        point_dir = raw / point
        on_path = point_dir / f"{point}_GRAPH_ON_NATIVE.json"
        off_path = point_dir / f"{point}_GRAPH_OFF_NATIVE.json"
        observed_path = point_dir / f"{point}_GRAPH_OFF_OBSERVED.json"
        on = json.loads(on_path.read_text()) if on_path.is_file() else None
        off = json.loads(off_path.read_text()) if off_path.is_file() else None
        observed = json.loads(observed_path.read_text()) if observed_path.is_file() else None
        point_results[point] = {"on": on, "off": off, "observed": observed}

        reference = on["samples"][0]["rows"] if on and on.get("status") == "PASS" else None
        output_checks = []
        if reference:
            for result in (on, off, observed):
                if result and result.get("status") == "PASS":
                    for sample in result["samples"]:
                        output_checks.append(compare_rows(reference, sample["rows"]))
        signatures = [backend_signature(result) for result in (on, off, observed) if result and result.get("status") == "PASS"]
        backend_exact = len(signatures) == 3 and all(value == signatures[0] for value in signatures[1:])
        expected_method = "AutoAWQMarlinLinearMethod" if point == "MP05" else "UnquantizedLinearMethod"
        expected_kernel = "MarlinLinearKernel" if point == "MP05" else None
        methods = sorted({row.get("quant_method_class") for row in (on or {}).get("module_census", []) if row.get("quant_method_class")})
        kernels = sorted({row.get("kernel_backend_class") for row in (on or {}).get("module_census", []) if row.get("kernel_backend_class")})
        attention = sorted({row.get("impl_class") for row in (on or {}).get("attention_backend", {}).get("modules", []) if row.get("impl_class")})
        legal_backend = expected_method in methods and "FlashAttentionImpl" in attention and (expected_kernel is None or expected_kernel in kernels)

        semantic = None
        if observed and observed.get("status") == "PASS":
            semantic = observed["samples"][0].get("instrumentation")
        semantic_order = semantic.get("semantic_order", []) if semantic else []
        semantic_exact = (len(semantic_order) == cfg["expected_semantic_occurrences"]
                          and [row["ordinal"] for row in semantic_order] == list(range(len(semantic_order))))
        input_exact = all(item["status"] == "PASS" for item in cfg["inputs"])
        correctness_pass = (bool(output_checks) and all(row["pass"] for row in output_checks)
                            and backend_exact and legal_backend and semantic_exact and input_exact)
        correctness_rows.append({
            "point": point, "input_exact": input_exact,
            "tokens_exact": all(row["tokens_exact"] for row in output_checks) if output_checks else False,
            "logprobs_within_tolerance": all(row["logprobs_within_tolerance"] for row in output_checks) if output_checks else False,
            "max_logprob_abs": max((row["max_logprob_abs"] or 0.0 for row in output_checks), default=""),
            "batch_rows_exact": all(row.get("row_identity_exact", False) for row in output_checks) if output_checks else False,
            "semantic_shape_order_exact": semantic_exact,
            "backend_identity_exact": backend_exact and legal_backend,
            "status": "PASS" if correctness_pass else "FAIL",
        })
        backend_rows.append({
            "point": point, "attention_backend": json.dumps(attention, separators=(",", ":")),
            "quant_method_classes": json.dumps(methods, separators=(",", ":")),
            "kernel_backend_classes": json.dumps(kernels, separators=(",", ":")),
            "expected_quant_method": expected_method, "expected_kernel_backend": expected_kernel or "NONE",
            "cross_arm_signature_exact": backend_exact, "no_requantization": cfg.get("no_requantization", "NOT_APPLICABLE"),
            "status": "PASS" if backend_exact and legal_backend else "FAIL",
        })
        observer_rows.append({
            "point": point, "observer_identity": cfg["observer_identity"],
            "observer_source_sha256": cfg["observer_source_sha256"],
            "per_occurrence_cuda_events": cfg["per_occurrence_cuda_events"],
            "outer_request_cuda_events": 2, "semantic_occurrences": len(semantic_order),
            "semantic_order_sha256": semantic.get("semantic_order_sha256", "") if semantic else "",
            "status": "PASS" if semantic_exact else "FAIL",
        })

        for graph, result in (("GRAPH_ON", on), ("GRAPH_OFF", off)):
            if not result or result.get("status") != "PASS":
                continue
            host_values, cuda_values = [], []
            for index, sample in enumerate(result["samples"]):
                host_values.append(sample["host_wall_ms"])
                cuda_values.append(sample["cuda_event_ms"])
                sample_rows.append({
                    "point": point, "graph_mode": graph, "sample_index": index,
                    "host_wall_ms": sample["host_wall_ms"], "cuda_event_ms": sample["cuda_event_ms"],
                    "batch_rows": len(sample["rows"]),
                    "tokens_by_row": json.dumps([row["completion"]["tokens"] for row in sample["rows"]], separators=(",", ":")),
                })
            summary_rows.append({
                "point": point, "graph_mode": graph, "sample_count": len(cuda_values),
                "host_median_ms": statistics.median(host_values), "cuda_median_ms": statistics.median(cuda_values),
                "host_cv": cv(host_values), "cuda_cv": cv(cuda_values),
                "min_cuda_ms": min(cuda_values), "max_cuda_ms": max(cuda_values),
                "timing_authority": "NATIVE_INSTRUMENTATION_OFF_REQUEST_CUDA_EVENT",
            })

        raw_status = execution["points"].get(point, {}).get("status", "NOT_RUN")
        trace = point_dir / f"{point}_GRAPH_OFF_OBSERVED.nsys-rep"
        parse_receipt = None
        if trace.is_file() and observed and observed.get("status") == "PASS":
            parse_dir = raw / "analysis"
            parse_dir.mkdir(exist_ok=True)
            subprocess.run([
                "python3", config["nsys_extract"], "--point", point,
                "--trace", str(trace), "--observed-json", str(observed_path),
                "--output-dir", str(parse_dir),
            ], cwd=repo, check=True)
            parse_receipt = json.loads((parse_dir / f"{point}_NSYS_PARSE_RECEIPT.json").read_text())
            parsed_points.append(point)
        capture_rows.append({
            "point": point, "capture_count": execution["points"].get(point, {}).get("nsys_capture_count", 0),
            "trace_path": str(trace) if trace.is_file() else "", "trace_bytes": trace.stat().st_size if trace.is_file() else "",
            "trace_sha256": sha(trace) if trace.is_file() else "",
            "semantic_ranges": parse_receipt.get("semantic_range_count", "") if parse_receipt else "",
            "kernel_count": parse_receipt.get("kernel_count_in_parent", "") if parse_receipt else "",
            "parent_cuda_union_ns": parse_receipt.get("parent_cuda_interval_union_ns", "") if parse_receipt else "",
            "status": parse_receipt.get("status", "UNAVAILABLE") if parse_receipt else "UNAVAILABLE",
        })
        analysis_pass = correctness_pass and parse_receipt is not None and parse_receipt.get("status") == "PASS"
        status_rows.append({
            "point": point, "gpu_status": raw_status,
            "correctness_status": "PASS" if correctness_pass else "FAIL",
            "nsys_status": parse_receipt.get("status", "UNAVAILABLE") if parse_receipt else "UNAVAILABLE",
            "point_gpu_active_seconds": execution["points"].get(point, {}).get("gpu_active_seconds", 0),
            "point_cap_seconds": cfg["gpu_active_cap_seconds"],
            "status": "COMPLETE" if analysis_pass else "PARTIAL",
        })

    write_tsv(out / "POINT_IDENTITY.tsv", point_identity,
              ["point", "model_kind", "model_revision", "phase", "batch", "prompt_tokens_per_row", "decode_tokens", "native_timing_endpoint", "observer_identity", "gpu_cap_seconds"])
    write_tsv(out / "TOKENIZATION_RECHECK.tsv", token_rows,
              ["point", "source_id", "model_key", "model_revision", "tokenizer_revision", "source_utf8_sha256", "token_ids_sha256", "token_id_file_sha256", "token_count", "path", "status"])
    write_tsv(out / "NATIVE_REQUEST_SAMPLES.tsv", sample_rows,
              ["point", "graph_mode", "sample_index", "host_wall_ms", "cuda_event_ms", "batch_rows", "tokens_by_row"])
    write_tsv(out / "NATIVE_REQUEST_SUMMARY.tsv", summary_rows,
              ["point", "graph_mode", "sample_count", "host_median_ms", "cuda_median_ms", "host_cv", "cuda_cv", "min_cuda_ms", "max_cuda_ms", "timing_authority"])
    write_tsv(out / "GRAPH_MODE_CORRECTNESS.tsv", correctness_rows,
              ["point", "input_exact", "tokens_exact", "logprobs_within_tolerance", "max_logprob_abs", "batch_rows_exact", "semantic_shape_order_exact", "backend_identity_exact", "status"])
    write_tsv(out / "BACKEND_KERNEL_IDENTITY.tsv", backend_rows,
              ["point", "attention_backend", "quant_method_classes", "kernel_backend_classes", "expected_quant_method", "expected_kernel_backend", "cross_arm_signature_exact", "no_requantization", "status"])
    write_tsv(out / "OBSERVER_IDENTITY.tsv", observer_rows,
              ["point", "observer_identity", "observer_source_sha256", "per_occurrence_cuda_events", "outer_request_cuda_events", "semantic_occurrences", "semantic_order_sha256", "status"])
    write_tsv(out / "NSYS_CAPTURE_INDEX.tsv", capture_rows,
              ["point", "capture_count", "trace_path", "trace_bytes", "trace_sha256", "semantic_ranges", "kernel_count", "parent_cuda_union_ns", "status"])
    write_tsv(out / "POINT_EXECUTION_STATUS.tsv", status_rows,
              ["point", "gpu_status", "correctness_status", "nsys_status", "point_gpu_active_seconds", "point_cap_seconds", "status"])

    analysis_dir = raw / "analysis"
    append_tsv([analysis_dir / f"{point}_SEMANTIC_INTERVALS.tsv" for point in parsed_points], out / "SEMANTIC_INTERVALS.tsv")
    append_tsv([analysis_dir / f"{point}_CUDA_INTERVALS.tsv" for point in parsed_points], out / "CUDA_INTERVALS.tsv")
    append_tsv([analysis_dir / f"{point}_LAUNCH_GAPS.tsv" for point in parsed_points], out / "LAUNCH_GAPS.tsv")

    summary_lookup = {(row["point"], row["graph_mode"]): row for row in summary_rows}
    headroom_rows = []
    for point in parsed_points:
        receipt = json.loads((analysis_dir / f"{point}_NSYS_PARSE_RECEIPT.json").read_text())
        parent_ns = int(receipt["parent_cuda_interval_union_ns"])
        cuda = read_tsv(analysis_dir / f"{point}_CUDA_INTERVALS.tsv")
        by_family = defaultdict(list)
        for row in cuda:
            if row["semantic_family"]:
                by_family[row["semantic_family"]].append((int(row["kernel_start_ns"]), int(row["kernel_end_ns"])))
        gap_ns = int(receipt["positive_launch_gap_union_ns"])
        off_ms = float(summary_lookup[(point, "GRAPH_OFF")]["cuda_median_ms"])
        on_ms = float(summary_lookup[(point, "GRAPH_ON")]["cuda_median_ms"])
        estimator = config["graph_control_estimator"]
        if estimator == "OFF_MINUS_ON_OVER_GRAPH_OFF_POSITIVE_LAUNCH_GAP_UNION":
            absorbed = max(0.0, off_ms - on_ms) / (gap_ns / 1e6) if gap_ns else None
            graph_status = "STOP_DIRECTION" if absorbed is not None and absorbed >= 0.85 else "DIRECTION_SURVIVES_GRAPH_CONTROL"
        else:
            absorbed = None
            graph_status = "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE"
        for family_name, intervals in sorted(by_family.items()):
            family_ns = union_duration(intervals)
            f = family_ns / parent_ns if parent_ns else 0.0
            s_zero = 1.0 / (1.0 - f) if f < 1.0 else math.inf
            local_status = "PASS_LOCAL_3PCT" if f >= 0.03 else "STOP_LOCAL_LINE"
            ceiling_status = "PASS_ZERO_COST_2PCT" if s_zero - 1.0 >= 0.02 else "STOP_LINE"
            headroom_rows.append({
                "point": point, "family": family_name,
                "family_cuda_union_ns": family_ns, "parent_cuda_union_ns": parent_ns,
                "local_wall_weight": f, "s_zero": s_zero,
                "zero_cost_incremental_ceiling": s_zero - 1.0,
                "local_3pct_gate": local_status, "zero_cost_2pct_gate": ceiling_status,
                "graph_off_native_median_ms": off_ms, "graph_on_native_median_ms": on_ms,
                "graph_off_positive_launch_gap_union_ns": gap_ns,
                "graph_control_absorption_ratio": "" if absorbed is None else absorbed,
                "graph_control_status": graph_status,
                "interpretation": "OPTIMISTIC_GRAPH_OFF_SCREEN_NOT_REALIZABLE_SPEEDUP",
            })
    write_tsv(out / "POINT_HEADROOM_SCREEN.tsv", headroom_rows,
              ["point", "family", "family_cuda_union_ns", "parent_cuda_union_ns", "local_wall_weight", "s_zero", "zero_cost_incremental_ceiling", "local_3pct_gate", "zero_cost_2pct_gate", "graph_off_native_median_ms", "graph_on_native_median_ms", "graph_off_positive_launch_gap_union_ns", "graph_control_absorption_ratio", "graph_control_status", "interpretation"])

    material = [row for row in headroom_rows if row["local_3pct_gate"] == "PASS_LOCAL_3PCT" and row["zero_cost_2pct_gate"] == "PASS_ZERO_COST_2PCT"]
    question_rows = [
        {"question": "DQ1", "producer_precheck": "MATERIAL_LOCAL_FAMILIES" if any(row["point"] in ("MP01", "MP02") for row in material) else "STOP_LOCAL_OR_LINE", "evidence": "MP01;MP02 semantic CUDA interval unions", "claim_boundary": "Graph-OFF optimistic composition only"},
        {"question": "DQ2", "producer_precheck": "B1_B4_AND_AWQ_CONTROL_CAPTURED" if all(point in parsed_points for point in ("MP02", "MP03", "MP05")) else "PARTIAL", "evidence": "Graph ON/OFF medians; effective M; shapes; backend", "claim_boundary": "no causal utilization or precision claim"},
        {"question": "DQ3", "producer_precheck": "MEMORY_SERVICE_CANDIDATE" if material else "NO_MEMORY_SERVICE_CANDIDATE", "evidence": "material native exposure plus attention/projection layout clue", "claim_boundary": "no L1/L2/DRAM/TLB attribution; no NCU"},
        {"question": "DQ4a", "producer_precheck": "CHRONOLOGY_AVAILABLE" if all(point in parsed_points for point in ("MP01", "MP02")) else "PARTIAL", "evidence": "ordered semantic↔CUDA intervals and positive boundary gaps", "claim_boundary": "no handoff/cache/materialization mechanism"},
    ]
    write_tsv(out / "QUESTION_GATE_STATUS.tsv", question_rows,
              ["question", "producer_precheck", "evidence", "claim_boundary"])

    complete = all(row["status"] == "COMPLETE" for row in status_rows)
    final_status = "STAGEA_TIER0_PRODUCER_COMPLETE" if complete else "STAGEA_TIER0_PRODUCER_PARTIAL"
    final = {
        "status": final_status,
        "point_status": {row["point"]: row["status"] for row in status_rows},
        "all_authorized_points_complete": complete,
        "automatic_next_goal": False,
        "tier1_authorized": False,
        "holdout_executed": False,
        "olmoe_executed": False,
        "mechanism_implemented": False,
        "ncu_executed": False,
        "nvbit_executed": False,
        "sass_captured": False,
        "accel_sim_executed": False,
        "stop": True,
    }
    write_json(out / "FINAL_DECISION.json", final)
    lines = [
        "# Stage A dense-first Tier0 producer interpretation",
        "",
        f"Producer status: `{final_status}`.",
        "",
        "All native medians come only from instrumentation-OFF request-level CUDA Events. Observed/NSYS wall time is not scientific timing authority.",
        "",
        "Local-family fractions use correlated GPU interval unions inside the same Graph-OFF parent range. They are optimistic screening ceilings, not achieved or realizable speedups and not direct Graph-ON contributions.",
        "",
        "MP05 is a representation/runtime control, not a strict causal BF16/AWQ precision comparison. B1/B4 differences are reported without labeling their ratio as utilization gain.",
        "",
        "DQ3 remains candidate-level only: no L1/L2/DRAM/TLB bottleneck attribution is made without Tier1 authority. DQ4a reports chronology and gaps only, not a cache, handoff, materialization, or prefetch mechanism.",
        "",
        "No Tier1, holdout, OLMoE, NCU, NVBit, SASS, Accel-Sim, or mechanism work was started.",
    ]
    (out / "PRODUCER_INTERPRETATION.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(final, sort_keys=True))


if __name__ == "__main__":
    main()
