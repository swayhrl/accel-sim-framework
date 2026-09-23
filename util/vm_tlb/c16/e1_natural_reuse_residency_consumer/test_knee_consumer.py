#!/usr/bin/env python3
import csv
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from knee_consumer import (
    DEVICE_L2_BYTES,
    DOSE_SETS_MIB,
    MIB,
    PACKED_STATE_BYTES,
    KneeError,
    analyze_timing_rows,
    consume,
    consume_ncu_profiles,
)


ROLE_HASHES = {
    "q_proj": ("1" * 64, "2" * 64),
    "down_proj": ("3" * 64, "4" * 64),
    "up_proj": ("5" * 64, "6" * 64),
}
TIMING_KNEES = {"q_proj": 60, "down_proj": 28, "up_proj": 30}
DRAM_KNEES = {"q_proj": 64, "down_proj": 32, "up_proj": 36}


def timing_rows():
    rows = []
    for role, doses in DOSE_SETS_MIB.items():
        input_sha, output_sha = ROLE_HASHES[role]
        for dose in doses:
            elapsed = 1.1 if dose >= TIMING_KNEES[role] else 1.0
            for rep in range(7):
                rows.append({
                    "domain": "TEXT", "role": role, "M": "1",
                    "implementation": "AWQ_FP16_INPUT",
                    "pressure_mode": "DENSE_PREFIX_READ",
                    "dose_mib": str(dose),
                    "pressure_prefix_bytes": str(dose * MIB),
                    "rep": str(rep), "timing_ms": str(elapsed),
                    "input_sha256": input_sha, "output_sha256": output_sha,
                })
    return rows


def dram_for(role, dose):
    return 4_000_000 if dose >= DRAM_KNEES[role] else 80_000


def write_base(path, target_range, target_kernel, dram, unit="byte", pressure=False):
    header = ["ID", "Process ID", "Kernel Name", "profiler__replayer_passes",
              "NVTX Push/Pop_Range", "dram__bytes.sum"]
    rows = [["1", "123", target_kernel, "1", target_range, str(dram)]]
    if pressure:
        rows.append(["2", "123", "pressure_kernel", "1", target_range, "10"])
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerow(["", "", "", "", "", unit])
        writer.writerows(rows)


def write_session(path, target_range, replay="application", metric="dram__bytes.sum"):
    path.write_text(
        f"ncu --replay-mode {replay} --cache-control none "
        f"--nvtx-include {target_range}/ --metrics {metric}\n", encoding="utf-8")


def write_profile(path, spec, **changes):
    receipt = {
        "status": "PASS", "role": spec["role"], "M": 1,
        "implementation": "AWQ_FP16_INPUT", "pressure_mode": "DENSE_PREFIX_READ",
        "dose_mib": spec["dose_mib"],
        "pressure_prefix_bytes": spec["pressure_prefix_bytes"],
        "range": spec["range_name"], "input_sha256": spec["input_sha256"],
        "output_sha256": spec["output_sha256"],
    }
    receipt.update(changes)
    path.write_text("==PROF== synthetic\n" + json.dumps(receipt) + "\n", encoding="utf-8")


class Fixture:
    def __init__(self, root):
        self.root = root
        self.rows = timing_rows()
        self.timing_path = root / "RAW_KNEE_TIMING.tsv"
        self.write_timing()
        self.profiles = []
        for role, doses in DOSE_SETS_MIB.items():
            input_sha, output_sha = ROLE_HASHES[role]
            for dose in doses:
                stem = f"{role}_{dose}"
                target_range = f"C16_E1_KNEE_{role.upper()}_{dose}MIB"
                spec = {
                    "domain": "TEXT", "role": role, "M": 1,
                    "implementation": "AWQ_FP16_INPUT",
                    "pressure_mode": "DENSE_PREFIX_READ", "dose_mib": dose,
                    "pressure_prefix_bytes": dose * MIB, "range_name": target_range,
                    "input_sha256": input_sha, "output_sha256": output_sha,
                    "expected_pass_count": 1,
                    "expected_kernel_names": [f"target_{role}"],
                    "pressure_kernel_names": ["pressure_kernel"],
                    "base_path": f"{stem}_BASE.csv",
                    "session_path": f"{stem}_SESSION.csv",
                    "profile_path": f"{stem}_PROFILE.log",
                }
                write_base(root / spec["base_path"], target_range,
                           f"target_{role}", dram_for(role, dose))
                write_session(root / spec["session_path"], target_range)
                write_profile(root / spec["profile_path"], spec)
                self.profiles.append(spec)

    def write_timing(self):
        with self.timing_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(self.rows[0]), delimiter="\t")
            writer.writeheader()
            writer.writerows(self.rows)

    def contract(self):
        return {"schema_version": 1, "timing_tsv": self.timing_path.name,
                "profiles": self.profiles}


class TimingTests(unittest.TestCase):
    def test_exact_matrix_stats_ratios_and_materiality(self):
        result = analyze_timing_rows(timing_rows())
        self.assertEqual(result["status"], "PASS")
        q = next(item for item in result["roles"] if item["role"] == "q_proj")
        self.assertEqual([x["dose_mib"] for x in q["doses"]], list(DOSE_SETS_MIB["q_proj"]))
        self.assertEqual(q["doses"][0]["sample_count"], 7)
        knee = next(x for x in q["doses"] if x["dose_mib"] == 60)
        self.assertAlmostEqual(knee["ratio_to_0MiB"], 1.1)
        self.assertTrue(knee["material_vs_0MiB"])

    def test_missing_duplicate_rep_and_dose_fail(self):
        with self.assertRaisesRegex(KneeError, "repetition matrix mismatch"):
            analyze_timing_rows(timing_rows()[:-1])
        rows = timing_rows(); rows.append(dict(rows[0]))
        with self.assertRaisesRegex(KneeError, "duplicate role/dose/rep"):
            analyze_timing_rows(rows)
        rows = [r for r in timing_rows() if not (r["role"] == "q_proj" and r["dose_mib"] == "32")]
        with self.assertRaisesRegex(KneeError, "timing point matrix mismatch"):
            analyze_timing_rows(rows)

    def test_nonfinite_identity_and_prefix_fail(self):
        mutations = (
            ("timing_ms", "nan", "nonpositive/nonfinite"),
            ("role", "bad", "wrong role"),
            ("implementation", "RAW_FP16", "wrong point identity"),
            ("pressure_prefix_bytes", "1", "wrong pressure prefix"),
            ("output_sha256", "f" * 64, "identity drift"),
        )
        for field, value, message in mutations:
            with self.subTest(field=field):
                rows = timing_rows(); rows[0][field] = value
                with self.assertRaisesRegex(KneeError, message):
                    analyze_timing_rows(rows)


class IntegratedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fixture = Fixture(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_complete_raw_closure(self):
        result = consume(self.fixture.contract(), self.root)
        self.assertFalse(result["authority"]["producer_summary_used"])
        self.assertFalse(result["exact_knee_equality_is_pass_gate"])
        for item in result["roles"]:
            role = item["role"]
            residual = DEVICE_L2_BYTES - PACKED_STATE_BYTES[role]
            self.assertEqual(item["nominal_residual_l2_bytes"], residual)
            self.assertEqual(item["first_dram_over_1MiB_and_10pct_packed_mib"], DRAM_KNEES[role])
            self.assertEqual(item["first_material_timing_dose_mib"], TIMING_KNEES[role])
            self.assertAlmostEqual(item["observed_dram_knee_minus_nominal_residual_l2_mib"],
                                   DRAM_KNEES[role] - residual / MIB)

    def test_duplicate_missing_ncu_dose_fail(self):
        profiles = deepcopy(self.fixture.profiles); profiles.append(deepcopy(profiles[0]))
        with self.assertRaisesRegex(KneeError, "duplicate semantic NCU dose"):
            consume_ncu_profiles(profiles, self.root)
        with self.assertRaisesRegex(KneeError, "NCU point matrix mismatch"):
            consume_ncu_profiles(self.fixture.profiles[:-1], self.root)

    def test_metric_unit_session_and_profile_fail(self):
        spec = self.fixture.profiles[0]
        write_session(self.root / spec["session_path"], spec["range_name"], metric="lts__t_bytes.sum")
        with self.assertRaisesRegex(KneeError, "metric set mismatch"):
            consume_ncu_profiles(self.fixture.profiles, self.root)
        write_session(self.root / spec["session_path"], spec["range_name"])
        write_base(self.root / spec["base_path"], spec["range_name"],
                   spec["expected_kernel_names"][0], 80_000, unit="Kbyte")
        with self.assertRaisesRegex(KneeError, "metric/unit mismatch"):
            consume_ncu_profiles(self.fixture.profiles, self.root)
        write_base(self.root / spec["base_path"], spec["range_name"],
                   spec["expected_kernel_names"][0], 80_000)
        write_session(self.root / spec["session_path"], spec["range_name"], replay="kernel")
        with self.assertRaisesRegex(KneeError, "replay mode mismatch"):
            consume_ncu_profiles(self.fixture.profiles, self.root)
        write_session(self.root / spec["session_path"], spec["range_name"])
        write_profile(self.root / spec["profile_path"], spec, dose_mib=999)
        with self.assertRaisesRegex(KneeError, "PROFILE identity mismatch"):
            consume_ncu_profiles(self.fixture.profiles, self.root)

    def test_wrong_ncu_role_implementation_prefix_fail(self):
        for field, value, message in (
            ("role", "bad", "wrong role"),
            ("implementation", "RAW_FP16", "wrong point identity"),
            ("pressure_prefix_bytes", 1, "wrong pressure prefix"),
        ):
            with self.subTest(field=field):
                profiles = deepcopy(self.fixture.profiles); profiles[0][field] = value
                with self.assertRaisesRegex(KneeError, message):
                    consume_ncu_profiles(profiles, self.root)

    def test_pressure_kernel_leak_and_cross_source_sha_drift_fail(self):
        spec = self.fixture.profiles[0]
        spec["expected_kernel_names"].append("pressure_kernel")
        write_base(self.root / spec["base_path"], spec["range_name"],
                   spec["expected_kernel_names"][0], 80_000, pressure=True)
        with self.assertRaisesRegex(KneeError, "inventories overlap"):
            consume_ncu_profiles(self.fixture.profiles, self.root)
        # Restore fixture, then make NCU internally coherent but unlike timing.
        self.tearDown(); self.setUp()
        for point in self.fixture.profiles:
            if point["role"] == "q_proj":
                point["input_sha256"] = "a" * 64
                write_profile(self.root / point["profile_path"], point)
        with self.assertRaisesRegex(KneeError, "timing/NCU identity drift"):
            consume(self.fixture.contract(), self.root)

    def test_zero_dram_ratio_is_undefined(self):
        spec = next(p for p in self.fixture.profiles if p["role"] == "q_proj" and p["dose_mib"] == 0)
        write_base(self.root / spec["base_path"], spec["range_name"],
                   spec["expected_kernel_names"][0], 0)
        q = next(x for x in consume(self.fixture.contract(), self.root)["roles"] if x["role"] == "q_proj")
        self.assertIsNone(q["doses"][0]["dram_ratio_to_0MiB"])


if __name__ == "__main__":
    unittest.main()
