#!/usr/bin/env python3
"""Deterministic qualification-only postprocess; no performance conclusions."""

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path


TARGETS = ("QWEN_BF16", "QWEN_AWQ", "OLMOE")
TOL = {key: {"atol": 0.05, "rtol": 0.01} for key in TARGETS}


def load(path):
    return json.loads(path.read_text()) if path.is_file() else None


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_tsv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=tuple(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def compare_outputs(left, right, target):
    if left is None or right is None:
        return {"pass": False, "reason": "MISSING_OUTPUT"}
    token_equal = left["tokens"] == right["tokens"]
    route_equal = left.get("routed_experts") == right.get("routed_experts")
    a, b = left.get("logprobs", []), right.get("logprobs", [])
    structure = len(a) == len(b) == len(left["tokens"])
    max_abs = 0.0
    numeric = structure
    if structure:
        for sampled_token, ra, rb in zip(left["tokens"], a, b):
            ma = {x["token_id"]: x["logprob"] for x in ra}
            mb = {x["token_id"]: x["logprob"] for x in rb}
            if sampled_token not in ma or sampled_token not in mb:
                numeric = False; break
            delta = abs(ma[sampled_token] - mb[sampled_token])
            max_abs = max(max_abs, delta)
            if delta > TOL[target]["atol"] + TOL[target]["rtol"] * abs(ma[sampled_token]):
                numeric = False
    return {"pass": token_equal and route_equal and structure and numeric,
            "tokens_exact": token_equal, "routing_exact": route_equal,
            "sampled_logprob_present_each_step": structure, "logprob_within_tolerance": numeric,
            "max_logprob_abs": max_abs, **TOL[target]}


def flatten_routes(value):
    if value is None:
        return []
    if isinstance(value, list):
        out = []
        for item in value:
            out.extend(flatten_routes(item))
        return out
    return [int(value)]


def backend_signature(data):
    if not data:
        return None
    modules = []
    for row in data["module_census"]:
        modules.append((row["module_class"], row["quant_method_class"], row["kernel_backend_class"],
                        json.dumps(row["parameter_shapes"], sort_keys=True)))
    attention = sorted((row["module_class"], row["impl_class"]) for row in data["attention_backend"]["modules"])
    groups = sorted((row["group_class"], row["backend_class"]) for row in data["attention_backend"]["runner_groups"])
    return {"modules": sorted(modules), "attention": attention, "groups": groups}


def med(values):
    return statistics.median(values)


def compact_run(data, path):
    if data is None:
        return {"status": "NOT_RUN", "raw_path": str(path)}
    profiler = {}
    for arm, row in data.get("profiler", {}).items():
        profiler[arm] = {"kernel_count": row["kernel_count"],
                         "kernel_inventory_sha256": row["kernel_inventory_sha256"],
                         "kernel_sequence_sha256": row["kernel_sequence_sha256"],
                         "tokens": row["output"]["tokens"],
                         "logprobs_sha256": row["output"]["logprobs_sha256"],
                         "routing_sha256": row["output"]["routing_sha256"]}
    native = [{"arm": row["arm"], "host_wall_ms": row["host_wall_ms"],
               "cuda_event_ms": row["cuda_event_ms"], "tokens": row["output"]["tokens"],
               "logprobs_sha256": row["output"]["logprobs_sha256"],
               "routing_sha256": row["output"]["routing_sha256"]}
              for row in data.get("native_runs", [])]
    return {"status": data.get("status"), "error_type": data.get("error_type"),
            "error": data.get("error"), "oom": data.get("oom", False),
            "model_revision": data.get("model_revision"), "vllm_config": data.get("vllm_config"),
            "attention_backend": data.get("attention_backend"),
            "module_backend_signature": backend_signature(data),
            "semantic_module_names": data.get("semantic_module_names"),
            "native_runs": native, "profiler": profiler, "vram": data.get("vram"),
            "raw_path": str(path), "raw_sha256": file_sha(path) if path.is_file() else None}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    correctness_rows = []
    neutrality_rows = []
    backend_rows = []
    vram_rows = []
    receipts = {}
    readiness = {}
    for target in TARGETS:
        off = load(args.raw / f"{target}_off.json")
        on = load(args.raw / f"{target}_on.json")
        off_pass = bool(off and off.get("status") == "PASS")
        on_pass = bool(on and on.get("status") == "PASS")
        blocker = None
        instr = {"pass": False, "reason": "GRAPH_OFF_FAILED"}
        graph = {"pass": False, "reason": "GRAPH_CONDITION_MISSING"}
        if off_pass:
            off_runs = [row for row in off["native_runs"] if row["arm"] == "OFF"]
            on_runs = [row for row in off["native_runs"] if row["arm"] == "ON"]
            all_outputs = [row["output"] for row in off_runs + on_runs]
            output_checks = [compare_outputs(all_outputs[0], row, target) for row in all_outputs[1:]]
            prof_compare = compare_outputs(off["profiler"]["OFF"]["output"], off["profiler"]["ON"]["output"], target)
            inventory_equal = off["profiler"]["OFF"]["kernel_inventory"] == off["profiler"]["ON"]["kernel_inventory"]
            host_off, host_on = med([row["host_wall_ms"] for row in off_runs]), med([row["host_wall_ms"] for row in on_runs])
            cuda_off, cuda_on = med([row["cuda_event_ms"] for row in off_runs]), med([row["cuda_event_ms"] for row in on_runs])
            host_limit, cuda_limit = max(5.0, .10 * host_off), max(5.0, .10 * cuda_off)
            host_neutral = abs(host_on - host_off) <= host_limit
            cuda_neutral = abs(cuda_on - cuda_off) <= cuda_limit
            semantic = next((row["instrumentation"] for row in on_runs if row["instrumentation"]), None)
            instr = {"pass": all(x["pass"] for x in output_checks) and prof_compare["pass"] and inventory_equal and host_neutral and cuda_neutral and semantic is not None,
                     "native_output_checks": output_checks, "profiled_output_check": prof_compare,
                     "kernel_inventory_exact": inventory_equal,
                     "off_kernel_inventory_sha256": off["profiler"]["OFF"]["kernel_inventory_sha256"],
                     "on_kernel_inventory_sha256": off["profiler"]["ON"]["kernel_inventory_sha256"],
                     "host_off_median_ms": host_off, "host_on_median_ms": host_on,
                     "host_abs_delta_ms": abs(host_on-host_off), "host_limit_ms": host_limit, "host_neutral": host_neutral,
                     "cuda_off_median_ms": cuda_off, "cuda_on_median_ms": cuda_on,
                     "cuda_abs_delta_ms": abs(cuda_on-cuda_off), "cuda_limit_ms": cuda_limit, "cuda_neutral": cuda_neutral,
                     "semantic_order_sha256": semantic["semantic_order_sha256"] if semantic else None,
                     "semantic_occurrences": len(semantic["semantic_order"]) if semantic else 0}
        if off_pass and on_pass:
            left = next(row["output"] for row in off["native_runs"] if row["arm"] == "OFF")
            right = on["native_runs"][0]["output"]
            values = compare_outputs(left, right, target)
            backend_equal = backend_signature(off) == backend_signature(on)
            left_routes = flatten_routes(left.get("routed_experts"))
            right_routes = flatten_routes(right.get("routed_experts"))
            route_mismatches = (sum(a != b for a, b in zip(left_routes, right_routes))
                                + abs(len(left_routes) - len(right_routes)))
            graph = {**values, "pass": values["pass"] and backend_equal,
                     "backend_identity_exact": backend_equal,
                     "routing_value_count_off": len(left_routes),
                     "routing_value_count_on": len(right_routes),
                     "routing_mismatch_count": route_mismatches,
                     "graph_off_kernel_inventory_sha256": off["profiler"]["OFF"]["kernel_inventory_sha256"],
                     "graph_on_kernel_inventory_sha256": on["profiler"]["GRAPH_ON"]["kernel_inventory_sha256"],
                     "semantic_order_contract": "same vLLM model modules; graph ON compiled replay, hooks not injected"}
        elif off and off.get("oom"):
            blocker = "OLMOE_GRAPH_OFF_VRAM_FAILED" if target == "OLMOE" else "GRAPH_OFF_VRAM_FAILED"
        elif off_pass and on and on.get("oom"):
            blocker = "OLMOE_GRAPH_ON_VRAM_QUALIFICATION_FAILED" if target == "OLMOE" else "GRAPH_ON_VRAM_QUALIFICATION_FAILED"
        else:
            blocker = "RUNTIME_OR_GRAPH_CONDITION_FAILED"
        if off_pass and on_pass and not graph["pass"]:
            blocker = "CORRECTNESS_OR_BACKEND_IDENTITY_FAILED"
        if off_pass and not instr["pass"] and blocker is None:
            blocker = "INSTRUMENTATION_NON_NEUTRAL"
        target_ready = off_pass and on_pass and graph["pass"] and instr["pass"]
        if not target_ready and blocker is None:
            blocker = "CORRECTNESS_OR_BACKEND_IDENTITY_FAILED"
        readiness[target] = {"ready": target_ready, "blocker": blocker}
        correctness_rows.append({"target": target, "graph_off_status": off.get("status") if off else "NOT_RUN",
                                 "graph_on_status": on.get("status") if on else "NOT_RUN",
                                 "tokens_exact": graph.get("tokens_exact", False),
                                 "routing_exact": graph.get("routing_exact", False),
                                 "routing_mismatch_count": graph.get("routing_mismatch_count", ""),
                                 "logprob_within_tolerance": graph.get("logprob_within_tolerance", False),
                                 "max_logprob_abs": graph.get("max_logprob_abs", ""),
                                 "backend_identity_exact": graph.get("backend_identity_exact", False),
                                 "status": "PASS" if graph["pass"] else blocker})
        neutrality_rows.append({"target": target, "kernel_inventory_exact": instr.get("kernel_inventory_exact", False),
                                "tokens_shapes_routing_exact": all(x.get("pass", False) for x in instr.get("native_output_checks", [])),
                                "host_off_median_ms": instr.get("host_off_median_ms", ""),
                                "host_on_median_ms": instr.get("host_on_median_ms", ""),
                                "host_abs_delta_ms": instr.get("host_abs_delta_ms", ""),
                                "host_limit_ms": instr.get("host_limit_ms", ""),
                                "cuda_off_median_ms": instr.get("cuda_off_median_ms", ""),
                                "cuda_on_median_ms": instr.get("cuda_on_median_ms", ""),
                                "cuda_abs_delta_ms": instr.get("cuda_abs_delta_ms", ""),
                                "cuda_limit_ms": instr.get("cuda_limit_ms", ""),
                                "semantic_occurrences": instr.get("semantic_occurrences", 0),
                                "status": "PASS" if instr["pass"] else "INSTRUMENTATION_NON_NEUTRAL"})
        for mode, data in (("off", off), ("on", on)):
            if not data:
                continue
            v = data.get("vram", {})
            vram_rows.append({"target": target, "graph_mode": mode, "load_status": data["status"],
                              "oom": data.get("oom", False), "after_load_mib": v.get("after_load_mib", ""),
                              "steady_mib": v.get("steady_after_canary_mib", ""),
                              "torch_peak_allocated_bytes": v.get("torch_peak_allocated_bytes", ""),
                              "torch_peak_reserved_bytes": v.get("torch_peak_reserved_bytes", "")})
            if data.get("status") == "PASS":
                prof_key = "OFF" if mode == "off" else "GRAPH_ON"
                prof = data["profiler"][prof_key]
                sig = backend_signature(data)
                kernels = list(prof["kernel_inventory"])
                backend_rows.append({"target": target, "graph_mode": mode,
                                     "attention_backend": json.dumps(sig["attention"] + sig["groups"], separators=(",", ":")),
                                     "module_kernel_backends": json.dumps(sorted(set(((x[1] or ""), (x[2] or "")) for x in sig["modules"])), separators=(",", ":")),
                                     "cuda_kernel_count": prof["kernel_count"],
                                     "kernel_inventory_sha256": prof["kernel_inventory_sha256"],
                                     "representative_kernel_names": json.dumps(kernels[:20], separators=(",", ":")),
                                     "evidence": "runtime object selection plus qualification-only torch CUDA activity inventory"})
        off_path = args.raw / f"{target}_off.json"
        on_path = args.raw / f"{target}_on.json"
        receipts[target] = {"target": target, "status": "RUNTIME_READY" if target_ready else "BLOCKED",
                            "blocker": blocker, "graph_off": off, "graph_on": on,
                            "instrumentation_neutrality": instr, "graph_off_on_correctness": graph,
                            "performance_use": "NONE_QUALIFICATION_DIAGNOSTIC_ONLY"}
        receipts[target]["graph_off"] = compact_run(off, off_path)
        receipts[target]["graph_on"] = compact_run(on, on_path)
        (args.output_dir / f"{target}_RUNTIME_RECEIPT.json").write_text(json.dumps(receipts[target], indent=2, sort_keys=True) + "\n")
    write_tsv(args.output_dir / "GRAPH_OFF_ON_CORRECTNESS.tsv", correctness_rows)
    write_tsv(args.output_dir / "INSTRUMENTATION_NEUTRALITY.tsv", neutrality_rows)
    write_tsv(args.output_dir / "ACTUAL_BACKEND_KERNEL_IDENTITY.tsv", backend_rows if backend_rows else [{"target":"NONE","graph_mode":"NONE","attention_backend":"","module_kernel_backends":"","cuda_kernel_count":0,"kernel_inventory_sha256":"","representative_kernel_names":"","evidence":"no successful runtime"}])
    write_tsv(args.output_dir / "VRAM_OBSERVATION.tsv", vram_rows if vram_rows else [{"target":"NONE","graph_mode":"NONE","load_status":"NOT_RUN","oom":"","after_load_mib":"","steady_mib":"","torch_peak_allocated_bytes":"","torch_peak_reserved_bytes":""}])
    point_map = [("MP01","QWEN_BF16"),("MP02","QWEN_BF16"),("MP03","QWEN_BF16"),("MP05","QWEN_AWQ"),("MP06","OLMOE")]
    point_rows = [{"point_id": point, "runtime_target": target,
                   "status": "RUNTIME_READY" if readiness[target]["ready"] else "BLOCKED",
                   "blocker": readiness[target]["blocker"] or "NONE"} for point, target in point_map]
    write_tsv(args.output_dir / "STAGEA_POINT_RUNTIME_READINESS.tsv", point_rows)
    ready_count = sum(row["status"] == "RUNTIME_READY" for row in point_rows)
    decision = ("RUNTIME_QUALIFICATION_PASS_STAGEA_REVIEW_READY" if ready_count == 5 else
                "RUNTIME_QUALIFICATION_FAILED" if ready_count == 0 else "RUNTIME_QUALIFICATION_PARTIAL")
    final = {"status": decision, "runtime_ready_points": ready_count, "point_count": 5,
             "target_readiness": readiness,
             "stagea_tier0_contract_condition": "STAGEA_TIER0_CONTRACT_CAN_NOW_BE_PREPARED_FOR_PROJECT_REVIEW" if ready_count == 5 else "BLOCKED_PENDING_PROJECT_REVIEW",
             "scientific_performance_conclusion": None, "automatic_next_goal": False,
             "holdout_outputs_generated": False}
    (args.output_dir / "FINAL_DECISION.json").write_text(json.dumps(final, indent=2, sort_keys=True) + "\n")
    print(json.dumps(final, sort_keys=True))


if __name__ == "__main__":
    main()
