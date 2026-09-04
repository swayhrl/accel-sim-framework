#!/usr/bin/env python3
"""Route-E host suitability gate: no toolkit/tracer requirement."""
from __future__ import annotations
import argparse, datetime as dt, json, shutil, subprocess
from pathlib import Path

def command(*argv):
    try:
        result = subprocess.run(argv, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return result.returncode, result.stdout
    except FileNotFoundError: return 127, f"command not found: {argv[0]}\n"

def parse_gpu_rows(text: str, count: int) -> list[str]:
    rows = [row.strip() for row in text.splitlines() if row.strip()]
    if len(rows) != count: return [f"expected exactly {count} visible GPU(s), saw {len(rows)}"]
    fields = [row.split(", ") for row in rows]
    errors = []
    if len({row[0] for row in fields if len(row) >= 4}) != 1: errors.append("visible GPUs are not the same model")
    for row in fields:
        if len(row) != 4 or row[1] != "8.6": errors.append(f"Route E requires SM86; got {row}"); continue
        memory = int(row[2].split()[0]) if row[2].split()[0].isdigit() else 0
        if memory < 12288: errors.append(f"Route E requires >=12 GiB VRAM; got {row[2]}")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--framework-root", type=Path); parser.add_argument("--work-root", type=Path); parser.add_argument("--minimum-free-gib", type=int, default=500); parser.add_argument("--required-gpu-count", type=int, default=4); parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        assert not parse_gpu_rows("RTX 3080 Ti, 8.6, 12288 MiB, 555.1\n" * 4, 4)
        assert parse_gpu_rows("RTX 3080 Ti, 8.6, 12288 MiB, 555.1\n" * 3, 4)
        assert parse_gpu_rows("RTX 3080 Ti, 8.9, 12288 MiB, 555.1\n" * 4, 4)
        print("PASS host preflight parser self-test"); return 0
    if not args.framework_root or not args.work_root: parser.error("--framework-root and --work-root are required unless --self-test")
    root, work = args.framework_root.resolve(), args.work_root.resolve(); work.mkdir(parents=True, exist_ok=True)
    errors = []
    if args.required_gpu_count != 4: errors.append("Route E requires required-gpu-count=4")
    for item in ("bash", "python3", "git", "sha256sum", "tar", "nvidia-smi"):
        if not shutil.which(item): errors.append(f"missing command: {item}")
    rc, gpu = command("nvidia-smi", "--query-gpu=name,compute_cap,memory.total,driver_version", "--format=csv,noheader")
    if rc: errors.append("nvidia-smi query failed")
    else: errors += parse_gpu_rows(gpu, args.required_gpu_count)
    free_gib = shutil.disk_usage(work).free // 1024**3
    if free_gib < args.minimum_free_gib: errors.append(f"free disk {free_gib} GiB < {args.minimum_free_gib} GiB")
    _, cpu = command("nproc"); _, memory = command("free", "-h"); network_rc, network = command("curl", "--fail", "--silent", "--head", "https://github.com")
    if network_rc: errors.append("approved dependency network reachability check failed")
    _, commit = command("git", "-C", str(root), "rev-parse", "HEAD"); _, branch = command("git", "-C", str(root), "branch", "--show-current")
    report = {"schema_version":"m4a-route-e-host-preflight-v1", "timestamp_utc":dt.datetime.now(dt.timezone.utc).isoformat(), "status":"PASS" if not errors else "BLOCKED", "errors":errors, "gpu_query":gpu, "free_gib":free_gib, "minimum_free_gib":args.minimum_free_gib, "cpu":cpu.strip(), "host_memory":memory, "network_github_head_exit":network_rc, "framework_commit":commit.strip(), "framework_branch":branch.strip(), "note":"nvcc/tracer deliberately not checked at host-only gate"}
    output = work / "host-preflight.json"; output.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n"); print(f"{report['status']} report={output}")
    for error in errors: print(f"error: {error}")
    return 0 if not errors else 1
if __name__ == "__main__": raise SystemExit(main())
