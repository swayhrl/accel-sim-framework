#!/usr/bin/env python3
import importlib.util
from importlib.machinery import SourceFileLoader
import tempfile
import unittest
import hashlib
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("e1_b16_reuse_canary.py")
SPEC = importlib.util.spec_from_loader(
    "e1_b16_reuse_canary", SourceFileLoader("e1_b16_reuse_canary", str(MODULE_PATH))
)
CANARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CANARY)


class B16ReuseCanaryTest(unittest.TestCase):
    def test_parse_output_and_diagnostics(self):
        text = """launching kernel name: kernel_a uid: 1 cuda_stream_id: 0
gpu_tot_sim_cycle = 10
gpu_tot_sim_insn = 20
gpu_tot_issued_cta = 2
oracle_elastic_l2_snapshot_begin
oracle_elastic_l2\tinstance=0\tquota=4\toccupancy=1
oracle_elastic_l2_class_occupancy\tinstance=0\tclass_1=1\tclass_2=0
oracle_elastic_l2_snapshot_end
launching kernel name: kernel_b uid: 2 cuda_stream_id: 0
gpu_tot_sim_cycle = 15
gpu_tot_sim_insn = 25
gpu_tot_issued_cta = 3
GPGPU-Sim: *** exit detected ***
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "simulator.stdout"
            path.write_text(text, encoding="utf-8")
            parsed = CANARY.parse_simulator_output(path, True)
        self.assertTrue(parsed["terminal"])
        self.assertEqual([row["uid"] for row in parsed["launches"]], [1, 2])
        self.assertEqual(parsed["completed"][2]["gpu_tot_sim_cycle"], 15)
        self.assertEqual(parsed["diagnostics"][1][0]["occupancy"], 1)
        self.assertEqual(parsed["class_occupancy"][1][0]["class_1"], 1)

    def test_response_sign(self):
        result = CANARY.response(100, 90)
        self.assertEqual(result["R0_minus_M1_cycles"], 10)
        self.assertAlmostEqual(result["response_fraction"], 0.1)

    def test_malformed_diagnostic_fails_closed(self):
        with self.assertRaises(CANARY.ContractError):
            CANARY.parse_key_values("oracle_elastic_l2\tinstance=bad", "oracle_elastic_l2")

    def test_duplicate_diagnostic_instance_fails_closed(self):
        text = """launching kernel name: kernel_a uid: 1 cuda_stream_id: 0
oracle_elastic_l2_snapshot_begin
oracle_elastic_l2\tinstance=0\tquota=8192
oracle_elastic_l2\tinstance=0\tquota=8192
oracle_elastic_l2_snapshot_end
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "simulator.stdout"
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(CANARY.ContractError):
                CANARY.parse_simulator_output(path, True)

    def test_output_manifest_requires_exact_members(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lines = []
            for name in sorted(CANARY.REQUIRED_OUTPUT_MEMBERS):
                path = root / name
                path.write_text(name, encoding="utf-8")
                lines.append(f"{hashlib.sha256(name.encode()).hexdigest()}  {name}")
            (root / "OUTPUT_SHA256SUMS").write_text("\n".join(lines) + "\n")
            self.assertEqual(set(CANARY.verify_output_sums(root)),
                             CANARY.REQUIRED_OUTPUT_MEMBERS)
            (root / "extra.txt").write_text("extra", encoding="utf-8")
            lines.append(f"{hashlib.sha256(b'extra').hexdigest()}  extra.txt")
            (root / "OUTPUT_SHA256SUMS").write_text("\n".join(lines) + "\n")
            with self.assertRaises(CANARY.ContractError):
                CANARY.verify_output_sums(root)

    def test_per_uid_neutrality_detects_cycle_drift(self):
        row = {"gpu_tot_sim_cycle": 10, "gpu_tot_sim_insn": 20,
               "gpu_tot_issued_cta": 2}
        left = {"completed": {1: dict(row), 2: dict(row)}}
        right = {"completed": {1: dict(row), 2: dict(row)}}
        self.assertTrue(CANARY.per_uid_stats_exact(left, right, 2))
        right["completed"][2]["gpu_tot_sim_cycle"] += 1
        self.assertFalse(CANARY.per_uid_stats_exact(left, right, 2))

    def test_case4_uses_only_exact_zero_retention_subset(self):
        counters = {"target_protection_admission_denied": 1,
                    "normal_fallback_protected_victims": 0}
        self.assertEqual(
            CANARY.classify_interpretation(-0.01, -0.01, -0.01, 8, 0, counters),
            "CASE_4_EXACT_ZERO_RETENTION_WITH_OBSERVED_CONSTRAINT_EVENTS")
        counters["target_protection_admission_denied"] = 0
        self.assertEqual(
            CANARY.classify_interpretation(-0.01, -0.01, -0.01, 8, 0, counters),
            "CASE_3_RESIDENCY_ACTIVITY_WITHOUT_TARGET_LOCAL_TIMING_BENEFIT")

    def test_diagnostic_coverage_requires_all_instances_and_closure(self):
        counters = {}
        classes = {}
        for instance in range(16):
            counter = {field: 0 for field in CANARY.DIAGNOSTIC_COUNTER_FIELDS}
            counter.update({"instance": instance, "quota": 8192, "occupancy": 1,
                            "occupancy_max": 1})
            counters[instance] = counter
            row = {f"class_{index}": 0 for index in range(1, 29)}
            row.update({"instance": instance, "class_1": 1})
            classes[instance] = row
        result = CANARY.verify_diagnostic_coverage(
            {"diagnostics": {1: counters}, "class_occupancy": {1: classes},
             "snapshot_begin": {1}, "snapshot_end": {1}}, 1)
        self.assertEqual(result["counter_row_count"], 16)
        del classes[15]
        with self.assertRaises(CANARY.ContractError):
            CANARY.verify_diagnostic_coverage(
                {"diagnostics": {1: counters}, "class_occupancy": {1: classes},
                 "snapshot_begin": {1}, "snapshot_end": {1}}, 1)


if __name__ == "__main__":
    unittest.main()
