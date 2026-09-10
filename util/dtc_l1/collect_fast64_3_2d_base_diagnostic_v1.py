#!/usr/bin/env python3
"""Fail-closed, read-only terminal collector for the 2D Base diagnostic."""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
RUN = pathlib.Path("/workspace/fast64-diagnostics/fast64_3_2DConvolution_base_coref283_diag_v1")
ANALYZER = ROOT / "util/dtc_l1/analyze_fast64_3_2d_base_diagnostic_v1.py"
OUTPUT = ROOT / "docs/dtc_l1/fast64/generated/fast64_3_diagnostics_v1/fast64_3_2d_base_coref283_diag_v1.json"
EXPECTED = {
    "runner_schema": "FAST64_TRACE_V2_IMMUTABLE_ATTEMPT",
    "runner_sha256": "bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af",
    "simulator_sha256": "361aada1e0fc166cb161670e0c9386dc63baad9c8f75587d34cfb69d51da48e7",
    "config_sha256": "1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde",
    "trace_list_sha256": "23bcc08b04d82fc527ffc1365d3199f4d1f3057bf6a2705d1110c5c226227d64",
    "core_source_head": "f2836ea1258ce64d2ca48e1b7a8ec8522060203f",
    "result_classification": "NONFORMAL_DIAGNOSTIC_NOT_RESULT",
    "attempt_uuid": "a970b692-22d5-441d-ad6a-faa500d9d573",
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
    terminal = RUN / "RUN_TERMINAL.tsv"
    if OUTPUT.exists():
        print(f"FAST64_3_2D_DIAG_COLLECT_SKIP_PRESENT\toutput={OUTPUT}")
        return 0
    if not terminal.is_file():
        print(f"FAST64_3_2D_DIAG_COLLECT_WAIT_TERMINAL\trun={RUN}")
        return 0
    manifest = tsv(RUN / "RUN_MANIFEST.tsv")
    start = tsv(RUN / "RUN_START.tsv")
    end = tsv(terminal)
    for key, expected in EXPECTED.items():
        observed = manifest.get(key) if key not in {"attempt_uuid"} else start.get(key)
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
    stdout = RUN / "simulator.stdout"
    if not stdout.is_file():
        raise ValueError("terminal diagnostic stdout missing")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(ANALYZER), "--input", str(stdout), "--output", str(OUTPUT)], check=True)
    if not OUTPUT.is_file():
        raise ValueError("analyzer did not publish output")
    print(f"FAST64_3_2D_DIAG_COLLECT_PUBLISHED\texit={end['simulator_exit_status']}\toutput={OUTPUT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collect", action="store_true", help="check exactly once; never launches or signals a process")
    args = parser.parse_args()
    if not args.collect:
        parser.error("--collect is required")
    return collect()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"FAST64_3_2D_DIAG_COLLECT_FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
