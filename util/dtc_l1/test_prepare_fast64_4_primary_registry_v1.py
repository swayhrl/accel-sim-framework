#!/usr/bin/env python3
"""Regression for the future-only FAST64.4 collector-registry preparer."""
from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "util/dtc_l1/prepare_fast64_4_primary_registry_v1.py"
spec = importlib.util.spec_from_file_location("prepare_fast64_4_primary_registry_v1", PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


def write_tsv(path: Path, headings: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=headings, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


with tempfile.TemporaryDirectory() as directory:
    generated = Path(directory)
    base_rows, coverage_rows = [], []
    for workload in module.ROSTER:
        base_ref = f"base/{workload}.json"
        (generated / "base").mkdir(exist_ok=True)
        (generated / base_ref).write_text(json.dumps({"schema": "dtc_l1_summary_v1", "metrics": {"DTC_L1_lower_cap_full_events": 0}}), encoding="utf-8")
        base_rows.append({"workload": workload, "source_class": "REPAIRED_CORE_FRESH", "summary": base_ref, "structural": "unused.json", "core_sha": "core", "runtime_sha256": "runtime"})
        for mode in ("IO", "OO"):
            ref = f"{mode.lower()}/{workload}.json"
            (generated / mode.lower()).mkdir(exist_ok=True)
            (generated / ref).write_text(json.dumps({"schema": "dtc_l1_summary_v1", "metrics": {"DTC_L1_lower_cap_full_events": 0}}), encoding="utf-8")
            coverage_rows.append({"workload": workload, "mode": mode, "coverage_status": "STRICT_TERMINAL_REUSE_CANDIDATE", "identity_disposition": "CORE95_EXACT", "compact_or_run_reference": ref, "note": "strict"})
    base_path, coverage_path, output = generated / "base.tsv", generated / "coverage.tsv", generated / "output.tsv"
    write_tsv(base_path, module.BASE_HEADINGS, base_rows)
    write_tsv(coverage_path, module.COVERAGE_HEADINGS, coverage_rows)
    result = subprocess.run([str(PATH), "--generated-root", str(generated), "--base-registry", str(base_path), "--coverage", str(coverage_path), "--output", str(output)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    rows = list(csv.DictReader(output.open(encoding="utf-8", newline=""), delimiter="\t"))
    assert len(rows) == 36
    assert {(row["workload"], row["mode"]) for row in rows} == {(workload, mode) for workload in module.ROSTER for mode in ("BASE", "IO", "OO")}
    assert all(row["cap_disposition"] == "ZERO" for row in rows)
    bad = json.loads((generated / "io" / f"{module.ROSTER[0]}.json").read_text(encoding="utf-8")); bad["metrics"]["DTC_L1_lower_cap_full_events"] = 1
    (generated / "io" / f"{module.ROSTER[0]}.json").write_text(json.dumps(bad), encoding="utf-8")
    result = subprocess.run([str(PATH), "--generated-root", str(generated), "--base-registry", str(base_path), "--coverage", str(coverage_path), "--output", str(generated / "bad.tsv"), "--dry-run"], text=True, capture_output=True)
    assert result.returncode != 0 and "CAP_RESOLUTION_REQUIRED" in result.stderr

print("FAST64_4_PRIMARY_REGISTRY_V1_REGRESSION_PASS")
