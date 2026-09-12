#!/usr/bin/env python3
"""Small no-simulator contract checks for C15 Lane C."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location("c15", ROOT / "util/vm_tlb/c15/lane_c/c15_sampling_validation.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

assert MODULE.even_positions(list(range(10)), 3) == [0, 4, 9]
assert MODULE.allocate_budget(8, {"prefill": 692, "decode1": 740}) == {"prefill": 4, "decode1": 4}
assert len(set(range(65530 // 65536, (65542 - 1) // 65536 + 1))) == 2
assert len(set(range(0, 8)) | set(range(4, 12))) == 12
assert MODULE.relative(0, 0) == "UNDEFINED_ZERO_DENOMINATOR"
print("PASS C15 Lane C synthetic contract tests")
