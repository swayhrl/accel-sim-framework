#!/usr/bin/env python3
import csv
import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("e1_m1f_headroom_admission.py")
SPEC = importlib.util.spec_from_loader(
    "e1_m1f_headroom_admission",
    SourceFileLoader("e1_m1f_headroom_admission", str(MODULE_PATH)))
HEADROOM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HEADROOM)


class HeadroomAdmissionTest(unittest.TestCase):
    def test_frozen_hash_known_selected_and_filtered_witnesses(self):
        self.assertEqual(HEADROOM.THRESHOLD,
                         (1 << 64) * 131072 // 7426048)
        self.assertEqual(HEADROOM.stable_hash(1, 2212), 0x046AB7B4585923D0)
        self.assertLess(HEADROOM.stable_hash(1, 2212), HEADROOM.THRESHOLD)
        self.assertEqual(HEADROOM.stable_hash(1, 1186), 0xD92231F51D5C2EFB)
        self.assertGreaterEqual(HEADROOM.stable_hash(1, 1186), HEADROOM.THRESHOLD)

    def test_counter_delta_fails_on_decrease(self):
        self.assertEqual(HEADROOM.counter_delta({"a": 2}, {"a": 5}), {"a": 3})
        with self.assertRaises(HEADROOM.ContractError):
            HEADROOM.counter_delta({"a": 5}, {"a": 4})

    def test_response_sign(self):
        self.assertEqual(HEADROOM.response(100, 90), 0.1)
        self.assertEqual(HEADROOM.response(100, 110), -0.1)
        with self.assertRaises(HEADROOM.ContractError):
            HEADROOM.response(0, 0)

    def test_canonical_u64_hash_is_order_independent(self):
        self.assertEqual(HEADROOM.canonical_u64_sha([3, 1, 2]),
                         HEADROOM.canonical_u64_sha([2, 3, 1]))

    def test_target_localization_uses_scope_and_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for kernel, observed in ((10, False), (11, True)):
                target = root / "kernels" / str(kernel)
                target.mkdir(parents=True)
                (target / "summary.json").write_text(json.dumps({
                    "kernel_id": kernel, "decode_iteration": 2,
                    "semantic_layer": 0, "semantic_identity": "up_proj",
                    "expected_target_class": 1,
                    "expected_target_observed": observed,
                    "semantic_range_first_dynamic_kernel": 10,
                    "semantic_range_last_dynamic_kernel": 11,
                }))
            scope = {"range": {"first_dynamic_kernel": 10,
                               "last_dynamic_kernel": 11,
                               "kernel_ids": [10, 11]}}
            sequence = {
                kernel: {"decode_iteration": "2", "semantic_layer": "0",
                         "semantic_identity": "up_proj", "profile_range_active": "True"}
                for kernel in (10, 11)
            }
            self.assertEqual(HEADROOM.locate_target_kernel(
                scope, sequence, root, "range", 2, 1), 11)
            second = root / "kernels" / "10" / "summary.json"
            document = json.loads(second.read_text())
            document["expected_target_observed"] = True
            second.write_text(json.dumps(document))
            with self.assertRaises(HEADROOM.ContractError):
                HEADROOM.locate_target_kernel(scope, sequence, root, "range", 2, 1)

    def test_manifest_verification_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pack = root / "pack"
            pack.mkdir()
            payload = pack / "payload"
            payload.write_text("ok")
            digest = HEADROOM.sha256(payload)
            (pack / "SHA256SUMS").write_text(f"{digest}  payload\n")
            self.assertEqual(HEADROOM.verify_manifest(root, pack, "SHA256SUMS"),
                             {"payload": digest})
            payload.write_text("drift")
            with self.assertRaises(HEADROOM.ContractError):
                HEADROOM.verify_manifest(root, pack, "SHA256SUMS")


if __name__ == "__main__":
    unittest.main()
