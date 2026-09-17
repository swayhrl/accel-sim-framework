#!/usr/bin/env python3
"""Fail-closed immutable-attempt controller for the SG4A logical-Tag sweep.

The controller deliberately knows only the predeclared four capacities and
two DTC modes.  It never reads existing sensitivity results and it refuses a
config, trace, or runtime whose identity was not recorded before a new row is
started.
"""
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


TRACE_CONFIG_SHA = "19dd14b3a4b6c1a1cb2833bd091f0dbd485ad79336ef7d4b0c9db1f7c46f504e"
POINTS = {
    (16, "IO"): ("configs/dtc_l1/fast64/FAST64_IO.config", "d4a2d9d0088946b950370b922a8d8e34422bbca9bac26f109b3977fe02a7f621", None, 32),
    (16, "OO"): ("configs/dtc_l1/fast64/FAST64_OO.config", "546c68f96d47f4650703ccfbc925bd789f923501d5607a77e79ca4845f234caa", None, 32),
    (32, "IO"): ("configs/dtc_l1/fast64/sensitivity_frozen_v2/logical_32/FAST64_SENS_LOGICAL_32KB_IO.config", "fc760923bdea08ce1b256b7944171042a33e74fbe8b5844e7fa582f9bd43d2e3", None, 64),
    (32, "OO"): ("configs/dtc_l1/fast64/sensitivity_frozen_v2/logical_32/FAST64_SENS_LOGICAL_32KB_OO.config", "cab21e03554de67271b7c7493c397ca2a30747f3d7fbc8ca6cc7d22bc5f3c399", None, 64),
    (64, "IO"): ("configs/dtc_l1/fast64/sensitivity_frozen_v2/logical_64/FAST64_SENS_LOGICAL_64KB_IO.config", "35b84094cf357a593606fc1f334d91317932caebd6d78084040cb9c0d9edb5aa", None, 128),
    (64, "OO"): ("configs/dtc_l1/fast64/sensitivity_frozen_v2/logical_64/FAST64_SENS_LOGICAL_64KB_OO.config", "313ff9096e3255735829cb45df28a432be38b1fd4161e381868e10da17fa144f", None, 128),
    (80, "IO"): ("configs/dtc_l1/fast64/FAST64_IO.config", "d4a2d9d0088946b950370b922a8d8e34422bbca9bac26f109b3977fe02a7f621", "docs/dtc_l1/iscas2027/granularity/sg4a/config/SG4A_LOGICAL80_IO_OVERLAY.config", 160),
    (80, "OO"): ("configs/dtc_l1/fast64/FAST64_OO.config", "546c68f96d47f4650703ccfbc925bd789f923501d5607a77e79ca4845f234caa", "docs/dtc_l1/iscas2027/granularity/sg4a/config/SG4A_LOGICAL80_OO_OVERLAY.config", 160),
}


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def row_for(authority, workload):
    hits = [row for row in rows(authority) if row["workload"] == workload]
    if len(hits) != 1:
        raise RuntimeError("workload is not an exact FAST12 authority member")
    return hits[0]


def write_kv(path, values):
    path.write_text("".join(f"{key}\t{value}\n" for key, value in values.items()), encoding="utf-8")


def read_kv(path):
    return dict(line.split("\t", 1) for line in path.read_text(encoding="utf-8").splitlines() if "\t" in line)


def require(path, expected, what):
    if not path.is_file() or sha(path) != expected:
        raise RuntimeError(f"{what} identity preflight failed: {path}")


def point_paths(repo, kib, mode):
    config_rel, config_sha, overlay_rel, sets = POINTS[(kib, mode)]
    config = (repo / config_rel).resolve()
    overlay = (repo / overlay_rel).resolve() if overlay_rel else None
    require(config, config_sha, "point config")
    if overlay and not overlay.is_file():
        raise RuntimeError(f"80-KiB overlay missing: {overlay}")
    return config, overlay, sets


def run(args):
    repo, authority = Path(args.repo).resolve(), Path(args.authority).resolve()
    point = (args.logical_kib, args.mode)
    if point not in POINTS:
        raise RuntimeError("only predeclared SG4A point/mode combinations are legal")
    source = row_for(authority, args.workload)
    config, overlay, sets = point_paths(repo, *point)
    trace = Path(source["trace_list"])
    trace_config = Path(args.trace_config).resolve()
    runtime = Path(args.simulator or source["runtime_path"])
    require(trace, source["trace_list_sha256"], "trace list")
    require(trace_config, TRACE_CONFIG_SHA, "trace config")
    if not runtime.is_file():
        raise RuntimeError(f"runtime identity preflight failed: {runtime}")
    attempt = str(uuid.uuid4())
    run_dir = Path(args.runs_root) / f"sg4a_logical{args.logical_kib}_{args.mode}_{args.workload}_{attempt}"
    if run_dir.exists():
        raise RuntimeError(f"refusing to reuse immutable attempt {run_dir}")
    run_dir.mkdir(parents=True)
    copied = run_dir / "immutable_sg4a_campaign.py"
    shutil.copy2(Path(__file__), copied)
    copied.chmod(0o555)
    chain = [config] + ([overlay] if overlay else []) + [trace_config]
    manifest = {
        "runner_schema": "SG4A_LOGICAL_TAG_IMMUTABLE_ATTEMPT_V1", "attempt_uuid": attempt,
        "lane": "SG4A", "stage": "SG4A.2", "workload": args.workload, "ordinal": source["ordinal"],
        "mode": args.mode, "logical_kib": args.logical_kib, "logical_sets": sets,
        "physical_pool_lines": 640, "physical_pool_bytes": 81920, "launch_utc": now(),
        "immutable_runner": str(copied), "runner_sha256": sha(copied), "simulator": str(runtime),
        "simulator_sha256": sha(runtime), "core_source_head": args.core_source_head or source["run_core_sha"],
        "config_chain": "|".join(map(str, chain)), "config_chain_sha256": "|".join(sha(item) for item in chain),
        "trace_list": str(trace), "trace_list_sha256": sha(trace),
        "trace_member_manifest_sha256": source["trace_member_manifest_sha256"], "expected_instructions": source["instructions"],
    }
    write_kv(run_dir / "RUN_MANIFEST.tsv", manifest)
    write_kv(run_dir / "RUN_START.tsv", manifest)
    command = [str(runtime), "-trace", str(trace)]
    for item in chain:
        command += ["-config", str(item)]
    with (run_dir / "simulator.stdout").open("wb") as stdout, (run_dir / "simulator.stderr").open("wb") as stderr:
        status = subprocess.run(command, cwd=run_dir, stdout=stdout, stderr=stderr, check=False).returncode
    terminal = {"attempt_uuid": attempt, "terminal_utc": now(), "simulator_exit_status": status,
                "stdout_sha256": sha(run_dir / "simulator.stdout"), "stderr_sha256": sha(run_dir / "simulator.stderr")}
    write_kv(run_dir / "RUN_TERMINAL.tsv", terminal)
    with (run_dir / "RUN_MANIFEST.tsv").open("a", encoding="utf-8") as stream:
        for key, value in terminal.items():
            stream.write(f"{key}\t{value}\n")
    print(run_dir)


def metric(output, name):
    values = re.findall(rf"^{re.escape(name)}\s*=\s*(\d+)\s*$", output, re.MULTILINE)
    if not values:
        raise RuntimeError(f"missing terminal metric {name}")
    return int(values[-1])


def validate(args):
    authority = Path(args.authority)
    source = row_for(authority, args.workload)
    run_dir = Path(args.run_dir)
    manifest, terminal = read_kv(run_dir / "RUN_MANIFEST.tsv"), read_kv(run_dir / "RUN_TERMINAL.tsv")
    output = (run_dir / "simulator.stdout").read_text(encoding="utf-8", errors="replace")
    errors = (run_dir / "simulator.stderr").read_text(encoding="utf-8", errors="replace")
    sets = POINTS[(args.logical_kib, args.mode)][3]
    prefix = "io" if args.mode == "IO" else "oo"
    required = [f"DTC_L1_{prefix}_lower_created", f"DTC_L1_{prefix}_lower_responses",
                f"DTC_L1_{prefix}_pending_hits", f"DTC_L1_{prefix}_tag_evictions",
                "DTC_L1_lower_credit_acquired", "DTC_L1_lower_credit_released", "DTC_L1_lower_outstanding"]
    if args.mode == "IO":
        required += ["DTC_L1_io_duplicate_after_eviction", "DTC_L1_io_pending_tag_evictions", "DTC_L1_io_physical_allocations"]
    checks = {
        "uuid": manifest.get("attempt_uuid") == terminal.get("attempt_uuid") and bool(manifest.get("attempt_uuid")),
        "natural_exit": terminal.get("simulator_exit_status") == "0", "workload": manifest.get("workload") == args.workload,
        "mode": manifest.get("mode") == args.mode, "logical_kib": manifest.get("logical_kib") == str(args.logical_kib),
        "trace": manifest.get("trace_list_sha256") == source["trace_list_sha256"],
        "logical_sets_echo": bool(re.search(rf"^-gpgpu_dtc_l1_logical_sets\s+{sets}\s+#", output, re.MULTILINE)),
        "physical_lines_echo": bool(re.search(r"^-gpgpu_dtc_l1_physical_lines\s+640\s+#", output, re.MULTILINE)),
        "mode_echo": bool(re.search(rf"^-gpgpu_dtc_l1_mode\s+{2 if args.mode == 'IO' else 3}\s+#", output, re.MULTILINE)),
        "error_scan": not bool(re.search(r"assertion failed|fatal error|deadlock detected|segmentation fault|core dumped|cannot open config", output + "\n" + errors, re.I)),
    }
    values = {}
    try:
        for name in ["gpu_tot_sim_cycle", "gpu_tot_sim_insn"] + required:
            values[name] = metric(output, name)
        checks["instruction_identity"] = values["gpu_tot_sim_insn"] == int(source["instructions"])
        checks["lower_drained"] = values[f"DTC_L1_{prefix}_lower_created"] == values[f"DTC_L1_{prefix}_lower_responses"]
        checks["credit_drained"] = values["DTC_L1_lower_credit_acquired"] == values["DTC_L1_lower_credit_released"] and values["DTC_L1_lower_outstanding"] == 0
    except RuntimeError:
        checks["instruction_identity"] = checks["lower_drained"] = checks["credit_drained"] = False
    result = {"schema": "SG4A_LOGICAL_TAG_STRICT_VALIDATION_V1", "status": "PASS" if all(checks.values()) else "FAIL",
              "workload": args.workload, "mode": args.mode, "logical_kib": args.logical_kib, "run_dir": str(run_dir),
              "cycles": values.get("gpu_tot_sim_cycle"), "instructions": values.get("gpu_tot_sim_insn"), "metrics": values, "checks": checks, "validation_utc": now()}
    target = Path(args.output) if args.output else run_dir / "VALIDATION.json"
    target.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("run", "validate"):
        item = commands.add_parser(command)
        item.add_argument("--authority", required=True)
        item.add_argument("--workload", required=True)
        item.add_argument("--mode", choices=("IO", "OO"), required=True)
        item.add_argument("--logical-kib", type=int, choices=(16, 32, 64, 80), required=True)
        if command == "run":
            item.add_argument("--repo", required=True); item.add_argument("--runs-root", required=True)
            item.add_argument("--trace-config", required=True); item.add_argument("--simulator"); item.add_argument("--core-source-head")
            item.set_defaults(handler=run)
        else:
            item.add_argument("--run-dir", required=True); item.add_argument("--output"); item.set_defaults(handler=validate)
    args = parser.parse_args(); args.handler(args)


if __name__ == "__main__":
    main()
