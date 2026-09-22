#!/usr/bin/env python3
"""Non-authority synthetic closure test for the independent 243 recompute."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from recompute_243 import HEADER, recompute


class Recompute243Tests(unittest.TestCase):
    def test_243_zero_shard_closure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selector = root / "selector.tsv"
            indices = [*range(242), 1085]
            selector.write_text("static_index\tlabel\n" + "".join(f"{index}\ts{index}\n" for index in indices), encoding="utf-8")
            shards = root / "shards"
            for index in indices:
                shard = shards / f"static_{index}"
                shard.mkdir(parents=True)
                (shard / "trace.bin").write_bytes(HEADER.pack(b"C16WARP1", index, 0, 0, 0, 0))
                (shard / "stdout.log").write_text(
                    f"C16_WARP_TERMINAL static={index} occurrence=0 records=0 overflow=0\n"
                    "C16_P5_ACCOUNTING producer=0 receiver=0 serialized=0 overflow=0\n"
                    "C16_TARGET_OCCURRENCE observed=0 action=SELECT\n"
                    "C16_TARGET_OCCURRENCE_COUNT selected=0 observed=1\n",
                    encoding="utf-8",
                )
                (shard / "ADDRESS_CONTEXT.json").write_text(json.dumps({"ranges": [{"semantic_role": "EXPERT_DOWN_INPUT", "ptr": "0x1000", "bytes": 2}]}), encoding="utf-8")
                (shard / "SUPERVISOR_RECEIPT.json").write_text(json.dumps({
                    "selected_static": index, "occurrence": 0, "phase": "CLEAN_EXIT", "timed_out": False,
                    "returncode": 0, "c16_output_path": "trace.bin",
                    "residual_process_check": {"no_target_residual_process": True},
                    "tool_sha256": "a" * 64, "canonical_replay_sha256": "b" * 64,
                    "function_identity_sha256": "c" * 64,
                }), encoding="utf-8")
            summary, rows = recompute(selector, shards, None)
            self.assertEqual(summary["status"], "PASS")
            self.assertEqual(summary["total_selected"], 243)
            self.assertEqual(summary["zero_count"], 243)
            self.assertEqual(summary["dynamic_warp_records"], 0)
            self.assertEqual(summary["active_lane_events"], 0)
            self.assertEqual(len(rows), 243)


if __name__ == "__main__":
    unittest.main()
