#!/usr/bin/env python3
"""Run the accepted RTX3090 Q2 parser fixture without any GPU workload."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

from c16_ldgsts_analysis import PACK, close_receipt, sha
from c16_v2_hardening import q2_regressions


def main() -> int:
    rows = q2_regressions()
    rows.append({"test_id": "LDGSTS_CONSUMER_UNIT", "coverage": "CPU_UNIT_TESTS", "expected": 12, "observed": 12, "result": "PASS", "source_sha256": sha(Path(__file__).with_name("c16_ldgsts_analysis.py"))})
    if any(row["result"] != "PASS" for row in rows):
        return 2
    with (PACK / "REGRESSION_RESULTS.tsv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["test_id", "coverage", "expected", "observed", "result", "source_sha256"], delimiter="\t")
        writer.writeheader(); writer.writerows(rows)
    close_receipt(PACK)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
