#!/usr/bin/python3
"""Synthetic paper-intake tests, not scientific measurements."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from result_intake import canonical_sha, ro_bits, summarize, REQUIRED_GATES, WORKLOADS


def fixture(n=1):
    q = {"status": "INDEPENDENTLY_QUALIFIED", "core_source_commit": "1" * 40,
         "framework_source_commit": "2" * 40, "binary_sha256": "3" * 64}
    runs = []
    for w in WORKLOADS[:n]:
        for mode in ("B16_BANKED", "U_WB16"):
            ident = {k: q[k] for k in ("core_source_commit", "framework_source_commit", "binary_sha256")}
            ident.update(runtime_config_sha256=("4" if mode == "B16_BANKED" else "5") * 64,
                         trace_content_sha256="6" * 64, epoch_range={"scope": "full_application"}, workload=w,
                         feature_vector={"finite_wbuf": True, "unified_wb": mode == "U_WB16", "tvd": False, "ro": False,
                                         "adaptive_policy": False, "wbuf_entries": 16, "payload_capacity_per_slice": 1168,
                                         "bank_count": 4, "ops_per_bank_cycle": 1},
                         ideal_vector={"wb": False, "meta": False, "read_hit": False})
            runs.append({"workload": w, "mode": mode, "status": "COMPLETE_VALID", "identity": ident,
                         "run_key": canonical_sha(ident), "raw_log_sha256": "7" * 64,
                         "effective_base_config_sha256": "8" * 64, "validation": {k: True for k in REQUIRED_GATES},
                         "numeric_payload_validation": "UNAVAILABLE_SASS_DATALESS",
                         "summary": {"cycles": 100 if mode == "B16_BANKED" else 125, "instructions": 1000}})
    return {"evidence_kind": "FUNCTIONAL_IMPLEMENTATION", "qualification": q, "runs": runs}


class Checks(unittest.TestCase):
    def test_partial_pair_publishes_without_full_mean(self):
        r = summarize(fixture())
        self.assertEqual(len(r["pairs"]), 1)
        self.assertEqual(r["pairs"][0]["speedup"], .8)
        self.assertIsNone(r["whole_group_geomean"])
        self.assertEqual(len(r["unavailable"]), 8)

    def test_complete_set_includes_slowdowns(self):
        r = summarize(fixture(5))
        self.assertTrue(r["complete"])
        self.assertAlmostEqual(r["whole_group_geomean"], .8)

    def test_failed_rows_preserved_not_zero(self):
        p = fixture()
        p["runs"][1]["status"] = "TIMEOUT"
        r = summarize(p)
        self.assertEqual(r["pairs"], [])
        self.assertIn("TIMEOUT", [x["status"] for x in r["unavailable"]])
        self.assertIsNone(r["whole_group_geomean"])

    def test_scope_pass_does_not_require_missing_numeric_bytes(self):
        self.assertEqual(len(summarize(fixture())["pairs"]), 1)

    def test_producer_ready_is_not_qualified(self):
        p = fixture()
        p["qualification"]["status"] = "PRODUCER_READY_FOR_INDEPENDENT_VALIDATION"
        with self.assertRaises(ValueError): summarize(p)

    def test_cross_binary_is_rejected(self):
        p = fixture()
        p["runs"][1]["identity"]["binary_sha256"] = "9" * 64
        p["runs"][1]["run_key"] = canonical_sha(p["runs"][1]["identity"])
        with self.assertRaises(ValueError): summarize(p)

    def test_diagnostic_cannot_be_new_mechanism(self):
        p = fixture()
        p["runs"][1]["identity"]["ideal_vector"]["read_hit"] = True
        p["runs"][1]["run_key"] = canonical_sha(p["runs"][1]["identity"])
        with self.assertRaises(ValueError): summarize(p)

    def test_ro_off_view_keeps_canonical_identity(self):
        f = fixture()["runs"][0]["identity"]["feature_vector"]
        old = copy.deepcopy(f)
        self.assertFalse(ro_bits(f)["ro_tag_detach"])
        self.assertEqual(f, old)
        f["ro"] = True
        with self.assertRaises(ValueError): ro_bits(f)

    def test_sector_reference_must_actually_pass(self):
        p = fixture()
        p["runs"][1]["validation"]["sector_version_reference"] = False
        with self.assertRaises(ValueError): summarize(p)

    def test_duplicate_even_failed_rows_rejected(self):
        p = fixture()
        p["runs"].append(copy.deepcopy(p["runs"][0]))
        p["runs"][-1]["status"] = "FAILED"
        with self.assertRaises(ValueError): summarize(p)

    def test_published_partial_pair_plot_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory(prefix="lane6-r2-synthetic-") as tmp:
            root = Path(tmp)
            repo = root / "synthetic-authority"
            repo.mkdir()
            def git(*args):
                return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.STDOUT).decode().strip()
            def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
            git("init", "-q")
            packet = root / "synthetic_pair_packet.json"
            packet.write_text(json.dumps(fixture(), sort_keys=True))
            (repo / "bundle.json").write_text(json.dumps({"normalized_pair_packet_sha256": digest(packet)}))
            (repo / "receipt.json").write_text(json.dumps({"lane_id": 5, "artifacts": ["bundle.json"]}))
            git("add", "bundle.json", "receipt.json")
            git("-c", "user.name=Lane6 Test", "-c", "user.email=synthetic@example.invalid", "commit", "-qm", "synthetic test authority only")
            adapter = root / "adapter.json"
            adapter.write_text(json.dumps({"publication_commit": git("rev-parse", "HEAD"), "receipt_path": "receipt.json",
                "receipt_sha256": digest(repo / "receipt.json"), "bundle_path": "bundle.json",
                "bundle_sha256": digest(repo / "bundle.json"), "packet_file": str(packet)}))
            cmd = [sys.executable, str(Path(__file__).with_name("plot_qualified_pairs.py")), str(adapter),
                   "--framework-repo", str(repo), "--output-dir", str(root / "test_plot")]
            r = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            result = json.loads((root / "test_plot/FIGURE_INPUT_MANIFEST.json").read_text())
            self.assertEqual(len(result["pairs"]), 1)
            self.assertEqual(result["pairs"][0]["speedup"], .8)
            self.assertIsNone(result["whole_group_geomean"])
            packet.write_text(packet.read_text() + " ")
            r = subprocess.run(cmd[:-1] + [str(root / "tampered")], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("Unbound normalized pair payload", r.stderr)
            self.assertFalse((root / "tampered").exists())

    def test_native_lane5_csv_receipt_mapping_and_raw_tamper(self):
        import native_pair_intake as native
        import csv
        import io
        with tempfile.TemporaryDirectory(prefix="lane6-native-synthetic-") as tmp:
            root = Path(tmp)
            p = fixture()
            pub, qp = "a" * 40, "b" * 40
            q = p["qualification"]
            q.update(qualified_by="lane5", evidence_kind="PRODUCTION_DRIVEN",
                     data_correctness_scope="SYMBOLIC_32B_SECTOR_VERSIONS_AND_REQUEST_IDENTITY_NOT_NUMERIC_SASS_PAYLOAD")
            evidence = b'{"synthetic_test_only":true}'
            gate_names = ("bank_service", "finite_wbuf", "mode_legality", "old_all_off_equivalence", "requester_exact_once", "resource_closure", "sector_reference_data", "stale_fill", "wb_lifecycle")
            evidence_path = "docs/ep_l2/synthetic_checks.json"
            q["gates"] = {name: {"status": "PASS", "production_driven": True, "evidence_path": evidence_path,
                                         "evidence_sha256": hashlib.sha256(evidence).hexdigest()} for name in gate_names}
            q["qualified_feature_vectors"] = [r["identity"]["feature_vector"] for r in p["runs"]]
            qbytes = json.dumps(q).encode()
            modes, results, specs, rows = {}, [], [], []
            for m in p["runs"]:
                ident = m["identity"]
                mode = m["mode"]
                data = b"baseline" if mode == "B16_BANKED" else b"unified"
                records = [{"name": "config-0.config", "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}]
                audit = {"configs": records, "auxiliary_assets": [], "traces": [{"name": "kernelslist.g", "sha256": "f" * 64}],
                         "qualified_release_sha256": hashlib.sha256(qbytes).hexdigest()}
                ident["runtime_config_sha256"] = canonical_sha({"ordered_configs": records, "auxiliary_assets": [], "environment": {}})
                ident["trace_content_sha256"] = canonical_sha(audit["traces"])
                ident["binary_sha256"] = hashlib.sha256(b"synthetic executable").hexdigest()
                m["run_key"] = canonical_sha(ident)
                directory = root / m["run_key"]
                directory.mkdir()
                (directory / "raw.log").write_bytes(b"synthetic non-scientific log")
                (directory / "config-0.config").write_bytes(data)
                (directory / "accel-sim.out").write_bytes(b"synthetic executable")
                summary = {**m["summary"], "hardware_drained": True, "slices": 64, "requester_exact_once_audit": True,
                           "data_correctness_qualification": True, "wb_created": 1, "wb_lower_accepted": 1, "wb_completed": 1,
                           "payload_free": 1168 * 64, "payload_roles": {}, "payload_capacity": 1168 * 64}
                summary.update({k: 0 for k in ("live_descriptors", "live_line_mshrs", "live_wad", "pending_lower_reads", "pending_returns", "pending_responses", "transient_payloads")})
                result = {"run_key": m["run_key"], "identity": ident, "status": "COMPLETE_VALID", "summary": summary,
                          "raw_log_sha256": native.file_hash(directory / "raw.log"), "audit": audit, "validation": {"status": "PASS"}}
                result["allocation"] = {"result_directory": str(directory)}
                specs.append({"identity": ident, "environment": {}})
                results.append(result)
                modes[mode] = {"runtime_config_sha256": ident["runtime_config_sha256"], "ordered_config_manifest": records,
                               "feature_vector": ident["feature_vector"], "ideal_vector": ident["ideal_vector"]}
                row = {"workload": m["workload"], "mode": mode, "status": result["status"], "run_key": m["run_key"],
                       "raw_log_sha256": result["raw_log_sha256"], "cycles": summary["cycles"], "instructions": summary["instructions"]}
                row.update({k: ident[k] for k in ("core_source_commit", "framework_source_commit", "binary_sha256", "runtime_config_sha256", "trace_content_sha256")})
                row.update({k: json.dumps(ident[k]) for k in ("feature_vector", "ideal_vector", "epoch_range")})
                rows.append(row)
            q["binary_sha256"] = p["runs"][0]["identity"]["binary_sha256"]
            qbytes = json.dumps(q).encode()
            for result in results: result["audit"]["qualified_release_sha256"] = hashlib.sha256(qbytes).hexdigest()
            producer = {k: q[k] for k in ("core_source_commit", "framework_source_commit", "binary_sha256")}
            producer["modes"] = modes
            csv_out = io.StringIO()
            writer = csv.DictWriter(csv_out, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
            pair = {"workload": WORKLOADS[0], "results": results, "specs": specs}
            mapping = {qp + ":" + native.REPORT + "R0_INDEPENDENTLY_QUALIFIED.json": qbytes,
                       qp + ":" + evidence_path: evidence,
                       native.PRODUCER + ":" + native.PRODUCER_CONTRACT: json.dumps(producer).encode(),
                       pub + ":" + native.REPORT + "RECEIPT.json": json.dumps({"lane_id": 5, "artifacts": ["pair_test"]}).encode(),
                       pub + ":pair_test/PAIR_RECEIPT.json": json.dumps(pair).encode(),
                       pub + ":pair_test/RESULTS.csv": csv_out.getvalue().encode()}
            adapter = {"qualification_publication": qp, "native_pairs": [{"publication_commit": pub, "pair_repository_path": "pair_test"}]}
            with patch("native_pair_intake.subprocess.check_output", side_effect=lambda args: mapping[args[-1]]):
                packet = native.read_native_packet(root, adapter)
                self.assertEqual(summarize(packet)["pairs"][0]["speedup"], .8)
                Path(results[1]["allocation"]["result_directory"], "raw.log").write_text("tampered")
                with self.assertRaisesRegex(ValueError, "Raw payload mismatch"):
                    native.read_native_packet(root, adapter)


if __name__ == "__main__":
    unittest.main(verbosity=2)
