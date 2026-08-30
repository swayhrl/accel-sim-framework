#!/usr/bin/env python3
"""Fail-closed post-processing for one already-finished M0a simulator log.

This tool deliberately never launches a simulator.  It is for a retained raw
log whose producer has exited normally, and applies the same parser/status
contract used by the M0a campaign runner.
"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys

from run_m0a_observability import ROOT, digest, terminal, write_json


def run_parser(command: list[str], label: str) -> None:
    completed = subprocess.run(command, text=True, capture_output=True)
    destination = Path(command[command.index("--out") + 1])
    (destination / f"{label}_parser.stdout").write_text(completed.stdout)
    (destination / f"{label}_parser.stderr").write_text(completed.stderr)
    if completed.returncode:
        raise ValueError(completed.stderr.strip() or f"{label} parser failed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--workload", required=True)
    parser.add_argument("--mode", choices=("ON",), default="ON")
    args = parser.parse_args()
    directory = args.results / args.mode / args.workload
    log = directory / "raw.log"
    if (directory / "run_status.json").exists():
        raise SystemExit("refusing to replace existing run status")
    if not log.is_file():
        raise SystemExit("missing retained raw log: " + str(log))
    audit = json.loads((args.results / "campaign_manifest.json").read_text())
    normal, cycles, instructions = terminal(log)
    status = {"workload": args.workload, "mode": args.mode, "exit_code": 0,
              "normal_simulator_exit": normal, "terminal_gpu_tot_sim_cycle": cycles,
              "terminal_gpu_tot_sim_insn": instructions, "audit": audit}
    if not normal or cycles is None or instructions is None:
        status.update({"status": "FAILED", "detail": "missing normal terminal evidence"})
        write_json(directory / "run_status.json", status)
        raise SystemExit(status["detail"])
    try:
        run_parser([sys.executable, str(ROOT / "util/ep_l2/parse_epl2_m0a.py"), str(log),
                    "--out", str(directory), "--framework-commit", audit["framework_sha"],
                    "--core-commit", audit["core_sha"]], "m0a")
        run_parser([sys.executable, str(ROOT / "util/ep_l2/parse_epl2_b0.py"), str(log),
                    "--out", str(directory), "--framework-commit", audit["framework_sha"],
                    "--core-commit", audit["core_sha"], "--source-log", str(log)], "b0")
        packed = log.with_suffix(".log.gz")
        with log.open("rb") as source, gzip.open(packed, "wb") as destination:
            shutil.copyfileobj(source, destination)
        log.unlink()
        status.update({"status": "COMPLETE_VALID", "raw_log_gz": str(packed),
                       "raw_log_gz_sha256": digest(packed)})
        write_json(directory / "run_status.json", status)
    except (OSError, ValueError, KeyError) as error:
        status.update({"status": "FAILED", "detail": str(error)})
        write_json(directory / "run_status.json", status)
        raise SystemExit(str(error))


if __name__ == "__main__":
    main()
