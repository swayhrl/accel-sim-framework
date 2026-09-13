from __future__ import annotations
import unittest
from pathlib import Path

SOURCE = (Path(__file__).parent / "retry570_multimodel_model_worker.py").read_text()

class MultimodelWorkerTests(unittest.TestCase):
    def test_s1_is_the_exact_frozen_llama_workload(self) -> None:
        for token in ("S0/B1/T128/decode4", "meta-llama/Llama-3.2-1B", "4e20de362430cd3b72f300e6b0f18e50e7166e08", "decode_once(model, prompt, 4"):
            self.assertIn(token, SOURCE)

    def test_s1_cannot_arm_measurement_or_emit_trace(self) -> None:
        for token in ("NO_TRACE_RANGE", "MeasurementActive.assert_available", "S1 no-trace workload emitted a trace", "measurement_active_created\": False"):
            self.assertIn(token, SOURCE)

    def test_s2_requires_an_exact_function_and_fresh_nvbit_native_map(self) -> None:
        for token in ("S2_STATIC_MAP", "C16_NVBIT_TARGET_FUNCTION_MANGLED", "S2 exact-function mapper emitted no static map"):
            self.assertIn(token, SOURCE)

    def test_no_cpu_or_identity_fallback(self) -> None:
        for token in ("refusing CPU fallback", "assert_cuda_residency", "runtime source commit differs"):
            self.assertIn(token, SOURCE)

if __name__ == "__main__": unittest.main()
