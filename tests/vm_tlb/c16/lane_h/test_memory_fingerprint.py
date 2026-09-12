from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from util.vm_tlb.c16.lane_h.memory_fingerprint import (  # noqa: E402
    TraceManifestError,
    canonical_memory_event,
    compare_memory_only_events,
    fingerprint_entry,
    fingerprint_rows,
    load_manifest,
    parse_trace_record,
    reuse_rows,
)
from util.vm_tlb.c16.lane_h.runtime_object_map_v2 import RuntimeObjectMapV2, sha256_file  # noqa: E402


FIXTURES = Path(__file__).with_name("fixtures")
OBJECT_MAP = FIXTURES / "object_map_v2.json"
COMPLETE_TRACE = FIXTURES / "trace_complete.traceg"
PARTIAL_TRACE = FIXTURES / "trace_partial.traceg"


def manifest_entry(trace_name: str, trace_sha: str, *, ordinal: int = 0,
                   capture_status: str = "COMPLETE", terminal_status: str = "COMPLETE",
                   order_model: str = "SET_ONLY") -> dict[str, object]:
    return {
        "address_domain": "GPU_VA_OBSERVED",
        "capture_status": capture_status,
        "deployment_id": "qwen-fixture-awq",
        "kernel_identity": "fixture_kernel:grid=1:block=32",
        "order_model": order_model,
        "phase": "DECODE",
        "run_id": "fixture-run-0",
        "scenario_id": "S1",
        "source_receipt": "fixture-capture-receipt",
        "terminal_status": terminal_status,
        "tool_version": "nvbit-fixture-v1",
        "trace_path": trace_name,
        "trace_sha256": trace_sha,
        "window_ordinal": ordinal,
    }


class MemoryFingerprintTest(unittest.TestCase):
    def setUp(self) -> None:
        self.object_map = RuntimeObjectMapV2.from_file(OBJECT_MAP)

    def _manifest(self, directory: Path, trace_fixture: Path, **entry_kwargs: object) -> tuple[Path, str]:
        trace = directory / trace_fixture.name
        shutil.copyfile(trace_fixture, trace)
        payload = {
            "schema_version": "c16-trace-manifest-v1",
            "entries": [manifest_entry(trace.name, sha256_file(trace), **entry_kwargs)],
        }
        path = directory / "TRACE_MANIFEST.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path, sha256_file(path)

    def test_active_lanes_width_pages_lines_and_access_kinds(self) -> None:
        event = parse_trace_record("0100 00000005 0 LDG.E.32 0 4 0 0x7f 0x80 0", 1)
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual([lane.lane_id for lane in event.lanes], [0, 2])
        self.assertEqual([lane.address for lane in event.lanes], [0x7F, 0x80])
        self.assertEqual(event.width, 4)
        self.assertEqual(event.access_kind, "READ")
        self.assertEqual(parse_trace_record("0130 00000005 0 STG.E.32 0 4 2 0x210 16 0", 2).access_kind, "WRITE")
        self.assertEqual(parse_trace_record("0140 00000001 0 ATOM.E.ADD.32 0 4 0 0x80000 0", 3).access_kind, "ATOMIC")
        raw = parse_trace_record("0 0 0 3 0100 00000001 0 LDG.E.32 0 4 0 0x10 0", 4, "RAW_CTA")
        self.assertEqual(raw.cta, (0, 0, 0))
        self.assertEqual(raw.warp_in_cta, 3)

    def test_complete_and_partial_capture_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            manifest, manifest_sha = self._manifest(directory, COMPLETE_TRACE)
            loaded_sha, entries = load_manifest(manifest, manifest_sha)
            result = fingerprint_entry(entries[0], loaded_sha, self.object_map, cache_set_count=16)
            rows = list(fingerprint_rows(result, 16))
            self.assertEqual(result.parse_status, "COMPLETE")
            self.assertEqual(result.zero_active_memory_events, 1)
            by_key = {(row["object_class"], row["access_kind"]): row for row in rows}
            self.assertGreaterEqual(by_key[("WEIGHT", "READ")]["unique_128b_lines"], 2)
            self.assertEqual(by_key[("KV_CACHE", "READ")]["unique_4k_va_buckets"], 2)
            self.assertEqual(by_key[("KV_CACHE", "READ")]["unique_64k_va_buckets"], 2)
            self.assertIn(("QUANT_METADATA", "WRITE"), by_key)
            self.assertIn(("UNKNOWN_RUNTIME", "ATOMIC"), by_key)
            self.assertEqual(by_key[("WEIGHT", "READ")]["local_line_revisit_references"], "NA")
            self.assertLessEqual(by_key[("WEIGHT", "READ")]["unique_cache_sets"], 16)

            partial_manifest, partial_sha = self._manifest(
                directory, PARTIAL_TRACE, ordinal=1, capture_status="BOUNDED_PARTIAL", terminal_status="PARTIAL_TERMINAL"
            )
            partial_loaded_sha, partial_entries = load_manifest(partial_manifest, partial_sha)
            partial = fingerprint_entry(partial_entries[0], partial_loaded_sha, self.object_map, cache_set_count=None)
            self.assertEqual(partial.parse_status, "PARTIAL_TERMINAL")
            self.assertEqual(partial.entry.capture_status, "BOUNDED_PARTIAL")

    def test_manifest_hash_and_file_order_contracts_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            manifest, manifest_sha = self._manifest(directory, COMPLETE_TRACE)
            with self.assertRaises(TraceManifestError):
                load_manifest(manifest, "0" * 64)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["entries"][0]["order_model"] = "CTA_GROUP_FILE_ORDER"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(TraceManifestError):
                load_manifest(manifest, sha256_file(manifest))
            self.assertNotEqual(manifest_sha, sha256_file(manifest))

    def test_set_overlap_is_not_global_order_and_cli_is_manifest_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            trace = directory / COMPLETE_TRACE.name
            shutil.copyfile(COMPLETE_TRACE, trace)
            payload = {
                "schema_version": "c16-trace-manifest-v1",
                "entries": [
                    manifest_entry(trace.name, sha256_file(trace), ordinal=0),
                    manifest_entry(trace.name, sha256_file(trace), ordinal=1),
                ],
            }
            manifest = directory / "TRACE_MANIFEST.json"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            manifest_sha = sha256_file(manifest)
            loaded_sha, entries = load_manifest(manifest, manifest_sha)
            results = [fingerprint_entry(entry, loaded_sha, self.object_map, None) for entry in entries]
            overlaps = list(reuse_rows(results))
            self.assertTrue(overlaps)
            self.assertEqual({row["order_model"] for row in overlaps}, {"SET_ONLY"})
            self.assertTrue(all("not global L2 order" in str(row["limitation"]) for row in overlaps))

            output = directory / "MEMORY_FINGERPRINTS.tsv"
            validation = directory / "FINGERPRINT_VALIDATION.tsv"
            reuse = directory / "REUSE_AND_OVERLAP.tsv"
            command = [
                sys.executable, str(ROOT / "util/vm_tlb/c16/lane_h/memory_fingerprint.py"),
                "--trace-manifest", str(manifest), "--expected-manifest-sha256", manifest_sha,
                "--object-map", str(OBJECT_MAP), "--output", str(output),
                "--validation-output", str(validation), "--reuse-output", str(reuse),
            ]
            completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
            self.assertIn("PASS c16-memory-fingerprint", completed.stdout)
            self.assertTrue(output.read_text(encoding="utf-8").startswith("manifest_sha256\t"))

    def test_memory_only_equivalence_gate_is_exact(self) -> None:
        full = parse_trace_record("0100 00000001 0 LDG.E.32 0 4 0 0x7f 0", 1)
        assert full is not None
        payload = {"terminal_status": "COMPLETE", "events": [canonical_memory_event(full)]}
        self.assertEqual(compare_memory_only_events([full], payload), [])
        payload["events"][0]["width"] = 8
        self.assertEqual(len(compare_memory_only_events([full], payload)), 1)


if __name__ == "__main__":
    unittest.main()
