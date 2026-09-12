#!/usr/bin/env python3
"""Fail closed on an observer-off/on scientific-output difference."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys


NEW_OBSERVER = re.compile(
    r"^DTC_L1_(?:io|oo)_(?:duplicate_after_eviction|alloc_to_ready_"
    r"(?:count|sum_cycles|max_cycles)|pending_tag_eviction_count|"
    r"pending_evict_to_response_(?:count|sum_cycles|max_cycles)|"
    r"observer_live_records)$"
)
STAT = re.compile(r"^([A-Za-z][A-Za-z0-9_]*) = (.+)$")
TERMINAL_MARKER = "GPGPU-Sim: *** exit detected ***"
SCIENTIFIC_PREFIXES = ("DTC_L1_", "L2_", "gpu_tot_sim_", "gpgpu_n_")


def parse_run(path: pathlib.Path) -> dict[str, object]:
    stdout = path / "simulator.stdout"
    terminal = path / "RUN_TERMINAL.tsv"
    if not stdout.is_file() or not terminal.is_file():
        raise ValueError(f"missing immutable terminal artifacts under {path}")
    text = stdout.read_text(encoding="utf-8", errors="replace")
    if TERMINAL_MARKER not in text:
        raise ValueError(f"no natural terminal marker in {stdout}")
    status = dict(
        line.split("\t", 1)
        for line in terminal.read_text(encoding="utf-8").splitlines()[1:]
        if "\t" in line
    ).get("simulator_exit_status")
    if status != "0":
        raise ValueError(f"nonzero terminal status {status!r} in {terminal}")
    stats: dict[str, str] = {}
    for line in text.splitlines():
        match = STAT.match(line)
        if match:
            key, value = match.groups()
            if not key.startswith(SCIENTIFIC_PREFIXES):
                continue
            if key in stats and stats[key] != value:
                raise ValueError(f"ambiguous repeated stat {key!r} in {stdout}")
            stats[key] = value
    if "gpu_tot_sim_cycle" not in stats or "gpu_tot_sim_insn" not in stats:
        raise ValueError(f"missing cycle/instruction stats in {stdout}")
    return {"path": str(path), "stats": stats}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--off-run", type=pathlib.Path, required=True)
    parser.add_argument("--on-run", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    try:
        off = parse_run(args.off_run)
        on = parse_run(args.on_run)
        off_stats = off["stats"]
        on_stats = on["stats"]
        assert isinstance(off_stats, dict) and isinstance(on_stats, dict)
        preexisting = sorted(
            key for key in set(off_stats) | set(on_stats) if not NEW_OBSERVER.match(key)
        )
        missing = [key for key in preexisting if key not in off_stats or key not in on_stats]
        changed = [
            {"key": key, "off": off_stats[key], "on": on_stats[key]}
            for key in preexisting
            if key in off_stats and key in on_stats and off_stats[key] != on_stats[key]
        ]
        new_keys = sorted(key for key in set(off_stats) | set(on_stats) if NEW_OBSERVER.match(key))
        missing_new = [key for key in new_keys if key not in off_stats or key not in on_stats]
        off_nonzero = {key: off_stats[key] for key in new_keys if off_stats.get(key) != "0"}
        live_keys = [key for key in new_keys if key.endswith("observer_live_records")]
        live_nonzero = {
            key: {"off": off_stats.get(key), "on": on_stats.get(key)}
            for key in live_keys
            if off_stats.get(key) != "0" or on_stats.get(key) != "0"
        }
        report = {
            "schema": "POST_FAST64_OBSERVER_EQUIVALENCE_V1",
            "classification": "POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT",
            "off_run": off["path"],
            "on_run": on["path"],
            "cycles": {"off": off_stats["gpu_tot_sim_cycle"], "on": on_stats["gpu_tot_sim_cycle"]},
            "instructions": {"off": off_stats["gpu_tot_sim_insn"], "on": on_stats["gpu_tot_sim_insn"]},
            "preexisting_stat_count": len(preexisting),
            "new_observer_stat_count": len(new_keys),
            "missing_preexisting": missing,
            "changed_preexisting": changed,
            "missing_new_observer": missing_new,
            "telemetry_off_nonzero": off_nonzero,
            "terminal_live_observer_records": live_nonzero,
        }
        report["pass"] = not any(
            (missing, changed, missing_new, off_nonzero, live_nonzero)
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print("POST_FAST64_OBSERVER_EQUIVALENCE_" + ("PASS" if report["pass"] else "FAIL"))
        return 0 if report["pass"] else 1
    except (OSError, ValueError, AssertionError) as error:
        print(f"POST_FAST64_OBSERVER_EQUIVALENCE_ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
