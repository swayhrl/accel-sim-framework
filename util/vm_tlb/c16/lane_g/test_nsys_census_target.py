#!/usr/bin/env python3
"""No-GPU contract tests for frozen full-range G1 discovery targets."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from c16_native_common import ContractError  # noqa: E402
from nsys_census_target import target_from_binding  # noqa: E402
from runtime_native_runner import git_head  # noqa: E402


COMMIT = git_head()
RUN_ID = "123e4567-e89b-12d3-a456-426614174000"


def binding() -> dict:
    return {
        "model_id": "unit/model", "model_revision": "b" * 40,
        "tokenizer_revision": "c" * 40, "deployment_id": "unit-deployment",
        "scenario": {"scenario_id": "S2", "batch_size": 1, "prefill_tokens": 2048, "decode_tokens": 32},
        "input": {"raw_input_sha256": "d" * 64},
    }


def receipt() -> dict:
    return {
        "execution_mode": "NATIVE_GPU", "scientific_eligible": True,
        "identity": {
            "model_id": "unit/model", "model_revision": "b" * 40,
            "tokenizer_revision": "c" * 40, "deployment_id": "unit-deployment",
            "implementation_key": "UNIT_IMPL", "dtype": "float16", "quantization": "NONE",
            "scenario_id": "S2", "input_hash": "d" * 64,
            "run_id": "123e4567-e89b-12d3-a456-426614174999", "code_commit": COMMIT,
        },
        "runtime": {
            "device": "cuda:0", "gpu_uuid": "GPU-unit", "driver_version": "unit",
            "cuda_version": "12.4", "torch_version": "unit", "attention_backend": "DIRECT",
            "compile_state": "EAGER_UNCOMPILED",
        },
        "checks": {
            "model_all_cuda": True, "input_all_cuda": True, "cache_correct_decode": True,
            "adapter_load_evidence": {"cpu_offload_forbidden": True},
        },
        "artifacts": {"terminal_status": "COMPLETE"},
    }


class NsysCensusTargetTests(unittest.TestCase):
    def test_builds_conservative_full_range_target(self) -> None:
        target = target_from_binding(binding(), receipt(), run_id=RUN_ID, adapter="unit", implementation_key="UNIT_IMPL", dtype="float16", quantization="NONE")
        self.assertEqual(target["shape_key"], "B1_T2048_D32")
        self.assertEqual(target["kernel_name"], "NSYS_FULL_FROZEN_SCENARIO_CENSUS_REGION")
        self.assertEqual(target["operator_class"], "UNKNOWN_PRE_CENSUS")
        self.assertEqual(target["identity"]["run_id"], RUN_ID)
        self.assertEqual(target["runtime"]["profiler_mode"], "NSYS_LIGHTWEIGHT_CENSUS_PARENT_LEASED")

    def test_rejects_source_identity_mismatch(self) -> None:
        source = receipt()
        source["identity"]["model_revision"] = "e" * 40
        with self.assertRaises(ContractError):
            target_from_binding(binding(), source, run_id=RUN_ID, adapter="unit", implementation_key="UNIT_IMPL", dtype="float16", quantization="NONE")


if __name__ == "__main__":
    unittest.main()
