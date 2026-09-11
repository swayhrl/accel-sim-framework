#!/usr/bin/env python3
"""Positive/negative regression for the cap-resolved acceptance bridge."""
from __future__ import annotations
import shutil, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'util/dtc_l1/promote_fast64_4_cap_resolved_matrix_v1.py'
PACKAGE = ROOT / 'docs/dtc_l1/fast64/generated/fast64_4_cap_resolved_matrix_v1'
with tempfile.TemporaryDirectory(prefix='fast64-bridge-') as raw:
    root = Path(raw); good = root / 'good.tsv'
    subprocess.run(['python3', str(TOOL), '--package', str(PACKAGE), '--output', str(good)], check=True)
    assert good.is_file() and (root / 'fast64_4_primary_matrix.tsv').is_file()
    bad = root / 'bad-package'; shutil.copytree(PACKAGE, bad)
    status = bad / 'fast64_4_collector_status.tsv'
    status.write_text(status.read_text(encoding='utf-8').replace('formal_common_cap\t32768', 'formal_common_cap\t8192'), encoding='utf-8')
    target = root / 'bad-output'; target.mkdir()
    result = subprocess.run(['python3', str(TOOL), '--package', str(bad), '--output', str(target / 'bad.tsv')], text=True, capture_output=True)
    assert result.returncode != 0 and 'FINAL_COMMON_CAP_REQUIRED' in result.stderr
print('FAST64_4_CAP_RESOLVED_ACCEPTANCE_BRIDGE_V1_REGRESSION_PASS')
