import unittest

from crosscheck import compare_handoff_boundaries, compare_headroom_summary, compare_launch_gaps, compare_native_summary


class CrosscheckTests(unittest.TestCase):
    def test_launch_and_handoff_exact(self):
        own = {"MP01": {
            "global_launch_gaps": [{"predecessor": "1", "successor": "2", "positive_gap_ns": 5,
                                    "gap_start_ns": 10, "gap_end_ns": 15}],
            "sibling_boundaries": [{"producer_ordinal": "0", "consumer_ordinal": "1",
                                    "signed_gap_ns": 5, "parent_cuda_union_ns": 100}],
        }}
        producer_gaps = [{"point_id": "MP01", "preceding_cuda_interval_id": "1",
                          "following_cuda_interval_id": "2", "gap_duration_ns": "5",
                          "gap_start_ns": "10", "gap_end_ns": "15"}]
        producer_boundaries = [{"point_id": "MP01", "producer_ordinal": "0",
                                "consumer_ordinal": "1", "boundary_gap_ns": "5",
                                "boundary_gap_parent_cuda_union_fraction": "0.05"}]
        self.assertEqual({r["status"] for r in compare_launch_gaps(own, producer_gaps, {"MP01"})}, {"MATCH"})
        self.assertEqual({r["status"] for r in compare_handoff_boundaries(own, producer_boundaries, {"MP01"})}, {"MATCH"})

    def test_headroom_display_match(self):
        own = [{"point_id": "MP01", "family": "ATTENTION", "candidate_graph_off_union_ns": 20,
                "parent_graph_off_cuda_union_ns": 100, "f_graph_off": 0.2,
                "s_zero_graph_off_screen": 1.25}]
        producer = [{"point_id": "MP01", "question_id": "DQ1", "candidate_id": "ATTENTION",
                     "graph_off_candidate_union_ns": "20", "graph_off_parent_cuda_union_ns": "100",
                     "f_graph_off": "0.2", "s_zero_graph_off_screen": "1.25"}]
        self.assertEqual({r["status"] for r in compare_headroom_summary(own, producer, {"MP01"})}, {"MATCH"})

    def test_match_and_mismatch(self):
        own = [{"point_id": "MP02", "arm": "GRAPH_ON_NATIVE", "cuda_sample_count": 3,
                "cuda_median": 2.0, "cuda_min": 1.0, "cuda_max": 3.0}]
        producer = [{"point_id": "MP02", "arm": "GRAPH_ON_NATIVE", "measured_n": "3",
                     "median_request_cuda_event_ms": "2.0", "minimum_request_cuda_event_ms": "1.0",
                     "maximum_request_cuda_event_ms": "3.0"}]
        self.assertEqual({r["status"] for r in compare_native_summary(own, producer, {"MP02"})}, {"MATCH"})
        bad = [{**producer[0], "median_request_cuda_event_ms": "2.1"}]
        self.assertIn("CONSUMER_PRODUCER_NUMERIC_MISMATCH", {r["status"] for r in compare_native_summary(own, bad, {"MP02"})})
        with self.assertRaises(ValueError):
            compare_native_summary(own, producer + producer, {"MP02"})


if __name__ == "__main__":
    unittest.main()
