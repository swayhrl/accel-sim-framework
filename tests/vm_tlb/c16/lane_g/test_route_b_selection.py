#!/usr/bin/env python3
"""CPU-only fixtures for Route-B map-summary selection."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "util" / "vm_tlb" / "c16" / "lane_g"))

from route_b_selection import RouteBSelectionError, freeze_final_selection


SHA_A = "a" * 64
SHA_B = "b" * 64


def request(request_id: str, phase: str, duration: int, grid: str = "2x1x1"):
    return {"request_id": request_id, "phase": phase, "exact_full_function": "full::" + request_id,
            "known_mangled_name": "MAP_DISCOVERY_REQUIRED", "grid": grid, "block": "64x1x1",
            "shape_key": "B1_T128_D4", "dtype_key": "float16", "launch_count": 2,
            "phase_duration_ns": duration, "source_catalog_sha": SHA_A}


def summary(row, count: int, **updates):
    value = {"request_id": row["request_id"], "status": "MAPPED_EXACT", "exact_full_function": row["exact_full_function"],
             "grid": row["grid"], "block": row["block"], "shape_key": row["shape_key"], "dtype_key": row["dtype_key"],
             "function_mangled_name": "_Z" + row["request_id"], "static_map_sha256": SHA_A,
             "code_object_sha256": SHA_B, "static_global_mref_count": count}
    value.update(updates)
    return value


class RouteBSelectionTests(unittest.TestCase):
    def test_duration_union_proxy_is_deterministic(self):
        a, b, c = request("a", "PREFILL", 70), request("b", "PREFILL", 20), request("c", "PREFILL", 10)
        result = freeze_final_selection({"requests": [a, b, c]}, [summary(a, 1), summary(b, 50), summary(c, 1)])
        phase = result["phases"]["PREFILL"]
        self.assertEqual(["a", "b", "c"], phase["duration_prefix_request_ids"])
        self.assertEqual(["b"], phase["memory_proxy_prefix_request_ids"])
        self.assertEqual(["a", "b", "c"], phase["final_request_ids"])
        self.assertEqual(0.9615384615384616, phase["memory_proxy_prefix_fraction"])

    def test_failed_closed_candidate_is_never_substituted(self):
        a, b = request("a", "DECODE", 80), request("b", "DECODE", 20)
        result = freeze_final_selection({"requests": [a, b]}, [summary(a, 1), {"request_id": "b", "status": "FAILED_CLOSED", "failure_reason": "exact function absent"}])
        self.assertEqual(["a"], result["final_request_ids"])
        self.assertEqual("b", result["map_failures_closed"][0]["request_id"])

    def test_missing_map_identity_or_outcome_data_fails_closed(self):
        a = request("a", "PREFILL", 1)
        with self.assertRaises(RouteBSelectionError):
            freeze_final_selection({"requests": [a]}, [summary(a, 1, function_mangled_name="")])
        with self.assertRaises(RouteBSelectionError):
            freeze_final_selection({"requests": [a]}, [summary(a, 1, gpu_va=0x1000)])
        with self.assertRaises(RouteBSelectionError):
            freeze_final_selection({"requests": [a]}, [])


if __name__ == "__main__":
    unittest.main()
