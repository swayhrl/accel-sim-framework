#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

from a17_a18_latpc_lib import LOG_DIR, REPORT_DIR, RUN_DIR, REPO_ROOT, clean, ensure_local_dirs, extract_stat_lines, latest, rel, repo_path, run_logged, selected_workload, source_accelsim_env, ts, write_csv, write_stage_report
from accelsim_stats_parser import first_stat, parse_log


def prepare_run_dir(run_dir: Path, kernelslist: Path, config: Path, trace_config: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    trace_dir = kernelslist.parent
    link = run_dir / "traces"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(trace_dir)
    shutil.copytree(config.parent, run_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns("gpgpusim.config"))
    combined = run_dir / "gpgpusim.config"
    combined.write_text(config.read_text(errors="replace").replace("\r", "") + "\n#SASS\n#SASS-Driven Accel-Sim\n\n" + trace_config.read_text(errors="replace").replace("\r", ""))


def main() -> int:
    ensure_local_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    build_log = LOG_DIR / f"A18C_latpc_build_{stamp}.log"
    results_csv = REPORT_DIR / f"A18C_latpc_stats_probe_results_{stamp}.csv"
    latpc_stats_csv = REPORT_DIR / f"A18C_latpc_extracted_latpc_stats_{stamp}.csv"
    command_csv = REPORT_DIR / f"A18C_latpc_probe_commands_{stamp}.csv"
    report = REPORT_DIR / f"A18C_latpc_build_and_stats_probe_report_{stamp}.md"
    commands: list[str] = []
    status = "PASS"
    blocker = "none"

    selected = selected_workload()
    kernelslist = repo_path(selected.get("kernelslist_path", ""))
    config = repo_path(selected.get("config_path", "gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config"))
    trace_config = REPO_ROOT / "gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
    sim_bin = REPO_ROOT / "gpu-simulator/bin/release/accel-sim.out"

    build_env = source_accelsim_env({"ACCELSIM_ROUND": "A18", "ACCELSIM_PAPER": "LATPC"})
    build_cmd = ["make", "-B", f"-j{os.cpu_count() or 1}", "-C", "./gpu-simulator/"]
    build_info = run_logged(build_cmd, build_log, cwd=REPO_ROOT, env=build_env)
    commands.append(build_info["command"])
    command_rows = [build_info]
    if build_info["return_code"] != "0":
        fallback_log = LOG_DIR / f"A18C_latpc_build_fallback_{stamp}.log"
        fallback_info = run_logged(["make", "-C", "./gpu-simulator/"], fallback_log, cwd=REPO_ROOT, env=build_env)
        commands.append(fallback_info["command"])
        command_rows.append(fallback_info)
        if fallback_info["return_code"] != "0":
            status = "BLOCKED_BUILD_FAILED"
            blocker = "forced rebuild and fallback make both failed"

    result_rows: list[dict[str, str]] = []
    latpc_rows: list[dict[str, str]] = []
    if status == "PASS":
        missing = [str(p) for p in [kernelslist, config, trace_config, sim_bin] if not p.exists()]
        if missing:
            status = "BLOCKED_MISSING_INPUT"
            blocker = "missing " + "; ".join(missing)
        elif not os.access(sim_bin, os.X_OK):
            status = "BLOCKED_BINARY_NOT_EXECUTABLE"
            blocker = f"{rel(sim_bin)} is not executable"
        else:
            for variant in ["baseline", "latpc_stats_only"]:
                run_dir = RUN_DIR / f"A18C_latpc_stats_probe_{stamp}" / variant
                prepare_run_dir(run_dir, kernelslist, config, trace_config)
                log_path = LOG_DIR / f"A18C_latpc_probe_{stamp}_{variant}.log"
                timeout = os.environ.get("ACCELSIM_A18C_TIMEOUT_SEC", "900")
                cmd = ["timeout", timeout, str(sim_bin), "-config", "./gpgpusim.config", "-trace", "./traces/kernelslist.g"]
                env = source_accelsim_env({"ACCELSIM_ROUND": "A18", "ACCELSIM_PAPER": "LATPC", "ACCELSIM_VARIANT": variant})
                info = run_logged(cmd, log_path, cwd=run_dir, env=env)
                commands.append(info["command"])
                command_rows.append(info)
                text = Path(log_path).read_text(errors="replace")
                row_status = "PASS" if info["return_code"] == "0" and "GPGPU-Sim" in text else ("TIMEOUT" if info["return_code"] == "124" else "FAIL")
                if row_status != "PASS":
                    status = "FAIL_PROBE_RUN"
                    blocker = f"{variant} returned {info['return_code']}"
                result_rows.append({
                    "variant": variant,
                    "workload": clean(selected.get("selected_workload")) or "nw",
                    "status": row_status,
                    "run_dir": rel(run_dir),
                    "log_path": rel(log_path),
                    "cycles": first_stat(log_path, "gpu_tot_sim_cycle", "last"),
                    "instructions": first_stat(log_path, "gpu_tot_sim_insn", "last"),
                    "ipc": first_stat(log_path, "gpu_tot_ipc", "last"),
                    "l2_accesses": first_stat(log_path, "l2_total_cache_accesses", "last"),
                    "l2_misses": first_stat(log_path, "l2_total_cache_misses", "last"),
                    "raw_stats_fields_count": str(len(parse_log(log_path))),
                })
                for row in extract_stat_lines(log_path, "latpc_"):
                    row["variant"] = variant
                    latpc_rows.append(row)
            if status == "PASS" and not latpc_rows:
                status = "FAIL_NO_LATPC_STATS"
                blocker = "probe ran but no latpc_* stats appeared"

    write_csv(command_csv, command_rows, ["command", "cwd", "log_path", "start_time", "end_time", "wall_seconds", "return_code"])
    write_csv(results_csv, result_rows, ["variant", "workload", "status", "run_dir", "log_path", "cycles", "instructions", "ipc", "l2_accesses", "l2_misses", "raw_stats_fields_count"])
    write_csv(latpc_stats_csv, latpc_rows, ["variant", "stat_key", "stat_value", "line_no", "log_path"])
    write_stage_report(
        report,
        "A18C LATPC Build And Stats Probe",
        status,
        start_iso,
        start,
        commands,
        [clean(selected.get("_source_path")), rel(kernelslist), rel(config), rel(trace_config)],
        [rel(build_log), rel(command_csv), rel(results_csv), rel(latpc_stats_csv), rel(report)],
        blocker,
        ["Only selected workload NW/A16 selection is run.", "No tracer or full benchmark campaign is run."],
    )
    print(f"A18C status: {status}")
    print(f"A18C results: {rel(results_csv)}")
    print(f"A18C latpc stats: {rel(latpc_stats_csv)}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
