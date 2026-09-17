#!/usr/bin/env python3
"""Immutable SG3 downstream-observer OFF/ON attempts and strict comparison."""
from __future__ import annotations

import argparse
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


def chain_digest(configs: tuple[Path, ...]) -> str:
    h = hashlib.sha256()
    for config in configs:
        h.update(str(config).encode("utf-8"))
        h.update(b"\0")
        h.update(digest(config).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def write_tsv(path: Path, data: dict[str, object]) -> None:
    path.write_text("".join(f"{key}\t{value}\n" for key, value in data.items()))


def read_tsv(path: Path) -> dict[str, str]:
    return dict(line.split("\t", 1) for line in path.read_text().splitlines() if "\t" in line)


def metrics(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    ignored = {
        "Bank_Level_Parallism_Col", "gpgpu_silicon_slowdown",
        "gpu_total_sim_rate", "gpgpu_simulation_rate", "gpgpu_simulation_time",
        "n_ref",
    }
    return {
        name: value for name, value in re.findall(
            r"^([A-Za-z][A-Za-z0-9_]*)\s*=\s*([^\n]+)$", text, re.M)
        if not name.startswith("SG3_") and name not in ignored
    }


def run(args: argparse.Namespace) -> None:
    simulator, trace, trace_config = map(Path.resolve,
                                         map(Path, (args.simulator, args.trace, args.trace_config)))
    configs = tuple(Path(item).resolve() for item in args.config)
    for item in (simulator, trace, trace_config, *configs):
        if not item.is_file():
            raise RuntimeError(f"required input missing: {item}")
    observer = int(args.observer)
    root = Path(args.runs_root).resolve()
    attempt_uuid = str(uuid.uuid4())
    out = root / f"sg3_equivalence_{args.mode}_{args.workload}_{'ON' if observer else 'OFF'}_{attempt_uuid}"
    out.mkdir(parents=True, exist_ok=False)
    overlay = out / "sg3_downstream_observer_overlay.config"
    overlay.write_text(f"-gpgpu_sg3_downstream_observer {observer}\n")
    immutable_runner = out / "immutable_sg3_observer_equivalence.py"
    shutil.copy2(Path(__file__), immutable_runner)
    immutable_runner.chmod(0o555)
    manifest = {
        "schema": "SG3_OBSERVER_EQUIVALENCE_ATTEMPT_V1",
        "attempt_uuid": attempt_uuid, "lane": "SG3", "stage": "SG3.1",
        "workload": args.workload, "mode": args.mode, "observer": observer,
        "launch_utc": stamp(), "core_source_head": args.core_source_head,
        "simulator": simulator, "simulator_sha256": digest(simulator),
        "config_chain": ";".join(map(str, configs)),
        "config_chain_sha256": chain_digest(configs),
        "trace": trace, "trace_sha256": digest(trace),
        "trace_config": trace_config, "trace_config_sha256": digest(trace_config),
        "overlay": overlay, "overlay_sha256": digest(overlay),
        "immutable_runner": immutable_runner,
        "immutable_runner_sha256": digest(immutable_runner),
    }
    write_tsv(out / "RUN_MANIFEST.tsv", manifest)
    write_tsv(out / "RUN_START.tsv", manifest)
    command = [str(simulator), "-trace", str(trace)]
    for config in configs:
        command.extend(("-config", str(config)))
    command.extend(("-config", str(trace_config), "-config", str(overlay)))
    with (out / "simulator.stdout").open("wb") as stdout, \
         (out / "simulator.stderr").open("wb") as stderr:
        status = subprocess.run(command, cwd=out, stdout=stdout, stderr=stderr,
                                check=False).returncode
    terminal = {"attempt_uuid": attempt_uuid, "terminal_utc": stamp(),
                "simulator_exit_status": status,
                "stdout_sha256": digest(out / "simulator.stdout"),
                "stderr_sha256": digest(out / "simulator.stderr")}
    write_tsv(out / "RUN_TERMINAL.tsv", terminal)
    with (out / "RUN_MANIFEST.tsv").open("a") as f:
        for key, value in terminal.items():
            f.write(f"{key}\t{value}\n")
    print(out)


def validate(args: argparse.Namespace) -> None:
    off, on = Path(args.off_dir), Path(args.on_dir)
    off_manifest, on_manifest = read_tsv(off / "RUN_MANIFEST.tsv"), read_tsv(on / "RUN_MANIFEST.tsv")
    off_terminal, on_terminal = read_tsv(off / "RUN_TERMINAL.tsv"), read_tsv(on / "RUN_TERMINAL.tsv")
    off_text = (off / "simulator.stdout").read_text(encoding="utf-8", errors="replace")
    on_text = (on / "simulator.stdout").read_text(encoding="utf-8", errors="replace")
    off_metrics, on_metrics = metrics(off / "simulator.stdout"), metrics(on / "simulator.stdout")
    identity_keys = ("workload", "mode", "simulator_sha256", "config_chain_sha256",
                     "trace_sha256", "trace_config_sha256", "core_source_head")
    required_on = {
        "SG3_downstream_observer", "SG3_dtc_core_tick_samples",
        "SG3_dtc_lower_outstanding_integral", "SG3_l2_bank_tick_samples",
        "SG3_l2_mshr_occupancy_integral", "SG3_l2_miss_queue_occupancy_integral",
        "SG3_lower_lifetime_completed", "SG3_lower_lifetime_sum_cycles",
        "SG3_lower_lifetime_max_cycles", "SG3_lower_lifetime_unmatched_completions",
        "SG3_lower_lifetime_live_records",
    }
    reported_on = set(re.findall(r"^(SG3_[A-Za-z0-9_]+)\s*=", on_text, re.M))
    checks = {
        "off_natural_exit": off_terminal.get("simulator_exit_status") == "0",
        "on_natural_exit": on_terminal.get("simulator_exit_status") == "0",
        "off_identity": off_manifest.get("observer") == "0",
        "on_identity": on_manifest.get("observer") == "1",
        "common_identity": all(off_manifest.get(key) == on_manifest.get(key)
                               for key in identity_keys),
        "off_has_no_sg3": "SG3_downstream_observer" not in off_text,
        "on_has_complete_sg3": required_on <= reported_on,
        "preexisting_metric_keyset": set(off_metrics) == set(on_metrics),
        "preexisting_metric_values": off_metrics == on_metrics,
        "cycles_present": "gpu_tot_sim_cycle" in off_metrics,
        "instructions_present": "gpu_tot_sim_insn" in off_metrics,
        "terminal_lifetime_closure": (
            re.search(r"^SG3_lower_lifetime_unmatched_completions = 0$", on_text, re.M) is not None and
            re.search(r"^SG3_lower_lifetime_live_records = 0$", on_text, re.M) is not None),
    }
    result = {
        "schema": "SG3_OBSERVER_EQUIVALENCE_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "off_dir": str(off), "on_dir": str(on),
        "cycles": off_metrics.get("gpu_tot_sim_cycle"),
        "instructions": off_metrics.get("gpu_tot_sim_insn"),
        "checked_preexisting_metric_count": len(off_metrics),
        "checks": checks, "validation_utc": stamp(),
    }
    target = Path(args.output) if args.output else on / "SG3_EQUIVALENCE_VALIDATION.json"
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command", required=True)
run_parser = subparsers.add_parser("run")
for name in ("simulator", "trace", "trace_config", "runs_root", "workload", "mode"):
    run_parser.add_argument(f"--{name.replace('_', '-')}", required=True)
run_parser.add_argument("--config", required=True, action="append")
run_parser.add_argument("--observer", choices=("0", "1"), required=True)
run_parser.add_argument("--core-source-head", required=True)
run_parser.set_defaults(func=run)
validate_parser = subparsers.add_parser("validate")
validate_parser.add_argument("--off-dir", required=True)
validate_parser.add_argument("--on-dir", required=True)
validate_parser.add_argument("--output")
validate_parser.set_defaults(func=validate)
arguments = parser.parse_args()
arguments.func(arguments)
