#!/usr/bin/env python3
"""Produce auditable paper-style C2P metrics for the canonical 16 traces.

The primary root contains the 200-cycle Table-1 runs.  An optional second
root contains baseline-only replays with the L2 path set to 50 cycles; their
IPC ratio classifies each trace as S0/S1.  Missing runs remain explicit in the
status report so partial campaigns cannot silently become a paper aggregate.
"""

import argparse
import csv
import re
from pathlib import Path


MODES = ("baseline", "oracle", "ideal", "c2p", "ata", "ccd", "ring")
COUNTERS = (
    "gpu_tot_sim_cycle", "gpu_sim_insn", "l2_total_cache_accesses",
    "l2_global_read_accesses", "c2p_l1_misses", "c2p_oracle_peer_hits",
    "c2p_candidate_total", "c2p_candidate_queries", "c2p_peer_probes",
    "c2p_peer_l1_accesses", "c2p_remote_hits", "c2p_l2_requests_avoided",
    "c2p_fallback_no_candidate", "c2p_fallback_candidates_exhausted",
    "c2p_fallback_probe_timeout", "c2p_snapshot_false_positive",
    "c2p_snapshot_false_negative", "c2p_snapshot_true_positive",
    "c2p_snapshot_true_negative", "c2p_ccd_false_positive",
    "c2p_ccd_false_negative", "c2p_ccd_true_positive",
    "c2p_ccd_true_negative", "c2p_peer_access_hit_samples",
    "c2p_peer_access_miss_samples", "c2p_peer_access_hit_p90",
    "c2p_peer_access_hit_p95", "c2p_peer_access_hit_p99",
    "c2p_peer_access_miss_p90", "c2p_peer_access_miss_p95",
    "c2p_peer_access_miss_p99",
)
L2_TOTAL = re.compile(r"^\s*L2_total_cache_accesses = (\d+)$")
L2_GLOBAL_READ = re.compile(
    r"^\s*L2_cache_stats_breakdown\[GLOBAL_ACC_R\]\[TOTAL_ACCESS\] = (\d+)$")
HIST = re.compile(r"^c2p_peer_access_(hit|miss)_count_(\d+) = (\d+)$")


def read_manifest(path):
    with path.open(newline="") as stream:
        rows = (line for line in stream if not line.startswith("#"))
        return list(csv.DictReader(rows, delimiter="\t"))


def read_summary(run_dir):
    summary = run_dir / "summary.txt"
    if not summary.is_file():
        return None
    values = {}
    for line in summary.read_text().splitlines():
        if " = " not in line:
            continue
        key, value = line.split(" = ", 1)
        try:
            values[key] = int(value)
        except ValueError:
            continue
    # L2 totals are added to new summaries but old self-contained bundles can
    # still be analyzed by taking these values directly from run.out.
    run_out = run_dir / "run.out"
    if run_out.is_file():
        for line in run_out.read_text(errors="replace").splitlines():
            total = L2_TOTAL.match(line)
            global_read = L2_GLOBAL_READ.match(line)
            if total:
                # Accel-Sim may print an intermediate report before its final
                # aggregate.  Match the runner's AWK behavior and retain the
                # final occurrence.
                values["l2_total_cache_accesses"] = int(total.group(1))
            if global_read:
                values["l2_global_read_accesses"] = int(global_read.group(1))
    return values


def read_histogram(run_dir):
    result = {"hit": {}, "miss": {}}
    run_out = run_dir / "run.out"
    if not run_out.is_file():
        return result
    for line in run_out.read_text(errors="replace").splitlines():
        match = HIST.match(line)
        if match:
            result[match.group(1)][int(match.group(2))] = int(match.group(3))
    return result


def value(data, key):
    return "" if data is None or key not in data else data[key]


def ratio(numerator, denominator):
    if numerator == "" or denominator == "" or not denominator:
        return ""
    return numerator / denominator


def classification_rates(data, prefix):
    fp = value(data, prefix + "false_positive")
    fn = value(data, prefix + "false_negative")
    tp = value(data, prefix + "true_positive")
    tn = value(data, prefix + "true_negative")
    total = sum(v for v in (fp, fn, tp, tn) if v != "")
    return (ratio(tp, total), ratio(fn, total), ratio(fp, total), ratio(tn, total))


def write_csv(path, rows, columns):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--manifest", type=Path,
                        default=Path(__file__).resolve().parents[1] /
                        "configs/c2p-cache/paper16_workloads.tsv")
    parser.add_argument("--l2-fast-root", type=Path,
                        help="baseline-only root with 50-cycle L2 runs")
    parser.add_argument("--redundancy-threshold", type=float, default=0.30)
    parser.add_argument("--sensitivity-threshold", type=float, default=1.10)
    parser.add_argument("--strict", action="store_true",
                        help="fail unless every case has all modes and L2-50")
    args = parser.parse_args()

    manifest = read_manifest(args.manifest)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    mode_rows = []
    case_rows = []
    hist_rows = []
    missing = []
    invariant_failures = []
    for item in manifest:
        case = item["case"]
        run_root = args.results_root / case
        results = {mode: read_summary(run_root / mode) for mode in MODES}
        absent = [mode for mode, data in results.items() if data is None]
        if absent:
            missing.append(f"{case}: missing {', '.join(absent)}")
        baseline = results["baseline"]
        oracle = results["oracle"]
        fast = (read_summary(args.l2_fast_root / case / "baseline")
                if args.l2_fast_root else None)
        if args.l2_fast_root and fast is None:
            missing.append(f"{case}: missing 50-cycle baseline")

        # These are mechanism invariants, not performance expectations.  The
        # oracle path must remain observational, and an admitted peer return
        # must replace exactly one lower-L2 request in every sharing scheme.
        baseline_cycles = value(baseline, "gpu_tot_sim_cycle")
        oracle_cycles = value(oracle, "gpu_tot_sim_cycle")
        if baseline_cycles != "" and oracle_cycles != "" and \
                baseline_cycles != oracle_cycles:
            invariant_failures.append(
                f"{case}: oracle changed baseline cycles "
                f"({baseline_cycles} -> {oracle_cycles})")
        for mode, data in results.items():
            remote_hits = value(data, "c2p_remote_hits")
            l2_avoided = value(data, "c2p_l2_requests_avoided")
            if remote_hits != "" and l2_avoided != "" and remote_hits != l2_avoided:
                invariant_failures.append(
                    f"{case}/{mode}: remote hits ({remote_hits}) != "
                    f"L2 requests avoided ({l2_avoided})")

        baseline_l2 = value(baseline, "l2_total_cache_accesses")
        redundancy = ratio(value(oracle, "c2p_oracle_peer_hits"),
                           value(oracle, "c2p_l1_misses"))
        sensitivity = ratio(baseline_cycles,
                            value(fast, "gpu_tot_sim_cycle"))
        group = "unknown"
        if redundancy != "" and sensitivity != "":
            group = "R{}S{}".format(
                "1" if redundancy >= args.redundancy_threshold else "0",
                "1" if sensitivity >= args.sensitivity_threshold else "0")
        c2p_tp, c2p_fn, c2p_fp, c2p_tn = classification_rates(
            results["c2p"], "c2p_snapshot_")
        ccd_tp, ccd_fn, ccd_fp, ccd_tn = classification_rates(
            results["ccd"], "c2p_ccd_")
        case_rows.append({
            **item,
            "group": group,
            "oracle_redundancy": redundancy,
            "l2_sensitivity": sensitivity,
            "baseline_cycles": baseline_cycles,
            "l2_50_cycles": value(fast, "gpu_tot_sim_cycle"),
            "snapshot_tp_rate": c2p_tp,
            "snapshot_fn_rate": c2p_fn,
            "snapshot_fp_rate": c2p_fp,
            "snapshot_tn_rate": c2p_tn,
            "ccd_tp_rate": ccd_tp,
            "ccd_fn_rate": ccd_fn,
            "ccd_fp_rate": ccd_fp,
            "ccd_tn_rate": ccd_tn,
        })
        for mode, data in results.items():
            if data is None:
                continue
            row = {"case": case, "suite": item["suite"], "abbr": item["abbr"],
                   "input_label": item["input_label"], "group": group, "mode": mode}
            row.update({key: value(data, key) for key in COUNTERS})
            row["ipc_normalized"] = ratio(baseline_cycles,
                                           value(data, "gpu_tot_sim_cycle"))
            row["l2_access_normalized"] = ratio(
                value(data, "l2_total_cache_accesses"), baseline_l2)
            row["l2_global_read_normalized"] = ratio(
                value(data, "l2_global_read_accesses"),
                value(baseline, "l2_global_read_accesses"))
            row["remote_hit_rate"] = ratio(value(data, "c2p_remote_hits"),
                                            value(data, "c2p_l1_misses"))
            row["candidates_per_query"] = ratio(
                value(data, "c2p_candidate_total"),
                value(data, "c2p_candidate_queries"))
            mode_rows.append(row)
            for outcome, histogram in read_histogram(run_root / mode).items():
                for probes, count in histogram.items():
                    hist_rows.append({"case": case, "group": group, "mode": mode,
                                      "outcome": outcome, "peer_probes": probes,
                                      "count": count})

    case_columns = ["case", "suite", "abbr", "input_label",
                    "trace_relative_to_hw_run", "group", "oracle_redundancy",
                    "l2_sensitivity", "baseline_cycles", "l2_50_cycles",
                    "snapshot_tp_rate", "snapshot_fn_rate", "snapshot_fp_rate",
                    "snapshot_tn_rate", "ccd_tp_rate", "ccd_fn_rate",
                    "ccd_fp_rate", "ccd_tn_rate"]
    mode_columns = ["case", "suite", "abbr", "input_label", "group", "mode",
                    *COUNTERS, "ipc_normalized", "l2_access_normalized",
                    "l2_global_read_normalized", "remote_hit_rate",
                    "candidates_per_query"]
    write_csv(args.out_dir / "paper16_cases.csv", case_rows, case_columns)
    write_csv(args.out_dir / "paper16_modes.csv", mode_rows, mode_columns)
    write_csv(args.out_dir / "paper16_probe_histogram.csv", hist_rows,
              ["case", "group", "mode", "outcome", "peer_probes", "count"])
    report = ["# C2P paper16 analysis status", "",
              "## Classification thresholds", "",
              f"- R1: oracle redundancy >= {args.redundancy_threshold:.2f}",
              f"- S1: IPC(50-cycle L2) / IPC(200-cycle L2) >= {args.sensitivity_threshold:.2f}",
              ""]
    if missing:
        report.extend(["## Missing evidence", ""])
        report.extend(f"- {entry}" for entry in missing)
    else:
        report.extend(["All canonical cases contain seven comparison modes and a 50-cycle baseline."])
    if invariant_failures:
        report.extend(["", "## Mechanism invariant failures", ""])
        report.extend(f"- {entry}" for entry in invariant_failures)
    elif not missing:
        report.extend(["", "All oracle and remote-hit/L2-avoidance invariants passed."])
    (args.out_dir / "paper16_status.md").write_text("\n".join(report) + "\n")
    if args.strict and (missing or invariant_failures):
        raise SystemExit("; ".join(missing + invariant_failures))


if __name__ == "__main__":
    main()
