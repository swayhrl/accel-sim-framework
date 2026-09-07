#!/usr/bin/env python3
"""Assemble a transparent, partial-capable Window-B speculative review pack.

The tool copies only B-owned artifacts under the supplied scratch root.  It
never reads process state, other worktrees, or non-B scratch directories.
Missing experiments are emitted as explicit deferred rows rather than empty
measurements or relabelled evidence.
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
from collections import Counter
from pathlib import Path


LABEL = "SPECULATIVE_DIAGNOSTIC"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], data: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def copy_required(source: Path, output: Path) -> None:
    if not source.is_file():
        raise SystemExit(f"FAIL missing B-owned input: {source}")
    shutil.copy2(source, output)


def b1_coverage(scratch: Path, output: Path) -> list[dict[str, object]]:
    audit_paths = {
        "prefill": scratch / "analysis/b1-prefill-stream-full-v2/PARTIAL_INTEGRITY_V2.tsv",
        "decode1": scratch / "analysis/b1-decode1-stream-full-v2/PARTIAL_INTEGRITY_V2.tsv",
    }
    audit_rows = [{"evidence_label": LABEL, **entry}
                  for path in audit_paths.values() for entry in rows(path)]
    write_tsv(output / "B1_PARTIAL_COVERAGE.tsv", list(audit_rows[0]), audit_rows)
    totals = Counter(entry["roi"] for entry in audit_rows)
    passes = Counter(entry["roi"] for entry in audit_rows if entry["result"] == "PASS")
    result: list[dict[str, object]] = []
    for roi in ("prefill", "decode1"):
        result.append({
            "roi": roi, "evidence_label": LABEL, "coverage_status": "PARTIAL_ATOMICALLY_VALIDATED",
            "available_kernel_partials": passes[roi], "total_compute_kernels": totals[roi],
            "analysis_status": "REDUCER_DEFERRED_LOW_RESOURCE",
            "reason": "全局集合归约尚未完成峰值内存校准；不将 partial 覆盖伪装为完整 ROI 指标。",
        })
    fields = list(result[0])
    for name in ("TRACE_STATIC_KERNEL_STATS.tsv", "TRACE_REUSE_DISTANCE_SUMMARY.tsv",
                 "TRACE_KERNEL_WINDOW_WSS.tsv", "TRACE_CROSS_KERNEL_OVERLAP.tsv"):
        write_tsv(output / name, fields, result)
    return result


def b2_results(scratch: Path, output: Path) -> tuple[int, int]:
    ledger = rows(scratch / "b2/B2_SMOKE_PROGRESS_V4.tsv")
    converted = []
    for entry in ledger:
        converted.append({
            "stage": entry["stage"], "config_id": entry["config_id"], "roi": entry["roi"],
            "evidence_label": LABEL, "semantic_status": entry["semantic_status"],
            "realized_run_id": entry["realized_run_id"], "rss_kb": entry["rss_kb"],
            "wall_seconds": entry["wall_seconds"], "gpu_tot_ipc": entry["ipc"],
            "vm_l2_tlb_misses": entry["l2_tlb_misses"],
        })
    write_tsv(output / "VM_SWEEP_RESULTS.tsv", list(converted[0]), converted)
    done = sum(row["semantic_status"] == "COMPLETE" for row in ledger)
    return done, len(ledger) - done


def planned_cache_results(scratch: Path, output: Path, file_name: str, source_name: str,
                          stage: str) -> None:
    source = rows(scratch / source_name)
    data = [{
        "stage": stage, "run_id": entry["run_id"], "config_id": entry["config_id"],
        "roi": entry["roi"], "evidence_label": LABEL,
        "experiment_status": "DEFERRED_LOW_RESOURCE", "geometry_validation_mode": entry["validation_mode"],
        "geometry_validation_result": entry["result"],
        "effective_l1_bytes_per_sm": entry["effective_l1_bytes_per_sm"],
        "effective_l2_total_bytes": entry["effective_l2_total_bytes"],
        "effective_l2_assoc": entry["effective_l2_assoc"],
        "simulator_metrics": "UNAVAILABLE_NOT_RUN",
    } for entry in source]
    write_tsv(output / file_name, list(data[0]), data)


def nonllm_results(scratch: Path, output: Path) -> None:
    jobs = rows(scratch / "jobs/b4-smoke.tsv")
    data = [{
        "stage": job["stage"], "workload": job["workload"], "config_id": job["config_id"],
        "roi": job["roi"], "evidence_label": LABEL, "experiment_status": "DEFERRED_LOW_RESOURCE",
        "compatibility_status": "STATIC_TRACE_LIST_AND_FORMAT_CHECKED",
        "trace_list": job["trace_list"], "simulator_metrics": "UNAVAILABLE_NOT_RUN",
    } for job in jobs]
    write_tsv(output / "NON_LLM_COMPARISON.tsv", list(data[0]), data)


def failed_and_logs(scratch: Path, output: Path) -> None:
    summary = rows(scratch / "RUN_SUMMARY.tsv")
    failures = [{
        "run_id": row["run_id"], "stage": row["stage"], "evidence_label": LABEL,
        "classification": "FAILED", "reason": "simulator_or_launcher_nonzero_exit",
        "replacement_or_disposition": "保留原始 run 目录；重试项由语义完成账本去重。",
    } for row in summary if row["status"] == "FAILED"]
    failures.extend([
        {"run_id": "B1_PREFILL_PARALLEL_MINING", "stage": "B1", "evidence_label": LABEL,
         "classification": "PREEMPTED_LOW_RESOURCE", "reason": "低资源保护下停止继续高内存 trace mining；已完成 atomic partial 保留。",
         "replacement_or_disposition": "待 trace-miner 峰值校准及宿主恢复后续跑。"},
        {"run_id": "B1_DECODE1_PARALLEL_MINING", "stage": "B1", "evidence_label": LABEL,
         "classification": "PREEMPTED_LOW_RESOURCE", "reason": "低资源保护下停止继续高内存 trace mining；已完成 atomic partial 保留。",
         "replacement_or_disposition": "待 trace-miner 峰值校准及宿主恢复后续跑。"},
    ])
    write_tsv(output / "FAILED_OR_SUPERSEDED_RUNS.tsv", list(failures[0]), failures)
    raw = []
    for row in summary:
        run_dir = Path(row["run_dir"])
        log = run_dir / "run.log"
        raw.append({
            "run_id": row["run_id"], "stage": row["stage"], "evidence_label": LABEL,
            "run_dir": run_dir, "raw_log_path": log,
            "raw_log_hash_status": "DEFERRED_LOW_RESOURCE_IO_PROTECTION",
            "raw_log_sha256": "UNAVAILABLE", "reason": "路径已索引；全量日志散列延后以避免增加宿主 I/O 压力。",
        })
    write_tsv(output / "RAW_LOG_INDEX.tsv", list(raw[0]), raw)


def copied_registry(scratch: Path, output: Path) -> None:
    source = rows(scratch / "RUN_REGISTRY.tsv")
    for row in source:
        if row.get("evidence_label") not in {"SPECULATIVE_DIAGNOSTIC", "SPECULATIVE_CANDIDATE", "SUPERSEDED"}:
            row["evidence_label"] = LABEL
        for field, value in row.items():
            if value == "":
                row[field] = "NONE"
    write_tsv(output / "RUN_REGISTRY.tsv", list(source[0]), source)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--framework-head", required=True)
    parser.add_argument("--core-head", required=True)
    parser.add_argument("--simulator-sha256", required=True)
    parser.add_argument("--refresh", action="store_true",
                        help="replace only this tool's derived files in an existing B6 pack")
    args = parser.parse_args()
    if args.output.exists() and not args.refresh:
        raise SystemExit(f"FAIL output must be fresh: {args.output}")
    scratch = args.scratch_root
    args.output.mkdir(parents=True, exist_ok=args.refresh)
    write_tsv(args.output / "PROVENANCE.tsv",
              ["window", "evidence_label", "framework_branch", "framework_head", "core_branch", "core_head",
               "simulator_sha256", "scratch_root"], [{
                  "window": "B", "evidence_label": LABEL, "framework_branch": "hrl/vm-spec-farm-v0",
                  "framework_head": args.framework_head, "core_branch": "hrl/vm-spec-farm-v0",
                  "core_head": args.core_head, "simulator_sha256": args.simulator_sha256, "scratch_root": scratch,
              }])
    copy_required(scratch / "b0/FARM_CONCURRENCY_CALIBRATION.tsv", args.output / "FARM_CONCURRENCY_CALIBRATION.tsv")
    copied_registry(scratch, args.output)
    b1 = b1_coverage(scratch, args.output)
    b2_done, b2_missing = b2_results(scratch, args.output)
    planned_cache_results(scratch, args.output, "CACHE_SWEEP_RESULTS.tsv",
                          "b3/B3_PLANNED_GEOMETRY_VALIDATION.tsv", "B3_CACHE")
    planned_cache_results(scratch, args.output, "TLB_L2_GRID.tsv",
                          "b5/B5_PLANNED_GEOMETRY_VALIDATION.tsv", "B5_TLB_L2_GRID")
    nonllm_results(scratch, args.output)
    failed_and_logs(scratch, args.output)
    mem = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, value, *_ = line.replace(":", "").split()
        if key in {"MemAvailable", "SwapTotal", "SwapFree"}:
            mem[key] = value
    (args.output / "HOST_RESOURCE_INVENTORY.md").write_text(
        "# Window B host resource inventory（`SPECULATIVE_DIAGNOSTIC`，脱敏）\n\n"
        "- 逻辑 CPU：512；物理核心：256；插槽/NUMA：2/2。\n"
        "- B0 校准只使用 B 专属 worktree、binary 与 scratch；该包不含也不查询 Window A 进程或私有路径。\n"
        f"- closeout 观测 MemAvailable：{mem.get('MemAvailable', 'UNKNOWN')} KiB；"
        f"SwapTotal：{mem.get('SwapTotal', 'UNKNOWN')} KiB；SwapFree：{mem.get('SwapFree', 'UNKNOWN')} KiB。\n"
        "- 常规恢复线保持为总内存 20% + 4 GiB；当前采用有效并发 1 的动态低资源 gate。\n"
    )
    (args.output / "LOW_RESOURCE_MODE.md").write_text(
        "# B_LOW_RESOURCE_OPPORTUNISTIC_MODE（`SPECULATIVE_DIAGNOSTIC`）\n\n"
        "有效并发固定为 1。仅已校准的 decode1 smoke 类允许在无持续 swap、可接受 iowait、"
        "且 MemAvailable 大于 `max(4×peak, 最近波动+2×peak)` 时启动。\n\n"
        "已观测 decode1 smoke 峰值 RSS=204800 KiB；prefill smoke 峰值 RSS=626688 KiB。"
        "发现快速内存下降后，停止新增高负载 B 作业；B1 reducer/miner、B3/B4/B5 实际回放均延后。\n"
        "cgroup v2 存在但委派子树不可写，因此没有改变宿主 cgroup；B worker 使用 taskset、nice、ionice。\n"
    )
    (args.output / "SPECULATIVE_FINDINGS.md").write_text(
        "# Window B speculative findings（`SPECULATIVE_DIAGNOSTIC`）\n\n"
        "## 已测事实（仅 `SPECULATIVE_DIAGNOSTIC`）\n\n"
        f"- B0 的吞吐膝点冻结为 32；低资源模式当前有效并发为 1。\n"
        f"- B2 bounded smoke 语义完成 {b2_done}/54，缺失 {b2_missing}/54；所有已完成行仍为 speculative diagnostic。\n"
        f"- B1 原子 partial：prefill {b1[0]['available_kernel_partials']}/{b1[0]['total_compute_kernels']}，"
        f"decode1 {b1[1]['available_kernel_partials']}/{b1[1]['total_compute_kernels']}。\n"
        "- B3/B5 仅完成计划几何数值预检；B4 仅完成 trace-list/格式静态检查；均无运行时结果。\n\n"
        "## 假设\n\n"
        "- 在完整、经资源安全执行的 B2/B3/B5 ROI 完成前，不对 TLB、walker、PWC 或 cache 敏感性作性能归因。\n\n"
        "## 供正式复跑的候选\n\n"
        "- B2 的已完成 smoke 可作为后续 accepted 环境中重跑的候选清单，但不构成 formal evidence。\n"
    )
    print(f"PASS review_pack={args.output} b2_complete={b2_done} b2_missing={b2_missing}")


if __name__ == "__main__":
    main()
