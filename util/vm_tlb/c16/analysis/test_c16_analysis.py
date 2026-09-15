#!/usr/bin/env python3
import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c16_analysis import AnalysisError, COMPACT_BINARY_READY_HOOK, LOGICAL_TARGET_SCHEMA, V2_SHARD_SCHEMA, analyze_catalog_run, analyze_logical_target, decode_compact_binary, fingerprint, normalize_record, object_join, parse_route_b


def raw(address=4095, width=2, kind="READ", mask=3):
    return {"record_kind":"LANE_EVENT", "raw_schema":"C16_ROUTE_B_LANE_EVENT_V1", "access_kind":kind,
            "gpu_va":address, "width_bytes":width, "active_mask":mask, "lane_id":0, "kernel_launch_id":0}


class C16AnalysisTests(unittest.TestCase):
    def make_v2_root(self, directory, evidence_class, children, selected=None):
        root = Path(directory)
        identity = {"model_id": "m", "input_binding_sha256": "i", "scenario_id": "S2", "target_function": "f", "code_object_sha256": "c", "launch_selector": {"launch": 7}, "static_mref_set_sha256": "mref-sha"}
        entry_dir = root / "catalog" / "entries"; entry_dir.mkdir(parents=True)
        child_specs = []
        for run_id, selector, events in children:
            raw_dir = root / "raw" / run_id; raw_dir.mkdir(parents=True)
            raw_path = raw_dir / "memory.jsonl"
            records = []
            for event in events:
                value = raw(event["address"], event.get("width", 4), event.get("kind", "READ")); value.update({"static_index": event.get("mref", 1), "cta": event.get("cta", [0, 0, 0])}); records.append(value)
            raw_path.write_text("".join(json.dumps(value) + "\n" for value in records), encoding="utf-8")
            payload_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()
            binding = {"schema_version": V2_SHARD_SCHEMA, "formal_evidence_class": evidence_class, "target_identity": identity, "selector": selector, "static_mref_set_sha256": "mref-sha"}
            manifest = {"artifacts": [{"relative_path": "memory.jsonl", "size_bytes": raw_path.stat().st_size, "sha256": payload_hash}], "schema_version": 1, "v2_shard_binding": binding}
            manifest_path = raw_dir / "RUN_MANIFEST.json"; manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            (entry_dir / f"{run_id}.json").write_text(json.dumps({"raw_path": str(raw_dir), "raw_manifest_sha256": manifest_hash, "scientific_status": "FORMAL"}), encoding="utf-8")
            child_specs.append({"run_id": run_id, "raw_rel": "memory.jsonl"})
        logical = {"schema_version": LOGICAL_TARGET_SCHEMA, "logical_target_id": "LT", "formal_evidence_class": evidence_class, "target_identity": identity, "child_shards": child_specs}
        if selected is not None: logical["selected_static_mref_indices"] = selected
        logical_path = root / "logical.json"; logical_path.write_text(json.dumps(logical), encoding="utf-8")
        return root, logical_path

    def test_page_line_and_crossing(self):
        stats = fingerprint([normalize_record(raw(4095, 2), "x"), normalize_record(raw(65535, 2), "x")])
        self.assertEqual(stats["unique_4k_pages"], 4)
        self.assertEqual(stats["unique_64k_pages"], 2)
        self.assertEqual(stats["unique_128b_lines"], 4)

    def test_access_and_active_mask(self):
        stats = fingerprint([normalize_record(raw(1, 4, "READ", 1), "x"), normalize_record(raw(2, 4, "WRITE", 0), "x"), normalize_record(raw(3, 4, "ATOMIC", 7), "x")])
        self.assertEqual(stats["access_counts"], {"ATOMIC": 1, "READ": 1, "WRITE": 1})
        self.assertEqual(stats["active_lane_distribution"], {"0": 1, "1": 1, "3": 1})

    def test_object_alias_priority_and_unknown(self):
        rec = normalize_record(raw(100), "x")
        self.assertEqual(object_join(rec, [])["object_class"], "UNKNOWN_RUNTIME")
        joined = object_join(rec, [{"start": 0, "end": 200, "object_class": "KV_CACHE", "object_id": "z"}, {"start": 0, "end": 200, "object_class": "WEIGHT", "object_id": "a"}])
        self.assertEqual(joined["object_class"], "WEIGHT")

    def test_empty_partial_and_deterministic_parse(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / "raw.jsonl"; out = root / "out.jsonl"
            source.write_text(json.dumps(raw(1)) + "\n" + json.dumps(raw(2, kind="WRITE")) + "\n", encoding="utf-8")
            first = parse_route_b(source, "x", out); first_text = out.read_text(encoding="utf-8")
            second = parse_route_b(source, "x", out)
            self.assertEqual(first, second); self.assertEqual(first_text, out.read_text(encoding="utf-8"))
            source.write_text("", encoding="utf-8")
            with self.assertRaises(AnalysisError): parse_route_b(source, "x", out)

    def test_complete_terminal_is_accepted_and_bad_terminal_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / "raw.jsonl"; out = root / "out.jsonl"
            source.write_text(json.dumps(raw(1)) + "\n" + json.dumps({"record_kind":"TERMINAL", "terminal_status":"COMPLETE", "event_count":1, "overflow_count":0, "drop_count":0}) + "\n", encoding="utf-8")
            self.assertEqual(parse_route_b(source, "x", out)["lane_events"], 1)
            source.write_text(json.dumps(raw(1)) + "\n" + json.dumps({"record_kind":"TERMINAL", "terminal_status":"COMPLETE", "event_count":2, "overflow_count":0, "drop_count":0}) + "\n", encoding="utf-8")
            with self.assertRaises(AnalysisError): parse_route_b(source, "x", out)

    def test_incremental_catalog_entry_verifies_then_indexes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); run_id = "C16R_test"; raw_dir = root / "raw" / run_id
            raw_dir.mkdir(parents=True); payload = raw_dir / "memory.jsonl"
            payload.write_text(json.dumps(raw(128)) + "\n", encoding="utf-8")
            payload_hash = hashlib.sha256(payload.read_bytes()).hexdigest()
            manifest = {"artifacts": [{"relative_path": "memory.jsonl", "size_bytes": payload.stat().st_size, "sha256": payload_hash}], "schema_version": 1}
            manifest_path = raw_dir / "RUN_MANIFEST.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            entry_dir = root / "catalog" / "entries"; entry_dir.mkdir(parents=True)
            (entry_dir / f"{run_id}.json").write_text(json.dumps({"raw_path": str(raw_dir), "raw_manifest_sha256": manifest_hash, "scientific_status": "FORMAL"}), encoding="utf-8")
            result = analyze_catalog_run(root, run_id, "memory.jsonl", "test-commit", ["test"])
            self.assertEqual(result["lane_events"], 1)
            self.assertTrue((root / "derived" / "PARSE_INDEX.tsv").is_file())
            self.assertTrue((root / "derived" / "FEATURE_INDEX.tsv").is_file())
            receipt = json.loads((root / "derived" / "features" / run_id / "DERIVED_RECEIPT.json").read_text(encoding="utf-8"))
            self.assertIn("parser_config", receipt)
            for item in receipt["outputs"]:
                path = Path(item["path"])
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item["sha256"])

    def test_cta_shard_union_and_order_prohibition(self):
        with tempfile.TemporaryDirectory() as directory:
            root, logical = self.make_v2_root(directory, "CTA_SHARDED_ALL_MREF", [
                ("A", {"cta_ids": [[0, 0, 0]]}, [{"address": 0, "cta": [0, 0, 0], "mref": 1}]),
                ("B", {"cta_ids": [[1, 0, 0]]}, [{"address": 4096, "cta": [1, 0, 0], "mref": 2}]),
            ])
            result = analyze_logical_target(root, logical, "test-commit", ["test"])
            self.assertEqual(result["unique_4k_pages"], 2)
            self.assertEqual(result["spatial_cta_diversity"], 2)
            self.assertEqual(result["aggregate_order_label"], "CROSS_SHARD_ORDER_PROHIBITED")
            self.assertEqual(result["cross_shard_reuse_distance"], "UNSUPPORTED")

    def test_cta_overlap_and_wrong_identity_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root, logical = self.make_v2_root(directory, "CTA_SHARDED_ALL_MREF", [
                ("A", {"cta_ids": [[0, 0, 0]]}, [{"address": 0, "cta": [0, 0, 0]}]),
                ("B", {"cta_ids": [[0, 0, 0]]}, [{"address": 8, "cta": [0, 0, 0]}]),
            ])
            with self.assertRaises(AnalysisError): analyze_logical_target(root, logical, "test", [])
            data = json.loads(logical.read_text(encoding="utf-8")); data["child_shards"] = data["child_shards"][:1]; logical.write_text(json.dumps(data), encoding="utf-8")
            manifest = root / "raw" / "A" / "RUN_MANIFEST.json"; raw_manifest = json.loads(manifest.read_text(encoding="utf-8")); raw_manifest["v2_shard_binding"]["target_identity"]["code_object_sha256"] = "wrong"; manifest.write_text(json.dumps(raw_manifest), encoding="utf-8")
            entry = root / "catalog" / "entries" / "A.json"; entry_data = json.loads(entry.read_text(encoding="utf-8")); entry_data["raw_manifest_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest(); entry.write_text(json.dumps(entry_data), encoding="utf-8")
            with self.assertRaises(AnalysisError): analyze_logical_target(root, logical, "test", [])

    def test_wrong_static_mref_set_and_partial_cta_status(self):
        with tempfile.TemporaryDirectory() as directory:
            root, logical = self.make_v2_root(directory, "CTA_SHARDED_ALL_MREF", [
                ("A", {"cta_ids": [[0, 0, 0]]}, [{"address": 0, "cta": [0, 0, 0]}]),
            ])
            manifest = root / "raw" / "A" / "RUN_MANIFEST.json"; raw_manifest = json.loads(manifest.read_text(encoding="utf-8")); raw_manifest["v2_shard_binding"]["static_mref_set_sha256"] = "wrong"; manifest.write_text(json.dumps(raw_manifest), encoding="utf-8")
            entry = root / "catalog" / "entries" / "A.json"; entry_data = json.loads(entry.read_text(encoding="utf-8")); entry_data["raw_manifest_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest(); entry.write_text(json.dumps(entry_data), encoding="utf-8")
            with self.assertRaises(AnalysisError): analyze_logical_target(root, logical, "test", [])
            raw_manifest["v2_shard_binding"]["static_mref_set_sha256"] = "mref-sha"; manifest.write_text(json.dumps(raw_manifest), encoding="utf-8"); entry_data["raw_manifest_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest(); entry.write_text(json.dumps(entry_data), encoding="utf-8")
            data = json.loads(logical.read_text(encoding="utf-8")); data["expected_child_run_ids"] = ["A", "B"]; logical.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(analyze_logical_target(root, logical, "test", [])["shard_status"], "PARTIAL_SHARDS_PRESENT")

    def test_compact_binary_without_frozen_spec_fails_closed(self):
        with self.assertRaisesRegex(AnalysisError, COMPACT_BINARY_READY_HOOK):
            decode_compact_binary(Path("absent.bin"))

    def test_mref_complete_set_and_missing_shard_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root, logical = self.make_v2_root(directory, "MREF_SHARDED_COMPLETE_SET", [
                ("A", {"static_mref_indices": [1]}, [{"address": 0, "mref": 1}]),
                ("B", {"static_mref_indices": [2]}, [{"address": 128, "mref": 2}]),
            ], selected=[1, 2])
            result = analyze_logical_target(root, logical, "test", [])
            self.assertEqual(result["observed_static_mref_indices"], [1, 2])
            data = json.loads(logical.read_text(encoding="utf-8")); data["child_shards"] = data["child_shards"][:1]; logical.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(AnalysisError): analyze_logical_target(root, logical, "test", [])


if __name__ == "__main__":
    unittest.main()
