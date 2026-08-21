#!/usr/bin/env python3
"""Produce auditable paper-style C2P metrics for the canonical 16 traces.

The primary root contains the 200-cycle Table-1 runs.  An optional second
root contains baseline-only replays with the L2 path set to 50 cycles; their
IPC ratio classifies each trace as S0/S1.  Missing runs remain explicit in the
status report so partial campaigns cannot silently become a paper aggregate.
"""

import argparse
import csv
import hashlib
import re
from pathlib import Path


MODES = ("baseline", "oracle", "ideal", "c2p", "ata", "ccd", "ring")
COUNTERS = (
    "gpu_tot_sim_cycle", "gpu_sim_insn", "l2_total_cache_accesses",
    "l2_global_read_accesses", "c2p_l1_misses", "c2p_oracle_peer_hits",
    "c2p_queries_accepted", "c2p_queries_queue_bypass",
    "c2p_updates_queue_bypass",
    "c2p_candidate_total", "c2p_candidate_queries", "c2p_peer_probes",
    "c2p_peer_probe_hits", "c2p_peer_probe_misses",
    "c2p_peer_l1_accesses", "c2p_remote_hits", "c2p_l2_requests_avoided",
    "c2p_target_probe_port_busy_cycles",
    "c2p_target_probe_queue_wait_cycles",
    "c2p_target_probe_queue_full_cycles",
    "c2p_requester_fill_wait_cycles",
    "c2p_fallback_no_candidate", "c2p_fallback_candidates_exhausted",
    "c2p_fallback_probe_timeout", "c2p_fallback_queue",
    "c2p_snapshot_false_positive",
    "c2p_snapshot_false_negative", "c2p_snapshot_true_positive",
    "c2p_snapshot_true_negative", "c2p_ccd_false_positive",
    "c2p_ccd_false_negative", "c2p_ccd_true_positive",
    "c2p_ccd_true_negative", "c2p_peer_access_hit_samples",
    "c2p_peer_access_miss_samples", "c2p_peer_access_hit_p90",
    "c2p_peer_access_hit_p95", "c2p_peer_access_hit_p99",
    "c2p_peer_access_hit_max",
    "c2p_peer_access_miss_p90", "c2p_peer_access_miss_p95",
    "c2p_peer_access_miss_p99", "c2p_peer_access_miss_max",
)
L2_TOTAL = re.compile(r"^\s*L2_total_cache_accesses = (\d+)$")
L2_GLOBAL_READ = re.compile(
    r"^\s*L2_cache_stats_breakdown\[GLOBAL_ACC_R\]\[TOTAL_ACCESS\] = (\d+)$")
C2P_STAT = re.compile(r"^\s*(c2p_[A-Za-z0-9_]+) = (\d+)$")
HIST = re.compile(r"^c2p_peer_access_(hit|miss)_count_(\d+) = (\d+)$")
PROVENANCE_KEYS = ("gpgpusim_commit", "accelsim_commit", "config_sha256",
                   "trace_sha256", "sim_sha256", "cudart_sha256")

# These options were introduced as explicit spelling of existing defaults
# while the v7 campaign was already running. Keep the raw run-file
# hash for provenance, but compare an effective configuration below: omitted
# and explicitly-default forms are the same experiment point.
EFFECTIVE_CONFIG_DEFAULTS = {
    # Scheme 0 is the parser default used by the original C2P runs.  Later
    # campaign configs spell it out so that ATA/CCD/RING overlays are easier
    # to inspect; both forms denote the same baseline C2P experiment.
    "-c2p_cache_scheme": "0",
    "-c2p_cache_bf_engines": "128",
    "-c2p_cache_bf_latency": "2",
    "-c2p_cache_snapshot_bf_rows_per_bank": "64",
    "-c2p_cache_bf_hashes": "3",
    "-c2p_cache_snapshot_latency": "2",
    "-c2p_cache_remote_tag_latency": "7",
    "-c2p_cache_remote_return_latency": "2",
    "-c2p_cache_query_queue_size": "256",
    "-c2p_cache_update_queue_size": "1024",
    "-c2p_cache_update_transport_bytes_per_cycle": "128",
    "-c2p_cache_snapshot_rebuild_interval": "0",
    "-c2p_cache_probe_timeout": "32",
    "-c2p_cache_target_probe_queue_size": "32",
    "-c2p_cache_diagnostic_target_port_bypass": "0",
    "-c2p_cache_snapshot_copies": "4",
    "-c2p_cache_ata_cluster_issue_width": "4",
    "-c2p_cache_ata_tag_latency": "7",
    "-c2p_cache_ccd_predictor_latency": "1",
    "-c2p_cache_ccd_broadcast_latency": "3",
    "-c2p_cache_ring_hop_latency": "2",
    "-c2p_cache_peer_line_latency": "14",
}

# These are parser defaults, not experiment defaults.  Materializing just the
# mode-selection options lets the audit treat an older run that relied on a
# documented parser default as equivalent to a newer run that spells it out.
MODE_OPTION_DEFAULTS = {
    "-c2p_cache_enable": "0",
    "-c2p_cache_oracle_only": "0",
    "-c2p_cache_ideal_peer": "0",
    "-c2p_cache_collect_oracle": "1",
    "-c2p_cache_scheme": "0",
}

MODE_CONTRACT = {
    "baseline": {
        "-c2p_cache_enable": "0",
        "-c2p_cache_oracle_only": "0",
        "-c2p_cache_ideal_peer": "0",
        "-c2p_cache_scheme": "0",
    },
    "oracle": {
        "-c2p_cache_enable": "0",
        "-c2p_cache_oracle_only": "1",
        "-c2p_cache_ideal_peer": "0",
        "-c2p_cache_collect_oracle": "1",
        "-c2p_cache_scheme": "0",
    },
    "ideal": {
        "-c2p_cache_enable": "1",
        "-c2p_cache_oracle_only": "0",
        "-c2p_cache_ideal_peer": "1",
        "-c2p_cache_collect_oracle": "1",
        "-c2p_cache_scheme": "0",
    },
    "c2p": {
        "-c2p_cache_enable": "1",
        "-c2p_cache_oracle_only": "0",
        "-c2p_cache_ideal_peer": "0",
        "-c2p_cache_collect_oracle": "1",
        "-c2p_cache_scheme": "0",
    },
    "ata": {
        "-c2p_cache_enable": "1",
        "-c2p_cache_oracle_only": "0",
        "-c2p_cache_scheme": "1",
    },
    "ccd": {
        "-c2p_cache_enable": "1",
        "-c2p_cache_oracle_only": "0",
        "-c2p_cache_scheme": "2",
    },
    "ring": {
        "-c2p_cache_enable": "1",
        "-c2p_cache_oracle_only": "0",
        "-c2p_cache_scheme": "3",
    },
}


def read_manifest(path):
    with path.open(newline="") as stream:
        rows = (line for line in stream if not line.startswith("#"))
        return list(csv.DictReader(rows, delimiter="\t"))


def read_paper_groups(path):
    with path.open(newline="") as stream:
        rows = (line for line in stream if not line.startswith("#"))
        return {row["case"]: row for row in csv.DictReader(rows, delimiter="\t")}


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
            # Early paper16 runners intentionally kept summary.txt small and
            # omitted several C2P diagnostics.  The simulator's final stats
            # block is authoritative, so recover every C2P counter from it
            # rather than treating an omitted summary field as a measured 0.
            c2p_stat = C2P_STAT.match(line)
            if c2p_stat:
                values[c2p_stat.group(1)] = int(c2p_stat.group(2))
    return values


def locate_run(roots, case, mode, mode_override_roots=None):
    """Return the canonical-first completed run directory and its summary.

    Long full-trace replays may be safely parallelized only into separate
    result roots.  The canonical root remains authoritative whenever it has a
    completed mode; a supplemental root fills only a missing mode and is
    recorded verbatim in provenance.
    """
    # An override is intentionally exclusive: a corrected mode must not fall
    # back to an older result merely because its fresh replay is incomplete.
    search_roots = (mode_override_roots[mode]
                    if mode_override_roots and mode in mode_override_roots
                    else roots)
    for root in search_roots:
        run_dir = root / case / mode
        data = read_summary(run_dir)
        if data is not None:
            return run_dir, data
    return search_roots[0] / case / mode, None


def read_provenance(run_dir):
    path = run_dir / "provenance.txt"
    if not path.is_file():
        return None
    values = {}
    for line in path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def effective_config_sha256(run_dir):
    """Hash the last-value semantics of a copied GPGPU-Sim configuration.

    The raw ``config_sha256`` remains in provenance and detects an exact file
    change.  This canonical hash removes comments/blank lines, keeps the last
    assignment of every option, and materializes only documented C2P defaults.
    It therefore catches a real overlay or option-order change without falsely
    splitting long-running campaigns that changed from implicit to explicit
    default spelling.
    """
    path = run_dir / "gpgpusim.config"
    if not path.is_file():
        return ""
    values = {}
    for raw_line in path.read_text(errors="replace").splitlines():
        tokens = raw_line.split("#", 1)[0].split()
        if not tokens or not tokens[0].startswith("-"):
            continue
        if len(tokens) < 2:
            return ""
        values[tokens[0]] = " ".join(tokens[1:])
    for option, default in EFFECTIVE_CONFIG_DEFAULTS.items():
        values.setdefault(option, default)
    canonical = "".join(f"{option} {values[option]}\n"
                        for option in sorted(values))
    return hashlib.sha256(canonical.encode()).hexdigest()


def read_effective_options(run_dir):
    """Return last-value config options, including documented parser defaults."""
    path = run_dir / "gpgpusim.config"
    if not path.is_file():
        return None
    options = dict(MODE_OPTION_DEFAULTS)
    for raw in path.read_text().splitlines():
        fields = raw.split()
        if len(fields) >= 2 and fields[0].startswith("-"):
            options[fields[0]] = fields[1]
    return options


def validate_mode_contract(case, mode, run_dir, invariant_failures):
    options = read_effective_options(run_dir)
    if options is None:
        invariant_failures.append(f"{case}/{mode}: missing resolved config")
        return
    for option, expected in MODE_CONTRACT[mode].items():
        actual = options.get(option)
        if actual != expected:
            invariant_failures.append(
                f"{case}/{mode}: {option}={actual}, expected {expected}")
    # The paper point fixes logical comparator scope independently from the
    # 64 one-SM simulation endpoints.  A missing or altered scope would make
    # ATA/CCD and C2P candidate locality incomparable.
    if options.get("-c2p_cache_comparator_cluster_size") != "8":
        invariant_failures.append(
            f"{case}/{mode}: comparator_cluster_size="
            f"{options.get('-c2p_cache_comparator_cluster_size')}, expected 8")


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
    parser.add_argument("--supplemental-results-root", action="append", type=Path,
                        default=[], help="canonical-fallback roots from parallel replays")
    parser.add_argument("--mode-override-root", action="append", default=[],
                        metavar="MODE=DIR",
                        help="use only DIR for one corrected mode; repeatable")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--manifest", type=Path,
                        default=Path(__file__).resolve().parents[1] /
                        "configs/c2p-cache/paper16_workloads.tsv")
    parser.add_argument("--paper-groups", type=Path,
                        default=Path(__file__).resolve().parents[1] /
                        "configs/c2p-cache/paper16_paper_groups.tsv",
                        help="Figure-10 paper grouping reference; never used for local classification")
    parser.add_argument("--l2-fast-root", type=Path,
                        help="baseline-only root with 50-cycle L2 runs")
    parser.add_argument("--supplemental-l2-fast-root", action="append", type=Path,
                        default=[], help="50-cycle fallback roots from parallel replays")
    parser.add_argument("--ccd-metrics-root", type=Path,
                        help="CCD-only replays carrying TP/FN/FP/TN counters")
    parser.add_argument("--supplemental-ccd-metrics-root", action="append", type=Path,
                        default=[], help="CCD-counter fallback roots from parallel replays")
    parser.add_argument("--redundancy-threshold", type=float, default=0.30)
    parser.add_argument("--sensitivity-threshold", type=float, default=1.10)
    parser.add_argument("--strict", action="store_true",
                        help="fail unless every case has all modes and L2-50")
    args = parser.parse_args()

    manifest = read_manifest(args.manifest)
    paper_groups = read_paper_groups(args.paper_groups)
    primary_roots = [args.results_root, *args.supplemental_results_root]
    mode_override_roots = {}
    for item in args.mode_override_root:
        mode, separator, path = item.partition("=")
        if not separator or mode not in MODES or not path:
            parser.error("--mode-override-root must be MODE=DIR for a known mode")
        root = Path(path)
        if not root.is_dir():
            parser.error(f"mode override root does not exist: {root}")
        mode_override_roots.setdefault(mode, []).append(root)
    fast_roots = ([args.l2_fast_root, *args.supplemental_l2_fast_root]
                  if args.l2_fast_root else [])
    ccd_roots = ([args.ccd_metrics_root, *args.supplemental_ccd_metrics_root]
                 if args.ccd_metrics_root else [])
    args.out_dir.mkdir(parents=True, exist_ok=True)
    mode_rows = []
    case_rows = []
    hist_rows = []
    provenance_rows = []
    missing = []
    invariant_failures = []

    def record_provenance(case, mode, source, run_dir, data):
        if data is None:
            return None
        provenance = read_provenance(run_dir)
        if provenance is None:
            missing.append(f"{case}/{mode}: missing {source} provenance")
            return None
        provenance_rows.append({"case": case, "mode": mode, "source": source,
                                "run_dir": str(run_dir),
                                "effective_config_sha256": effective_config_sha256(run_dir),
                                **{key: provenance.get(key, "")
                                   for key in PROVENANCE_KEYS}})
        if any(not provenance.get(key) for key in PROVENANCE_KEYS):
            invariant_failures.append(
                f"{case}/{mode}: incomplete {source} provenance")
        return provenance

    for item in manifest:
        case = item["case"]
        paper_group = paper_groups.get(case)
        if paper_group is None:
            missing.append(f"{case}: missing Figure-10 paper-group reference")
        primary_runs = {
            mode: locate_run(primary_roots, case, mode, mode_override_roots)
            for mode in MODES}
        results = {mode: primary_runs[mode][1] for mode in MODES}
        primary_provenance = {
            mode: record_provenance(case, mode, "primary", primary_runs[mode][0], data)
            for mode, data in results.items()}
        for mode, data in results.items():
            if data is not None:
                validate_mode_contract(case, mode, primary_runs[mode][0],
                                       invariant_failures)
        absent = [mode for mode, data in results.items() if data is None]
        if absent:
            missing.append(f"{case}: missing {', '.join(absent)}")
        baseline = results["baseline"]
        oracle = results["oracle"]
        fast_dir, fast = (locate_run(fast_roots, case, "baseline")
                          if fast_roots else (None, None))
        record_provenance(case, "baseline", "l2_50", fast_dir, fast) \
            if fast_roots else None
        if fast_roots and fast is None:
            missing.append(f"{case}: missing 50-cycle baseline")
        ccd_dir, ccd_metrics = (locate_run(ccd_roots, case, "ccd")
                                if ccd_roots else (primary_runs["ccd"][0], results["ccd"]))
        ccd_provenance = (record_provenance(case, "ccd", "ccd_metrics",
                                            ccd_dir, ccd_metrics)
                          if ccd_roots else primary_provenance["ccd"])
        if ccd_roots and ccd_metrics is not None:
            validate_mode_contract(case, "ccd", ccd_dir, invariant_failures)
        if ccd_roots and ccd_metrics is None:
            missing.append(f"{case}: missing CCD metric replay")
        elif ccd_roots and any(
                value(ccd_metrics, "c2p_ccd_" + suffix) == ""
                for suffix in ("false_positive", "false_negative",
                               "true_positive", "true_negative")):
            missing.append(f"{case}: CCD metric replay lacks classification counters")
        if (ccd_roots and results["ccd"] is not None and ccd_metrics is not None and
                effective_config_sha256(primary_runs["ccd"][0]) !=
                effective_config_sha256(ccd_dir)):
            invariant_failures.append(
                f"{case}: CCD metric config differs from primary CCD config")

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
            # RING is a serialized traversal comparator.  Its finite
            # discovery queue must backpressure the L1 miss head, rather than
            # silently falling through to lower L2 as C2P may do under its
            # explicitly modelled query pressure.  A non-zero bypass value
            # therefore identifies a pre-backpressure or mixed-semantics run
            # that is ineligible for the final comparator figures.
            if mode == "ring" and value(data, "c2p_queries_queue_bypass") not in ("", "0"):
                invariant_failures.append(
                    f"{case}/ring: queue bypass "
                    f"({value(data, 'c2p_queries_queue_bypass')}) is not allowed")

        baseline_l2 = value(baseline, "l2_total_cache_accesses")
        redundancy = ratio(value(oracle, "c2p_oracle_peer_hits"),
                           value(oracle, "c2p_l1_misses"))
        sensitivity = ratio(baseline_cycles,
                            value(fast, "gpu_tot_sim_cycle"))
        # Oracle records opportunity at miss acceptance.  Exact/finite peer
        # paths can subsequently lose it to target-L1 contention, a full
        # candidate scan, or a query-queue bypass.  Keep those stages visible
        # so a small realized L2 reduction is not misdiagnosed as a Bloom
        # filtering error.
        ideal_opportunity_retained = ratio(
            value(results["ideal"], "c2p_remote_hits"),
            value(oracle, "c2p_oracle_peer_hits"))
        c2p_opportunity_retained = ratio(
            value(results["c2p"], "c2p_remote_hits"),
            value(oracle, "c2p_oracle_peer_hits"))
        ideal_probe_timeout_rate = ratio(
            value(results["ideal"], "c2p_fallback_probe_timeout"),
            value(results["ideal"], "c2p_queries_accepted"))
        c2p_probe_timeout_rate = ratio(
            value(results["c2p"], "c2p_fallback_probe_timeout"),
            value(results["c2p"], "c2p_queries_accepted"))
        group = "unknown"
        if redundancy != "" and sensitivity != "":
            group = "R{}S{}".format(
                "1" if redundancy >= args.redundancy_threshold else "0",
                "1" if sensitivity >= args.sensitivity_threshold else "0")
        c2p_tp, c2p_fn, c2p_fp, c2p_tn = classification_rates(
            results["c2p"], "c2p_snapshot_")
        ccd_tp, ccd_fn, ccd_fp, ccd_tn = classification_rates(
            ccd_metrics, "c2p_ccd_")
        case_rows.append({
            **item,
            "group": group,
            "paper_group": "" if paper_group is None else paper_group["paper_group"],
            "paper_label": "" if paper_group is None else paper_group["paper_label"],
            "paper_group_note": "" if paper_group is None else paper_group["note"],
            "oracle_redundancy": redundancy,
            "l2_sensitivity": sensitivity,
            "ideal_opportunity_retained": ideal_opportunity_retained,
            "c2p_opportunity_retained": c2p_opportunity_retained,
            "ideal_probe_timeout_rate": ideal_probe_timeout_rate,
            "c2p_probe_timeout_rate": c2p_probe_timeout_rate,
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
            for outcome, histogram in read_histogram(primary_runs[mode][0]).items():
                for probes, count in histogram.items():
                    hist_rows.append({"case": case, "group": group, "mode": mode,
                                      "outcome": outcome, "peer_probes": probes,
                                      "count": count})

    case_columns = ["case", "suite", "abbr", "input_label",
                    "trace_relative_to_hw_run", "paper_group", "paper_label",
                    "paper_group_note", "group", "oracle_redundancy",
                    "l2_sensitivity", "ideal_opportunity_retained",
                    "c2p_opportunity_retained", "ideal_probe_timeout_rate",
                    "c2p_probe_timeout_rate", "baseline_cycles", "l2_50_cycles",
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
    provenance_columns = ["case", "mode", "source", "run_dir",
                          "effective_config_sha256", *PROVENANCE_KEYS]
    write_csv(args.out_dir / "paper16_provenance.csv", provenance_rows,
              provenance_columns)
    # Every mode is a fixed experiment point.  Its *effective* configuration
    # must be constant across the manifest; raw file hashes remain beside it
    # for byte-for-byte provenance.
    for source in ("primary", "l2_50", "ccd_metrics"):
        for mode in MODES:
            hashes = {row["effective_config_sha256"] for row in provenance_rows
                      if row["source"] == source and row["mode"] == mode}
            if len(hashes) > 1:
                invariant_failures.append(
                    f"{source}/{mode}: inconsistent effective configuration hashes")
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
    if provenance_rows:
        report.extend(["", "## Provenance audit", "",
                       "- `paper16_provenance.csv` records each completed run's "
                       "source commit, raw and effective configuration hashes, trace hash, "
                       "simulator hash, and runtime hash.",
                       "- The analyzer requires one effective configuration hash per "
                       "source/mode and requires every CCD metric replay to use the "
                       "same effective configuration as its primary CCD run.",
                       "- Every completed resolved config is checked against the "
                       "baseline/oracle/ideal/C2P/ATA/CCD/RING mode contract and the "
                       "paper's eight-SM logical comparator scope."])
    (args.out_dir / "paper16_status.md").write_text("\n".join(report) + "\n")
    if args.strict and (missing or invariant_failures):
        raise SystemExit("; ".join(missing + invariant_failures))


if __name__ == "__main__":
    main()
