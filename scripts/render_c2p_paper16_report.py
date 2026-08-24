#!/usr/bin/env python3
"""Render an auditable C2P-Cache paper16 comparison report from CSV evidence."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path


GROUPS = ("R0S0", "R1S0", "R0S1", "R1S1")
MODES = ("baseline", "ata", "ccd", "ring", "c2p")
MODE_LABEL = {"baseline": "Baseline", "ata": "ATA", "ccd": "CCD",
              "ring": "RING", "c2p": "C2P-Cache"}
PAPER_TARGETS = {
    "R1S1": "C2P IPC +23.5% average (up to +49.7%)",
    "R0S1": "C2P about -2.0%; ATA -31.7%; RING -19.3%; CCD +0.4%",
    "R1S0/R1S1": "C2P normalized L2 access 53.4% / 69.8%",
}


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def number(row, field):
    try:
        return float(row[field])
    except (KeyError, TypeError, ValueError):
        return None


def mean(values):
    return None if not values else sum(values) / len(values)


def aggregate(rows, field):
    result = {}
    for group in GROUPS:
        for mode in MODES:
            values = [number(row, field) for row in rows
                      if row["group"] == group and row["mode"] == mode]
            values = [value for value in values if value is not None]
            result[group, mode] = (len(values), mean(values))
    return result


def aggregate_cases(rows, complete_cases, field):
    result = {}
    for group in GROUPS:
        values = [number(row, field) for row in rows
                  if row["case"] in complete_cases and row["group"] == group]
        values = [value for value in values if value is not None]
        result[group] = (len(values), mean(values))
    return result


def format_value(value):
    return "—" if value is None else f"{value:.3f}"


def safe_ratio(numerator, denominator):
    return None if numerator is None or denominator in (None, 0) else numerator / denominator


def trend(result, condition, statement):
    value = result[1]
    if value is None:
        return f"- insufficient local points: {statement}"
    return f"- {'consistent' if condition(value) else 'different'}: {statement} (observed {value:.3f})"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--figures-dir", type=Path)
    parser.add_argument("--queue-sensitivity-csv", type=Path,
                        help="optional finite-queue diagnostic from analyze_c2p_queue_sensitivity.py")
    args = parser.parse_args()
    rows = read_csv(args.analysis_dir / "paper16_modes.csv")
    cases = read_csv(args.analysis_dir / "paper16_cases.csv")
    modes_by_case = defaultdict(set)
    for row in rows:
        modes_by_case[row["case"]].add(row["mode"])
    complete_cases = {case for case, modes in modes_by_case.items()
                      if set(MODES) <= modes}
    complete_rows = [row for row in rows if row["case"] in complete_cases]
    ipc = aggregate(complete_rows, "ipc_normalized")
    l2 = aggregate(complete_rows, "l2_access_normalized")
    ideal_recovery = aggregate_cases(cases, complete_cases,
                                     "ideal_opportunity_retained")
    c2p_recovery = aggregate_cases(cases, complete_cases,
                                   "c2p_opportunity_retained")
    ideal_timeout = aggregate_cases(cases, complete_cases,
                                    "ideal_probe_timeout_rate")
    c2p_timeout = aggregate_cases(cases, complete_cases,
                                  "c2p_probe_timeout_rate")
    equivalence_path = args.analysis_dir / "default_c2p_equivalence.csv"
    equivalence_rows = read_csv(equivalence_path) if equivalence_path.is_file() else []
    equivalent_cases = [row["case"] for row in equivalence_rows
                        if row.get("equal") == "yes"]
    c2p_outliers = []
    for row in complete_rows:
        if row["mode"] != "c2p":
            continue
        ipc_value = number(row, "ipc_normalized")
        l2_value = number(row, "l2_access_normalized")
        # A lower L2-access count alone is not a performance proof.  Make the
        # most important counter-direction explicit: a slowdown despite a
        # material L2 reduction must remain an investigation item, along with
        # the queue/probe quantities that could explain it.
        if ipc_value is not None and l2_value is not None and \
                ipc_value < 0.995 and l2_value < 0.99:
            accepted = number(row, "c2p_queries_accepted")
            c2p_outliers.append({
                "case": row["case"], "group": row["group"],
                "ipc": ipc_value, "l2": l2_value,
                "candidates": safe_ratio(number(row, "c2p_candidate_total"),
                                         number(row, "c2p_candidate_queries")),
                "queue_bypass": safe_ratio(number(row, "c2p_queries_queue_bypass"),
                                            accepted),
                "probe_timeout": safe_ratio(number(row, "c2p_fallback_probe_timeout"),
                                            accepted),
                "fp": safe_ratio(number(row, "c2p_snapshot_false_positive"),
                                 sum(value for value in (
                                     number(row, "c2p_snapshot_false_positive"),
                                     number(row, "c2p_snapshot_false_negative"),
                                     number(row, "c2p_snapshot_true_positive"),
                                     number(row, "c2p_snapshot_true_negative"))
                                     if value is not None)),
            })

    lines = ["# C2P-Cache paper16 directional reproduction", "",
             "## Scope and acceptance", "",
             "This report evaluates the canonical local 16 complete replay traces; "
             "it is not a claim of cycle-identical reproduction of unpublished "
             "author traces or address hashes.  All numbers below are derived "
             "from `paper16_cases.csv` and `paper16_modes.csv`.", "",
             "## Local workload classification", "",
             "| Group | Cases |", "|---|---|"]
    for group in GROUPS:
        names = [row["abbr"] for row in cases if row["group"] == group]
        lines.append(f"| {group} | {', '.join(names) if names else '—'} |")

    lines.extend(["", "## Paper group reference versus local reclassification", "",
                  "The Figure-10 group is retained as a paper reference only. "
                  "The local group always comes from this campaign's independent "
                  "oracle-redundancy and 50-cycle-L2 measurements; a mismatch is "
                  "trace/input evidence, not a relabeling of the paper.", "",
                  "| Case | Paper label | Paper group | Local group | Local redundancy | Local L2 sensitivity |",
                  "|---|---|---|---|---:|---:|"])
    for row in cases:
        lines.append("| {} | {} | {} | {} | {} | {} |".format(
            row["case"], row.get("paper_label", "—") or "—",
            row.get("paper_group", "—") or "—", row["group"],
            format_value(number(row, "oracle_redundancy")),
            format_value(number(row, "l2_sensitivity"))))

    lines.extend(["", "## Figure-10-style normalized IPC aggregate", "",
                  "Arithmetic mean across locally complete seven-mode cases in each group; "
                  "not a replacement for the paper's original workload-weighted set.", "",
                  "| Group | Baseline | ATA | CCD | RING | C2P-Cache |", "|---|---:|---:|---:|---:|---:|"])
    for group in GROUPS:
        lines.append("| {} | {} | {} | {} | {} | {} |".format(
            group, *(format_value(ipc[group, mode][1]) for mode in MODES)))

    lines.extend(["", "## Figure-11-style normalized L2 access aggregate", "",
                  "| Group | Baseline | ATA | CCD | RING | C2P-Cache |", "|---|---:|---:|---:|---:|---:|"])
    for group in GROUPS:
        lines.append("| {} | {} | {} | {} | {} | {} |".format(
            group, *(format_value(l2[group, mode][1]) for mode in MODES)))

    lines.extend(["", "## Remote-opportunity retention diagnostic", "",
                  "The oracle measures a peer opportunity when a miss is accepted. "
                  "The two retention columns show how much survives later exact "
                  "probing; timeout is the fraction of accepted peer requests that "
                  "fall back because a target-L1 probe remained blocked. This is a "
                  "diagnostic for model/queue contention, not a paper performance "
                  "metric.", "",
                  "| Group | Exact ideal retains oracle opportunity | C2P retains oracle opportunity | Ideal target-timeout rate | C2P target-timeout rate |",
                  "|---|---:|---:|---:|---:|"])
    for group in GROUPS:
        lines.append("| {} | {} | {} | {} | {} |".format(
            group, format_value(ideal_recovery[group][1]),
            format_value(c2p_recovery[group][1]),
            format_value(ideal_timeout[group][1]),
            format_value(c2p_timeout[group][1])))

    lines.extend(["", "## Paper target versus local directional evidence", ""])
    for group, target in PAPER_TARGETS.items():
        lines.append(f"- paper target ({group}): {target}.")
    lines.extend(["",
                  trend(ipc["R1S1", "c2p"], lambda value: value > 1.0,
                        "R1S1 C2P has positive IPC direction"),
                  trend(ipc["R0S1", "c2p"], lambda value: 0.95 <= value <= 1.05,
                        "R0S1 C2P remains near neutral"),
                  trend(ipc["R0S1", "ata"], lambda value: value < 1.0,
                        "R0S1 ATA exposes sharing overhead"),
                  trend(ipc["R0S1", "ring"], lambda value: value < 1.0,
                        "R0S1 RING exposes sharing overhead"),
                  trend(l2["R1S1", "c2p"], lambda value: value < 1.0,
                        "R1S1 C2P reduces L2 accesses"),
                  trend(l2["R1S0", "c2p"], lambda value: value < 1.0,
                        "R1S0 C2P reduces L2 accesses")])

    lines.extend(["", "## Counter-direction outliers requiring explanation", "",
                  "Rows below are not silently averaged away: they reduce L2 access "
                  "but slow down. The displayed C2P queue, candidate, false-positive, "
                  "and target-timeout rates are evidence for diagnosis, not automatic "
                  "proof of a single root cause.", "",
                  "| Case | Local group | C2P IPC | C2P L2 access | Candidates/query | Query bypass rate | Target-timeout rate | Snapshot FP rate |",
                  "|---|---|---:|---:|---:|---:|---:|---:|"])
    if c2p_outliers:
        for item in c2p_outliers:
            lines.append("| {case} | {group} | {ipc:.3f} | {l2:.3f} | {candidates} | "
                         "{queue_bypass} | {probe_timeout} | {fp} |".format(
                             **{**item,
                                "candidates": format_value(item["candidates"]),
                                "queue_bypass": format_value(item["queue_bypass"]),
                                "probe_timeout": format_value(item["probe_timeout"]),
                                "fp": format_value(item["fp"])}))
    else:
        lines.append("| — | — | — | — | — | — | — | — |")

    lines.extend(["", "## Mechanism and provenance gates", "",
                  "- `analyze_c2p_paper16.py --strict` requires every seven-mode "
                  "bundle and every 50-cycle baseline, oracle timing invariance, "
                  "and one avoided L2 request per remote hit.",
                  "- Figure 12 uses independent CCD and C2P tag-time TP/FN/FP/TN "
                  "classification.  Figure 13 is a distinct measured m/k sweep, "
                  "not an interpolation of the default point.",
                  "- Figure 14 is built from the dynamic peer-access histograms, "
                  "split into completed remote-hit and miss/fallback paths."])
    lines.extend(["", "## Default C2P binary-equivalence audit", "",
                  "The parameterized Snapshot Matrix must preserve the default "
                  "5,120-row/four-encoding C2P point before pre-parameterization "
                  "replays can enter this aggregate. The strict closeout requires a "
                  "paired, field-by-field equivalence result for every local case.",
                  "",
                  "- audit rows: {}; equivalent cases: {}.".format(
                      len(equivalence_rows), len(equivalent_cases)),
                  "- audit artifact: {}.".format(
                      "present" if equivalence_path.is_file() else "missing")])
    if args.figures_dir:
        figures = ("fig10_normalized_ipc", "fig11_l2_access",
                   "fig12_filtering_accuracy", "fig13_ipc_vs_fp_ratio",
                   "fig14_peer_probe_distribution")
        lines.extend(["", "## Rendered artifacts", ""])
        for figure in figures:
            rendered = [extension for extension in ("pdf", "svg", "png")
                        if (args.figures_dir / (figure + "." + extension)).is_file()]
            lines.append(f"- {figure}: {', '.join(rendered) if rendered else 'missing'}")
        style_audit = args.figures_dir / "figure_style_audit.md"
        lines.append(f"- figure-style audit: {'present' if style_audit.is_file() else 'missing'}")

    if args.queue_sensitivity_csv:
        queue_rows = read_csv(args.queue_sensitivity_csv)
        lines.extend(["", "## Finite-queue sensitivity diagnostic", "",
                      "This is a separate Btree model diagnostic, not a Figure-10 "
                      "data point. It quantifies whether requester/target queue "
                      "headroom explains an observed C2P opportunity gap.", "",
                      "| Point | Requester FIFO | Target FIFO | Timeout | Cycle / default | Remote hits / default | Requester bypass | Target timeout |",
                      "|---|---:|---:|---:|---:|---:|---:|---:|"])
        for row in queue_rows:
            lines.append("| {} | {} | {} | {} | {} | {} | {} | {} |".format(
                row["point"], row["query_queue_size"],
                row["target_probe_queue_size"], row["probe_timeout"],
                format_value(number(row, "cycle_ratio_to_default")),
                format_value(number(row, "remote_hit_ratio_to_default")),
                row["c2p_queries_queue_bypass"],
                row["c2p_fallback_probe_timeout"]))

    lines.extend(["", "## Separate V100 extension set", "",
                  "The ISPASS (BFS, LIB, LPS, RAY) and Pannotia "
                  "(color_max, fw_block, mis, pagerank) traces are now available as "
                  "a V100-generated extension set. They are deliberately excluded "
                  "from this canonical 16-workload aggregate: their trace capture, "
                  "inputs, hashes, compatibility, uncapped baseline, seven-mode, and "
                  "L2=50 evidence are audited independently by the V100 extension "
                  "closeout."])
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
