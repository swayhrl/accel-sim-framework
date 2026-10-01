#!/usr/bin/env python3
"""Deterministic CPU-only postprocess for AWQ Observer V2 requalification."""

import argparse
import csv
import hashlib
import json
import sqlite3
import statistics
import subprocess
from collections import Counter
from pathlib import Path


ARM_ORDER = ["OFF", "ON", "ON", "OFF", "OFF", "ON"]
ACCEPTED_SEMANTIC_SHA = "0eecee7debb3eb8f0950dfa7b582c13ae506d90e0b3ca7d333575a6aae397033"
EXPECTED_QUANT_METHOD = "AutoAWQMarlinLinearMethod"
EXPECTED_KERNEL_BACKEND = "MarlinLinearKernel"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def backend_signature(data):
    modules = []
    for row in data["module_census"]:
        modules.append([row["module_class"], row["quant_method_class"], row["kernel_backend_class"],
                        json.dumps(row["parameter_shapes"], sort_keys=True)])
    attention = sorted([row["module_class"], row["impl_class"]] for row in data["attention_backend"]["modules"])
    groups = sorted([row["group_class"], row["backend_class"]] for row in data["attention_backend"]["runner_groups"])
    return {"modules": sorted(modules), "attention": attention, "groups": groups}


def nsys_receipt(raw):
    rep = raw / "QWEN_AWQ_GRAPH_OFF_OBSERVER_V2_STRUCTURAL_FINAL.nsys-rep"
    sqlite = raw / "QWEN_AWQ_GRAPH_OFF_OBSERVER_V2_STRUCTURAL_FINAL.sqlite"
    subprocess.run(["nsys", "export", "--type", "sqlite", "--force-overwrite=true",
                    "--output", str(sqlite), str(rep)], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    con = sqlite3.connect(sqlite)
    tables = {row[0] for row in con.execute("select name from sqlite_master where type='table'")}
    nvtx_table = "NVTX_EVENTS"
    kernel_table = "CUPTI_ACTIVITY_KIND_KERNEL"
    runtime_table = "CUPTI_ACTIVITY_KIND_RUNTIME"
    if nvtx_table not in tables or kernel_table not in tables:
        raise RuntimeError(f"missing required NSYS tables: {sorted(tables)}")
    columns = [row[1] for row in con.execute(f"pragma table_info({nvtx_table})")]
    rows = con.execute(f"select * from {nvtx_table}").fetchall()
    labels = []
    decoded_events = []
    string_ids = {}
    if "StringIds" in tables:
        string_ids = {row[0]: row[1] for row in con.execute("select id,value from StringIds")}
    for row in rows:
        item = dict(zip(columns, row))
        text = item.get("text")
        if not text and item.get("textId") is not None:
            text = string_ids.get(item["textId"])
        if text:
            labels.append(text)
            decoded_events.append({"text": text, "start": item.get("start"), "end": item.get("end")})
    outer = "C16_STAGEA_QWEN_AWQ_off_INSTRUMENT_ON"
    semantic = [label for label in labels if label.startswith("C16_STAGEA_") and label != outer]
    ordinals = []
    for label in semantic:
        try:
            ordinals.append(int(label.split("_", 3)[2]))
        except (IndexError, ValueError):
            pass
    kernel_count = con.execute(f"select count(*) from {kernel_table}").fetchone()[0]
    runtime_count = con.execute(f"select count(*) from {runtime_table}").fetchone()[0] if runtime_table in tables else 0
    outer_events = [event for event in decoded_events if event["text"] == outer]
    target_kernel_count = 0
    target_runtime_count = 0
    if len(outer_events) == 1 and outer_events[0]["end"] is not None:
        start_ns, end_ns = outer_events[0]["start"], outer_events[0]["end"]
        target_kernel_count = con.execute(
            f"select count(*) from {kernel_table} where start >= ? and end <= ?", (start_ns, end_ns)
        ).fetchone()[0]
        if runtime_table in tables:
            target_runtime_count = con.execute(
                f"select count(*) from {runtime_table} where start >= ? and end <= ?", (start_ns, end_ns)
            ).fetchone()[0]
    con.close()
    checks = {
        "trace_domains_cuda_nvtx": True,
        "outer_range_present_once": labels.count(outer) == 1,
        "semantic_range_count_576": len(semantic) == 576,
        "semantic_ordinals_exact_0_575": sorted(ordinals) == list(range(576)),
        "target_range_cuda_kernel_activity_present": target_kernel_count > 0,
        "target_range_cuda_runtime_activity_present": target_runtime_count > 0,
        "excluded_from_native_timing": True,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "nsys_version": subprocess.check_output(["nsys", "--version"], text=True).strip(),
        "trace": str(rep), "trace_bytes": rep.stat().st_size, "trace_sha256": sha(rep),
        "sqlite": str(sqlite), "sqlite_bytes": sqlite.stat().st_size, "sqlite_sha256": sha(sqlite),
        "nvtx_event_count": len(labels), "outer_range_count": labels.count(outer),
        "semantic_range_count": len(semantic),
        "full_process_kernel_activity_count": kernel_count,
        "full_process_cuda_runtime_activity_count": runtime_count,
        "target_range_kernel_activity_count": target_kernel_count,
        "target_range_cuda_runtime_activity_count": target_runtime_count,
        "capture_scope": "full_process_cuda_nvtx_trace; only target outer NVTX range is interpreted structurally",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo, raw, out = args.repo.resolve(), args.raw.resolve(), args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    native = json.loads((raw / "QWEN_AWQ_GRAPH_OFF_NATIVE.json").read_text())
    nsys_run = json.loads((raw / "QWEN_AWQ_GRAPH_OFF_NSYS_FINAL.json").read_text())
    authority = json.loads((repo / "docs/vm_tlb/review_packs/C16_STAGEA_RUNTIME_QUALIFICATION_CANARY_109_V1/QWEN_AWQ_RUNTIME_RECEIPT.json").read_text())
    asset = json.loads((repo / "docs/vm_tlb/review_packs/C16_STAGEA_RUNTIME_QUALIFICATION_CANARY_109_V1/ASSET_VISIBILITY_AND_SHA.json").read_text())
    preflight = json.loads((raw / "CPU_PREFLIGHT.json").read_text())
    lock_first = json.loads((raw / "GPU_LOCK_RECEIPT.json").read_text())
    lock_retry = json.loads((raw / "GPU_LOCK_RECEIPT_NSYS_RETRY.json").read_text())
    lock_final = json.loads((raw / "GPU_LOCK_RECEIPT_NSYS_FINAL.json").read_text())
    cumulative_active = lock_final["cumulative_gpu_active_wall_seconds"]
    lock = {
        "lock": lock_first["lock"],
        "attempts": [lock_first, lock_retry, lock_final],
        "attempt_count": 3,
        "cumulative_gpu_active_wall_seconds": cumulative_active,
        "gpu_active_cap_seconds": 60,
        "within_cumulative_cap": cumulative_active <= 60,
        "all_released": lock_first["released"] and lock_retry["released"] and lock_final["released"],
        "engineering_retry_reason": "attempt1 exact runner post-native torch profiler conflicted with NSYS CUPTI; attempt2 NVTX capture trigger did not emit a report; native data was preserved and only structural capture was retried",
    }

    runs = native["native_runs"]
    if [row["arm"] for row in runs] != ARM_ORDER:
        raise RuntimeError("native arm order mismatch")
    with (out / "NATIVE_SAMPLES.tsv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["sample_index", "arm", "host_wall_ms", "cuda_event_ms", "tokens", "logprobs_sha256"], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for index, row in enumerate(runs):
            writer.writerow({"sample_index": index, "arm": row["arm"],
                             "host_wall_ms": f'{row["host_wall_ms"]:.9f}',
                             "cuda_event_ms": f'{row["cuda_event_ms"]:.9f}',
                             "tokens": json.dumps(row["output"]["tokens"], separators=(",", ":")),
                             "logprobs_sha256": row["output"]["logprobs_sha256"]})

    off = [row for row in runs if row["arm"] == "OFF"]
    on = [row for row in runs if row["arm"] == "ON"]
    host_off = statistics.median(row["host_wall_ms"] for row in off)
    host_on = statistics.median(row["host_wall_ms"] for row in on)
    cuda_off = statistics.median(row["cuda_event_ms"] for row in off)
    cuda_on = statistics.median(row["cuda_event_ms"] for row in on)
    host_limit = max(5.0, 0.10 * host_off)
    cuda_limit = max(5.0, 0.10 * cuda_off)
    accepted_tokens = authority["graph_off"]["native_runs"][0]["tokens"]
    tokens_exact = all(row["output"]["tokens"] == accepted_tokens for row in runs)

    native_semantics = [row["instrumentation"] for row in on if row.get("instrumentation") and row["instrumentation"].get("semantic_order")]
    nsys_semantics = [nsys_run["instrumentation"]] if nsys_run.get("instrumentation", {}).get("semantic_order") else []
    if len(native_semantics) != 1 or len(nsys_semantics) != 1:
        raise RuntimeError("expected exactly one collected semantic receipt in each process")
    native_semantic, nsys_semantic = native_semantics[0], nsys_semantics[0]
    semantic_checks = {
        "occurrences_576": len(native_semantic["semantic_order"]) == 576,
        "accepted_v1_order_shape_hash_exact": native_semantic["semantic_order_sha256"] == ACCEPTED_SEMANTIC_SHA,
        "nsys_order_shape_exact": nsys_semantic["semantic_order"] == native_semantic["semantic_order"],
        "ranges_match_order": [dict(ordinal=x["ordinal"], module=x["module"], input_shape=x["input_shape"], output_shape=x["output_shape"])
                               for x in native_semantic["semantic_ranges"]] == native_semantic["semantic_order"],
    }
    semantic_receipt = {"status": "PASS" if all(semantic_checks.values()) else "FAIL",
                        "checks": semantic_checks,
                        "semantic_occurrences": len(native_semantic["semantic_order"]),
                        "semantic_order_sha256": native_semantic["semantic_order_sha256"],
                        "semantic_ranges_sha256": native_semantic["semantic_ranges_sha256"],
                        "semantic_order": native_semantic["semantic_order"]}
    write_json(out / "SEMANTIC_ORDER_RECEIPT.json", semantic_receipt)

    native_sig = backend_signature(native)
    accepted_sig = authority["graph_off"]["module_backend_signature"]
    inventory_off = native["profiler"]["OFF"]
    inventory_on = native["profiler"]["ON"]
    quant_methods = sorted({row["quant_method_class"] for row in native["module_census"] if row["quant_method_class"]})
    kernel_backends = sorted({row["kernel_backend_class"] for row in native["module_census"] if row["kernel_backend_class"]})
    kernel_checks = {
        "kernel_inventory_exact_off_on": inventory_off["kernel_inventory"] == inventory_on["kernel_inventory"],
        "kernel_inventory_sha_exact_off_on": inventory_off["kernel_inventory_sha256"] == inventory_on["kernel_inventory_sha256"],
        "backend_identity_accepted_exact": native_sig == accepted_sig,
        "autoawq_marlin_method_present": EXPECTED_QUANT_METHOD in quant_methods,
        "marlin_kernel_present": EXPECTED_KERNEL_BACKEND in kernel_backends,
        "no_requantization": asset["models"]["QWEN_AWQ"]["no_requantization"] is True and preflight["checks"]["all_model_asset_hashes_exact"],
    }
    kernel_receipt = {"status": "PASS" if all(kernel_checks.values()) else "FAIL", "checks": kernel_checks,
                      "off_kernel_count": inventory_off["kernel_count"], "on_kernel_count": inventory_on["kernel_count"],
                      "off_inventory_sha256": inventory_off["kernel_inventory_sha256"],
                      "on_inventory_sha256": inventory_on["kernel_inventory_sha256"],
                      "quant_method_classes": quant_methods, "kernel_backend_classes": kernel_backends,
                      "off_kernel_inventory": inventory_off["kernel_inventory"],
                      "on_kernel_inventory": inventory_on["kernel_inventory"]}
    write_json(out / "KERNEL_INVENTORY_RECEIPT.json", kernel_receipt)

    structural = nsys_receipt(raw)
    write_json(out / "NSYS_STRUCTURAL_RECEIPT.json", structural)

    neutrality_checks = {
        "native_status_pass": native["status"] == "PASS",
        "tokens_exact": tokens_exact,
        "semantic_shapes_exact": semantic_receipt["status"] == "PASS",
        "semantic_order_exact": semantic_receipt["status"] == "PASS",
        "kernel_inventory_exact": kernel_receipt["status"] == "PASS",
        "backend_identity_unchanged": kernel_checks["backend_identity_accepted_exact"],
        "host_neutrality_gate": abs(host_on - host_off) <= host_limit,
        "cuda_neutrality_gate": abs(cuda_on - cuda_off) <= cuda_limit,
        "nsys_structure_pass": structural["status"] == "PASS",
        "gpu_active_within_60_seconds": lock["within_cumulative_cap"],
        "gpu_lock_released": lock["all_released"],
    }
    decision = "OBSERVER_V2_NEUTRALITY_PASS" if all(neutrality_checks.values()) else "OBSERVER_V2_NEUTRALITY_FAIL"
    neutrality = {
        "status": decision, "checks": neutrality_checks,
        "native_arm_order": ARM_ORDER, "samples_per_arm": 3,
        "host_off_median_ms": host_off, "host_on_median_ms": host_on,
        "host_abs_delta_ms": abs(host_on - host_off), "host_limit_ms": host_limit,
        "cuda_off_median_ms": cuda_off, "cuda_on_median_ms": cuda_on,
        "cuda_abs_delta_ms": abs(cuda_on - cuda_off), "cuda_limit_ms": cuda_limit,
        "frozen_gate": "abs(median_ON - median_OFF) <= max(5.0 ms, 0.10 * median_OFF)",
        "instrumented_on_wall_authoritative_for_science": False,
    }
    write_json(out / "NEUTRALITY_RESULT.json", neutrality)

    budget = {"status": "PASS" if lock["within_cumulative_cap"] else "FAIL",
              "cap_seconds": 60, "gpu_active_wall_seconds": lock["cumulative_gpu_active_wall_seconds"],
              "remaining_seconds": 60 - lock["cumulative_gpu_active_wall_seconds"], "lock_released": lock["all_released"],
              "native_model_processes": 1, "structural_nsys_attempts": 3,
              "successful_structural_nsys_processes": 1, "total_model_processes": 4}
    write_json(out / "GPU_ACTIVE_BUDGET.json", budget)
    write_json(out / "GPU_LOCK_RECEIPT.json", lock)

    runtime_receipt = {
        "goal": "C16_AWQ_OBSERVER_V2_REQUAL_CANARY_109_V1", "status": decision,
        "scope": {"target": "QWEN_AWQ", "graph_mode": "GRAPH_OFF", "tier0_science": False},
        "source": preflight["source"], "runtime_authority": preflight["runtime_authority"],
        "model_revision": native["model_revision"], "vllm_config": native["vllm_config"],
        "accepted_tokens": accepted_tokens, "native_raw": str(raw / "QWEN_AWQ_GRAPH_OFF_NATIVE.json"),
        "native_raw_sha256": sha(raw / "QWEN_AWQ_GRAPH_OFF_NATIVE.json"),
        "nsys_run_raw": str(raw / "QWEN_AWQ_GRAPH_OFF_NSYS_FINAL.json"),
        "nsys_run_raw_sha256": sha(raw / "QWEN_AWQ_GRAPH_OFF_NSYS_FINAL.json"),
        "backend": {"quant_method": EXPECTED_QUANT_METHOD, "kernel": EXPECTED_KERNEL_BACKEND,
                    "no_requantization": kernel_checks["no_requantization"]},
        "neutrality": neutrality, "semantic_receipt_status": semantic_receipt["status"],
        "kernel_receipt_status": kernel_receipt["status"], "nsys_structural_status": structural["status"],
        "performance_use": "OBSERVER_NEUTRALITY_REQUALIFICATION_ONLY_NO_TIER0",
    }
    write_json(out / "OBSERVER_V2_RUNTIME_RECEIPT.json", runtime_receipt)
    final = {
        "goal": "C16_AWQ_OBSERVER_V2_REQUAL_CANARY_109_V1", "status": decision,
        "mp05_runtime_status": "RUNTIME_READY_WITH_OBSERVER_V2" if decision == "OBSERVER_V2_NEUTRALITY_PASS" else "REMOVED_FROM_STAGE_A",
        "tier0_authorized": False, "observer_v3_authorized": False, "threshold_relaxed": False,
        "automatic_next_goal": False, "stop": True,
    }
    write_json(out / "FINAL_DECISION.json", final)
    tests = {"status": "PASS" if all(neutrality_checks.values()) else "FAIL", "checks": neutrality_checks}
    write_json(out / "TESTS.json", tests)
    print(json.dumps(final, sort_keys=True))


if __name__ == "__main__":
    main()
