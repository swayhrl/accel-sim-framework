#!/usr/bin/env python3
"""Resumable, single-heavy-worker supervisor for B11 frozen E01--E10.

The supervisor deliberately owns only Window-B scratch.  It does not inspect
or manipulate another window's worktree/processes.  It gates each frozen B9
heavy job with a ten-second host sample and a shared advisory flock, records
all waits, and invokes the previously validated B9 launcher unchanged except
for its safe valid-arm resume option.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import fcntl
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, Tuple


FRAMEWORK = Path(__file__).resolve().parents[2]
SCRATCH_DEFAULT = Path("/workspace/vm-spec-farm")
ATTESTATION_DEFAULT = Path("/workspace/m4c-c3-formal-20260905-v1/A_TERMINAL_ATTESTATION.txt")
LOCK_PATH = Path("/workspace/vm_tlb_post_terminal_heavy_slot.lock")
EXPECTED_BINARY = "2d6f825faf71e4aa9acc8d62e98186c9d7c1a92ecd2c41cbfd108e918de44915"
TASKS = ("E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10")
SIM_ARMS = {
    "E01": ("E01-generic", "E01-pwc32"),
    "E02": ("E02-generic", "E02-pwc512"),
    "E03": ("E03-generic", "E03-pwcideal"),
    "E04": ("E04-generic64k", "E04-page2mb"),
    "E05": ("E05-generic", "E05-disabled"),
    "E06": ("E06-generic", "E06-ideal"),
}


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def meminfo() -> Dict[str, int]:
    result: Dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, value = line.split(":", 1)
        result[key] = int(value.strip().split()[0])
    return result


def vmstat() -> Dict[str, int]:
    wanted = {"pswpin", "pswpout"}
    values = {key: 0 for key in wanted}
    for line in Path("/proc/vmstat").read_text().splitlines():
        key, value = line.split()
        if key in wanted:
            values[key] = int(value)
    return values


def psi_full_total(path: Path) -> int:
    for line in path.read_text().splitlines():
        if line.startswith("full "):
            match = re.search(r"total=(\d+)", line)
            if match:
                return int(match.group(1))
    raise RuntimeError(f"missing full PSI total in {path}")


def cpu_totals() -> Tuple[int, int]:
    fields = Path("/proc/stat").read_text().splitlines()[0].split()
    numbers = [int(value) for value in fields[1:]]
    return numbers[4], sum(numbers)


def one_sample() -> Dict[str, int]:
    memory = meminfo()
    vm = vmstat()
    iowait, cpu_total = cpu_totals()
    return {
        "mem_total_kb": memory["MemTotal"],
        "mem_available_kb": memory["MemAvailable"],
        "swap_total_kb": memory.get("SwapTotal", 0),
        "swap_free_kb": memory.get("SwapFree", 0),
        "pswpin": vm["pswpin"],
        "pswpout": vm["pswpout"],
        "memory_full_total_us": psi_full_total(Path("/proc/pressure/memory")),
        "io_full_total_us": psi_full_total(Path("/proc/pressure/io")),
        "iowait": iowait,
        "cpu_total": cpu_total,
    }


def resource_sample() -> Dict[str, object]:
    first = one_sample()
    time.sleep(10)
    second = one_sample()
    mem_required = max(64 * 1024 * 1024, second["mem_total_kb"] // 5)
    mem_full = (second["memory_full_total_us"] - first["memory_full_total_us"]) / 10000000 * 100
    io_full = (second["io_full_total_us"] - first["io_full_total_us"]) / 10000000 * 100
    cpu_delta = second["cpu_total"] - first["cpu_total"]
    iowait = (second["iowait"] - first["iowait"]) / max(cpu_delta, 1) * 100
    swapin = second["pswpin"] - first["pswpin"]
    swapout = second["pswpout"] - first["pswpout"]
    failures = []
    if second["mem_available_kb"] < mem_required:
        failures.append("MEMAVAILABLE")
    if second["swap_total_kb"] and second["swap_free_kb"] < 512 * 1024:
        failures.append("SWAPFREE")
    if swapin or swapout:
        failures.append("SWAP_ACTIVITY")
    if mem_full > 0.5:
        failures.append("MEMORY_PSI_FULL")
    if io_full > 1.0:
        failures.append("IO_PSI_FULL")
    if iowait > 10.0:
        failures.append("IOWAIT")
    return {
        "pass": not failures,
        "reason": ",".join(failures) if failures else "PASS",
        "mem_available_kb": second["mem_available_kb"],
        "mem_required_kb": mem_required,
        "swap_free_kb": second["swap_free_kb"],
        "swap_in_delta": swapin,
        "swap_out_delta": swapout,
        "memory_full_pct": f"{mem_full:.6f}",
        "io_full_pct": f"{io_full:.6f}",
        "iowait_pct": f"{iowait:.6f}",
    }


def append_tsv(path: Path, header: Iterable[str], row: Dict[str, object]) -> None:
    exists = path.exists()
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(header), delimiter="\t", lineterminator="\n")
        if not exists:
            writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in writer.fieldnames})


class Supervisor:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.scratch = Path(args.scratch_root)
        self.root = self.scratch / "b11-goal"
        self.root.mkdir(parents=True, exist_ok=True)
        self.future = self.scratch / "future-evidence" / "b9-e01-e10"
        self.helper = FRAMEWORK / "util/vm_tlb/run_b9_e01_e10_after_a_terminal.sh"
        self.log_root = self.root / "attempt_logs"
        self.log_root.mkdir(exist_ok=True)
        self.state_path = self.root / "GOAL_STATE.tsv"
        self.wait_path = self.root / "RESOURCE_WAIT_HISTORY.tsv"
        self.calibration_path = self.root / "RSS_CALIBRATION.tsv"
        self._initialize_state()

    def _initialize_state(self) -> None:
        if self.state_path.exists():
            return
        for task in TASKS:
            self.state(task, "NOT_STARTED", "B11 initialized; no heavy work has started")

    def state(self, task: str, state: str, detail: str) -> None:
        append_tsv(self.state_path, ("timestamp_utc", "task", "state", "detail"), {
            "timestamp_utc": utcnow(), "task": task, "state": state, "detail": detail,
        })

    def record_sample(self, task: str, event: str, sample: Dict[str, object]) -> None:
        append_tsv(self.wait_path, (
            "timestamp_utc", "task", "event", "reason", "mem_available_kb", "mem_required_kb",
            "swap_free_kb", "swap_in_delta", "swap_out_delta", "memory_full_pct", "io_full_pct", "iowait_pct",
        ), {"timestamp_utc": utcnow(), "task": task, "event": event, **sample})

    def validate_inputs(self) -> None:
        attestation = Path(self.args.attestation)
        if not attestation.is_file() or attestation.open().readline().rstrip("\n") != "A_TERMINAL_CONFIRMED":
            raise RuntimeError("immutable A terminal attestation is missing or invalid")
        binary = FRAMEWORK / "gpu-simulator/bin/release/accel-sim.out"
        if not binary.is_file() or sha256(binary) != EXPECTED_BINARY:
            raise RuntimeError("immutable B9 simulator SHA-256 mismatch")
        for path in (self.helper,
                     FRAMEWORK / "docs/vm_tlb/review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B9_MINIMUM_EXPERIMENT_EXECUTION_PREFLIGHT/E01_E10_EXECUTION_MANIFEST.tsv",
                     FRAMEWORK / "docs/vm_tlb/review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B9_MINIMUM_EXPERIMENT_EXECUTION_PREFLIGHT/ARM_DELTA_WHITELIST.tsv"):
            if not path.is_file():
                raise RuntimeError(f"required frozen B9 input absent: {path}")

    def latest_states(self) -> Dict[str, str]:
        latest = {task: "NOT_STARTED" for task in TASKS}
        if self.state_path.exists():
            with self.state_path.open(newline="") as handle:
                for row in csv.DictReader(handle, delimiter="\t"):
                    if row["task"] in latest:
                        latest[row["task"]] = row["state"]
        return latest

    def sim_valid(self, arm: str) -> bool:
        output = self.future / arm
        manifest, log = output / "RUN_MANIFEST.tsv", output / "run.log"
        if not (manifest.is_file() and log.is_file()):
            return False
        return ("simulator_exit_status\t0" in manifest.read_text(errors="replace") and
                len(re.findall(r"^Processing kernel ", log.read_text(errors="replace"), re.M)) == 1 and
                re.search(r"^m4c_telemetry_schema =", log.read_text(errors="replace"), re.M) is not None)

    def task_valid(self, task: str) -> bool:
        if task in SIM_ARMS:
            return all(self.sim_valid(arm) for arm in SIM_ARMS[task])
        if task in ("E07", "E08"):
            arm = "E07-decode-rss" if task == "E07" else "E08-prefill-rss"
            return ((self.future / arm / "partials/00000.pkl.xz").is_file() and
                    (self.future / f"{arm}.time-v.txt").is_file())
        if task in ("E09", "E10"):
            arm = "E09-prefill-static16" if task == "E09" else "E10-decode-static16"
            out = self.future / arm
            conservation = out / "TRACE_MINING_CONSERVATION.tsv"
            if not conservation.is_file() or len(list((out / "partials").glob("*.pkl.xz"))) != 16:
                return False
            rows = {}
            for line in conservation.read_text(errors="replace").splitlines():
                fields = line.split("\t")
                if len(fields) >= 3:
                    rows[fields[0]] = fields
            return all(name in rows and rows[name][-1] == "PASS"
                       for name in ("lane_references_by_object", "sectors_by_object", "lines_by_object"))
        raise AssertionError(task)

    def task_artifacts(self, task: str) -> Iterable[Path]:
        if task in SIM_ARMS:
            for arm in SIM_ARMS[task]:
                yield self.future / arm
                yield self.future / f"{arm}.PRELAUNCH.tsv"
        elif task in ("E07", "E08"):
            arm = "E07-decode-rss" if task == "E07" else "E08-prefill-rss"
            yield self.future / arm
            yield self.future / f"{arm}.kernelslist.g"
            yield self.future / f"{arm}.time-v.txt"
        else:
            arm = "E09-prefill-static16" if task == "E09" else "E10-decode-static16"
            yield self.future / arm
            yield self.future / f"{arm}.kernelslist.g"
            yield self.future / f"{arm}.time-v.txt"
            if task == "E09":
                yield self.future / "B9_MATCHED_16_SELECTOR.tsv"

    def task_units(self, task: str) -> Tuple[str | None, ...]:
        return SIM_ARMS[task] if task in SIM_ARMS else (None,)

    def unit_valid(self, task: str, unit: str | None) -> bool:
        return self.sim_valid(unit) if unit is not None else self.task_valid(task)

    def unit_artifacts(self, task: str, unit: str | None) -> Iterable[Path]:
        if unit is not None:
            yield self.future / unit
            yield self.future / f"{unit}.PRELAUNCH.tsv"
            return
        yield from self.task_artifacts(task)

    def quarantine_invalid(self, task: str, unit: str | None) -> None:
        if self.unit_valid(task, unit):
            return
        artifacts = [path for path in self.unit_artifacts(task, unit) if path.exists()]
        if not artifacts:
            return
        # Unit validity was tested by the caller.  A valid completed arm is
        # never moved merely because its paired arm is still pending.
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        name = unit if unit is not None else task
        destination = self.future / "failed_attempts" / stamp / name
        destination.mkdir(parents=True, exist_ok=False)
        for source in artifacts:
            target = destination / source.name
            shutil.move(str(source), str(target))
        (destination / "QUARANTINE_REASON.txt").write_text(
            "B11 supervisor proved this task incomplete against its frozen completion contract; "
            "the artifacts were moved, not deleted, before retry.\n")
        self.state(task, "INVALID", f"incomplete artifacts for {name} moved to {destination}")

    def calibrated_environment(self, task: str) -> Dict[str, str]:
        calibration_task = "E08" if task == "E09" else "E07"
        candidates = []
        if self.calibration_path.exists():
            with self.calibration_path.open(newline="") as handle:
                candidates = [row for row in csv.DictReader(handle, delimiter="\t") if row["task"] == calibration_task]
        if not candidates:
            raise RuntimeError(f"no recorded valid RSS calibration for dependent task {task}")
        latest = candidates[-1]
        return {"B9_CALIBRATED_PEAK_KB": latest["peak_rss_kb"], "B9_MEMORY_SPAN_KB": latest["memory_span_kb"]}

    def record_calibration(self, task: str, before_kb: int, after_kb: int) -> None:
        arm = "E07-decode-rss" if task == "E07" else "E08-prefill-rss"
        time_v = (self.future / f"{arm}.time-v.txt").read_text(errors="replace")
        match = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", time_v)
        if not match:
            raise RuntimeError(f"time -v RSS absent for {task}")
        peak = int(match.group(1))
        append_tsv(self.calibration_path, (
            "timestamp_utc", "task", "arm", "peak_rss_kb", "mem_before_kb", "mem_after_kb", "memory_span_kb", "time_v_path",
        ), {"timestamp_utc": utcnow(), "task": task, "arm": arm, "peak_rss_kb": peak,
            "mem_before_kb": before_kb, "mem_after_kb": after_kb,
            "memory_span_kb": abs(after_kb - before_kb), "time_v_path": str(self.future / f"{arm}.time-v.txt")})

    def invoke(self, task: str, unit: str | None) -> Tuple[int, Path]:
        command = [str(self.helper), "--enable-execution", "--resume-valid", "--a-terminal-attestation", self.args.attestation,
                   "--experiment", task]
        if unit is not None:
            command.extend(("--arm", unit))
        environment = os.environ.copy()
        environment["B9_EXTERNAL_RESOURCE_GATE"] = "1"
        if task in ("E09", "E10"):
            environment.update(self.calibrated_environment(task))
        label = unit if unit is not None else task
        log = self.log_root / f"{utcnow().replace(':', '').replace('-', '')}_{label}.log"
        with log.open("w") as handle:
            handle.write("command\t" + " ".join(command) + "\n")
            handle.flush()
            completed = subprocess.run(command, cwd=FRAMEWORK, env=environment, stdout=handle, stderr=subprocess.STDOUT)
        return completed.returncode, log

    def wait_for_admission(self, task: str) -> object:
        while True:
            sample = resource_sample()
            self.record_sample(task, "RESOURCE_GATE", sample)
            if not sample["pass"]:
                self.state(task, "NOT_STARTED", f"RESOURCE_DEFERRED {sample['reason']}; retry after {self.args.wait_seconds}s")
                time.sleep(self.args.wait_seconds)
                continue
            lock = LOCK_PATH.open("a+")
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.record_sample(task, "LOCK_ACQUIRED", sample)
                return lock
            except BlockingIOError:
                lock.close()
                self.record_sample(task, "LOCK_BUSY", sample)
                self.state(task, "NOT_STARTED", f"heavy-slot lock busy; retry after {self.args.wait_seconds}s")
                time.sleep(self.args.wait_seconds)

    def run_task(self, task: str) -> None:
        if self.task_valid(task):
            self.state(task, "PASS", "frozen completion contract already satisfied; preserved valid evidence")
            return
        for unit in self.task_units(task):
            if self.unit_valid(task, unit):
                continue
            self.quarantine_invalid(task, unit)
            while True:
                lock = self.wait_for_admission(task)
                try:
                    name = unit if unit is not None else task
                    self.state(task, "RUNNING", f"{name}: resource gate passed; shared heavy-slot lock held; effective B heavy concurrency=1")
                    before = meminfo()["MemAvailable"]
                    code, log = self.invoke(task, unit)
                    after = meminfo()["MemAvailable"]
                finally:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
                    lock.close()
                if code == 0 and self.unit_valid(task, unit):
                    if task in ("E07", "E08"):
                        self.record_calibration(task, before, after)
                    break
                log_text = log.read_text(errors="replace") if log.exists() else ""
                if "RESOURCE_DEFERRED" in log_text:
                    self.state(task, "NOT_STARTED", "inner B9 resource gate deferred; B11 will wait/retry")
                    self.record_sample(task, "INNER_RESOURCE_DEFERRED", {"reason": "B9_INNER_GATE", "pass": False})
                    time.sleep(self.args.wait_seconds)
                    continue
                self.state(task, "FAILED_DIAGNOSING", f"B9 executor exit={code}; log={log}; no blind retry")
                raise RuntimeError(f"{task} failed non-transiently; inspect {log} before retry")
        if not self.task_valid(task):
            raise RuntimeError(f"{task} units returned but frozen completion contract is unsatisfied")
        self.state(task, "PASS", "all frozen B9 units completed with their task completion contract")

    def run(self) -> None:
        self.validate_inputs()
        for task in TASKS:
            self.run_task(task)
        print("PASS B11 frozen E01-E10 execution completed; synthesis remains required")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch-root", default=str(SCRATCH_DEFAULT))
    parser.add_argument("--attestation", default=str(ATTESTATION_DEFAULT))
    parser.add_argument("--wait-seconds", type=int, default=300)
    parser.add_argument("--validate-only", action="store_true", help="validate immutable inputs and create no heavy work")
    args = parser.parse_args()
    if args.wait_seconds < 1:
        parser.error("--wait-seconds must be positive")
    supervisor = Supervisor(args)
    try:
        supervisor.validate_inputs()
        if args.validate_only:
            print("PASS B11 supervisor static validation; no heavy job started")
            return 0
        supervisor.run()
        return 0
    except Exception as error:
        print(f"FAIL B11 supervisor: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
