#!/usr/bin/env python3
"""Immutable SG5 OFF/ON equivalence attempts and strict comparison."""
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


def kv(path: Path) -> dict[str, str]:
    return dict(line.split("\t", 1) for line in path.read_text().splitlines() if "\t" in line)


def write(path: Path, data: dict[str, object]) -> None:
    path.write_text("".join(f"{k}\t{v}\n" for k, v in data.items()))


def run(args: argparse.Namespace) -> None:
    simulator, config, trace, trace_config = map(lambda p: Path(p).resolve(),
                                                   (args.simulator, args.config, args.trace, args.trace_config))
    for item in (simulator, config, trace, trace_config):
        if not item.is_file():
            raise RuntimeError(f"required input missing: {item}")
    enabled = int(args.observer) == 1
    root = Path(args.runs_root).resolve()
    attempt = str(uuid.uuid4())
    out = root / f"sg5_equivalence_{args.variant}_{args.workload}_{'ON' if enabled else 'OFF'}_{attempt}"
    out.mkdir(parents=True, exist_ok=False)
    overlay = out / "sg5_observer_overlay.config"
    overlay.write_text(f"-gpgpu_l1_lower_traffic_observer {int(enabled)}\n")
    runner = out / "immutable_sg5_equivalence.py"
    shutil.copy2(Path(__file__), runner)
    runner.chmod(0o555)
    manifest = {"schema": "SG5_EQUIVALENCE_ATTEMPT_V1", "attempt_uuid": attempt,
                "lane": "SG5", "stage": "SG5.3", "workload": args.workload,
                "variant": args.variant, "observer": int(enabled), "launch_utc": stamp(),
                "simulator": simulator, "simulator_sha256": digest(simulator),
                "config": config, "config_sha256": digest(config), "trace": trace,
                "trace_sha256": digest(trace), "trace_config": trace_config,
                "trace_config_sha256": digest(trace_config), "overlay": overlay,
                "overlay_sha256": digest(overlay), "immutable_runner": runner,
                "immutable_runner_sha256": digest(runner)}
    write(out / "RUN_MANIFEST.tsv", manifest)
    write(out / "RUN_START.tsv", manifest)
    with (out / "simulator.stdout").open("wb") as stdout, (out / "simulator.stderr").open("wb") as stderr:
        status = subprocess.run([str(simulator), "-trace", str(trace), "-config", str(config),
                                 "-config", str(trace_config), "-config", str(overlay)], cwd=out,
                                stdout=stdout, stderr=stderr, check=False).returncode
    terminal = {"attempt_uuid": attempt, "terminal_utc": stamp(), "simulator_exit_status": status,
                "stdout_sha256": digest(out / "simulator.stdout"),
                "stderr_sha256": digest(out / "simulator.stderr")}
    write(out / "RUN_TERMINAL.tsv", terminal)
    with (out / "RUN_MANIFEST.tsv").open("a") as f:
        for key, value in terminal.items(): f.write(f"{key}\t{value}\n")
    print(out)


def metrics(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return {name: value for name, value in re.findall(r"^([A-Za-z][A-Za-z0-9_]*)\s*=\s*([^\n]+)$", text, re.M)
            if not name.startswith("SG5_")}


def validate(args: argparse.Namespace) -> None:
    off, on = Path(args.off_dir), Path(args.on_dir)
    om, nm = kv(off / "RUN_MANIFEST.tsv"), kv(on / "RUN_MANIFEST.tsv")
    ot, nt = kv(off / "RUN_TERMINAL.tsv"), kv(on / "RUN_TERMINAL.tsv")
    out_off, out_on = (off / "simulator.stdout").read_text(errors="replace"), (on / "simulator.stdout").read_text(errors="replace")
    a, b = metrics(off / "simulator.stdout"), metrics(on / "simulator.stdout")
    identity = ("workload", "variant", "simulator_sha256", "config_sha256", "trace_sha256", "trace_config_sha256")
    checks = {"off_natural_exit": ot.get("simulator_exit_status") == "0",
              "on_natural_exit": nt.get("simulator_exit_status") == "0",
              "off_identity": om.get("observer") == "0", "on_identity": nm.get("observer") == "1",
              "common_identity": all(om.get(k) == nm.get(k) for k in identity),
              "off_has_no_sg5": "SG5_l1_lower_traffic_observer" not in out_off,
              "on_has_sg5": "SG5_l1_lower_traffic_observer = 1" in out_on,
              "metric_keyset": set(a) == set(b), "metric_values": a == b,
              "cycles_present": "gpu_tot_sim_cycle" in a,
              "instructions_present": "gpu_tot_sim_insn" in a}
    result = {"schema": "SG5_EQUIVALENCE_VALIDATION_V1", "status": "PASS" if all(checks.values()) else "FAIL",
              "off_dir": str(off), "on_dir": str(on), "cycles": a.get("gpu_tot_sim_cycle"),
              "instructions": a.get("gpu_tot_sim_insn"), "checked_metric_count": len(a), "checks": checks,
              "validation_utc": stamp()}
    target = Path(args.output) if args.output else on / "SG5_EQUIVALENCE_VALIDATION.json"
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS": raise SystemExit(1)


parser = argparse.ArgumentParser()
subs = parser.add_subparsers(dest="command", required=True)
p = subs.add_parser("run")
for name in ("simulator", "config", "trace", "trace_config", "runs_root", "workload", "variant"):
    p.add_argument(f"--{name.replace('_', '-')}", required=True)
p.add_argument("--observer", choices=("0", "1"), required=True); p.set_defaults(func=run)
p = subs.add_parser("validate"); p.add_argument("--off-dir", required=True); p.add_argument("--on-dir", required=True); p.add_argument("--output"); p.set_defaults(func=validate)
args = parser.parse_args(); args.func(args)
