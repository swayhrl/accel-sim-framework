#!/usr/bin/env python3
"""Run and validate the frozen C12 C5 full-ROI matrix.

This tool never writes a simulator config, trace list, registration, or binary.
It executes only a verbatim C11 command-manifest row, preserves its raw log, and
then validates that immutable result.  A parser correction can use --validate or
--collect without replaying a simulator arm.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


FUNCTIONAL_FRAMEWORK = "d64408a97d76a320a6d49468653d416e33677af8"
CORE = "57bb71ecd015b6ec0ab32e45b0815e5beaf69172"
BINARY_SHA = "2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a"
PREFILL_TRACE = "a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f"
DECODE_TRACE = "b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc"
PREFILL_REG = "6ae0e18cc3bba29871002c4ff1877052489740163424723a845ead45c4a5f4b0"
DECODE_REG = "3dc77c1f348028ba7b8abfef3dc6c4cffa0c9678f003bc23bdc9158d62762b48"

RESULT_FIELDS = (
    "roi", "arm", "lseg", "terminal_status", "framework_anchor",
    "core_head", "binary_sha256", "config_sha256", "trace_sha256",
    "registration_sha256", "charged_bits", "gpu_tot_sim_cycle",
    "gpu_tot_sim_insn", "gpu_tot_ipc", "speedup_vs_f0",
    "vm_l1_tlb_accesses", "vm_l1_tlb_hits", "vm_l1_tlb_misses",
    "vm_l2_tlb_accesses", "vm_l2_tlb_hits", "vm_l2_tlb_misses",
    "vm_l2_tlb_evictions", "vm_l2_tlb_port_stalls",
    "vm_translation_mshr_allocations", "vm_translation_mshr_merges",
    "vm_translation_mshr_full_events",
    "vm_translation_requester_mshr_wait_cycles_total",
    "vm_translation_requester_latency_cycles_total",
    "vm_translation_requester_latency_cycles_max", "vm_translation_walk_starts",
    "vm_pte_requests", "vm_pte_responses", "vm_pte_l2_only_responses",
    "vm_pte_dram_responses", "vm_pte_memory_wait_cycles_total",
    "vm_pte_memory_wait_cycles_max", "vm_pwc_accesses", "vm_pwc_hits",
    "vm_pwc_misses", "vm_pwc_evictions", "segment_lookup_attempts",
    "segment_hits", "segment_l2_suppressed", "subentry_hits",
    "subentry_misses", "l1d_summary", "l2_summary", "l2_queue_summary",
    "native_memory_latency_summary", "object_conservation_pass",
    "pte_conservation_pass", "kernel_markers", "telemetry_records",
    "peak_rss_kb", "elapsed_seconds", "raw_log_sha256", "parser_version",
)

STATUS_FIELDS = (
    "roi", "arm", "lseg", "terminal_status", "attempt", "run_dir",
    "simulator_exit", "kernel_markers", "expected_kernels",
    "telemetry_records", "raw_log_sha256", "validation_json", "failure_summary",
)

LIVE_FIELDS = (
    "roi", "arm", "lseg", "state", "owner_pid", "simulator_pid",
    "lock_path", "attempt_id", "start_time", "current_kernel_markers",
    "expected_kernels", "binary_sha256", "config_sha256", "trace_sha256",
    "registration_sha256", "updated_utc",
)


def fail(message: str) -> None:
    raise SystemExit("C12 FAIL: " + message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def write_tsv(path: Path, fields: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t",
                                lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "NOT_EMITTED") for key in fields})


def write_tsv_atomic(path: Path, fields: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    """Atomically replace a live TSV so independent collectors cannot tear it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp." + str(os.getpid()))
    write_tsv(temporary, fields, rows)
    os.replace(temporary, path)


def arm_lock_path(point: dict[str, str]) -> Path:
    suffix = point["arm"].lower()
    if point["lseg"] != "NONE":
        suffix += "_lseg" + point["lseg"]
    return Path("/workspace/vm-m4b-speculative/c5-results/.arm_locks") / (
        point["roi"] + "__" + suffix + ".lock")


def owner_metadata_path(point: dict[str, str]) -> Path:
    """Keep orchestration ownership outside the immutable arm output root."""
    return Path("/workspace/vm-m4b-speculative/c12/arm_owners") / (
        arm_lock_path(point).stem + ".json")


def owner_metadata(point: dict[str, str]) -> dict[str, str]:
    path = owner_metadata_path(point)
    if path.is_file():
        try:
            return {str(name): str(value) for name, value in json.loads(path.read_text()).items()}
        except (OSError, ValueError, TypeError):
            return {}
    # P0 predates the per-arm launcher ownership sidecar.  Its lock guard is
    # the legal owner until the original C12 process naturally completes.
    guards = Path("/workspace/vm-m4b-speculative/c12/ARM_LOCK_GUARDS.tsv")
    if guards.is_file():
        try:
            for raw in guards.read_text().splitlines():
                values = raw.split("\t")
                if len(values) == 4 and values[1] == arm_lock_path(point).name:
                    return {"owner_pid": values[3], "attempt_id": "P0_LOCK_GUARD",
                            "start_time": values[0]}
        except OSError:
            pass
    return {}


def write_owner_metadata(point: dict[str, str], owner_pid: int) -> None:
    path = owner_metadata_path(point)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = {"schema": "C12_ARM_OWNER_V1", "owner_pid": str(owner_pid),
            "attempt_id": "%s-pid%s" % (now(), owner_pid), "start_time": now(),
            "lock_path": str(arm_lock_path(point)), "roi": point["roi"],
            "arm": point["arm"], "lseg": point["lseg"]}
    temporary = path.with_name(path.name + ".tmp." + str(os.getpid()))
    temporary.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def acquire_arm_locks(selected: list[tuple[str, str, str]],
                      points: dict[tuple[str, str, str], dict[str, str]]) -> list[Any]:
    """Acquire every selected arm before creating any simulator child."""
    handles: list[Any] = []
    try:
        for point_key in selected:
            path = arm_lock_path(points[point_key])
            path.parent.mkdir(parents=True, exist_ok=True)
            handle = path.open("a+")
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                handle.close()
                fail("per-arm lock already held: " + str(path))
            handles.append(handle)
        return handles
    except BaseException:
        for handle in handles:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            handle.close()
        raise


def release_arm_locks(handles: list[Any]) -> None:
    for handle in handles:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def simulator_pid(run_dir: str) -> str:
    """Find only an accel-sim child that names this exact arm output root."""
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            executable = os.readlink(proc / "exe")
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="ignore")
        except OSError:
            continue
        if Path(executable).name == "accel-sim.out" and run_dir in command:
            return proc.name
    return ""


def kernel_markers(run_dir: str) -> str:
    log = Path(run_dir) / "run.log"
    if not log.is_file():
        return "0"
    # The independent monitor calls this for every arm.  Do not materialize a
    # multi-hour full-ROI log merely to count its marker lines: that transient
    # allocation can itself perturb the host resource audit.  Streaming leaves
    # the count exact while bounding collector RSS.
    with log.open("r", errors="ignore") as source:
        return str(sum(1 for line in source if line.startswith("Processing kernel ")))


def f0_passed(points: dict[tuple[str, str, str], dict[str, str]]) -> bool:
    for roi in ("prefill", "decode1"):
        path = Path(points[(roi, "F0", "NONE")]["output_dir"]) / "C12_ARM_VALIDATION.json"
        if not path.is_file() or json.loads(path.read_text()).get("terminal_status") != "PASS":
            return False
    return True


def write_live_state(points: dict[tuple[str, str, str], dict[str, str]], review: Path) -> None:
    baseline_ready = f0_passed(points)
    rows: list[dict[str, Any]] = []
    for point in sorted(points.values(), key=lambda value: key(value)):
        run_dir = point["output_dir"]
        sim = simulator_pid(run_dir)
        validation = Path(run_dir) / "C12_ARM_VALIDATION.json"
        if sim:
            state = "RUNNING" if point["arm"] == "F0" else "SPECULATIVE_EARLY_EXECUTION_PENDING_BASELINE_GATE"
        elif validation.is_file():
            terminal = json.loads(validation.read_text()).get("terminal_status", "FAILED_RETRY")
            state = terminal if baseline_ready or point["arm"] == "F0" else "SPECULATIVE_EARLY_EXECUTION_PENDING_BASELINE_GATE"
        else:
            state = "NOT_STARTED"
        attempt = Path(run_dir) / "C12_ATTEMPT.json"
        owner = owner_metadata(point)
        attempt_id = owner.get("attempt_id", "1" if attempt.is_file() else "0")
        start = owner.get("start_time", "") or (dt.datetime.fromtimestamp(
            Path(run_dir).stat().st_mtime, dt.timezone.utc).isoformat() if Path(run_dir).exists() else "")
        rows.append({"roi": point["roi"], "arm": point["arm"], "lseg": point["lseg"],
                     "state": state, "owner_pid": owner.get("owner_pid", ""), "simulator_pid": sim,
                     "lock_path": str(arm_lock_path(point)), "attempt_id": attempt_id,
                     "start_time": start, "current_kernel_markers": kernel_markers(run_dir),
                     "expected_kernels": "692" if point["roi"] == "prefill" else "740",
                     "binary_sha256": point["binary_sha256"], "config_sha256": point["config_sha256"],
                     "trace_sha256": point["trace_list_sha256"],
                     "registration_sha256": point["registration_sha256"], "updated_utc": now()})
    write_tsv_atomic(review / "C12_LIVE_ARM_STATE.tsv", LIVE_FIELDS, rows)


def key(row: dict[str, str]) -> tuple[str, str, str]:
    return (row["roi"], row["arm"], row["lseg"])


def load_points(matrix_path: Path, command_path: Path) -> dict[tuple[str, str, str], dict[str, str]]:
    matrix = {key(row): row for row in read_tsv(matrix_path)}
    commands = {key(row): row for row in read_tsv(command_path)}
    if len(matrix) != 22 or len(commands) != 22 or set(matrix) != set(commands):
        fail("C11 primary matrix/command manifest is not a matching 22-point set")
    points: dict[tuple[str, str, str], dict[str, str]] = {}
    for point, row in matrix.items():
        cmd = commands[point]
        if row["config_path"] != cmd["config_path"]:
            fail("matrix/command config mismatch for " + "/".join(point))
        if row["config_sha256"] != cmd["config_sha256"]:
            fail("matrix/command config SHA mismatch for " + "/".join(point))
        if row["trace_list_sha256"] != cmd["trace_sha256"]:
            fail("matrix/command trace SHA mismatch for " + "/".join(point))
        if row["registration_sha256"] != cmd["registration_sha256"]:
            fail("matrix/command registration SHA mismatch for " + "/".join(point))
        if row["binary_sha256"] != cmd["binary_sha256"]:
            fail("matrix/command binary SHA mismatch for " + "/".join(point))
        points[point] = {**row, **{"command": cmd["exact_command"],
                                      "trace_list_path": cmd["trace_list"],
                                      "trace_root": cmd["trace_root"],
                                      "registration_path": cmd["registration_path"],
                                      "binary_path": cmd["binary"],
                                      "runtime_libcudart": cmd["runtime_libcudart"],
                                      "output_dir": cmd["output_dir"],
                                      "resume_policy": cmd["resume_policy"]}}
    return points


def expected(point: dict[str, str], name: str) -> str:
    return PREFILL_TRACE if point["roi"] == "prefill" else DECODE_TRACE if name == "trace" else ""


def verify_input_identity(point: dict[str, str], framework: Path, core: Path) -> None:
    roi, arm, lseg = key(point)
    name = "/".join((roi, arm, lseg))
    if point["framework_head"] != FUNCTIONAL_FRAMEWORK:
        fail(name + " framework anchor differs from frozen identity")
    if point["core_head"] != CORE or subprocess.check_output(
            ["git", "-C", str(core), "rev-parse", "HEAD"], text=True).strip() != CORE:
        fail(name + " core identity differs from frozen identity")
    binary = Path(point["binary_path"])
    if point["binary_sha256"] != BINARY_SHA or sha256(binary) != BINARY_SHA:
        fail(name + " binary identity differs from frozen identity")
    config = framework / point["config_path"]
    if sha256(config) != point["config_sha256"]:
        fail(name + " config hash differs from C11 manifest")
    trace = Path(point["trace_list_path"])
    trace_expected = PREFILL_TRACE if roi == "prefill" else DECODE_TRACE
    if point["trace_list_sha256"] != trace_expected or sha256(trace) != trace_expected:
        fail(name + " trace-list hash differs from frozen identity")
    listed = [line.strip() for line in trace.read_text().splitlines() if line.strip()]
    kernels = 692 if roi == "prefill" else 740
    if len(listed) != kernels or len(set(listed)) != len(listed):
        fail(name + " trace-list cardinality/duplicate check failed")
    root = Path(point["trace_root"])
    if any(".." in Path(item).parts or not (root / item).is_file() for item in listed):
        fail(name + " has a missing or unsafe trace entry")
    registration = framework / point["registration_path"]
    registration_expected = PREFILL_REG if roi == "prefill" else DECODE_REG
    if point["registration_sha256"] != registration_expected or sha256(registration) != registration_expected:
        fail(name + " registration hash differs from frozen identity")
    if arm in ("F3", "F4", "F6", "H0"):
        fail(name + " is excluded from C12 primary execution")


def final_values(log: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in log.read_text(errors="strict").splitlines():
        if " = " not in raw:
            continue
        name, value = raw.split(" = ", 1)
        if name.startswith("vm_") or name in ("gpu_tot_sim_cycle", "gpu_tot_sim_insn", "gpu_tot_ipc"):
            values[name.strip()] = value.strip()
    return values


def integer(values: dict[str, str], name: str, errors: list[str]) -> int | None:
    raw = values.get(name)
    if raw is None:
        errors.append("NOT_EMITTED:" + name)
        return None
    try:
        return int(raw)
    except ValueError:
        errors.append("NONINTEGER:" + name + "=" + raw)
        return None


def finite_float(values: dict[str, str], name: str, errors: list[str]) -> float | None:
    """Validate scalar rate/statistics fields that are intentionally nonintegral."""
    raw = values.get(name)
    if raw is None:
        errors.append("NOT_EMITTED:" + name)
        return None
    try:
        value = float(raw)
    except ValueError:
        errors.append("NONNUMERIC:" + name + "=" + raw)
        return None
    if not math.isfinite(value):
        errors.append("NONFINITE:" + name + "=" + raw)
        return None
    return value


def require_equal(values: dict[str, str], left: str, right: str, errors: list[str]) -> None:
    lval, rval = integer(values, left, errors), integer(values, right, errors)
    if lval is not None and rval is not None and lval != rval:
        errors.append(left + "!=" + right)


def require_sum(values: dict[str, str], total: str, parts: tuple[str, ...], errors: list[str]) -> None:
    total_value = integer(values, total, errors)
    part_values = [integer(values, part, errors) for part in parts]
    if total_value is not None and all(value is not None for value in part_values):
        if total_value != sum(value for value in part_values if value is not None):
            errors.append(total + "!=" + "+".join(parts))


def time_metrics(log_lines: list[str]) -> tuple[str, str]:
    rss = "NOT_EMITTED"
    elapsed = "NOT_EMITTED"
    for line in log_lines:
        match = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", line)
        if match:
            rss = match.group(1)
        stripped = line.lstrip()
        if stripped.startswith("Elapsed (wall clock) time") and "):" in stripped:
            # GNU time's label itself contains ':' characters (h:mm:ss or m:ss),
            # so split at the final label terminator rather than a greedy regex.
            text = stripped.rpartition("):")[2].strip()
            try:
                fields = text.split(":")
                if len(fields) == 3:
                    hours, minutes, seconds = (float(value) for value in fields)
                    elapsed = str(hours * 3600.0 + minutes * 60.0 + seconds)
                elif len(fields) == 2:
                    minutes, seconds = (float(value) for value in fields)
                    elapsed = str(minutes * 60.0 + seconds)
                else:
                    elapsed = str(float(text))
            except ValueError:
                elapsed = "NOT_EMITTED"
    return rss, elapsed


def telemetry_summary(lines: list[str]) -> tuple[str, str, str, str]:
    l1 = sum(1 for line in lines if line.startswith("m4c_telemetry\tKERNEL\t"))
    l2 = sum(1 for line in lines if line.startswith("m4c_telemetry_l2\tKERNEL\t"))
    queue = sum(1 for line in lines if line.startswith("m4c_telemetry_l2_queue\tKERNEL\t"))
    native = []
    for name in ("averagemflatency", "avg_icnt2mem_latency", "avg_mrq_latency", "avg_icnt2sh_latency"):
        matches = [line.split("=", 1)[1].strip() for line in lines if line.startswith(name + " =")]
        if matches:
            native.append(name + "=" + matches[-1])
    return ("kernel_records=" + str(l1), "kernel_records=" + str(l2),
            "kernel_records=" + str(queue), ";".join(native) if native else "NOT_EMITTED")


def write_run_manifest(run_dir: Path, point: dict[str, str], exit_code: int) -> None:
    entries = {
        "schema": "C12_C5_RUN_MANIFEST_V1",
        "roi": point["roi"], "arm": point["arm"], "lseg": point["lseg"],
        "framework_anchor": FUNCTIONAL_FRAMEWORK, "framework_head": FUNCTIONAL_FRAMEWORK,
        "core_head": CORE,
        "binary_sha256": BINARY_SHA, "config_path": point["config_path"],
        "config_sha256": point["config_sha256"], "trace_list_path": point["trace_list_path"],
        "trace_sha256": point["trace_list_sha256"], "registration_path": point["registration_path"],
        "registration_sha256": point["registration_sha256"],
        "simulator_exit_status": str(exit_code), "command_manifest": "C11_C5_COMMAND_MANIFEST.tsv",
        "written_utc": now(),
    }
    with (run_dir / "RUN_MANIFEST.tsv").open("w", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow(("key", "value"))
        writer.writerows(entries.items())


def extract_time_sidecar(run_dir: Path) -> None:
    log = run_dir / "run.log"
    if not log.is_file():
        return
    lines = log.read_text(errors="strict").splitlines()
    starts = [index for index, line in enumerate(lines) if line.lstrip().startswith("Command being timed:")]
    if starts:
        (run_dir / "time-v.txt").write_text("\n".join(lines[starts[-1]:]) + "\n")


def validate_run(point: dict[str, str], framework: Path, run_dir: Path,
                 exit_code: int | None = None) -> dict[str, Any]:
    log = run_dir / "run.log"
    errors: list[str] = []
    if not log.is_file():
        errors.append("missing:run.log")
        lines: list[str] = []
        values: dict[str, str] = {}
    else:
        lines = log.read_text(errors="strict").splitlines()
        values = final_values(log)
    attempt_path = run_dir / "C12_ATTEMPT.json"
    if exit_code is None and attempt_path.is_file():
        exit_code = int(json.loads(attempt_path.read_text())["exit_code"])
    if exit_code is None:
        errors.append("missing:exit_code")
        exit_code = 999
    expected_kernels = 692 if point["roi"] == "prefill" else 740
    markers = sum(1 for line in lines if line.startswith("Processing kernel "))
    telemetry = sum(1 for line in lines if line.startswith("m4c_telemetry_schema ="))
    if exit_code != 0:
        errors.append("simulator_exit=" + str(exit_code))
    if markers != expected_kernels:
        errors.append("kernel_markers=%d/%d" % (markers, expected_kernels))
    if telemetry != expected_kernels:
        errors.append("telemetry_records=%d/%d" % (telemetry, expected_kernels))
    if "m4c_telemetry_schema = M4C_MEMORY_TELEMETRY_V1" not in lines:
        errors.append("missing:M4C_MEMORY_TELEMETRY_V1")
    for metric in ("gpu_tot_sim_cycle", "gpu_tot_sim_insn",
                   "vm_l1_tlb_accesses", "vm_l1_tlb_hits", "vm_l1_tlb_misses",
                   "vm_l2_tlb_accesses", "vm_l2_tlb_hits", "vm_l2_tlb_misses",
                   "vm_l2_tlb_evictions", "vm_l2_tlb_port_stalls",
                   "vm_translation_mshr_allocations", "vm_translation_mshr_merges",
                   "vm_translation_mshr_full_events",
                   "vm_translation_requester_mshr_wait_cycles_total",
                   "vm_translation_requester_latency_cycles_total",
                   "vm_translation_requester_latency_cycles_max", "vm_translation_walk_starts",
                   "vm_pte_requests", "vm_pte_responses", "vm_pte_l2_only_responses",
                   "vm_pte_dram_responses", "vm_pte_memory_wait_cycles_total",
                   "vm_pte_memory_wait_cycles_max", "vm_pwc_accesses", "vm_pwc_hits",
                   "vm_pwc_misses", "vm_pwc_evictions", "vm_object_attribution_conservation_pass",
                   "vm_translation_mshr_active", "vm_translation_pwq_occupancy",
                   "vm_translation_walkers_active"):
        integer(values, metric, errors)
    finite_float(values, "gpu_tot_ipc", errors)
    require_sum(values, "vm_l1_tlb_accesses", ("vm_l1_tlb_hits", "vm_l1_tlb_misses"), errors)
    require_sum(values, "vm_l2_tlb_accesses", ("vm_l2_tlb_hits", "vm_l2_tlb_misses"), errors)
    require_equal(values, "vm_pte_requests", "vm_pte_responses", errors)
    require_sum(values, "vm_pte_responses", ("vm_pte_l2_only_responses", "vm_pte_dram_responses"), errors)
    require_sum(values, "vm_pwc_accesses", ("vm_pwc_hits", "vm_pwc_misses"), errors)
    require_equal(values, "vm_translation_mshr_allocations", "vm_translation_mshr_entries_completed", errors)
    require_equal(values, "vm_translation_waiter_registrations", "vm_translation_waiter_wakeups", errors)
    for metric in ("vm_translation_mshr_active", "vm_translation_pwq_occupancy", "vm_translation_walkers_active",
                   "vm_pte_response_misassociations"):
        value = integer(values, metric, errors)
        if value is not None and value != 0:
            errors.append(metric + "!=0")
    if values.get("vm_object_attribution_conservation_pass") != "1":
        errors.append("object_attribution_conservation!=1")
    if values.get("vm_fair_arm_name") != point["arm"]:
        errors.append("fair_arm_name=" + values.get("vm_fair_arm_name", "MISSING"))
    if values.get("vm_fair_arm_charged_bits") != point["charged_bits"]:
        errors.append("fair_arm_charged_bits mismatch")

    arm = point["arm"]
    if arm in ("F0", "F2", "F5", "F9", "F1"):
        for metric in ("vm_weight_segmentation_enabled", "vm_weight_segment_lookup_attempts",
                       "vm_weight_segment_hits", "vm_weight_segment_l2_suppressed"):
            value = integer(values, metric, errors)
            if value is not None and value != 0:
                errors.append(arm + ":" + metric + " must be zero")
    if arm == "F1":
        if values.get("vm_l2_tlb_subentry_schema") != "REFERENCE_APPROX_SUBENTRY_16":
            errors.append("F1 subentry schema")
        if integer(values, "vm_l2_tlb_subentry_group_entries", errors) != 96:
            errors.append("F1 G96 geometry")
    if arm == "F5":
        for metric, expected_value in (("vm_pwc_physical_f5_enabled", 1),
                                       ("vm_pwc_physical_f5_entries_total", 120),
                                       ("vm_pwc_physical_f5_entries_per_nonleaf_level", 40),
                                       ("vm_pwc_physical_f5_ways", 4),
                                       # This counter is the physical PWC payload itself.
                                       # The C5 matrix separately charges the complete F5 arm
                                       # (PWC plus its exact-TLB remainder) at 64745 bits.
                                       ("vm_pwc_physical_f5_charged_bits", 8370)):
            if integer(values, metric, errors) != expected_value:
                errors.append("F5 " + metric + " geometry")
    if arm in ("F7", "F8"):
        for metric, expected_value in (("vm_weight_segmentation_enabled", 1),
                                       ("vm_weight_segment_entries_configured", 8),
                                       ("vm_weight_segment_local_table_replicas", 35),
                                       ("vm_weight_segment_lookup_latency_cycles", int(point["lseg"]))):
            if integer(values, metric, errors) != expected_value:
                errors.append(arm + " " + metric + " invariant")
        if values.get("vm_weight_segment_lifecycle_state") != "ACTIVE":
            errors.append(arm + " Segment not ACTIVE")
        attempts = integer(values, "vm_weight_segment_lookup_attempts", errors)
        hits = integer(values, "vm_weight_segment_hits", errors)
        misses = integer(values, "vm_weight_segment_misses", errors)
        completions = integer(values, "vm_weight_segment_lookup_completions", errors)
        launches = integer(values, "vm_weight_segment_lookup_launches", errors)
        late_discards = integer(values, "vm_weight_segment_late_result_discards", errors)
        # HIT_FIRST / MISS_JOIN permits a checked late shadow in either
        # direction.  A Segment-first hit can complete while its L1 shadow is
        # discarded; an L1-first hit can discard an unresolved Segment shadow.
        # Thus late_result_discards is intentionally not a disjoint remainder
        # of completions: it may overlap a completed Segment hit or denote an
        # unresolved cancellation.  Completions alone partition into hit/miss.
        if (attempts is not None and launches is not None and completions is not None
                and hits is not None and misses is not None and late_discards is not None):
            if attempts == 0 or attempts != launches:
                errors.append(arm + " Segment attempt/launch conservation")
            if completions != hits + misses:
                errors.append(arm + " Segment completion hit/miss conservation")
            if completions > attempts:
                errors.append(arm + " Segment completions exceed attempts")
            if late_discards > attempts:
                errors.append(arm + " Segment late-discard bound")
        if arm == "F8":
            if values.get("vm_l2_tlb_subentry_schema") != "REFERENCE_APPROX_SUBENTRY_16":
                errors.append("F8 subentry schema")
            if integer(values, "vm_l2_tlb_subentry_group_entries", errors) != 32:
                errors.append("F8 G32 geometry")
        else:
            if integer(values, "vm_fair_l2_entries_realized", errors) != 320:
                errors.append("F7 exact-320 geometry")
    if arm in ("F1", "F8"):
        require_sum(values, "vm_l2_tlb_subentry_base_tag_hits",
                    ("vm_l2_tlb_subentry_hits", "vm_l2_tlb_subentry_misses"), errors)
    if not any(line.startswith("m4c_telemetry_l2_queue\tKERNEL\t") for line in lines):
        errors.append("missing:L2_QUEUE telemetry")
    if not any(line.startswith("m4c_telemetry_dram\tKERNEL\t") for line in lines):
        errors.append("missing:DRAM telemetry")

    rss, elapsed = time_metrics(lines)
    l1d, l2, queue, native = telemetry_summary(lines)
    parser_hash = sha256(Path(__file__).resolve())
    result: dict[str, Any] = {
        "roi": point["roi"], "arm": arm, "lseg": point["lseg"],
        "terminal_status": "PASS" if not errors else "FAILED_DIAGNOSING",
        "framework_anchor": FUNCTIONAL_FRAMEWORK, "core_head": CORE,
        "binary_sha256": BINARY_SHA, "config_sha256": point["config_sha256"],
        "trace_sha256": point["trace_list_sha256"], "registration_sha256": point["registration_sha256"],
        "charged_bits": point["charged_bits"], "speedup_vs_f0": "BASELINE_PENDING",
        "segment_lookup_attempts": values.get("vm_weight_segment_lookup_attempts", "NOT_EMITTED"),
        "segment_hits": values.get("vm_weight_segment_hits", "NOT_EMITTED"),
        "segment_l2_suppressed": values.get("vm_weight_segment_l2_suppressed", "NOT_EMITTED"),
        "subentry_hits": values.get("vm_l2_tlb_subentry_hits", "NOT_EMITTED"),
        "subentry_misses": values.get("vm_l2_tlb_subentry_misses", "NOT_EMITTED"),
        "l1d_summary": l1d, "l2_summary": l2, "l2_queue_summary": queue,
        "native_memory_latency_summary": native,
        "object_conservation_pass": values.get("vm_object_attribution_conservation_pass", "NOT_EMITTED"),
        "pte_conservation_pass": "PASS" if not any("vm_pte_" in item for item in errors) else "FAIL",
        "kernel_markers": str(markers), "telemetry_records": str(telemetry),
        "peak_rss_kb": rss, "elapsed_seconds": elapsed,
        "raw_log_sha256": sha256(log) if log.is_file() else "MISSING",
        "parser_version": parser_hash, "errors": errors,
        "run_dir": str(run_dir), "simulator_exit": str(exit_code), "validated_utc": now(),
    }
    for field in RESULT_FIELDS:
        if field.startswith("vm_") or field.startswith("gpu_"):
            result[field] = values.get(field, "NOT_EMITTED")
    (run_dir / "C12_ARM_VALIDATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def resource_sample() -> dict[str, Any]:
    meminfo: dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        name, value, *_ = line.replace(":", "").split()
        meminfo[name] = int(value)
    def psi(kind: str) -> float:
        for line in Path("/proc/pressure/" + kind).read_text().splitlines():
            if line.startswith("full "):
                return float(re.search(r"avg10=([0-9.]+)", line).group(1))
        return math.nan
    vmstat = {parts[0]: int(parts[1]) for parts in
              (line.split() for line in Path("/proc/vmstat").read_text().splitlines()) if len(parts) == 2}
    cpu = Path("/proc/stat").read_text().splitlines()[0].split()
    cpu_ticks = [int(value) for value in cpu[1:] if value.isdigit()]
    workers: list[str] = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            executable = os.readlink(proc / "exe")
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="ignore")
            if Path(executable).name != "accel-sim.out" or "/workspace/vm-m4b-speculative/c5-results/C11_AUTHORIZED_NOT_RUN/" not in command:
                continue
            status = (proc / "status").read_text(errors="ignore")
            rss = next((line.split()[1] for line in status.splitlines() if line.startswith("VmRSS:")), "0")
            workers.append(proc.name + ":" + rss)
        except OSError:
            continue
    load1, load5, load15 = os.getloadavg()
    return {"utc": now(), "mem_available_kb": meminfo.get("MemAvailable", -1),
            "swap_free_kb": meminfo.get("SwapFree", -1), "memory_psi_full_avg10": psi("memory"),
            "io_psi_full_avg10": psi("io"), "pswpin": vmstat.get("pswpin", -1),
            "pswpout": vmstat.get("pswpout", -1), "cpu_iowait_ticks": cpu[5] if len(cpu) > 5 else "-1",
            "cpu_total_ticks": sum(cpu_ticks), "loadavg_1": "%.2f" % load1,
            "loadavg_5": "%.2f" % load5, "loadavg_15": "%.2f" % load15,
            "c12_simulator_count": len(workers), "c12_worker_rss_kb": ";".join(sorted(workers))}


def append_resource(path: Path, phase: str) -> None:
    sample = resource_sample()
    sample["swap_in_mib_s"] = "NOT_APPLICABLE_FIRST_SAMPLE"
    sample["swap_out_mib_s"] = "NOT_APPLICABLE_FIRST_SAMPLE"
    sample["cpu_iowait_pct"] = "NOT_APPLICABLE_FIRST_SAMPLE"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", newline="") as output:
        fcntl.flock(output.fileno(), fcntl.LOCK_EX)
        try:
            output.seek(0)
            prior = list(csv.DictReader(output, delimiter="\t"))
            if prior:
                previous = prior[-1]
                try:
                    seconds = max(0.001, (dt.datetime.fromisoformat(str(sample["utc"])) -
                                          dt.datetime.fromisoformat(previous["utc"])).total_seconds())
                    pages_to_mib = os.sysconf("SC_PAGE_SIZE") / (1024.0 * 1024.0)
                    sample["swap_in_mib_s"] = "%.6f" % ((int(sample["pswpin"]) - int(previous["pswpin"])) * pages_to_mib / seconds)
                    sample["swap_out_mib_s"] = "%.6f" % ((int(sample["pswpout"]) - int(previous["pswpout"])) * pages_to_mib / seconds)
                    total_delta = int(sample["cpu_total_ticks"]) - int(previous["cpu_total_ticks"])
                    wait_delta = int(sample["cpu_iowait_ticks"]) - int(previous["cpu_iowait_ticks"])
                    sample["cpu_iowait_pct"] = "%.4f" % (100.0 * wait_delta / total_delta) if total_delta > 0 else "0.0000"
                except (KeyError, TypeError, ValueError, OverflowError):
                    sample["swap_in_mib_s"] = "DELTA_UNAVAILABLE"
                    sample["swap_out_mib_s"] = "DELTA_UNAVAILABLE"
                    sample["cpu_iowait_pct"] = "DELTA_UNAVAILABLE"
            output.seek(0, os.SEEK_END)
            writer = csv.DictWriter(output, fieldnames=("phase", *sample.keys()), delimiter="\t", lineterminator="\n")
            if not prior:
                writer.writeheader()
            writer.writerow({"phase": phase, **sample})
        finally:
            fcntl.flock(output.fileno(), fcntl.LOCK_UN)


def execute(points: dict[tuple[str, str, str], dict[str, str]], selected: list[tuple[str, str, str]],
            framework: Path, core: Path, review: Path, resource_history: Path) -> int:
    processes: dict[tuple[str, str, str], subprocess.Popen[str]] = {}
    for point_key in selected:
        point = points[point_key]
        verify_input_identity(point, framework, core)
        output = Path(point["output_dir"])
        if output.exists():
            fail("fresh-output policy refuses existing " + str(output))
    append_resource(resource_history, "batch_before_launch")
    sample = resource_sample()
    if sample["mem_available_kb"] < 32 * 1024 * 1024 or sample["memory_psi_full_avg10"] > 1.0 or sample["io_psi_full_avg10"] > 2.0:
        fail("resource gate is not GREEN before batch launch")
    locks = acquire_arm_locks(selected, points)
    try:
        for point_key in selected:
            point = points[point_key]
            write_owner_metadata(point, os.getpid())
            command = "set -o pipefail; " + point["command"]
            # The frozen command already tee's the simulator stream into run.log.
            # Suppress its duplicate terminal copy so a long full-ROI log cannot
            # truncate the orchestration channel; raw evidence remains unchanged.
            processes[point_key] = subprocess.Popen(
                ["bash", "-lc", command], text=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        collect(points, review)
        remaining = set(processes)
        next_sample = time.monotonic() + 30.0
        results: list[dict[str, Any]] = []
        while remaining:
            for point_key in list(remaining):
                process = processes[point_key]
                code = process.poll()
                if code is None:
                    continue
                remaining.remove(point_key)
                point = points[point_key]
                run_dir = Path(point["output_dir"])
                if run_dir.is_dir():
                    (run_dir / "C12_ATTEMPT.json").write_text(json.dumps({
                        "schema": "C12_ATTEMPT_V1", "exit_code": code, "finished_utc": now(),
                        "command_manifest_command": point["command"],
                    }, indent=2, sort_keys=True) + "\n")
                    write_run_manifest(run_dir, point, code)
                    extract_time_sidecar(run_dir)
                    results.append(validate_run(point, framework, run_dir, code))
                else:
                    results.append({"roi": point["roi"], "arm": point["arm"], "lseg": point["lseg"],
                                    "terminal_status": "FAILED_DIAGNOSING", "errors": ["launcher created no run directory"],
                                    "run_dir": str(run_dir), "simulator_exit": str(code), "validated_utc": now()})
                collect(points, review)
            if time.monotonic() >= next_sample:
                append_resource(resource_history, "batch_running")
                next_sample += 30.0
            if remaining:
                time.sleep(5)
        append_resource(resource_history, "batch_complete")
        return 0 if all(row.get("terminal_status") == "PASS" for row in results) else 1
    finally:
        release_arm_locks(locks)


def load_validations(points: dict[tuple[str, str, str], dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for point in points.values():
        validation = Path(point["output_dir"]) / "C12_ARM_VALIDATION.json"
        if validation.is_file():
            rows.append(json.loads(validation.read_text()))
        else:
            rows.append({"roi": point["roi"], "arm": point["arm"], "lseg": point["lseg"],
                         "terminal_status": "PENDING", "run_dir": point["output_dir"], "errors": []})
    return sorted(rows, key=lambda row: (row["roi"], row["arm"], str(row["lseg"])))


def collect(points: dict[tuple[str, str, str], dict[str, str]], review: Path) -> None:
    """Serialize a complete snapshot, not merely its final file replacement.

    Atomic ``os.replace`` prevents a torn TSV, but several independent C12
    launchers can otherwise each derive a snapshot from a different instant.
    Without this lock, an older observation can be written after a newer arm
    completion and regress a terminal arm to ``NOT_STARTED`` in the live table.
    The lock covers read/derive/write only; it neither owns nor signals a
    simulator and therefore cannot alter experiment execution semantics.
    """
    review.mkdir(parents=True, exist_ok=True)
    lock_path = review / "C12_COLLECT.lock"
    with lock_path.open("a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            _collect_locked(points, review)
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _collect_locked(points: dict[tuple[str, str, str], dict[str, str]], review: Path) -> None:
    rows = load_validations(points)
    f0_cycles: dict[str, float] = {}
    for row in rows:
        if row.get("terminal_status") == "PASS" and row["arm"] == "F0":
            try:
                f0_cycles[row["roi"]] = float(row["gpu_tot_sim_cycle"])
            except (KeyError, ValueError):
                pass
    result_rows: list[dict[str, Any]] = []
    status_rows: list[dict[str, Any]] = []
    raw_index: list[dict[str, Any]] = []
    for row in rows:
        result = dict(row)
        if result.get("terminal_status") == "PASS" and result.get("roi") in f0_cycles:
            try:
                result["speedup_vs_f0"] = "%.9f" % (f0_cycles[result["roi"]] / float(result["gpu_tot_sim_cycle"]))
            except (KeyError, ValueError, ZeroDivisionError):
                result["speedup_vs_f0"] = "NOT_EMITTED"
        elif result.get("terminal_status") != "PASS":
            result["speedup_vs_f0"] = "NOT_VALID"
        else:
            result["speedup_vs_f0"] = "BASELINE_PENDING"
        result_rows.append(result)
        errors = result.get("errors", [])
        status_rows.append({"roi": result["roi"], "arm": result["arm"], "lseg": result["lseg"],
                            "terminal_status": result.get("terminal_status", "PENDING"),
                            "attempt": "1" if result.get("terminal_status") != "PENDING" else "0",
                            "run_dir": result.get("run_dir", "NOT_RUN"),
                            "simulator_exit": result.get("simulator_exit", "NOT_RUN"),
                            "kernel_markers": result.get("kernel_markers", "NOT_RUN"),
                            "expected_kernels": "692" if result["roi"] == "prefill" else "740",
                            "telemetry_records": result.get("telemetry_records", "NOT_RUN"),
                            "raw_log_sha256": result.get("raw_log_sha256", "NOT_RUN"),
                            "validation_json": str(Path(result.get("run_dir", "")) / "C12_ARM_VALIDATION.json"),
                            "failure_summary": ";".join(errors) if errors else ""})
        if result.get("raw_log_sha256") not in (None, "NOT_RUN", "MISSING"):
            raw_index.append({"roi": result["roi"], "arm": result["arm"], "lseg": result["lseg"],
                              "run_dir": result.get("run_dir", ""), "raw_log": str(Path(result.get("run_dir", "")) / "run.log"),
                              "raw_log_sha256": result["raw_log_sha256"], "time_sidecar": str(Path(result.get("run_dir", "")) / "time-v.txt")})
    # P0, an aggressive batch extension, and the independent monitor may all
    # observe completions.  Every live aggregate must therefore be replace-only.
    write_tsv_atomic(review / "ARM_STATUS.tsv", STATUS_FIELDS, status_rows)
    write_tsv_atomic(review / "ARM_RESULTS.tsv", RESULT_FIELDS, result_rows)
    write_tsv_atomic(review / "RAW_LOG_INDEX.tsv", ("roi", "arm", "lseg", "run_dir", "raw_log", "raw_log_sha256", "time_sidecar"), raw_index)
    write_live_state(points, review)


def parse_point(text: str) -> tuple[str, str, str]:
    parts = text.split(":")
    if len(parts) != 3:
        fail("point must be roi:arm:lseg, got " + text)
    return tuple(parts)  # type: ignore[return-value]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework", type=Path, required=True)
    parser.add_argument("--core", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--commands", type=Path, required=True)
    parser.add_argument("--review-pack", type=Path, required=True)
    parser.add_argument("--resource-history", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--monitor", action="store_true",
                        help="write precise 30-second live resource/state samples while C12 workers exist")
    parser.add_argument("--point", action="append", default=[])
    args = parser.parse_args()
    if not (args.execute or args.validate or args.collect or args.monitor):
        fail("choose --execute, --validate, --collect, or --monitor")
    points = load_points(args.matrix, args.commands)
    if args.point:
        selected = [parse_point(item) for item in args.point]
        if any(item not in points for item in selected):
            fail("selected point is not in the frozen primary matrix")
    else:
        selected = sorted(points)
    if args.execute:
        sys.exit(execute(points, selected, args.framework, args.core, args.review_pack, args.resource_history))
    if args.validate:
        for item in selected:
            point = points[item]
            validate_run(point, args.framework, Path(point["output_dir"]))
        collect(points, args.review_pack)
    if args.collect:
        collect(points, args.review_pack)
    if args.monitor:
        # Independent monitoring is deliberately non-invasive: it neither owns
        # nor signals workers, and its atomic live table can coexist with an
        # executing batch collector.
        while True:
            append_resource(args.resource_history, "independent_live_monitor")
            collect(points, args.review_pack)
            if resource_sample()["c12_simulator_count"] == 0:
                break
            time.sleep(30)
    print("C12 parser/collector PASS points=" + str(len(selected)))


if __name__ == "__main__":
    main()
