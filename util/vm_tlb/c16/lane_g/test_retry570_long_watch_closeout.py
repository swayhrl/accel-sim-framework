#!/usr/bin/env python3
"""CPU-only validation for Retry570 one-shot long-watch publication."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from retry570_long_watch_closeout import REQUIRED_RAW, STATUS, TOOL_SHA, validate, write  # noqa: E402


class LongWatchCloseoutTests(unittest.TestCase):
    def test_write_and_validate_preserves_pre_watch_failure_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw = root / "raw"
            raw.mkdir()
            baseline = {"status": "BASELINE_FIRST_CUDA_KERNEL_OBSERVED", "mode": "BASELINE", "run_id": "base", "first_cuda_kernel_completed_elapsed_seconds": 1.0, "trace_generated": False, "terminal_status": "COMPLETE", "child_receipt": {"path": "child"}}
            long = {"status": "NVBIT_LONG_WATCH_CHILD_FAILED_BEFORE_FIRST_KERNEL", "mode": "NVBIT_LONG_WATCH", "run_id": "long", "wall_limit_seconds": 300, "sample_seconds": 5, "first_cuda_kernel_completed_elapsed_seconds": None, "trace_generated": False, "terminal_status": "FAILED_OR_ABORTED", "runtime_code_commit": "d8021532adfd94b4196785475f5c3914a3f51c2e", "nvbit_tool": {"sha256": TOOL_SHA}}
            for name in REQUIRED_RAW:
                if name == "BASELINE_CHILD_RECEIPT.json":
                    raw.joinpath(name).write_text(json.dumps({"status": "CHILD_COMPLETE", "runtime_identity": {"gpu": "test"}}), encoding="utf-8")
                elif name == "BASELINE_RECEIPT.json":
                    raw.joinpath(name).write_text(json.dumps(baseline), encoding="utf-8")
                elif name == "NVBIT_LONG_WATCH_RECEIPT.json":
                    raw.joinpath(name).write_text(json.dumps(long), encoding="utf-8")
                elif name == "NVBIT_LONG_WATCH_STDOUT.log":
                    raw.joinpath(name).write_text("ERROR: /usr/local/cuda-12.4/bin/nvdisasm not found on PATH!!!", encoding="utf-8")
                else:
                    raw.joinpath(name).write_text("diagnostic", encoding="utf-8")
            ledger = root / "ledger.json"
            ledger.write_text(json.dumps({"entries": [
                *[{"operation_kind": "NVBIT", "deployment_id": "c16_retry570_indexselect_microreproducer"} for _ in range(6)],
                {"operation_kind": "NVBIT_LONG_WATCH_DIAGNOSTIC", "run_id": "base", "raw_bytes": 0, "evidence_classification": "NON_SCIENTIFIC_DIAGNOSTIC"},
                {"operation_kind": "NVBIT_LONG_WATCH_DIAGNOSTIC", "run_id": "long", "raw_bytes": 0, "evidence_classification": "NON_SCIENTIFIC_DIAGNOSTIC"},
            ]}), encoding="utf-8")
            authorization = root / "authorization.json"
            authorization.write_text(json.dumps({"status": "COMPLETE", "run_id": "long", "receipt_sha256": hashlib.sha256((raw / "NVBIT_LONG_WATCH_RECEIPT.json").read_bytes()).hexdigest()}), encoding="utf-8")
            directory = root / "publish"
            write(directory, raw, ledger, authorization)
            self.assertEqual(validate(directory)["status"], "PASS")
            self.assertEqual(json.loads((directory / "PUBLISH_MANIFEST.json").read_text())["status"], STATUS)


if __name__ == "__main__":
    unittest.main()
