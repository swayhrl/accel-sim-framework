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
    matches: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        fields = line.split("\t", 1)
        if len(fields) == 2 and fields[0] == key:
            matches.append(fields[1])
    if len(matches) != 1:
        qualifier = "absent" if not matches else f"duplicated {len(matches)} times"
        raise ValueError(f"{key!r} {qualifier} in run manifest {path}")
    return matches[0]


def receipt_values(path: pathlib.Path) -> dict[str, str]:
    """Read a small receipt strictly: every key must occur exactly once."""
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        fields = line.split("\t", 1)
        if len(fields) != 2:
            raise ValueError(f"malformed receipt line in {path}: {line!r}")
        key, value = fields
        if key in values:
            raise ValueError(f"duplicate receipt key {key!r} in {path}")
        values[key] = value
    return values


def require_value(values: dict[str, str], key: str, path: pathlib.Path) -> str:
    try:
        return values[key]
    except KeyError as error:
        raise ValueError(f"{key!r} absent from receipt {path}") from error


def validate_immutable_attempt(args: argparse.Namespace, run_manifest: pathlib.Path,
                               stdout: pathlib.Path) -> dict[str, str]:
    """Validate the v2 receipt boundary and the calibrated single-epoch proof.

    The epoch checks were calibrated against the three known-clean historical
    NN directories whose names contain ``_r2``: one perf stream, one
    initialization marker, and one natural exit marker.  Those historical
    directories predate the immutable-v2 receipt schema and are *not* formal
    FAST64.1 R2 evidence.  Receipts are the primary future exactly-once
    witness; these output checks prevent an additional simulator epoch from
    being hidden.
    """
    required_manifest = (
        "runner_schema", "runner_sha256", "immutable_runner_path", "attempt_uuid",
        "framework_scientific_config_source_sha", "core_source_head",
        "observer_overlay_sha256", "simulator_sha256", "launch_utc",
        "simulator_exit_status", "terminal_utc",
    )
    manifest = {key: run_value(run_manifest, key) for key in required_manifest}
    if manifest["runner_schema"] != "FAST64_TRACE_V2_IMMUTABLE_ATTEMPT":
        raise ValueError("immutable attempt has an unexpected runner schema")
    if manifest["framework_scientific_config_source_sha"] != args.framework_sha:
        raise ValueError("framework scientific/config source identity mismatch")
    if manifest["core_source_head"] != args.core_sha:
        raise ValueError("Core source identity mismatch")
    if args.observer_sha is not None and manifest["observer_overlay_sha256"] != args.observer_sha:
        raise ValueError("observer overlay identity mismatch")
    if args.runtime_sha is not None and manifest["simulator_sha256"] != args.runtime_sha:
        raise ValueError("runtime binary identity mismatch")
    runner = pathlib.Path(manifest["immutable_runner_path"])
    if not runner.is_file() or sha256(runner) != manifest["runner_sha256"]:
        raise ValueError("immutable runner path/SHA no longer verifies")
    if runner.stat().st_mode & 0o222:
        raise ValueError("immutable runner has writable permission bits")

    start_path = args.run_dir / "RUN_START.tsv"
    terminal_path = args.run_dir / "RUN_TERMINAL.tsv"
    for receipt in (start_path, terminal_path):
        if not receipt.is_file() or receipt.is_symlink():
            raise ValueError(f"required regular receipt unavailable: {receipt}")
    start = receipt_values(start_path)
    terminal = receipt_values(terminal_path)
    for receipt, expected_type in ((start, "START"), (terminal, "TERMINAL")):
        if require_value(receipt, "receipt_schema", start_path if receipt is start else terminal_path) != "FAST64_ATTEMPT_RECEIPT_V1":
            raise ValueError("unexpected attempt receipt schema")
        if require_value(receipt, "receipt_type", start_path if receipt is start else terminal_path) != expected_type:
            raise ValueError("unexpected attempt receipt type")
        for key in ("attempt_uuid", "runner_sha256", "immutable_runner_path"):
            if require_value(receipt, key, start_path if receipt is start else terminal_path) != manifest[key]:
                raise ValueError(f"receipt {key} disagrees with immutable manifest")
    if require_value(start, "launch_utc", start_path) != manifest["launch_utc"]:
        raise ValueError("START receipt launch time disagrees with manifest")
    if require_value(terminal, "simulator_exit_status", terminal_path) != "0":
        raise ValueError("TERMINAL receipt does not record natural exit zero")
    if require_value(terminal, "terminal_utc", terminal_path) != manifest["terminal_utc"]:
        raise ValueError("TERMINAL receipt time disagrees with manifest")

    perf_streams = list(args.run_dir.glob("perf_counter*.csv.gz"))
    if len(perf_streams) != 1:
        raise ValueError(f"single-epoch proof requires one perf stream, found {len(perf_streams)}")
    body = stdout.read_text(encoding="utf-8", errors="replace")
    if body.count("GPGPU-Sim uArch: performance model initialization complete.") != 1:
        raise ValueError("single-epoch proof requires exactly one simulator initialization marker")
    if body.count("GPGPU-Sim: *** exit detected ***") != 1:
        raise ValueError("single-epoch proof requires exactly one simulator exit marker")
    return {
        "start_receipt_sha256": sha256(start_path),
        "terminal_receipt_sha256": sha256(terminal_path),
        "attempt_uuid": manifest["attempt_uuid"],
        "runner_sha256": manifest["runner_sha256"],
        "immutable_runner_path": manifest["immutable_runner_path"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=pathlib.Path)
    parser.add_argument("--workload-id", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--config-file", required=True, type=pathlib.Path)
    parser.add_argument("--core-sha", required=True)
    parser.add_argument("--framework-sha", required=True)
    parser.add_argument("--observer-sha",
                        help="expected observer overlay SHA-256; required by formal collectors")
    parser.add_argument("--runtime-sha",
                        help="expected simulator binary SHA-256; required by formal collectors")
    parser.add_argument("--payload-manifest", required=True, type=pathlib.Path)
    parser.add_argument("--classification", required=True)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--require-immutable-attempt", action="store_true",
                        help="require v2 immutable runner receipts and the calibrated single-epoch proof")
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
    manifest_observer_sha = run_value(run_manifest, "observer_overlay_sha256")
    manifest_runtime_sha = run_value(run_manifest, "simulator_sha256")
    if args.observer_sha is not None and manifest_observer_sha != args.observer_sha:
        parser.error("observer overlay identity mismatch")
    if args.runtime_sha is not None and manifest_runtime_sha != args.runtime_sha:
        parser.error("runtime binary identity mismatch")

    immutable_attempt: dict[str, str] | None = None
    if args.require_immutable_attempt:
        try:
            immutable_attempt = validate_immutable_attempt(args, run_manifest, stdout)
        except ValueError as error:
            parser.error(str(error))

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
        "--workload-id", args.workload_id, "--mode", args.mode,
        "--workload-file", str(args.payload_manifest),
        "--resource-file", str(resource), "--result-classification", args.classification,
        "--strict",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(command, check=True)
    result = json.loads(args.output.read_text(encoding="utf-8"))
    result["provenance"]["observer_overlay_sha256"] = manifest_observer_sha
    result["provenance"]["runtime_binary_sha256"] = manifest_runtime_sha
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
    if immutable_attempt is not None:
        result["immutable_attempt"] = immutable_attempt
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(f"FAST64_ROW_PASS workload={args.workload_id} mode={args.mode} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
