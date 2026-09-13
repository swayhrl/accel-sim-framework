#!/usr/bin/env python3
"""CPU-only structural tests for the one-shot Retry570 long-watch harness."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from c16_native_common import ContractError  # noqa: E402
from retry570_long_watch import (  # noqa: E402
    BASELINE_SECONDS,
    LONG_WATCH_SECONDS,
    PATH_SMOKE_SECONDS,
    SAMPLE_SECONDS,
    classify_timeout,
    nvdisasm_environment_contract,
    reserve_long_watch,
    timeout_status,
    validate_mode,
)


class Retry570LongWatchTests(unittest.TestCase):
    def test_long_watch_is_exactly_one_300_second_nonbaseline_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            authorization = Path(temporary) / "one.json"
            validate_mode("NVBIT_LONG_WATCH", LONG_WATCH_SECONDS, SAMPLE_SECONDS, authorization)
            with self.assertRaises(ContractError):
                validate_mode("NVBIT_LONG_WATCH", 60, SAMPLE_SECONDS, authorization)
            with self.assertRaises(ContractError):
                validate_mode("BASELINE", BASELINE_SECONDS, SAMPLE_SECONDS, authorization)
            validate_mode("BASELINE", BASELINE_SECONDS, SAMPLE_SECONDS, None)
            validate_mode("NVBIT_PATH_SMOKE", PATH_SMOKE_SECONDS, SAMPLE_SECONDS, None)
            with self.assertRaises(ContractError):
                validate_mode("NVBIT_PATH_SMOKE", LONG_WATCH_SECONDS, SAMPLE_SECONDS, None)

    def test_nvdisasm_contract_requires_absolute_executable_and_prefixes_child_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "cuda-bin" / "nvdisasm"
            binary.parent.mkdir()
            binary.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            binary.chmod(0o755)
            contract = nvdisasm_environment_contract(binary, "/usr/bin:/bin")
            self.assertEqual(contract["NVDISASM"], "nvdisasm")
            self.assertEqual(contract["C16_NVBIT_NVDISASM_ABSOLUTE_PATH"], str(binary))
            self.assertEqual(contract["PATH"].split(":")[0], str(binary.parent))
            with self.assertRaises(ContractError):
                nvdisasm_environment_contract(Path("nvdisasm"), "/usr/bin")

    def test_one_shot_reservation_refuses_a_second_long_watch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "one.json"
            reserve_long_watch(path, {"status": "RESERVED"})
            with self.assertRaises(ContractError):
                reserve_long_watch(path, {"status": "SECOND"})

    def test_timeout_classification_requires_observed_progress_for_extreme_overhead(self) -> None:
        stalled = [{"process_state_wchan": "10 0.0 S futex_wait"} for _ in range(12)]
        self.assertEqual(
            classify_timeout(stalled, [{"stage": "PROCESS_START"}, {"stage": "CUDA_AVAILABLE_CONFIRMED"}]),
            "NVBIT_PYTORCH_PRE_FIRST_KERNEL_STALL_CONFIRMED",
        )
        busy = [{"process_state_wchan": "10 99.0 R -"} for _ in range(12)]
        self.assertEqual(
            classify_timeout(busy, [{"stage": "PROCESS_START"}, {"stage": "CUDA_AVAILABLE_CONFIRMED"}]),
            "NVBIT_PYTORCH_EXTREME_STARTUP_OVERHEAD",
        )
        self.assertEqual(
            timeout_status("NVBIT_PATH_SMOKE", busy, [{"stage": "PROCESS_START"}]),
            "NVBIT_PATH_SMOKE_TIMEOUT_BEFORE_FIRST_KERNEL",
        )


if __name__ == "__main__":
    unittest.main()
