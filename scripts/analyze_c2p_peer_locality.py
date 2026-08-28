#!/usr/bin/env python3
"""Audit observation-only C2P peer-locality diagnostics.

The simulator emits the complete histogram family into each oracle run.out.
This script keeps raw counters authoritative, writes compact CSVs, and refuses
to describe a run as qualified if its detect/issue or histogram conservation
relations do not hold.
"""

import argparse
import csv
import re
from pathlib import Path


MAX_SMS = 64
CLUSTERS = 8
RING_DISTANCE_MAX = 32
SIGNED_DELTA_MIN = -63
SIGNED_DELTA_MAX = 63
SNAPSHOTS = (
    ("detect", "sector"),
    ("issue", "sector"),
    ("detect", "line"),
    ("issue", "line"),
)
STAT = re.compile(r"^\s*(c2p_[A-Za-z0-9_-]+) = (\d+)\s*$")


def read_manifest(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader((line for line in stream
                                    if not line.startswith("#")),
                                   delimiter="\t"))


def parse_run(run_dir):
    run_out = run_dir / "run.out"
    if not run_out.is_file():
        return None, ["missing run.out"]
    values = {}
    exited = False
    for line in run_out.read_text(errors="replace").splitlines():
        if "GPGPU-Sim: *** exit detected ***" in line:
            exited = True
        match = STAT.match(line)
        if match:
            values[match.group(1)] = int(match.group(2))
    errors = []
    if not exited:
        errors.append("missing normal simulator exit")
    if values.get("c2p_peer_locality_diagnostic") != 1:
        errors.append("peer-locality diagnostic flag is not one")
    return values, errors


def value(values, key, errors):
    if key not in values:
        errors.append("missing " + key)
        return 0
    return values[key]


def prefix(phase, semantic):
    return "c2p_peer_locality_%s_%s" % (phase, semantic)


def audit_snapshot(values, phase, semantic, errors):
    name = prefix(phase, semantic)
    events = value(values, name + "_events", errors)
    redundant = value(values, name + "_redundant_events", errors)
    peer_count = [value(values, name + "_peer_count_%d" % count, errors)
                  for count in range(MAX_SMS)]
    local_only = value(values, name + "_local_only", errors)
    outer_only = value(values, name + "_outer_only", errors)
    both = value(values, name + "_both_local_and_outer", errors)
    local_total = value(values, name + "_local_peer_total", errors)
    outer_total = value(values, name + "_outer_peer_total", errors)
    nearest_abs = [0] + [value(values, name + "_nearest_abs_distance_%d" % d,
                               errors) for d in range(1, MAX_SMS)]
    all_abs = [0] + [value(values, name + "_all_abs_distance_%d" % d, errors)
                   for d in range(1, MAX_SMS)]
    nearest_ring = [0] + [value(values, name + "_nearest_ring_distance_%d" % d,
                                errors) for d in range(1, RING_DISTANCE_MAX + 1)]
    all_ring = [0] + [value(values, name + "_all_ring_distance_%d" % d, errors)
                    for d in range(1, RING_DISTANCE_MAX + 1)]
    signed = {d: value(values, name + "_signed_delta_%d" % d, errors)
              for d in range(SIGNED_DELTA_MIN, SIGNED_DELTA_MAX + 1) if d}
    clusters = [value(values, name + "_peer_clusters_%d" % count, errors)
                for count in range(CLUSTERS + 1)]

    if events != peer_count[0] + redundant:
        errors.append("%s: events != zero-peer + redundant" % name)
    if redundant != sum(peer_count[1:]):
        errors.append("%s: redundant != peer-count histogram" % name)
    if redundant != local_only + outer_only + both:
        errors.append("%s: redundant != locality partition" % name)
    if redundant != sum(nearest_abs):
        errors.append("%s: redundant != nearest-absolute histogram" % name)
    if redundant != sum(nearest_ring):
        errors.append("%s: redundant != nearest-ring histogram" % name)
    copies = sum(count * peer_count[count] for count in range(MAX_SMS))
    if copies != sum(all_abs):
        errors.append("%s: copies != all-absolute histogram" % name)
    if copies != sum(all_ring):
        errors.append("%s: copies != all-ring histogram" % name)
    if copies != sum(signed.values()):
        errors.append("%s: copies != signed-delta histogram" % name)
    if copies != local_total + outer_total:
        errors.append("%s: copies != local + outer copies" % name)
    if redundant != sum(clusters[1:]):
        errors.append("%s: redundant != peer-cluster histogram" % name)
    if clusters[0]:
        errors.append("%s: peer-cluster zero bin must be zero" % name)

    return {
        "events": events,
        "redundant": redundant,
        "peer_count": peer_count,
        "local_only": local_only,
        "outer_only": outer_only,
        "both": both,
        "local_total": local_total,
        "outer_total": outer_total,
        "clusters": clusters,
        "nearest_abs": nearest_abs,
        "all_abs": all_abs,
        "nearest_ring": nearest_ring,
        "all_ring": all_ring,
        "signed": signed,
    }


def read_provenance(run_dir):
    path = run_dir / "provenance.txt"
    if not path.is_file():
        return {}
    values = {}
    for line in path.read_text(errors="replace").splitlines():
        if "=" in line:
            key, val = line.split("=", 1)
            values[key] = val
    return values


def write_csv(path, header, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--case", action="append", default=[],
                        help="audit only this manifest case; may repeat or use commas")
    parser.add_argument("--root", action="append", required=True,
                        metavar="LABEL=PATH",
                        help="oracle diagnostic results root; may repeat")
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    roots = []
    for item in args.root:
        if "=" not in item:
            parser.error("--root must use LABEL=PATH")
        label, raw_path = item.split("=", 1)
        roots.append((label, Path(raw_path)))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    selected_cases = set()
    for item in args.case:
        selected_cases.update(case for case in item.split(",") if case)
    manifest = read_manifest(args.manifest)
    if selected_cases:
        known_cases = {entry["case"] for entry in manifest}
        unknown_cases = selected_cases - known_cases
        if unknown_cases:
            parser.error("unknown --case: " + ", ".join(sorted(unknown_cases)))
        manifest = [entry for entry in manifest
                    if entry["case"] in selected_cases]
    audit_rows = []
    event_rows = []
    diagnostic_rows = []
    count_rows = []
    locality_rows = []
    distance_rows = []
    markdown = ["# C2P peer-locality diagnostic audit", ""]
    qualified = 0
    failed = 0
    missing = 0

    for label, root in roots:
        for entry in manifest:
            case = entry["case"]
            run_dir = root / case / "oracle"
            values, errors = parse_run(run_dir)
            provenance = read_provenance(run_dir)
            if values is None:
                missing += 1
                audit_rows.append({
                    "label": label, "case": case, "status": "MISSING",
                    "errors": "; ".join(errors), "run_dir": str(run_dir),
                    "gpgpusim_commit": "", "accelsim_commit": "",
                    "config_sha256": "", "trace_sha256": "",
                    "sim_sha256": "",
                })
                continue

            registered = value(values, "c2p_peer_locality_registered_l1s", errors)
            pending = value(values, "c2p_peer_locality_pending_detect_records", errors)
            detects = value(values, "c2p_peer_locality_detect_records", errors)
            accepted = value(values, "c2p_peer_locality_l1_accepted_records",
                             errors)
            detect_merge = value(values,
                                 "c2p_peer_locality_l1_mshr_merge_records",
                                 errors)
            issues = value(values, "c2p_peer_locality_issue_records", errors)
            missing_detect = value(values, "c2p_peer_locality_missing_detect_records",
                                   errors)
            if registered != MAX_SMS:
                errors.append("registered L1 count is not 64")
            if pending:
                errors.append("pending detect records at exit")
            if missing_detect:
                errors.append("issue records missing detect record")
            if accepted != detects + detect_merge:
                errors.append("accepted L1 misses do not split into lower + MSHR merge")
            if detects != issues:
                errors.append("lower-queue detect and issue record counts differ")

            snapshots = {}
            for phase, semantic in SNAPSHOTS:
                snapshots[(phase, semantic)] = audit_snapshot(
                    values, phase, semantic, errors)
            if (snapshots[("issue", "sector")]["redundant"] !=
                    values.get("c2p_oracle_peer_hits", 0)):
                errors.append("issue-sector redundancy differs from oracle peer hits")

            sector_transition = 0
            line_transition = 0
            for detect_peer in (0, 1):
                for issue_peer in (0, 1):
                    sector_transition += value(
                        values, "c2p_peer_locality_sector_detect_%d_issue_%d" %
                        (detect_peer, issue_peer), errors)
                    line_transition += value(
                        values, "c2p_peer_locality_line_detect_%d_issue_%d" %
                        (detect_peer, issue_peer), errors)
            if sector_transition != issues:
                errors.append("sector transition matrix does not sum to issues")
            if line_transition != issues:
                errors.append("line transition matrix does not sum to issues")

            issue_sector = snapshots[("issue", "sector")]
            issue_line = snapshots[("issue", "line")]
            detect_sector = snapshots[("detect", "sector")]
            detect_line = snapshots[("detect", "line")]
            diagnostic_rows.append({
                "label": label, "case": case,
                "accepted_l1_events": accepted,
                "detect_events": detects,
                "detect_lower_events": detects,
                "detect_mshr_merge_events": detect_merge,
                "issue_events": issues,
                "detect_sector_redundant": detect_sector["redundant"],
                "issue_sector_redundant": issue_sector["redundant"],
                "detect_line_redundant": detect_line["redundant"],
                "issue_line_redundant": issue_line["redundant"],
                "issue_sector_redundant_ratio":
                    issue_sector["redundant"] / issues if issues else 0.0,
                "detect_0_issue_0": value(
                    values, "c2p_peer_locality_sector_detect_0_issue_0", errors),
                "detect_0_issue_1": value(
                    values, "c2p_peer_locality_sector_detect_0_issue_1", errors),
                "detect_1_issue_0": value(
                    values, "c2p_peer_locality_sector_detect_1_issue_0", errors),
                "detect_1_issue_1": value(
                    values, "c2p_peer_locality_sector_detect_1_issue_1", errors),
                "wait_cycles_total": value(
                    values, "c2p_peer_locality_wait_cycles_total", errors),
                "wait_cycles_max": value(
                    values, "c2p_peer_locality_wait_cycles_max", errors),
                "wait_cycles_mean": value(
                    values, "c2p_peer_locality_wait_cycles_total", errors) / issues
                    if issues else 0.0,
            })

            status = "PASS" if not errors else "FAIL"
            qualified += status == "PASS"
            failed += status == "FAIL"
            audit_rows.append({
                "label": label, "case": case, "status": status,
                "errors": "; ".join(errors), "run_dir": str(run_dir),
                "gpgpusim_commit": provenance.get("gpgpusim_commit", ""),
                "accelsim_commit": provenance.get("accelsim_commit", ""),
                "config_sha256": provenance.get("config_sha256", ""),
                "trace_sha256": provenance.get("trace_sha256", ""),
                "sim_sha256": provenance.get("sim_sha256", ""),
            })

            for phase, semantic in SNAPSHOTS:
                stats = snapshots[(phase, semantic)]
                events = stats["events"]
                redundant = stats["redundant"]
                event_rows.append({
                    "label": label, "case": case, "phase": phase,
                    "semantic": semantic, "events": events,
                    "redundant_events": redundant,
                    "redundant_ratio": redundant / events if events else 0.0,
                })
                locality_rows.append({
                    "label": label, "case": case, "phase": phase,
                    "semantic": semantic, "events": events,
                    "redundant_events": redundant,
                    "local_only": stats["local_only"],
                    "outer_only": stats["outer_only"],
                    "both": stats["both"],
                    "local_only_given_redundant":
                        stats["local_only"] / redundant if redundant else 0.0,
                    "outer_only_given_redundant":
                        stats["outer_only"] / redundant if redundant else 0.0,
                    "both_given_redundant":
                        stats["both"] / redundant if redundant else 0.0,
                    "local_peer_total": stats["local_total"],
                    "outer_peer_total": stats["outer_total"],
                })
                for count, occurrences in enumerate(stats["peer_count"]):
                    count_rows.append({
                        "label": label, "case": case, "phase": phase,
                        "semantic": semantic, "peer_count": count,
                        "occurrences": occurrences,
                    })
                for distance in range(1, MAX_SMS):
                    distance_rows.append({
                        "label": label, "case": case, "phase": phase,
                        "semantic": semantic, "metric": "nearest_abs",
                        "distance": distance,
                        "occurrences": stats["nearest_abs"][distance],
                    })
                    distance_rows.append({
                        "label": label, "case": case, "phase": phase,
                        "semantic": semantic, "metric": "all_abs",
                        "distance": distance,
                        "occurrences": stats["all_abs"][distance],
                    })
                for distance in range(1, RING_DISTANCE_MAX + 1):
                    distance_rows.append({
                        "label": label, "case": case, "phase": phase,
                        "semantic": semantic, "metric": "nearest_ring",
                        "distance": distance,
                        "occurrences": stats["nearest_ring"][distance],
                    })
                    distance_rows.append({
                        "label": label, "case": case, "phase": phase,
                        "semantic": semantic, "metric": "all_ring",
                        "distance": distance,
                        "occurrences": stats["all_ring"][distance],
                    })
                for distance, occurrences in stats["signed"].items():
                    distance_rows.append({
                        "label": label, "case": case, "phase": phase,
                        "semantic": semantic, "metric": "signed_delta",
                        "distance": distance,
                        "occurrences": occurrences,
                    })

    write_csv(args.out_dir / "run_audit.csv",
              ["label", "case", "status", "errors", "run_dir",
               "gpgpusim_commit", "accelsim_commit", "config_sha256",
               "trace_sha256", "sim_sha256"], audit_rows)
    write_csv(args.out_dir / "event_semantics.csv",
              ["label", "case", "phase", "semantic", "events",
               "redundant_events", "redundant_ratio"], event_rows)
    write_csv(args.out_dir / "diagnostic_summary.csv",
              ["label", "case", "accepted_l1_events", "detect_events", "detect_lower_events",
               "detect_mshr_merge_events", "issue_events",
               "detect_sector_redundant", "issue_sector_redundant",
               "detect_line_redundant", "issue_line_redundant",
               "issue_sector_redundant_ratio", "detect_0_issue_0",
               "detect_0_issue_1", "detect_1_issue_0", "detect_1_issue_1",
               "wait_cycles_total", "wait_cycles_max", "wait_cycles_mean"],
              diagnostic_rows)
    write_csv(args.out_dir / "peer_count_hist.csv",
              ["label", "case", "phase", "semantic", "peer_count",
               "occurrences"], count_rows)
    write_csv(args.out_dir / "cluster_locality.csv",
              ["label", "case", "phase", "semantic", "events",
               "redundant_events", "local_only", "outer_only", "both",
               "local_only_given_redundant", "outer_only_given_redundant",
               "both_given_redundant", "local_peer_total",
               "outer_peer_total"], locality_rows)
    write_csv(args.out_dir / "peer_distance_hist.csv",
              ["label", "case", "phase", "semantic", "metric",
               "distance", "occurrences"], distance_rows)

    markdown.extend([
        "## Qualification",
        "",
        "- qualified: %d" % qualified,
        "- failed: %d" % failed,
        "- missing: %d" % missing,
        "",
        "A `PASS` requires normal exit, 64 registered L1s, one-to-one "
        "new-MSHR detect/issue correspondence, no pending observation, and every "
        "histogram conservation equation in the diagnostic contract.",
        "",
        "## Runs",
        "",
        "| Label | Case | Status | Error |",
        "|---|---|---|---|",
    ])
    for row in audit_rows:
        markdown.append("| {label} | {case} | {status} | {errors} |".format(**row))
    (args.out_dir / "invariant_report.md").write_text("\n".join(markdown) + "\n")

    if failed:
        raise SystemExit("peer-locality invariant failures; see invariant_report.md")


if __name__ == "__main__":
    main()
