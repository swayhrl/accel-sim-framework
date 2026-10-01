import unittest

from intervals import handoff_chronology_summary, parse_observed_intervals, role_family


def sem(ordinal, module, start, end, parent="0"):
    return {"point_id": "MP02", "observed_request_id": "R", "ordinal": str(ordinal),
            "module": module, "phase": "decode", "nvtx_start_ns": str(start),
            "nvtx_end_ns": str(end), "parent_ordinal_or_NA": str(parent), "status": "PASS"}


def cuda(identity, ordinal, start, end):
    return {"point_id": "MP02", "observed_request_id": "R", "cuda_interval_id": identity,
            "parent_request_id": "R", "start_ns": str(start), "end_ns": str(end),
            "kernel_name": "synthetic_kernel",
            "correlated_nvtx_ordinal_or_NA": str(ordinal), "source_capture_sha256": "a" * 64}


class IntervalAdapterTests(unittest.TestCase):
    def test_role_family_explicit(self):
        self.assertEqual(role_family("model.layers.0.mlp.gate_up_proj"), "GATE_UP_PROJECTION")
        self.assertEqual(role_family("model.layers.0.self_attn"), "ATTENTION")
        self.assertEqual(role_family("other"), "OTHER:other")

    def test_union_overlap_and_sibling_gap(self):
        semantic = [sem(0, "parent", 0, 100, "NA"), sem(1, "producer", 0, 50), sem(2, "consumer", 50, 100)]
        events = [cuda("k1", 1, 0, 30), cuda("k2", 1, 20, 50), cuda("k3", 2, 70, 90)]
        result = parse_observed_intervals(semantic, events, "MP02", "R")
        self.assertEqual(result["parent_cuda_union_ns"], 70)
        producer = next(r for r in result["module_unions"] if r["module"] == "producer")
        self.assertEqual(producer["cuda_sum_ns"], 60)
        self.assertEqual(producer["cuda_union_ns"], 50)
        self.assertEqual(producer["overlap_double_count_ns"], 10)
        self.assertEqual(result["sibling_boundaries"][0]["signed_gap_ns"], 20)

    def test_unassigned_is_parent_not_module(self):
        semantic = [sem(0, "parent", 0, 100, "NA"), sem(1, "producer", 0, 50)]
        events = [cuda("k1", 1, 0, 20), cuda("k2", "NA", 30, 50)]
        result = parse_observed_intervals(semantic, events, "MP02", "R")
        self.assertEqual(result["parent_cuda_union_ns"], 40)
        self.assertEqual(result["uncorrelated_cuda_intervals"], 1)
        self.assertEqual(result["module_unions"][0]["cuda_union_ns"], 20)

    def test_missing_correlation_and_capture_fail(self):
        with self.assertRaises(ValueError):
            parse_observed_intervals([sem(1, "p", 0, 10)], [cuda("k", 99, 0, 10)], "MP02", "R")
        with self.assertRaises(ValueError):
            parse_observed_intervals([sem(1, "p", 0, 10)], [], "MP02", "R")

    def test_overlap_boundary_not_negative_launch_saving(self):
        semantic = [sem(0, "parent", 0, 100, "NA"), sem(1, "p", 0, 50), sem(2, "c", 30, 100)]
        events = [cuda("k1", 1, 0, 50), cuda("k2", 2, 40, 80)]
        result = parse_observed_intervals(semantic, events, "MP02", "R")
        self.assertEqual(result["sibling_boundaries"][0]["signed_gap_ns"], -10)
        self.assertEqual(result["sibling_boundaries"][0]["positive_gap_ns"], 0)

    def test_handoff_union_no_double_count(self):
        parsed = {"parent_cuda_span_ns": 100, "parent_cuda_union_ns": 80,
                  "sibling_boundaries": [
                      {"producer_module": "x.self_attn", "consumer_module": "x.mlp.gate_up_proj",
                       "producer_ordinal": "1", "consumer_ordinal": "2", "status": "GAP",
                       "gap_start_ns": 10, "gap_end_ns": 20},
                      {"producer_module": "x.mlp.gate_up_proj", "consumer_module": "x.mlp.act_fn",
                       "producer_ordinal": "2", "consumer_ordinal": "3", "status": "GAP",
                       "gap_start_ns": 15, "gap_end_ns": 25},
                  ]}
        result = handoff_chronology_summary(parsed)
        self.assertEqual(result["positive_gap_sum_ns"], 20)
        self.assertEqual(result["positive_gap_union_ns"], 15)
        self.assertEqual(result["status"], "HANDOFF_CHRONOLOGY_MATERIAL")


if __name__ == "__main__":
    unittest.main()
