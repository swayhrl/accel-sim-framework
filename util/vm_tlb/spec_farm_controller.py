#!/usr/bin/env python3
"""Resource-bounded Window-B simulator-farm controller.

Every child is a complete, continuous ROI replay in an isolated run directory.
This controller deliberately never discovers, attaches to, or manages processes
outside of its own registry.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TOTAL_MEMORY_KB = int(next(
    line.split()[1] for line in Path("/proc/meminfo").read_text().splitlines()
    if line.startswith("MemTotal:")
))
RESERVED_MEMORY_KB = int(TOTAL_MEMORY_KB * 0.20)
MEMORY_RESTART_HEADROOM_KB = 4 * 1024 * 1024
MIN_FREE_BYTES = 64 * 1024**3


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def cpu_snapshot() -> dict[str, int]:
    fields = Path("/proc/stat").read_text().splitlines()[0].split()
    values = [int(value) for value in fields[1:]]
    keys = ("user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal")
    return {key: values[index] if index < len(values) else 0 for index, key in enumerate(keys)}


def vm_snapshot() -> dict[str, int]:
    wanted = {"pgmajfault", "pswpin", "pswpout"}
    found: dict[str, int] = {}
    for line in Path("/proc/vmstat").read_text().splitlines():
        key, value = line.split()
        if key in wanted:
            found[key] = int(value)
    return found


def memory_snapshot() -> dict[str, int]:
    wanted = {"MemAvailable", "SwapFree"}
    found: dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, value, *_ = line.replace(":", "").split()
        if key in wanted:
            found[key] = int(value)
    return found


def disk_snapshot() -> int:
    """Return host-visible top-level NVMe read+write bytes (not B-exclusive)."""
    total_sectors = 0
    for line in Path("/proc/diskstats").read_text().splitlines():
        fields = line.split()
        if len(fields) < 14 or not re.fullmatch(r"nvme\d+n\d+", fields[2]):
            continue
        total_sectors += int(fields[5]) + int(fields[9])
    return total_sectors * 512


def snapshot() -> dict[str, Any]:
    return {
        "cpu": cpu_snapshot(), "vm": vm_snapshot(), "memory": memory_snapshot(),
        "disk_bytes": disk_snapshot(), "epoch": time.monotonic(),
    }


def delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, float]:
    total = sum(after["cpu"].values()) - sum(before["cpu"].values())
    busy = total - (after["cpu"]["idle"] - before["cpu"]["idle"])
    return {
        "wall_seconds": after["epoch"] - before["epoch"],
        "cpu_util_pct": (100.0 * busy / total) if total else 0.0,
        "iowait_pct": (100.0 * (after["cpu"]["iowait"] - before["cpu"]["iowait"]) / total) if total else 0.0,
        "major_faults": after["vm"].get("pgmajfault", 0) - before["vm"].get("pgmajfault", 0),
        "swapins": after["vm"].get("pswpin", 0) - before["vm"].get("pswpin", 0),
        "swapouts": after["vm"].get("pswpout", 0) - before["vm"].get("pswpout", 0),
        "storage_bytes": after["disk_bytes"] - before["disk_bytes"],
        "mem_available_min_kb": min(before["memory"].get("MemAvailable", 0), after["memory"].get("MemAvailable", 0)),
        "swap_free_min_kb": min(before["memory"].get("SwapFree", 0), after["memory"].get("SwapFree", 0)),
    }


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int((len(ordered) - 1) * fraction))]


def ensure_tsv(path: Path, fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="") as output:
            csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n").writeheader()


def append_tsv(path: Path, fields: list[str], row: dict[str, Any]) -> None:
    ensure_tsv(path, fields)
    with path.open("a", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writerow(row)


def physical_cpus() -> list[int]:
    rows = subprocess.check_output(["lscpu", "-p=CPU,CORE,SOCKET,NODE"], text=True).splitlines()
    chosen: list[int] = []
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        if row.startswith("#"):
            continue
        cpu, core, socket, node = row.split(",")
        identity = (core, socket, node)
        if identity not in seen:
            seen.add(identity)
            chosen.append(int(cpu))
    # Preserve 24 physical CPUs for the authoritative window and the OS.
    return [cpu for cpu in chosen if cpu >= 24]


def run_metrics(run_dir: Path) -> dict[str, str]:
    log = run_dir / "run.log"
    if not log.exists():
        return {"completed_kernels": "0", "telemetry_records": "0"}
    lines = log.read_text(errors="replace").splitlines()
    wanted = (
        "gpu_tot_sim_cycle", "gpu_tot_sim_insn", "gpu_tot_ipc", "vm_l1_tlb_accesses",
        "vm_l1_tlb_hits", "vm_l1_tlb_misses", "vm_l2_tlb_accesses", "vm_l2_tlb_hits",
        "vm_l2_tlb_misses", "vm_translation_mshr_allocations", "vm_translation_mshr_merges",
        "vm_translation_mshr_full_events", "vm_translation_pwq_full_events",
        "vm_translation_walk_starts", "vm_pwc_accesses", "vm_pwc_hits", "vm_pwc_misses",
        "vm_pte_requests", "vm_pte_responses", "vm_pte_response_misassociations",
        "vm_translation_waiter_registrations", "vm_translation_waiter_wakeups",
        "vm_object_attribution_conservation_pass",
    )
    result = {"completed_kernels": str(sum(line.startswith("Processing kernel ") for line in lines)),
              "telemetry_records": str(sum(line.startswith("m4c_telemetry_schema =") for line in lines))}
    for metric in wanted:
        prefix = metric + " = "
        values = [line[len(prefix):].strip() for line in lines if line.startswith(prefix)]
        result[metric] = values[-1] if values else "MISSING"
    return result


def runner_command(job: dict[str, str], args: argparse.Namespace, cpu: int, monitor: Path) -> list[str]:
    command = [
        "/usr/bin/time", "-v", "-o", str(monitor),
        "taskset", "-c", str(cpu), "nice", "-n", "10", "ionice", "-c", "3",
        str(args.runner), "--framework-root", str(args.framework_root), "--core-root", str(args.core_root),
        "--simulator", str(args.simulator), "--roi", job["roi"], "--profile", job["profile"],
        "--trace-list", job["trace_list"], "--trace-dir", job["trace_dir"],
        "--run-dir", job["run_dir"], "--max-kernels", job.get("max_kernels", "0"),
        "--telemetry-level", job.get("telemetry_level", "2"),
        "--window-transactions", job.get("window_transactions", "1000000"),
    ]
    extra = job.get("extra_config", "")
    if extra and extra != "NONE":
        command.extend(("--extra-config", extra))
    if "object_map" in job:
        command.extend(("--object-map", job["object_map"] or "NONE"))
    return command


@dataclass
class Active:
    job: dict[str, str]
    process: subprocess.Popen[str]
    started: float
    monitor: Path
    cpu: int
    stream: Any


REGISTRY_FIELDS = [
    "timestamp_utc", "window", "run_id", "evidence_label", "stage", "roi", "profile",
    "pid", "ppid", "cpu", "source_branch", "framework_head", "core_head", "run_dir",
    "trace_list", "trace_dir", "extra_config", "status", "start_utc", "end_utc",
    "exit_status", "command",
]
SUMMARY_FIELDS = [
    "run_id", "stage", "roi", "profile", "evidence_label", "status", "exit_status",
    "wall_seconds", "rss_kb", "major_faults", "completed_kernels", "telemetry_records",
    "gpu_tot_sim_cycle", "gpu_tot_sim_insn", "gpu_tot_ipc", "vm_l1_tlb_accesses",
    "vm_l1_tlb_hits", "vm_l1_tlb_misses", "vm_l2_tlb_accesses", "vm_l2_tlb_hits",
    "vm_l2_tlb_misses", "vm_translation_mshr_allocations", "vm_translation_mshr_merges",
    "vm_translation_mshr_full_events", "vm_translation_pwq_full_events",
    "vm_translation_walk_starts", "vm_pwc_accesses", "vm_pwc_hits", "vm_pwc_misses",
    "vm_pte_requests", "vm_pte_responses", "vm_pte_response_misassociations",
    "vm_translation_waiter_registrations", "vm_translation_waiter_wakeups",
    "vm_object_attribution_conservation_pass", "run_dir",
]


def read_time_v(path: Path) -> dict[str, str]:
    result = {"wall_seconds": "MISSING", "rss_kb": "MISSING", "major_faults": "MISSING"}
    if not path.exists():
        return result
    for line in path.read_text(errors="replace").splitlines():
        if "Elapsed (wall clock) time" in line:
            result["wall_seconds"] = line.rsplit(":", 1)[-1].strip()
        elif "Maximum resident set size" in line:
            result["rss_kb"] = line.rsplit(":", 1)[-1].strip()
        elif "Major (requiring I/O) page faults" in line:
            result["major_faults"] = line.rsplit(":", 1)[-1].strip()
    return result


def load_jobs(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"run_id", "stage", "roi", "profile", "trace_list", "trace_dir", "run_dir", "evidence_label"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit(f"FAIL jobs must contain {sorted(required)}")
    ids = [row["run_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("FAIL duplicate run_id in jobs")
    for row in rows:
        if Path(row["run_dir"]).exists():
            raise SystemExit(f"FAIL run directory already exists: {row['run_dir']}")
        if not Path(row["trace_list"]).is_file() or not Path(row["trace_dir"]).is_dir():
            raise SystemExit(f"FAIL missing immutable trace input for {row['run_id']}")
        if row.get("extra_config", "") not in ("", "NONE") and not Path(row["extra_config"]).is_file():
            raise SystemExit(f"FAIL missing extra config for {row['run_id']}")
    return rows


def dynamic_pressure(sample: dict[str, Any], prior: dict[str, Any], scratch: Path,
                     low_resource_peak_kb: int = 0, low_resource_span_kb: int = 0) -> tuple[bool, str]:
    change = delta(prior, sample)
    free_bytes = shutil.disk_usage(scratch).free
    if low_resource_peak_kb:
        # The low-resource margin is evidence-derived: two measured peaks plus
        # one observed host-memory swing, and never fewer than four peaks.
        # It is intentionally used only for a one-slot, pre-calibrated class.
        required = max(4 * low_resource_peak_kb,
                       low_resource_span_kb + 2 * low_resource_peak_kb)
        if sample["memory"].get("MemAvailable", 0) < required:
            return True, f"low_resource_memory_margin_below_{required}kb"
    elif sample["memory"].get("MemAvailable", 0) < RESERVED_MEMORY_KB + MEMORY_RESTART_HEADROOM_KB:
        return True, "memavailable_below_20pct_plus_4GiB_headroom"
    if change["swapins"] > 0 or change["swapouts"] > 0:
        return True, "new_swap_activity"
    if free_bytes < MIN_FREE_BYTES:
        return True, "scratch_below_64GiB"
    if change["iowait_pct"] > 15.0:
        return True, "iowait_above_15pct"
    return False, ""


def execute_jobs(jobs: list[dict[str, str]], args: argparse.Namespace, registry: Path, summary: Path,
                 max_slots: int) -> tuple[list[dict[str, str]], dict[str, Any]]:
    cpus = physical_cpus()
    if max_slots < 1 or max_slots > len(cpus):
        raise SystemExit(f"FAIL max_slots must be 1..{len(cpus)}")
    active: list[Active] = []
    completed: list[dict[str, str]] = []
    next_job = 0
    effective_slots = max_slots
    baseline = snapshot()
    previous = baseline
    pressure_events: list[str] = []
    while next_job < len(jobs) or active:
        sample = snapshot()
        pressured, reason = dynamic_pressure(sample, previous, args.scratch_root,
                                              args.low_resource_peak_kb,
                                              args.low_resource_span_kb)
        previous = sample
        if pressured and effective_slots > 1:
            effective_slots = max(1, effective_slots // 2)
            pressure_events.append(f"{now()}:{reason}:slots={effective_slots}")
        # Do not convert a host-pressure signal into even one new job.  Active
        # B-owned children are allowed to drain; fresh work resumes only after
        # the next snapshot is healthy.
        while not pressured and next_job < len(jobs) and len(active) < effective_slots:
            job = jobs[next_job]
            cpu = cpus[(next_job + len(active)) % len(cpus)]
            monitor = Path(job["run_dir"]).with_suffix(".time-v.txt")
            monitor.parent.mkdir(parents=True, exist_ok=True)
            command = runner_command(job, args, cpu, monitor)
            started_utc = now()
            stream = (Path(job["run_dir"]).with_suffix(".controller.stdout.log")).open("w")
            process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT, text=True)
            append_tsv(registry, REGISTRY_FIELDS, {
                "timestamp_utc": started_utc, "window": "B", "run_id": job["run_id"],
                "evidence_label": job["evidence_label"], "stage": job["stage"], "roi": job["roi"],
                "profile": job["profile"], "pid": process.pid, "ppid": os.getpid(), "cpu": cpu,
                "source_branch": "hrl/vm-spec-farm-v0", "framework_head": args.framework_head,
                "core_head": args.core_head, "run_dir": job["run_dir"], "trace_list": job["trace_list"],
                "trace_dir": job["trace_dir"], "extra_config": job.get("extra_config", "NONE"),
                "status": "STARTED", "start_utc": started_utc, "command": " ".join(command),
            })
            active.append(Active(job, process, time.monotonic(), monitor, cpu, stream))
            next_job += 1
        time.sleep(0.2)
        still_active: list[Active] = []
        for item in active:
            status = item.process.poll()
            if status is None:
                still_active.append(item)
                continue
            item.process.communicate()
            item.stream.close()
            run_dir = Path(item.job["run_dir"])
            run_dir.parent.mkdir(parents=True, exist_ok=True)
            # The runner normally owns this log.  If it failed before creating
            # one, keep only the controller's bounded diagnostic output.
            if not (run_dir / "run.log").exists():
                run_dir.mkdir(parents=True, exist_ok=True)
                controller_log = Path(item.job["run_dir"]).with_suffix(".controller.stdout.log")
                shutil.move(str(controller_log), str(run_dir / "controller_failure.log"))
            finished_utc = now()
            metrics = run_metrics(run_dir)
            timing = read_time_v(item.monitor)
            expected = sum(1 for line in Path(item.job["trace_list"]).read_text().splitlines() if line)
            valid = (
                status == 0 and int(metrics["completed_kernels"]) == expected and
                int(metrics["telemetry_records"]) == expected
            )
            label = item.job["evidence_label"]
            # Execution failure is a status, not an evidence label.  Every
            # Window-B artifact remains speculative even when its run failed.
            result_label = "SPECULATIVE_CANDIDATE" if valid and label == "SPECULATIVE_CANDIDATE" else "SPECULATIVE_DIAGNOSTIC"
            final_status = result_label if status == 0 else "FAILED"
            manifest = run_dir / "RUN_MANIFEST.tsv"
            if manifest.exists():
                with manifest.open("a") as output_file:
                    output_file.write(f"window\tB\nevidence_label\t{result_label}\nexecution_status\t{final_status}\nstage\t{item.job['stage']}\n")
            append_tsv(registry, REGISTRY_FIELDS, {
                "timestamp_utc": finished_utc, "window": "B", "run_id": item.job["run_id"],
                "evidence_label": result_label, "stage": item.job["stage"], "roi": item.job["roi"],
                "profile": item.job["profile"], "pid": item.process.pid, "ppid": os.getpid(), "cpu": item.cpu,
                "source_branch": "hrl/vm-spec-farm-v0", "framework_head": args.framework_head,
                "core_head": args.core_head, "run_dir": item.job["run_dir"], "trace_list": item.job["trace_list"],
                "trace_dir": item.job["trace_dir"], "extra_config": item.job.get("extra_config", "NONE"),
                "status": "FINISHED", "start_utc": "", "end_utc": finished_utc,
                "exit_status": status,
            })
            append_tsv(summary, SUMMARY_FIELDS, {
                "run_id": item.job["run_id"], "stage": item.job["stage"], "roi": item.job["roi"],
                "profile": item.job["profile"], "evidence_label": result_label, "status": final_status,
                "exit_status": status, **timing, **metrics, "run_dir": item.job["run_dir"],
            })
            completed.append({**item.job, "status": final_status, "exit_status": str(status), **timing, **metrics})
        active = still_active
    return completed, {"baseline": baseline, "final": snapshot(), "pressure_events": pressure_events, "effective_slots": effective_slots}


def calibrate(args: argparse.Namespace) -> None:
    levels = [int(value) for value in args.levels.split(",")]
    if levels != sorted(set(levels)) or any(value < 1 for value in levels):
        raise SystemExit("FAIL --levels must be strictly increasing positive integers")
    rows: list[dict[str, Any]] = []
    previous_throughput = 0.0
    frozen_slots = levels[-1]
    for level in levels:
        prefix = args.scratch_root / "runs" / f"b0-calibration-c{level}"
        jobs = []
        for index in range(level):
            jobs.append({
                "run_id": f"b0-cal-c{level}-{index:03d}", "stage": "B0_CALIBRATION", "roi": args.roi,
                "profile": "generic", "trace_list": str(args.trace_list), "trace_dir": str(args.trace_dir),
                "run_dir": str(prefix / f"job-{index:03d}"), "evidence_label": "SPECULATIVE_DIAGNOSTIC",
                "max_kernels": str(args.max_kernels), "telemetry_level": "1", "window_transactions": "1000000",
                "extra_config": "NONE",
            })
        started = snapshot()
        result, details = execute_jobs(jobs, args, args.registry, args.summary, level)
        finished = snapshot()
        host = delta(started, finished)
        rss = [float(row["rss_kb"]) for row in result if row["rss_kb"].isdigit()]
        passes = sum(row["status"] != "FAILED" for row in result)
        duration = max(host["wall_seconds"], 0.001)
        throughput = passes * args.max_kernels * 60.0 / duration
        gain_pct = ((throughput / previous_throughput - 1.0) * 100.0) if previous_throughput else 0.0
        pressure = ";".join(details["pressure_events"])
        row = {
            "requested_slots": level, "completed_jobs": passes, "failed_jobs": len(result) - passes,
            "wall_seconds": f"{duration:.3f}", "aggregate_kernels_per_minute": f"{throughput:.3f}",
            "throughput_gain_pct": f"{gain_pct:.3f}", "avg_rss_kb": f"{statistics.mean(rss) if rss else 0:.1f}",
            "p95_rss_kb": f"{percentile(rss, .95):.1f}", "cpu_util_pct": f"{host['cpu_util_pct']:.3f}",
            "iowait_pct": f"{host['iowait_pct']:.3f}", "major_faults": host["major_faults"],
            "swapins": host["swapins"], "swapouts": host["swapouts"],
            "storage_mib_per_second": f"{host['storage_bytes'] / duration / 1024**2:.3f}",
            "mem_available_min_kb": host["mem_available_min_kb"], "swap_free_min_kb": host["swap_free_min_kb"],
            "pressure_events": pressure or "NONE", "effective_slots_terminal": details["effective_slots"],
        }
        rows.append(row)
        pressure_stop = bool(pressure) or host["iowait_pct"] > 15.0 or host["swapins"] > 0 or host["swapouts"] > 0
        knee = previous_throughput > 0 and gain_pct < 20.0
        if pressure_stop or knee:
            frozen_slots = max(1, levels[max(0, levels.index(level) - 1)])
            break
        frozen_slots = level
        previous_throughput = throughput
    output = args.calibration_output
    if output.exists():
        raise SystemExit(f"FAIL refusing to overwrite calibration: {output}")
    fields = list(rows[0]) if rows else []
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    args.farm_limit_output.write_text(
        "FARM_CONCURRENCY_V1\t" + str(frozen_slots) + "\n"
        "policy\tone_physical_core_per_job; CPUs 0-23 reserved; dynamic backpressure halves slots\n"
        "evidence_label\tSPECULATIVE_DIAGNOSTIC\n"
    )
    print(f"PASS calibration={output} FARM_CONCURRENCY_V1={frozen_slots}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework-root", type=Path, required=True)
    parser.add_argument("--core-root", type=Path, required=True)
    parser.add_argument("--simulator", type=Path, required=True)
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--framework-head", required=True)
    parser.add_argument("--core-head", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    cal = sub.add_parser("calibrate")
    cal.add_argument("--roi", choices=("prefill", "decode1"), required=True)
    cal.add_argument("--trace-list", type=Path, required=True)
    cal.add_argument("--trace-dir", type=Path, required=True)
    cal.add_argument("--levels", default="16,32,64,128")
    cal.add_argument("--max-kernels", type=int, default=1)
    cal.add_argument("--calibration-output", type=Path, required=True)
    cal.add_argument("--farm-limit-output", type=Path, required=True)
    run = sub.add_parser("run-matrix")
    run.add_argument("--jobs", type=Path, required=True)
    run.add_argument("--max-slots", type=int, required=True)
    run.add_argument("--low-resource-peak-kb", type=int, default=0)
    run.add_argument("--low-resource-span-kb", type=int, default=0)
    args = parser.parse_args()
    if not args.simulator.is_file() or not args.runner.is_file():
        raise SystemExit("FAIL simulator or runner missing")
    args.scratch_root.mkdir(parents=True, exist_ok=True)
    if args.command == "calibrate":
        calibrate(args)
    else:
        if args.low_resource_peak_kb or args.low_resource_span_kb:
            if args.max_slots != 1 or args.low_resource_peak_kb < 1 or args.low_resource_span_kb < 0:
                raise SystemExit("FAIL low-resource mode requires max-slots=1, positive peak, nonnegative span")
        jobs = load_jobs(args.jobs)
        done, detail = execute_jobs(jobs, args, args.registry, args.summary, args.max_slots)
        failed = sum(row["status"] == "FAILED" for row in done)
        print(f"COMPLETE jobs={len(done)} failed={failed} terminal_slots={detail['effective_slots']}")
        if failed:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
