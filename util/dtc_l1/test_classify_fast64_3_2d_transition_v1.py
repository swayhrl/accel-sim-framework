#!/usr/bin/env python3
"""Regression coverage for A/B/C factual 2D source-followup buckets."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "util/dtc_l1/classify_fast64_3_2d_transition_v1.py"

with tempfile.TemporaryDirectory() as raw:
    root = Path(raw); input_path = root / "diagnostic.json"; output = root / "followup.json"
    input_path.write_text(json.dumps({"schema": "FAST64_3_2DCONVOLUTION_BASE_TRANSITION_DIAGNOSTIC_V2", "classification": "NONFORMAL_DIAGNOSTIC_NOT_RESULT", "terminal_dump": {"present": True, "l1d": {"L1D_003": {"reserved_lines": [{"block": "0x100", "way": 0, "owner_state": "OWNER_PRESENT", "owner": {"pending_read": 2}}, {"block": "0x180", "way": 1, "owner_state": "OWNER_ABSENT", "owner": None}, {"block": "0x200", "way": 2, "owner_state": "OWNER_PRESENT", "owner": {"pending_read": 0}}]}}}}), encoding="utf-8")
    good = subprocess.run([sys.executable, str(TOOL), "--diagnostic", str(input_path), "--output", str(output)], text=True, capture_output=True)
    assert good.returncode == 0, good.stderr
    buckets = {row["block"]: row["source_followup_bucket"] for row in json.loads(output.read_text(encoding="utf-8"))["reserved_lines"]}
    assert buckets == {"0x100": "A_PENDING_SECTOR_CHILD_RESPONSE", "0x180": "B_OWNERLESS_RESERVED_LINE", "0x200": "C_FINAL_FILL_OR_RETIRE_TRANSITION"}
    bad = subprocess.run([sys.executable, str(TOOL), "--diagnostic", str(input_path), "--output", str(output)], text=True, capture_output=True)
    assert bad.returncode != 0 and "OUTPUT_ALREADY_EXISTS" in bad.stderr
print("FAST64_3_2D_SOURCE_FOLLOWUP_V1_REGRESSION_PASS")
