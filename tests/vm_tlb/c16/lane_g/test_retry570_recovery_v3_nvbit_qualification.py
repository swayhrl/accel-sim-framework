"""Focused static contract checks for the Recovery-V3 NVBit qualification parent."""
from pathlib import Path
import sys
import tempfile
import unittest
import os
from argparse import Namespace
from unittest.mock import patch


SOURCE = (Path(__file__).resolve().parents[4] / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_nvbit_qualification.py").read_text(encoding="utf-8")
LANE = Path(__file__).resolve().parents[4] / "util/vm_tlb/c16/lane_g"
sys.path.insert(0, str(LANE))
from retry570_recovery_v3_nvbit_qualification import (  # noqa: E402
    ContractError, targeted_memory_evidence, validate_static_map, verify_code_object,
)
from runtime_native_runner import wrapper_owned_budget  # noqa: E402


class RecoveryV3QualificationContractTest(unittest.TestCase):
    def test_parent_owned_fresh_campaign_lease(self):
        for token in ("RecoveryV3CampaignLease", "initialize(", "write_parent_lease_start", "C16_G_PARENT_LEASE_TOKEN", "MeasurementActive(args.campaign_ledger", "child_acquired_second_lease"):
            self.assertIn(token, SOURCE)

    def test_only_identity_diagnostics_are_admitted(self):
        self.assertIn('"TARGETED_MEMORY_DISCRIMINATOR"', SOURCE)
        self.assertIn("scientific_eligible_for_timing\": False", SOURCE)
        self.assertIn("RECOVERY_V3_DIRECT_NVBIT_IDENTITY_QUALIFICATION_NOT_FOR_TIMING", SOURCE)
        self.assertIn("--route-b-llama-s0", SOURCE)
        self.assertIn("S0 requires the explicit frozen Route-B Llama inventory/static-map contract", SOURCE)
        self.assertIn('command.append("--route-b-llama-s0")', SOURCE)

    def test_static_map_closes_the_loaded_code_object(self):
        self.assertIn("--code-object-sha256", SOURCE)
        self.assertIn("C16_NVBIT_CODE_OBJECT_SHA256", SOURCE)

    def test_targeted_discriminator_is_parent_leased_and_counts_address_evidence(self):
        for token in ("TARGETED_MEMORY_TRACE", "targeted_memory_evidence", "predicate_true_count",
                      "nonzero_mref_count", "COMPLETE_VALID_ADDRESS_BEARING",
                      "COMPLETE_PREDICATED_OFF_TARGET", "COMPLETE_ZERO_ADDRESS_MREF"):
            self.assertIn(token, SOURCE)

    def test_phase_is_explicit_and_selects_its_own_recovery_authority(self):
        self.assertIn('parser.add_argument("--phase", choices=("PREFILL", "DECODE"), required=True)', SOURCE)
        self.assertIn('"RECOVERY_PREFILL" if args.phase == "PREFILL" else "RECOVERY_DECODE"', SOURCE)

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

    def test_actual_code_object_path_and_sha_are_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "libtorch_cuda.so"; path.write_bytes(b"exact-code-object")
            sha = __import__("hashlib").sha256(path.read_bytes()).hexdigest()
            self.assertEqual(verify_code_object(path, sha)["sha256"], sha)
            with self.assertRaises(ContractError):
                verify_code_object(path, "0" * 64)
            with self.assertRaises(ContractError):
                verify_code_object(path.with_name("absent.so"), sha)

    def test_static_map_requires_exact_function_code_object_and_unique_indices(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "map.tsv"; sha = "a" * 64
            header = ("nvbit_static_index\tvector_ordinal\tinstruction_offset\topcode\tmemory_space\t"
                      "is_load\tis_store\thas_mref\tsass\tfunction_full_name\t"
                      "function_mangled_name\tfunction_address\tlibtorch_cuda_sha256\n")
            row = lambda index: f"{index}\t{index}\t0\tLDG.E\tGLOBAL\t1\t0\t1\tLDG.E\tfull\t_Zexact\t0x1\t{sha}\n"
            path.write_text(header + row(8) + row(9), encoding="utf-8")
            self.assertEqual(validate_static_map(path, function="_Zexact", code_object_sha256=sha)["static_instruction_count"], 2)
            path.write_text(header + row(8) + row(8), encoding="utf-8")
            with self.assertRaises(ContractError):
                validate_static_map(path, function="_Zexact", code_object_sha256=sha)

    def test_bad_parent_token_and_absent_parent_lock_fail_closed(self):
        import hashlib
        import json
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "campaign.json"; ledger.write_text("{}", encoding="utf-8")
            receipt = Path(directory) / "parent.json"; identity = {"deployment_id": "d", "run_id": "r"}
            token = "valid-token"
            receipt.write_text(json.dumps({"schema_version": "C16_G_PARENT_LEASE_V1", "state": "ACTIVE_IMMUTABLE_START_RECEIPT",
                                            "parent_lease_id": "p", "lease_token_sha256": hashlib.sha256(token.encode()).hexdigest(),
                                            "ledger_path": str(ledger), "max_elapsed_seconds": 10, "valid_until_unix": 9999999999,
                                            "identity": identity, "operation_kind": "NVBIT", "wrapper_pid": 1,
                                            "child_must_prove_locked_ledger": True}), encoding="utf-8")
            args = Namespace(parent_lease_receipt=receipt, budget_ledger=ledger)
            with patch.dict(os.environ, {"C16_G_PARENT_LEASE_RECEIPT": str(receipt), "C16_G_PARENT_LEASE_TOKEN": "wrong"}, clear=False):
                with self.assertRaises(ContractError):
                    wrapper_owned_budget(args, identity)
            with patch.dict(os.environ, {"C16_G_PARENT_LEASE_RECEIPT": str(receipt), "C16_G_PARENT_LEASE_TOKEN": token}, clear=False):
                with self.assertRaisesRegex(ContractError, "not locked"):
                    wrapper_owned_budget(args, identity)


if __name__ == "__main__":
    unittest.main()
