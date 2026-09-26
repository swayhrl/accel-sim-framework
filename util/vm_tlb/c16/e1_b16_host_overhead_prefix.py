#!/usr/bin/env python3
"""Fail-closed analysis for the non-scientific B16 host-overhead prefix screen."""

import argparse
import hashlib
import json
import lzma
import re
import statistics
from pathlib import Path


CASES = (
    "BASELINE_M1",
    "MEMSTAT0",
    "PTXLINE0",
    "RUNTIME10000",
    "R0_CURRENT",
    "PREDECOMPRESSED",
)
LAUNCH_RE = re.compile(
    r"^launching kernel name: (.*) uid: ([0-9]+) cuda_stream_id: ([0-9]+)$"
)
STAT_RE = re.compile(
    r"^(gpu_tot_sim_cycle|gpu_tot_sim_insn|gpu_tot_issued_cta) = ([0-9]+)$"
)


def require(value, message):
    if not value:
        raise RuntimeError(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_sums(run_dir):
    sums = run_dir / "OUTPUT_SHA256SUMS"
    require(sums.is_file(), f"missing {sums}")
    result = {}
    for line in sums.read_text().splitlines():
        expected, relative = line.split(maxsplit=1)
        relative = relative.lstrip(" *")
        candidate = run_dir / relative
        require(candidate.is_file(), f"missing raw output {candidate}")
        require(sha256(candidate) == expected, f"SHA mismatch {candidate}")
        result[relative] = expected
    return result


def parse_output(path):
    launches = []
    completed = {}
    mechanism = []
    current_uid = None
    terminal = False
    for raw in path.read_text(encoding="utf-8", errors="strict").splitlines():
        launch = LAUNCH_RE.match(raw)
        if launch:
            current_uid = int(launch.group(2))
            launches.append((current_uid, int(launch.group(3)), launch.group(1)))
            continue
        stat = STAT_RE.match(raw)
        if stat and current_uid is not None:
            completed.setdefault(current_uid, {})[stat.group(1)] = int(stat.group(2))
            continue
        if raw.startswith("oracle_elastic_l2"):
            mechanism.append(raw)
        if "GPGPU-Sim: *** exit detected ***" in raw:
            terminal = True
    require(len(launches) == 16, f"launch count drift in {path}")
    require([row[0] for row in launches] == list(range(1, 17)),
            f"UID sequence drift in {path}")
    require(set(completed) == set(range(1, 17)), f"completion coverage drift in {path}")
    required = {"gpu_tot_sim_cycle", "gpu_tot_sim_insn", "gpu_tot_issued_cta"}
    require(all(set(row) == required for row in completed.values()),
            f"stat coverage drift in {path}")
    require(terminal, f"terminal marker missing in {path}")
    return {
        "launches": launches,
        "completed": completed,
        "mechanism_lines": mechanism,
        "terminal": terminal,
    }


def run_summary(run_dir, condition):
    receipt_path = run_dir / "RUN_RECEIPT.json"
    require(receipt_path.is_file(), f"missing {receipt_path}")
    receipt = json.loads(receipt_path.read_text())
    require(receipt["condition"] == condition, f"condition drift {receipt_path}")
    require(receipt["status"] == "PASS" and receipt["exit_code"] == 0,
            f"failed receipt {receipt_path}")
    require(receipt["terminal_exit_detected"] is True, f"receipt terminal drift {receipt_path}")
    verified = verify_sums(run_dir)
    parsed = parse_output(run_dir / "simulator.stdout")
    return {
        "receipt": receipt,
        "receipt_sha256": sha256(receipt_path),
        "verified_outputs": verified,
        "parsed": parsed,
    }


def payload_equivalence(root):
    compressed_list = (root / "stage/kernelslist.g").read_text().splitlines()
    plain_list = (root / "stage_uncompressed/kernelslist.g").read_text().splitlines()
    require(len(compressed_list) == len(plain_list) == 16, "trace list count drift")
    rows = []
    for compressed, plain in zip(compressed_list, plain_list):
        require(compressed.removesuffix(".xz") == plain, "decompressed filename drift")
        source = root / "stage" / compressed
        target = root / "stage_uncompressed" / plain
        expected = hashlib.sha256(lzma.open(source, "rb").read()).hexdigest()
        actual = sha256(target)
        require(expected == actual, f"decompressed payload mismatch {plain}")
        rows.append({"compressed": compressed, "plain": plain, "payload_sha256": actual})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    require((args.root / "SUITE_COMPLETE").read_text().strip() == "PASS",
            "suite incomplete")

    runs = {}
    for condition in CASES:
        runs[condition] = [
            run_summary(args.root / f"{condition}_rep{rep}", condition)
            for rep in (1, 2, 3)
        ]

    reference = runs["BASELINE_M1"][0]["parsed"]
    case_results = {}
    baseline_median = statistics.median(
        row["receipt"]["elapsed_ns"] for row in runs["BASELINE_M1"]
    )
    for condition in CASES:
        elapsed = [row["receipt"]["elapsed_ns"] for row in runs[condition]]
        identity_exact = all(row["parsed"]["launches"] == reference["launches"]
                             for row in runs[condition])
        stats_exact = all(row["parsed"]["completed"] == reference["completed"]
                          for row in runs[condition])
        termination_exact = all(row["parsed"]["terminal"] for row in runs[condition])
        mechanism_lines_exact = all(
            row["parsed"]["mechanism_lines"] == reference["mechanism_lines"]
            for row in runs[condition]
        )
        median_ns = statistics.median(elapsed)
        speedup = (baseline_median - median_ns) / baseline_median
        case_results[condition] = {
            "elapsed_seconds": [value / 1e9 for value in elapsed],
            "median_elapsed_seconds": median_ns / 1e9,
            "host_speedup_fraction_vs_M1_baseline": speedup,
            "kernel_identity_exact": identity_exact,
            "cycles_instructions_CTA_exact": stats_exact,
            "termination_exact": termination_exact,
            "diagnostic_mechanism_lines_exact": mechanism_lines_exact,
            "diagnostic_mechanism_lines_observable": bool(reference["mechanism_lines"]),
            "receipt_sha256": [row["receipt_sha256"] for row in runs[condition]],
            "raw_output_sha256": [row["verified_outputs"] for row in runs[condition]],
        }

    screened = [
        condition for condition in ("MEMSTAT0", "PTXLINE0", "RUNTIME10000", "PREDECOMPRESSED")
        if case_results[condition]["host_speedup_fraction_vs_M1_baseline"] >= 0.20
        and case_results[condition]["kernel_identity_exact"]
        and case_results[condition]["cycles_instructions_CTA_exact"]
        and case_results[condition]["termination_exact"]
    ]
    payloads = payload_equivalence(args.root)
    result = {
        "schema": "C16_E1_B16_HOST_OVERHEAD_PREFIX_AUDIT_V1",
        "status": "PASS",
        "raw_provenance": {
            "root": str(args.root),
            "suite_complete_sha256": sha256(args.root / "SUITE_COMPLETE"),
            "input_sha256s_sha256": sha256(args.root / "INPUT_SHA256SUMS"),
            "runner_sha256": sha256(args.root / "run_one.sh"),
            "suite_sha256": sha256(args.root / "run_suite.sh"),
            "all_run_receipts_and_outputs_verified": True,
        },
        "scientific_authority": False,
        "prefix": {
            "simulator_UID_first": 1,
            "simulator_UID_last": 16,
            "global_dynamic_kernel_first": 2926,
            "global_dynamic_kernel_last": 2941,
            "kernel_count": 16,
            "contains_qweight_target_range": False,
        },
        "affinity": {"CPU": 300, "CORE": 44, "SOCKET": 0, "NODE": 0,
                     "distinct_from_all_three_long_run_physical_cores": True},
        "case_results": case_results,
        "decompressed_payload_equivalence": {"status": "PASS", "files": payloads},
        "second_stage_candidates_meeting_20_percent_screen": screened,
        "future_run_admission": {
            "status": "NOT_ADMITTED_FROM_SMALL_PREFIX_ALONE",
            "requires_target_range_second_stage": True,
            "requires_cycles_instructions_CTA_termination_output_exact": True,
            "requires_mechanism_decisions_exact": True,
        },
        "current_primary_restart": {
            "permitted_by_this_audit": False,
            "performed": False,
            "reason": "small non-target prefix cannot satisfy final host-only admission even if a wall-time screen crosses 20 percent",
        },
        "interpretation": {
            "MEMSTAT0": "generic memory-stat hot-path screen only",
            "PTXLINE0": "PTX/source-line-stat hot-path screen only",
            "RUNTIME10000": "runtime-stat frequency hot-path screen only",
            "PREDECOMPRESSED": "trace decompression/parser screen with byte-exact decompressed payloads",
            "R0_CURRENT": "measurement of current enabled-but-inactive oracle path versus disabled control; not an optimization candidate",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": result["status"],
        "candidates": screened,
        "medians": {key: value["median_elapsed_seconds"] for key, value in case_results.items()},
    }, sort_keys=True))


if __name__ == "__main__":
    main()
