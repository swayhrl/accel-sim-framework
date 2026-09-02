#!/usr/bin/env python3
"""Record and validate an M4A-C capture host; never installs or traces."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
from pathlib import Path


def command(*argv: str) -> tuple[int, str]:
    try:
        result = subprocess.run(argv, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except FileNotFoundError:
        return 127, f"command not found: {argv[0]}\n"
    return result.returncode, result.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--minimum-free-gib", type=int, default=500)
    args = parser.parse_args()
    root, work = args.framework_root.resolve(), args.work_root.resolve()
    if args.minimum_free_gib < 1: parser.error("--minimum-free-gib must be positive")
    required = ["bash", "python3", "git", "sha256sum", "tar", "nvidia-smi", "nvcc"]
    missing = [x for x in required if not shutil.which(x)]
    errors = [f"missing commands: {', '.join(missing)}"] if missing else []
    tracer = root / "util/tracer_nvbit/tracer_tool/tracer_tool.so"
    post = root / "util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing"
    if not tracer.is_file(): errors.append(f"missing built tracer: {tracer}")
    if not post.is_file(): errors.append(f"missing postprocessor: {post}")
    usage = shutil.disk_usage(work)
    free_gib = usage.free // (1024 ** 3)
    if free_gib < args.minimum_free_gib: errors.append(f"free disk {free_gib} GiB < {args.minimum_free_gib} GiB")
    gpu_rc, gpu = command("nvidia-smi", "--query-gpu=name,compute_cap,driver_version,memory.total", "--format=csv,noheader")
    if gpu_rc: errors.append("nvidia-smi query failed")
    rows = [x for x in gpu.splitlines() if x.strip()]
    if gpu_rc == 0:
        if len(rows) != 1: errors.append(f"expected exactly one visible GPU, saw {len(rows)}")
        elif "8.6" not in rows[0]: errors.append(f"paper route requires SM86; got {rows[0]}")
    _, nvcc = command("nvcc", "--version") if shutil.which("nvcc") else (127, "nvcc absent")
    _, sha = command("git", "-C", str(root), "rev-parse", "HEAD") if (root / ".git").exists() else (1, "not a git checkout")
    work.mkdir(parents=True, exist_ok=True)
    report = {"schema_version": "m4a-c-host-preflight-v1", "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "framework_root": str(root), "framework_commit": sha.strip(), "free_gib": free_gib,
              "minimum_free_gib": args.minimum_free_gib, "gpu_query": gpu, "nvcc": nvcc,
              "tracer": str(tracer), "postprocessor": str(post), "status": "PASS" if not errors else "BLOCKED", "errors": errors}
    path = work / "host-preflight.json"; path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"{report['status']} report={path}")
    for error in errors: print(f"error: {error}")
    return 0 if not errors else 1


if __name__ == "__main__": raise SystemExit(main())
