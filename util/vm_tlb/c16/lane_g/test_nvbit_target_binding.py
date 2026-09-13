"""No-GPU tests for C-plan-to-NVBit structural target binding."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

import nvbit_target_binding as BINDER  # noqa: E402


def write_tsv(path: Path, fields: tuple[str, ...], row: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerow(row)


class NvbitTargetBindingTests(unittest.TestCase):
    def test_binder_requires_a_unique_full_composite_catalog_match(self) -> None:
        plan = {field: "x" for field in BINDER.PLAN_FIELDS}
        plan.update({
            "capture_modality": "NVBIT", "target_plan_id": "fixed", "selector_kind": "SELECTOR_R",
            "selector_code_sha256": "a" * 64, "budget": "48", "deployment_id": "c16_qwen25_7b_awq",
            "scenario_id": "S1", "phase": "DECODE", "run_id": "run", "device": "cuda:0", "context": "ctx",
            "stream": "stream", "correlation_id": "corr", "launch_ordinal": "17",
            "unit_id": "launch:run:cuda:0:ctx:stream:corr:17",
        })
        catalog = {field: "x" for field in BINDER.CATALOG_FIELDS}
        catalog.update({field: plan[field] for field in BINDER.COMPOSITE_FIELDS})
        catalog.update({"kernel_name": "void at::native::vectorized_elementwise_kernel<fixture>", "grid": "7x1x1", "block": "128x1x1"})
        self.assertEqual(BINDER.exact_source_row(plan, [catalog]), catalog)
        with self.assertRaises(Exception):
            BINDER.exact_source_row(plan, [catalog, dict(catalog)])

    def test_binder_rejects_non_supported_name_without_guessing(self) -> None:
        with self.assertRaises(Exception):
            BINDER.narrow_regex("awq_gemm_kernel")
        self.assertEqual(
            BINDER.narrow_regex("void at::native::vectorized_elementwise_kernel<(int)4, x>"),
            "void at::native::vectorized_elementwise_kernel.*",
        )


if __name__ == "__main__":
    unittest.main()
