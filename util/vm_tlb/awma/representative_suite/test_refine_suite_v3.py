#!/usr/bin/env python3
"""Directed contract tests for Phase 3 grouping and mass accounting."""

import unittest

from refine_suite_v3 import (
    canonical_function_key,
    canonical_stratum_key,
    medoid_step,
    observed_step_runs,
)


def steps(grids, medians=None, recurrence=48):
    medians = medians or [100] * len(grids)
    return [
        {
            "step": i + 1,
            "grid": f"{grid},1,1",
            "recurrence": recurrence,
            "median_launch_duration_ns": median,
            "selection_pool_median_launch_duration_ns": median,
        }
        for i, (grid, median) in enumerate(zip(grids, medians))
    ]


class TrajectoryContractTest(unittest.TestCase):
    def test_monotonic_shape_is_one_trajectory_with_medoid(self):
        records = steps([100, 102, 105, 107, 109])
        self.assertEqual(len(observed_step_runs(records)), 1)
        self.assertEqual(medoid_step(records), 3)

    def test_nonmonotonic_shape_splits(self):
        records = steps([100, 102, 104, 103, 101])
        self.assertEqual([[r["step"] for r in run] for run in observed_step_runs(records)],
                         [[1, 2, 3], [4, 5]])

    def test_recurring_duration_regime_splits(self):
        records = steps([100, 102, 104, 106, 108, 110],
                        [100, 101, 100, 150, 151, 150])
        self.assertEqual([[r["step"] for r in run] for run in observed_step_runs(records)],
                         [[1, 2, 3], [4, 5, 6]])

    def test_canonical_key_distinguishes_unrecognized_functions(self):
        one = canonical_function_key("void unknown_a()")
        two = canonical_function_key("void unknown_b()")
        self.assertNotEqual(one, two)
        self.assertNotEqual(
            canonical_stratum_key("DECODE", "OTHER", "void unknown_a()", "1,1,1", "128,1,1"),
            canonical_stratum_key("DECODE", "OTHER", "void unknown_b()", "1,1,1", "128,1,1"),
        )


if __name__ == "__main__":
    unittest.main()
