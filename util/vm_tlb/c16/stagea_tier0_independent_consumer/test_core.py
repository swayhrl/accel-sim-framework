import math
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

from core import (
    Interval, TimingSample, attach_by_correlation, audit_raw_file, audit_raw_index, chronological_gaps, dq2_batch_matched_graph_control, headroom_gate,
    matched_graph_absorption, sample_statistics, union_length_ns,
    validate_coverage, recompute_timing,
)


class Tier0CoreTests(unittest.TestCase):
    def setUp(self):
        self.parent = Interval(0, 100, "parent")

    def test_overlap_sum_is_not_union(self):
        xs = [Interval(0, 40, "a"), Interval(20, 50, "b")]
        self.assertEqual(sum(x.duration_ns for x in xs), 70)
        self.assertEqual(union_length_ns(xs, self.parent), 50)

    def test_nonoverlap_and_clipping(self):
        xs = [Interval(-5, 10, "a"), Interval(20, 30, "b")]
        self.assertEqual(union_length_ns(xs, self.parent), 20)

    def test_zero_length_and_reversed(self):
        self.assertEqual(union_length_ns([Interval(3, 3, "zero")], self.parent), 0)
        with self.assertRaises(ValueError):
            Interval(5, 4, "bad")

    def test_signed_launch_gap_and_overlap(self):
        xs = [Interval(0, 40, "a"), Interval(30, 50, "b"), Interval(70, 80, "c")]
        rows = chronological_gaps(xs, self.parent)
        self.assertEqual([r["signed_gap_ns"] for r in rows], [-10, 20])
        self.assertEqual([r["classification"] for r in rows], ["OVERLAP", "GAP"])

    def test_correlation_required_not_time_overlap(self):
        with self.assertRaises(ValueError):
            attach_by_correlation([Interval(0, 5, "kernel0")], {}, {"range0"})
        self.assertEqual(len(attach_by_correlation([Interval(0, 5, "kernel0")], {"kernel0": "range0"}, {"range0"})["range0"]), 1)

    def test_missing_nsys_and_partial_point(self):
        self.assertEqual(union_length_ns([], self.parent), 0)
        self.assertEqual(validate_coverage({"MP01", "MP02"}, "STAGEA_TIER0_PRODUCER_PARTIAL"), {
            "DQ1": "READY", "DQ2": "QUESTION_INCOMPLETE", "DQ3": "QUESTION_INCOMPLETE", "DQ4a": "READY"
        })
        with self.assertRaises(ValueError):
            validate_coverage({"MP08"}, "STAGEA_TIER0_PRODUCER_PARTIAL")

    def test_samples(self):
        self.assertEqual(sample_statistics([1, 2, 9])["median"], 2)
        self.assertEqual(sample_statistics([1, 2, 9])["spread"], 8)
        with self.assertRaises(ValueError):
            sample_statistics([1, math.nan])
        with self.assertRaises(ValueError):
            sample_statistics([])

    def test_headroom_gates(self):
        self.assertEqual(headroom_gate(2, 100)["status"], "STOPPED_BY_HEADROOM")
        self.assertIsNone(headroom_gate(2, 100)["below_2pct_zero_ceiling_gate"])
        self.assertEqual(headroom_gate(3, 100)["status"], "SURVIVES_HEADROOM_SCREEN")
        self.assertAlmostEqual(headroom_gate(20, 100)["s_zero_graph_off_screen"], 1.25)
        self.assertEqual(headroom_gate(20, 100)["whole_run_ceiling_status"], "WHOLE_RUN_CEILING_NOT_IDENTIFIABLE")
        self.assertTrue(headroom_gate(20, 100, comparable_whole_run_fraction=0.01)["below_2pct_zero_ceiling_gate"])
        self.assertIsNone(headroom_gate(100, 100)["s_zero_graph_off_screen"])
        with self.assertRaises(ValueError):
            headroom_gate(101, 100)

    def test_graph_matched_only(self):
        self.assertEqual(matched_graph_absorption(10, 1.5, commensurate=True)["status"], "STOP_DIRECTION")
        self.assertEqual(matched_graph_absorption(10, 1.6, commensurate=True)["status"], "NOT_STOPPED_BY_GRAPH_CONTROL")
        self.assertEqual(matched_graph_absorption(10, 1, commensurate=False)["status"], "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE")
        self.assertEqual(matched_graph_absorption(0, 1, commensurate=True)["status"], "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE")

    def test_exact_dq2_matched_estimator(self):
        m = {("MP02", "OFF"): 64.0, ("MP03", "OFF"): 128.0,
             ("MP02", "ON"): 32.0, ("MP03", "ON"): 115.2}
        n = {k: 3 for k in m}
        result = dq2_batch_matched_graph_control(m, n, identity_ok=True)
        self.assertAlmostEqual(result["G_off_ms_per_token"], 1.0)
        self.assertAlmostEqual(result["G_on_ms_per_token"], 0.1)
        self.assertEqual(result["status"], "STOP_DIRECTION")
        self.assertEqual(dq2_batch_matched_graph_control(m, n | {("MP02", "OFF"): 2}, identity_ok=True)["status"], "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE")
        self.assertEqual(dq2_batch_matched_graph_control(m, n, identity_ok=False)["status"], "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE")

    def test_raw_integrity_and_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "raw.bin"
            path.write_bytes(b"raw-cpu-fixture")
            digest = sha256(path.read_bytes()).hexdigest()
            self.assertEqual(audit_raw_file(str(path), path.stat().st_size, digest, temp)["status"], "PASS")
            self.assertEqual(audit_raw_file(str(path), 1, digest, temp)["status"], "FAIL")
            with tempfile.TemporaryDirectory() as other:
                with self.assertRaises(ValueError):
                    audit_raw_file(str(path), path.stat().st_size, digest, other)

    def test_raw_index_schema_and_duplicate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = root / "RAW.tsv"
            data.write_bytes(b"a\tb\n")
            digest = sha256(data.read_bytes()).hexdigest()
            index = root / "RAW_INDEX.tsv"
            header = "artifact\tnode109_path\tbytes\tsha256\tnode164_path\n"
            entry = f"RAW.tsv\t/data/raw/RAW.tsv\t4\t{digest}\t{data}\n"
            index.write_text(header + entry, encoding="utf-8")
            self.assertEqual(audit_raw_index(str(index), temp)[0]["status"], "PASS")
            index.write_text(header + entry + entry, encoding="utf-8")
            with self.assertRaises(ValueError):
                audit_raw_index(str(index), temp)

    def test_native_timing_only_instrumentation_off(self):
        base = dict(point_id="MP02", input_sha256="a" * 64, output_sha256="b" * 64,
                    batch=1, effective_m=1, backend="fast", shape="1x64x64")
        samples = [TimingSample(graph_mode="OFF", instrumentation="OFF", repetition=i,
                                duration_ms=t, **base) for i, t in enumerate([1.0, 2.0, 4.0])]
        samples.append(TimingSample(graph_mode="OFF", instrumentation="ON", repetition=0,
                                    duration_ms=100.0, **base))
        rows = recompute_timing(samples, {"MP02"})
        self.assertEqual(rows[0]["sample_count"], 3)
        self.assertEqual(rows[0]["median"], 2.0)
        with self.assertRaises(ValueError):
            recompute_timing(samples + [samples[0]], {"MP02"})
        with self.assertRaises(ValueError):
            recompute_timing(samples + [TimingSample(graph_mode="ON", instrumentation="OFF", repetition=0,
                duration_ms=2.0, **(base | {"output_sha256": "c" * 64}))], {"MP02"})


if __name__ == "__main__":
    unittest.main()
