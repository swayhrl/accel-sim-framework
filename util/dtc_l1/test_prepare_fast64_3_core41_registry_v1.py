#!/usr/bin/env python3
"""Static fail-closed regression for the Core41 FAST64.3 registry preparer."""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "util/dtc_l1/prepare_fast64_3_core41_registry_v1.py"
spec = importlib.util.spec_from_file_location("prepare_fast64_3_core41_registry_v1", PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)

rows = [{key: "x" for key in module.HEADINGS}]
rows[0].update({"workload": "2DConvolution", "source_class": "INVALID_HISTORICAL_BASE_PENDING_REPAIR"})
mapped = module.replacement(rows)
assert mapped[0]["source_class"] == "REPAIRED_CORE_FRESH"
assert mapped[0]["core_sha"] == module.CORE
assert mapped[0]["runtime_sha256"] == module.RUNTIME
assert mapped[0]["summary"].endswith("core41d740e8_a1_v1.json")

# The production evidence is intentionally absent while the simulator is live;
# dry-run must fail closed rather than manufacture a candidate registry.
result = subprocess.run([str(PATH), "--dry-run"], text=True, capture_output=True)
assert result.returncode != 0
assert "MISSING_2D_STRICT_SUMMARY" in result.stderr
print("FAST64_3_CORE41_REGISTRY_V1_STATIC_REGRESSION_PASS")
