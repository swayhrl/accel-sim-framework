#!/usr/bin/env python3
"""No-GPU contract tests for the explicit AutoAWQ runtime-native path."""
from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from c16_native_common import ContractError  # noqa: E402
from model_adapters import resolve_adapter  # noqa: E402
from runtime_native_runner import assert_cuda_residency, is_cuda_oom, load_runtime_model, resource_admission_receipt  # noqa: E402


class FakeDevice:
    type = "cuda"


class FakeTensor:
    device = FakeDevice()
    dtype = "torch.int32"

    def numel(self) -> int:
        return 1


class FakeModel:
    def __init__(self) -> None:
        self.evaluated = False

    def eval(self):
        self.evaluated = True
        return self

    def parameters(self):
        return [FakeTensor()]

    def named_buffers(self):
        return [("quant_scale", FakeTensor())]


class FakeAwqLoader:
    calls: list[tuple[str, dict[str, object]]] = []

    @classmethod
    def from_quantized(cls, path: str, **kwargs):
        cls.calls.append((path, kwargs))
        return types.SimpleNamespace(model=FakeModel())


class FakeTorch:
    float16 = "float16"
    bfloat16 = "bfloat16"


class AwqRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.previous_awq = sys.modules.get("awq")
        sys.modules["awq"] = types.SimpleNamespace(AutoAWQForCausalLM=FakeAwqLoader)
        FakeAwqLoader.calls = []

    def tearDown(self) -> None:
        if self.previous_awq is None:
            del sys.modules["awq"]
        else:
            sys.modules["awq"] = self.previous_awq

    def test_awq_load_is_explicit_no_offload_and_shape_bound(self) -> None:
        adapter = resolve_adapter("qwen25_7b_awq", "float16", "AWQ")
        model, evidence = load_runtime_model(
            adapter, Path("/immutable/awq"), FakeTorch(), "float16", required_sequence_length=8200,
        )
        self.assertTrue(model.evaluated)
        self.assertEqual(FakeAwqLoader.calls, [("/immutable/awq", {
            "max_seq_len": 8200, "fuse_layers": False, "trust_remote_code": False,
            "safetensors": True, "device_map": "cuda:0",
        })])
        self.assertEqual(evidence["quantization_implementation"], "AUTOAWQ_FROM_QUANTIZED_FUSE_FALSE")
        self.assertTrue(evidence["cpu_offload_forbidden"])
        _devices, dtypes = assert_cuda_residency(model, require_raw_dtype=None)
        self.assertEqual(dtypes, {"int32"})

    def test_awq_packed_dtype_cannot_be_treated_as_raw_float16(self) -> None:
        model = FakeModel()
        with self.assertRaises(ContractError):
            assert_cuda_residency(model, require_raw_dtype="float16")

    def test_cuda_oom_is_an_explicit_no_substitution_resource_result(self) -> None:
        class OutOfMemoryError(RuntimeError):
            pass

        error = OutOfMemoryError("CUDA out of memory")
        self.assertTrue(is_cuda_oom(error))
        self.assertFalse(is_cuda_oom(RuntimeError("ordinary loader failure")))
        receipt = resource_admission_receipt({"run_id": "unit", "deployment_id": "unit"}, types.SimpleNamespace(), error)
        self.assertEqual(receipt["status"], "SKIPPED_RESOURCE")
        self.assertFalse(receipt["scientific_eligible"])
        self.assertTrue(receipt["constraints"]["cpu_offload_forbidden"])
        self.assertTrue(receipt["constraints"]["frozen_context_batch_decode_unchanged"])


if __name__ == "__main__":
    unittest.main()
