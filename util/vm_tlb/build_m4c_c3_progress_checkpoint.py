#!/usr/bin/env python3
"""Build a read-only nonterminal C3 progress-review checkpoint."""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import time
from pathlib import Path

ARMS = tuple(f"{roi}-{profile}" for roi in ("decode1", "prefill")
             for profile in ("disabled", "ideal", "generic", "paper"))
METRICS = (
    "gpu_tot_sim_cycle", "gpu_tot_ipc", "vm_translation_lookup_requests",
    "vm_l1_tlb_hits", "vm_l1_tlb_misses", "vm_l2_tlb_hits", "vm_l2_tlb_misses",
    "vm_translation_mshr_allocations", "vm_translation_mshr_merges",
    "vm_translation_mshr_full_events", "vm_translation_pwq_full_events",
    "vm_translation_walk_starts", "vm_pwc_hits", "vm_pwc_misses",
    "vm_pte_requests", "vm_pte_responses", "vm_pte_dram_responses",
    "vm_object_WEIGHT_translation_requesters", "vm_object_KV_CACHE_translation_requesters",
    "vm_object_UNKNOWN_translation_requesters", "vm_object_attribution_conservation_pass",
)
BINARY_SHA256 = "100527f1d54600dcbbf7c713584512344a688521089aaa995a0b7e4106f81eda"
RUNTIME_SHA256 = "fc07def22e239de9fec8a3dd83d237a607a82162cab2933d6707a37c0a208b0a"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_manifest(path: Path) -> dict[str, str]:
    with path.open(newline="") as source:
        rows = list(csv.reader(source, delimiter="\t"))
    if not rows or rows[0] != ["field", "value"]:
        raise SystemExit(f"FAIL bad manifest: {path}")
    return {key: value for key, value in rows[1:]}


def log_state(path: Path) -> tuple[int, int, dict[str, str], bool]:
    markers = telemetry = 0
    scalars: dict[str, str] = {}
    marker_paths: set[str] = set()
    with path.open(errors="strict") as source:
        for line in source:
            if line.startswith("Processing kernel "):
                markers += 1
                marker_paths.add(line.rstrip("\n"))
            elif line.startswith("m4c_telemetry_schema ="):
                telemetry += 1
            elif line.startswith(("vm_", "gpu_tot_")) and " = " in line:
                key, value = line.rstrip("\n").split(" = ", 1)
                scalars[key] = value.strip()
    return markers, telemetry, scalars, markers != len(marker_paths)


def pid_snapshot(pid: int, log: Path) -> dict[str, str]:
    result = {"pid": str(pid), "process_state": "NOT_AVAILABLE", "cpu_time_ticks": "NOT_AVAILABLE",
              "rss_kb": "NOT_AVAILABLE", "log_size_bytes": str(log.stat().st_size),
              "log_mtime_epoch": str(int(log.stat().st_mtime))}
    stat_path = Path(f"/proc/{pid}/stat")
    if not stat_path.is_file():
        result["pid"] = "NOT_RUNNING"
        return result
    fields = stat_path.read_text().split()
    result.update({"process_state": fields[2], "cpu_time_ticks": str(int(fields[13]) + int(fields[14])),
                   "rss_kb": str(int(fields[23]) * os.sysconf("SC_PAGE_SIZE") // 1024)})
    return result


def write_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--active-pid", type=int, required=True)
    args = parser.parse_args()
    root, output = args.runs_root.resolve(), args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"FAIL refusing nonempty output: {output}")
    output.mkdir(parents=True, exist_ok=True)
    status_rows: list[list[str]] = []
    provenance_rows: list[list[str]] = []
    metric_rows: list[list[str]] = []
    terminal: dict[str, dict[str, str]] = {}
    active_log: Path | None = None
    for arm in ARMS:
        run = root / arm
        manifest_path, log_path, list_path = run / "RUN_MANIFEST.tsv", run / "run.log", run / "traces" / "kernelslist.g"
        if not manifest_path.is_file() or not log_path.is_file() or not list_path.is_file():
            status_rows.append([arm, "INCOMPLETE_UNKNOWN", "NOT_AVAILABLE", "NOT_AVAILABLE", "NOT_AVAILABLE", "NOT_AVAILABLE", "missing formal artifact"])
            continue
        manifest = read_manifest(manifest_path)
        expected = sum(1 for line in list_path.read_text().splitlines() if line)
        markers, telemetry, scalars, duplicate_marker = log_state(log_path)
        exit_status = manifest.get("simulator_exit_status", "NOT_AVAILABLE")
        if exit_status == "0" and markers == expected and telemetry == expected:
            state, reason = "TERMINAL_PASS", "exit=0; markers=list; telemetry=list"
            terminal[arm] = scalars
        elif exit_status != "NOT_AVAILABLE":
            state, reason = "TERMINAL_FAIL", "terminal manifest does not satisfy count gate"
        elif arm == "prefill-paper":
            state, reason, active_log = "RUNNING", "no terminal manifest; liveness recorded separately", log_path
        else:
            state, reason = "INCOMPLETE_UNKNOWN", "no terminal manifest"
        status_rows.append([arm, state, str(expected), str(markers), str(telemetry), exit_status, reason])
        provenance_rows.append([arm, manifest.get("framework_head", "NOT_AVAILABLE"), manifest.get("core_head", "NOT_AVAILABLE"),
                                BINARY_SHA256, RUNTIME_SHA256, manifest.get("roi", "NOT_AVAILABLE"),
                                manifest.get("profile", "NOT_AVAILABLE"), sha256(manifest_path), sha256(list_path), sha256(log_path)])
        if state == "TERMINAL_PASS":
            for metric in METRICS:
                metric_rows.append([arm, manifest.get("roi", "NOT_AVAILABLE"), manifest.get("profile", "NOT_AVAILABLE"),
                                    metric, scalars.get(metric, "NOT_AVAILABLE"), "existing_run_log_final_scalar"])
            completion = {
                "completion_missing_telemetry_records": str(expected - telemetry),
                "completion_duplicate_processing_kernel_marker": str(duplicate_marker).upper(),
                "completion_duplicate_telemetry_records": "NOT_AVAILABLE",
                "completion_start_time": "NOT_AVAILABLE",
                "completion_end_time": "NOT_AVAILABLE",
                "completion_elapsed_runtime": "NOT_AVAILABLE",
            }
            for metric, value in completion.items():
                metric_rows.append([arm, manifest.get("roi", "NOT_AVAILABLE"), manifest.get("profile", "NOT_AVAILABLE"),
                                    metric, value, "manifest/log checkpoint evidence"])
    write_tsv(output / "C3_ARM_STATUS_MATRIX.tsv", ["arm", "state", "expected_kernel_count", "processing_kernel_markers", "telemetry_kernel_records", "simulator_exit_status", "evidence"], status_rows)
    write_tsv(output / "INPUT_PROVENANCE.tsv", ["arm", "framework_head", "core_head", "simulator_binary_sha256", "runtime_libcudart_sha256", "roi", "profile", "run_manifest_sha256", "trace_list_sha256", "run_log_sha256"], provenance_rows)
    write_tsv(output / "C3_TERMINAL_ARM_METRICS.tsv", ["arm", "roi", "profile", "metric", "value", "provenance"], metric_rows)
    comparison = [[arm, key, value] for arm, scalars in sorted(terminal.items()) for key, value in sorted(scalars.items()) if key in ("gpu_tot_sim_cycle", "gpu_tot_ipc", "vm_translation_lookup_requests", "vm_l1_tlb_misses", "vm_l2_tlb_misses", "vm_pte_requests")]
    write_tsv(output / "C3_INTERIM_COMPARISON.tsv", ["terminal_arm", "metric", "value"], comparison)
    if active_log is not None:
        snap = pid_snapshot(args.active_pid, active_log)
        row = [["prefill-paper", snap["pid"], snap["process_state"], snap["cpu_time_ticks"], snap["rss_kb"], snap["log_size_bytes"], snap["log_mtime_epoch"], str(int(time.time()))]]
    else:
        row = [["prefill-paper", "NOT_RUNNING", "NOT_AVAILABLE", "NOT_AVAILABLE", "NOT_AVAILABLE", "NOT_AVAILABLE", "NOT_AVAILABLE", str(int(time.time()))]]
    write_tsv(output / "ACTIVE_ARM_LIVENESS.tsv", ["arm", "pid", "process_state", "cpu_time_ticks", "rss_kb", "log_size_bytes", "log_mtime_epoch", "checkpoint_epoch"], row)
    print(f"PASS progress_checkpoint={output}")


if __name__ == "__main__":
    main()
