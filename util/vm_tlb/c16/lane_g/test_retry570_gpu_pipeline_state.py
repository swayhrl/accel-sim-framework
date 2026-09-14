"""CPU-only contract tests for the single shared Recovery-V3 lane state."""
from __future__ import annotations

import argparse
import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from c16_native_common import ContractError, sha256_file  # noqa: E402
from retry570_gpu_pipeline_state import queue_ready, refresh_state  # noqa: E402


class PipelineStateTests(unittest.TestCase):
    def test_atomic_state_and_closed_copyback_publication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = argparse.Namespace(git_head="a" * 40, gpu_active_job="none", gpu_ready_queue_count=2,
                                       next_gpu_job="qwen0/S3/decode", measurement_active=False,
                                       active_gpu_process_count=0, transfer_slot_granted=True)
            refresh_state(root, state)
            raw = root / "raw.bin"; raw.write_bytes(b"closed")
            args = argparse.Namespace(run_id="r", model="Qwen0", scenario="S3", stage="R5",
                                      remote_path=str(raw), bytes=raw.stat().st_size, remote_sha256=sha256_file(raw))
            queue_ready(root, args)
            self.assertIn("COPYBACK_READY", (root / "COPYBACK_QUEUE.json").read_text(encoding="utf-8"))

    def test_rejects_mismatched_remote_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            raw = Path(directory) / "raw.bin"; raw.write_bytes(b"closed")
            args = argparse.Namespace(run_id="r", model="Qwen0", scenario="S3", stage="R5",
                                      remote_path=str(raw), bytes=raw.stat().st_size, remote_sha256="0" * 64)
            with self.assertRaises(ContractError):
                queue_ready(Path(directory), args)


if __name__ == "__main__":
    unittest.main()
