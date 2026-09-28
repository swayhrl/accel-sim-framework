#!/usr/bin/env python3
"""Analyze SHiP-SW and generation-survival observer closeout canaries."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import analyze_strong_baselines as base


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def exact_pair(reference: Path, candidate: Path, label: str) -> dict:
    left = reference.read_text(encoding="utf-8", errors="replace")
    right = candidate.read_text(encoding="utf-8", errors="replace")
    left_metrics, right_metrics = base.metrics(left), base.metrics(right)
    need(left_metrics == right_metrics, f"{label}: scalar drift")
    left_behavior = base.canonical_behavior(left)
    right_behavior = base.canonical_behavior(right)
    need(left_behavior == right_behavior, f"{label}: behavior signature drift")
    return {
        "label": label, "status": "PASS", "metrics": left_metrics,
        "canonical_behavior_sha256": hashlib.sha256(
            "\n".join(left_behavior).encode()).hexdigest(),
        "reference_stdout_sha256": sha256(reference),
        "candidate_stdout_sha256": sha256(candidate),
    }


def ship_snapshot(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = [line for line in text.splitlines()
             if line.startswith("c16_strong_baseline_l2\t")]
    need(len(lines) == 16, "SHiP canary requires 16 subpartition rows")
    total = {}
    instances = set()
    for line in lines:
        numbers, strings = base.parse_tab_fields(line)
        need(strings["policy"] == "SHIP_SW", "SHiP policy dump drift")
        instances.add(numbers.pop("instance"))
        numbers.pop("drrip_psel")
        for key, value in numbers.items():
            total[key] = total.get(key, 0) + value
    need(instances == set(range(16)), "SHiP subpartition closure failed")
    need(total["ship_critical_allocations"] > 0,
         "SHiP critical allocation path inactive")
    need(total["ship_regular_predictions"] ==
         total["ship_critical_allocations"],
         "zero-initial SHCT should predict REGULAR in cold canary")
    need(total["ship_noncritical_no_train"] > 0,
         "SHiP non-critical exclusion not observed")
    need(total["ship_shct_nonzero"] == 0 and total["ship_shct_sum"] == 0,
         "cold canary unexpectedly trained SHCT")
    return {"schema": "C16_SHIP_SW_STYLE_BOUNDED_ACTIVATION_V1",
            "status": "PASS", "scope": "KERNEL_4490_MAX_50000_CYCLES",
            "performance_comparison": False, "summed_counters": total,
            "synthetic_training_required_for_training_qualification": True,
            "stdout_sha256": sha256(path)}


def observer_activation(path: Path) -> dict:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    need(rows, "observer activation log empty")
    need(all(row["accounting_closed"] == "1" for row in rows),
         "observer accounting did not close")
    need({row["label"] for row in rows} >= {"D2_L0_BEFORE", "D2_L0_MID"},
         "observer boundary activation absent")
    return {
        "schema": "C16_OLD_ADDRESS_SURVIVAL_OBSERVER_BOUNDED_ACTIVATION_V1",
        "status": "PASS", "scientific_survival_result": False,
        "bounded_rows": rows,
        "note": "Single-kernel bounded activation has no D1 snapshot; exact nonzero cases are qualified by synthetic generation tests.",
        "log_sha256": sha256(path),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--logs", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    need(not args.output_dir.exists(), "output directory must be fresh")

    neutrality = {
        "schema": "C16_CLOSEOUT_OFF_NEUTRALITY_V1", "status": "PASS",
        "comparisons": [
            exact_pair(args.runs / "REFERENCE_R0_OFF/stdout.log",
                       args.runs / "CANDIDATE_R0_OFF/stdout.log",
                       "R0_PARENT_VS_CLOSEOUT_OBSERVER_OFF"),
            exact_pair(args.runs / "REFERENCE_M1_OBSERVER_OFF/stdout.log",
                       args.runs / "CANDIDATE_M1_OBSERVER_OFF/stdout.log",
                       "M1_PARENT_VS_CLOSEOUT_OBSERVER_OFF"),
            exact_pair(args.runs / "CANDIDATE_M1_OBSERVER_OFF/stdout.log",
                       args.runs / "M1_OBSERVER_ON/stdout.log",
                       "M1_OBSERVER_OFF_VS_ON_ARCHITECTURAL"),
        ],
        "observer_participates_in_decisions": False,
    }
    ship = ship_snapshot(args.runs / "SHIP_SW/stdout.log")
    observer = observer_activation(args.runs / "M1_OBSERVER_ON/survival.tsv")
    tests = (args.logs / "closeout_tests_v3.log").read_text(errors="replace")
    for marker in ("C16_STRONG_BASELINES_POLICY_TEST_PASS",
                   "C16_STRONG_BASELINES_TAG_ARRAY_TEST_PASS",
                   "C16_OLD_ADDRESS_SURVIVAL_OBSERVER_TEST_PASS",
                   "C16_STRONG_BASELINES_TEST_SUITE_PASS"):
        need(marker in tests, f"missing test marker {marker}")

    args.output_dir.mkdir(parents=True)
    dump(args.output_dir / "OFF_NEUTRALITY.json", neutrality)
    dump(args.output_dir / "SHIP_SW_BOUNDED_ACTIVATION.json", ship)
    dump(args.output_dir / "SURVIVAL_OBSERVER_BOUNDED_ACTIVATION.json", observer)
    dump(args.output_dir / "CLOSEOUT_VALIDATION.json", {
        "schema": "C16_E1_STRONG_BASELINES_SURVIVAL_CLOSEOUT_VALIDATION_V1",
        "status": "PASS",
        "strong_baselines_status":
            "C16_STRONG_BASELINE_PREP_QUALIFIED_NO_FULL_TIMING",
        "observer_status":
            "C16_OLD_ADDRESS_SURVIVAL_OBSERVER_IMPLEMENTATION_QUALIFIED",
        "observer_qualified_is_scientific_result": False,
        "full_timing_run": False,
    })
    checksums = []
    for item in sorted(args.output_dir.iterdir()):
        checksums.append(f"{sha256(item)}  {item.name}")
    (args.output_dir / "SHA256SUMS").write_text(
        "\n".join(checksums) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(args.output_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
