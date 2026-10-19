"""PREPARED_NOT_TESTED fixtures, only after authority/role registration.

These check independent small mathematical examples and rejection of
invalid coordinates; they do not qualify application or production loads.
"""
import unittest
from reference_algorithms import (
    bicg_reference, gemm_reference, spmv_coordinate_reference,
)


class ReferenceFixtures(unittest.TestCase):
    def test_bicg_both_outputs(self):
        self.assertEqual(bicg_reference([[1, 2], [3, 4]], [1, 2], [3, 4]),
                         ([7.0, 10.0], [11.0, 25.0]))

    def test_gemm_nonzero_initial_c(self):
        self.assertEqual(gemm_reference([[1, 2]], [[3], [4]], [[5]], 2, 3),
                         [[37.0]])

    def test_sparse_indirect_and_duplicate(self):
        self.assertEqual(spmv_coordinate_reference(
            2, 3, [(0, 2, 2), (1, 0, 3), (0, 2, -1)], [4, 5, 6]),
            [6.0, 12.0])

    def test_sparse_out_of_range_rejected(self):
        with self.assertRaises(AssertionError):
            spmv_coordinate_reference(1, 1, [(0, 1, 2)], [3])


if __name__ == "__main__":
    unittest.main()
