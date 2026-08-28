#!/usr/bin/env python3
"""Render the non-evidentiary Fig. 11 paper-R/S rebucketing diagnostic.

Unlike the original local Fig. 11 artifact, this script uses the retained,
audited ``paper16_modes.csv`` source directly.  It deliberately changes only
the presentation grouping: all metrics remain the final campaign's measured
``l2_access_normalized`` values, normalized to the baseline of the same
workload.  The result is an 0826 exploration, not a replacement for the
reviewed local-R/S result nor a formal paper figure.
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties


GROUPS = ("R1S0", "R1S1")
MODES = ("ata", "ccd", "ring", "c2p")
STYLE = {
    "ata": ("ATA", "#9ecae1", "///"),
    "ccd": ("CCD", "#9aa8b0", ""),
    "ring": ("RING", "#f5c7b8", "\\\\"),
    "c2p": ("本文提到的结构", "#e89b88", "xx"),
}
PAPER_ORDER = {
    "R1S0": ("CU", "HO", "GA"),
    "R1S1": ("LU", "SG", "3M", "GE", "B+", "2D", "ST"),
}


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def collect_rows(cases, modes):
    """Join the audited case labels to the five measured mode rows."""
    by_case = {row["case"]: row for row in cases}
    joined = defaultdict(dict)
    for row in modes:
        if row["mode"] in ("baseline", *MODES):
            joined[row["case"]][row["mode"]] = row

    records = []
    for group in GROUPS:
        for abbreviation in PAPER_ORDER[group]:
            matches = [row for row in cases if row["abbr"] == abbreviation]
            if len(matches) != 1:
                raise RuntimeError("expected exactly one case for {}".format(abbreviation))
            case = matches[0]
            available = joined[case["case"]]
            required = ("baseline", *MODES)
            if any(mode not in available for mode in required):
                raise RuntimeError("incomplete measured mode set for {}".format(case["case"]))
            records.append({
                "case": case["case"],
                "abbr": abbreviation,
                "paper_group": group,
                "local_group": case["group"],
                "baseline": float(available["baseline"]["l2_access_normalized"]),
                **{mode: float(available[mode]["l2_access_normalized"])
                   for mode in MODES},
            })
    return records


def averages(records):
    result = []
    for group in GROUPS:
        members = [row for row in records if row["paper_group"] == group]
        result.append({
            "paper_group": group,
            "workloads": ", ".join(row["abbr"] for row in members),
            "baseline": float(np.mean([row["baseline"] for row in members])),
            **{mode: float(np.mean([row[mode] for row in members])) for mode in MODES},
        })
    return result


def plot(records, group_averages, output):
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 9, "axes.linewidth": 0.8, "axes.spines.top": True,
        "axes.spines.right": True, "pdf.fonttype": 42, "ps.fonttype": 42,
        "hatch.linewidth": 0.35,
    })
    average_by_group = {row["paper_group"]: row for row in group_averages}
    fig, axis = plt.subplots(figsize=(4.15, 1.60))
    position, width, tick_x, tick_labels, boundaries = 0.0, 0.19, [], [], []
    for group in GROUPS:
        members = [row for row in records if row["paper_group"] == group]
        start = position
        for row in members:
            tick_x.append(position)
            tick_labels.append(row["abbr"])
            for index, mode in enumerate(MODES):
                label, color, hatch = STYLE[mode]
                axis.bar(position + (index - 1.5) * width, row[mode], width,
                         color=color, hatch=hatch, edgecolor="black", linewidth=0.45,
                         label=label if len(tick_x) == 1 else None)
            position += 1.0
        avg = average_by_group[group]
        tick_x.append(position)
        tick_labels.append("AVG")
        for index, mode in enumerate(MODES):
            _, color, hatch = STYLE[mode]
            axis.bar(position + (index - 1.5) * width, avg[mode], width,
                     color=color, hatch=hatch, edgecolor="black", linewidth=0.45)
        position += 1.0
        axis.text((start + position - 1.0) / 2.0, 0.045, group,
                  ha="center", va="bottom", fontsize=9, fontweight="bold")
        boundaries.append(position - 0.5)
        position += 0.55

    axis.axvline(boundaries[0], color="#666666", linestyle=(0, (4, 4)), linewidth=0.75)
    axis.axhline(1.0, color="black", linewidth=0.65)
    axis.set_xlim(-0.55, position - 0.55)
    axis.set_ylim(0.0, 1.25)
    axis.set_xticks(tick_x)
    axis.set_xticklabels(tick_labels, fontsize=8)
    axis.set_ylabel("Normalized L2 Access")
    axis.grid(axis="y", color="#b0b0b0", linewidth=0.35, alpha=0.45)
    handles, labels = axis.get_legend_handles_labels()
    # Matplotlib's generic serif fallback does not include Chinese glyphs;
    # apply the installed CJK serif only to the one bilingual legend label.
    cjk_serif = FontProperties(
        fname="/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", size=5.8)
    axis.legend(handles, labels, ncol=4, loc="upper left", frameon=False,
                prop=cjk_serif, handlelength=0.95, columnspacing=0.28,
                handletextpad=0.2)
    fig.tight_layout(pad=0.55)
    for extension in ("svg", "pdf", "png"):
        fig.savefig(output / ("fig11_paper_rs_rebucket16." + extension),
                    bbox_inches="tight", dpi=300)
    plt.close(fig)


def write_readme(path, source, records, group_averages):
    lines = [
        "# Fig. 11 paper-R/S rebucketed local-16 note",
        "",
        "> **Non-evidentiary 0826 diagnostic.** This reuses the final local",
        "> `l2_access_normalized` measurements but groups the same 16 workloads",
        "> with the C2P paper's R/S labels. It is not a new experiment, a formal",
        "> paper figure, or a basis for a performance claim.",
        "",
        "## Definition and provenance",
        "",
        "Each value is `mode l2_total_cache_accesses / baseline l2_total_cache_accesses`",
        "for the same workload. The source is the retained final analysis CSV:",
        "`{}`.".format(source),
        "The baseline is therefore 1.000 for every workload and is used only as",
        "the normalization reference; its redundant bars are not plotted.",
        "",
        "## Paper-R/S group averages",
        "",
        "| Paper R/S group | Workloads | ATA | CCD | RING | 本文提到的结构 |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in group_averages:
        lines.append("| {paper_group} | {workloads} | {ata:.3f} | {ccd:.3f} | {ring:.3f} | {c2p:.3f} |".format(**row))
    lines += [
        "",
        "## Per-workload measured values",
        "",
        "| Paper group | Workload | Local group | ATA | CCD | RING | 本文提到的结构 |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in records:
        lines.append("| {paper_group} | {abbr} | {local_group} | {ata:.3f} | {ccd:.3f} | {ring:.3f} | {c2p:.3f} |".format(**row))
    lines += [
        "",
        "## Rebuild",
        "",
        "```bash",
        "python3 rebuild_fig11_paper_rs_rebucket16.py --analysis-dir <final-analysis-dir>",
        "```",
    ]
    path.write_text("\n".join(lines) + "\n")


def main():
    default_analysis = Path(
        "/workspace/worktrees/accel-sim-c2p-cache/"
        "hw_run/c2p-paper16-analysis-final-v7-20260821"
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-dir", type=Path, default=default_analysis)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()

    cases_path = args.analysis_dir / "paper16_cases.csv"
    modes_path = args.analysis_dir / "paper16_modes.csv"
    records = collect_rows(read_csv(cases_path), read_csv(modes_path))
    group_averages = averages(records)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "fig11_paper_rs_rebucket16_l2_access.csv",
              ("case", "abbr", "paper_group", "local_group", "baseline", *MODES), records)
    write_csv(args.output_dir / "fig11_paper_rs_rebucket16_group_averages.csv",
              ("paper_group", "workloads", "baseline", *MODES), group_averages)
    plot(records, group_averages, args.output_dir)
    write_readme(args.output_dir / "README.md", modes_path, records, group_averages)


if __name__ == "__main__":
    main()
