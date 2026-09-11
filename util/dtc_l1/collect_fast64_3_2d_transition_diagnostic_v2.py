#!/usr/bin/env python3
"""Fail-closed, read-only terminal collector for the dc6062 2D diagnostic."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
RUN = pathlib.Path("/workspace/fast64-diagnostics/fast64_3_2DConvolution_base_coredc6062_transition_diag_v2")
ANALYZER = ROOT / "util/dtc_l1/analyze_fast64_3_2d_transition_diagnostic_v2.py"
OUTPUT = ROOT / "docs/dtc_l1/fast64/generated/fast64_3_transition_diagnostics_v2/fast64_3_2d_base_coredc6062_transition_diag_v2.json"
EXPECTED = {
    "runner_schema": "FAST64_TRACE_V2_IMMUTABLE_ATTEMPT",
    "runner_sha256": "bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af",
    "simulator_sha256": "8ad7f3c62e4b792f4c8aded8f56ba7a9a24cd4e69c331d1c59238ef0a54a1da1",
    "config_sha256": "1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde",
    "trace_list_sha256": "23bcc08b04d82fc527ffc1365d3199f4d1f3057bf6a2705d1110c5c226227d64",
    "core_source_head": "dc6062c69843ffb467ceabd32eed625fbc5776bf",
    "result_classification": "NONFORMAL_DIAGNOSTIC_NOT_RESULT",
    "attempt_uuid": "482ca8b3-fa7c-4a8b-b99d-494e349961a6",
}


def tsv(path: pathlib.Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "key\tvalue":
        raise ValueError(f"unexpected receipt/manifest header: {path}")
    values: dict[str, str] = {}
    for line in lines[1:]:
        key, value = line.split("\t", 1)
        if key in values:
            raise ValueError(f"duplicate key {key} in {path}")
        values[key] = value
    return values


def collect() -> int:
    if OUTPUT.exists():
        print(f"FAST64_3_2D_TRANSITION_DIAG_COLLECT_SKIP_PRESENT\toutput={OUTPUT}")
        return 0
    terminal = RUN / "RUN_TERMINAL.tsv"
    if not terminal.is_file():
        print(f"FAST64_3_2D_TRANSITION_DIAG_COLLECT_WAIT_TERMINAL\trun={RUN}")
        return 0
    manifest = tsv(RUN / "RUN_MANIFEST.tsv")
    start = tsv(RUN / "RUN_START.tsv")
    end = tsv(terminal)
    for key, expected in EXPECTED.items():
        observed = start.get(key) if key == "attempt_uuid" else manifest.get(key)
        if observed != expected:
            raise ValueError(f"immutable diagnostic identity mismatch {key}: {observed!r}")
    for receipt, kind in ((start, "START"), (end, "TERMINAL")):
        if receipt.get("receipt_schema") != "FAST64_ATTEMPT_RECEIPT_V1" or receipt.get("receipt_type") != kind:
            raise ValueError(f"bad {kind} receipt schema")
        if receipt.get("attempt_uuid") != EXPECTED["attempt_uuid"]:
            raise ValueError(f"bad {kind} receipt UUID")
        if receipt.get("runner_sha256") != EXPECTED["runner_sha256"]:
            raise ValueError(f"bad {kind} runner SHA")
    if end.get("simulator_exit_status") not in {"0", "1"}:
        raise ValueError(f"unexpected terminal status: {end.get('simulator_exit_status')!r}")
    transition_log = RUN / "simulator.stderr"
    if not transition_log.is_file():
        raise ValueError("terminal diagnostic transition log missing")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    terminal_dump = RUN / "simulator.stdout"
    if not terminal_dump.is_file():
        raise ValueError("terminal diagnostic stdout missing")
    analyzer = [str(ANALYZER), "--transition-log", str(transition_log), "--terminal-dump", str(terminal_dump), "--output", str(OUTPUT)]
    if end.get("simulator_exit_status") == "1":
        analyzer.append("--require-deadlock-snapshot")
    subprocess.run(analyzer, check=True)
    if not OUTPUT.is_file():
        raise ValueError("analyzer did not publish output")
    result = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if result.get("classification") != EXPECTED["result_classification"]:
        raise ValueError("analyzer classification mismatch")
    print(f"FAST64_3_2D_TRANSITION_DIAG_COLLECT_PUBLISHED\texit={end['simulator_exit_status']}\toutput={OUTPUT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collect", action="store_true", help="check once; never launches or signals a process")
    args = parser.parse_args()
    if not args.collect:
        parser.error("--collect is required")
    return collect()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"FAST64_3_2D_TRANSITION_DIAG_COLLECT_FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
