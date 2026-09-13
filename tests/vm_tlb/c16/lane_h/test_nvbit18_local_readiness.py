from __future__ import annotations

import hashlib
import json
import lzma
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from util.vm_tlb.c16.lane_h.c16_nvbit18_parser_qualification import (  # noqa: E402
    FIXTURE_LABEL,
    INPUT_SCHEMA as QUALIFICATION_INPUT_SCHEMA,
    qualify,
)
from util.vm_tlb.c16.lane_h.c16_nvbit_storage_estimate import (  # noqa: E402
    EstimateError,
    INPUT_SCHEMA as STORAGE_INPUT_SCHEMA,
    estimate,
)
from util.vm_tlb.c16.lane_h.real_model_trace_contract import AdmissionError, validate  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def real_input() -> dict[str, object]:
    return {
        "schema_version": "C16_REAL_MODEL_TRACE_INPUT_V1",
        "trace_kind": "REAL_MODEL_TRACE",
        "scientific_model_evidence": True,
        "terminal_status": "COMPLETE",
        "producer": {
            "g_producer_commit": "a" * 40,
            "nvbit18_tool_sha256": "b" * 64,
            "c16_tracer_sha256": "c" * 64,
        },
        "identity": {
            "model": "Llama-Example",
            "model_revision": "d" * 40,
            "package": "example-package",
            "package_revision": "e" * 40,
            "scenario": "B1-prefill-T256",
            "scenario_input_sha256": "f" * 64,
        },
        "raw_artifacts": [{
            "raw_path": "/outside-git/local/trace.raw",
            "remote_path": "/remote/trace.raw",
            "remote_size_bytes": 1024,
            "remote_sha256": "1" * 64,
            "local_size_bytes": 1024,
            "local_sha256": "1" * 64,
            "remote_local_sha256_closed": True,
        }],
    }


class Nvbit18LocalReadinessTest(unittest.TestCase):
    def test_synthetic_nvbit18_raw_cta_qualification_is_fixture_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "nvbit_180_c16tracer"
            trace_dir = root / "elementwise" / "traces"
            trace_dir.mkdir(parents=True)
            tool_dir = root.parent / "nvbit_180"
            tool_dir.mkdir()
            tool = tool_dir / "tool_sha256.txt"
            tool.write_text("tool-identity\n", encoding="utf-8")
            trace = trace_dir / "kernel-1.trace.xz"
            with lzma.open(trace, "wt", encoding="utf-8") as output:
                output.write("-kernel name = synthetic_kernel\n-kernel id = 1\n-grid dim = (1,1,1)\n")
                output.write("-block dim = (32,1,1)\n-nvbit version = 1.8\n-accelsim tracer version = 5\n")
                output.write("0 0 0 0 0100 00000001 0 LDG.E.32 0 4 0 0xfff 0\n")
            catalog = trace_dir / "kernelslist"
            catalog.write_text("kernel-1.trace.xz\n", encoding="utf-8")
            stats = trace_dir / "stats"
            stats.write_text(
                "kernel id, kernel mangled name, total_reported_insts\n"
                "kernel-1.trace.xz, synthetic_kernel, 1\n",
                encoding="utf-8",
            )
            source = {
                "schema_version": QUALIFICATION_INPUT_SCHEMA,
                "fixture_label": FIXTURE_LABEL,
                "scientific_model_evidence": False,
                "source_publication_commit": "9" * 40,
                "source_transfer_receipt": {"status": "SHA_CLOSED"},
                "tool_identity": {"tool_identity_path": "../nvbit_180/tool_sha256.txt", "tool_identity_sha256": digest(tool)},
                "fixture_groups": [{
                    "fixture_group": "synthetic",
                    "trace_directory": "elementwise/traces",
                    "kernel_catalog": "kernelslist",
                    "kernel_catalog_sha256": digest(catalog),
                    "kernel_stats": "stats",
                    "kernel_stats_sha256": digest(stats),
                    "traces": [{"path": trace.name, "sha256": digest(trace)}],
                }],
            }
            source_path = Path(temporary) / "input.json"
            source_path.write_text(json.dumps(source), encoding="utf-8")
            result = qualify(source_path, root)
            self.assertEqual(result["fixture_label"], FIXTURE_LABEL)
            self.assertFalse(result["scientific_model_evidence"])
            self.assertEqual(result["fixture_trace_count"], 1)
            self.assertEqual(result["qualification"]["status"], "PASS_NVBIT18_RAW_CTA_PARSER_QUALIFICATION")

    def test_local_transport_retains_raw_and_closes_compression_and_scratch(self) -> None:
        script = ROOT / "util/vm_tlb/c16/lane_h/c16_nvbit_raw_ingest.py"
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            remote = base / "remote.raw"
            remote.write_bytes(b"trace-record\n" * 4096)
            store = base / "store"
            probe = [
                sys.executable, str(script), "probe", "--local-root", str(store), "--remote-host", "LOCAL",
                "--remote-path", str(remote), "--run-id", "run", "--target-identity", "model/package/scenario",
                "--tool-identity", "nvbit=1.8", "--trace-kind", FIXTURE_LABEL,
            ]
            subprocess.run(probe, cwd=ROOT, check=True, capture_output=True, text=True)
            facts = next((store / "receipts").glob("REMOTE_FACTS_*.json"))
            subprocess.run(
                [sys.executable, str(script), "ingest", "--local-root", str(store), "--remote-facts", str(facts), "--compression", "xz"],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            ingest = next((store / "receipts").glob("INGEST_*.json"))
            compression = next((store / "receipts").glob("COMPRESSION_*.json"))
            scratch = base / "scratch"
            subprocess.run(
                [
                    sys.executable, str(script), "prepare-parser-scratch", "--local-root", str(store),
                    "--scratch-root", str(scratch), "--ingest-receipt", str(ingest),
                    "--compression-receipt", str(compression),
                ],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            ingested = json.loads(ingest.read_text(encoding="utf-8"))
            self.assertTrue(remote.is_file())
            self.assertTrue(Path(ingested["local"]["path"]).is_file())
            self.assertEqual(ingested["fixture_label"], FIXTURE_LABEL)
            self.assertFalse(ingested["scientific_model_evidence"])
            self.assertFalse(ingested["remote_delete_permitted"])
            self.assertFalse(ingested["local_uncompressed_delete_permitted"])
            self.assertTrue(next(scratch.iterdir()).is_file())
            self.assertEqual(ingest.stat().st_mode & 0o222, 0)

    def test_storage_estimator_refuses_fixture_campaign_projection(self) -> None:
        fixture = {
            "schema_version": STORAGE_INPUT_SCHEMA,
            "trace_kind": FIXTURE_LABEL,
            "scientific_model_evidence": False,
            "canary": {
                "raw_bytes": 1000, "compressed_bytes": 250, "trace_file_count": 2,
                "kernel_count": 2, "memory_record_count": 10, "capture_duration_seconds": 1,
                "source_batch_size": 1,
            },
            "storage": {"local_available_before_bytes": 10_000},
        }
        with tempfile.TemporaryDirectory() as temporary:
            result = estimate(fixture, Path(temporary), allow_fixture_test=True)
        self.assertEqual(result["fixture_label"], FIXTURE_LABEL)
        self.assertIsNone(result["projected_storage_B4"])
        self.assertIsNone(result["safe_campaign_budget"])
        with self.assertRaises(EstimateError):
            estimate(fixture, Path.cwd(), allow_fixture_test=False)

    def test_storage_estimator_projects_only_an_admitted_real_model_canary(self) -> None:
        real = {
            "schema_version": STORAGE_INPUT_SCHEMA,
            "trace_kind": "REAL_MODEL_TRACE",
            "scientific_model_evidence": True,
            "admission": {
                "status": "ADMITTED_REAL_TRACE_PIPELINE_CANARY",
                "pipeline_mode": "REAL_TRACE_PIPELINE_CANARY",
            },
            "canary_identity": {"admission": "REAL_TRACE_PIPELINE_CANARY"},
            "canary": {
                "raw_bytes": 1000, "compressed_bytes": 250, "trace_file_count": 2,
                "kernel_count": 2, "memory_record_count": 10, "capture_duration_seconds": 1,
                "source_batch_size": 1,
            },
            "storage": {"local_available_before_bytes": 10_000},
        }
        with tempfile.TemporaryDirectory() as temporary:
            result = estimate(real, Path(temporary), allow_fixture_test=False)
        self.assertTrue(result["formal_llm_campaign_estimate"])
        self.assertEqual(result["projected_storage_B4"]["raw_bytes"], 4000)
        self.assertIsNotNone(result["safe_campaign_budget"])

    def test_real_model_admission_requires_all_identity_closures_and_is_canary_only(self) -> None:
        payload = real_input()
        result = validate(payload, "a" * 40)
        self.assertEqual(result["producer"]["g_producer_commit"], "a" * 40)
        invalid = real_input()
        invalid["terminal_status"] = "PARTIAL_TERMINAL"
        with self.assertRaises(AdmissionError):
            validate(invalid)
        fixture = real_input()
        fixture["fixture_label"] = FIXTURE_LABEL
        with self.assertRaises(AdmissionError):
            validate(fixture)


if __name__ == "__main__":
    unittest.main()
