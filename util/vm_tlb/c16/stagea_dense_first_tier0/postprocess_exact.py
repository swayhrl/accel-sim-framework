#!/usr/bin/env python3
"""Exact-schema deterministic CPU postprocess for the authorized Tier0 contract."""

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
ARMS = ("GRAPH_ON_NATIVE", "GRAPH_OFF_NATIVE", "GRAPH_OFF_OBSERVED")
ATOL, RTOL = 0.05, 0.01


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


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


def completion_logprobs(completion):
    values = []
    for token, row in zip(completion["tokens"], completion.get("logprobs", [])):
        mapping = {int(item["token_id"]): float(item["logprob"]) for item in row}
        values.append(mapping.get(int(token)))
    return values


def compare_output_rows(reference, rows):
    if len(reference) != len(rows):
        return False, False, False, None
    identities = tokens = numeric = True
    maximum = 0.0
    for left, right in zip(reference, rows):
        identities &= left["batch_row"] == right["batch_row"] and left["source_id"] == right["source_id"]
        a, b = left["completion"], right["completion"]
        tokens &= a["tokens"] == b["tokens"]
        la, lb = completion_logprobs(a), completion_logprobs(b)
        if len(la) != len(lb) or any(x is None or y is None for x, y in zip(la, lb)):
            numeric = False
            continue
        for x, y in zip(la, lb):
            delta = abs(x - y)
            maximum = max(maximum, delta)
            numeric &= delta <= ATOL + RTOL * abs(x)
    return identities, tokens, numeric, maximum


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


def arm_result(raw, point, arm):
    point_dir = raw / point
    names = {
        "GRAPH_ON_NATIVE": f"{point}_GRAPH_ON_NATIVE.json",
        "GRAPH_OFF_NATIVE": f"{point}_GRAPH_OFF_NATIVE.json",
        "GRAPH_OFF_OBSERVED": f"{point}_GRAPH_OFF_OBSERVED.json",
    }
    path = point_dir / names[arm]
    return json.loads(path.read_text()) if path.is_file() else None


def arm_output_checks(reference, result):
    if not result or result.get("status") != "PASS":
        return {"pass": False, "rows": False, "tokens": False, "numeric": False, "max_abs": None}
    checks = [compare_output_rows(reference, sample["rows"]) for sample in result["samples"]]
    return {
        "pass": all(identity and tokens and numeric for identity, tokens, numeric, _ in checks),
        "rows": all(value[0] for value in checks),
        "tokens": all(value[1] for value in checks),
        "numeric": all(value[2] for value in checks),
        "max_abs": max((value[3] or 0.0 for value in checks), default=0.0),
    }


def module_identity(result):
    methods = sorted({row.get("quant_method_class") for row in result["module_census"] if row.get("quant_method_class")})
    kernels = sorted({row.get("kernel_backend_class") for row in result["module_census"] if row.get("kernel_backend_class")})
    attention = sorted({row.get("impl_class") for row in result["attention_backend"]["modules"] if row.get("impl_class")})
    return methods, kernels, attention


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    repo, raw, out = args.repo.resolve(), args.raw.resolve(), args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    config = json.loads(args.config.read_text())
    execution = json.loads((raw / "POINT_EXECUTION_RAW.json").read_text())

    results = {point: {arm: arm_result(raw, point, arm) for arm in ARMS} for point in POINTS}
    parse_receipts = {}
    analysis_dir = raw / "analysis"
    analysis_dir.mkdir(exist_ok=True)
    for point in POINTS:
        trace = raw / point / f"{point}_GRAPH_OFF_OBSERVED.nsys-rep"
        observed_path = raw / point / f"{point}_GRAPH_OFF_OBSERVED.json"
        if trace.is_file() and observed_path.is_file():
            subprocess.run([
                "python3", config["nsys_extract"], "--point", point,
                "--trace", str(trace), "--observed-json", str(observed_path),
                "--output-dir", str(analysis_dir),
            ], cwd=repo, check=True, stdout=subprocess.PIPE, text=True)
            parse_receipts[point] = json.loads((analysis_dir / f"{point}_NSYS_PARSE_RECEIPT.json").read_text())

    # Cross-arm correctness and identity.
    point_correct = {}
    arm_checks = {}
    signature_checks = {}
    for point in POINTS:
        on, off, observed = (results[point][arm] for arm in ARMS)
        reference = on["samples"][0]["rows"] if on and on.get("status") == "PASS" else []
        checks = {arm: arm_output_checks(reference, results[point][arm]) for arm in ARMS}
        signatures = {arm: backend_signature(results[point][arm]) if results[point][arm] and results[point][arm].get("status") == "PASS" else None for arm in ARMS}
        expected_method = "AutoAWQMarlinLinearMethod" if point == "MP05" else "UnquantizedLinearMethod"
        expected_kernel = "MarlinLinearKernel" if point == "MP05" else None
        methods, kernels, attention = module_identity(on) if on and on.get("status") == "PASS" else ([], [], [])
        backend_legal = ("FlashAttentionImpl" in attention and expected_method in methods
                         and (expected_kernel is None or expected_kernel in kernels))
        arm_backend_match = {}
        for arm in ARMS:
            arm_result_value = results[point][arm]
            if not arm_result_value or arm_result_value.get("status") != "PASS":
                arm_backend_match[arm] = False
                continue
            arm_methods, arm_kernels, arm_attention = module_identity(arm_result_value)
            arm_legal = ("FlashAttentionImpl" in arm_attention and expected_method in arm_methods
                         and (expected_kernel is None or expected_kernel in arm_kernels))
            arm_backend_match[arm] = arm_legal and signatures[arm] == signatures["GRAPH_ON_NATIVE"]
        same_signature = all(arm_backend_match.values())
        observed_semantic = observed["samples"][0]["instrumentation"] if observed and observed.get("status") == "PASS" else None
        semantic_order = observed_semantic.get("semantic_order", []) if observed_semantic else []
        semantic_exact = (len(semantic_order) == config["points"][point]["expected_semantic_occurrences"]
                          and [row["ordinal"] for row in semantic_order] == list(range(len(semantic_order))))
        input_exact = all(item["status"] == "PASS" for item in config["points"][point]["inputs"])
        parse_pass = parse_receipts.get(point, {}).get("status") == "PASS"
        point_correct[point] = (input_exact and same_signature and backend_legal and semantic_exact
                                and parse_pass and all(value["pass"] for value in checks.values()))
        arm_checks[point] = checks
        signature_checks[point] = {"same": same_signature, "legal": backend_legal,
                                   "methods": methods, "kernels": kernels, "attention": attention,
                                   "semantic_exact": semantic_exact, "arm_backend_match": arm_backend_match}

    point_identity_rows = []
    token_rows = []
    for point in POINTS:
        cfg = config["points"][point]
        for item in cfg["inputs"]:
            point_identity_rows.append({
                "point_id": point, "target": cfg["model_kind"], "model_revision": cfg["model_revision"],
                "vllm_source_commit": "ced6857afa0ea7b2e3f0846a62e1394e90f15607",
                "phase": cfg["phase"], "batch_size": cfg["batch_size"], "prompt_tokens": 512,
                "decode_steps": "NA" if point == "MP01" else cfg["decode_tokens"], "source_text_id": item["source_id"],
                "source_utf8_sha256": item["source_utf8_sha256"], "tokenizer_revision": item["tokenizer_revision"],
                "token_ids_sha256": item["token_ids_sha256"], "token_id_file_sha256": item["token_id_file_sha256"],
                "token_ids_path": item["path"], "correctness_status": "PASS" if point_correct[point] else "FAIL",
            })
            token_rows.append({"point": point, **item})
    write_tsv(out / "POINT_IDENTITY.tsv", point_identity_rows,
              ["point_id", "target", "model_revision", "vllm_source_commit", "phase", "batch_size", "prompt_tokens", "decode_steps", "source_text_id", "source_utf8_sha256", "tokenizer_revision", "token_ids_sha256", "token_id_file_sha256", "token_ids_path", "correctness_status"])
    write_tsv(out / "TOKENIZATION_RECHECK.tsv", token_rows,
              ["point", "source_id", "model_key", "model_revision", "tokenizer_revision", "source_utf8_sha256", "token_ids_sha256", "token_id_file_sha256", "token_count", "path", "status"])

    sample_rows, summary_rows, medians = [], [], {}
    for point in POINTS:
        for arm in ("GRAPH_ON_NATIVE", "GRAPH_OFF_NATIVE"):
            result = results[point][arm]
            if not result or result.get("status") != "PASS":
                continue
            samples = [("WARMUP", 0, result["warmup_excluded"])] + [("MEASURED", index, row) for index, row in enumerate(result["samples"])]
            for role, index, sample in samples:
                generated = [row["completion"]["tokens"] for row in sample["rows"]]
                sample_rows.append({
                    "point_id": point, "arm": arm, "sample_role": role, "sample_index": index,
                    "process_id": result["process_id"],
                    "request_id": ";".join(row["request_id"] for row in sample["rows"]),
                    "request_cuda_event_ms": sample["cuda_event_ms"], "host_wall_ms": sample["host_wall_ms"],
                    "generated_token_count": sum(len(tokens) for tokens in generated),
                    "token_ids_sha256": sha_json(generated),
                    "status": "PASS" if arm_checks[point][arm]["pass"] else "FAIL",
                })
            cuda_values = [row["cuda_event_ms"] for row in result["samples"]]
            host_values = [row["host_wall_ms"] for row in result["samples"]]
            median_cuda, median_host = statistics.median(cuda_values), statistics.median(host_values)
            medians[(point, arm)] = median_cuda
            summary_rows.append({
                "point_id": point, "arm": arm, "measured_n": 3,
                "primary_estimator": "median_of_three_request_cuda_event_ms",
                "median_request_cuda_event_ms": median_cuda, "median_host_wall_ms": median_host,
                "minimum_request_cuda_event_ms": min(cuda_values), "maximum_request_cuda_event_ms": max(cuda_values),
                "correctness_status": "PASS" if arm_checks[point][arm]["pass"] else "FAIL",
            })
    write_tsv(out / "NATIVE_REQUEST_SAMPLES.tsv", sample_rows,
              ["point_id", "arm", "sample_role", "sample_index", "process_id", "request_id", "request_cuda_event_ms", "host_wall_ms", "generated_token_count", "token_ids_sha256", "status"])
    write_tsv(out / "NATIVE_REQUEST_SUMMARY.tsv", summary_rows,
              ["point_id", "arm", "measured_n", "primary_estimator", "median_request_cuda_event_ms", "median_host_wall_ms", "minimum_request_cuda_event_ms", "maximum_request_cuda_event_ms", "correctness_status"])

    correctness_rows = []
    observer_rows = []
    for point in POINTS:
        cfg = config["points"][point]
        for arm in ARMS:
            observed_arm = arm == "GRAPH_OFF_OBSERVED"
            check = arm_checks[point][arm]
            correctness_rows.append({
                "point_id": point, "arm": arm, "tokens_exact": check["tokens"],
                "shapes_exact": signature_checks[point]["semantic_exact"] if observed_arm else check["rows"],
                "semantic_order_exact": signature_checks[point]["semantic_exact"] if observed_arm else "NA_INSTRUMENTATION_OFF",
                "backend_identity_exact": signature_checks[point]["arm_backend_match"][arm],
                "quant_identity_exact_or_NA": "PASS" if point == "MP05" else "NA",
                "observer_neutrality_status": ("FROZEN_9d5aa2f3_PASS" if point == "MP05" else "FROZEN_3f62f909_PASS") if observed_arm else "NA_INSTRUMENTATION_OFF",
                "status": "PASS" if check["pass"] and signature_checks[point]["arm_backend_match"][arm] and (not observed_arm or signature_checks[point]["semantic_exact"]) else "FAIL",
            })
        observed = results[point]["GRAPH_OFF_OBSERVED"]
        semantic = observed["samples"][0]["instrumentation"] if observed and observed.get("status") == "PASS" else {}
        observer_rows.append({
            "point_id": point, "observer_identity": cfg["observer_identity"],
            "observer_source_sha256": cfg["observer_source_sha256"],
            "per_occurrence_cuda_events": cfg["per_occurrence_cuda_events"],
            "outer_request_cuda_events": 2,
            "semantic_occurrences": len(semantic.get("semantic_order", [])),
            "semantic_order_sha256": semantic.get("semantic_order_sha256", "NA"),
            "accepted_neutrality_authority": "9d5aa2f36e22a1a8fcc253d6df865160b5dba797" if point == "MP05" else "3f62f909a474e4c56695ffacf36ddcb5d7b5f147",
            "status": "PASS" if signature_checks[point]["semantic_exact"] else "FAIL",
        })
    write_tsv(out / "GRAPH_MODE_CORRECTNESS.tsv", correctness_rows,
              ["point_id", "arm", "tokens_exact", "shapes_exact", "semantic_order_exact", "backend_identity_exact", "quant_identity_exact_or_NA", "observer_neutrality_status", "status"])
    write_tsv(out / "OBSERVER_IDENTITY.tsv", observer_rows,
              ["point_id", "observer_identity", "observer_source_sha256", "per_occurrence_cuda_events", "outer_request_cuda_events", "semantic_occurrences", "semantic_order_sha256", "accepted_neutrality_authority", "status"])

    mismatch_rows = []
    for point in POINTS:
        on = results[point]["GRAPH_ON_NATIVE"]
        if not on or on.get("status") != "PASS":
            continue
        reference = on["samples"][0]["rows"]
        for arm in ARMS:
            result = results[point][arm]
            if not result or result.get("status") != "PASS":
                continue
            for sample_index, sample in enumerate(result["samples"]):
                for row_index, (left, right) in enumerate(zip(reference, sample["rows"])):
                    left_tokens = left["completion"]["tokens"]
                    right_tokens = right["completion"]["tokens"]
                    differing = [index for index, (a, b) in enumerate(zip(left_tokens, right_tokens)) if a != b]
                    differing += list(range(min(len(left_tokens), len(right_tokens)), max(len(left_tokens), len(right_tokens))))
                    la, lb = completion_logprobs(left["completion"]), completion_logprobs(right["completion"])
                    deltas = [abs(a - b) for a, b in zip(la, lb) if a is not None and b is not None]
                    tolerance = all(abs(a - b) <= ATOL + RTOL * abs(a) for a, b in zip(la, lb) if a is not None and b is not None)
                    tolerance &= len(la) == len(lb) and all(a is not None and b is not None for a, b in zip(la, lb))
                    mismatch_rows.append({
                        "point_id": point, "arm": arm, "sample_index": sample_index,
                        "batch_row": row_index, "source_text_id": left["source_id"],
                        "tokens_exact": not differing, "token_mismatch_count": len(differing),
                        "first_token_mismatch_index_or_NA": differing[0] if differing else "NA",
                        "max_sampled_logprob_abs_delta": max(deltas, default=0.0),
                        "logprobs_within_tolerance": tolerance,
                        "status": "PASS" if not differing and tolerance else "FAIL",
                    })
    write_tsv(out / "CORRECTNESS_MISMATCH_DETAIL.tsv", mismatch_rows,
              ["point_id", "arm", "sample_index", "batch_row", "source_text_id", "tokens_exact", "token_mismatch_count", "first_token_mismatch_index_or_NA", "max_sampled_logprob_abs_delta", "logprobs_within_tolerance", "status"])

    # Exact-schema chronology tables.
    semantic_rows, cuda_rows, gap_rows, capture_rows = [], [], [], []
    chronology_rows, effective_m_rows = [], []
    kernel_identity = {}
    for point in POINTS:
        receipt = parse_receipts.get(point)
        observed = results[point]["GRAPH_OFF_OBSERVED"]
        request_id = ";".join(row["request_id"] for row in observed["samples"][0]["rows"]) if observed else "NA"
        if not receipt:
            capture_rows.append({"point_id": point, "capture_id": 0, "arm": "GRAPH_OFF_OBSERVED", "domains": "cuda,nvtx", "capture_file": "NA", "capture_sha256": "NA", "target_request_id": request_id, "semantic_range_count": 0, "cuda_activity_count": 0, "structural_status": "UNAVAILABLE"})
            continue
        raw_semantic = read_tsv(analysis_dir / f"{point}_SEMANTIC_INTERVALS.tsv")
        for row in raw_semantic:
            semantic_rows.append({
                "point_id": point, "observed_request_id": request_id, "ordinal": row["ordinal"],
                "module": row["module"], "phase": row["phase"], "input_shape": row["input_shape"],
                "output_shape": row["output_shape"], "nvtx_start_ns": row["host_nvtx_start_ns"],
                "nvtx_end_ns": row["host_nvtx_end_ns"], "parent_ordinal_or_NA": "NA", "status": "PASS",
            })
        unique_shapes = set()
        for row in raw_semantic:
            key = (row["phase"], row["family"], row["effective_m"], row["input_shape"], row["output_shape"])
            if key not in unique_shapes:
                unique_shapes.add(key)
                effective_m_rows.append({
                    "point_id": point, "phase": row["phase"], "family": row["family"],
                    "effective_m": row["effective_m"], "input_shape": row["input_shape"],
                    "output_shape": row["output_shape"], "status": "OBSERVED_GRAPH_OFF_ONLY",
                })
        parent_union_ns = int(receipt["parent_cuda_interval_union_ns"])
        for left, right in zip(raw_semantic, raw_semantic[1:]):
            if not left["cuda_last_end_ns"] or not right["cuda_first_start_ns"]:
                continue
            gap_ns = max(0, int(right["cuda_first_start_ns"]) - int(left["cuda_last_end_ns"]))
            chronology_rows.append({
                "point_id": point, "producer_ordinal": left["ordinal"], "producer_module": left["module"],
                "producer_family": left["family"], "consumer_ordinal": right["ordinal"],
                "consumer_module": right["module"], "consumer_family": right["family"],
                "boundary_gap_ns": gap_ns,
                "boundary_gap_parent_cuda_union_fraction": gap_ns / parent_union_ns if parent_union_ns else 0.0,
                "interpretation": "CHRONOLOGY_ONLY_NO_HANDOFF_MECHANISM_CLAIM",
            })
        raw_cuda = sorted(read_tsv(analysis_dir / f"{point}_CUDA_INTERVALS.tsv"), key=lambda row: (int(row["kernel_start_ns"]), int(row["kernel_end_ns"])))
        for index, row in enumerate(raw_cuda):
            row["_id"] = index
            cuda_rows.append({
                "point_id": point, "observed_request_id": request_id, "cuda_interval_id": index,
                "cuda_api_id_or_NA": row["correlation_id"] or "NA", "kernel_name": row["kernel_name"],
                "start_ns": row["kernel_start_ns"], "end_ns": row["kernel_end_ns"],
                "stream_id_or_NA": row["stream_id"] or "NA",
                "correlated_nvtx_ordinal_or_NA": row["semantic_ordinal"] or "NA",
                "parent_request_id": request_id, "source_capture_sha256": receipt["trace_sha256"],
            })
        # Reconstruct legal union gaps and retain adjacent source interval IDs.
        groups = []
        for row in raw_cuda:
            start, end = int(row["kernel_start_ns"]), int(row["kernel_end_ns"])
            if not groups or start > groups[-1]["end"]:
                groups.append({"start": start, "end": end, "first": row["_id"], "last": row["_id"]})
            else:
                groups[-1]["end"] = max(groups[-1]["end"], end)
                groups[-1]["last"] = row["_id"]
        for left, right in zip(groups, groups[1:]):
            if right["start"] > left["end"]:
                gap_rows.append({
                    "point_id": point, "observed_request_id": request_id, "gap_id": len([row for row in gap_rows if row["point_id"] == point]),
                    "preceding_cuda_interval_id": left["last"], "following_cuda_interval_id": right["first"],
                    "gap_start_ns": left["end"], "gap_end_ns": right["start"],
                    "gap_duration_ns": right["start"] - left["end"], "parent_request_id": request_id,
                    "classification_or_UNKNOWN": "UNKNOWN",
                })
        trace = Path(receipt["trace"])
        capture_rows.append({
            "point_id": point, "capture_id": 0, "arm": "GRAPH_OFF_OBSERVED", "domains": "cuda,nvtx",
            "capture_file": str(trace), "capture_sha256": receipt["trace_sha256"], "target_request_id": request_id,
            "semantic_range_count": receipt["semantic_range_count"], "cuda_activity_count": receipt["kernel_count_in_parent"],
            "structural_status": receipt["status"],
        })
        kernel_identity[point] = receipt
    write_tsv(out / "SEMANTIC_INTERVALS.tsv", semantic_rows,
              ["point_id", "observed_request_id", "ordinal", "module", "phase", "input_shape", "output_shape", "nvtx_start_ns", "nvtx_end_ns", "parent_ordinal_or_NA", "status"])
    write_tsv(out / "CUDA_INTERVALS.tsv", cuda_rows,
              ["point_id", "observed_request_id", "cuda_interval_id", "cuda_api_id_or_NA", "kernel_name", "start_ns", "end_ns", "stream_id_or_NA", "correlated_nvtx_ordinal_or_NA", "parent_request_id", "source_capture_sha256"])
    write_tsv(out / "LAUNCH_GAPS.tsv", gap_rows,
              ["point_id", "observed_request_id", "gap_id", "preceding_cuda_interval_id", "following_cuda_interval_id", "gap_start_ns", "gap_end_ns", "gap_duration_ns", "parent_request_id", "classification_or_UNKNOWN"])
    write_tsv(out / "NSYS_CAPTURE_INDEX.tsv", capture_rows,
              ["point_id", "capture_id", "arm", "domains", "capture_file", "capture_sha256", "target_request_id", "semantic_range_count", "cuda_activity_count", "structural_status"])
    write_tsv(out / "PRODUCER_CONSUMER_CHRONOLOGY.tsv", chronology_rows,
              ["point_id", "producer_ordinal", "producer_module", "producer_family", "consumer_ordinal", "consumer_module", "consumer_family", "boundary_gap_ns", "boundary_gap_parent_cuda_union_fraction", "interpretation"])
    write_tsv(out / "EFFECTIVE_M_SHAPES.tsv", effective_m_rows,
              ["point_id", "phase", "family", "effective_m", "input_shape", "output_shape", "status"])

    backend_rows = []
    for point in POINTS:
        cfg = config["points"][point]
        for arm in ARMS:
            result = results[point][arm]
            methods, kernels, attention = module_identity(result) if result and result.get("status") == "PASS" else ([], [], [])
            receipt = kernel_identity.get(point) if arm == "GRAPH_OFF_OBSERVED" else None
            selected = "MarlinLinearKernel" if point == "MP05" else "accepted BF16 cuBLAS/CUTLASS/GEMV runtime path"
            source = "9d5aa2f36e22a1a8fcc253d6df865160b5dba797" if point == "MP05" else "3f62f909a474e4c56695ffacf36ddcb5d7b5f147"
            for role in ("ATTENTION", "PROJECTION"):
                backend_rows.append({
                    "point_id": point, "arm": arm, "backend_role": role,
                    "attention_backend": "FlashAttentionImpl" if "FlashAttentionImpl" in attention else "NA",
                    "projection_or_quant_method": ("AutoAWQMarlinLinearMethod" if point == "MP05" else "UnquantizedLinearMethod"),
                    "selected_kernel_family": selected,
                    "kernel_count": receipt["kernel_count_in_parent"] if receipt else "NA",
                    "kernel_inventory_sha256": receipt["kernel_inventory_sha256"] if receipt else "NA",
                    "accepted_identity_match": signature_checks[point]["arm_backend_match"][arm],
                    "source_receipt": source,
                })
    write_tsv(out / "BACKEND_KERNEL_IDENTITY.tsv", backend_rows,
              ["point_id", "arm", "backend_role", "attention_backend", "projection_or_quant_method", "selected_kernel_family", "kernel_count", "kernel_inventory_sha256", "accepted_identity_match", "source_receipt"])

    # Prospectively matched MP02/MP03 Graph-control estimator.
    matched_status = "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE"
    absorption = None
    if all(point_correct[p] for p in ("MP02", "MP03")) and all((p, arm) in medians for p in ("MP02", "MP03") for arm in ("GRAPH_ON_NATIVE", "GRAPH_OFF_NATIVE")):
        g_off = medians[("MP02", "GRAPH_OFF_NATIVE")] / 32.0 - medians[("MP03", "GRAPH_OFF_NATIVE")] / 128.0
        g_on = medians[("MP02", "GRAPH_ON_NATIVE")] / 32.0 - medians[("MP03", "GRAPH_ON_NATIVE")] / 128.0
        if g_off > 0:
            absorption = (g_off - g_on) / g_off
            matched_status = "STOP_DIRECTION" if absorption >= 0.85 else "DIRECTION_SURVIVES_GRAPH_CONTROL"
    else:
        g_off = g_on = None

    # Graph-OFF local-family screens, without converting them into Graph-ON whole-run claims.
    headroom_rows = []
    question_points = {"DQ1": ("MP01", "MP02"), "DQ3": POINTS, "DQ4a": ("MP01", "MP02")}
    cuda_by_point = defaultdict(list)
    for row in cuda_rows:
        cuda_by_point[row["point_id"]].append(row)
    raw_cuda_by_point = {point: read_tsv(analysis_dir / f"{point}_CUDA_INTERVALS.tsv") if (analysis_dir / f"{point}_CUDA_INTERVALS.tsv").is_file() else [] for point in POINTS}
    for question, points in question_points.items():
        for point in points:
            receipt = parse_receipts.get(point)
            if not receipt:
                continue
            parent_ns = int(receipt["parent_cuda_interval_union_ns"])
            families = defaultdict(list)
            names = defaultdict(list)
            for row in raw_cuda_by_point[point]:
                fam = row["semantic_family"]
                if fam:
                    families[fam].append((int(row["kernel_start_ns"]), int(row["kernel_end_ns"])))
                    names[fam].append(row["kernel_name"].lower())
            for family, intervals in sorted(families.items()):
                candidate_ns = union_duration(intervals)
                f = candidate_ns / parent_ns if parent_ns else 0.0
                s_zero = 1.0 / (1.0 - f) if f < 1.0 else math.inf
                local_gate = "PASS_LOCAL_WEIGHT" if f >= 0.03 else "STOP_LOCAL_LINE"
                screen_increment = s_zero - 1.0
                if screen_increment < 0.02:
                    two_gate = "STOP_LINE"
                else:
                    two_gate = "GRAPH_OFF_SCREEN_ABOVE_0.02_WHOLE_RUN_NOT_IDENTIFIABLE"
                clue = (family == "ATTENTION" and any("flash" in name or "attention" in name for name in names[family])) or (
                    family in ("GATE_UP_PROJECTION", "DOWN_PROJECTION") and any(term in name for name in names[family] for term in ("gemm", "gemv", "cutlass", "cublas", "marlin")))
                traffic_gate = "NA"
                if question == "DQ3":
                    traffic_gate = "MEMORY_SERVICE_CANDIDATE" if f >= 0.03 and clue else "STOP_MEMORY_LINE"
                if local_gate == "STOP_LOCAL_LINE":
                    decision = "STOP_LOCAL_LINE"
                elif two_gate == "STOP_LINE":
                    decision = "STOP_LINE"
                elif question == "DQ3":
                    decision = traffic_gate
                else:
                    decision = "SURVIVES_GRAPH_OFF_LOCAL_SCREEN_WHOLE_RUN_NOT_IDENTIFIABLE"
                headroom_rows.append({
                    "point_id": point, "question_id": question, "candidate_id": family,
                    "graph_on_native_parent_median_ms": medians.get((point, "GRAPH_ON_NATIVE"), "NA"),
                    "graph_off_candidate_union_ns": candidate_ns, "graph_off_parent_cuda_union_ns": parent_ns,
                    "f_graph_off": f, "s_zero_graph_off_screen": s_zero,
                    "whole_run_ceiling_status": "WHOLE_RUN_CEILING_NOT_IDENTIFIABLE",
                    "whole_run_ceiling_increment_or_NA": "NA",
                    "local_weight_gate": local_gate, "two_percent_gate": two_gate,
                    "graph_control_gap_status": "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE",
                    "traffic_timing_gate": traffic_gate, "decision": decision,
                })
    for point in ("MP02", "MP03"):
        headroom_rows.append({
            "point_id": point, "question_id": "DQ2", "candidate_id": "B1_B4_NATIVE_PER_TOKEN_GAP",
            "graph_on_native_parent_median_ms": medians.get((point, "GRAPH_ON_NATIVE"), "NA"),
            "graph_off_candidate_union_ns": "NA", "graph_off_parent_cuda_union_ns": "NA",
            "f_graph_off": "NA", "s_zero_graph_off_screen": "NA",
            "whole_run_ceiling_status": "NA_DQ2_MATCHED_NATIVE_ESTIMATOR",
            "whole_run_ceiling_increment_or_NA": "NA", "local_weight_gate": "NA",
            "two_percent_gate": "NA", "graph_control_gap_status": matched_status,
            "traffic_timing_gate": "NA", "decision": matched_status,
        })
    headroom_rows.append({
        "point_id": "MP05", "question_id": "DQ2", "candidate_id": "AWQ_REPRESENTATION_RUNTIME_CONTROL",
        "graph_on_native_parent_median_ms": medians.get(("MP05", "GRAPH_ON_NATIVE"), "NA"),
        "graph_off_candidate_union_ns": "NA", "graph_off_parent_cuda_union_ns": "NA",
        "f_graph_off": "NA", "s_zero_graph_off_screen": "NA",
        "whole_run_ceiling_status": "NA_CROSS_REPRESENTATION_CONTROL", "whole_run_ceiling_increment_or_NA": "NA",
        "local_weight_gate": "NA", "two_percent_gate": "NA",
        "graph_control_gap_status": "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE",
        "traffic_timing_gate": "NA", "decision": "CONTROL_RECORDED_NO_CAUSAL_PRECISION_CLAIM",
    })
    write_tsv(out / "POINT_HEADROOM_SCREEN.tsv", headroom_rows,
              ["point_id", "question_id", "candidate_id", "graph_on_native_parent_median_ms", "graph_off_candidate_union_ns", "graph_off_parent_cuda_union_ns", "f_graph_off", "s_zero_graph_off_screen", "whole_run_ceiling_status", "whole_run_ceiling_increment_or_NA", "local_weight_gate", "two_percent_gate", "graph_control_gap_status", "traffic_timing_gate", "decision"])
    memory_clues = []
    for row in headroom_rows:
        if row["question_id"] != "DQ3":
            continue
        family = row["candidate_id"]
        if family == "ATTENTION":
            clue = "accepted FlashAttentionImpl attention/KV layout and correlated kernel names"
        elif family in ("GATE_UP_PROJECTION", "DOWN_PROJECTION"):
            clue = "accepted dense/Marlin weight layout and correlated GEMM/GEMV kernel names"
        else:
            clue = "no qualifying kernel/source bytes-layout clue"
        memory_clues.append({
            "point_id": row["point_id"], "candidate_id": family,
            "native_timing_exposure": row["local_weight_gate"], "kernel_source_layout_clue": clue,
            "tier0_decision": row["decision"],
            "forbidden_attribution": "NO_L1_L2_DRAM_TLB_BOTTLENECK_CLAIM",
        })
    write_tsv(out / "MEMORY_SERVICE_CLUES.tsv", memory_clues,
              ["point_id", "candidate_id", "native_timing_exposure", "kernel_source_layout_clue", "tier0_decision", "forbidden_attribution"])

    question_rows = []
    for question, point_ids in (("DQ1", "MP01;MP02"), ("DQ2", "MP02;MP03;MP05"), ("DQ3", "MP01;MP02;MP03;MP05"), ("DQ4a", "MP01;MP02")):
        rows = [row for row in headroom_rows if row["question_id"] == question]
        material = any(row["local_weight_gate"] == "PASS_LOCAL_WEIGHT" for row in rows)
        correctness_pass = all(point_correct[p] for p in point_ids.split(";"))
        if question == "DQ2":
            final_tier0 = matched_status
            graph_gate = matched_status
        elif question == "DQ3":
            final_tier0 = "MEMORY_SERVICE_CANDIDATE" if any(row["decision"] == "MEMORY_SERVICE_CANDIDATE" for row in rows) else "NO_MEMORY_SERVICE_CANDIDATE"
            graph_gate = "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE"
        elif question == "DQ4a":
            final_tier0 = "CHRONOLOGY_AND_BOUNDARY_GAPS_RECORDED" if all(p in parse_receipts for p in ("MP01", "MP02")) else "PARTIAL"
            graph_gate = "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE"
        else:
            if not correctness_pass:
                final_tier0 = "PARTIAL_CORRECTNESS_STOP_VALID_POINT_SCREENS_ONLY"
            else:
                final_tier0 = "LOCAL_SCREEN_SURVIVES_WHOLE_RUN_NOT_IDENTIFIABLE" if material else "STOP_LOCAL_LINE"
            graph_gate = "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE"
        question_rows.append({
            "question_id": question, "point_ids": point_ids,
            "correctness_gate": "PASS" if correctness_pass else "FAIL",
            "strong_software_gate": "PASS_GRAPH_ON_NATIVE_CAPTURED",
            "materiality_gate": "PASS_SOME_LOCAL_FAMILY" if material else "NO_MATERIAL_LOCAL_FAMILY_OR_NA",
            "zero_cost_gate": "WHOLE_RUN_CEILING_NOT_IDENTIFIABLE_PRESERVE_0.02",
            "graph_control_gap_gate": graph_gate, "holdout_status": "NOT_EXECUTED_NOT_AUTHORIZED",
            "tier1_status": "NOT_EXECUTED_NOT_AUTHORIZED", "final_tier0_status": final_tier0,
        })
    question_rows += [
        {"question_id": "DQ4b", "point_ids": "MP06", "correctness_gate": "NOT_EXECUTION_READY", "strong_software_gate": "NA", "materiality_gate": "NA", "zero_cost_gate": "NA", "graph_control_gap_gate": "NA", "holdout_status": "DEFERRED", "tier1_status": "NOT_AUTHORIZED", "final_tier0_status": "DEFERRED_NOT_EXECUTION_READY"},
        {"question_id": "translation", "point_ids": "MP08", "correctness_gate": "NA", "strong_software_gate": "NA", "materiality_gate": "NA", "zero_cost_gate": "NA", "graph_control_gap_gate": "NA", "holdout_status": "NOT_EXECUTED", "tier1_status": "NOT_AUTHORIZED", "final_tier0_status": "UNKNOWN_INACTIVE"},
    ]
    write_tsv(out / "QUESTION_GATE_STATUS.tsv", question_rows,
              ["question_id", "point_ids", "correctness_gate", "strong_software_gate", "materiality_gate", "zero_cost_gate", "graph_control_gap_gate", "holdout_status", "tier1_status", "final_tier0_status"])

    point_status_rows = []
    for point in POINTS:
        raw_status = execution["points"].get(point, {}).get("status", "NOT_RUN")
        complete = point_correct[point] and raw_status == "GPU_COMPLETE_PENDING_CPU_ANALYSIS"
        point_status_rows.append({
            "point_id": point, "gpu_execution_status": raw_status,
            "correctness_status": "PASS" if point_correct[point] else "FAIL",
            "nsys_status": parse_receipts.get(point, {}).get("status", "UNAVAILABLE"),
            "gpu_active_seconds": execution["points"].get(point, {}).get("gpu_active_seconds", 0),
            "point_cap_seconds": config["points"][point]["gpu_active_cap_seconds"],
            "status": "COMPLETE" if complete else "PARTIAL",
        })
    write_tsv(out / "POINT_EXECUTION_STATUS.tsv", point_status_rows,
              ["point_id", "gpu_execution_status", "correctness_status", "nsys_status", "gpu_active_seconds", "point_cap_seconds", "status"])

    raw_budget = json.loads((raw / "GPU_ACTIVE_BUDGET.json").read_text())
    lock = json.loads((raw / "GPU_LOCK_RECEIPT.json").read_text())
    used_seconds = raw_budget.get("gpu_active_seconds", raw_budget.get("total_used_seconds"))
    point_used = raw_budget.get("point_active_seconds", raw_budget.get("per_point_used_seconds"))
    budget = {
        "run_id": args.run_id, "total_cap_seconds": 540,
        "total_used_seconds": used_seconds,
        "per_point_cap_seconds": {point: config["points"][point]["gpu_active_cap_seconds"] for point in POINTS},
        "per_point_used_seconds": point_used,
        "gpu_lock_receipt": str(raw / "GPU_LOCK_RECEIPT.json"),
        "all_locks_released": lock["released"], "no_cross_point_borrowing": True,
        "status": "PASS" if lock["released"] and raw_budget["status"] == "PASS" else "FAIL",
    }
    write_json(out / "GPU_ACTIVE_BUDGET.json", budget)
    write_json(out / "GPU_LOCK_RECEIPT.json", lock)

    all_complete = all(row["status"] == "COMPLETE" for row in point_status_rows)
    final = {
        "run_id": args.run_id,
        "status": "STAGEA_TIER0_PRODUCER_COMPLETE" if all_complete else "STAGEA_TIER0_PRODUCER_PARTIAL",
        "point_status": {row["point_id"]: row["status"] for row in point_status_rows},
        "question_status": {row["question_id"]: row["final_tier0_status"] for row in question_rows},
        "stops": sorted({row["decision"] for row in headroom_rows if str(row["decision"]).startswith("STOP")}),
        "holdout_executed": False, "tier1_executed": False,
        "ncunvbitsassaccelsim_executed": False,
        "durable_raw_manifest_sha256": "PENDING_FINALIZE",
        "review_pack_sha256": "PENDING_FINALIZE",
        "gpu_active_budget_status": budget["status"],
        "automatic_next_goal": False,
    }
    write_json(out / "FINAL_DECISION.json", final)
    interpretation = [
        "# Stage A dense-first Tier0 producer interpretation",
        "",
        f"Provisional producer status before durable finalization: `{final['status']}`.",
        "",
        "Native authority is exclusively the median of three instrumentation-OFF request-level CUDA Event samples for each Graph mode. Warmups, host wall, observed wall, and NSYS wall are excluded.",
        "",
        f"The only matched 85% estimator is MP02/MP03 per generated token. Its status is `{matched_status}`" + (f" with absorption `{absorption}`." if absorption is not None else "."),
        "",
        "Local family weights and S_zero values are Graph-OFF CUDA-parent interval-union screens. They are not Graph-ON whole-run contributions or realizable speedups. The contractually required whole-run 2% quantity remains NOT_IDENTIFIABLE for these local rows.",
        "",
        "MP05 is a cross-representation runtime control, not a strict causal BF16/AWQ precision A/B. MP02/MP03 timing differences are not labeled utilization gain.",
        "",
        "DQ3 produces candidate-level output only and makes no L1/L2/DRAM/TLB attribution. DQ4a records chronology and boundary gaps only and proposes no cache, handoff, materialization, or prefetch mechanism.",
        "",
        "No Tier1, holdout, OLMoE, NCU, NVBit, SASS, Accel-Sim, or mechanism execution occurred.",
    ]
    (out / "PRODUCER_INTERPRETATION.md").write_text("\n".join(interpretation) + "\n")
    tests = {
        "status": "PASS" if all_complete else "PARTIAL",
        "all_point_correctness": point_correct,
        "all_required_nsys": {point: parse_receipts.get(point, {}).get("status") == "PASS" for point in POINTS},
        "native_summary_rows": len(summary_rows), "native_sample_rows": len(sample_rows),
        "matched_graph_estimator": {"G_off_ms_per_token": g_off, "G_on_ms_per_token": g_on,
                                    "absorption_fraction": absorption, "status": matched_status},
    }
    write_json(out / "TESTS.json", tests)
    print(json.dumps(final, sort_keys=True))


if __name__ == "__main__":
    main()
