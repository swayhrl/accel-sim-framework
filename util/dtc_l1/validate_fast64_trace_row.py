#!/usr/bin/env python3
"""Fail-closed validation and compact evidence binding for one FAST64 replay."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_value(path: pathlib.Path, key: str) -> str:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        fields = line.split("\t")
        if fields and fields[0] == key:
            return fields[2]
    raise ValueError(f"workload {key!r} absent from payload manifest {path}")


def run_value(path: pathlib.Path, key: str) -> str:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        fields = line.split("\t", 1)
        if len(fields) == 2 and fields[0] == key:
            value = fields[1]
    try:
        return value
    except UnboundLocalError as error:
        raise ValueError(f"{key!r} absent from run manifest {path}") from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=pathlib.Path)
    parser.add_argument("--workload-id", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--config-file", required=True, type=pathlib.Path)
    parser.add_argument("--core-sha", required=True)
    parser.add_argument("--framework-sha", required=True)
    parser.add_argument("--payload-manifest", required=True, type=pathlib.Path)
    parser.add_argument("--classification", required=True)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    args = parser.parse_args()

    run_manifest = args.run_dir / "RUN_MANIFEST.tsv"
    stdout = args.run_dir / "simulator.stdout"
    stderr = args.run_dir / "simulator.stderr"
    resource = args.run_dir / "resource.time"
    for path in (run_manifest, stdout, stderr, resource, args.config_file,
                 args.payload_manifest):
        if not path.is_file():
            parser.error("required file does not exist: " + str(path))
    if run_value(run_manifest, "simulator_exit_status") != "0":
        parser.error("simulator did not terminate with exit status zero")

    body = stdout.read_text(encoding="utf-8", errors="replace")
    if "GPGPU-Sim: *** exit detected ***" not in body:
        parser.error("natural simulator exit marker is absent")
    failure = re.search(
        r"assertion failed|fatal error|deadlock detected|segmentation fault|core dumped",
        body + "\n" + stderr.read_text(encoding="utf-8", errors="replace"),
        flags=re.IGNORECASE,
    )
    if failure:
        parser.error("failure signature found: " + failure.group(0))

    trace_list = pathlib.Path(run_value(run_manifest, "trace_list"))
    if not trace_list.is_file():
        parser.error("trace list unavailable: " + str(trace_list))
    expected_sha = manifest_value(args.payload_manifest, args.workload_id.lower())
    if sha256(trace_list) != expected_sha:
        parser.error("trace list SHA-256 disagrees with frozen payload manifest")
    root = trace_list.parent
    expected = [str(root / line.strip()) for line in
                trace_list.read_text(encoding="utf-8", errors="replace").splitlines()
                if line.strip().endswith(".traceg")]
    actual = re.findall(r"^Processing kernel (.+)$", body, flags=re.MULTILINE)
    if actual != expected:
        parser.error("processed trace sequence disagrees with frozen trace list")

    parser_path = pathlib.Path(__file__).with_name("parse_dtc_l1_summary.py")
    command = [
        sys.executable, str(parser_path), str(stdout), "--output", str(args.output),
        "--core-sha", args.core_sha, "--framework-sha", args.framework_sha,
        "--config-id", args.config_id, "--config-file", str(args.config_file),
        "--workload-id", args.workload_id, "--workload-file", str(args.payload_manifest),
        "--resource-file", str(resource), "--result-classification", args.classification,
        "--strict",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(command, check=True)
    result = json.loads(args.output.read_text(encoding="utf-8"))
    result["external_artifacts"] = {
        "run_dir": str(args.run_dir),
        "run_manifest_sha256": sha256(run_manifest),
        "simulator_stdout_bytes": stdout.stat().st_size,
        "simulator_stdout_sha256": sha256(stdout),
        "simulator_stderr_bytes": stderr.stat().st_size,
        "simulator_stderr_sha256": sha256(stderr),
        "resource_time_sha256": sha256(resource),
        "trace_list": str(trace_list),
        "trace_list_sha256": sha256(trace_list),
        "processed_trace_members": actual,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(f"FAST64_ROW_PASS workload={args.workload_id} mode={args.mode} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
