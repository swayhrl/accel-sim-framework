#!/usr/bin/env python3
import csv
import json
import tempfile
import unittest
from pathlib import Path

from raw_ncu_consumer import METRICS, RawNcuError, consume


INPUT_SHA = "1" * 64
OUTPUT_SHA = "2" * 64
TARGET_KERNEL = "target_gemm_kernel"
PRESSURE_KERNEL = "pressure_reduce_kernel"


def write_base(path, target_range, kernels=None, omit_metric=None, bad_unit=None):
    kernels = kernels or [("1", TARGET_KERNEL, (100, 200, 300))]
    header = [
        "ID",
        "Process ID",
        "Kernel Name",
        "Block Size",
        "Grid Size",
        "profiler__replayer_passes",
        "NVTX Push/Pop_Range",
        *METRICS,
    ]
    if omit_metric:
        header.remove(omit_metric)
    units = ["", "", "", "", "", "", "", *["byte" for _ in METRICS]]
    if omit_metric:
        units.pop(7 + METRICS.index(omit_metric))
    if bad_unit:
        units[header.index(bad_unit)] = "Kbyte"
    rows = []
    for kernel_id, name, values in kernels:
        mapping = dict(zip(METRICS, values))
        rows.append(
            [
                kernel_id,
                "1234",
                name,
                "(32, 1, 1)",
                "(1, 1, 1)",
                "1",
                target_range,
                *[str(mapping[m]) for m in METRICS if m != omit_metric],
            ]
        )
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerow(units)
        writer.writerows(rows)


def write_session(path, target_range, input_sha=INPUT_SHA, output_sha=OUTPUT_SHA):
    path.write_text(
        " ".join(
            (
                "ncu --replay-mode application --cache-control none",
                f"--nvtx-include {target_range}/",
                "--metrics " + ",".join(METRICS),
                f'{{"input_sha256": "{input_sha}", "output_sha256": "{output_sha}"}}',
            )
        )
        + "\n",
        encoding="utf-8",
    )


def profile(state, base_name, session_name, target_range="TARGET_RANGE", expected=None):
    return {
        "point": "TEXT_UP_M1_RAW",
        "role": "up_proj",
        "M": 1,
        "implementation": "RAW_FP16",
        "state": state,
        "range_name": target_range,
        "input_sha256": INPUT_SHA,
        "output_sha256": OUTPUT_SHA,
        "expected_pass_count": 1,
        "expected_kernel_names": expected or [TARGET_KERNEL],
        "pressure_kernel_names": [] if state == "WARM" else [PRESSURE_KERNEL],
        "input_elements": 3584,
        "output_elements": 18944,
        "dense_weight_bytes": 135790592,
        "packed_weight_bytes": None,
        "base_path": base_name,
        "session_path": session_name,
    }


class RawNcuConsumerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def add_evidence(self, stem, target="TARGET_RANGE", kernels=None, **kwargs):
        base = self.root / f"{stem}_BASE.csv"
        session = self.root / f"{stem}_SESSION.csv"
        write_base(base, target, kernels=kernels, **kwargs)
        write_session(session, target)
        return base.name, session.name

    def test_warm_sparse_dense_are_unique_semantic_identities_and_ratioed(self):
        profiles = []
        for state, value in (
            ("WARM", 100),
            ("SPARSE_PAGE_PRESSURE", 110),
            ("DENSE_MEMORY_PRESSURE", 200),
        ):
            base, session = self.add_evidence(
                state, kernels=[("1", TARGET_KERNEL, (value, value * 2, value * 3))]
            )
            profiles.append(profile(state, base, session))
        result = consume({"schema_version": 1, "profiles": profiles}, self.root)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["authority"], "DIRECT_RAW_BASE_SESSION_ONLY")
        identities = [tuple(p["semantic_identity"].values()) for p in result["profiles"]]
        self.assertEqual(len(identities), len(set(identities)))
        dense_dram = next(
            row
            for row in result["state_ratios"]
            if row["state"] == "DENSE_MEMORY_PRESSURE"
            and row["metric_name"] == "dram__bytes.sum"
        )
        self.assertEqual(dense_dram["pressure_over_warm"], 2.0)
        self.assertTrue(all("intervention_state" in row for row in result["normalized_rows"]))

    def test_duplicate_semantic_state_fails(self):
        base, session = self.add_evidence("warm")
        item = profile("WARM", base, session)
        with self.assertRaisesRegex(RawNcuError, "duplicate semantic intervention state"):
            consume({"schema_version": 1, "profiles": [item, dict(item)]}, self.root)

    def test_pressure_kernel_inside_target_range_fails(self):
        base, session = self.add_evidence(
            "dense",
            kernels=[
                ("1", TARGET_KERNEL, (1, 2, 3)),
                ("2", PRESSURE_KERNEL, (4, 5, 6)),
            ],
        )
        item = profile(
            "DENSE_MEMORY_PRESSURE",
            base,
            session,
            expected=[TARGET_KERNEL, PRESSURE_KERNEL],
        )
        # Model producer inventory corruption while retaining independent pressure identity.
        item["expected_kernel_names"] = [TARGET_KERNEL]
        with self.assertRaisesRegex(RawNcuError, "pressure kernel entered target"):
            consume({"schema_version": 1, "profiles": [item]}, self.root)

    def test_missing_metric_fails(self):
        base, session = self.add_evidence("warm", omit_metric="dram__bytes.sum")
        with self.assertRaisesRegex(RawNcuError, "missing required columns"):
            consume(
                {"schema_version": 1, "profiles": [profile("WARM", base, session)]},
                self.root,
            )

    def test_unit_mismatch_fails(self):
        base, session = self.add_evidence("warm", bad_unit="lts__t_bytes.sum")
        with self.assertRaisesRegex(RawNcuError, "unit mismatch"):
            consume(
                {"schema_version": 1, "profiles": [profile("WARM", base, session)]},
                self.root,
            )

    def test_session_input_hash_mismatch_fails(self):
        base = self.root / "warm_BASE.csv"
        session = self.root / "warm_SESSION.csv"
        write_base(base, "TARGET_RANGE")
        write_session(session, "TARGET_RANGE", input_sha="3" * 64)
        with self.assertRaisesRegex(RawNcuError, "input_sha256 mismatch"):
            consume(
                {
                    "schema_version": 1,
                    "profiles": [profile("WARM", base.name, session.name)],
                },
                self.root,
            )

    def test_session_not_application_replay_fails(self):
        base, session = self.add_evidence("warm")
        session_path = self.root / session
        session_path.write_text(
            session_path.read_text().replace("application", "kernel"), encoding="utf-8"
        )
        with self.assertRaisesRegex(RawNcuError, "replay mode"):
            consume(
                {"schema_version": 1, "profiles": [profile("WARM", base, session)]},
                self.root,
            )

    def test_exact_target_range_required(self):
        base, session = self.add_evidence("warm", target="TARGET_RANGE_EXTRA")
        item = profile("WARM", base, session, target_range="TARGET_RANGE")
        # SESSION must bind the expected exact range before BASE selection can occur.
        with self.assertRaisesRegex(RawNcuError, "exact target range mismatch"):
            consume({"schema_version": 1, "profiles": [item]}, self.root)

    def test_cli_contract_has_no_summary_input(self):
        source = Path(__file__).with_name("raw_ncu_consumer.py").read_text(encoding="utf-8")
        self.assertNotIn("--producer-summary", source)
        self.assertNotIn("NCU_SEMANTIC_SUMS.tsv", source)


if __name__ == "__main__":
    unittest.main()
