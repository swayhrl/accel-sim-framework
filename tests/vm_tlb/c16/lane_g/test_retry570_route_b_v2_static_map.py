"""CPU-only contract tests for V2 actual-code-object static maps."""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parents[4] / "util/vm_tlb/c16/lane_g"
sys.path.insert(0, str(LANE))
from c16_native_common import ContractError  # noqa: E402
from retry570_recovery_v3_nvbit_qualification import (  # noqa: E402
    V2_STATIC_MAP_COLUMNS, load_code_object_manifest, validate_static_map_v2,
)


class RouteBV2StaticMapTest(unittest.TestCase):
    def test_v2_source_resolves_owner_at_runtime_not_from_libtorch_env(self):
        source = (LANE / "retry570_route_b_v2_static_map_tool.cu").read_text(encoding="utf-8")
        for token in ("cuFuncGetModule", "API_CUDA_cuLibraryLoadData", "API_CUDA_cuLibraryGetModule",
                      "API_CUDA_cuModuleLoadData", "API_CUDA_cuModuleLoadDataEx",
                      "C16_NVBIT_CODE_OBJECT_MANIFEST", "code_object_path", "code_object_sha256", "width_bytes",
                      "instruction->getSize()"):
            self.assertIn(token, source)
        self.assertNotIn("C16_NVBIT_CODE_OBJECT_SHA256", source)

    def test_manifest_and_v2_map_close_exact_owner_and_semantics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); owner = root / "libvendor.so"; owner.write_bytes(b"closed owner")
            sha = hashlib.sha256(owner.read_bytes()).hexdigest(); manifest = root / "owners.tsv"
            manifest.write_text(f"{owner}\t{sha}\n", encoding="utf-8")
            closed = load_code_object_manifest(manifest)
            header = "\t".join(V2_STATIC_MAP_COLUMNS) + "\n"
            row = ["8", "0", "16", "LDG.E", "GLOBAL", "1", "0", "1", "1", "8", "LDG.E",
                   "full", "_Zexact", "0x1", str(owner), sha]
            static_map = root / "map.tsv"; static_map.write_text(header + "\t".join(row) + "\n", encoding="utf-8")
            valid = validate_static_map_v2(static_map, function="_Zexact", manifest=closed)
            self.assertEqual(valid["code_object_sha256"], sha)
            row[-1] = "0" * 64
            static_map.write_text(header + "\t".join(row) + "\n", encoding="utf-8")
            with self.assertRaises(ContractError):
                validate_static_map_v2(static_map, function="_Zexact", manifest=closed)

    def test_v2_rejects_zero_width_for_a_memory_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); owner = root / "libvendor.so"; owner.write_bytes(b"closed owner")
            sha = hashlib.sha256(owner.read_bytes()).hexdigest(); manifest = root / "owners.tsv"
            manifest.write_text(f"{owner}\t{sha}\n", encoding="utf-8")
            header = "\t".join(V2_STATIC_MAP_COLUMNS) + "\n"
            row = ["8", "0", "16", "LDG.E", "GLOBAL", "1", "0", "1", "1", "0", "LDG.E",
                   "full", "_Zexact", "0x1", str(owner), sha]
            static_map = root / "map.tsv"; static_map.write_text(header + "\t".join(row) + "\n", encoding="utf-8")
            with self.assertRaises(ContractError):
                validate_static_map_v2(static_map, function="_Zexact", manifest=load_code_object_manifest(manifest))

    def test_v2_parent_forbids_caller_selected_owner(self):
        source = (LANE / "retry570_recovery_v3_nvbit_qualification.py").read_text(encoding="utf-8")
        self.assertIn('"NVBIT_STATIC_MAP_V2"', source)
        self.assertIn("V2 static-map mode forbids caller-selected code-object identity", source)
        self.assertIn("validate_static_map_v2", source)


if __name__ == "__main__":
    unittest.main()
