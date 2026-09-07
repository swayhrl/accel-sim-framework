#!/usr/bin/env python3
"""Streaming-only synthesis of existing Window-B speculative artifacts.

This tool has no simulator, build, trace-generation, or process-management
path.  It reads only files below the supplied B scratch root.  B1 partials
are decoded one at a time and never accumulated as page/line sets.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import lzma
import pickle
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


LABEL = "SPECULATIVE_DIAGNOSTIC"
CLASSES = {"REAL_PASS", "REAL_PARTIAL", "SMOKE_ONLY", "PLANNED_ONLY", "STATIC_ONLY", "MISSING"}
OBJECTS = ("WEIGHT", "KV_CACHE", "UNKNOWN")
BASE_METRICS = (
    "gpu_tot_ipc", "vm_l1_tlb_accesses", "vm_l1_tlb_hits", "vm_l1_tlb_misses",
    "vm_l2_tlb_accesses", "vm_l2_tlb_hits", "vm_l2_tlb_misses",
    "vm_translation_mshr_allocations", "vm_translation_mshr_merges",
    "vm_translation_mshr_full_events", "vm_translation_pwq_full_events",
    "vm_translation_walk_starts", "vm_pwc_accesses", "vm_pwc_hits", "vm_pwc_misses",
    "vm_pte_requests", "vm_pte_responses", "vm_pte_response_misassociations",
    "vm_translation_waiter_registrations", "vm_translation_waiter_wakeups",
)
OBJECT_SUFFIXES = (
    "translation_requesters", "unique_translation_keys", "l1_lookup_launches", "l1_hits", "l1_misses",
    "l2_lookup_launches", "l2_hits", "l2_misses", "mshr_allocations", "mshr_merges", "walk_starts",
    "completed", "pwc_accesses", "pwc_hits", "pwc_misses", "pte_requests", "pte_l2_only_responses",
    "pte_dram_responses", "pte_memory_wait_cycles_total", "pte_memory_wait_cycles_max", "l2_fills",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def write_tsv(path: Path, data: list[dict[str, object]]) -> None:
    if not data:
        raise RuntimeError(f"refusing empty output: {path}")
    fields = list(data[0])
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in data:
            writer.writerow({key: "NA" if value in (None, "") else value for key, value in row.items()})


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def int_value(value: str | int | None) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def job_rows(paths: Iterable[Path]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for path in paths:
        result.extend(read_tsv(path))
    return result


def b1_characterization(scratch: Path, max_partial_bytes: int) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    audits = [
        scratch / "analysis/b1-prefill-stream-full-v2/PARTIAL_INTEGRITY_V2.tsv",
        scratch / "analysis/b1-decode1-stream-full-v2/PARTIAL_INTEGRITY_V2.tsv",
    ]
    audit_rows = [row for path in audits for row in read_tsv(path)]
    totals: dict[str, int] = Counter(row["roi"] for row in audit_rows)
    available: dict[str, int] = Counter(row["roi"] for row in audit_rows if row["result"] == "PASS")
    aggregate: dict[str, dict[str, Any]] = {}
    for roi in ("prefill", "decode1"):
        aggregate[roi] = {
            "global": Counter(), "op": Counter(), "instruction_class": Counter(),
            "objects": {kind: Counter() for kind in OBJECTS},
            "object_hot_max": {kind: {"line": 0, "page": 0} for kind in OBJECTS},
        }
    for row in audit_rows:
        if row["result"] != "PASS":
            continue
        partial = Path(row["partial"])
        if partial.stat().st_size > max_partial_bytes:
            raise RuntimeError(f"partial exceeds streaming guard {max_partial_bytes} bytes: {partial}")
        with lzma.open(partial, "rb") as stream:
            item = pickle.load(stream)
        if item.get("schema") != "VM_SPEC_FARM_TRACE_PARTIAL_V1" or item.get("trace") != row["trace"]:
            raise RuntimeError(f"partial schema/trace mismatch: {partial}")
        out = aggregate[row["roi"]]
        out["global"].update({key: int_value(value) for key, value in item["global"].items()
                              if isinstance(value, (int, float))})
        out["op"].update(item["global"]["op_class"])
        out["instruction_class"].update(item["global"]["instruction_object_class"])
        for kind in OBJECTS:
            source = item["objects"][kind]
            target = out["objects"][kind]
            target["lane_references"] += int_value(source["lane_references"])
            target["requested_bytes"] += int_value(source["requested_bytes"])
            for unit in ("sectors", "lines", "pages64", "pages2"):
                target[f"unique_{unit}_sum_per_kernel"] += len(source[unit])
            out["object_hot_max"][kind]["line"] = max(out["object_hot_max"][kind]["line"], int_value(source["line_hot_max"]))
            out["object_hot_max"][kind]["page"] = max(out["object_hot_max"][kind]["page"], int_value(source["page_hot_max"]))
        del item
    result: list[dict[str, object]] = []
    for roi in ("prefill", "decode1"):
        out = aggregate[roi]
        result.append({
            "evidence_label": LABEL, "stage": "B1", "workload": "llama", "roi": roi,
            "object_class": "ALL", "coverage_class": "REAL_PARTIAL", "available_kernel_partials": available[roi],
            "total_compute_kernels": totals[roi], "memory_instructions_partial_sum": out["global"]["memory_instructions"],
            "lane_references_partial_sum": out["global"]["lane_references"],
            "requested_bytes_partial_sum": out["global"]["requested_bytes"],
            "load_memory_instructions_partial_sum": out["op"]["LOAD"],
            "store_memory_instructions_partial_sum": out["op"]["STORE"],
            "atomic_memory_instructions_partial_sum": out["op"]["ATOMIC"],
            "lane_adjacent_pairs_partial_sum": out["global"]["lane_adjacent_pairs"],
            "lane_adjacent_equal_width_partial_sum": out["global"]["lane_adjacent_equal_width"],
            "lane_adjacent_zero_stride_partial_sum": out["global"]["lane_adjacent_zero_stride"],
            "lane_adjacent_positive_other_partial_sum": out["global"]["lane_adjacent_positive_other"],
            "lane_adjacent_negative_partial_sum": out["global"]["lane_adjacent_negative"],
            "unique_32b_sectors_sum_per_kernel": "NOT_COMPUTED_FOR_ALL",
            "unique_128b_lines_sum_per_kernel": "NOT_COMPUTED_FOR_ALL",
            "unique_64kb_pages_sum_per_kernel": "NOT_COMPUTED_FOR_ALL",
            "unique_2mb_pages_sum_per_kernel": "NOT_COMPUTED_FOR_ALL",
            "caveat": "只累计已验证 partial；未构造跨 kernel union 或 full-ROI 重用距离。",
        })
        for kind in OBJECTS:
            source = out["objects"][kind]
            result.append({
                "evidence_label": LABEL, "stage": "B1", "workload": "llama", "roi": roi,
                "object_class": kind, "coverage_class": "REAL_PARTIAL", "available_kernel_partials": available[roi],
                "total_compute_kernels": totals[roi], "memory_instructions_partial_sum": "NOT_APPLICABLE",
                "lane_references_partial_sum": source["lane_references"], "requested_bytes_partial_sum": source["requested_bytes"],
                "load_memory_instructions_partial_sum": "NOT_APPLICABLE", "store_memory_instructions_partial_sum": "NOT_APPLICABLE",
                "atomic_memory_instructions_partial_sum": "NOT_APPLICABLE", "lane_adjacent_pairs_partial_sum": "NOT_APPLICABLE",
                "lane_adjacent_equal_width_partial_sum": "NOT_APPLICABLE", "lane_adjacent_zero_stride_partial_sum": "NOT_APPLICABLE",
                "lane_adjacent_positive_other_partial_sum": "NOT_APPLICABLE", "lane_adjacent_negative_partial_sum": "NOT_APPLICABLE",
                "unique_32b_sectors_sum_per_kernel": source["unique_sectors_sum_per_kernel"],
                "unique_128b_lines_sum_per_kernel": source["unique_lines_sum_per_kernel"],
                "unique_64kb_pages_sum_per_kernel": source["unique_pages64_sum_per_kernel"],
                "unique_2mb_pages_sum_per_kernel": source["unique_pages2_sum_per_kernel"],
                "caveat": f"max_observed_line_hot={out['object_hot_max'][kind]['line']}; max_observed_page_hot={out['object_hot_max'][kind]['page']}; 非完整 phase union。",
            })
    return result, audit_rows


def parse_log_metrics(log: Path) -> dict[str, str]:
    wanted = {f"vm_object_{kind}_{suffix}" for kind in OBJECTS for suffix in OBJECT_SUFFIXES}
    found = {name: "MISSING" for name in wanted}
    if not log.is_file():
        return found
    with log.open(errors="replace") as stream:
        for raw in stream:
            if " = " not in raw:
                continue
            key, value = raw.rstrip("\n").split(" = ", 1)
            if key in wanted:
                found[key] = value
    return found


def b2_results(scratch: Path) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    summary = {row["run_id"]: row for row in read_tsv(scratch / "RUN_SUMMARY.tsv")}
    ledger = read_tsv(scratch / "b2/B2_SMOKE_PROGRESS_V4.tsv")
    characterization: list[dict[str, object]] = []
    objects: list[dict[str, object]] = []
    completed: dict[tuple[str, str], dict[str, object]] = {}
    for row in ledger:
        base = {
            "evidence_label": LABEL, "stage": row["stage"], "workload": "llama", "config_id": row["config_id"],
            "roi": row["roi"], "coverage_class": "SMOKE_ONLY" if row["semantic_status"] == "COMPLETE" else "MISSING",
            "semantic_status": row["semantic_status"], "realized_run_id": row["realized_run_id"],
            "sample_scope": "one_kernel_continuous_replay" if row["semantic_status"] == "COMPLETE" else "NOT_RUN",
        }
        if row["semantic_status"] != "COMPLETE":
            characterization.append({**base, **{metric: "NOT_RUN" for metric in BASE_METRICS},
                                     "completed_kernels": "0", "telemetry_records": "0", "rss_kb": "NOT_RUN",
                                     "wall_seconds": "NOT_RUN", "caveat": "无 smoke，亦无 full ROI。"})
            continue
        source = summary.get(row["realized_run_id"])
        if source is None or source["status"] == "FAILED":
            raise RuntimeError(f"semantic completion without successful summary: {row['realized_run_id']}")
        entry = {**base, **{metric: source.get(metric, "MISSING") for metric in BASE_METRICS},
                 "completed_kernels": source["completed_kernels"], "telemetry_records": source["telemetry_records"],
                 "rss_kb": source["rss_kb"], "wall_seconds": source["wall_seconds"],
                 "caveat": "单 kernel smoke；不可用于完整 workload 性能结论。"}
        characterization.append(entry)
        completed[(row["config_id"], row["roi"])] = entry
        log_metrics = parse_log_metrics(Path(source["run_dir"]) / "run.log")
        for kind in OBJECTS:
            objects.append({
                "evidence_label": LABEL, "stage": row["stage"], "workload": "llama", "config_id": row["config_id"],
                "roi": row["roi"], "coverage_class": "SMOKE_ONLY", "realized_run_id": row["realized_run_id"],
                "object_class": kind, **{suffix: log_metrics[f"vm_object_{kind}_{suffix}"] for suffix in OBJECT_SUFFIXES},
                "caveat": "单 kernel smoke；对象归因守恒应由原始 manifest/log 复核。",
            })
    differences: list[dict[str, object]] = []
    signal_metrics = ("gpu_tot_ipc", "vm_l2_tlb_misses", "vm_translation_walk_starts", "vm_pwc_hits", "vm_pwc_misses", "vm_pte_requests")
    for (config, roi), entry in sorted(completed.items()):
        if config == "b2-baseline":
            continue
        baseline = completed.get(("b2-baseline", roi))
        if baseline is None:
            continue
        changed = []
        strong = False
        for metric in signal_metrics:
            before, after = int_value(baseline[metric]), int_value(entry[metric])
            if before != after:
                changed.append(f"{metric}:{before}->{after}")
                if metric in {"vm_pwc_hits", "vm_pwc_misses", "vm_pte_requests"} or (before and abs(after - before) / before >= .10):
                    strong = True
        ipc_before, ipc_after = float(baseline["gpu_tot_ipc"]), float(entry["gpu_tot_ipc"])
        if ipc_before and abs(ipc_after - ipc_before) / ipc_before >= .005:
            strong = True
        differences.append({
            "evidence_label": LABEL, "stage": "B2_VM_SMOKE", "workload": "llama", "config_id": config,
            "roi": roi, "coverage_class": "SMOKE_ONLY",
            "signal_class": "OBSERVED_STRONG_SMOKE_SIGNAL" if strong else (
                "OBSERVED_SMALL_SMOKE_DELTA" if changed else "NO_DETECTABLE_SMOKE_DELTA"),
            "changed_metrics": ";".join(changed) if changed else "NONE",
            "ipc_delta_pct": f"{100.0 * (ipc_after - ipc_before) / ipc_before:.4f}" if ipc_before else "NA",
            "interpretation_limit": "只比较单 kernel smoke；需完整 ROI 重跑后才能判断 workload-level 行为。",
        })
    return characterization, objects, differences


def coverage_matrix(scratch: Path, b1_audit: list[dict[str, str]]) -> list[dict[str, object]]:
    coverage: list[dict[str, object]] = []
    totals, passes = Counter(row["roi"] for row in b1_audit), Counter(row["roi"] for row in b1_audit if row["result"] == "PASS")
    for roi in ("prefill", "decode1"):
        coverage.append({"evidence_label": LABEL, "stage": "B1", "workload": "llama", "config_id": "offline_trace_mining",
                         "roi": roi, "coverage_class": "REAL_PARTIAL", "run_scope": "per_kernel_offline_analysis",
                         "completed_units": passes[roi], "expected_units": totals[roi],
                         "evidence_source": "B1_PARTIAL_INTEGRITY_V2", "reason": "atomic partial 已验证，但 full phase reducer 未运行。"})
    for row in read_tsv(scratch / "b2/B2_SMOKE_PROGRESS_V4.tsv"):
        state = "SMOKE_ONLY" if row["semantic_status"] == "COMPLETE" else "MISSING"
        coverage.append({"evidence_label": LABEL, "stage": "B2", "workload": "llama", "config_id": row["config_id"],
                         "roi": row["roi"], "coverage_class": state,
                         "run_scope": "one_kernel_continuous_smoke" if state == "SMOKE_ONLY" else "not_run",
                         "completed_units": "1" if state == "SMOKE_ONLY" else "0", "expected_units": "full_roi_not_run",
                         "evidence_source": row["realized_run_id"], "reason": "完整 ROI 尚未运行。"})
    planned = (("B3", scratch / "jobs/b3-full.tsv", "planned_cache_geometry"),
               ("B5", scratch / "jobs/b5-full.tsv", "planned_tlb_l2_geometry"))
    for stage, path, source in planned:
        for row in read_tsv(path):
            coverage.append({"evidence_label": LABEL, "stage": stage, "workload": "llama", "config_id": row["config_id"],
                             "roi": row["roi"], "coverage_class": "PLANNED_ONLY", "run_scope": "smoke_and_full_not_run",
                             "completed_units": "0", "expected_units": "full_roi_not_run", "evidence_source": source,
                             "reason": "仅 planned geometry/static preflight；没有 simulator telemetry。"})
    for row in read_tsv(scratch / "jobs/b4-full.tsv"):
        coverage.append({"evidence_label": LABEL, "stage": "B4", "workload": row["workload"], "config_id": row["config_id"],
                         "roi": row["roi"], "coverage_class": "STATIC_ONLY", "run_scope": "smoke_and_full_not_run",
                         "completed_units": "0", "expected_units": "full_workload_not_run", "evidence_source": "immutable_trace_stage_lock",
                         "reason": "trace-list/format 静态兼容；无 simulator 回放。"})
    for row in coverage:
        if row["coverage_class"] not in CLASSES:
            raise RuntimeError(f"invalid coverage class: {row}")
    return coverage


def priority_rows(scratch: Path, b1_audit: list[dict[str, str]]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []

    def add(rank: int, band: str, stage: str, workload: str, config: str, roi: str, job: str,
            gain: str, cost: str, gap: str, prerequisite: str, rationale: str) -> None:
        result.append({"priority_rank": rank, "priority_band": band, "evidence_label": LABEL, "stage": stage,
                       "workload": workload, "config_id": config, "roi": roi, "job_id": job,
                       "information_gain": gain, "resource_cost": cost, "evidence_gap": gap,
                       "prerequisite": prerequisite, "rationale": rationale})

    missing_b2 = [row for row in read_tsv(scratch / "b2/B2_SMOKE_PROGRESS_V4.tsv") if row["semantic_status"] == "MISSING"]
    first = [("b2-pwc-finite32", "decode1"), ("b2-pwc-finite512", "decode1"), ("b2-pwc-ideal", "decode1"),
             ("b2-page-2mb-diagnostic", "decode1"), ("b2-control-vm-disabled", "decode1"),
             ("b2-control-ideal-identity", "decode1")]
    index = {(row["config_id"], row["roi"]): row for row in missing_b2}
    for rank, key in enumerate(first, 1):
        if key in index:
            add(rank, "P0_FIRST_SMALL_BATCH", "B2", "llama", key[0], key[1], f"B2_RETRY_{key[0]}_{key[1]}",
                "HIGH", "LOW_CALIBRATED_DECODE_SMOKE", "PWC/control/page diagnostic smoke missing",
                "A terminal; clean no-swap gate; effective concurrency=1",
                "补齐 PWC-off 已见 smoke 信号的相邻 PWC 模式，随后补页大小和 translation controls。")
    for row in missing_b2:
        if (row["config_id"], row["roi"]) in first:
            continue
        rank = 15 if row["roi"] == "decode1" else 25
        add(rank, "P1_REMAINING_B2_SMOKE", "B2", "llama", row["config_id"], row["roi"],
            f"B2_RETRY_{row['config_id']}_{row['roi']}", "MEDIUM", "LOW_CALIBRATED_DECODE_SMOKE" if row["roi"] == "decode1" else "MEDIUM_CALIBRATED_PREFILL_SMOKE",
            "B2 OFAT smoke missing", "A terminal; clean no-swap gate; effective concurrency=1",
            "先完成语义去重的 B2 smoke matrix，仍不启动 full ROI。")
    add(7, "P0_CALIBRATION", "B1", "llama", "trace_miner_worker", "decode1", "B1_DECODE1_WORKER_PEAK_CALIBRATION",
        "HIGH", "CALIBRATION_ONLY", "B1 miner/reducer peak RSS 未知", "A terminal; clean no-swap gate; one worker",
        "先记录单 worker peak RSS，才允许继续任何 B1 missing partial。")
    add(8, "P0_CALIBRATION", "B1", "llama", "trace_miner_worker", "prefill", "B1_PREFILL_WORKER_PEAK_CALIBRATION",
        "HIGH", "CALIBRATION_ONLY", "B1 miner/reducer peak RSS 未知", "A terminal; clean no-swap gate; one worker",
        "先记录单 worker peak RSS，才允许继续任何 B1 missing partial。")
    for row in b1_audit:
        if row["result"] == "MISSING":
            add(35, "P2_B1_PARTIALS", "B1", "llama", "offline_trace_mining", row["roi"],
                f"B1_{row['roi']}_KERNEL_{row['index']}", "HIGH", "UNKNOWN_UNTIL_CALIBRATED",
                "missing atomic trace partial", "对应 ROI worker peak calibration 已通过；one worker",
                "保持 immutable trace mining 的 per-kernel 恢复顺序。")
    for stage, path, rank, cost in (("B3", scratch / "jobs/b3-smoke.tsv", 45, "UNKNOWN_SMOKE_CALIBRATE_FIRST"),
                                    ("B4", scratch / "jobs/b4-smoke.tsv", 55, "UNKNOWN_SMOKE_CALIBRATE_FIRST"),
                                    ("B5", scratch / "jobs/b5-smoke.tsv", 65, "UNKNOWN_SMOKE_CALIBRATE_FIRST"),
                                    ("B3", scratch / "jobs/b3-full.tsv", 85, "HIGH_FULL_ROI"),
                                    ("B4", scratch / "jobs/b4-full.tsv", 90, "HIGH_FULL_WORKLOAD"),
                                    ("B5", scratch / "jobs/b5-full.tsv", 95, "HIGH_FULL_ROI")):
        for row in read_tsv(path):
            workload = row.get("workload", "llama")
            add(rank, "P3_LATER_SMOKE" if "smoke" in path.name else "P4_FULL_AFTER_SMOKE", stage, workload,
                row["config_id"], row["roi"], row["run_id"], "MEDIUM", cost,
                "planned/static-only coverage", "完成前序 smoke 与对应 memory calibration",
                "B3/B4/B5 不得在 B2 基础 smoke 与资源门控恢复前抢占资源。")
    return sorted(result, key=lambda row: (int(row["priority_rank"]), row["stage"], row["workload"], row["config_id"], row["roi"], row["job_id"]))


def conservation_rows(b1: list[dict[str, object]], b2: list[dict[str, object]],
                      objects: list[dict[str, object]]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for roi in ("prefill", "decode1"):
        all_row = next(row for row in b1 if row["roi"] == roi and row["object_class"] == "ALL")
        object_rows = [row for row in b1 if row["roi"] == roi and row["object_class"] in OBJECTS]
        for metric in ("lane_references_partial_sum", "requested_bytes_partial_sum"):
            expected = int_value(all_row[metric])
            observed = sum(int_value(row[metric]) for row in object_rows)
            result.append({"evidence_label": LABEL, "area": "B1_partial_object", "config_id": "offline_trace_mining",
                           "roi": roi, "metric": metric, "expected": expected, "observed": observed,
                           "result": "PASS" if expected == observed else "FAIL", "scope": "available atomic partials only"})
    mapping = {
        "vm_l1_tlb_accesses": ("translation_requesters",), "vm_l1_tlb_hits": ("l1_hits",),
        "vm_l1_tlb_misses": ("l1_misses",), "vm_l2_tlb_accesses": ("l2_lookup_launches",),
        "vm_l2_tlb_hits": ("l2_hits",), "vm_l2_tlb_misses": ("l2_misses",),
        "vm_translation_mshr_allocations": ("mshr_allocations",), "vm_translation_mshr_merges": ("mshr_merges",),
        "vm_translation_walk_starts": ("walk_starts",), "vm_pwc_accesses": ("pwc_accesses",),
        "vm_pwc_hits": ("pwc_hits",), "vm_pwc_misses": ("pwc_misses",), "vm_pte_requests": ("pte_requests",),
        "vm_pte_responses": ("pte_l2_only_responses", "pte_dram_responses"),
    }
    for entry in b2:
        if entry["coverage_class"] != "SMOKE_ONLY":
            continue
        object_rows = [row for row in objects if row["realized_run_id"] == entry["realized_run_id"]]
        for global_metric, object_metrics in mapping.items():
            expected = int_value(entry[global_metric])
            observed = sum(sum(int_value(row[metric]) for metric in object_metrics) for row in object_rows)
            result.append({"evidence_label": LABEL, "area": "B2_smoke_object_ptw", "config_id": entry["config_id"],
                           "roi": entry["roi"], "metric": global_metric, "expected": expected, "observed": observed,
                           "result": "PASS" if expected == observed else "FAIL", "scope": "one-kernel smoke only"})
    if any(row["result"] != "PASS" for row in result):
        bad = sum(row["result"] != "PASS" for row in result)
        raise RuntimeError(f"synthesis conservation failure rows={bad}")
    return result


def b1_phase_comparison(b1: list[dict[str, object]]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for roi in ("prefill", "decode1"):
        all_row = next(row for row in b1 if row["roi"] == roi and row["object_class"] == "ALL")
        object_rows = {row["object_class"]: row for row in b1 if row["roi"] == roi and row["object_class"] in OBJECTS}
        lanes = int_value(all_row["lane_references_partial_sum"])
        pairs = int_value(all_row["lane_adjacent_pairs_partial_sum"])
        result.append({
            "evidence_label": LABEL, "stage": "B1", "workload": "llama", "roi": roi,
            "coverage_class": "REAL_PARTIAL", "available_kernel_partials": all_row["available_kernel_partials"],
            "total_compute_kernels": all_row["total_compute_kernels"],
            "coverage_pct": f"{100.0 * int_value(all_row['available_kernel_partials']) / int_value(all_row['total_compute_kernels']):.3f}",
            "memory_instructions_partial_sum": all_row["memory_instructions_partial_sum"],
            "lane_references_partial_sum": lanes, "requested_bytes_partial_sum": all_row["requested_bytes_partial_sum"],
            "lane_adjacent_equal_width_pct": f"{100.0 * int_value(all_row['lane_adjacent_equal_width_partial_sum']) / pairs:.3f}" if pairs else "NA",
            "weight_lane_ref_pct": f"{100.0 * int_value(object_rows['WEIGHT']['lane_references_partial_sum']) / lanes:.3f}" if lanes else "NA",
            "kv_cache_lane_ref_pct": f"{100.0 * int_value(object_rows['KV_CACHE']['lane_references_partial_sum']) / lanes:.3f}" if lanes else "NA",
            "unknown_lane_ref_pct": f"{100.0 * int_value(object_rows['UNKNOWN']['lane_references_partial_sum']) / lanes:.3f}" if lanes else "NA",
            "caveat": "两个 ROI 的 coverage 比例不同；此表只比较已完成 partial 累计，不能外推为完整 phase。",
        })
    return result


def input_provenance(scratch: Path) -> list[dict[str, object]]:
    inputs = (
        ("B1_PREFILL_PARTIAL_AUDIT", scratch / "analysis/b1-prefill-stream-full-v2/PARTIAL_INTEGRITY_V2.tsv"),
        ("B1_DECODE1_PARTIAL_AUDIT", scratch / "analysis/b1-decode1-stream-full-v2/PARTIAL_INTEGRITY_V2.tsv"),
        ("B2_SEMANTIC_LEDGER", scratch / "b2/B2_SMOKE_PROGRESS_V4.tsv"),
        ("B2_RUN_SUMMARY", scratch / "RUN_SUMMARY.tsv"),
        ("B3_PLANNED_GEOMETRY", scratch / "b3/B3_PLANNED_GEOMETRY_VALIDATION.tsv"),
        ("B4_IMMUTABLE_STAGE_LOCK", scratch / "b4/nonllm_stage_lock.tsv"),
        ("B5_PLANNED_GEOMETRY", scratch / "b5/B5_PLANNED_GEOMETRY_VALIDATION.tsv"),
        ("B3_JOB_MATRIX", scratch / "jobs/b3-full.tsv"),
        ("B4_JOB_MATRIX", scratch / "jobs/b4-full.tsv"),
        ("B5_JOB_MATRIX", scratch / "jobs/b5-full.tsv"),
    )
    output = []
    for role, path in inputs:
        if not path.is_file():
            raise RuntimeError(f"missing B7 input: {path}")
        output.append({"evidence_label": LABEL, "input_role": role, "path": path,
                       "sha256": digest(path), "access_mode": "READ_ONLY_STREAMING"})
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-partial-compressed-bytes", type=int, default=1024 * 1024)
    parser.add_argument("--refresh", action="store_true", help="replace only this tool's derived B7 files")
    args = parser.parse_args()
    if args.output.exists() and not args.refresh:
        raise SystemExit(f"FAIL output must be fresh: {args.output}")
    if args.max_partial_compressed_bytes < 1:
        raise SystemExit("FAIL partial byte guard must be positive")
    scratch = args.scratch_root
    args.output.mkdir(parents=True, exist_ok=args.refresh)
    b1, b1_audit = b1_characterization(scratch, args.max_partial_compressed_bytes)
    b2, objects, differences = b2_results(scratch)
    coverage = coverage_matrix(scratch, b1_audit)
    priorities = priority_rows(scratch, b1_audit)
    conservation = conservation_rows(b1, b2, objects)
    phase_comparison = b1_phase_comparison(b1)
    provenance = input_provenance(scratch)
    write_tsv(args.output / "EXPERIMENT_COVERAGE_MATRIX.tsv", coverage)
    write_tsv(args.output / "B1_PARTIAL_TRACE_CHARACTERIZATION.tsv", b1)
    write_tsv(args.output / "B1_PHASE_PARTIAL_COMPARISON.tsv", phase_comparison)
    write_tsv(args.output / "B2_SMOKE_TRANSLATION_CHARACTERIZATION.tsv", b2)
    write_tsv(args.output / "B2_OBJECT_PTW_CHARACTERIZATION.tsv", objects)
    write_tsv(args.output / "OBSERVED_BEHAVIOR_DIFFERENCES.tsv", differences)
    write_tsv(args.output / "SYNTHESIS_CONSERVATION.tsv", conservation)
    write_tsv(args.output / "B7_INPUT_PROVENANCE.tsv", provenance)
    write_tsv(args.output / "RESUME_PRIORITY_V1.tsv", priorities)
    gaps = [
        {"evidence_label": LABEL, "area": "B1_phase_unions_reuse", "coverage_class": "REAL_PARTIAL",
         "status": "MISSING", "required_evidence": "complete partial set plus resource-safe reducer", "reason": "现有 partial 不足以构造 full-phase union/overlap/reuse-distance。"},
        {"evidence_label": LABEL, "area": "B2_full_roi", "coverage_class": "SMOKE_ONLY",
         "status": "MISSING", "required_evidence": "continuous decode1 and prefill full ROI", "reason": "所有完成 B2 行均为 one-kernel smoke。"},
        {"evidence_label": LABEL, "area": "B3_runtime_cache", "coverage_class": "PLANNED_ONLY",
         "status": "MISSING", "required_evidence": "realized cache geometry plus telemetry", "reason": "只有 planned geometry preflight。"},
        {"evidence_label": LABEL, "area": "B4_nonllm_comparison", "coverage_class": "STATIC_ONLY",
         "status": "MISSING", "required_evidence": "compatible trace smoke and continuous workload runs", "reason": "只有 immutable trace 静态兼容。"},
        {"evidence_label": LABEL, "area": "B5_tlb_l2_interaction", "coverage_class": "PLANNED_ONLY",
         "status": "MISSING", "required_evidence": "nine-point grid per ROI", "reason": "只有 planned geometry preflight。"},
    ]
    write_tsv(args.output / "EVIDENCE_GAPS_AND_LIMITATIONS.tsv", gaps)
    strong = [row for row in differences if row["signal_class"] == "OBSERVED_STRONG_SMOKE_SIGNAL"]
    (args.output / "B7_SYNTHESIS.md").write_text(
        "# B7 partial farm evidence synthesis（`SPECULATIVE_DIAGNOSTIC`）\n\n"
        "本目录只由现有 Window-B scratch、partial、manifest 与 telemetry 流式生成；没有启动 simulator、"
        "生成 trace 或重建。B1 每次只解开一个已验证 partial，且受压缩大小 guard 限制；没有构造跨 partial 大集合。\n\n"
        "## 覆盖结论\n\n"
        f"- coverage matrix 包含 {len(coverage)} 个 workload/config/ROI 行。B1 是 `REAL_PARTIAL`；"
        "B2 已完成项均为 `SMOKE_ONLY`；B3/B5 为 `PLANNED_ONLY`；B4 为 `STATIC_ONLY`。\n"
        f"- 现有 B2 smoke 的强可观测信号数为 {len(strong)}。强信号仅说明该单 kernel telemetry 有差异，"
        "不构成 full-workload 或性能因果结论。\n\n"
        "## A terminal 后的第一小批建议\n\n"
        "1. 在 clean no-swap、单 worker 下补 B2 decode1 的 PWC finite-32、finite-512、ideal 三个 smoke，"
        "以围绕已观察到的 PWC-off smoke 信号建立最小对照。\n"
        "2. 接着补 decode1 的 2MB diagnostic 与两个 translation controls。\n"
        "3. 只在上述项稳定且资源门控通过后，分别做一次 B1 decode1/prefill miner peak-RSS 校准；"
        "其后才允许补 B1 partial。\n\n"
        "所有结论和 resume 排序都必须在 accepted 环境中的连续 full ROI 重跑后才能升级。\n"
    )
    print(f"PASS coverage={len(coverage)} b1_rows={len(b1)} b2_rows={len(b2)} object_rows={len(objects)} priorities={len(priorities)}")


if __name__ == "__main__":
    main()
