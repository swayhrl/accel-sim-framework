#!/usr/bin/env python3
"""Fail-closed controller and validator for the config-only TC80 campaign.

The tool can launch only the new TC80 conventional configuration.  It never
launches B16, IO, or OO; it refuses to reuse an output directory; and it binds
each run to the frozen FAST12 trace identity prepared by ``prepare-authority``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


CORE95 = "95ccdb7a056f2d53f740d90869785cac6d4ee0f5"
CORE658 = "6587238c60214d99491f4048e28ce8a3458c1509"
RUNTIME95 = Path("/tmp/dtc-fast64-zero-access-formal-95ccdb7a/accel-sim.out")
RUNTIME658 = Path("/tmp/dtc-fast64-2d-reserved-tag-repair-v1/accel-sim.out")
RUNTIME95_SHA = "462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9"
RUNTIME658_SHA = "29a3dd9f57a5accb89822ca3fcf06b11c437bfe864ee43d2ff5f26c8c056f3c1"
EXPECTED_DL1 = "S:32:128:20,L:T:m:L:L,A:512:8,16:0,32"
EXPECTED_GEOMETRY = "32x20x128=640_lines=81920_bytes"
GEOMETRY_PROFILES = {
    "TC80_S32_W20": {"dl1": EXPECTED_DL1, "geometry": EXPECTED_GEOMETRY},
    "CM5_S128_W5": {
        "dl1": "S:128:128:5,L:T:m:L:L,A:512:8,16:0,32",
        "geometry": "128x5x128=640_lines=81920_bytes",
    },
}
EXPECTED_BASE_CONFIG_SHA = "1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde"
EXPECTED_TRACE_CONFIG_SHA = "19dd14b3a4b6c1a1cb2833bd091f0dbd485ad79336ef7d4b0c9db1f7c46f504e"
EXPECTED_PRIMARY_OVERLAY_SHA = "92496d3664f24539df8ec4d17fe717b526a8eb5a1a391ef4a2db86e9a3ba44f4"
EXPECTED_CM5_OVERLAY_SHA = "f365018a72901d8d8aeda2088382014b9ddd5369b614da7101680cf6a63f9b93"
STAGE_BINDINGS = {
    "CM2": ("TC80_S32_W20", EXPECTED_PRIMARY_OVERLAY_SHA),
    "CM3": ("TC80_S32_W20", EXPECTED_PRIMARY_OVERLAY_SHA),
    "CM5": ("CM5_S128_W5", EXPECTED_CM5_OVERLAY_SHA),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def tsv_read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def tsv_write(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def kv_read(path: Path) -> dict[str, str]:
    rows = tsv_read(path)
    if rows and set(rows[0]) == {"key", "value"}:
        return {row["key"]: row["value"] for row in rows}
    answer: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition("\t")
        if sep and key != "key":
            answer[key] = value
    return answer


def kv_write(path: Path, values: dict[str, object]) -> None:
    tsv_write(path, ["key", "value"], [{"key": key, "value": value} for key, value in values.items()])


def trace_members(trace_list: Path) -> tuple[int, int, str]:
    members: list[tuple[str, int, str]] = []
    for line in trace_list.read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if not item or not item.endswith(".traceg"):
            continue
        member = Path(item)
        if not member.is_absolute():
            member = trace_list.parent / member
        if not member.is_file():
            raise RuntimeError(f"missing frozen trace member: {member}")
        members.append((item, member.stat().st_size, digest(member)))
    if not members:
        raise RuntimeError(f"no .traceg members named by {trace_list}")
    payload = "".join(f"{name}\t{size}\t{sha}\n" for name, size, sha in members).encode()
    return len(members), sum(size for _, size, _ in members), hashlib.sha256(payload).hexdigest()


def locate_raw_manifest(source_log: str) -> dict[str, str]:
    run_manifest = Path(source_log).parent / "RUN_MANIFEST.tsv"
    if not run_manifest.is_file():
        raise RuntimeError(f"missing frozen raw run manifest: {run_manifest}")
    return kv_read(run_manifest)


def prepare_authority(args: argparse.Namespace) -> None:
    summary_rows = [row for row in tsv_read(Path(args.summary)) if row["workload"] != "GM-FAST12"]
    if len(summary_rows) != 12:
        raise RuntimeError(f"expected exactly 12 frozen FAST12 rows, found {len(summary_rows)}")
    raw_rows = tsv_read(Path(args.raw_index))
    raw = {(row["workload"], row["mode"]): row for row in raw_rows}
    fields = [
        "ordinal", "workload", "instructions", "trace_list", "trace_list_sha256",
        "trace_member_count", "trace_total_bytes", "trace_member_manifest_sha256",
        "b16_cycles", "io_cycles", "oo_cycles", "b16_source_log", "b16_source_stdout_sha256",
        "io_source_log", "io_source_stdout_sha256", "oo_source_log", "oo_source_stdout_sha256",
        "run_core_sha", "runtime_path", "runtime_sha256", "frozen_framework_sha",
        "frozen_b16_config_sha256", "frozen_trace_config_sha256", "selection_reason",
    ]
    out: list[dict[str, object]] = []
    for ordinal, summary in enumerate(summary_rows, start=1):
        workload = summary["workload"]
        refs = {mode: raw.get((workload, mode)) for mode in ("BASE", "IO", "OO")}
        if any(value is None for value in refs.values()):
            raise RuntimeError(f"missing frozen source mapping for {workload}")
        base_manifest = locate_raw_manifest(refs["BASE"]["source_log"])
        trace_list = Path(base_manifest["trace_list"])
        if not trace_list.is_file():
            raise RuntimeError(f"missing frozen trace list for {workload}: {trace_list}")
        trace_sha = digest(trace_list)
        if trace_sha != base_manifest["trace_list_sha256"]:
            raise RuntimeError(f"frozen trace list hash changed for {workload}")
        count, total_bytes, members_sha = trace_members(trace_list)
        if workload == "2DConvolution":
            core, runtime, runtime_sha = CORE658, RUNTIME658, RUNTIME658_SHA
            reason = "Required repaired conventional-MSHR Core658 identity for the frozen 2DConvolution path."
        else:
            core, runtime, runtime_sha = CORE95, RUNTIME95, RUNTIME95_SHA
            reason = "Frozen formal Core95 conventional Base path; its zero-access change is IO/OO-only."
        if not runtime.is_file() or digest(runtime) != runtime_sha:
            raise RuntimeError(f"required immutable runtime unavailable or wrong for {workload}: {runtime}")
        out.append({
            "ordinal": ordinal, "workload": workload, "instructions": summary["instructions"],
            "trace_list": str(trace_list), "trace_list_sha256": trace_sha,
            "trace_member_count": count, "trace_total_bytes": total_bytes,
            "trace_member_manifest_sha256": members_sha,
            "b16_cycles": summary["base_cycles"], "io_cycles": summary["io_cycles"],
            "oo_cycles": summary["oo_cycles"],
            "b16_source_log": refs["BASE"]["source_log"],
            "b16_source_stdout_sha256": refs["BASE"]["stdout_sha256"],
            "io_source_log": refs["IO"]["source_log"],
            "io_source_stdout_sha256": refs["IO"]["stdout_sha256"],
            "oo_source_log": refs["OO"]["source_log"],
            "oo_source_stdout_sha256": refs["OO"]["stdout_sha256"],
            "run_core_sha": core, "runtime_path": str(runtime), "runtime_sha256": runtime_sha,
            "frozen_framework_sha": base_manifest.get("framework_scientific_config_source_sha", "UNKNOWN"),
            "frozen_b16_config_sha256": base_manifest.get("config_sha256", "UNKNOWN"),
            "frozen_trace_config_sha256": base_manifest.get("trace_config_sha256", "UNKNOWN"),
            "selection_reason": reason,
        })
    if [row["workload"] for row in out] != [row["workload"] for row in summary_rows]:
        raise RuntimeError("frozen workload ordering changed while preparing authority")
    tsv_write(Path(args.output), fields, out)


def authority_row(path: Path, workload: str) -> dict[str, str]:
    found = [row for row in tsv_read(path) if row["workload"] == workload]
    if len(found) != 1:
        raise RuntimeError(f"authority must contain exactly one {workload} row")
    return found[0]


def require_stage_binding(stage: str, geometry_profile: str, overlay_sha256: str) -> None:
    """Reject a stage/profile/hash mix before any immutable attempt is made."""
    expected = STAGE_BINDINGS.get(stage)
    if expected is None:
        raise RuntimeError(f"unknown TC80 stage binding: {stage}")
    expected_profile, expected_overlay = expected
    if (geometry_profile, overlay_sha256) != expected:
        raise RuntimeError(
            f"stage binding preflight failed for {stage}: expected profile/hash="
            f"{expected_profile}/{expected_overlay}; got {geometry_profile}/{overlay_sha256}"
        )


def resolve_config(args: argparse.Namespace) -> None:
    resolved: dict[str, tuple[str, str]] = {}
    for config_name in (args.base_config, args.overlay, args.trace_config):
        config = Path(config_name)
        for raw in config.read_text(encoding="utf-8").splitlines():
            text = raw.split("#", 1)[0].strip()
            if not text or not text.startswith("-"):
                continue
            option, value = (text.split(maxsplit=1) + [""])[:2]
            resolved[option] = (value, str(config))
    rows = [{"option": option, "value": value, "source_config": source}
            for option, (value, source) in sorted(resolved.items())]
    tsv_write(Path(args.output), ["option", "value", "source_config"], rows)


def run_tc80(args: argparse.Namespace) -> None:
    require_stage_binding(args.stage, args.geometry_profile, args.overlay_sha256)
    authority = authority_row(Path(args.authority), args.workload)
    profile = GEOMETRY_PROFILES[args.geometry_profile]
    # The simulator runs from a fresh attempt directory; all config paths must
    # therefore be absolute before changing cwd, while the immutable receipt
    # still records the exact digest of the repository files.
    base, overlay, trace_config = (Path(args.base_config).resolve(), Path(args.overlay).resolve(), Path(args.trace_config).resolve())
    simulator, trace = Path(authority["runtime_path"]), Path(authority["trace_list"])
    expected = {
        "base_config_sha256": EXPECTED_BASE_CONFIG_SHA,
        "trace_config_sha256": EXPECTED_TRACE_CONFIG_SHA,
        "overlay_sha256": args.overlay_sha256,
        "runtime_sha256": authority["runtime_sha256"],
        "trace_list_sha256": authority["trace_list_sha256"],
    }
    actual = {
        "base_config_sha256": digest(base), "trace_config_sha256": digest(trace_config),
        "overlay_sha256": digest(overlay), "runtime_sha256": digest(simulator),
        "trace_list_sha256": digest(trace),
    }
    if actual != expected:
        raise RuntimeError(f"identity preflight failed: expected={expected}; actual={actual}")
    root = Path(args.runs_root)
    attempt = str(uuid.uuid4())
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", authority["workload"])
    run_dir = root / f"{args.stage.lower()}_{authority['ordinal']}_{safe}_{attempt}"
    if run_dir.exists():
        raise RuntimeError(f"refusing to reuse attempt directory {run_dir}")
    run_dir.mkdir(parents=True)
    immutable_runner = run_dir / "immutable_tc80_campaign.py"
    shutil.copy2(Path(__file__), immutable_runner)
    immutable_runner.chmod(0o555)
    runner_sha = digest(immutable_runner)
    manifest = {
        "runner_schema": "TC80_IMMUTABLE_ATTEMPT_V1", "attempt_uuid": attempt,
        "stage": args.stage, "workload": authority["workload"], "ordinal": authority["ordinal"],
        "immutable_runner_path": str(immutable_runner), "runner_sha256": runner_sha,
        "simulator": str(simulator), "simulator_sha256": actual["runtime_sha256"],
        "core_source_head": authority["run_core_sha"], "base_config": str(base),
        "base_config_sha256": actual["base_config_sha256"], "overlay_config": str(overlay),
        "overlay_config_sha256": actual["overlay_sha256"], "trace_config": str(trace_config),
        "trace_config_sha256": actual["trace_config_sha256"], "trace_list": str(trace),
        "trace_list_sha256": actual["trace_list_sha256"], "trace_member_count": authority["trace_member_count"],
        "trace_total_bytes": authority["trace_total_bytes"],
        "trace_member_manifest_sha256": authority["trace_member_manifest_sha256"],
        "expected_instructions": authority["instructions"], "geometry": profile["geometry"],
        "effective_pib": "8", "effective_mshr": "32", "launch_utc": utc_now(),
    }
    kv_write(run_dir / "RUN_MANIFEST.tsv", manifest)
    kv_write(run_dir / "RUN_START.tsv", manifest)
    command = [str(simulator), "-trace", str(trace), "-config", str(base), "-config", str(overlay), "-config", str(trace_config)]
    with (run_dir / "simulator.stdout").open("wb") as stdout, (run_dir / "simulator.stderr").open("wb") as stderr:
        status = subprocess.run(command, cwd=run_dir, stdout=stdout, stderr=stderr, check=False).returncode
    terminal = {"attempt_uuid": attempt, "terminal_utc": utc_now(), "simulator_exit_status": status,
                "stdout_sha256": digest(run_dir / "simulator.stdout"), "stderr_sha256": digest(run_dir / "simulator.stderr")}
    kv_write(run_dir / "RUN_TERMINAL.tsv", terminal)
    with (run_dir / "RUN_MANIFEST.tsv").open("a", encoding="utf-8") as stream:
        for key, value in terminal.items():
            stream.write(f"{key}\t{value}\n")
    print(run_dir)


def final_metric(output: str, name: str) -> int:
    values = re.findall(rf"^{re.escape(name)}\s*=\s*(\d+)\s*$", output, re.MULTILINE)
    if not values:
        raise RuntimeError(f"missing metric {name}")
    return int(values[-1])


def final_dtc_metric(output: str, name: str) -> int:
    values = re.findall(rf"^{re.escape(name)}\s*=\s*(\d+)\s*$", output, re.MULTILINE)
    if not values:
        raise RuntimeError(f"missing terminal DTC metric {name}")
    return int(values[-1])


def validate_tc80(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir)
    profile = GEOMETRY_PROFILES[args.geometry_profile]
    manifest = kv_read(run_dir / "RUN_MANIFEST.tsv")
    terminal = kv_read(run_dir / "RUN_TERMINAL.tsv")
    authority = authority_row(Path(args.authority), args.workload)
    stdout = (run_dir / "simulator.stdout").read_text(encoding="utf-8", errors="replace")
    stderr = (run_dir / "simulator.stderr").read_text(encoding="utf-8", errors="replace")
    checks: dict[str, bool] = {}
    expected_binding = STAGE_BINDINGS.get(manifest.get("stage", ""))
    checks["stage_profile_binding"] = (
        expected_binding is not None and args.geometry_profile == expected_binding[0] and
        manifest.get("geometry") == GEOMETRY_PROFILES[expected_binding[0]]["geometry"]
    )
    checks["stage_overlay_binding"] = (
        expected_binding is not None and args.overlay_sha256 == expected_binding[1] and
        manifest.get("overlay_config_sha256") == expected_binding[1]
    )
    checks["workload_identity"] = manifest.get("workload") == authority["workload"]
    checks["attempt_unique"] = bool(manifest.get("attempt_uuid")) and manifest.get("attempt_uuid") == terminal.get("attempt_uuid")
    checks["natural_exit"] = terminal.get("simulator_exit_status") == "0"
    checks["runtime_identity"] = manifest.get("simulator_sha256") == authority["runtime_sha256"]
    checks["core_identity"] = manifest.get("core_source_head") == authority["run_core_sha"]
    checks["trace_identity"] = manifest.get("trace_list_sha256") == authority["trace_list_sha256"]
    checks["base_config_identity"] = manifest.get("base_config_sha256") == EXPECTED_BASE_CONFIG_SHA
    checks["trace_config_identity"] = manifest.get("trace_config_sha256") == EXPECTED_TRACE_CONFIG_SHA
    checks["overlay_identity"] = manifest.get("overlay_config_sha256") == args.overlay_sha256
    checks["geometry_manifest"] = manifest.get("geometry") == profile["geometry"]
    checks["dl1_geometry_echo"] = bool(re.search(rf"^-gpgpu_cache:dl1\s+{re.escape(profile['dl1'])}\s+#", stdout, re.MULTILINE))
    checks["dl1_prefl1_geometry_echo"] = bool(re.search(rf"^-gpgpu_cache:dl1PrefL1\s+{re.escape(profile['dl1'])}\s+#", stdout, re.MULTILINE))
    checks["dl1_prefshared_geometry_echo"] = bool(re.search(rf"^-gpgpu_cache:dl1PrefShared\s+{re.escape(profile['dl1'])}\s+#", stdout, re.MULTILINE))
    checks["unified_capacity_echo"] = bool(re.search(r"^-gpgpu_unified_l1d_size\s+80\s+#", stdout, re.MULTILINE))
    checks["base_mode_echo"] = bool(re.search(r"^-gpgpu_dtc_l1_mode\s+1\s+#", stdout, re.MULTILINE)) and "DTC_L1_mode = PAPER_BASE" in stdout
    checks["pib_echo"] = bool(re.search(r"^-gpgpu_dtc_l1_pib_entries\s+8\s+#", stdout, re.MULTILINE))
    checks["mshr_echo"] = bool(re.search(r"^-gpgpu_dtc_l1_mshr_entries\s+32\s+#", stdout, re.MULTILINE))
    checks["l1_latency_echo"] = bool(re.search(r"^-gpgpu_l1_latency\s+20\s+#", stdout, re.MULTILINE))
    checks["no_io_oo_mode"] = "DTC_L1_mode = PAPER_IO" not in stdout and "DTC_L1_mode = PAPER_OO" not in stdout
    scans = re.compile(r"assertion failed|fatal error|deadlock detected|segmentation fault|core dumped|cannot open config|trace.*(?:error|fail)|output mismatch", re.IGNORECASE)
    checks["error_scan"] = not bool(scans.search(stdout + "\n" + stderr))
    cycles = instructions = None
    pib_admits = pib_retires = pib_occupancy = None
    try:
        cycles = final_metric(stdout, "gpu_tot_sim_cycle")
        instructions = final_metric(stdout, "gpu_tot_sim_insn")
        pib_admits = final_dtc_metric(stdout, "DTC_L1_pib_admits")
        pib_retires = final_dtc_metric(stdout, "DTC_L1_pib_retires")
        pib_occupancy = final_dtc_metric(stdout, "DTC_L1_pib_occupancy")
        checks["instruction_identity"] = instructions == int(authority["instructions"])
        checks["terminal_pib_closed"] = pib_admits == pib_retires and pib_occupancy == 0
    except RuntimeError:
        checks["instruction_identity"] = False
        checks["terminal_pib_closed"] = False
    passed = all(checks.values())
    result = {
        "schema": "TC80_STRICT_VALIDATION_V1", "workload": args.workload, "run_dir": str(run_dir),
        "status": "PASS" if passed else "FAIL", "checks": checks, "cycles": cycles,
        "instructions": instructions, "pib_admits": pib_admits, "pib_retires": pib_retires,
        "pib_occupancy": pib_occupancy, "validation_utc": utc_now(),
    }
    output = Path(args.output) if args.output else run_dir / "VALIDATION.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    if not passed:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare-authority")
    p.add_argument("--summary", required=True)
    p.add_argument("--raw-index", required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(handler=prepare_authority)
    p = commands.add_parser("run")
    p.add_argument("--authority", required=True)
    p.add_argument("--workload", required=True)
    p.add_argument("--stage", choices=("CM2", "CM3", "CM5"), required=True)
    p.add_argument("--runs-root", required=True)
    p.add_argument("--base-config", required=True)
    p.add_argument("--overlay", required=True)
    p.add_argument("--overlay-sha256", required=True)
    p.add_argument("--trace-config", required=True)
    p.add_argument("--geometry-profile", choices=sorted(GEOMETRY_PROFILES), default="TC80_S32_W20")
    p.set_defaults(handler=run_tc80)
    p = commands.add_parser("resolve-config")
    p.add_argument("--base-config", required=True)
    p.add_argument("--overlay", required=True)
    p.add_argument("--trace-config", required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(handler=resolve_config)
    p = commands.add_parser("validate")
    p.add_argument("--authority", required=True)
    p.add_argument("--workload", required=True)
    p.add_argument("--run-dir", required=True)
    p.add_argument("--overlay-sha256", required=True)
    p.add_argument("--geometry-profile", choices=sorted(GEOMETRY_PROFILES), default="TC80_S32_W20")
    p.add_argument("--output")
    p.set_defaults(handler=validate_tc80)
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
