#!/usr/bin/env python3
"""Small schema/64-slice fail-closed checks for parse_epl2_m0a.py."""
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PARSER = ROOT / "util/ep_l2/parse_epl2_m0a.py"
FIELDS = {
    "resident_samples": 5000,
    "m0_resident_payload_occupied_sum": 0,
    "m0_resident_payload_free_sum": 5120000,
    "m0_resident_payload_occupied_avg": 0,
    "m0_resident_payload_free_avg": 1024,
    "m0_resident_payload_occupied_max": 0,
    "m0_resident_payload_free_min": 1024,
    "m0_frontend_head_observed_cycles": 1,
    "m0_frontend_head_any_blocked_cycles": 0,
    "m0_frontend_head_blocked_cycles_tag_way": 0,
    "m0_frontend_head_blocked_cycles_wad_full": 0,
    "m0_frontend_head_blocked_cycles_wad_hazard": 0,
    "m0_frontend_head_blocked_cycles_line_mshr": 0,
    "m0_frontend_head_blocked_cycles_descriptor": 0,
    "m0_frontend_head_blocked_cycles_per_address": 0,
    "m0_frontend_head_blocked_cycles_missq": 0,
    "m0_frontend_head_blocked_cycles_payload_service": 0,
    "m0_frontend_head_blocked_cycles_payload_capacity": 0,
    "m0_frontend_head_blocked_cycles_lowerq": 0,
    "m0_frontend_head_blocked_cycles_responseq": 0,
    "m0_useful_frontend_admit": 1,
    "m0_useful_response_enqueue": 1,
}


def row(scope, slice_id):
    fields = {"scope": scope,
              "interval": "5000_cycle" if scope == "window" else "application_cumulative",
              "slice": slice_id, "kernel_uid": 0, "start_cycle": 0,
              "completion_cycle": 5000, **FIELDS}
    return "EPL2M0AV1|" + "|".join("%s=%s" % item for item in fields.items()) + "\n"


class ParseM0aTest(unittest.TestCase):
    def invoke(self, text):
        root = Path(tempfile.mkdtemp())
        log, out = root / "raw.log", root / "out"
        log.write_text(text)
        return subprocess.run(("python3", str(PARSER), str(log), "--out", str(out)), text=True,
                              capture_output=True), out

    def test_complete_64_slice_stream_passes(self):
        text = "".join(row("application", i) + row("window", i) for i in range(64))
        result, out = self.invoke(text)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((out / "m0a_summary.csv").is_file())

    def test_incomplete_stream_fails_closed(self):
        result, _ = self.invoke("".join(row("application", i) for i in range(63)))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("64 terminal", result.stderr)


if __name__ == "__main__":
    unittest.main()
