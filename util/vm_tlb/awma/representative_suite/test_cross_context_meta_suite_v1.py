#!/usr/bin/env python3
"""Directed identity and recurrence tests for the cross-context selector."""
import unittest

from build_cross_context_meta_suite_v1 import enrich, implementation_family, recurrence


class CrossContextIdentityTest(unittest.TestCase):
    def test_present_step_count_normalizes_zero_inclusive_s2_catalog(self):
        s2 = {
            "phase": "DECODE", "decode_step_count": "32", "launch_count": "48",
            "launches_per_decode_step_min": "0", "launches_per_decode_step_max": "48",
        }
        context = {
            "phase": "DECODE", "decode_step_count": "1", "launch_count": "48",
            "launches_per_decode_step_min": "48", "launches_per_decode_step_max": "48",
        }
        self.assertEqual(recurrence(s2), "ONE_STEP_SHAPE_48")
        self.assertEqual(recurrence(s2), recurrence(context))

    def test_shape_change_preserves_level1_and_level2(self):
        base = {
            "phase": "DECODE", "normalized_kernel_family": "PYTORCH_FLASH_FWD",
            "exact_implementation": "void pytorch_flash::flash_fwd_splitkv_kernel<X>()",
            "block": "128,1,1", "launch_count": "24",
            "accumulated_gpu_duration_ns": "1000", "decode_step_count": "32",
            "launches_per_decode_step_min": "24", "launches_per_decode_step_max": "24",
        }
        first = enrich(dict(base, grid="1,9,14"))
        second = enrich(dict(base, grid="1,2,14"))
        self.assertEqual(first["level1"], second["level1"])
        self.assertEqual(first["level2"], second["level2"])
        self.assertNotEqual(first["level3"], second["level3"])

    def test_gemv_exact_implementation_families_remain_distinct(self):
        one = implementation_family("internal::gemvx::kernel<int, half, 6>()")
        two = implementation_family("internal::gemvx::kernel<int, half, 7>()")
        self.assertNotEqual(one, two)

    def test_splitkv_and_combine_are_different_level2_families(self):
        one = implementation_family("pytorch_flash::flash_fwd_splitkv_kernel<T>()")
        two = implementation_family("pytorch_flash::flash_fwd_splitkv_combine_kernel<T>()")
        self.assertNotEqual(one, two)


if __name__ == "__main__":
    unittest.main()
