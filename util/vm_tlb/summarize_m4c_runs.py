#!/usr/bin/env python3
"""Validate and summarize immutable-input M4C/M4B replay directories."""

import argparse
import csv
import re
from pathlib import Path


METRICS = (
    "gpu_tot_sim_cycle", "gpu_tot_sim_insn", "gpu_tot_ipc",
    "vm_pte_requests", "vm_pte_responses", "vm_pte_response_misassociations",
    "vm_translation_waiter_registrations", "vm_translation_waiter_wakeups",
    "vm_object_attribution_conservation_pass", "vm_l1_tlb_accesses",
    "vm_l1_tlb_hits", "vm_l1_tlb_misses", "vm_l2_tlb_accesses",
    "vm_l2_tlb_hits", "vm_l2_tlb_misses", "vm_translation_mshr_allocations",
    "vm_translation_mshr_merges", "vm_translation_mshr_full_events",
    "vm_translation_pwq_full_events", "vm_translation_walk_starts",
    "vm_pwc_accesses", "vm_pwc_hits", "vm_pwc_misses",
)


def manifest(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text().splitlines()[1:]:
        if "\t" in line:
            key, value = line.split("\t", 1)
            data[key] = value
    return data


def last_value(lines: list[str], key: str) -> str:
    prefix = key + " = "
    values = [line[len(prefix):].strip() for line in lines if line.startswith(prefix)]
    return values[-1] if values else "MISSING"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-level", type=int, default=2)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("FAIL: refusing to overwrite summary")
    rows: list[list[str]] = []
    failures: list[str] = []
    for run_dir in sorted(path.parent for path in args.runs_root.glob("*/RUN_MANIFEST.tsv")):
        data = manifest(run_dir / "RUN_MANIFEST.tsv")
        log_path = run_dir / "run.log"
        if not log_path.is_file():
            failures.append(f"{run_dir}: missing run.log")
            continue
        lines = log_path.read_text(errors="strict").splitlines()
        expected = sum(1 for line in (run_dir / "traces/kernelslist.g").read_text().splitlines() if line)
        completed = sum(1 for line in lines if line.startswith("Processing kernel "))
        status = data.get("simulator_exit_status", "MISSING")
        telemetry = sum(1 for line in lines if line.startswith("m4c_telemetry_schema ="))
        profile = data.get("profile", "MISSING")
        vm_metrics = {
            metric: last_value(lines, metric)
            for metric in (
                "vm_pte_requests", "vm_pte_responses",
                "vm_pte_response_misassociations",
                "vm_translation_waiter_registrations",
                "vm_translation_waiter_wakeups",
                "vm_object_attribution_conservation_pass",
            )
        }
        # The disabled and ideal-identity controls intentionally do not create a
        # mode-2 translation controller, so its M4I conservation counters are
        # not emitted.  Treating their absence as a failed PTE invariant would
        # make a valid control look corrupt.  Conversely, an absent counter in
        # either mode-2 profile is a hard validation failure.
        if profile in ("disabled", "ideal"):
            vm_checks = [value == "MISSING" for value in vm_metrics.values()]
        else:
            vm_checks = [
                vm_metrics["vm_pte_requests"] != "MISSING",
                vm_metrics["vm_pte_requests"] == vm_metrics["vm_pte_responses"],
                vm_metrics["vm_pte_response_misassociations"] == "0",
                vm_metrics["vm_translation_waiter_registrations"] ==
                vm_metrics["vm_translation_waiter_wakeups"],
                vm_metrics["vm_object_attribution_conservation_pass"] == "1",
            ]
        checks = [
            status == "0", completed == expected,
            telemetry == expected if args.require_level else telemetry == 0,
            *vm_checks,
        ]
        result = "PASS" if all(checks) else "FAIL"
        if result == "FAIL":
            failures.append(f"{run_dir}: status={status} completed={completed}/{expected} telemetry={telemetry}")
        rows.append([
            run_dir.name, result, data.get("roi", "MISSING"),
            data.get("profile", "MISSING"), data.get("telemetry_level", "MISSING"),
            str(expected), str(completed), str(telemetry),
            data.get("framework_head", "MISSING"), data.get("core_head", "MISSING"),
            *[last_value(lines, metric) for metric in METRICS],
        ])
    if not rows:
        failures.append("no replay manifests found")
    header = ["run", "result", "roi", "profile", "telemetry_level",
              "expected_kernels", "completed_kernels", "telemetry_kernel_records",
              "framework_head", "core_head", *METRICS]
    with args.output.open("w", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    if failures:
        raise SystemExit("FAIL: " + "; ".join(failures))
    print("PASS runs=" + str(len(rows)))


if __name__ == "__main__":
    main()
