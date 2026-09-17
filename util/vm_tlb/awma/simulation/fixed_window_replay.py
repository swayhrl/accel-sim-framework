#!/usr/bin/env python3
"""Admit and run one hash-bound trace bundle for the qualified 10k window."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import simulation_foundation as foundation


FIXED_WINDOW_CYCLES = 10000
STATUSES = (
    "EXPECTED_FIXED_WINDOW_BOUNDARY",
    "NORMAL_COMPLETION",
    "PARSER_ABORT",
    "SIMULATOR_ASSERT_OR_FATAL",
    "EXTERNAL_RUNTIME_FAILURE",
)
FATAL = re.compile(r"(?:assert(?:ion)?(?: failed)?|\bfatal\b|segmentation fault|core dumped)", re.IGNORECASE)


def classify_execution(log_text, returncode, admitted=True, external_failure=False):
    if not admitted:
        return "PARSER_ABORT"
    if external_failure:
        return "EXTERNAL_RUNTIME_FAILURE"
    if FATAL.search(log_text) or returncode < 0:
        return "SIMULATOR_ASSERT_OR_FATAL"
    cycle_match = re.findall(r"^gpu_sim_cycle = ([0-9]+)$", log_text, re.MULTILINE)
    boundary = "GPGPU-Sim: ** break due to reaching the maximum cycles (or instructions) **" in log_text
    if returncode == 0 and boundary and cycle_match and int(cycle_match[-1]) == FIXED_WINDOW_CYCLES:
        return "EXPECTED_FIXED_WINDOW_BOUNDARY"
    if boundary:
        return "EXTERNAL_RUNTIME_FAILURE"
    if returncode == 0:
        return "NORMAL_COMPLETION"
    return "EXTERNAL_RUNTIME_FAILURE"


def last_config_value(path, option):
    pattern = re.compile(r"^\s*" + re.escape(option) + r"\s+([^#\s]+)")
    values = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            values.append(match.group(1))
    return values[-1] if values else None


def environment_receipt(overrides):
    relevant = {key: os.environ.get(key, "") for key in ("PATH", "GPGPUSIM_ROOT", "LD_LIBRARY_PATH")}
    relevant.update(overrides)
    return relevant


def write_manifest(path, values):
    lines = ["key\tvalue"] + ["%s\t%s" % item for item in sorted(values.items())]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare_effective_config(base_config, overlay, output_path):
    allowed = {
        "-gpgpu_vm_object_map",
        "-gpgpu_vm_weight_segment_map",
        "-gpgpu_max_cycle",
    }
    options = {}
    for raw_line in overlay.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or parts[0] not in allowed:
            raise foundation.ContractError("unsupported runtime overlay option: %s" % line)
        if parts[0] in options:
            raise foundation.ContractError("duplicate runtime overlay option: %s" % parts[0])
        options[parts[0]] = parts[1]
    missing = sorted(allowed - set(options))
    if missing:
        raise foundation.ContractError("runtime overlay missing: %s" % ", ".join(missing))
    if options["-gpgpu_max_cycle"] != str(FIXED_WINDOW_CYCLES):
        raise foundation.ContractError("runtime overlay must set the fixed 10000-cycle policy")
    assets = {}
    for option in ("-gpgpu_vm_object_map", "-gpgpu_vm_weight_segment_map"):
        path = Path(options[option]).resolve()
        if not path.is_file():
            raise foundation.ContractError("runtime overlay asset not found: %s" % path)
        assets[option] = {"path": str(path), "sha256": foundation.sha(path)}
    content = base_config.read_text(encoding="utf-8")
    if content and not content.endswith("\n"):
        content += "\n"
    content += overlay.read_text(encoding="utf-8")
    if content and not content.endswith("\n"):
        content += "\n"
    output_path.write_text(content, encoding="utf-8")
    overlay_closure = {"overlay": foundation.sha(overlay)}
    overlay_closure.update({option: receipt["sha256"] for option, receipt in assets.items()})
    return foundation.hash_root(overlay_closure), assets


def run(args):
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise foundation.ContractError("refusing to overwrite output directory")
    output_dir.mkdir(parents=True)
    log_path = output_dir / "run.log"
    try:
        admission = (json.loads(args.admission_receipt.read_text(encoding="utf-8"))
                     if args.admission_receipt else foundation.validate_bundle(args.manifest, args.parser))
    except (foundation.ContractError, json.JSONDecodeError, OSError) as exc:
        receipt = {"execution_status": "PARSER_ABORT", "reason": str(exc), "sim_input_id": None}
        (output_dir / "SIM_RUN_RECEIPT.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return receipt
    if admission.get("status") != "ADMITTED" or not admission.get("admitted"):
        receipt = {"execution_status": "PARSER_ABORT", "reason": admission.get("reason", "admission receipt is not ADMITTED"), "sim_input_id": None}
        (output_dir / "SIM_RUN_RECEIPT.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return receipt

    baseline = foundation.obj(args.baseline_identity)
    expected_baseline_id = foundation.identity_for("SIM_BASELINE", baseline)
    if baseline.get("sim_baseline_id") != expected_baseline_id:
        raise foundation.ContractError("SIM_BASELINE_ID does not match deterministic identity")
    if foundation.sha(args.binary) != baseline["binary_sha256"]:
        raise foundation.ContractError("qualified simulator binary hash mismatch")
    if not args.telemetry_exporter or not args.telemetry_exporter.is_file():
        raise foundation.ContractError("telemetry exporter is required")
    base_config_hash = foundation.sha(args.base_config)
    if base_config_hash not in baseline["accepted_base_config_sha256s"]:
        raise foundation.ContractError("base config is not admitted by SIM_BASELINE")
    effective_config = output_dir / "effective.config"
    overlay_hash, overlay_assets = prepare_effective_config(args.base_config, args.overlay, effective_config)
    if last_config_value(effective_config, "-gpgpu_max_cycle") != str(FIXED_WINDOW_CYCLES):
        raise foundation.ContractError("effective config does not end with the fixed 10000-cycle policy")

    overrides = {}
    for assignment in args.env:
        if "=" not in assignment:
            raise foundation.ContractError("--env must be KEY=VALUE")
        key, value = assignment.split("=", 1)
        if not key or not key.replace("_", "").isalnum():
            raise foundation.ContractError("invalid environment key")
        overrides[key] = value
    environment = os.environ.copy()
    environment.update(overrides)
    command = [str(args.binary.resolve()), "-config", str(effective_config), "-trace", str((args.manifest.resolve().parent / foundation.obj(args.manifest)["kernelslist"]).resolve())]

    external_failure = False
    returncode = 127
    try:
        completed = subprocess.run(
            command, cwd=output_dir, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=args.timeout_seconds, check=False,
        )
        returncode = completed.returncode
        log_text = completed.stdout
    except (OSError, subprocess.TimeoutExpired) as exc:
        external_failure = True
        log_text = "EXTERNAL_RUNTIME_FAILURE: %s\n" % exc
    log_path.write_text(log_text, encoding="utf-8")
    status = classify_execution(log_text, returncode, admitted=True, external_failure=external_failure)

    manifest_values = {
        "roi": foundation.obj(args.manifest)["target_id"],
        "framework_head": baseline["framework_sha"],
        "core_head": baseline["core_sha"],
        "sim_input_id": admission["sim_input_id"],
        "sim_baseline_id": baseline["sim_baseline_id"],
        "fixed_window_cycles": str(FIXED_WINDOW_CYCLES),
        "simulator_exit_status": str(returncode),
        "execution_status": status,
        "base_config_sha256": base_config_hash,
        "overlay_sha256": overlay_hash,
        "effective_config_sha256": foundation.sha(effective_config),
    }
    write_manifest(output_dir / "RUN_MANIFEST.tsv", manifest_values)

    telemetry = {"status": "NOT_RUN", "output_sha256": None}
    if status in ("EXPECTED_FIXED_WINDOW_BOUNDARY", "NORMAL_COMPLETION"):
        telemetry_dir = output_dir / "telemetry"
        exported = subprocess.run(
            [sys.executable, str(args.telemetry_exporter.resolve()), "--run-dir", str(output_dir),
             "--output-dir", str(telemetry_dir), "--trace-policy", args.trace_policy],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
        )
        telemetry["diagnostic"] = exported.stdout.strip()
        if telemetry_dir.is_dir():
            hashes = {str(path.relative_to(telemetry_dir)): foundation.sha(path) for path in sorted(telemetry_dir.glob("*")) if path.is_file()}
            telemetry["files"] = hashes
            if hashes:
                telemetry["output_sha256"] = foundation.hash_root(hashes)
        telemetry["status"] = "PASS" if exported.returncode == 0 and telemetry["output_sha256"] else "FAIL"

    environment_values = environment_receipt(overrides)
    command_hash = foundation.stable_id("COMMAND", {"argv": command}).split("_", 1)[1]
    environment_hash = foundation.stable_id("ENVIRONMENT", environment_values).split("_", 1)[1]
    receipt = {
        "schema_version": foundation.SCHEMA_VERSION,
        "execution_status": status,
        "returncode": returncode,
        "fixed_window_cycles": FIXED_WINDOW_CYCLES,
        "sim_input_id": admission["sim_input_id"],
        "sim_baseline_id": baseline["sim_baseline_id"],
        "base_config_sha256": base_config_hash,
        "config_sha256": foundation.sha(effective_config),
        "overlay_sha256": overlay_hash,
        "runtime_command_sha256": command_hash,
        "runtime_environment_sha256": environment_hash,
        "raw_log_sha256": foundation.sha(log_path),
        "telemetry": telemetry,
        "overlay_assets": overlay_assets,
    }
    (output_dir / "SIM_RUN_RECEIPT.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    classify = commands.add_parser("classify")
    classify.add_argument("log", type=Path)
    classify.add_argument("--returncode", type=int, required=True)
    replay = commands.add_parser("run")
    replay.add_argument("--manifest", type=Path, required=True)
    replay.add_argument("--parser", type=Path, required=True)
    replay.add_argument("--admission-receipt", type=Path,
                        help="previously hash-closed ADMITTED receipt; avoids a redundant parser scan")
    replay.add_argument("--baseline-identity", type=Path, required=True)
    replay.add_argument("--binary", type=Path, required=True)
    replay.add_argument("--base-config", type=Path, required=True)
    replay.add_argument("--overlay", type=Path, required=True)
    replay.add_argument("--output-dir", type=Path, required=True)
    replay.add_argument("--timeout-seconds", type=int, default=3600)
    replay.add_argument("--env", action="append", default=[])
    replay.add_argument("--telemetry-exporter", type=Path, required=True)
    replay.add_argument("--trace-policy", choices=("COMPUTE_ONLY_TP_PARTITION", "FULL_RANK0"), default="FULL_RANK0")
    args = parser.parse_args()
    try:
        if args.command == "classify":
            result = {"execution_status": classify_execution(args.log.read_text(encoding="utf-8"), args.returncode)}
        else:
            result = run(args)
        print(json.dumps(result, sort_keys=True, indent=2))
        execution_passed = result["execution_status"] in ("EXPECTED_FIXED_WINDOW_BOUNDARY", "NORMAL_COMPLETION")
        telemetry_passed = result.get("telemetry", {}).get("status") != "FAIL"
        return 0 if execution_passed and telemetry_passed else 2
    except foundation.ContractError as exc:
        print("CONTRACT_ERROR: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
