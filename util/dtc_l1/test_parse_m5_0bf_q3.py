#!/usr/bin/env python3
"""Regression coverage for the complete-metrics M5.0BF Q3 extractor."""

import gzip
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("parse_m5_0bf_q3.py")


def terminal_log(include_cycle_sum=True):
    values = {
        "gpu_tot_sim_cycle": 100,
        "gpu_tot_sim_insn": 250,
        "DTC_L1_lower_outstanding_cap": 10240,
        "DTC_L1_lower_outstanding_peak": 40,
        "DTC_L1_lower_outstanding_cycle_sum": 1500,
        "DTC_L1_lower_outstanding_sample_cycles": 100,
        "DTC_L1_lower_cap_full_events": 12,
        "DTC_L1_nonexclusive_lower_cap_full_cycles": 7,
        "DTC_L1_pib_full_events": 3,
        "DTC_L1_nonexclusive_pib_full_cycles": 2,
        "DTC_L1_nonexclusive_mshr_entry_full_cycles": 4,
        "DTC_L1_nonexclusive_mshr_merge_full_cycles": 5,
        "DTC_L1_baseline_l1d_line_allocation_fail_events": 6,
        "DTC_L1_nonexclusive_tag_bank_conflict_cycles": 8,
        "gpu_stall_dramfull": 9,
    }
    if not include_cycle_sum:
        values.pop("DTC_L1_lower_outstanding_cycle_sum")
    return "".join("%s = %s\n" % item for item in values.items())


class ParseM50BFQ3Tests(unittest.TestCase):
    def write_fixture(self, directory, include_cycle_sum=True):
        log = directory / "m5_run.log"
        log.write_text(terminal_log(include_cycle_sum), encoding="utf-8")
        perf = directory / "perf.csv.gz"
        with gzip.open(perf, "wt", encoding="utf-8", newline="") as fh:
            fh.write("chiplet_queue_full_0,L2_dram_queue_full_0\n")
            fh.write("11,12\n")
        config = directory / "config"
        workload = directory / "workload"
        config.write_text("config\n", encoding="utf-8")
        workload.write_text("workload\n", encoding="utf-8")
        return log, perf, config, workload

    def command(self, log, perf, output, config, workload):
        return [
            sys.executable, str(SCRIPT), "--log", str(log), "--perf-counter",
            str(perf), "--output", str(output), "--candidate", "fixture",
            "--core-sha", "core", "--framework-sha", "framework",
            "--config-file", str(config), "--workload-file", str(workload),
        ]

    def test_complete_metrics_v2(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            log, perf, config, workload = self.write_fixture(directory)
            output = directory / "out.json"
            subprocess.run(self.command(log, perf, output, config, workload),
                           check=True, capture_output=True, text=True)
            result = json.loads(output.read_text(encoding="utf-8"))
            metrics = result["metrics"]
            self.assertEqual("dtc_l1_m5_0bf_q3_v2", result["schema"])
            self.assertEqual(2.5, metrics["base_ipc"])
            self.assertEqual(15.0, metrics["lower_outstanding_average"])
            self.assertEqual(7, metrics["lower_cap_full_cycles"])
            self.assertEqual(12, metrics["lower_cap_full_events"])
            self.assertEqual(6, metrics["true_tag_cacheline_allocation_fail_events"])

    def test_rejects_missing_complete_metrics_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            log, perf, config, workload = self.write_fixture(directory, False)
            output = directory / "out.json"
            completed = subprocess.run(
                self.command(log, perf, output, config, workload),
                capture_output=True, text=True)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("DTC_L1_lower_outstanding_cycle_sum", completed.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
