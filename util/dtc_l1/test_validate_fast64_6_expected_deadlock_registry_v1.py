#!/usr/bin/env python3
"""Regression boundary for the nonnumeric FAST64.6 deadlock registry."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "util/dtc_l1/validate_fast64_6_expected_deadlock_registry_v1.py"
REGISTRY = ROOT / "docs/dtc_l1/fast64/generated/FAST64_6_EXPECTED_RESOURCE_DEADLOCK_REGISTRY_V1.tsv"
MATRIX = ROOT / "docs/dtc_l1/fast64/generated/FAST64_6_SENSITIVITY_MATRIX_V1.tsv"


def run(registry: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run((sys.executable, str(TOOL), "--registry", str(registry), "--matrix", str(MATRIX)),
                          cwd=ROOT, text=True, capture_output=True, check=False)


good = run(REGISTRY)
if good.returncode != 0 or "FAST64_6_EXPECTED_DEADLOCK_REGISTRY_V1_PASS rows=4" not in good.stdout:
    raise SystemExit("EXPECTED_DEADLOCK_VALID_REGISTRY_REGRESSION_FAILED")

with tempfile.TemporaryDirectory() as directory:
    altered = Path(directory) / "registry.tsv"
    altered.write_text(REGISTRY.read_text(encoding="utf-8").replace(
        "EXPECTED_RESOURCE_DEADLOCK_NO_NUMERIC_PERFORMANCE", "ILLEGAL_NUMERIC_PROMOTION", 1), encoding="utf-8")
    bad = run(altered)
    if bad.returncode == 0 or "DISPOSITION_INVALID" not in (bad.stderr + bad.stdout):
        raise SystemExit("EXPECTED_DEADLOCK_ILLEGAL_PROMOTION_NOT_REJECTED")

print("FAST64_6_EXPECTED_DEADLOCK_REGISTRY_V1_REGRESSION_PASS")
