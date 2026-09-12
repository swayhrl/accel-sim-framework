#!/usr/bin/env python3
"""No-GPU unit tests for direct runtime semantic instrumentation and mapping."""
from __future__ import annotations

import sqlite3
import sys
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from direct_semantic_map import kernel_rows, parse_direct_tag  # noqa: E402
from direct_semantic_runtime import TAG_PREFIX, direct_module_semantic  # noqa: E402
from run_schema import validate_receipt  # noqa: E402


IDENTITY = {"run_id": "123e4567-e89b-12d3-a456-426614174000", "deployment_id": "unit-deployment", "scenario_id": "S2"}


class DirectSemanticTests(unittest.TestCase):
    def test_module_path_classification_is_direct_and_conservative(self) -> None:
        q = direct_module_semantic("model.layers.7.self_attn.q_proj", "Linear")
        self.assertIsNotNone(q)
        self.assertEqual((q.layer_id, q.operator, q.operator_detail), ("7", "ATTENTION", "Q_PROJ"))
        ffn = direct_module_semantic("model.layers.7.mlp.down_proj", "Linear")
        self.assertEqual((ffn.layer_id, ffn.operator, ffn.operator_detail), ("7", "FFN", "DOWN"))
        self.assertEqual(direct_module_semantic("model.layers.7.unknown_linear", "Linear"), None)
        self.assertEqual(direct_module_semantic("model.layers.0.self_attn.q_proj", "Linear").operator, "ATTENTION")

    def test_temporal_mapping_uses_direct_tag_not_kernel_name(self) -> None:
        tag = "|".join((TAG_PREFIX, "run_id=" + IDENTITY["run_id"], "deployment_id=unit-deployment", "scenario_id=S2", "layer_id=7", "operator=ATTENTION", "operator_detail=Q_PROJ", "module_path=model.layers.7.self_attn.q_proj", "module_class=Linear"))
        self.assertIsNotNone(parse_direct_tag(tag, IDENTITY))
        connection = sqlite3.connect(":memory:")
        connection.executescript("""
            CREATE TABLE NVTX_EVENTS(start INTEGER, end INTEGER, text TEXT);
            CREATE TABLE CUPTI_ACTIVITY_KIND_KERNEL(start INTEGER, end INTEGER, deviceId INTEGER, contextId INTEGER, streamId INTEGER, correlationId INTEGER, gridX INTEGER, gridY INTEGER, gridZ INTEGER, blockX INTEGER, blockY INTEGER, blockZ INTEGER, demangledName INTEGER);
            CREATE TABLE StringIds(id INTEGER, value TEXT);
        """)
        connection.execute("INSERT INTO NVTX_EVENTS VALUES (0, 100, 'C16_PHASE_PREFILL')")
        connection.execute("INSERT INTO NVTX_EVENTS VALUES (20, 80, ?)", (tag,))
        connection.execute("INSERT INTO StringIds VALUES (1, 'a kernel name that must not classify semantics')")
        connection.execute("INSERT INTO CUPTI_ACTIVITY_KIND_KERNEL VALUES (30, 40, 0, 1, 2, 3, 1, 1, 1, 32, 1, 1, 1)")
        connection.execute("INSERT INTO CUPTI_ACTIVITY_KIND_KERNEL VALUES (110, 120, 0, 1, 2, 4, 1, 1, 1, 32, 1, 1, 1)")
        rows, range_count, ambiguity = kernel_rows(connection, IDENTITY, source_run_sha="a" * 64, source_profile_sha="b" * 64, source_manifest_sha="c" * 64)
        self.assertEqual((range_count, ambiguity), (1, 0))
        self.assertEqual(rows[0]["mapping_status"], "DIRECT_UNAMBIGUOUS")
        self.assertEqual(rows[0]["operator"], "ATTENTION")
        self.assertEqual(rows[0]["evidence_type"], "DIRECT_MODULE_ID")
        self.assertEqual(rows[0]["nvtx_evidence_type"], "DIRECT_RUNTIME_NVTX")
        self.assertEqual(rows[1]["mapping_status"], "UNKNOWN_CONSERVATIVE")
        self.assertEqual(rows[1]["operator"], "UNKNOWN")

    def test_native_diagnostic_receipt_cannot_be_promoted_to_timing_evidence(self) -> None:
        receipt = {
            "schema_version": "C16_G_NATIVE_RECEIPT_V1", "stage_id": "C16-SEMANTIC-1",
            "execution_mode": "NATIVE_GPU", "scientific_eligible": False,
            "identity": {
                "model_id": "unit/model", "model_revision": "a" * 40, "tokenizer_revision": "b" * 40,
                "deployment_id": "unit-deployment", "implementation_key": "TEST", "dtype": "float16",
                "quantization": "NONE", "scenario_id": "S2", "input_hash": "c" * 64,
                "run_id": IDENTITY["run_id"], "code_commit": "d" * 40,
            },
            "runtime": {
                "device": "cuda:0", "gpu_uuid": "GPU-unit", "driver_version": "unit", "cuda_version": "12.4",
                "torch_version": "unit", "attention_backend": "DIRECT", "compile_state": "EAGER_UNCOMPILED",
                "profiler_mode": "NSYS_DIRECT_SEMANTIC_DIAGNOSTIC",
            },
            "checks": {}, "artifacts": {},
        }
        validate_receipt(receipt, allow_native_diagnostic=True)
        with self.assertRaises(Exception):
            validate_receipt(receipt, require_native=True)


if __name__ == "__main__":
    unittest.main()
