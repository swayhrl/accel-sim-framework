#!/usr/bin/env python3
from __future__ import annotations

import json
import importlib.util
import os
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
QUALIFIED_TRACE_ROOT = Path(
    "/root/share/mnt164/huangrulin/c16_ai_workload/raw/"
    "C16R_qwen2p5-7b-instruct-awq_s2-text-d1-d3_decode3_nvbit1771-"
    "sim-native-full-sass_bounded-context_20260925T120107Z_2b41b26fdb03")
U64 = struct.Struct("<Q")
PAIR = struct.Struct("<QQ")


def load_static_module():
    spec = importlib.util.spec_from_file_location("build_static_mapping", ROOT / "build_static_mapping.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_orchestrator_module():
    spec = importlib.util.spec_from_file_location(
        "orchestrate_trace_pressure", ROOT / "orchestrate_trace_pressure.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sidecar(path: Path) -> None:
    rows = ["ORACLE_ELASTIC_QWEIGHT_RESIDENCY_V1\t1\tMODELED_L2_GET_ADDR"]
    for layer in range(28):
        begin = 0x100000 + layer * 0x10000
        rows.append(f"0x{begin:x}\t0x{begin + 0x200:x}\tlayer{layer}\t{layer + 1}")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def trace(path: Path, kernel: int, *, bad_stride: bool = False) -> None:
    stride_mask = "00000005" if bad_stride else "00000007"
    text = f"""-kernel name = synthetic
-kernel id = {kernel}
-grid dim = (2,1,1)
-block dim = (32,1,1)
-shmem = 0
-nregs = 8
-binary version = 89
-cuda stream id = 0
-shmem base_addr = 0x700000
-local mem base_addr = 0x800000
-nvbit version = test
-accelsim tracer version = 5
-enable lineinfo = 0

#BEGIN_TB
thread block = 0,0,0
warp = 0
insts = 9
0000 00000001 0 LDG.E.32 0 4 0 0x9000 0
0010 00000003 0 LDG.E.64 0 4 0 0x100000 0x9080 0
0020 00000001 0 LDC.64 0 4 0 0x100000 0
0030 00000001 0 LD.E.32 0 4 0 0x700000 0
0040 00000001 0 LD.E.32 0 4 0 0x800000 0
0050 00000001 0 LD.E.32 0 4 0 0xa000 0
0060 {stride_mask} 0 LDG.E.32 0 4 1 0xb000 128 0
0070 00000007 0 LDG.E.32 0 4 2 0x100080 128 128 0 0
0080 00000001 0 STG.E.32 0 4 0 0xc000 0
#END_TB
#BEGIN_TB
thread block = 1,0,0
#END_TB
"""
    path.write_text(text, encoding="utf-8")


def read_u64(path: Path) -> list[int]:
    raw = path.read_bytes()
    return [U64.unpack_from(raw, offset)[0] for offset in range(0, len(raw), 8)]


def read_pairs(path: Path) -> list[tuple[int, int]]:
    raw = path.read_bytes()
    return [PAIR.unpack_from(raw, offset) for offset in range(0, len(raw), 16)]


class TracePressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.build = Path(tempfile.mkdtemp(prefix="trace-pressure-build-"))
        cls.scanner = cls.build / "scanner"
        subprocess.run([str(ROOT / "build_scanner.sh"), str(cls.scanner)], check=True)

    @classmethod
    def tearDownClass(cls) -> None:
        import shutil
        shutil.rmtree(cls.build)

    def scanner_command(self, trace_path: Path, sidecar_path: Path, output: Path, kernel: int) -> list[str]:
        return [str(self.scanner), "--trace", str(trace_path), "--sidecar", str(sidecar_path),
                "--output", str(output), "--kernel-id", str(kernel), "--decode", "1",
                "--semantic-layer", "0", "--semantic-identity", "up_proj",
                "--exact-function", "awq_gemm_kernel"]

    def test_exact_scanner_counts_and_prefix_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sidecar(root / "sidecar.tsv")
            trace(root / "kernel.traceg", 41)
            subprocess.run(self.scanner_command(root / "kernel.traceg", root / "sidecar.tsv",
                                                root / "out", 41), check=True)
            summary = json.loads((root / "out/summary.json").read_text())
            self.assertEqual(summary["schema"], "C16_E1_TRACE_KERNEL_SUMMARY_V1")
            self.assertEqual(summary["dynamic_instructions"], 9)
            self.assertEqual(summary["cta_count"], 2)
            self.assertEqual(summary["global_memory_instructions"], 6)
            self.assertEqual(summary["global_address_references"], 11)
            self.assertEqual(summary["target_address_references"], 4)
            self.assertEqual(summary["non_target_address_references"], 7)
            self.assertEqual(summary["target_refs_by_class"][0], 4)
            self.assertEqual(summary["first_expected_target_instruction_ordinal"], 2)
            self.assertEqual(summary["first_expected_target_reference_ordinal"], 2)
            self.assertEqual(summary["last_expected_target_instruction_ordinal"], 8)
            self.assertEqual(summary["last_expected_target_reference_ordinal"], 10)
            self.assertEqual(summary["prefix"]["address_references"], 1)
            self.assertEqual(summary["suffix"]["address_references"], 1)
            boundary = summary["target_boundaries"]["1"]
            self.assertEqual(boundary["prefix"]["dynamic_instructions"], 1)
            self.assertEqual(boundary["suffix"]["dynamic_instructions"], 1)
            self.assertEqual(boundary["prefix"]["global_address_references"], 1)
            self.assertEqual(read_u64(root / "out/prefix_non_target_unique_lines.u64"), [0x9000])
            self.assertEqual(read_u64(root / "out/suffix_non_target_unique_lines.u64"), [0xC000])
            pairs = dict(read_pairs(root / "out/non_target_line_refs.u64"))
            self.assertEqual(sum(pairs.values()), 7)
            self.assertEqual(pairs[0xB000], 1)
            self.assertEqual(sum(count for _, count in read_pairs(root / "out/all_line_refs.u64")), 11)

    def test_noncontiguous_base_stride_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sidecar(root / "sidecar.tsv")
            trace(root / "bad.traceg", 42, bad_stride=True)
            result = subprocess.run(self.scanner_command(root / "bad.traceg", root / "sidecar.tsv",
                                                         root / "out", 42), text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("base-stride active mask is non-contiguous", result.stderr)

    def test_orchestrator_skip_mapper_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "traces").mkdir()
            sidecar(root / "sidecar.tsv")
            trace(root / "traces/kernel-41-ctx_0x1.traceg", 41)
            sequence = root / "sequence.tsv"
            sequence.write_text(
                "global_dynamic_order\tdecode_iteration\tsemantic_layer\tsemantic_identity\texact_function\tstream\n"
                "41\t1\t0\tup_proj\tawq_gemm_kernel\t0\n", encoding="utf-8")
            analysis = root / "analysis"
            subprocess.run([
                "python3", str(ROOT / "orchestrate_trace_pressure.py"),
                "--scanner", str(self.scanner), "--skip-mapper", "--trace-root", str(root),
                "--kernel-sequence", str(sequence), "--sidecar", str(root / "sidecar.tsv"),
                "--analysis-root", str(analysis), "--workers", "1", "--require-kernel-count", "1",
                "--skip-trace-index-validation"],
                check=True)
            index = json.loads((analysis / "TRACE_REFERENCE_SUMMARY.json").read_text())
            summary = json.loads((analysis / "kernels/41/summary.json").read_text())
            self.assertEqual(index["kernel_count"], 1)
            self.assertEqual(index["totals"]["global_address_references"], 11)
            self.assertEqual(summary["mapper"]["status"], "SKIPPED")
            self.assertEqual((analysis / "kernels/41/non_target_set_refs.u64").stat().st_size,
                             32768 * 8)

    def test_mapper_contract_and_histogram(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "traces").mkdir()
            sidecar(root / "sidecar.tsv")
            trace(root / "traces/kernel-41-ctx_0x1.traceg", 41)
            sequence = root / "sequence.tsv"
            sequence.write_text(
                "global_dynamic_order\tdecode_iteration\tsemantic_layer\tsemantic_identity\texact_function\n"
                "41\t1\t0\tup_proj\tawq_gemm_kernel\n", encoding="utf-8")
            mapper = root / "mapper.py"
            mapper.write_text("""#!/usr/bin/env python3
import argparse,struct,sys
if '--provenance' in sys.argv:
 print('accepted_source_mode=SOURCE_DIRECT_CORE');print('accepted_core_sha=a2322069b9701597db7019080b5b54d29518e3a2');print('accepted_config_sha256=de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8');raise SystemExit(0)
p=argparse.ArgumentParser();p.add_argument('command');p.add_argument('--input-lines-u64');p.add_argument('--output-tsv');a=p.parse_args()
raw=open(a.input_lines_u64,'rb').read(); values=[struct.unpack_from('<Q',raw,i)[0] for i in range(0,len(raw),8)]
with open(a.output_tsv,'w') as out:
 out.write('line_address_hex\\tsubpartition\\tset_index\\n')
 for value in values: out.write(f'{value:#x}\\t{(value//128)%16}\\t{(value//2048)%2048}\\n')
""", encoding="utf-8")
            mapper.chmod(0o755)
            analysis = root / "analysis"
            subprocess.run([
                "python3", str(ROOT / "orchestrate_trace_pressure.py"),
                "--scanner", str(self.scanner), "--mapper", str(mapper),
                "--trace-root", str(root), "--kernel-sequence", str(sequence),
                "--sidecar", str(root / "sidecar.tsv"), "--analysis-root", str(analysis),
                "--workers", "1", "--skip-trace-index-validation"], check=True)
            summary = json.loads((analysis / "kernels/41/summary.json").read_text())
            histogram = read_u64(analysis / "kernels/41/non_target_set_refs.u64")
            all_histogram = read_u64(analysis / "kernels/41/all_set_refs.u64")
            prefix_histogram = read_u64(analysis / "kernels/41/prefix_non_target_set_refs.u64")
            suffix_histogram = read_u64(analysis / "kernels/41/suffix_non_target_set_refs.u64")
            self.assertEqual(sum(histogram), summary["non_target_128b_line_references"])
            self.assertEqual(sum(all_histogram), summary["global_128b_line_references"])
            self.assertEqual(sum(prefix_histogram), 1)
            self.assertEqual(sum(suffix_histogram), 1)
            self.assertEqual(summary["mapper"]["status"], "MAPPED_ACCEPTED_CORE")

    def test_trace_index_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "traces").mkdir()
            sidecar(root / "sidecar.tsv")
            trace(root / "traces/kernel-41-ctx_0x1.traceg", 41)
            sequence = root / "sequence.tsv"
            sequence.write_text(
                "global_dynamic_order\tdecode_iteration\tsemantic_layer\tsemantic_identity\texact_function\n"
                "41\t1\t0\tup_proj\tawq_gemm_kernel\n", encoding="utf-8")
            index = root / "index.tsv"
            index.write_text(
                "global_dynamic_order\ttraceg_artifact\tsize_bytes\tthread_blocks\tinstructions\tgrammar_status\n"
                f"41\tkernel-41-ctx_0x1.traceg\t{(root / 'traces/kernel-41-ctx_0x1.traceg').stat().st_size}"
                "\t2\t10\tTRACEG_GRAMMAR_PASS\n", encoding="utf-8")
            result = subprocess.run([
                "python3", str(ROOT / "orchestrate_trace_pressure.py"),
                "--scanner", str(self.scanner), "--skip-mapper", "--trace-root", str(root),
                "--kernel-sequence", str(sequence), "--trace-index", str(index),
                "--sidecar", str(root / "sidecar.tsv"), "--analysis-root", str(root / "analysis"),
                "--workers", "1"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("scanner/index instruction mismatch", result.stderr)

    def test_static_mapping_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sidecar(root / "sidecar.tsv")
            mapper = root / "mapper.py"
            mapper.write_text("""#!/usr/bin/env python3
import argparse,struct,sys
if '--provenance' in sys.argv:
 print('accepted_source_mode=SOURCE_DIRECT_CORE');print('accepted_core_sha=a2322069b9701597db7019080b5b54d29518e3a2');print('accepted_config_sha256=de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8');raise SystemExit(0)
p=argparse.ArgumentParser();p.add_argument('command');p.add_argument('--input-lines-u64');p.add_argument('--output-tsv');a=p.parse_args()
raw=open(a.input_lines_u64,'rb').read(); values=[struct.unpack_from('<Q',raw,i)[0] for i in range(0,len(raw),8)]
with open(a.output_tsv,'w') as out:
 out.write('line_address_hex\\tsubpartition\\tset_index\\n')
 for value in values: out.write(f'{value:#x}\\t{(value//128)%16}\\t{(value//2048)%2048}\\n')
""", encoding="utf-8")
            mapper.chmod(0o755)
            output = root / "static.json"
            subprocess.run(["python3", str(ROOT / "build_static_mapping.py"),
                            "--mapper", str(mapper), "--sidecar", str(root / "sidecar.tsv"),
                            "--output", str(output)], check=True)
            document = json.loads(output.read_text())
            self.assertEqual(document["region_count"], 28)
            self.assertEqual(document["total_target_lines"], 28 * 4)
            self.assertTrue(all(sum(item["subpartition_line_counts"]) == 4
                                for item in document["regions"]))

    def test_qualified_sidecar_address_order_is_normalized_by_target_class(self) -> None:
        module = load_static_module()
        actual = ROOT.parents[3] / "docs/vm_tlb/review_packs" / \
            "C16_E1_TRACE_ADDRESS_NAMESPACE_INTEGRATION_174NEW_V1" / \
            "ORACLE_QWEIGHT_L2_SIDECAR.tsv"
        raw_first_class = int(actual.read_text(encoding="utf-8").splitlines()[1].split("\t")[3])
        self.assertNotEqual(raw_first_class, 1)
        rows = module.intervals(actual)
        self.assertEqual([row["target_class"] for row in rows], list(range(1, 29)))

    def test_resume_option_is_rejected(self) -> None:
        result = subprocess.run(["python3", str(ROOT / "orchestrate_trace_pressure.py"),
                                 "--scanner", "/bin/true", "--skip-mapper",
                                 "--trace-root", ".", "--kernel-sequence", "sequence.tsv",
                                 "--sidecar", "sidecar.tsv", "--analysis-root", "analysis",
                                 "--resume"], text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments: --resume", result.stderr)

    def test_histogram_closure_mismatch_fails(self) -> None:
        module = load_orchestrator_module()
        summary = {
            "global_128b_line_references": 10,
            "non_target_128b_line_references": 7,
            "prefix": {"line_references": 2, "non_target_line_references": 1},
            "suffix": {"line_references": 3, "non_target_line_references": 2},
        }
        mapped = {
            "all_histogram_sum": 10, "histogram_sum": 7,
            "segment_histogram_sums": {
                "prefix_all": 2, "prefix_non_target": 1,
                "suffix_all": 3, "suffix_non_target": 999,
            },
        }
        with self.assertRaisesRegex(module.ContractError, "suffix non-target-set"):
            module.validate_histogram_closure(summary, mapped)

    def test_semantic_ranges_ignore_unknown_and_split_noncontiguous_runs(self) -> None:
        module = load_orchestrator_module()
        rows = [
            {"global_dynamic_order": "1", "decode_iteration": "1",
             "semantic_layer": "", "semantic_identity": "UNKNOWN",
             "exact_function": "ordinary", "profile_range_active": "True"},
            {"global_dynamic_order": "2", "decode_iteration": "1",
             "semantic_layer": "0", "semantic_identity": "up_proj",
             "exact_function": "fill-a", "profile_range_active": "True"},
            {"global_dynamic_order": "3", "decode_iteration": "1",
             "semantic_layer": "0", "semantic_identity": "up_proj",
             "exact_function": "awq-a", "profile_range_active": "True"},
            {"global_dynamic_order": "4", "decode_iteration": "1",
             "semantic_layer": "", "semantic_identity": "UNKNOWN",
             "exact_function": "separator", "profile_range_active": "True"},
            {"global_dynamic_order": "5", "decode_iteration": "1",
             "semantic_layer": "0", "semantic_identity": "up_proj",
             "exact_function": "fill-b", "profile_range_active": "True"},
            {"global_dynamic_order": "6", "decode_iteration": "1",
             "semantic_layer": "0", "semantic_identity": "up_proj",
             "exact_function": "awq-b", "profile_range_active": "True"},
        ]
        normalized = module.normalize_sequence(rows)
        self.assertTrue(normalized[0]["profile_range_active"])
        self.assertFalse(normalized[0]["semantic_range_active"])
        self.assertNotIn("semantic_range_first_dynamic_kernel", normalized[0])
        self.assertEqual((normalized[1]["semantic_range_first_dynamic_kernel"],
                          normalized[1]["semantic_range_last_dynamic_kernel"]), (2, 3))
        self.assertEqual((normalized[4]["semantic_range_first_dynamic_kernel"],
                          normalized[4]["semantic_range_last_dynamic_kernel"]), (5, 6))

    def test_full_formal_sequence_preflight(self) -> None:
        if not QUALIFIED_TRACE_ROOT.is_dir():
            self.skipTest("qualified trace is not mounted")
        sidecar_path = ROOT.parents[3] / "docs/vm_tlb/review_packs" / \
            "C16_E1_TRACE_ADDRESS_NAMESPACE_INTEGRATION_174NEW_V1" / \
            "ORACLE_QWEIGHT_L2_SIDECAR.tsv"
        result = subprocess.run([
            "python3", str(ROOT / "orchestrate_trace_pressure.py"),
            "--preflight-only", "--skip-mapper",
            "--trace-root", str(QUALIFIED_TRACE_ROOT),
            "--kernel-sequence", str(QUALIFIED_TRACE_ROOT / "control/KERNEL_SEQUENCE_FORMAL.tsv"),
            "--sidecar", str(sidecar_path), "--require-kernel-count", "4515"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["kernel_count"], 4515)
        self.assertTrue(receipt["preflight_only"])


if __name__ == "__main__":
    unittest.main()
