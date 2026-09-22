#!/usr/bin/env python3
"""Deterministic V40 owner for one official-NVBit expert58 replay attempt."""
import argparse
import json
import os
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = "/home/huangrulin/workspace/worktrees/accel-sim-c16-olmoe-v39"
PYTHON = "/data/c16/env/c16-py310/bin/python"
REPLAY = f"{REPO}/util/vm_tlb/c16/olmoe_v40_marked_replay.py"


def write(path, text):
    path.write_text(text, encoding="utf-8")


def command(path, argv, timeout=15):
    try:
        result = subprocess.run(argv, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=timeout)
        write(path, result.stdout)
    except Exception as error:
        write(path, f"DIAGNOSTIC_ERROR: {error}\n")


def capture(root, pid):
    diag = root / "timeout_diagnostics"; diag.mkdir(exist_ok=True)
    command(diag / "ps.txt", ["ps", "-o", "pid,ppid,pgid,stat,etime,wchan:32,cmd", "-p", str(pid)])
    command(diag / "ps_threads.txt", ["ps", "-L", "-p", str(pid), "-o", "pid,tid,stat,wchan:32,comm"])
    for name in ("status",):
        src = Path(f"/proc/{pid}/{name}")
        write(diag / f"proc_{name}.txt", src.read_text(errors="replace") if src.exists() else "ABSENT\n")
    task = Path(f"/proc/{pid}/task")
    if task.exists():
        for entry in task.iterdir():
            lines = []
            for name in ("status", "wchan", "stack"):
                src = entry / name
                try: lines.append(f"## {name}\n{src.read_text(errors='replace')}")
                except Exception as error: lines.append(f"## {name}\nERROR {error}\n")
            write(diag / f"thread_{entry.name}.txt", "\n".join(lines))
    command(diag / "gdb_threads.txt", ["gdb", "-batch", "-ex", "set pagination off", "-ex", "thread apply all bt", "-p", str(pid)], 12)
    command(diag / "nvidia_smi.txt", ["nvidia-smi"])
    command(diag / "gpu_processes.txt", ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader"])
    command(diag / "fds.txt", ["ls", "-l", f"/proc/{pid}/fd"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--tool", required=True, type=Path)
    ap.add_argument("--nvbit-version", required=True)
    ap.add_argument("--timeout-seconds", type=int, default=90)
    ap.add_argument("--instr-begin", default="101")
    ap.add_argument("--instr-end", default="102")
    ap.add_argument("--root", type=Path, default=Path("/data/c16/olmoe_v40/supervised"))
    a = ap.parse_args(); root = a.root / a.tag; root.mkdir(parents=True, exist_ok=True)
    markers = root / "markers.log"
    env = os.environ.copy(); env.update({"PATH": "/usr/local/cuda-12.8/bin:" + env["PATH"], "NVDISASM": "nvdisasm", "INSTR_BEGIN": a.instr_begin, "INSTR_END": a.instr_end, "TOOL_VERBOSE": "0", "CUDA_INJECTION64_PATH": str(a.tool), "C16_V40_MARKER_FILE": str(markers)})
    argv = [PYTHON, REPLAY]
    stdout = (root / "stdout.log").open("w"); stderr = (root / "stderr.log").open("w")
    started = datetime.now(timezone.utc).isoformat(); proc = subprocess.Popen(argv, cwd=REPO, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
    receipt = {"tag": a.tag, "pid": proc.pid, "pgid": os.getpgid(proc.pid), "argv": argv, "nvbit_version": a.nvbit_version, "tool": str(a.tool), "start": started, "timeout_seconds": a.timeout_seconds, "env": {k: env[k] for k in ("CUDA_INJECTION64_PATH", "INSTR_BEGIN", "INSTR_END", "NVDISASM")}}
    write(root / "SUPERVISOR_RECEIPT.json", json.dumps(receipt, indent=2) + "\n")
    deadline = time.monotonic() + a.timeout_seconds
    while proc.poll() is None and time.monotonic() < deadline: time.sleep(0.5)
    timed_out = proc.poll() is None
    if timed_out:
        capture(root, proc.pid)
        os.killpg(receipt["pgid"], signal.SIGTERM)
        try: proc.wait(8)
        except subprocess.TimeoutExpired: os.killpg(receipt["pgid"], signal.SIGKILL); proc.wait()
    stdout.close(); stderr.close()
    marker_lines = markers.read_text(errors="replace").splitlines() if markers.exists() else []
    phase = "CLEAN_EXIT" if proc.returncode == 0 and "M6_BEFORE_NORMAL_PROCESS_EXIT" in marker_lines else ("PRE_TARGET_INIT_HANG" if "M1_BEFORE_EXPERT58_CALL" not in marker_lines else "TARGET_CALL_HANG" if "M2_AFTER_EXPERT58_CALL_RETURN" not in marker_lines else "CUDA_SYNC_HANG" if "M4_AFTER_TORCH_CUDA_SYNCHRONIZE" not in marker_lines else "TEARDOWN_HANG")
    write(root / "result.json", json.dumps({"returncode": proc.returncode, "timed_out": timed_out, "markers": marker_lines, "phase": phase}, indent=2) + "\n")
    print(json.dumps({"tag": a.tag, "pid": proc.pid, "returncode": proc.returncode, "phase": phase, "timed_out": timed_out}))

if __name__ == "__main__": main()
