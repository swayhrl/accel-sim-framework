#!/usr/bin/env python3
"""Immutable-attempt supervisor for one official-NVBit expert58 replay."""
import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = "/home/huangrulin/workspace/worktrees/accel-sim-c16-olmoe-v39"
PYTHON = "/data/c16/env/c16-py310/bin/python"
REPLAY = f"{REPO}/util/vm_tlb/c16/olmoe_v40_marked_replay.py"
M6 = "M6_BEFORE_NORMAL_PROCESS_EXIT"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path, value):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def command(path, argv, timeout=15):
    try:
        result = subprocess.run(argv, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=timeout)
        path.write_text(result.stdout, encoding="utf-8")
    except Exception as error:
        path.write_text(f"DIAGNOSTIC_ERROR: {error}\n", encoding="utf-8")


def capture_timeout(root, pid):
    diag = root / "timeout_diagnostics"
    diag.mkdir(exist_ok=True)
    command(diag / "ps.txt", ["ps", "-o", "pid,ppid,pgid,stat,etime,wchan:32,cmd", "-p", str(pid)])
    command(diag / "ps_threads.txt", ["ps", "-L", "-p", str(pid), "-o", "pid,tid,stat,wchan:32,comm"])
    command(diag / "nvidia_smi.txt", ["nvidia-smi"])
    command(diag / "gpu_processes.txt", ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader"])


def residual_check(pgid):
    ps = subprocess.run(["ps", "-eo", "pid=,ppid=,pgid=,stat=,cmd="], text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    members = []
    for line in ps.stdout.splitlines():
        fields = line.strip().split(None, 4)
        if len(fields) >= 4 and fields[2].isdigit() and int(fields[2]) == pgid:
            members.append({"pid": int(fields[0]), "ppid": int(fields[1]), "pgid": int(fields[2]),
                            "stat": fields[3], "cmd": fields[4] if len(fields) == 5 else ""})
    gpu = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory",
                          "--format=csv,noheader"], text=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, check=False)
    all_gpu = gpu.stdout.splitlines()
    pids = {entry["pid"] for entry in members}
    target_gpu = [line for line in all_gpu if line.split(",", 1)[0].strip().isdigit()
                  and int(line.split(",", 1)[0].strip()) in pids]
    return {"target_process_group_members": members,
            "gpu_compute_processes": {"returncode": gpu.returncode, "output": all_gpu},
            "target_gpu_compute_processes": target_gpu,
            "target_residual_process_count": len(members),
            "target_gpu_residual_process_count": len(target_gpu),
            "no_target_residual_process": not members and not target_gpu}


def allocate_attempt(campaign_root, tag, requested):
    tag_root = campaign_root / tag
    tag_root.mkdir(parents=True, exist_ok=True)
    if requested is not None:
        root = tag_root / f"attempt_{requested:04d}"
        if root.exists():
            raise SystemExit(f"refusing to overwrite existing immutable attempt: {root}")
    else:
        values = [int(match.group(1)) for child in tag_root.iterdir()
                  if (match := re.fullmatch(r"attempt_(\d+)", child.name))]
        root = tag_root / f"attempt_{max(values) + 1 if values else 1:04d}"
    root.mkdir()
    return root


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--tool", required=True, type=Path)
    ap.add_argument("--nvbit-version", required=True)
    ap.add_argument("--nvbit-root", type=Path)
    ap.add_argument("--timeout-seconds", type=int, default=90)
    ap.add_argument("--instr-begin", default="101")
    ap.add_argument("--instr-end", default="102")
    ap.add_argument("--target-function-file", type=Path)
    ap.add_argument("--selected-static", type=int)
    ap.add_argument("--c16-output", type=Path)
    ap.add_argument("--occurrence", type=int, default=0)
    ap.add_argument("--tool-verbose", default="0")
    ap.add_argument("--attempt", type=int)
    ap.add_argument("--root", type=Path, default=Path("/data/c16/olmoe_v40/supervised"))
    a = ap.parse_args()
    root = allocate_attempt(a.root, a.tag, a.attempt)
    markers = root / "markers.log"
    trace = root / (a.c16_output.name if a.c16_output else "trace.bin")
    env = os.environ.copy()
    env.update({"PATH": "/usr/local/cuda-12.8/bin:" + env["PATH"], "NVDISASM": "nvdisasm",
                "INSTR_BEGIN": a.instr_begin, "INSTR_END": a.instr_end, "TOOL_VERBOSE": a.tool_verbose,
                "CUDA_INJECTION64_PATH": str(a.tool), "C16_V40_MARKER_FILE": str(markers),
                "C16_P5_OUTPUT": str(trace), "C16_P5_OCCURRENCE": str(a.occurrence)})
    function_sha = None
    if a.target_function_file:
        env["C16_P1_FUNCTION"] = a.target_function_file.read_text(encoding="utf-8").strip()
        function_sha = sha256(a.target_function_file)
    if a.selected_static is not None:
        env["C16_P3_STATIC"] = str(a.selected_static)
    started = datetime.now(timezone.utc).isoformat()
    argv = [PYTHON, REPLAY]
    stdout = (root / "stdout.log").open("w")
    stderr = (root / "stderr.log").open("w")
    proc = subprocess.Popen(argv, cwd=REPO, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
    receipt = {"schema_version": 2, "tag": a.tag, "attempt_root": str(root), "pid": proc.pid,
               "pgid": os.getpgid(proc.pid), "argv": argv, "nvbit_version": a.nvbit_version,
               "nvbit_root": str(a.nvbit_root) if a.nvbit_root else None, "tool_path": str(a.tool),
               "tool_sha256": sha256(a.tool), "canonical_replay_path": REPLAY,
               "canonical_replay_sha256": sha256(Path(REPLAY)),
               "function_identity_path": str(a.target_function_file) if a.target_function_file else None,
               "function_identity_sha256": function_sha, "selected_static": a.selected_static,
               "occurrence": a.occurrence, "c16_output_path": str(trace), "start": started,
               "timeout_seconds": a.timeout_seconds,
               "relevant_environment": {key: env[key] for key in ("CUDA_INJECTION64_PATH", "INSTR_BEGIN", "INSTR_END", "NVDISASM", "C16_P1_FUNCTION", "C16_P3_STATIC", "C16_P5_OUTPUT", "C16_P5_OCCURRENCE") if key in env}}
    atomic_json(root / "SUPERVISOR_RECEIPT.json", receipt)
    deadline = time.monotonic() + a.timeout_seconds
    while proc.poll() is None and time.monotonic() < deadline:
        time.sleep(0.5)
    timed_out = proc.poll() is None
    if timed_out:
        capture_timeout(root, proc.pid)
        os.killpg(receipt["pgid"], signal.SIGTERM)
        try:
            proc.wait(8)
        except subprocess.TimeoutExpired:
            os.killpg(receipt["pgid"], signal.SIGKILL)
            proc.wait()
    stdout.close()
    stderr.close()
    residual = residual_check(receipt["pgid"])
    marker_lines = markers.read_text(errors="replace").splitlines() if markers.exists() else []
    furthest_marker = marker_lines[-1] if marker_lines else None
    clean = not timed_out and proc.returncode == 0 and M6 in marker_lines and residual["no_target_residual_process"]
    if clean:
        phase = "CLEAN_EXIT"
    elif timed_out:
        phase = "PRE_TARGET_INIT_HANG" if "M1_BEFORE_EXPERT58_CALL" not in marker_lines else "TARGET_CALL_HANG" if "M2_AFTER_EXPERT58_CALL_RETURN" not in marker_lines else "CUDA_SYNC_HANG" if "M4_AFTER_TORCH_CUDA_SYNCHRONIZE" not in marker_lines else "TEARDOWN_HANG"
    elif proc.returncode != 0:
        phase = "PROCESS_ERROR"
    elif not residual["no_target_residual_process"]:
        phase = "RESIDUAL_PROCESS_ERROR"
    else:
        phase = "INCOMPLETE_EXIT"
    replay_output = root / "output.sha256"
    result = {"returncode": proc.returncode, "timed_out": timed_out, "markers": marker_lines,
              "furthest_marker": furthest_marker, "phase": phase, "residual_process_check": residual,
              "output_sha256": replay_output.read_text(encoding="ascii").strip() if replay_output.is_file() else None,
              "c16_trace_sha256": sha256(trace) if trace.is_file() else None, "end": datetime.now(timezone.utc).isoformat()}
    atomic_json(root / "result.json", result)
    receipt.update({"end": result["end"], "returncode": proc.returncode, "timed_out": timed_out,
                    "furthest_marker": furthest_marker, "phase": phase, "residual_process_check": residual,
                    "output_sha256": result["output_sha256"], "c16_trace_sha256": result["c16_trace_sha256"]})
    atomic_json(root / "SUPERVISOR_RECEIPT.json", receipt)
    print(json.dumps({"tag": a.tag, "attempt_root": str(root), "pid": proc.pid,
                      "returncode": proc.returncode, "phase": phase, "timed_out": timed_out}))


if __name__ == "__main__":
    main()
