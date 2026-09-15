#!/usr/bin/env python3
"""Run the slow canonical rehash gate and persist only its PASS result."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from post_archive_cleanup import CleanupError, predelete_recheck

if len(sys.argv) != 3:
    raise SystemExit("usage: run_predelete_recheck.py STATUS_TSV RESULT_JSON")
try:
    rows = predelete_recheck(Path(sys.argv[1]))
except CleanupError as error:
    raise SystemExit(f"PRE_DELETE_CANONICAL_RECHECK_FAIL: {error}")
Path(sys.argv[2]).write_text(json.dumps({"status": "PASS", "models": [row["model_slug"] for row in rows]}, indent=2) + "\n", encoding="utf-8")
print("PRE_DELETE_CANONICAL_RECHECK_PASS", len(rows))
