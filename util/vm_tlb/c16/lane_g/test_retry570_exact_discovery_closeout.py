#!/usr/bin/env python3
"""CPU-only contract checks for exact-target discovery closeout."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from retry570_exact_discovery_closeout import (  # noqa: E402
    ATTEMPTS, EXACT_TARGET, STATUS, validate, write,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_raw(root: Path, spec: dict[str, str], pre_lookup: bool) -> None:
    root.mkdir(parents=True)
    stdout = [f'C16_EXACT_DISCOVERY_CHILD_STAGE {{"stage": "EXACT_TARGET_SUBMISSION_BEGIN", "exact_target_mangled": "{EXACT_TARGET}"}}']
    if pre_lookup:
        stdout = []
        for index in range(4):
            stdout.extend((
                f"C16_EXACT_DISCOVERY ts_us={100 + index * 2} stage=PRE_TARGET_NAME_LOOKUP_BEGIN launch=0 function_mangled=UNRESOLVED function_handle=0x{index} index=-1 related_function_count=-1 unique_handle_count=-1 unique_name_count=-1 static_instruction_count=-1 cumulative_us=0 elapsed_us=0",
                f"C16_EXACT_DISCOVERY ts_us={101 + index * 2} stage=PRE_TARGET_NAME_LOOKUP_END launch=0 function_mangled=other{index} function_handle=0x{index} index=-1 related_function_count=-1 unique_handle_count=-1 unique_name_count=-1 static_instruction_count=-1 cumulative_us=0 elapsed_us=1",
            ))
        stdout.append(f'C16_EXACT_DISCOVERY_CHILD_STAGE {{"stage": "EXACT_TARGET_SUBMISSION_BEGIN", "exact_target_mangled": "{EXACT_TARGET}"}}')
    (root / "stdout.log").write_text("\n".join(stdout) + "\n")
    (root / "stderr.log").write_text("diagnostic only\n")
    (root / "stage.json").write_text(json.dumps({"stage": "EXACT_TARGET_SUBMISSION_BEGIN"}))
    (root / "EXECUTION_BUDGET_LEDGER_AFTER.json").write_text("{}\n")
    (root / "stack_snapshot.txt").write_text("kernel_stack=UNAVAILABLE: PermissionError\n")
    samples = []
    for ordinal in range(2):
        samples.append({"stage": {"stage": "EXACT_TARGET_SUBMISSION_BEGIN"}, "gpu_utilization_and_memory": "0, 335", "child_pid_present_in_gpu_processes": True, "process_tree": [{"cpu_percent": str(104 + ordinal)}]})
    (root / "samples.jsonl").write_text("\n".join(json.dumps(row) for row in samples) + "\n")
    receipt = {"status": "BOUNDED_TIMEOUT_DISCOVERY_LAST_MARKER_RETAINED", "terminal_status": "BOUNDED_TIMEOUT", "scientific_eligible": False, "trace_generated": False, "raw_trace_bytes": 0, "wall_limit_seconds": 60, "runtime_code_commit": spec["runtime_commit"], "exact_target_mangled": EXACT_TARGET, "tool": {"sha256": spec["tool_sha256"]}, "run_id": f"unit-{spec['key']}", "elapsed_seconds": 60.1, "stack_snapshots": [{"path": "stack_snapshot.txt"}]}
    (root / "receipt.json").write_text(json.dumps(receipt))
    entries = []
    for item in sorted(path for path in root.rglob("*") if path.is_file()):
        entries.append({"logical_path": item.relative_to(root).as_posix(), "bytes": item.stat().st_size, "sha256": _sha(item)})
    tree = hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (root / "REMOTE_ARTIFACT_MANIFEST.json").write_text(json.dumps({"schema_version": "C16_RETRY570_REMOTE_RAW_MANIFEST_V1", "root": str(root), "payload_count": len(entries), "payloads": entries, "payload_tree_sha256": tree}))


class ExactDiscoveryCloseoutTests(unittest.TestCase):
    def test_write_and_validate_pre_callback_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary) / "raw"
            _make_raw(base / ATTEMPTS[0]["root_name"], ATTEMPTS[0], False)
            _make_raw(base / ATTEMPTS[1]["root_name"], ATTEMPTS[1], True)
            directory = Path(temporary) / "publish"
            write(directory, base)
            self.assertEqual(validate(directory)["status"], "PASS")
            self.assertEqual(json.loads((directory / "PUBLISH_MANIFEST.json").read_text())["status"], STATUS)

    def test_rejects_target_discovery_attribution_without_callback_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary) / "raw"
            _make_raw(base / ATTEMPTS[0]["root_name"], ATTEMPTS[0], False)
            target = base / ATTEMPTS[1]["root_name"]
            _make_raw(target, ATTEMPTS[1], True)
            with (target / "stdout.log").open("a", encoding="utf-8") as handle:
                handle.write("C16_EXACT_DISCOVERY ts_us=999 stage=TARGET_CALLBACK_ENTER launch=1 function_mangled=x function_handle=0x1 index=-1 related_function_count=-1 unique_handle_count=-1 unique_name_count=-1 static_instruction_count=-1 cumulative_us=0 elapsed_us=0\n")
            # Reclose only the changed raw payload; the stale manifest must itself fail closed.
            with self.assertRaises(Exception):
                write(Path(temporary) / "publish", base)


if __name__ == "__main__":
    unittest.main()
