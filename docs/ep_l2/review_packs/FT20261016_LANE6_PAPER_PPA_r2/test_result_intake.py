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


if __name__ == "__main__":
    unittest.main(verbosity=2)
