import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import subprocess

import ingest
import plot


class PaperIngestTests(unittest.TestCase):
    def test_pending_simulator_has_no_numeric_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = ingest.simulator_rows(Path(tmp))
        self.assertEqual(24, len(rows))
        self.assertTrue(all(row["status"] == "PENDING" and row["value"] is None for row in rows))
        self.assertTrue(all(row["source_stage"] == "PENDING_B16_TIMING_RESULT"
                            for row in rows if row["condition"] == "B16"))

    def test_simulator_rejects_unaccepted_and_bad_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / ingest.PACKS / "C16_E1_FUTURE" / "PAPER_SIM_RESULTS_ACCEPTED.json"
            path.parent.mkdir(parents=True)
            path.write_text("{}")
            payload = {"schema": "C16_E1_PAPER_SIM_RESULTS_ACCEPTED_V1",
                       "status": "PENDING", "framework_commit": "a" * 40,
                       "core_commit": "b" * 40, "trace_sha256": "c" * 64,
                       "independent_review_pack": "C16_E1_FUTURE",
                       "results": {"B16": {"correctness_pass": True, "terminal_pass": True,
                                           "baseline_cycles": 100, "candidate_cycles": 90,
                                           "mechanism_activations": 1, "protected_hits": 1,
                                           "admission_denials": 0}}}
            with patch.object(ingest, "committed_source", return_value=(payload, "d" * 64, "e" * 40)):
                with self.assertRaises(ingest.SourceError):
                    ingest.simulator_rows(root)
                payload["status"] = "INDEPENDENT_ACCEPTED"
                payload["results"]["B16"]["correctness_pass"] = False
                with self.assertRaises(ingest.SourceError):
                    ingest.simulator_rows(root)
                payload["results"]["B16"]["correctness_pass"] = True
                rows = ingest.simulator_rows(root)
                self.assertAlmostEqual(1, [x for x in rows if x["condition"] == "B16" and
                                           x["metric"] == "window_speedup"][0]["value"] * 0.9)
                self.assertTrue(all(x["value"] is None for x in rows if x["condition"] != "B16"))
                payload["results"]["B16"]["unexpected_metric"] = 1
                with self.assertRaises(ingest.SourceError):
                    ingest.simulator_rows(root)

    def test_nonfinite_or_missing_native_number_fails(self):
        for value in (None, "0", float("nan"), float("inf")):
            with self.assertRaises(ingest.SourceError):
                ingest.number({"metric": value}, "metric", "fixture")

    def test_committed_source_rejects_modified_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Paper test"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "paper@example.invalid"], check=True)
            source = root / "source.json"
            source.write_text('{"status":"PASS"}\n', encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "source.json"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)
            value, sha, commit = ingest.committed_source(root, Path("source.json"))
            self.assertEqual("PASS", value["status"])
            self.assertEqual(64, len(sha))
            self.assertEqual(40, len(commit))
            source.write_text('{"status":"PENDING"}\n', encoding="utf-8")
            with self.assertRaises(ingest.SourceError):
                ingest.committed_source(root, Path("source.json"))

    def test_plot_omits_pending_simulator_point(self):
        native = []
        def add(domain, condition, metric, value):
            native.append(dict(domain=domain, condition=condition, metric=metric,
                               value=value, status="ACCEPTED", source_sha256="a", source_commit="b"))
        for metric in ("AWQ_packed_storage_bytes", "device_L2_bytes", "RAW_FP16_dense_weight_bytes"):
            add("footprint", "M1", metric, 1024 * 1024)
        for budget in ingest.BUDGETS:
            for metric in ("direct_up_saving_ms", "observed_decode_saving_ms", "self_attn_saving_ms",
                           "mlp_top_saving_ms", "norm_saving_ms", "final_stage_saving_ms",
                           "unexplained_residual_ms"):
                add("native_budget", budget, metric, 0.1)
            native.append(dict(domain="simulator", condition=budget, metric="window_speedup",
                               value=None, status="PENDING", source_sha256="", source_commit=""))
        for condition, metric in (("UP28", "direct_up_saving_ms"), ("GUD84", "direct_ffn_saving_ms")):
            add("operator_family", condition, metric, 0.1)
            add("operator_family", condition, "outside_ffn_residual_ms", -0.1)
        with tempfile.TemporaryDirectory() as tmp:
            names = plot.generate({"schema": "C16_E1_PAPER_RESULTS_V1", "rows": native}, Path(tmp))
            self.assertNotIn("FIG_SIM_BUDGET.svg", names)
            self.assertFalse((Path(tmp) / "FIG_SIM_BUDGET.svg").exists())


if __name__ == "__main__":
    unittest.main()
