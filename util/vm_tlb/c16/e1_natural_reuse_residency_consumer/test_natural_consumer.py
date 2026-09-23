#!/usr/bin/env python3
import csv
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from natural_consumer import (
    METRICS,
    NATURAL_MATRIX,
    NCU_MATRIX,
    NaturalConsumerError,
    analyze_natural_timing_rows,
    compare_natural_to_isolated,
    consume_natural_ncu,
    frame_integrated_interpretation,
    validate_natural_contract,
)


PREFIX = "a" * 64
INPUT = "b" * 64
OUTPUT = "c" * 64
TOKENS = [11, 22, 33, 44]


def occurrence(layer, role, decode):
    tag = f"C16_E1_NAT_L{layer}_{role.upper()}_D{decode}"
    # Make each SHA stable and unique while retaining 64 lowercase hex digits.
    input_sha = f"{layer + decode + (0 if role == 'up_proj' else 7):064x}"
    output_sha = f"{layer + decode + (20 if role == 'up_proj' else 40):064x}"
    return {
        "layer_index": layer, "role": role, "decode_index": decode, "M": 1,
        "implementation": "AWQ_FP16_INPUT",
        "generated_token_id": TOKENS[decode], "input_sha256": input_sha,
        "output_sha256": output_sha, "range_name": tag,
    }


def contract():
    occurrences = [occurrence(*key) for key in sorted(NATURAL_MATRIX)]
    return {
        "accepted_prefix_sha256": PREFIX,
        "prefix_token_sha256": PREFIX,
        "fresh_process_prefix_token_sha256": PREFIX,
        "generated_token_ids": list(TOKENS),
        "fresh_process_generated_token_ids": list(TOKENS),
        "occurrences": occurrences,
        "fresh_process_occurrences": deepcopy(occurrences),
    }


def timing_rows(reps=7):
    by_key = {(x["layer_index"], x["role"], x["decode_index"]): x for x in contract()["occurrences"]}
    rows = []
    for key in sorted(NATURAL_MATRIX):
        item = by_key[key]
        for rep in range(reps):
            rows.append({
                **item, "rep": rep, "prefix_token_sha256": PREFIX,
                "timing_ms": 1.0 + key[0] / 100 + key[2] / 10 + rep / 1000,
            })
    return rows


def write_base(path, range_name, value=100, bad_unit=None, wrong_range=None):
    header = ["ID", "Process ID", "Kernel Name", "profiler__replayer_passes", "NVTX Push/Pop_Range", *METRICS]
    units = ["", "", "", "", "", "byte", "byte", "byte"]
    if bad_unit:
        units[header.index(bad_unit)] = "Kbyte"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerow(units)
        writer.writerow(["1", "42", "target_kernel", "1", wrong_range or range_name, value, value * 2, value * 3])


def write_session(path, range_name, replay="application", cache="none"):
    path.write_text(
        f"ncu --replay-mode {replay} --cache-control {cache} --nvtx-include {range_name}/ "
        f"--metrics {','.join(METRICS)}\n", encoding="utf-8"
    )


def write_profile(path, item, **overrides):
    receipt = {
        "status": "PASS", "layer_index": item["layer_index"], "role": item["role"],
        "decode_index": item["decode_index"], "M": 1,
        "implementation": "AWQ_FP16_INPUT",
        "generated_token_id": item["generated_token_id"], "range": item["range_name"],
        "input_sha256": item["input_sha256"], "output_sha256": item["output_sha256"],
        "prefix_token_sha256": PREFIX,
    }
    receipt.update(overrides)
    path.write_text("==PROF== raw\n" + json.dumps(receipt) + "\n", encoding="utf-8")


class NaturalConsumerTests(unittest.TestCase):
    def test_contract_and_timing_full_matrix(self):
        result = analyze_natural_timing_rows(timing_rows(), contract())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(len(result["points"]), 12)
        self.assertEqual(result["points"][0]["statistics"]["sample_count"], 7)

    def test_fresh_process_token_mismatch_fails(self):
        bad = contract()
        bad["fresh_process_generated_token_ids"][2] += 1
        with self.assertRaisesRegex(NaturalConsumerError, "token sequence mismatch"):
            validate_natural_contract(bad)

    def test_fresh_process_occurrence_sha_mismatch_fails(self):
        bad = contract()
        bad["fresh_process_occurrences"][0]["input_sha256"] = "f" * 64
        with self.assertRaisesRegex(NaturalConsumerError, "occurrence SHA/identity mismatch"):
            validate_natural_contract(bad)

    def test_non_m1_wrong_identity_and_range_fail(self):
        for field, value, message in (
            ("M", 2, "M mismatch"),
            ("layer_index", 1, "wrong layer/role/decode"),
            ("range_name", "WRONG", "range_name mismatch"),
        ):
            rows = timing_rows()
            rows[0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(NaturalConsumerError, message):
                analyze_natural_timing_rows(rows, contract())

    def test_duplicate_and_missing_timing_occurrence_fail(self):
        rows = timing_rows()
        with self.assertRaisesRegex(NaturalConsumerError, "duplicate timing"):
            analyze_natural_timing_rows(rows + [dict(rows[0])], contract())
        with self.assertRaisesRegex(NaturalConsumerError, "missing/extra|missing/extra timing repetition"):
            analyze_natural_timing_rows(rows[:-1], contract())

    def test_sha_drift_and_nonfinite_timing_fail(self):
        rows = timing_rows()
        rows[0]["input_sha256"] = "d" * 64
        with self.assertRaisesRegex(NaturalConsumerError, "input_sha256 mismatch"):
            analyze_natural_timing_rows(rows, contract())
        rows = timing_rows()
        rows[0]["timing_ms"] = "nan"
        with self.assertRaisesRegex(NaturalConsumerError, "nonfinite"):
            analyze_natural_timing_rows(rows, contract())

    def test_comparator_unclamped_and_zero_denominator(self):
        natural = [{"layer_index": 0, "role": "up_proj", "decode_index": 0,
                    "implementation": "AWQ_FP16_INPUT", "M": 1,
                    "timing_ms": 4, "dram_bytes": 50}]
        refs = [{"role": "up_proj", "implementation": "AWQ_FP16_INPUT", "M": 1,
                 "warm_timing_ms": 1, "dense_timing_ms": 2,
                 "warm_dram_bytes": 10, "dense_dram_bytes": 10}]
        got = compare_natural_to_isolated(natural, refs)["comparisons"][0]
        self.assertEqual(got["timing"]["warm_fraction"], 3.0)
        self.assertTrue(got["timing"]["outside_bracket"])
        self.assertIsNone(got["dram"]["warm_fraction"])
        self.assertEqual(got["dram"]["status"], "UNDEFINED_ZERO_DENOMINATOR")

    def test_case_framing_keeps_effects_separate(self):
        result = frame_integrated_interpretation(
            refill_clear=True, natural_warm_like=False, role_dependent=True,
            capacity_observation="knee differs by size",
            access_policy_observation="role-dependent",
            natural_interference_observation="dense-like natural interval",
        )
        self.assertEqual(result["primary_case"], "CASE_B_ISOLATED_REFILL_NATURAL_DENSE_LIKE")
        self.assertTrue(result["case_d_role_dependent"])
        self.assertFalse(result["mechanism_authorized"])
        self.assertEqual(len(result["separable_observations"]), 3)


class NaturalNcuTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def document(self, mutate=None):
        occurrences = {(x["layer_index"], x["role"], x["decode_index"]): x for x in contract()["occurrences"]}
        profiles = []
        for number, key in enumerate(sorted(NCU_MATRIX)):
            item = occurrences[key]
            stem = f"p{number}"
            base, session, profile = (self.root / f"{stem}_BASE.csv", self.root / f"{stem}_SESSION.csv", self.root / f"{stem}_PROFILE.log")
            write_base(base, item["range_name"], value=100 + number)
            write_session(session, item["range_name"])
            write_profile(profile, item)
            profiles.append({
                **item, "expected_kernel_names": ["target_kernel"], "expected_pass_count": 1,
                "base_path": base.name, "session_path": session.name, "profile_path": profile.name,
            })
        document = {"schema_version": 1, "contract": contract(), "profiles": profiles}
        if mutate:
            mutate(document, self.root)
        return document

    def test_three_source_ncu_closes_seven_profiles(self):
        result = consume_natural_ncu(self.document(), self.root)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["authority"], "DIRECT_RAW_BASE_SESSION_PROFILE_ONLY")
        self.assertEqual(len(result["profiles"]), 7)
        self.assertIn("decode_index", result["semantic_identity_fields"])
        self.assertEqual(result["profiles"][0]["base"]["metric_sums"]["dram__bytes.sum"], "300")

    def test_duplicate_or_missing_ncu_occurrence_fails(self):
        duplicate = self.document(lambda doc, _root: doc["profiles"].append(deepcopy(doc["profiles"][0])))
        with self.assertRaisesRegex(NaturalConsumerError, "duplicate NCU"):
            consume_natural_ncu(duplicate, self.root)
        missing = self.document(lambda doc, _root: doc["profiles"].pop())
        with self.assertRaisesRegex(NaturalConsumerError, "NCU occurrence matrix mismatch"):
            consume_natural_ncu(missing, self.root)

    def test_session_replay_cache_and_range_mismatch_fail(self):
        def bad_replay(doc, root):
            p = root / doc["profiles"][0]["session_path"]
            p.write_text(p.read_text().replace("application", "kernel"), encoding="utf-8")
        with self.assertRaisesRegex(NaturalConsumerError, "replay mode"):
            consume_natural_ncu(self.document(bad_replay), self.root)

        def bad_range(doc, root):
            p = root / doc["profiles"][0]["session_path"]
            p.write_text(p.read_text().replace(doc["profiles"][0]["range_name"], "WRONG"), encoding="utf-8")
        with self.assertRaisesRegex(NaturalConsumerError, "range mismatch"):
            consume_natural_ncu(self.document(bad_range), self.root)

    def test_profile_sha_and_decode_identity_mismatch_fail(self):
        def bad_profile(doc, root):
            item = doc["profiles"][0]
            write_profile(root / item["profile_path"], item, input_sha256="f" * 64)
        with self.assertRaisesRegex(NaturalConsumerError, "PROFILE natural identity mismatch"):
            consume_natural_ncu(self.document(bad_profile), self.root)

    def test_base_unit_inventory_and_exact_range_fail(self):
        def bad_unit(doc, root):
            item = doc["profiles"][0]
            write_base(root / item["base_path"], item["range_name"], bad_unit="dram__bytes.sum")
        with self.assertRaisesRegex(NaturalConsumerError, "unit mismatch"):
            consume_natural_ncu(self.document(bad_unit), self.root)

        def bad_inventory(doc, _root):
            doc["profiles"][0]["expected_kernel_names"] = ["another_kernel"]
        with self.assertRaisesRegex(NaturalConsumerError, "kernel inventory mismatch"):
            consume_natural_ncu(self.document(bad_inventory), self.root)

        def bad_base_range(doc, root):
            item = doc["profiles"][0]
            write_base(root / item["base_path"], item["range_name"], wrong_range=item["range_name"] + "_EXTRA")
        with self.assertRaisesRegex(NaturalConsumerError, "no exact target range"):
            consume_natural_ncu(self.document(bad_base_range), self.root)

    def test_no_producer_summary_authority(self):
        source = Path(__file__).with_name("natural_consumer.py").read_text(encoding="utf-8")
        self.assertNotIn("NATURAL_NCU_SUMMARY.tsv", source)
        self.assertNotIn("producer-summary", source)


if __name__ == "__main__":
    unittest.main()
