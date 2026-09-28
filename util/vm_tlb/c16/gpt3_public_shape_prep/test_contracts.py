#!/usr/bin/env python3
import math
import ast
import unittest
from pathlib import Path

from contracts import (
    CONDITIONER_BYTES, DEVICE_CAPACITY_BYTES, EXPECTED_TINY_REFERENCE_SHA256,
    POINTS, SCALE, canonical_tables, dequantized_nibbles, point_math, tiny_reference,
)


class ContractTests(unittest.TestCase):
    def test_public_shapes_and_static_math(self):
        budget, launch = canonical_tables()
        self.assertEqual(len(budget), 4)
        self.assertEqual(len(launch), 8)
        expand = point_math(POINTS[0], 8)
        self.assertEqual(expand["dense_parameter_count"], 603_979_776)
        self.assertEqual(expand["dense_weight_bytes"], 1_207_959_552)
        self.assertEqual(expand["qweight_bytes"], 301_989_888)
        self.assertEqual(expand["qzeros_bytes"], 2_359_296)
        self.assertEqual(expand["scales_bytes"], 9_437_184)
        self.assertEqual(expand["grid"], 3072)
        self.assertEqual(expand["scratch_bytes"], 786432)

    def test_grid_and_scratch_all_points(self):
        _, launch = canonical_tables()
        for row in launch:
            self.assertEqual(row["gemm_grid"], math.ceil(row["M"] / 16) * (row["N"] // 128) * row["split_k_iters"])
            self.assertEqual(row["scratch_bytes"], row["split_k_iters"] * row["M"] * row["N"] * 2)
        reductions = {row["point"]: row["reduction_grid"] for row in launch if row["arm"] == "A"}
        self.assertEqual(reductions, {"EXPAND_M1": 96, "EXPAND_M256": 24576, "CONTRACT_M1": 24, "CONTRACT_M256": 6144})

    def test_packed_pattern_and_reference(self):
        self.assertEqual(dequantized_nibbles(), [-7*SCALE,-5*SCALE,-3*SCALE,-SCALE,SCALE,3*SCALE,5*SCALE,7*SCALE])
        reference = tiny_reference()["reference_sha256"]
        if EXPECTED_TINY_REFERENCE_SHA256 != "TO_BE_FROZEN":
            self.assertEqual(reference, EXPECTED_TINY_REFERENCE_SHA256)

    def test_peak_bounds(self):
        budget, _ = canonical_tables()
        self.assertEqual(CONDITIONER_BYTES, 4 * 67_108_864)
        self.assertTrue(all(row["max_peak_bound_bytes"] < DEVICE_CAPACITY_BYTES for row in budget))

    def test_cuda_import_is_lock_guarded(self):
        root = Path(__file__).resolve().parent
        runner = (root / "runner.py").read_text(encoding="utf-8")
        tree = ast.parse(runner)
        top_imports = []
        for node in tree.body:
            if isinstance(node, ast.Import): top_imports.extend(alias.name for alias in node.names)
            if isinstance(node, ast.ImportFrom): top_imports.append(node.module or "")
        self.assertNotIn("torch", top_imports)
        main = runner[runner.index("def main():"):]
        self.assertLess(main.index("require_outer_lock(); ready = require_ready"), main.index('importlib.import_module("torch")'))
        prepare = (root / "prepare.py").read_text(encoding="utf-8")
        prepare_tree = ast.parse(prepare)
        prepare_imports = []
        for node in prepare_tree.body:
            if isinstance(node, ast.Import): prepare_imports.extend(alias.name for alias in node.names)
            if isinstance(node, ast.ImportFrom): prepare_imports.append(node.module or "")
        self.assertNotIn("torch", prepare_imports)
        locked = (root / "run_locked.sh").read_text(encoding="utf-8")
        self.assertLess(locked.index("flock -n 9"), locked.index("nvidia-smi"))
        self.assertIn("l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum,gpu__time_duration.sum", locked)


if __name__ == "__main__":
    unittest.main(verbosity=2)
