#!/usr/bin/env python3
"""Immutable SG5 OFF/ON equivalence attempts and strict comparison."""
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


def stamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def config_chain_digest(configs: tuple[Path, ...]) -> str:
    """Bind both order and bytes of a simulator -config chain."""
    h = hashlib.sha256()
    for config in configs:
        h.update(str(config).encode("utf-8"))
        h.update(b"\0")
        h.update(digest(config).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def kv(path: Path) -> dict[str, str]:
    return dict(line.split("\t", 1) for line in path.read_text().splitlines() if "\t" in line)


def write(path: Path, data: dict[str, object]) -> None:
    path.write_text("".join(f"{k}\t{v}\n" for k, v in data.items()))


def authority_row(path: Path, workload: str) -> dict[str, str]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = [row for row in csv.DictReader(stream, delimiter="\t")
                if row["workload"] == workload]
    if len(rows) != 1:
        raise RuntimeError(f"authority must contain exactly one {workload} row")
    return rows[0]


def run(args: argparse.Namespace) -> None:
    simulator, trace, trace_config = map(lambda p: Path(p).resolve(),
                                         (args.simulator, args.trace, args.trace_config))
    allowed_workloads = {"NN", "Btree"} if args.stage == "SG5.3" else {
        "ATAX", "BICG", "GESUMMV", "Btree", "2DConvolution", "Gaussian"}
    allowed_variants = {"B16-S", "TC80-S", "B16-N", "TC80-N", "IO", "OO"}
    if args.workload not in allowed_workloads or args.variant not in allowed_variants:
        raise RuntimeError("workload/variant is outside the predeclared SG5 stage matrix")
    source = authority_row(Path(args.authority), args.workload)
    if digest(trace) != source["trace_list_sha256"]:
        raise RuntimeError("trace identity does not match the frozen FAST12 authority")
    configs = tuple(Path(p).resolve() for p in args.config)
    for item in (simulator, *configs, trace, trace_config):
        if not item.is_file():
            raise RuntimeError(f"required input missing: {item}")
    enabled = int(args.observer) == 1
    root = Path(args.runs_root).resolve()
    attempt = str(uuid.uuid4())
    prefix = "sg5_g6_observer" if args.stage == "SG5.4" else "sg5_equivalence"
    out = root / f"{prefix}_{args.variant}_{args.workload}_{'ON' if enabled else 'OFF'}_{attempt}"
    out.mkdir(parents=True, exist_ok=False)
    overlay = out / "sg5_observer_overlay.config"
    overlay.write_text(f"-gpgpu_l1_lower_traffic_observer {int(enabled)}\n")
    runner = out / ("immutable_sg5_g6_observer.py" if args.stage == "SG5.4"
                    else "immutable_sg5_equivalence.py")
    shutil.copy2(Path(__file__), runner)
    runner.chmod(0o555)
    manifest = {"schema": "SG5_G6_OBSERVER_ATTEMPT_V1" if args.stage == "SG5.4"
                          else "SG5_EQUIVALENCE_ATTEMPT_V1", "attempt_uuid": attempt,
                "lane": "SG5", "stage": args.stage, "workload": args.workload,
                "variant": args.variant, "observer": int(enabled), "launch_utc": stamp(),
                "core_source_head": args.core_source_head,
                "simulator": simulator, "simulator_sha256": digest(simulator),
                # Keep the original single-config fields for existing evidence,
                # and bind every ordered config when an overlay is required.
                "config": configs[0], "config_sha256": digest(configs[0]),
                "config_chain": ";".join(map(str, configs)),
                "config_chain_sha256": config_chain_digest(configs), "trace": trace,
                "trace_sha256": digest(trace), "authority": Path(args.authority).resolve(),
                "authority_trace_sha256": source["trace_list_sha256"],
                "expected_instructions": source["instructions"], "trace_config": trace_config,
                "trace_config_sha256": digest(trace_config), "overlay": overlay,
                "overlay_sha256": digest(overlay), "immutable_runner": runner,
                "immutable_runner_sha256": digest(runner)}
    write(out / "RUN_MANIFEST.tsv", manifest)
    write(out / "RUN_START.tsv", manifest)
    with (out / "simulator.stdout").open("wb") as stdout, (out / "simulator.stderr").open("wb") as stderr:
        command = [str(simulator), "-trace", str(trace)]
        for config in configs:
            command.extend(("-config", str(config)))
        command.extend(("-config", str(trace_config), "-config", str(overlay)))
        status = subprocess.run(command, cwd=out,
                                stdout=stdout, stderr=stderr, check=False).returncode
    terminal = {"attempt_uuid": attempt, "terminal_utc": stamp(), "simulator_exit_status": status,
                "stdout_sha256": digest(out / "simulator.stdout"),
                "stderr_sha256": digest(out / "simulator.stderr")}
    write(out / "RUN_TERMINAL.tsv", terminal)
    with (out / "RUN_MANIFEST.tsv").open("a") as f:
        for key, value in terminal.items(): f.write(f"{key}\t{value}\n")
    print(out)


NON_SCIENTIFIC_STDOUT_FIELDS = {
    # Host-wallclock formatting, an uninitialised diagnostic pointer, and a
    # NaN/Inf report are not simulator scientific counters. They vary even in
    # an unchanged run and cannot be used to assess an observer-only change.
    "Bank_Level_Parallism_Col", "gpgpu_silicon_slowdown", "gpu_total_sim_rate",
    "gpgpu_simulation_rate", "gpgpu_simulation_time", "n_ref",
}


def metrics(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return {name: value for name, value in re.findall(r"^([A-Za-z][A-Za-z0-9_]*)\s*=\s*([^\n]+)$", text, re.M)
            if not name.startswith("SG5_") and name not in NON_SCIENTIFIC_STDOUT_FIELDS}


def validate(args: argparse.Namespace) -> None:
    off, on = Path(args.off_dir), Path(args.on_dir)
    om, nm = kv(off / "RUN_MANIFEST.tsv"), kv(on / "RUN_MANIFEST.tsv")
    ot, nt = kv(off / "RUN_TERMINAL.tsv"), kv(on / "RUN_TERMINAL.tsv")
    out_off, out_on = (off / "simulator.stdout").read_text(errors="replace"), (on / "simulator.stdout").read_text(errors="replace")
    a, b = metrics(off / "simulator.stdout"), metrics(on / "simulator.stdout")
    identity = ("workload", "variant", "simulator_sha256", "trace_sha256", "authority_trace_sha256", "trace_config_sha256")
    config_identity = om.get("config_chain_sha256", om.get("config_sha256")) == \
                      nm.get("config_chain_sha256", nm.get("config_sha256"))
    normal = {
        "B16-N": "N:32:128:4,L:T:m:L:L,A:512:8,16:0,32",
        "TC80-N": "N:32:128:20,L:T:m:L:L,A:512:8,16:0,32",
    }
    normal_checks = {}
    if args.normal_variant:
        expected = normal[args.normal_variant]
        for prefix, text in (("off", out_off), ("on", out_on)):
            normal_checks[f"{prefix}_normal_dl1_echo"] = all(
                re.search(rf"^-gpgpu_cache:{name}\s+{re.escape(expected)}\s+#", text, re.M)
                for name in ("dl1", "dl1PrefL1", "dl1PrefShared"))
            normal_checks[f"{prefix}_paper_base_mode"] = bool(
                re.search(r"^-gpgpu_dtc_l1_mode\s+1\s+#", text, re.M)) and \
                "DTC_L1_mode = PAPER_BASE" in text
            normal_checks[f"{prefix}_pib_mshr_identity"] = bool(
                re.search(r"^-gpgpu_dtc_l1_pib_entries\s+8\s+#", text, re.M)) and bool(
                re.search(r"^-gpgpu_dtc_l1_mshr_entries\s+32\s+#", text, re.M))
        if args.normal_variant == "TC80-N":
            normal_checks["off_unified_capacity_echo"] = bool(
                re.search(r"^-gpgpu_unified_l1d_size\s+80\s+#", out_off, re.M))
            normal_checks["on_unified_capacity_echo"] = bool(
                re.search(r"^-gpgpu_unified_l1d_size\s+80\s+#", out_on, re.M))
    checks = {"off_natural_exit": ot.get("simulator_exit_status") == "0",
              "on_natural_exit": nt.get("simulator_exit_status") == "0",
              "off_identity": om.get("observer") == "0", "on_identity": nm.get("observer") == "1",
              "common_identity": all(om.get(k) == nm.get(k) for k in identity) and config_identity,
              "off_has_no_sg5": "SG5_l1_lower_traffic_observer" not in out_off,
              "on_has_sg5": "SG5_l1_lower_traffic_observer = 1" in out_on,
              "metric_keyset": set(a) == set(b), "metric_values": a == b,
              "cycles_present": "gpu_tot_sim_cycle" in a,
              "instructions_present": "gpu_tot_sim_insn" in a,
              "authority_instruction_identity": a.get("gpu_tot_sim_insn") == om.get("expected_instructions") and
                                              b.get("gpu_tot_sim_insn") == nm.get("expected_instructions")}
    if args.expected_core_source_head:
        checks["core_source_identity"] = om.get("core_source_head") == args.expected_core_source_head and \
                                         nm.get("core_source_head") == args.expected_core_source_head
    if args.expected_config_chain_sha256:
        checks["config_chain_identity"] = om.get("config_chain_sha256") == args.expected_config_chain_sha256 and \
                                          nm.get("config_chain_sha256") == args.expected_config_chain_sha256
    checks.update(normal_checks)
    result = {"schema": "SG5_EQUIVALENCE_VALIDATION_V1", "status": "PASS" if all(checks.values()) else "FAIL",
              "off_dir": str(off), "on_dir": str(on), "cycles": a.get("gpu_tot_sim_cycle"),
              "instructions": a.get("gpu_tot_sim_insn"), "checked_metric_count": len(a), "checks": checks,
              "validation_utc": stamp()}
    target = Path(args.output) if args.output else on / "SG5_EQUIVALENCE_VALIDATION.json"
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS": raise SystemExit(1)


def validate_run(args: argparse.Namespace) -> None:
    """Fail closed for one diagnostic SG5.4 observer attempt.

    SG5.4 rows intentionally have no OFF peer: they are diagnostic telemetry
    samples, not an observer-equivalence test.  This validator therefore
    checks immutable input identity, natural termination, and that the
    complete source-defined observer report was emitted.  It does not infer
    any performance result from the counters.
    """
    run_dir = Path(args.run_dir)
    manifest, terminal = kv(run_dir / "RUN_MANIFEST.tsv"), kv(run_dir / "RUN_TERMINAL.tsv")
    stdout = (run_dir / "simulator.stdout").read_text(encoding="utf-8", errors="replace")
    reported = set(re.findall(r"^(SG5_[A-Za-z0-9_]+)\s*=", stdout, re.M))
    required = {
        "SG5_l1_lower_traffic_observer",
        "SG5_conventional_lower_read_transactions",
        "SG5_conventional_lower_read_payload_bytes",
        "SG5_dtc_io_lower_transactions",
        "SG5_dtc_io_lower_payload_bytes",
        "SG5_dtc_oo_lower_transactions",
        "SG5_dtc_oo_lower_payload_bytes",
        "SG5_dtc_sector_lower_transactions",
        "SG5_dtc_sector_lower_payload_bytes",
    }
    checks = {
        "stage_identity": manifest.get("stage") == "SG5.4",
        "natural_exit": terminal.get("simulator_exit_status") == "0",
        "observer_enabled": manifest.get("observer") == "1" and
                            "SG5_l1_lower_traffic_observer = 1" in stdout,
        "all_observer_counters_reported": required <= reported,
        "cycles_present": bool(re.search(r"^gpu_tot_sim_cycle\s*=", stdout, re.M)),
        "instructions_present": bool(re.search(r"^gpu_tot_sim_insn\s*=", stdout, re.M)),
    }
    if args.expected_core_source_head:
        checks["core_source_identity"] = manifest.get("core_source_head") == args.expected_core_source_head
    if args.expected_config_chain_sha256:
        checks["config_chain_identity"] = manifest.get("config_chain_sha256") == args.expected_config_chain_sha256
    result = {
        "schema": "SG5_G6_OBSERVER_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "run_dir": str(run_dir), "checks": checks,
        "reported_observer_counters": sorted(reported), "validation_utc": stamp(),
    }
    target = Path(args.output) if args.output else run_dir / "SG5_G6_VALIDATION.json"
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS": raise SystemExit(1)


parser = argparse.ArgumentParser()
subs = parser.add_subparsers(dest="command", required=True)
p = subs.add_parser("run")
for name in ("simulator", "config", "trace", "trace_config", "runs_root", "workload", "variant"):
    p.add_argument(f"--{name.replace('_', '-')}", required=True,
                   action="append" if name == "config" else None)
p.add_argument("--authority", required=True)
p.add_argument("--observer", choices=("0", "1"), required=True)
p.add_argument("--core-source-head", required=True)
p.add_argument("--stage", choices=("SG5.3", "SG5.4"), default="SG5.3")
p.set_defaults(func=run)
p = subs.add_parser("validate"); p.add_argument("--off-dir", required=True); p.add_argument("--on-dir", required=True); p.add_argument("--output")
p.add_argument("--expected-core-source-head"); p.add_argument("--expected-config-chain-sha256")
p.add_argument("--normal-variant", choices=("B16-N", "TC80-N")); p.set_defaults(func=validate)
p = subs.add_parser("validate-run"); p.add_argument("--run-dir", required=True); p.add_argument("--output")
p.add_argument("--expected-core-source-head"); p.add_argument("--expected-config-chain-sha256")
p.set_defaults(func=validate_run)
args = parser.parse_args(); args.func(args)
