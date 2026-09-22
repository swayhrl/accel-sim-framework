#!/usr/bin/env python3
"""Immutable-attempt runner and strict validator for SG1 same-Core controls."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path


BASE_SHA = "1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde"
TRACE_SHA = "19dd14b3a4b6c1a1cb2833bd091f0dbd485ad79336ef7d4b0c9db1f7c46f504e"
VARIANTS = {
    "B16-S": {
        "overlay_sha256": None,
        "dl1": "S:32:128:4,L:T:m:L:L,A:512:8,16:0,32",
        "geometry": "32x4x128=128_lines=16384_bytes",
        "unified_l1d_size": None,
    },
    "TC80-S": {
        "overlay_sha256": "92496d3664f24539df8ec4d17fe717b526a8eb5a1a391ef4a2db86e9a3ba44f4",
        "dl1": "S:32:128:20,L:T:m:L:L,A:512:8,16:0,32",
        "geometry": "32x20x128=640_lines=81920_bytes",
        "unified_l1d_size": "80",
    },
    "B16-N": {
        "overlay_sha256": "658a13634cfc4a05e03437ed9b9a3922f9a91c2fce5d16c7b37784cfb38ccda8",
        "dl1": "N:32:128:4,L:T:m:L:L,A:512:8,16:0,32",
        "geometry": "32x4x128=128_lines=16384_bytes",
        "unified_l1d_size": None,
    },
    "TC80-N": {
        "overlay_sha256": "423832831f7d45757fcca350886dcf7a26cdd0158604a3b7c883638d006bbabd",
        "dl1": "N:32:128:20,L:T:m:L:L,A:512:8,16:0,32",
        "geometry": "32x20x128=640_lines=81920_bytes",
        "unified_l1d_size": "80",
    },
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def read_kv(path: Path) -> dict[str, str]:
    return {key: value for key, value in
            (line.split("\t", 1) for line in path.read_text(encoding="utf-8").splitlines()
             if "\t" in line)}


def write_kv(path: Path, values: dict[str, object]) -> None:
    path.write_text("".join(f"{key}\t{value}\n" for key, value in values.items()), encoding="utf-8")


def authority_row(path: Path, workload: str) -> dict[str, str]:
    rows = [row for row in read_tsv(path) if row["workload"] == workload]
    if len(rows) != 1:
        raise RuntimeError(f"authority must contain exactly one {workload} row")
    return rows[0]


def required_file(path: Path, expected_sha: str, label: str) -> None:
    if not path.is_file() or sha256(path) != expected_sha:
        raise RuntimeError(f"{label} identity preflight failed: {path}")


def run(args: argparse.Namespace) -> None:
    variant = VARIANTS[args.variant]
    authority = authority_row(Path(args.authority), args.workload)
    base, trace_config = Path(args.base_config).resolve(), Path(args.trace_config).resolve()
    overlay = Path(args.overlay).resolve() if args.overlay else None
    if bool(args.simulator) != bool(args.core_source_head):
        raise RuntimeError("a repaired SG1 runtime requires both --simulator and --core-source-head")
    runtime = Path(args.simulator) if args.simulator else Path(authority["runtime_path"])
    core_source_head = args.core_source_head or authority["run_core_sha"]
    trace = Path(authority["trace_list"])
    required_file(base, BASE_SHA, "base config")
    required_file(trace_config, TRACE_SHA, "trace config")
    if variant["overlay_sha256"] is None:
        if overlay is not None:
            raise RuntimeError("B16-S is bound to FAST64_BASE.config alone; no overlay is legal")
    else:
        if overlay is None:
            raise RuntimeError("this variant requires its frozen overlay")
        required_file(overlay, variant["overlay_sha256"], "variant overlay")
    if not runtime.is_file():
        raise RuntimeError(f"runtime identity preflight failed: {runtime}")
    required_file(trace, authority["trace_list_sha256"], "trace list")

    attempt_uuid = str(uuid.uuid4())
    root = Path(args.runs_root)
    safe_workload = re.sub(r"[^A-Za-z0-9._-]+", "_", args.workload)
    run_dir = root / f"sg1_{args.stage.lower()}_{args.variant}_{safe_workload}_{attempt_uuid}"
    if run_dir.exists():
        raise RuntimeError(f"refusing to reuse immutable attempt {run_dir}")
    run_dir.mkdir(parents=True)
    immutable_runner = run_dir / "immutable_sg1_campaign.py"
    shutil.copy2(Path(__file__), immutable_runner)
    immutable_runner.chmod(0o555)
    manifest = {
        "runner_schema": "SG1_NORMAL_IMMUTABLE_ATTEMPT_V1",
        "attempt_uuid": attempt_uuid,
        "lane": "SG1",
        "stage": args.stage,
        "variant": args.variant,
        "workload": args.workload,
        "ordinal": authority["ordinal"],
        "launch_utc": now(),
        "immutable_runner_path": str(immutable_runner),
        "runner_sha256": sha256(immutable_runner),
        "simulator": str(runtime),
        "simulator_sha256": sha256(runtime),
        "core_source_head": core_source_head,
        "base_config": str(base),
        "base_config_sha256": sha256(base),
        "overlay_config": str(overlay) if overlay else "NONE",
        "overlay_config_sha256": sha256(overlay) if overlay else "NONE",
        "trace_config": str(trace_config),
        "trace_config_sha256": sha256(trace_config),
        "trace_list": str(trace),
        "trace_list_sha256": sha256(trace),
        "trace_member_manifest_sha256": authority["trace_member_manifest_sha256"],
        "expected_instructions": authority["instructions"],
        "normal_cache_geometry": variant["geometry"],
        "effective_pib": "8",
        "effective_mshr": "32",
    }
    write_kv(run_dir / "RUN_MANIFEST.tsv", manifest)
    write_kv(run_dir / "RUN_START.tsv", manifest)
    command = [str(runtime), "-trace", str(trace), "-config", str(base)]
    if overlay:
        command += ["-config", str(overlay)]
    command += ["-config", str(trace_config)]
    with (run_dir / "simulator.stdout").open("wb") as stdout, \
         (run_dir / "simulator.stderr").open("wb") as stderr:
        status = subprocess.run(command, cwd=run_dir, stdout=stdout, stderr=stderr,
                                check=False).returncode
    terminal = {"attempt_uuid": attempt_uuid, "terminal_utc": now(),
                "simulator_exit_status": status,
                "stdout_sha256": sha256(run_dir / "simulator.stdout"),
                "stderr_sha256": sha256(run_dir / "simulator.stderr")}
    write_kv(run_dir / "RUN_TERMINAL.tsv", terminal)
    with (run_dir / "RUN_MANIFEST.tsv").open("a", encoding="utf-8") as stream:
        for key, value in terminal.items():
            stream.write(f"{key}\t{value}\n")
    print(run_dir)


def final_metric(output: str, name: str) -> int:
    values = re.findall(rf"^{re.escape(name)}\s*=\s*(\d+)\s*$", output, re.MULTILINE)
    if not values:
        raise RuntimeError(f"missing terminal metric {name}")
    return int(values[-1])


def validate(args: argparse.Namespace) -> None:
    variant = VARIANTS[args.variant]
    authority = authority_row(Path(args.authority), args.workload)
    run_dir = Path(args.run_dir)
    if bool(args.expected_runtime_sha) != bool(args.expected_core_source_head):
        raise RuntimeError("validation requires both repaired-runtime identity arguments or neither")
    expected_runtime_sha = args.expected_runtime_sha or authority["runtime_sha256"]
    expected_core_source_head = args.expected_core_source_head or authority["run_core_sha"]
    manifest, terminal = read_kv(run_dir / "RUN_MANIFEST.tsv"), read_kv(run_dir / "RUN_TERMINAL.tsv")
    stdout = (run_dir / "simulator.stdout").read_text(encoding="utf-8", errors="replace")
    stderr = (run_dir / "simulator.stderr").read_text(encoding="utf-8", errors="replace")
    checks = {
        "attempt_uuid": bool(manifest.get("attempt_uuid")) and manifest.get("attempt_uuid") == terminal.get("attempt_uuid"),
        "natural_exit": terminal.get("simulator_exit_status") == "0",
        "workload_identity": manifest.get("workload") == args.workload,
        "variant_identity": manifest.get("variant") == args.variant,
        "runtime_identity": manifest.get("simulator_sha256") == expected_runtime_sha,
        "core_identity": manifest.get("core_source_head") == expected_core_source_head,
        "trace_identity": manifest.get("trace_list_sha256") == authority["trace_list_sha256"],
        "base_config_identity": manifest.get("base_config_sha256") == BASE_SHA,
        "trace_config_identity": manifest.get("trace_config_sha256") == TRACE_SHA,
        "overlay_identity": manifest.get("overlay_config_sha256") == (variant["overlay_sha256"] or "NONE"),
        "normal_dl1_echo": all(re.search(rf"^-gpgpu_cache:{name}\s+{re.escape(variant['dl1'])}\s+#", stdout, re.MULTILINE)
                               for name in ("dl1", "dl1PrefL1", "dl1PrefShared")),
        "paper_base_mode": bool(re.search(r"^-gpgpu_dtc_l1_mode\s+1\s+#", stdout, re.MULTILINE)) and "DTC_L1_mode = PAPER_BASE" in stdout,
        "pib_identity": bool(re.search(r"^-gpgpu_dtc_l1_pib_entries\s+8\s+#", stdout, re.MULTILINE)),
        "mshr_identity": bool(re.search(r"^-gpgpu_dtc_l1_mshr_entries\s+32\s+#", stdout, re.MULTILINE)),
        "no_io_oo_mode": "DTC_L1_mode = PAPER_IO" not in stdout and "DTC_L1_mode = PAPER_OO" not in stdout,
        "error_scan": not bool(re.search(r"assertion failed|fatal error|deadlock detected|segmentation fault|core dumped|cannot open config|trace.*(?:error|fail)|output mismatch", stdout + "\n" + stderr, re.IGNORECASE)),
    }
    if variant["unified_l1d_size"] is not None:
        checks["unified_capacity_echo"] = bool(re.search(r"^-gpgpu_unified_l1d_size\s+80\s+#", stdout, re.MULTILINE))
    else:
        checks["unified_capacity_echo"] = True
    try:
        cycles = final_metric(stdout, "gpu_tot_sim_cycle")
        instructions = final_metric(stdout, "gpu_tot_sim_insn")
        admits = final_metric(stdout, "DTC_L1_pib_admits")
        retires = final_metric(stdout, "DTC_L1_pib_retires")
        occupancy = final_metric(stdout, "DTC_L1_pib_occupancy")
        checks["instruction_identity"] = instructions == int(authority["instructions"])
        checks["terminal_accounting"] = admits == retires and occupancy == 0
    except RuntimeError:
        cycles = instructions = admits = retires = occupancy = None
        checks["instruction_identity"] = False
        checks["terminal_accounting"] = False
    result = {"schema": "SG1_NORMAL_STRICT_VALIDATION_V1", "status": "PASS" if all(checks.values()) else "FAIL",
              "workload": args.workload, "variant": args.variant, "run_dir": str(run_dir),
              "cycles": cycles, "instructions": instructions, "pib_admits": admits,
              "pib_retires": retires, "pib_occupancy": occupancy, "checks": checks,
              "validation_utc": now()}
    output = Path(args.output) if args.output else run_dir / "VALIDATION.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("run", "validate"):
        item = commands.add_parser(command)
        item.add_argument("--authority", required=True)
        item.add_argument("--workload", required=True)
        item.add_argument("--variant", choices=sorted(VARIANTS), required=True)
        if command == "run":
            item.add_argument("--runs-root", required=True)
            item.add_argument("--base-config", required=True)
            item.add_argument("--overlay")
            item.add_argument("--trace-config", required=True)
            item.add_argument("--simulator")
            item.add_argument("--core-source-head")
            item.add_argument("--stage", choices=("SMOKE", "G6", "FAST12"), default="SMOKE",
                              help="immutable attempt classification; defaults to SMOKE")
            item.set_defaults(handler=run)
        else:
            item.add_argument("--run-dir", required=True)
            item.add_argument("--output")
            item.add_argument("--expected-runtime-sha")
            item.add_argument("--expected-core-source-head")
            item.set_defaults(handler=validate)
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
