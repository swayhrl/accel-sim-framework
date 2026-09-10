#!/usr/bin/env python3
"""Materialize compact FAST64.3 evidence after immutable pool validation.

This future-only observer never writes a live run directory or interacts with
simulator processes.  It waits for the pool's alias-v3 strict summary, then
copies that compact proof and generates the source-defined Base structural
companion in the repository evidence namespace.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import pathlib
import subprocess
import sys
import time


ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNS = pathlib.Path("/workspace/fast64-runs")
VALIDATED = RUNS / "validated"
OUT = ROOT / "docs/dtc_l1/fast64/generated/fast64_3_dynamic_base_v1"
EXTRACTOR = ROOT / "util/dtc_l1/extract_fast64_3_base_structural_metrics_v1.py"
CORE = "bbcbb5e7565417102087bc80b14c349b4e568c05"
FRAMEWORK = "037f008b330eb230353b60edf126d6be9f45afdc"
RUNTIME = "6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041"
OBSERVER = "2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e"
CLASSIFICATION = "PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE"
CONFIG_SHA = "1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde"
ROWS = (
    ("2DConvolution", "fast64_3_2DConvolution_base_cap8192_a1_v2"),
    ("Btree", "fast64_3_Btree_base_cap8192_a1_v2"),
    ("Gaussian", "fast64_3_Gaussian_base_cap8192_a1_v2"),
    ("Hotspot1", "fast64_3_Hotspot1_base_cap8192_a1_v2"),
    ("LUD", "fast64_3_LUD_base_cap8192_a1_v2"),
    ("NN", "fast64_3_NN_base_cap8192_a1_v2"),
    ("MRI-Q", "fast64_3_MRI-Q_base_cap8192_a1_v2"),
)


def emit(log: pathlib.Path, event: str, detail: str) -> None:
    line = f"{event}\tutc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{detail}\n"
    with log.open("a", encoding="utf-8") as stream:
        stream.write(line)
    print(line, end="", flush=True)


def stem(workload: str) -> str:
    return workload.upper().replace("-", "_")


def validate_and_materialize(summary: pathlib.Path, workload: str,
                             output_json: pathlib.Path, output_tsv: pathlib.Path) -> None:
    record = json.loads(summary.read_text(encoding="utf-8"))
    if record.get("schema") != "dtc_l1_summary_v1":
        raise RuntimeError("unexpected strict-summary schema")
    provenance = record.get("provenance", {})
    expected = {
        "core_sha": CORE,
        "framework_sha": FRAMEWORK,
        "observer_overlay_sha256": OBSERVER,
        "runtime_binary_sha256": RUNTIME,
        "result_classification": CLASSIFICATION,
        "config_sha256": CONFIG_SHA,
        "config_id": "FAST64_BASE_A1",
    }
    for key, value in expected.items():
        if provenance.get(key) != value:
            raise RuntimeError(f"strict-summary provenance mismatch {key}: {provenance.get(key)!r}")
    if provenance.get("workload_id", "").casefold() != workload.casefold():
        raise RuntimeError("strict-summary workload mismatch")
    if not record.get("immutable_attempt", {}).get("attempt_uuid"):
        raise RuntimeError("strict-summary immutable-attempt proof absent")
    metrics = record.get("metrics", {})
    required = (
        "DTC_L1_mode", "DTC_L1_lower_outstanding_cap",
        "DTC_L1_lower_requests_acquired", "DTC_L1_lower_requests_released",
        "DTC_L1_lower_outstanding", "DTC_L1_pib_admits", "DTC_L1_pib_retires",
        "DTC_L1_pib_occupancy", "DTC_L1_lower_cap_full_events",
        "gpu_tot_sim_cycle", "gpu_tot_sim_insn",
    )
    missing = [key for key in required if key not in metrics]
    if missing:
        raise RuntimeError("missing Base metrics: " + ", ".join(missing))
    if metrics["DTC_L1_mode"] != "PAPER_BASE" or metrics["DTC_L1_lower_outstanding_cap"] != 8192:
        raise RuntimeError("unexpected Base mode or lower-cap")
    if metrics["DTC_L1_lower_requests_acquired"] != metrics["DTC_L1_lower_requests_released"]:
        raise RuntimeError("lower conservation failure")
    if metrics["DTC_L1_pib_admits"] != metrics["DTC_L1_pib_retires"]:
        raise RuntimeError("PIB conservation failure")
    if metrics["DTC_L1_lower_outstanding"] != 0 or metrics["DTC_L1_pib_occupancy"] != 0:
        raise RuntimeError("nonzero terminal Base state")
    if metrics["DTC_L1_lower_cap_full_events"] != 0:
        raise RuntimeError("Base lower cap unexpectedly binding")
    if metrics["gpu_tot_sim_cycle"] <= 0 or metrics["gpu_tot_sim_insn"] <= 0:
        raise RuntimeError("nonpositive Base progress")
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_tsv.write_text(
        "schema\tFAST64_3_DYNAMIC_BASE_V1\n"
        "status\tFAST64_3_BASE_STRICT_VALID_PENDING_FAST64_3_ACCEPTANCE\n"
        f"workload\t{workload}\n"
        f"source_strict_summary\t{summary}\n"
        f"cycles\t{metrics['gpu_tot_sim_cycle']}\n"
        f"instructions\t{metrics['gpu_tot_sim_insn']}\n"
        f"lower_acquired\t{metrics['DTC_L1_lower_requests_acquired']}\n"
        f"lower_released\t{metrics['DTC_L1_lower_requests_released']}\n"
        f"pib_admits\t{metrics['DTC_L1_pib_admits']}\n"
        f"pib_retires\t{metrics['DTC_L1_pib_retires']}\n"
        "terminal_state\tlower=0;pib=0\n"
        "lower_cap_full_events\t0\n", encoding="utf-8")


def poll_once(log: pathlib.Path) -> bool:
    complete = 0
    for workload, row in ROWS:
        run = RUNS / row
        summary = VALIDATED / f"{row}.alias_v3.summary.json"
        output_json = OUT / f"{row}.json"
        output_tsv = OUT / f"FAST64_3_{stem(workload)}_BASE_DYNAMIC_V1.tsv"
        structural = OUT / f"FAST64_3_{stem(workload)}_BASE_STRUCTURAL_METRICS_V1.json"
        if output_json.is_file() and output_tsv.is_file() and structural.is_file():
            complete += 1
            continue
        if not (run / "RUN_TERMINAL.tsv").is_file():
            emit(log, "FAST64_3_DYNAMIC_BASE_V1_WAIT_TERMINAL", f"workload={workload} namespace={row}")
            continue
        if not summary.is_file():
            emit(log, "FAST64_3_DYNAMIC_BASE_V1_WAIT_STRICT_SUMMARY", f"workload={workload} namespace={row}")
            continue
        if not output_json.exists() and not output_tsv.exists():
            emit(log, "FAST64_3_DYNAMIC_BASE_V1_MATERIALIZE", f"workload={workload} namespace={row}")
            validate_and_materialize(summary, workload, output_json, output_tsv)
        elif not output_json.is_file() or not output_tsv.is_file():
            raise RuntimeError(f"partial compact output for {workload}")
        if not structural.is_file():
            perf = sorted(path for path in run.glob("perf_counter_*.csv.gz") if path.is_file())
            if len(perf) != 1:
                raise RuntimeError(f"expected one canonical perf stream for {workload}, found {len(perf)}")
            emit(log, "FAST64_3_DYNAMIC_BASE_V1_EXTRACT", f"workload={workload} namespace={row}")
            subprocess.run([str(EXTRACTOR), "--summary", str(output_json), "--perf", str(perf[0]), "--output", str(structural)], check=True)
        if not structural.is_file():
            raise RuntimeError(f"structural companion missing for {workload}")
        emit(log, "FAST64_3_DYNAMIC_BASE_V1_COLLECTED", f"workload={workload} namespace={row}")
        complete += 1
    return complete == len(ROWS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=pathlib.Path, required=True)
    parser.add_argument("--poll-seconds", type=int, default=120)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.poll_seconds < 1:
        parser.error("--poll-seconds must be positive")
    if not EXTRACTOR.is_file():
        raise RuntimeError("structural extractor missing")
    lock = RUNS / ".fast64_3_dynamic_base_evidence_v1.lock"
    with lock.open("w", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("FAST64_3_DYNAMIC_BASE_EVIDENCE_V1_ALREADY_ACTIVE") from error
        while True:
            if poll_once(args.log):
                emit(args.log, "FAST64_3_DYNAMIC_BASE_V1_COMPLETE", f"rows={len(ROWS)}")
                return 0
            if args.once:
                return 0
            time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
