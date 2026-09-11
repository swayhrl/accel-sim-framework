#!/usr/bin/env python3
"""Static regression for the future-only Core658 FAST64.3 registry preparer."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "util/dtc_l1/prepare_fast64_3_core658_registry_v1.py"
spec = importlib.util.spec_from_file_location("prepare_fast64_3_core658_registry_v1", PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("CANNOT_LOAD_CORE658_REGISTRY_PREPARER")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

assert module.REGISTRY.name == "FAST64_3_BASE_SOURCE_REGISTRY_V2.tsv"
assert module.OUTPUT.name == "FAST64_3_BASE_SOURCE_REGISTRY_V4_CORE658.tsv"
assert set(module.REPLACEMENTS) == {"GESUMMV", "2DConvolution"}
assert module.REPLACEMENTS["GESUMMV"]["core_sha"] == "95ccdb7a056f2d53f740d90869785cac6d4ee0f5"
assert module.REPLACEMENTS["2DConvolution"]["core_sha"] == "6587238c60214d99491f4048e28ce8a3458c1509"
assert module.REPLACEMENTS["2DConvolution"]["expected_source_class"] == "INVALID_HISTORICAL_BASE_PENDING_REPAIR"
source = PATH.read_text(encoding="utf-8")
assert "path.exists()" in source and "CANDIDATE_REGISTRY_ALREADY_EXISTS" in source
assert "os.link(temporary, path)" in source
assert "PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE" in source
print("FAST64_3_CORE658_REGISTRY_V1_STATIC_REGRESSION_PASS")
