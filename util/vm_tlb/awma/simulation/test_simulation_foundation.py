#!/usr/bin/env python3
import hashlib
import json
import lzma
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import fixed_window_replay as replay
import simulation_foundation as foundation


VALID_TRACE = b"""-kernel name = test_kernel
-kernel id = 1
-grid dim = (1,1,1)
-block dim = (32,1,1)
-shmem = 0
-nregs = 8
-binary version = 89
-cuda stream id = 0
-shmem base_addr = 0x0
-local mem base_addr = 0x0
-nvbit version = 1.7.6
-accelsim tracer version = 5
-enable lineinfo = 0

#traces format = [line_num] PC mask dest_num [reg_dests] opcode src_num [reg_srcs] mem_width [addresscompress?] [mem_addresses] immediate

#BEGIN_TB
thread block = 0,0,0
warp = 0
insts = 4
0000 ffffffff 1 R1 LDG.E.32 1 R2 4 1 1000 4 0
0010 ffffffff 0 STG.E.32 1 R1 4 1 2000 4 0
0020 ffffffff 0 BAR.SYNC 0 0 0
0030 ffffffff 0 EXIT 0 0 0
#END_TB
"""


LDGDEPBAR_TRACE = VALID_TRACE.replace(
    b"insts = 4\n", b"insts = 5\n"
).replace(
    b"0020 ffffffff 0 BAR.SYNC 0 0 0\n",
    b"0020 ffffffff 0 LDGDEPBAR 0 0 0\n"
    b"0030 ffffffff 0 BAR.SYNC 0 0 0\n",
).replace(
    b"0030 ffffffff 0 EXIT 0 0 0\n",
    b"0040 ffffffff 0 EXIT 0 0 0\n",
)

LDG_WIDTH_ZERO_TRACE = VALID_TRACE.replace(b"R2 4 1 1000 4 0", b"R2 0 0")
LDGSTS_WIDTH_ZERO_TRACE = VALID_TRACE.replace(
    b"0000 ffffffff 1 R1 LDG.E.32 1 R2 4 1 1000 4 0",
    b"0000 ffffffff 0 LDGSTS 1 R2 0 0",
)
LDC_WIDTH_ZERO_TRACE = VALID_TRACE.replace(
    b"LDG.E.32 1 R2 4 1 1000 4 0",
    b"LDC.U8 1 R2 0 0",
)
MISSING_MEMORY_ADDRESS_TRACE = VALID_TRACE.replace(b"R2 4 1 1000 4 0", b"R2 4 1 1000")

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refresh(manifest_path):
    root = manifest_path.parent
    manifest = json.loads(manifest_path.read_text())
    manifest["files"] = {name: digest(root / name) for name in sorted(manifest["files"])}
    manifest["bundle_hash_root"] = foundation.hash_root(manifest["files"])
    manifest_path.write_text(json.dumps(manifest, sort_keys=True))
    return manifest_path


def fixture(root, trace=VALID_TRACE):
    (root / "kernel-1.traceg.xz").write_bytes(lzma.compress(trace))
    (root / "kernelslist.g").write_text("kernel-1.traceg.xz\n")
    (root / "address.json").write_text('{"asid_epoch":"0","page_policy":"4K","va_width":49}\n')
    (root / "terminal.json").write_text('{"drop_count":0,"overflow_count":0,"status":"COMPLETE"}\n')
    manifest = {
        "schema_version": foundation.SCHEMA_VERSION,
        "evidence_class": foundation.TRACE_SCHEMA,
        "workload_id": "W",
        "model_id": "M",
        "model_revision": "rev",
        "input_binding_sha256": "1" * 64,
        "scenario_id": "S2_TEXT",
        "phase": "PREFILL",
        "backend": "sdpa",
        "dtype": "float16",
        "runtime_identity": "runtime",
        "target_id": "Q05_ATTN",
        "target_launch": "function-occurrence=0",
        "stream_context": "stream0",
        "grid": [1, 1, 1],
        "block": [32, 1, 1],
        "trace_schema": foundation.TRACE_SCHEMA,
        "trace_grammar_version": "ACCEL_SIM_TRACE_V5",
        "producer_source_sha256": "2" * 64,
        "producer_binary_sha256": "3" * 64,
        "tracer_version": "1.7.6",
        "tracer_build_sha256": "4" * 64,
        "address_context_sidecar": "address.json",
        "asid_epoch": "0",
        "va_width": 49,
        "page_policy": "4K",
        "producer_terminal_receipt": "terminal.json",
        "kernelslist": "kernelslist.g",
        "instruction_semantics": dict(foundation.SEMANTIC_ENCODINGS),
        "required_control_opcodes": ["BAR.SYNC"],
        "terminal": {"status": "COMPLETE", "drop_count": 0, "overflow_count": 0},
        "files": {name: digest(root / name) for name in ("address.json", "kernel-1.traceg.xz", "kernelslist.g", "terminal.json")},
    }
    manifest["bundle_hash_root"] = foundation.hash_root(manifest["files"])
    path = root / "SIM_INPUT_MANIFEST.json"
    path.write_text(json.dumps(manifest, sort_keys=True))
    return path


class TestFoundation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build = tempfile.TemporaryDirectory()
        cls.parser = Path(cls.build.name) / "traceg_grammar_smoke"
        subprocess.run(
            ["g++", "-std=c++17", "-O2", "-I", str(ROOT / "gpu-simulator/trace-parser"),
             str(HERE / "traceg_grammar_smoke.cc"), str(ROOT / "gpu-simulator/trace-parser/trace_parser.cc"),
             "-o", str(cls.parser)], check=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.build.cleanup()

    def admitted(self, path):
        return foundation.validate_bundle(path, self.parser)

    def compiled_smoke(self, trace):
        with tempfile.TemporaryDirectory() as temp:
            trace_path = Path(temp) / "fixture.traceg.xz"
            trace_path.write_bytes(lzma.compress(trace))
            return subprocess.run(
                [str(self.parser), str(trace_path)], text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )

    def test_ldgdepbar_width_zero_without_address_passes_compiled(self):
        result = self.compiled_smoke(LDGDEPBAR_TRACE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"LDGDEPBAR":1', result.stdout)
    def test_address_bearing_ldg_width_zero_rejected_compiled(self):
        result = self.compiled_smoke(LDG_WIDTH_ZERO_TRACE)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("memory opcode has zero/missing width: LDG.E.32", result.stderr)

    def test_ldgsts_width_zero_rejected_compiled(self):
        result = self.compiled_smoke(LDGSTS_WIDTH_ZERO_TRACE)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("memory opcode has zero/missing width: LDGSTS", result.stderr)

    def test_implicit_ldc_width_zero_without_address_passes_compiled(self):
        result = self.compiled_smoke(LDC_WIDTH_ZERO_TRACE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"LDC.U8":1', result.stdout)

    def test_valid_memory_record_passes_compiled(self):
        result = self.compiled_smoke(VALID_TRACE)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_memory_address_rejected_compiled(self):
        result = self.compiled_smoke(MISSING_MEMORY_ADDRESS_TRACE)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing stride", result.stderr)

    def test_valid_real_grammar_and_stable_id(self):
        with tempfile.TemporaryDirectory() as temp:
            path = fixture(Path(temp))
            first = self.admitted(path)
            second = self.admitted(path)
            self.assertTrue(first["admitted"])
            self.assertEqual(first["sim_input_id"], second["sim_input_id"])
            self.assertEqual(first["instruction_count"], 4)
            self.assertEqual(first["sim_input_id"], foundation.identity_for("SIM_INPUT", first["identity"]))

    def test_missing_sync_semantics_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = fixture(Path(temp))
            manifest = json.loads(path.read_text())
            del manifest["instruction_semantics"]["sync_control"]
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(foundation.ContractError, "instruction_semantics mismatch"):
                self.admitted(path)

    def test_missing_required_control_record_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = fixture(Path(temp))
            manifest = json.loads(path.read_text())
            manifest["required_control_opcodes"] = ["MEMBAR"]
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(foundation.ContractError, "required control opcode absent"):
                self.admitted(path)

    def test_empty_required_control_contract_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = fixture(Path(temp))
            manifest = json.loads(path.read_text())
            manifest["required_control_opcodes"] = []
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(foundation.ContractError, "explicit nonempty list"):
                self.admitted(path)

    def test_missing_kernelslist_member_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = fixture(root)
            (root / "kernelslist.g").write_text("kernel-missing.traceg.xz\n")
            refresh(path)
            with self.assertRaisesRegex(foundation.ContractError, "unhashed member"):
                self.admitted(path)

    def test_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = fixture(Path(temp))
            manifest = json.loads(path.read_text())
            manifest["files"]["address.json"] = "0" * 64
            manifest["bundle_hash_root"] = foundation.hash_root(manifest["files"])
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(foundation.ContractError, "hash mismatch"):
                self.admitted(path)

    def test_malformed_trace_record_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = fixture(root, VALID_TRACE.replace(b"0000 ffffffff", b"MALFORMED"))
            with self.assertRaisesRegex(foundation.ContractError, "grammar rejected"):
                self.admitted(path)

    def test_invalid_width_semantics_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = fixture(root, VALID_TRACE.replace(b"R2 4 1 1000", b"R2 3 1 1000"))
            with self.assertRaisesRegex(foundation.ContractError, "grammar rejected"):
                self.admitted(path)

    def test_drop_overflow_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = fixture(Path(temp))
            manifest = json.loads(path.read_text())
            manifest["terminal"]["drop_count"] = 1
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(foundation.ContractError, "drop/overflow"):
                self.admitted(path)

    def test_partial_bundle_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = fixture(Path(temp))
            manifest = json.loads(path.read_text())
            manifest["terminal"]["status"] = "PARTIAL"
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(foundation.ContractError, "terminal must be COMPLETE"):
                self.admitted(path)

    def test_c16_mref_gets_no_id(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.json"
            path.write_text(json.dumps({"evidence_class": "C16WARP1", "simulator_eligibility": "NOT_PROVEN_LOSSLESS"}))
            result = foundation.validate_bundle(path, self.parser)
            self.assertFalse(result["admitted"])
            self.assertIsNone(result["sim_input_id"])

    def test_parser_is_mandatory(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(foundation.ContractError, "grammar parser is required"):
                foundation.validate_bundle(fixture(Path(temp)))

    def test_catalog_schema_and_immutability(self):
        record = {
            "schema_version": foundation.SCHEMA_VERSION,
            "framework_sha": "a" * 40,
            "core_sha": "b" * 40,
            "binary_sha256": "c" * 64,
            "toolchain_receipt_sha256": "d" * 64,
            "base_config_sha256": "e" * 64,
            "vm_overlay_sha256": "f" * 64,
            "telemetry_exporter_sha256": "1" * 64,
            "normalizer_sha256": "2" * 64,
            "runtime_wrapper_sha256": "3" * 64,
            "accepted_base_config_sha256s": ["4" * 64, "5" * 64],
            "fixed_window_cycles": 10000,
            "qualification_scope": "HASH_BOUND_FIXED_WINDOW_10000",
        }
        record["sim_baseline_id"] = foundation.identity_for("SIM_BASELINE", record)
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(foundation.catalog_put(temp, "SIM_BASELINE", record)["result"], "CREATED")
            self.assertEqual(foundation.catalog_put(temp, "SIM_BASELINE", record)["result"], "NOOP_IDENTICAL")
            changed = dict(record)
            changed["binary_sha256"] = "4" * 64
            with self.assertRaises(foundation.ContractError):
                foundation.catalog_put(temp, "SIM_BASELINE", changed)

    def test_json_schemas_align_with_identity_contract(self):
        schema_dir = HERE / "schemas"
        for kind, fields in foundation.SCHEMAS.items():
            schema = json.loads((schema_dir / (kind + ".schema.json")).read_text())
            expected = {"schema_version", foundation.CATALOG_ID_FIELDS[kind], *fields}
            self.assertFalse(schema["additionalProperties"])
            self.assertEqual(set(schema["required"]), expected)
            self.assertEqual(set(schema["properties"]), expected)

    def test_telemetry_and_runtime_statuses(self):
        row = {"metric_name": "tlb.l1.miss", "metric_value": 3, "unit": "count", "evidence_origin": "SIM_RUN", "scientific_status": "FORMAL", "claim_scope": "FIXED_WINDOW_10000"}
        self.assertEqual(len(foundation.normalize([row])), 1)
        with self.assertRaises(foundation.ContractError):
            foundation.normalize([row, row])
        boundary = "gpu_sim_cycle = 10000\nGPGPU-Sim: ** break due to reaching the maximum cycles (or instructions) **\n"
        self.assertEqual(replay.classify_execution(boundary, 0), "EXPECTED_FIXED_WINDOW_BOUNDARY")
        wrong_boundary = boundary.replace("10000", "9999")
        self.assertEqual(replay.classify_execution(wrong_boundary, 0), "EXTERNAL_RUNTIME_FAILURE")
        self.assertEqual(replay.classify_execution("done\n", 0), "NORMAL_COMPLETION")
        self.assertEqual(replay.classify_execution("assertion failed\n", 1), "SIMULATOR_ASSERT_OR_FATAL")
        self.assertEqual(replay.classify_execution("", 2, admitted=False), "PARSER_ABORT")
        self.assertEqual(replay.classify_execution("", 2), "EXTERNAL_RUNTIME_FAILURE")

    def test_fixed_window_wrapper_smoke(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = fixture(root)
            binary = root / "fake-simulator.sh"
            binary.write_text("#!/bin/sh\necho 'gpu_sim_cycle = 10000'\necho 'GPGPU-Sim: ** break due to reaching the maximum cycles (or instructions) **'\n")
            binary.chmod(0o755)
            base_config = root / "base.config"
            base_config.write_text("# accepted base\n")
            object_map = root / "object.tsv"
            object_map.write_text("object\tbase\n")
            segment_map = root / "segment.tsv"
            segment_map.write_text("segment\tbase\n")
            overlay = root / "overlay.config"
            overlay.write_text(
                "-gpgpu_vm_object_map %s\n-gpgpu_vm_weight_segment_map %s\n-gpgpu_max_cycle 10000\n"
                % (object_map, segment_map)
            )
            baseline = {
                "schema_version": foundation.SCHEMA_VERSION,
                "framework_sha": "a" * 40,
                "core_sha": "b" * 40,
                "binary_sha256": digest(binary),
                "toolchain_receipt_sha256": "c" * 64,
                "base_config_sha256": "d" * 64,
                "vm_overlay_sha256": "e" * 64,
                "telemetry_exporter_sha256": "f" * 64,
                "normalizer_sha256": "1" * 64,
                "runtime_wrapper_sha256": "2" * 64,
                "accepted_base_config_sha256s": [digest(base_config)],
                "fixed_window_cycles": 10000,
                "qualification_scope": "HASH_BOUND_FIXED_WINDOW_10000",
            }
            baseline["sim_baseline_id"] = foundation.identity_for("SIM_BASELINE", baseline)
            baseline_path = root / "baseline.json"
            baseline_path.write_text(json.dumps(baseline))
            exporter = root / "fake-exporter.py"
            exporter.write_text(
                "import pathlib,sys\n"
                "out=pathlib.Path(sys.argv[sys.argv.index('--output-dir')+1])\n"
                "out.mkdir(parents=True)\n"
                "(out/'telemetry.tsv').write_text('metric\\tvalue\\ncycles\\t10000\\n')\n"
            )
            args = types.SimpleNamespace(
                output_dir=root / "run", manifest=manifest, parser=self.parser,
                baseline_identity=baseline_path, binary=binary, base_config=base_config,
                overlay=overlay, env=[], timeout_seconds=10, telemetry_exporter=exporter,
                trace_policy="FULL_RANK0", admission_receipt=None,
            )
            receipt = replay.run(args)
            self.assertEqual(receipt["execution_status"], "EXPECTED_FIXED_WINDOW_BOUNDARY")
            self.assertEqual(receipt["telemetry"]["status"], "PASS")
            self.assertEqual(receipt["base_config_sha256"], digest(base_config))


if __name__ == "__main__":
    unittest.main(verbosity=2)
