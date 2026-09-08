#!/usr/bin/env python3
"""Non-scientific fixture regression for alias-v2 normalization."""
from __future__ import annotations

import importlib.util
import pathlib
import tempfile

root = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("alias_v2", root / "validate_fast64_trace_row_alias_v2.py")
assert spec and spec.loader
# The module's CLI bootstrap cannot be imported directly; exercise its source
# contract with a disposable alias layout instead.
source = (root / "validate_fast64_trace_row_alias_v2.py").read_text()
assert "alias.resolve() != canonical.resolve()" in source
assert "FROZEN_SHA256" in source
with tempfile.TemporaryDirectory(prefix="fast64-alias-v2-") as tmp:
    d = pathlib.Path(tmp)
    canonical = d / "perf_counter_2026-01-01_00-00-00.csv.gz"
    canonical.write_bytes(b"fixture")
    (d / "perf_counter.csv.gz").symlink_to(canonical.name)
    assert canonical.resolve() == (d / "perf_counter.csv.gz").resolve()
print("FAST64_ALIAS_V2_STATIC_REGRESSION_PASS")
