#!/usr/bin/env python3
"""Exclusive-lock bounded executor for the four-point dense-first Tier0 campaign."""

import argparse
import fcntl
import json
import os
import signal
import statistics
import subprocess
import time
from pathlib import Path


LOCK_PATH = Path("/data/c16/locks/c16_gpu_campaign.lock")


def now_utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def nvidia_query(fields):
    output = subprocess.check_output([
        "nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader,nounits"
    ], text=True).strip().splitlines()
    if len(output) != 1:
        raise RuntimeError(f"expected one GPU, got {len(output)}")
    return [item.strip() for item in output[0].split(",")]


def compute_pids():
    output = subprocess.check_output([
        "nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader,nounits"
    ], text=True).strip()
    return [line.strip() for line in output.splitlines() if line.strip()]


def run_command(command, cwd, stdout_path, stderr_path, timeout_seconds):
    start = time.monotonic()
    with stdout_path.open("w") as stdout, stderr_path.open("w") as stderr:
        proc = subprocess.Popen(command, cwd=cwd, stdout=stdout, stderr=stderr,
                                text=True, start_new_session=True)
        try:
            code = proc.wait(timeout=max(1, timeout_seconds))
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                code = proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                code = proc.wait()
            code = 124
    return {"exit_code": code, "timed_out": timed_out,
            "process_wall_seconds": time.monotonic() - start,
            "command": command, "stdout": str(stdout_path), "stderr": str(stderr_path)}


def load_result(path):
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def backend_legal(result, point):
    quant_methods = {row.get("quant_method_class") for row in result.get("module_census", []) if row.get("quant_method_class")}
    kernels = {row.get("kernel_backend_class") for row in result.get("module_census", []) if row.get("kernel_backend_class")}
    attention = {row.get("impl_class") for row in result.get("attention_backend", {}).get("modules", []) if row.get("impl_class")}
    if "FlashAttentionImpl" not in attention:
        return False
    if point == "MP05":
        return "AutoAWQMarlinLinearMethod" in quant_methods and "MarlinLinearKernel" in kernels
    return "UnquantizedLinearMethod" in quant_methods


def sampled_logprobs(completion):
    values = []
    for token, row in zip(completion["tokens"], completion.get("logprobs", [])):
        mapping = {int(item["token_id"]): float(item["logprob"]) for item in row}
        values.append(mapping.get(int(token)))
    return values


def compare_run_outputs(reference, other, atol=0.05, rtol=0.01):
    if len(reference) != len(other):
        return False
    for left, right in zip(reference, other):
        a, b = left["completion"], right["completion"]
        if left["batch_row"] != right["batch_row"] or left["source_id"] != right["source_id"]:
            return False
        if a["tokens"] != b["tokens"]:
            return False
        la, lb = sampled_logprobs(a), sampled_logprobs(b)
        if len(la) != len(lb) or any(x is None or y is None for x, y in zip(la, lb)):
            return False
        for x, y in zip(la, lb):
            if abs(x - y) > atol + rtol * abs(x):
                return False
    return True


def native_correct(on_result, off_result):
    if not on_result or not off_result or on_result.get("status") != "PASS" or off_result.get("status") != "PASS":
        return False
    reference = on_result["samples"][0]["rows"]
    all_rows = [sample["rows"] for sample in on_result["samples"] + off_result["samples"]]
    return all(compare_run_outputs(reference, rows) for rows in all_rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    args = parser.parse_args()
    repo, raw = args.repo.resolve(), args.raw.resolve()
    raw.mkdir(parents=True, exist_ok=True)
    config = json.loads(args.config.read_text())
    if config.get("status") != "READY_FOR_LOCKED_GPU_CAMPAIGN":
        raise SystemExit("campaign config not ready")
    if config["point_allowlist"] != ["MP01", "MP02", "MP03", "MP05"]:
        raise SystemExit("point allowlist mismatch")
    total_cap = int(config["total_gpu_active_cap_seconds"])
    if total_cap > 540:
        raise SystemExit("total cap exceeds authority")

    request_utc = now_utc()
    request_mono = time.monotonic()
    lock_file = LOCK_PATH.open("a+")
    acquired = False
    while time.monotonic() - request_mono <= 2700:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            acquired = True
            break
        except BlockingIOError:
            time.sleep(5)
    if not acquired:
        write_json(raw / "GPU_LOCK_RECEIPT.json", {
            "status": "GPU_LOCK_45MIN_TIMEOUT_STOP", "lock": str(LOCK_PATH),
            "request_utc": request_utc, "released": False,
        })
        raise SystemExit(75)

    acquired_utc = now_utc()
    campaign_start = time.monotonic()
    campaign = {"points": {}, "status": "RUNNING"}
    exit_code = 0
    baseline_memory = []
    try:
        pids = compute_pids()
        if pids:
            campaign["status"] = "GPU_BUSY_FAIL_CLOSED"
            campaign["unexpected_compute_pids"] = pids
            exit_code = 76
            raise SystemExit(exit_code)
        gpu = nvidia_query("name,uuid,driver_version,compute_cap,memory.total,memory.used,memory.free")
        for _ in range(3):
            baseline_memory.append(int(nvidia_query("memory.used")[0]))
            time.sleep(0.25)
        if gpu[1] != config["gpu_uuid"] or gpu[0] != config["gpu_name"] or gpu[2] != config["driver_version"]:
            campaign["status"] = "GPU_IDENTITY_MISMATCH_STOP"
            campaign["observed_gpu"] = gpu
            exit_code = 77
            raise SystemExit(exit_code)
        if max(baseline_memory) - min(baseline_memory) > 64:
            campaign["status"] = "GPU_BASELINE_MEMORY_UNSTABLE_STOP"
            campaign["baseline_memory_mib"] = baseline_memory
            exit_code = 78
            raise SystemExit(exit_code)
        campaign["gpu"] = gpu
        campaign["baseline_memory_mib"] = baseline_memory

        shared_bf16_legal = True
        for point in config["point_allowlist"]:
            if time.monotonic() - campaign_start >= total_cap:
                campaign["status"] = "STOP_ALL_GPU"
                break
            point_cfg = config["points"][point]
            point_start = time.monotonic()
            point_cap = int(point_cfg["gpu_active_cap_seconds"])
            point_dir = raw / point
            point_dir.mkdir()
            point_record = {"status": "RUNNING", "cap_seconds": point_cap, "commands": []}
            campaign["points"][point] = point_record
            if point != "MP05" and not shared_bf16_legal:
                point_record["status"] = "STOP_SHARED_BF16_BACKEND_IDENTITY"
                continue

            def remaining():
                point_left = point_cap - (time.monotonic() - point_start)
                total_left = total_cap - (time.monotonic() - campaign_start)
                return int(min(point_left, total_left))

            def runner_command(graph_mode, arm, output):
                command = [config["python"], config["runner"], "--point", point,
                           "--graph-mode", graph_mode, "--arm", arm,
                           "--observer", point_cfg["observer_identity"],
                           "--observer-source", point_cfg["observer_source"],
                           "--model", point_cfg["model_path"],
                           "--model-kind", point_cfg["model_kind"]]
                for path in point_cfg["input_jsons"]:
                    command += ["--input-json", path]
                command += ["--decode-tokens", str(point_cfg["decode_tokens"]),
                            "--timing-endpoint", point_cfg["native_timing_endpoint"],
                            "--output", str(output)]
                return command

            stop_point = False
            native_results = {}
            for graph_mode in ("on", "off"):
                left = remaining()
                if left <= 0:
                    point_record["status"] = "STOP_POINT_BUDGET"
                    stop_point = True
                    break
                output = point_dir / f"{point}_GRAPH_{graph_mode.upper()}_NATIVE.json"
                command = runner_command(graph_mode, "native", output)
                execution = run_command(command, repo,
                                        point_dir / f"{point}_GRAPH_{graph_mode.upper()}_NATIVE.stdout.log",
                                        point_dir / f"{point}_GRAPH_{graph_mode.upper()}_NATIVE.stderr.log", left)
                point_record["commands"].append(execution)
                result = load_result(output)
                native_results[graph_mode] = result
                if execution["exit_code"] != 0 or not result or result.get("status") != "PASS":
                    point_record["status"] = "STOP_POINT_BUDGET" if execution["timed_out"] else "STOP_POINT_RUNTIME"
                    stop_point = True
                    break
                if not backend_legal(result, point):
                    point_record["status"] = "STOP_POINT_BACKEND_IDENTITY"
                    stop_point = True
                    if point != "MP05":
                        shared_bf16_legal = False
                        for prior_point, prior_record in campaign["points"].items():
                            if prior_point != "MP05":
                                prior_record["status"] = "STOP_SHARED_BF16_BACKEND_IDENTITY"
                    break
                memory = int(nvidia_query("memory.used")[0])
                if memory > max(baseline_memory) + 256:
                    point_record["status"] = "STOP_POINT_GPU_MEMORY_RELEASE"
                    stop_point = True
                    break
            if stop_point:
                point_record["gpu_active_seconds"] = time.monotonic() - point_start
                continue
            if not native_correct(native_results["on"], native_results["off"]):
                point_record["status"] = "STOP_POINT_CORRECTNESS"
                point_record["gpu_active_seconds"] = time.monotonic() - point_start
                continue

            left = remaining()
            if left <= 0:
                point_record["status"] = "STOP_POINT_BUDGET"
                point_record["gpu_active_seconds"] = time.monotonic() - point_start
                continue
            observed_output = point_dir / f"{point}_GRAPH_OFF_OBSERVED.json"
            trace_prefix = point_dir / f"{point}_GRAPH_OFF_OBSERVED"
            observed_command = runner_command("off", "observed", observed_output)
            command = ["nsys", "profile", "--trace=cuda,nvtx", "--sample=none", "--cpuctxsw=none",
                       "--force-overwrite=true", f"--output={trace_prefix}", *observed_command]
            execution = run_command(command, repo,
                                    point_dir / f"{point}_GRAPH_OFF_OBSERVED.stdout.log",
                                    point_dir / f"{point}_GRAPH_OFF_OBSERVED.stderr.log", left)
            point_record["commands"].append(execution)
            observed = load_result(observed_output)
            report = trace_prefix.with_suffix(".nsys-rep")
            point_record["nsys_capture_count"] = 1
            point_record["nsys_report"] = str(report)
            if execution["exit_code"] != 0 or not observed or observed.get("status") != "PASS" or not report.is_file():
                point_record["status"] = "NSYS_STRUCTURAL_CAPTURE_UNAVAILABLE"
            elif not backend_legal(observed, point):
                point_record["status"] = "STOP_POINT_BACKEND_IDENTITY"
                if point != "MP05":
                    shared_bf16_legal = False
                    for prior_point, prior_record in campaign["points"].items():
                        if prior_point != "MP05":
                            prior_record["status"] = "STOP_SHARED_BF16_BACKEND_IDENTITY"
            else:
                reference = native_results["on"]["samples"][0]["rows"]
                if not compare_run_outputs(reference, observed["samples"][0]["rows"]):
                    point_record["status"] = "STOP_POINT_CORRECTNESS"
                else:
                    point_record["status"] = "GPU_COMPLETE_PENDING_CPU_ANALYSIS"
            point_record["gpu_active_seconds"] = time.monotonic() - point_start
            if point_record["gpu_active_seconds"] > point_cap:
                point_record["status"] = "STOP_POINT_BUDGET"
            memory = int(nvidia_query("memory.used")[0])
            point_record["post_point_memory_mib"] = memory
            if memory > max(baseline_memory) + 256:
                point_record["status"] = "STOP_POINT_GPU_MEMORY_RELEASE"

        if campaign["status"] == "RUNNING":
            campaign["status"] = "GPU_PHASE_COMPLETE"
    finally:
        campaign_active = time.monotonic() - campaign_start
        campaign["gpu_active_seconds"] = campaign_active
        campaign["total_cap_seconds"] = total_cap
        campaign["within_total_cap"] = campaign_active <= total_cap
        write_json(raw / "POINT_EXECUTION_RAW.json", campaign)
        end_utc = now_utc()
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        lock_file.close()
        write_json(raw / "GPU_LOCK_RECEIPT.json", {
            "lock": str(LOCK_PATH), "request_utc": request_utc,
            "acquired_utc": acquired_utc, "end_utc": end_utc,
            "wait_seconds": time.monotonic() - request_mono - campaign_active,
            "gpu_active_seconds": campaign_active, "gpu_active_cap_seconds": total_cap,
            "within_cap": campaign_active <= total_cap, "released": True,
            "exit_code": exit_code,
        })
        write_json(raw / "GPU_ACTIVE_BUDGET.json", {
            "status": "PASS" if campaign_active <= total_cap else "STOP_ALL_GPU",
            "total_cap_seconds": total_cap, "gpu_active_seconds": campaign_active,
            "remaining_seconds": total_cap - campaign_active,
            "point_caps_seconds": {point: config["points"][point]["gpu_active_cap_seconds"] for point in config["point_allowlist"]},
            "point_active_seconds": {point: record.get("gpu_active_seconds", 0) for point, record in campaign["points"].items()},
            "cross_point_budget_transfer": False,
        })
    if exit_code:
        raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
