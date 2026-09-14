#!/usr/bin/env python3
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c16_analysis import AnalysisError, fingerprint, normalize_record, object_join, parse_route_b


def raw(address=4095, width=2, kind="READ", mask=3):
    return {"record_kind":"LANE_EVENT", "raw_schema":"C16_ROUTE_B_LANE_EVENT_V1", "access_kind":kind,
            "gpu_va":address, "width_bytes":width, "active_mask":mask, "lane_id":0, "kernel_launch_id":0}


class C16AnalysisTests(unittest.TestCase):
    def test_page_line_and_crossing(self):
        stats = fingerprint([normalize_record(raw(4095, 2), "x"), normalize_record(raw(65535, 2), "x")])
        self.assertEqual(stats["unique_4k_pages"], 4)
        self.assertEqual(stats["unique_64k_pages"], 2)
        self.assertEqual(stats["unique_128b_lines"], 4)

    def test_access_and_active_mask(self):
        stats = fingerprint([normalize_record(raw(1, 4, "READ", 1), "x"), normalize_record(raw(2, 4, "WRITE", 0), "x"), normalize_record(raw(3, 4, "ATOMIC", 7), "x")])
        self.assertEqual(stats["access_counts"], {"ATOMIC": 1, "READ": 1, "WRITE": 1})
        self.assertEqual(stats["active_lane_distribution"], {"0": 1, "1": 1, "3": 1})

    def test_object_alias_priority_and_unknown(self):
        rec = normalize_record(raw(100), "x")
        self.assertEqual(object_join(rec, [])["object_class"], "UNKNOWN_RUNTIME")
        joined = object_join(rec, [{"start": 0, "end": 200, "object_class": "KV_CACHE", "object_id": "z"}, {"start": 0, "end": 200, "object_class": "WEIGHT", "object_id": "a"}])
        self.assertEqual(joined["object_class"], "WEIGHT")

    def test_empty_partial_and_deterministic_parse(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / "raw.jsonl"; out = root / "out.jsonl"
            source.write_text(json.dumps(raw(1)) + "\n" + json.dumps(raw(2, kind="WRITE")) + "\n", encoding="utf-8")
            first = parse_route_b(source, "x", out); first_text = out.read_text(encoding="utf-8")
            second = parse_route_b(source, "x", out)
            self.assertEqual(first, second); self.assertEqual(first_text, out.read_text(encoding="utf-8"))
            source.write_text("", encoding="utf-8")
            with self.assertRaises(AnalysisError): parse_route_b(source, "x", out)

    def test_complete_terminal_is_accepted_and_bad_terminal_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / "raw.jsonl"; out = root / "out.jsonl"
            source.write_text(json.dumps(raw(1)) + "\n" + json.dumps({"record_kind":"TERMINAL", "terminal_status":"COMPLETE", "event_count":1, "overflow_count":0, "drop_count":0}) + "\n", encoding="utf-8")
            self.assertEqual(parse_route_b(source, "x", out)["lane_events"], 1)
            source.write_text(json.dumps(raw(1)) + "\n" + json.dumps({"record_kind":"TERMINAL", "terminal_status":"COMPLETE", "event_count":2, "overflow_count":0, "drop_count":0}) + "\n", encoding="utf-8")
            with self.assertRaises(AnalysisError): parse_route_b(source, "x", out)


if __name__ == "__main__":
    unittest.main()
