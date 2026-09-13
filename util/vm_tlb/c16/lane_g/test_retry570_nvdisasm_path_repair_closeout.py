#!/usr/bin/env python3
"""CPU-only smoke-closeout guard: path repair never qualifies long-watch."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from retry570_nvdisasm_path_repair_closeout import (  # noqa: E402
    OFFICIAL_TOOL_SHA, REQUIRED_RAW, RUNTIME_COMMIT, STATUS, validate, write,
)


class NvdisasmPathRepairCloseoutTests(unittest.TestCase):
    def test_path_smoke_timeout_cannot_qualify_a_long_watch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, raw = Path(temporary), Path(temporary) / "raw"
            raw.mkdir()
            contract = {"NVDISASM": "nvdisasm", "C16_NVBIT_NVDISASM_ABSOLUTE_PATH": "/usr/local/cuda-12.4/bin/nvdisasm", "PATH": "/usr/local/cuda-12.4/bin:/usr/bin"}
            gate_b = {"status": "NVBIT_OFFICIAL_VECTORADD_SMOKE_PASS", "runtime_code_commit": RUNTIME_COMMIT, "tool": {"sha256": OFFICIAL_TOOL_SHA}, "official_instrumentation_evidence": {"banner": True}, "nvdisasm_environment_contract": contract}
            gate_c = {"mode": "NVBIT_PATH_SMOKE", "runtime_code_commit": RUNTIME_COMMIT, "wall_limit_seconds": 60, "terminal_status": "BOUNDED_TIMEOUT_NO_FIRST_KERNEL", "first_cuda_kernel_completed_elapsed_seconds": None, "tool_evidence_marker_observed": False, "trace_generated": False, "raw_trace_bytes": 0, "status": "NVBIT_PYTORCH_EXTREME_STARTUP_OVERHEAD"}
            for name in REQUIRED_RAW:
                path = raw / name
                if name == "GATE_A_NVDISASM_VERSION.log":
                    path.write_text("resolved=/usr/local/cuda-12.4/bin/nvdisasm\nCuda compilation tools, release 12.4", encoding="utf-8")
                elif name == "ENVIRONMENT_AUDIT_POST_GATE.log":
                    path.write_text("NVIDIA GeForce RTX 3090\n570.124.04\n/usr/local/cuda-12.4/bin/nvdisasm\nCUDA version:\nCUDA driver version:", encoding="utf-8")
                elif name == "GATE_B_OFFICIAL_NVBIT_RECEIPT.json":
                    path.write_text(json.dumps(gate_b), encoding="utf-8")
                elif name == "GATE_C_RUNTIME_FIRST_KERNEL_RECEIPT.json":
                    path.write_text(json.dumps(gate_c), encoding="utf-8")
                elif name == "GATE_C_RUNTIME_FIRST_KERNEL_STDOUT.log":
                    path.write_text('NVBit (NVidia Binary Instrumentation Tool v1.8) Loaded\nFIRST_CUDA_KERNEL_SUBMISSION_BEGIN\nC16_LONG_WATCH_STAGE {"runtime_identity":{"torch_version":"2.5.1+cu124"}}', encoding="utf-8")
                else:
                    path.write_text("diagnostic", encoding="utf-8")
            ledger = root / "ledger.json"
            ledger.write_text(json.dumps({"entries": [
                {"operation_kind": "NVBIT_OFFICIAL_VECTORADD_SMOKE_DIAGNOSTIC", "raw_bytes": 0, "evidence_classification": "NON_SCIENTIFIC_DIAGNOSTIC"},
                {"operation_kind": "NVBIT_PATH_SMOKE_DIAGNOSTIC", "raw_bytes": 0, "evidence_classification": "NON_SCIENTIFIC_DIAGNOSTIC"},
            ]}), encoding="utf-8")
            directory = root / "publish"
            write(directory, raw, ledger)
            self.assertEqual(validate(directory)["status"], "PASS")
            receipt = json.loads((directory / "NVBIT_NVDISASM_PATH_REPAIR_RECEIPT.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["status"], STATUS)
            self.assertEqual(receipt["formal_long_watch_reapplication"], "NOT_QUALIFIED")


if __name__ == "__main__":
    unittest.main()
