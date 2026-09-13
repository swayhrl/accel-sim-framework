#!/usr/bin/env python3
"""CPU-only unit tests for the diagnostic-only model NVBit runner guards."""
from __future__ import annotations

import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from c16_native_common import ContractError  # noqa: E402
from nvbit_model_qualify import output_checksum, trace_evidence, validate_tool_contract  # noqa: E402


class FakeTokens:
    def __init__(self, values: list[int]) -> None:
        self.values = values

    def detach(self) -> "FakeTokens":
        return self

    def to(self, _device: str) -> "FakeTokens":
        return self

    def flatten(self) -> "FakeTokens":
        return self

    def tolist(self) -> list[int]:
        return self.values


class FakeLogits:
    def __getitem__(self, _item: object) -> "FakeLogits":
        return self

    def argmax(self, *, dim: int) -> FakeTokens:
        self.dim = dim
        return FakeTokens([7])


class ModelQualificationTests(unittest.TestCase):
    def test_baseline_rejects_declared_or_preloaded_tool(self) -> None:
        self.assertEqual(validate_tool_contract("BASELINE", None, None, None)["tool_path"], "NA")
        with self.assertRaises(ContractError):
            validate_tool_contract("BASELINE", None, None, "/tmp/tool.so")

    def test_profile_tool_requires_exact_file_hash_and_preload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tool.so"
            path.write_bytes(b"fixed tool")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            closed = validate_tool_contract("OFFICIAL_MEM_TRACE", path, digest, str(path))
            self.assertEqual(closed["tool_sha256"], digest)
            self.assertEqual(closed["ld_preload_launch_declaration"], str(path))
            with self.assertRaises(ContractError):
                validate_tool_contract("OFFICIAL_MEM_TRACE", path, digest, "/wrong/tool.so")
            with self.assertRaises(ContractError):
                validate_tool_contract("OFFICIAL_MEM_TRACE", path, "0" * 64, str(path))

    def test_terminal_token_checksum_is_canonical(self) -> None:
        checksum, values = output_checksum(FakeLogits())
        self.assertEqual(values, [7])
        self.assertEqual(checksum, hashlib.sha256(b"[7]").hexdigest())

    def test_qualification_uses_frozen_cache_correct_decode_workload(self) -> None:
        source = (LANE / "nvbit_model_qualify.py").read_text(encoding="utf-8")
        self.assertIn("decode_once(", source)
        self.assertIn("cache_correct_decode", source)
        self.assertNotIn("model(input_ids=prompt, use_cache=False)", source)

    def test_non_s0_recovery_requires_an_explicit_generic_gate(self) -> None:
        source = (LANE / "nvbit_model_qualify.py").read_text(encoding="utf-8")
        self.assertIn('parser.add_argument("--recovery-v3-generic", action="store_true"', source)
        self.assertIn('load_binding(args.binding_receipt, canary=not args.recovery_v3_generic)', source)
        self.assertIn('Recovery-V3 generic qualification is reserved for non-S0 frozen scenario bindings', source)

    def test_wrapper_owned_child_proves_parent_and_does_not_open_second_lease(self) -> None:
        source = (LANE / "nvbit_model_qualify.py").read_text(encoding="utf-8")
        self.assertIn('parser.add_argument("--parent-lease-receipt", type=Path', source)
        self.assertIn("lease, parent = wrapper_owned_budget(args, identity)", source)
        self.assertIn("marker = wrapper_measurement_marker(args, identity)", source)
        self.assertIn('"child_acquired_second_lease": False', source)

    def test_profile_requires_real_declared_evidence_and_c16_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "stdout.log").write_text("MEMTRACE: CTX - grid_launch_id 3\n", encoding="utf-8")
            result = trace_evidence(
                raw_dir=root, mode="OFFICIAL_MEM_TRACE", trace_glob="stdout.log",
                trace_marker=r"grid_launch_id", kernel_catalog_glob=None,
            )
            self.assertTrue(result["required"])
            with self.assertRaises(ContractError):
                trace_evidence(
                    raw_dir=root, mode="C16_MEMORY_TRACER", trace_glob="traces/*.trace.xz",
                    trace_marker=None, kernel_catalog_glob="traces/kernelslist*",
                )
            traces = root / "traces"
            traces.mkdir()
            (traces / "kernel-1.trace.xz").write_bytes(b"nonzero compressed trace")
            (traces / "kernelslist_ctx_0x1").write_text("kernel id, kernel name\n1,test\n", encoding="utf-8")
            result = trace_evidence(
                raw_dir=root, mode="C16_MEMORY_TRACER", trace_glob="traces/*.trace.xz",
                trace_marker=None, kernel_catalog_glob="traces/kernelslist*",
            )
            self.assertEqual(len(result["kernel_catalogs"]), 1)

    def test_baseline_cannot_claim_trace_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ContractError):
                trace_evidence(
                    raw_dir=Path(directory), mode="BASELINE", trace_glob="stdout.log",
                    trace_marker=None, kernel_catalog_glob=None,
                )

    def test_noop_control_closes_tool_identity_without_trace_claim(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = trace_evidence(
                raw_dir=root, mode="NVBIT_NOOP_CONTROL", trace_glob=None,
                trace_marker=None, kernel_catalog_glob=None,
            )
            self.assertFalse(result["required"])
            with self.assertRaises(ContractError):
                trace_evidence(
                    raw_dir=root, mode="NVBIT_NOOP_CONTROL", trace_glob="stdout.log",
                    trace_marker=None, kernel_catalog_glob=None,
                )

    def test_launch_inventory_requires_direct_in_raw_payload_and_matching_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inventory = root / "launch_inventory.tsv"
            inventory.write_text(
                "global_launch_ordinal\tfunction_full_name\tfunction_mangled_name\n"
                "1\texact full\texact mangled\n",
                encoding="utf-8",
            )
            previous = os.environ.get("C16_NVBIT_LAUNCH_INVENTORY_PATH")
            self.addCleanup(
                lambda: os.environ.pop("C16_NVBIT_LAUNCH_INVENTORY_PATH", None)
                if previous is None else os.environ.__setitem__("C16_NVBIT_LAUNCH_INVENTORY_PATH", previous)
            )
            os.environ["C16_NVBIT_LAUNCH_INVENTORY_PATH"] = str(inventory)
            result = trace_evidence(
                raw_dir=root, mode="NVBIT_LAUNCH_INVENTORY", trace_glob=None,
                trace_marker=None, kernel_catalog_glob=None, launch_inventory_path=inventory,
            )
            self.assertEqual(result["records"][0]["record_count"], 1)
            with self.assertRaises(ContractError):
                trace_evidence(
                    raw_dir=root, mode="NVBIT_LAUNCH_INVENTORY", trace_glob="unexpected",
                    trace_marker=None, kernel_catalog_glob=None, launch_inventory_path=inventory,
                )


if __name__ == "__main__":
    unittest.main()
