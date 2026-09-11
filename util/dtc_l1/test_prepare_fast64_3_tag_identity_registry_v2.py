#!/usr/bin/env python3
"""Static fail-closed regression for the Core-658 Stage3 registry bridge."""
from __future__ import annotations
import importlib.util
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "util/dtc_l1/prepare_fast64_3_tag_identity_registry_v2.py"
spec = importlib.util.spec_from_file_location("fast64_3_tag_identity_v2", PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
rows = [{key: "x" for key in module.HEADINGS}]
rows[0].update({"workload": "2DConvolution", "source_class": "INVALID_HISTORICAL_BASE_PENDING_REPAIR"})
mapped = module.replacement(rows, module.GENERATED / "x.json", module.GENERATED / "y.json")
assert mapped[0]["source_class"] == "REPAIRED_CORE_FRESH"
assert mapped[0]["core_sha"] == module.CORE and mapped[0]["runtime_sha256"] == module.RUNTIME
result = subprocess.run([str(PATH), "--dry-run"], text=True, capture_output=True)
assert result.returncode != 0 and "MISSING_2D_STRICT_OR_STRUCTURAL_EVIDENCE" in result.stderr
print("FAST64_3_TAG_IDENTITY_REGISTRY_V2_STATIC_REGRESSION_PASS")
