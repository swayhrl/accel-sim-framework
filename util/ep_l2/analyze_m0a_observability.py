#!/usr/bin/env python3
"""Fail-closed integrated M0a+M1 static neutrality and 5K analyzer."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

EQUIVALENCE = ("vectorAdd_4M", "cfd_097k", "sad")
BASE_MODE = "BASE_M1_STATIC"
M0A_ON_MODE = "M0A_ON_M1_STATIC"
M0_FIELDS = ("m0_frontend_head_blocked_cycles_tag_way", "m0_frontend_head_blocked_cycles_wad_full",
             "m0_frontend_head_blocked_cycles_wad_hazard", "m0_frontend_head_blocked_cycles_line_mshr",
             "m0_frontend_head_blocked_cycles_descriptor", "m0_frontend_head_blocked_cycles_per_address",
             "m0_frontend_head_blocked_cycles_missq", "m0_frontend_head_blocked_cycles_payload_service",
             "m0_frontend_head_blocked_cycles_payload_capacity", "m0_frontend_head_blocked_cycles_lowerq",
             "m0_frontend_head_blocked_cycles_responseq")


def read_csv(path):
    with path.open(newline="") as source:
        return list(csv.DictReader(source))


def write_csv(path, rows):
    keys = sorted({key for row in rows for key in row})
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=keys)
        writer.writeheader(); writer.writerows(rows)


def percentile(values, fraction):
    values = sorted(values)
    return values[min(len(values) - 1, int((len(values) - 1) * fraction))]


def canonical(rows):
    return sorted((tuple(sorted(row.items())) for row in rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((args.results / "campaign_manifest.json").read_text())
    audit = {"runtime_config_composite_sha256": manifest["runtime_config_sha256"],
             "framework_sha": manifest["framework_sha"], "core_sha": manifest["core_sha"],
             "semantic_base_id": manifest["semantic_base_id"],
             "maturity": manifest["maturity"],
             "promotion_dependencies": ";".join(manifest["promotion_dependencies"]),
             "config_delta": "m0a_off.config ↔ m0a_on.config only"}
    timing = []
    for workload in EQUIVALENCE:
        off, on = args.results / BASE_MODE / workload, args.results / M0A_ON_MODE / workload
        for path in (off / "run_status.json", on / "run_status.json"):
            if not path.is_file(): raise ValueError("missing equivalence status: " + str(path))
        a, b = json.loads((off / "run_status.json").read_text()), json.loads((on / "run_status.json").read_text())
        if a["status"] != "COMPLETE_VALID" or b["status"] != "COMPLETE_VALID":
            raise ValueError("non-valid equivalence cell: " + workload)
        # Compare all parsed B0/L1/DRAM outputs, which include terminal
        # invariants, C7e DRAM issues/bytes and every slice's B0 counters.
        equal = (a["terminal_gpu_tot_sim_cycle"] == b["terminal_gpu_tot_sim_cycle"] and
                 a["terminal_gpu_tot_sim_insn"] == b["terminal_gpu_tot_sim_insn"])
        for artifact in ("target_summary.csv", "target_slice.csv", "target_kernel.csv",
                         "target_bank.csv", "target_window.csv", "target_l1.csv",
                         "target_dram.csv"):
            equal &= canonical(read_csv(off / artifact)) == canonical(read_csv(on / artifact))
        timing.append({"workload": workload, "off_cycles": a["terminal_gpu_tot_sim_cycle"],
                       "on_cycles": b["terminal_gpu_tot_sim_cycle"], "off_instructions": a["terminal_gpu_tot_sim_insn"],
                       "on_instructions": b["terminal_gpu_tot_sim_insn"], "all_required_parsed_fields_equal": int(equal),
                       "config_delta_pass": int(bool(a["audit"].get("config_delta_pass")) and
                                                bool(b["audit"].get("config_delta_pass"))),
                       **audit})
        if not timing[-1]["config_delta_pass"]:
            raise ValueError("OFF/ON config-delta contract failed: " + workload)
        if not equal: raise ValueError("OFF/ON timing-neutrality mismatch: " + workload)
    write_csv(args.out / "TIMING_NEUTRALITY.csv", timing)

    summary_rows, temporal_rows = [], []
    for directory in sorted((args.results / M0A_ON_MODE).iterdir()):
        if not directory.is_dir(): continue
        status = json.loads((directory / "run_status.json").read_text())
        if status["status"] != "COMPLETE_VALID": raise ValueError("invalid ON cell: " + directory.name)
        summary = read_csv(directory / "m0a_summary.csv")[0]
        observed = int(summary["m0_frontend_head_observed_cycles"])
        blocked = int(summary["m0_frontend_head_any_blocked_cycles"])
        row = {"workload": directory.name, "blocked_fraction": blocked / observed if observed else 0,
               "observed_cycles": observed, "any_blocked_cycles": blocked,
               "useful_frontend_admit": summary["m0_useful_frontend_admit"],
               "useful_response_enqueue": summary["m0_useful_response_enqueue"],
               "reason_semantics": "production-visible stage-primary preview reasons; not exhaustive multi-cause; do not sum",
               **audit}
        # Per-slice sums preserve the exact application sampling denominator.
        app = read_csv(directory / "m0a_application.csv")
        resident_samples = sum(int(r["resident_samples"]) for r in app)
        row["resident_payload_occupied_avg"] = sum(int(r["m0_resident_payload_occupied_sum"]) for r in app) / resident_samples
        row["resident_payload_free_avg"] = sum(int(r["m0_resident_payload_free_sum"]) for r in app) / resident_samples
        for field in M0_FIELDS: row[field] = summary[field]
        summary_rows.append(row)
        windows = read_csv(directory / "m0a_window.csv")
        grouped = defaultdict(list)
        for item in windows: grouped[(item["start_cycle"], item["completion_cycle"])].append(item)
        values = []
        for group in grouped.values():
            if len(group) != 64: raise ValueError("incomplete 5K group after parser")
            observed_w = sum(int(r["m0_frontend_head_observed_cycles"]) for r in group)
            blocked_w = sum(int(r["m0_frontend_head_any_blocked_cycles"]) for r in group)
            values.append(blocked_w / observed_w if observed_w else 0)
        temporal_rows.append({"workload": directory.name, "complete_5k_windows": len(values),
                              "blocked_fraction_p50": percentile(values, .50),
                              "blocked_fraction_p95": percentile(values, .95),
                              "blocked_fraction_max": max(values), **audit})
    write_csv(args.out / "WORKLOAD_M0A_SUMMARY.csv", summary_rows)
    write_csv(args.out / "TEMPORAL_M0A_SUMMARY.csv", temporal_rows)
    (args.out / "ANALYSIS_MANIFEST.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    try: main()
    except (OSError, ValueError, KeyError, ZeroDivisionError) as error:
        raise SystemExit("M0a analyzer error: %s" % error)
