#!/usr/bin/env python3
"""Positive and cap-negative regression for the explicit FAST64.4 V2 bridge."""
from __future__ import annotations

import csv
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "util/dtc_l1/prepare_fast64_4_primary_registry_v2.py"
ROSTER = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree", "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")
BASE_HEADINGS = ("workload", "source_class", "summary", "structural", "core_sha", "runtime_sha256")
COVERAGE_HEADINGS = ("workload", "mode", "coverage_status", "identity_disposition", "compact_or_run_reference", "note")


def write_tsv(path: Path, headings: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=headings, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


with tempfile.TemporaryDirectory() as directory:
    generated = Path(directory)
    bases, coverage = [], []
    for workload in ROSTER:
        (generated / "base").mkdir(exist_ok=True)
        base = f"base/{workload}.json"
        (generated / base).write_text(json.dumps({"schema": "dtc_l1_summary_v1", "metrics": {"DTC_L1_lower_cap_full_events": 0}}), encoding="utf-8")
        bases.append({"workload": workload, "source_class": "REPAIRED_CORE_FRESH", "summary": base, "structural": "unused.json", "core_sha": "core", "runtime_sha256": "runtime"})
        for mode in ("IO", "OO"):
            (generated / mode.lower()).mkdir(exist_ok=True)
            ref = f"{mode.lower()}/{workload}.json"
            (generated / ref).write_text(json.dumps({"schema": "dtc_l1_summary_v1", "metrics": {"DTC_L1_lower_cap_full_events": 0}}), encoding="utf-8")
            coverage.append({"workload": workload, "mode": mode, "coverage_status": "STRICT_TERMINAL_REUSE_CANDIDATE", "identity_disposition": "EXACT", "compact_or_run_reference": ref, "note": "strict"})
    base_tsv, coverage_tsv, output = generated / "base.tsv", generated / "coverage.tsv", generated / "out.tsv"
    write_tsv(base_tsv, BASE_HEADINGS, bases)
    write_tsv(coverage_tsv, COVERAGE_HEADINGS, coverage)
    command = [str(PATH), "--generated-root", str(generated), "--base-registry", str(base_tsv), "--coverage", str(coverage_tsv), "--output", str(output)]
    result = subprocess.run(command, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    rows = list(csv.DictReader(output.open(encoding="utf-8", newline=""), delimiter="\t"))
    assert len(rows) == 36
    bad = json.loads((generated / "io" / "ATAX.json").read_text(encoding="utf-8"))
    bad["metrics"]["DTC_L1_lower_cap_full_events"] = 1
    (generated / "io" / "ATAX.json").write_text(json.dumps(bad), encoding="utf-8")
    result = subprocess.run(command[:-1] + [str(generated / "bad.tsv"), "--dry-run"], text=True, capture_output=True)
    assert result.returncode != 0 and "CAP_RESOLUTION_REQUIRED" in result.stderr

print("FAST64_4_PRIMARY_REGISTRY_V2_REGRESSION_PASS")
