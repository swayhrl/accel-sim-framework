#!/usr/bin/env python3
"""Run the bounded, application-level L2CHARV1 Round-1 campaign.

The default selection is Wave-1A: the reviewed PRIMARY_FULL/RUN entries whose
historical scheduler prior is below one hour.  Only normal simulator exit,
successful production parsing, and terminal invariant success is called
COMPLETE_VALID; every other terminal state is preserved explicitly.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from dataclasses import dataclass


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CORE = Path("/workspace/worktrees/gpgpu-sim-l2-resource-char")
DEFAULT_RSS = Path(
    "/workspace/worktrees/accel-sim-decoupled-l2/hw_run/"
    "decoupled-l2-rss-profile-20260828-r2/valid_rss_summary.tsv"
)
EXIT_MARKER = "GPGPU-Sim: *** exit detected ***"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def mem_available_kib() -> int:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1])
    raise RuntimeError("/proc/meminfo has no MemAvailable")


def oom_kill_count() -> int | None:
    for path in (Path("/sys/fs/cgroup/memory.events"), Path("/sys/fs/cgroup/memory/memory.oom_control")):
        try:
            values = dict(line.split()[:2] for line in path.read_text().splitlines() if line.split())
            if "oom_kill" in values:
                return int(values["oom_kill"])
        except (OSError, ValueError):
            pass
    return None


def process_rss_kib(pid: int) -> int:
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    except OSError:
        pass
    return 0


def safe_component(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_.") or "NO_ARGS"


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def bundle_sha(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode() + b"\0" + sha256(path).encode() + b"\n")
    return digest.hexdigest()


def check_overlay(path: Path) -> dict[str, int]:
    values: dict[str, int] = {}
    for line in path.read_text().splitlines():
        fields = line.strip().split()
        if len(fields) == 2 and fields[0].startswith("-gpgpu_l2_char_"):
            values[fields[0]] = int(fields[1])
    required = {
        "-gpgpu_l2_char_enable": 1,
        "-gpgpu_l2_char_window": 5000,
        "-gpgpu_l2_char_set_detail": 1,
        "-gpgpu_l2_char_emit_windows": 1,
        "-gpgpu_l2_char_dram_issue_hold_cycles": 0,
        "-gpgpu_l2_char_dram_issue_hold_after_issues": 0,
        "-gpgpu_l2_char_returnq_hold_cycles": 0,
    }
    for name, wanted in required.items():
        if values.get(name) != wanted:
            raise ValueError(f"observation overlay requires {name}={wanted}, got {values.get(name)!r}")
    return values


def choose(row: dict[str, str], wave: str) -> bool:
    primary = row["cohort"] == "PRIMARY_FULL" and row["round1_decision"] == "RUN"
    return {
        "wave1a": primary and row["runtime_tier"] == "LT_1H",
        "wave1b": primary and row["runtime_tier"] == "1_TO_4H",
        "wave1c": primary and row["runtime_tier"] == "UNKNOWN_OR_BOUNDED",
        "primary-all": primary,
        "ubench": row["cohort"] == "MICROBENCH",
        "secondary": row["cohort"] in {"V100_BOUNDED", "V100_SPECIAL", "DERIVED_TRIMMED"},
    }[wave]


def load_rss(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    with path.open(newline="") as source:
        rows = csv.DictReader((line for line in source if not line.startswith("#")), delimiter="\t")
        return {row["workload"].lower(): row for row in rows}


def rss_prior(row: dict[str, str], data: dict[str, dict[str, str]]) -> dict[str, str] | None:
    suite = row["suite"].lower().replace(" ", "")
    if "ubench" in suite:
        suite = "ubench"
    workload = row["workload"].lower()
    for key, value in data.items():
        if key == f"{suite}/{workload}" or key.startswith(f"{suite}/{workload}_"):
            return value
    return None


def run_dir(out: Path, row: dict[str, str]) -> Path:
    return out / safe_component(row["suite"]) / safe_component(row["workload"]) / safe_component(row["input"])


def is_valid(path: Path) -> bool:
    try:
        return json.loads((path / "run_status.json").read_text()).get("status") == "COMPLETE_VALID"
    except (OSError, json.JSONDecodeError):
        return False


@dataclass
class Active:
    row: dict[str, str]
    prior: dict[str, str] | None
    directory: Path
    process: subprocess.Popen
    log: object
    command: list[str]
    started_epoch: float
    started_monotonic: float
    oom_before: int | None
    peak_rss_kib: int = 0


def launch(args: argparse.Namespace, row: dict[str, str], prior: dict[str, str] | None) -> Active:
    directory = run_dir(args.out, row)
    directory.mkdir(parents=True, exist_ok=True)
    # A retry must not leave a previous successful CSV beside a new failed log.
    for name in ("summary.csv", "slice.csv", "window.csv", "manifest.json",
                 "parser.stdout", "parser.stderr", "run_status.json"):
        (directory / name).unlink(missing_ok=True)
    command = [str(args.sim), "-config", str(args.base_config), "-config", str(args.trace_config),
               "-config", str(args.overlay), "-trace", row["current_trace_path"]]
    # setup_environment intentionally probes optional unset variables, so do
    # not enable nounset until after both environment scripts have returned.
    shell = ('set -eo pipefail; source "$CORE/setup_environment" release >/dev/null; '
             'source "$FRAME/gpu-simulator/setup_environment.sh" release >/dev/null; exec "$@"')
    env = os.environ.copy()
    env.update({"CORE": str(args.core), "FRAME": str(ROOT)})
    log = (directory / "raw.log").open("w")
    process = subprocess.Popen(["bash", "-lc", shell, "round1-run", *command], cwd=directory,
                               stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
    return Active(row, prior, directory, process, log, command, time.time(), time.monotonic(), oom_kill_count())


def terminal_log_fields(log: Path) -> tuple[bool, str | None, str | None]:
    """Read a potentially multi-GiB simulator log once, without retaining it.

    A campaign runner must never make its host-memory footprint proportional to
    a workload's raw log.  Keep only the terminal markers required for status
    and provenance while streaming through the file.
    """
    normal_exit = False
    cycle = None
    insn = None
    with log.open(encoding="utf-8", errors="replace") as source:
        for line in source:
            if EXIT_MARKER in line:
                normal_exit = True
            if line.startswith("gpu_tot_sim_cycle="):
                cycle = line.split("=", 1)[1].strip()
            elif line.startswith("gpu_tot_sim_insn="):
                insn = line.split("=", 1)[1].strip()
    return normal_exit, cycle, insn


def parser_result(args: argparse.Namespace, item: Active, audit: dict) -> tuple[str, str | None]:
    row = item.row
    command = [
        sys.executable, str(ROOT / "util/l2_char/parse_l2_char.py"), str(item.directory / "raw.log"),
        "--out", str(item.directory), "--workload", row["workload"], "--input", row["input"],
        "--kernel", "all", "--kernel-id", "all", "--config", str(args.base_config),
        "--trace", row["current_trace_path"], "--framework-repo", str(ROOT), "--core-repo", str(args.core),
        "--framework-commit", audit["framework_commit"], "--core-commit", audit["core_commit"],
        "--framework-branch", audit["framework_branch"], "--core-branch", audit["core_branch"],
        "--command", " ".join(item.command), "--production", "--window-l2-cycles", "5000",
        "--set-detail", "1", "--emit-windows", "1",
    ]
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (item.directory / "parser.stdout").write_text(result.stdout)
    (item.directory / "parser.stderr").write_text(result.stderr)
    if result.returncode:
        return "PARSE_FAIL", result.stderr.strip() or "parser returned non-zero"
    try:
        with (item.directory / "summary.csv").open(newline="") as source:
            summary = next(csv.DictReader(source))
        if summary.get("invariant_records") in (None, "0") or summary.get("invariants_pass") != "1":
            return "INVARIANT_FAIL", "terminal L2CHARV1 invariant record is not PASS"
        manifest = json.loads((item.directory / "manifest.json").read_text())
        manifest["campaign_audit"] = audit
        manifest["trace_tree_sha256"] = row["trace_tree_sha256"]
        manifest["trace_file_count_hashed"] = int(row["trace_file_count_hashed"])
        write_json(item.directory / "manifest.json", manifest)
    except (OSError, StopIteration, ValueError, json.JSONDecodeError) as error:
        return "PARSE_FAIL", f"unable to validate parser output: {error}"
    return "COMPLETE_VALID", None


def stop_process(item: Active) -> None:
    os.killpg(item.process.pid, signal.SIGTERM)
    try:
        item.process.wait(timeout=60)
    except subprocess.TimeoutExpired:
        os.killpg(item.process.pid, signal.SIGKILL)
        item.process.wait()


def finish(args: argparse.Namespace, item: Active, audit: dict, timed_out: bool) -> dict:
    item.log.close()
    log = item.directory / "raw.log"
    elapsed = time.monotonic() - item.started_monotonic
    code = item.process.returncode
    normal_exit, terminal_cycle, terminal_insn = terminal_log_fields(log)
    oom_after = oom_kill_count()
    if timed_out:
        status, detail = "TIMEOUT_8H", f"exceeded configured timeout of {args.timeout_seconds}s"
    elif item.oom_before is not None and oom_after is not None and oom_after > item.oom_before:
        status, detail = "OOM", "cgroup oom_kill counter increased during replay"
    elif code != 0 or not normal_exit:
        status = "SIM_ERROR"
        detail = f"simulator exit code {code}" if code else "missing normal simulator exit marker"
    else:
        status, detail = parser_result(args, item, audit)
    result = {
        "status": status, "detail": detail, "wave": args.wave,
        "suite": item.row["suite"], "workload": item.row["workload"], "input": item.row["input"],
        "trace": item.row["current_trace_path"], "trace_tree_sha256": item.row["trace_tree_sha256"],
        "trace_file_count_hashed": int(item.row["trace_file_count_hashed"]),
        "trace_body_sha_status": item.row["trace_body_sha_status"], "exit_code": code,
        "normal_simulator_exit": normal_exit, "started_epoch": item.started_epoch,
        "finished_epoch": time.time(), "wall_seconds": round(elapsed, 3),
        "peak_rss_kib": item.peak_rss_kib, "rss_prior": item.prior,
        "mem_available_kib_at_finish": mem_available_kib(), "oom_kill_before": item.oom_before,
        "oom_kill_after": oom_after, "audit": audit,
        "terminal_gpu_tot_sim_cycle": terminal_cycle,
        "terminal_gpu_tot_sim_insn": terminal_insn,
    }
    write_json(item.directory / "run_status.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wave", choices=("wave1a", "wave1b", "wave1c", "primary-all", "ubench", "secondary"), default="wave1a")
    parser.add_argument("--roster", type=Path, default=ROOT / "docs/l2_char_v1/ROUND1_WAVE1_COST_ROSTER.tsv")
    parser.add_argument("--rss-summary", type=Path, default=DEFAULT_RSS)
    parser.add_argument("--out", type=Path, default=ROOT / "docs/l2_char_v1/round1_results")
    parser.add_argument("--core", type=Path, default=DEFAULT_CORE)
    parser.add_argument("--sim", type=Path, default=ROOT / "gpu-simulator/bin/release/accel-sim.out")
    parser.add_argument("--base-config", type=Path, default=DEFAULT_CORE / "configs/tested-cfgs/SM7_QV100/gpgpusim.config")
    parser.add_argument("--trace-config", type=Path, default=ROOT / "gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config")
    parser.add_argument("--overlay", type=Path, default=ROOT / "tests/l2_char/qv100_round1_observation.config")
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--mem-available-min-gib", type=float, default=96.0)
    parser.add_argument("--timeout-seconds", type=int, default=8 * 60 * 60)
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    parser.add_argument("--rerun-nonvalid", action="store_true")
    parser.add_argument("--only", help="regular expression matched against suite/workload/input for a bounded replay")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.jobs < 1 or args.timeout_seconds < 1 or args.mem_available_min_gib <= 0:
        raise SystemExit("jobs, timeout, and memory gate must be positive")
    for path in (args.roster, args.sim, args.base_config, args.trace_config, args.overlay, args.core):
        if not path.exists():
            raise SystemExit(f"required path is missing: {path}")
    if not os.access(args.sim, os.X_OK):
        raise SystemExit(f"simulator is not executable: {args.sim}")
    overlay = check_overlay(args.overlay)
    with args.roster.open(newline="") as source:
        rows = [row for row in csv.DictReader(source, delimiter="\t") if choose(row, args.wave)]
    if args.only:
        pattern = re.compile(args.only)
        rows = [row for row in rows if pattern.search("/".join((row["suite"], row["workload"], row["input"]))) ]
    rows.sort(key=lambda row: (row["suite"], row["workload"], row["input"]))
    if not rows:
        raise SystemExit(f"no workloads selected for {args.wave}")
    audit = {
        "framework_branch": git(ROOT, "branch", "--show-current"), "framework_commit": git(ROOT, "rev-parse", "HEAD"),
        "core_branch": git(args.core, "branch", "--show-current"), "core_commit": git(args.core, "rev-parse", "HEAD"),
        "base_config_sha256": sha256(args.base_config), "trace_config_sha256": sha256(args.trace_config),
        "overlay_sha256": sha256(args.overlay),
        "config_bundle_sha256": bundle_sha([args.base_config, args.trace_config, args.overlay]),
        "test_hooks": {key: value for key, value in overlay.items() if "hold" in key},
        "characterization": {"enabled": overlay["-gpgpu_l2_char_enable"],
                               "window_l2_cycles": overlay["-gpgpu_l2_char_window"],
                               "set_detail": overlay["-gpgpu_l2_char_set_detail"],
                               "emit_windows": overlay["-gpgpu_l2_char_emit_windows"]},
        "timeout_seconds": args.timeout_seconds,
        "mem_available_min_kib": int(args.mem_available_min_gib * 1024 * 1024),
    }
    print(f"Round-1 {args.wave}: {len(rows)} selected; jobs={args.jobs}; memory gate={args.mem_available_min_gib:g}GiB")
    if args.dry_run:
        for row in rows:
            print(f"DRY_RUN\t{row['suite']}\t{row['workload']}\t{row['input']}")
        return
    args.out.mkdir(parents=True, exist_ok=True)
    write_json(args.out / f"campaign_{args.wave}.json", {"wave": args.wave, "selected_workloads": rows,
               "audit": audit, "rss_summary": str(args.rss_summary) if args.rss_summary.is_file() else "MISSING"})
    rss_data = load_rss(args.rss_summary)
    pending = [(row, rss_prior(row, rss_data)) for row in rows]
    active: list[Active] = []
    results: list[dict] = []
    while pending or active:
        while pending and len(active) < args.jobs and mem_available_kib() >= audit["mem_available_min_kib"]:
            row, prior = pending.pop(0)
            directory = run_dir(args.out, row)
            if is_valid(directory) and not args.rerun_nonvalid:
                print(f"SKIP_COMPLETE\t{row['suite']}\t{row['workload']}\t{row['input']}")
                continue
            item = launch(args, row, prior)
            active.append(item)
            print(f"START\t{row['suite']}\t{row['workload']}\t{row['input']}\tpid={item.process.pid}", flush=True)
        if pending and not active and mem_available_kib() < audit["mem_available_min_kib"]:
            raise SystemExit("memory gate blocks every pending launch; free memory before resuming")
        time.sleep(args.poll_seconds)
        for item in list(active):
            item.peak_rss_kib = max(item.peak_rss_kib, process_rss_kib(item.process.pid))
            timed_out = time.monotonic() - item.started_monotonic >= args.timeout_seconds
            if timed_out and item.process.poll() is None:
                stop_process(item)
            if item.process.poll() is not None:
                result = finish(args, item, audit, timed_out)
                active.remove(item); results.append(result)
                print(f"{result['status']}\t{item.row['suite']}\t{item.row['workload']}\t{item.row['input']}\t"
                      f"wall_s={result['wall_seconds']}\trss_kib={item.peak_rss_kib}", flush=True)
    counts: dict[str, int] = {}
    for result in results:
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    write_json(args.out / f"campaign_{args.wave}_status.json", {"wave": args.wave,
               "completed_this_invocation": results, "status_counts": counts, "audit": audit})
    if any(result["status"] != "COMPLETE_VALID" for result in results):
        raise SystemExit(f"Round-1 {args.wave} completed with non-valid results: {counts}")
    print(f"Round-1 {args.wave}: COMPLETE_VALID={len(results)}")


if __name__ == "__main__":
    main()
