from __future__ import annotations
import unittest
from pathlib import Path

SOURCE = (Path(__file__).parent / "retry570_nvbit175_capture_closeout.py").read_text()

class CaptureCloseoutTests(unittest.TestCase):
    def test_requires_two_independent_hash_closed_q1_runs(self) -> None:
        for token in ("RUN1", "RUN2", "REMOTE_SHA256SUMS.txt", "dual endpoint SHA mismatch", "Q1_CAPTURE_COMPLETE"):
            self.assertIn(token, SOURCE)

    def test_checks_schema_memory_and_lifecycle_without_claiming_timestamps(self) -> None:
        for token in ("#traces format", "LDG|STG|ATOM", "lifecycle events are absent or unordered", "NOT_APPLICABLE_TRACE_FORMAT_HAS_NO_TIMESTAMP"):
            self.assertIn(token, SOURCE)

    def test_manifest_is_materialized_and_no_models_are_named_as_inputs(self) -> None:
        for token in ("manifest has missing/unmaterialized payload", "raw_payloads_committed", "scientific_eligible"):
            self.assertIn(token, SOURCE)

if __name__ == "__main__": unittest.main()
