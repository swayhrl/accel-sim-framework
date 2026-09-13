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
    SAMPLE_SECONDS,
    classify_timeout,
    reserve_long_watch,
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


if __name__ == "__main__":
    unittest.main()
