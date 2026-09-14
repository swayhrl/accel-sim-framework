"""Focused static contract checks for the Recovery-V3 NVBit qualification parent."""
from pathlib import Path
import sys
import tempfile
import unittest


SOURCE = (Path(__file__).resolve().parents[4] / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_nvbit_qualification.py").read_text(encoding="utf-8")
LANE = Path(__file__).resolve().parents[4] / "util/vm_tlb/c16/lane_g"
sys.path.insert(0, str(LANE))
from retry570_recovery_v3_nvbit_qualification import targeted_memory_evidence  # noqa: E402


class RecoveryV3QualificationContractTest(unittest.TestCase):
    def test_parent_owned_fresh_campaign_lease(self):
        for token in ("RecoveryV3CampaignLease", "initialize(", "write_parent_lease_start", "C16_G_PARENT_LEASE_TOKEN", "MeasurementActive(args.campaign_ledger", "child_acquired_second_lease"):
            self.assertIn(token, SOURCE)

    def test_only_identity_diagnostics_are_admitted(self):
        self.assertIn('"TARGETED_MEMORY_DISCRIMINATOR"', SOURCE)
        self.assertIn("scientific_eligible_for_timing\": False", SOURCE)
        self.assertIn("RECOVERY_V3_DIRECT_NVBIT_IDENTITY_QUALIFICATION_NOT_FOR_TIMING", SOURCE)

    def test_static_map_closes_the_loaded_code_object(self):
        self.assertIn("--code-object-sha256", SOURCE)
        self.assertIn("C16_NVBIT_CODE_OBJECT_SHA256", SOURCE)

    def test_targeted_discriminator_is_parent_leased_and_counts_address_evidence(self):
        for token in ("TARGETED_MEMORY_TRACE", "targeted_memory_evidence", "predicate_true_count",
                      "nonzero_mref_count", "COMPLETE_VALID_ADDRESS_BEARING",
                      "COMPLETE_PREDICATED_OFF_TARGET", "COMPLETE_ZERO_ADDRESS_MREF"):
            self.assertIn(token, SOURCE)

    def test_predicate_false_zeroed_device_record_remains_bound_to_host_target(self):
        target = {"function": {"mangled_name": "_Zexact"}, "target_instruction": {"nvbit_static_index": 8}}
        line = ("C16_TARGETED_NVBIT_FUNCTION_LAUNCH function_mangled=_Zexact launch_id=0 nvbit_static_index=8\n"
                "C16_TARGETED_NVBIT_MEMORY_RECORD function_mangled=_Zexact present=0 address=0x0 launch_id=0 "
                "nvbit_static_index=0 callback_count=9 predicate_true_count=0 active_lane_count=0 "
                "nonzero_mref_count=0 zero_mref_count=0\n")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tool.log"; path.write_text(line, encoding="utf-8")
            evidence = targeted_memory_evidence(path, target)
        self.assertEqual(evidence["exact_function_launch_count"], 1)
        self.assertEqual(evidence["predicate_true_count"], 0)
        self.assertEqual(evidence["observed_record_static_indices"], [0])


if __name__ == "__main__":
    unittest.main()
