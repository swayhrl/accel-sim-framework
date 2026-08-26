#!/usr/bin/env python3
"""Render a paper-style local reproduction of C2P-Cache Figure 3.

Figure 3 classifies workloads by redundant-L2 opportunity (R) and sensitivity
to lower-cache latency (S).  This renderer deliberately consumes the audited
``paper16_cases.csv`` rather than a hand-maintained table:

* R = oracle peer hits / eligible L1 misses at L2=200 cycles;
* S = baseline IPC(L2=50) / baseline IPC(L2=200), equivalently
      baseline_cycles(L2=200) / baseline_cycles(L2=50).

The output is a local-data counterpart, not a claim that its points reproduce
the authors' unpublished traces.  It retains the paper's four group colours
and marker vocabulary, exports editable vector formats, and writes the exact
plotted points beside the figure for audit.
"""

import argparse
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


GROUP_ORDER = ("R0S1", "R1S1", "R1S0", "R0S0")
GROUP_STYLE = {
    # Paper Fig. 3: red diamond, orange circle, purple triangle, green square.
    "R0S1": {"label": "R0S1", "color": "#d74b43", "marker": "D"},
    "R1S1": {"label": "R1S1", "color": "#e5a43a", "marker": "o"},
    "R1S0": {"label": "R1S0", "color": "#9a5ab5", "marker": "^"},
    "R0S0": {"label": "R0S0", "color": "#4b9c50", "marker": "s"},
}


def read_rows(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def classify(redundancy, sensitivity, r_threshold, s_threshold):
    return "R{}S{}".format("1" if redundancy >= r_threshold else "0",
                            "1" if sensitivity >= s_threshold else "0")


def load_points(path, r_threshold, s_threshold):
    points = []
    for row in read_rows(path):
        try:
            redundancy = float(row["oracle_redundancy"])
            sensitivity = float(row["l2_sensitivity"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("missing numeric R/S value for {}".format(
                row.get("case", "unknown"))) from error
        if not math.isfinite(redundancy) or not math.isfinite(sensitivity):
            raise ValueError("non-finite R/S value for {}".format(row["case"]))
        calculated = classify(redundancy, sensitivity, r_threshold, s_threshold)
        if row.get("group") != calculated:
            raise ValueError(
                "stored group disagrees with thresholds for {}: {} != {}".format(
                    row["case"], row.get("group"), calculated))
        points.append({
            "case": row["case"],
            "abbr": row.get("abbr", row["case"]),
            "paper_group": row.get("paper_group", ""),
            "group": calculated,
            "redundancy": redundancy,
            "sensitivity": sensitivity,
        })
    return points


def configure_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
        "font.size": 9,
        "axes.linewidth": 0.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def write_points(path, points):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=("case", "abbr", "paper_group", "group",
                        "oracle_redundancy", "l2_sensitivity"))
        writer.writeheader()
        for point in points:
            writer.writerow({
                "case": point["case"],
                "abbr": point["abbr"],
                "paper_group": point["paper_group"],
                "group": point["group"],
                "oracle_redundancy": "{:.12g}".format(point["redundancy"]),
                "l2_sensitivity": "{:.12g}".format(point["sensitivity"]),
            })


def render(points, output, formats, r_threshold, s_threshold):
    # The source paper uses a compact near-square scatter.  Keep that geometry
    # and its closed black frame, but extend the S axis to include the measured
    # Stencil point rather than clipping local data to the paper's y range.
    y_max = max(1.55, math.ceil(max(point["sensitivity"] for point in points) * 10) / 10)
    fig, axis = plt.subplots(figsize=(3.55, 2.72))

    for group in GROUP_ORDER:
        group_points = [point for point in points if point["group"] == group]
        if not group_points:
            continue
        style = GROUP_STYLE[group]
        axis.scatter(
            [point["redundancy"] for point in group_points],
            [point["sensitivity"] for point in group_points],
            s=34,
            marker=style["marker"],
            facecolor=style["color"],
            edgecolor="black",
            linewidth=0.45,
            label=style["label"],
            zorder=3,
        )

    # These subdued guide lines make the local threshold contract explicit;
    # they are intentionally secondary to the paper-like marker legend.
    axis.axvline(r_threshold, color="#777777", linewidth=0.65,
                 linestyle=(0, (3, 3)), zorder=1)
    axis.axhline(s_threshold, color="#777777", linewidth=0.65,
                 linestyle=(0, (3, 3)), zorder=1)

    axis.set_xlim(-0.02, 1.02)
    axis.set_ylim(0.98, y_max + 0.02)
    axis.set_xlabel("Redundant L2 Access Ratio")
    axis.set_ylabel("Normalized IPC (L2=50 / L2=200)")
    axis.set_xticks((0.0, 0.2, 0.4, 0.6, 0.8, 1.0))
    axis.grid(color="#c7c7c7", linewidth=0.35, alpha=0.45, zorder=0)
    axis.legend(loc="upper right", ncol=2, frameon=False, fontsize=8,
                handletextpad=0.35, columnspacing=0.85, borderaxespad=0.25)
    fig.tight_layout(pad=0.55)
    for extension in formats:
        fig.savefig(output / ("fig3_local_rs64." + extension),
                    bbox_inches="tight", dpi=300)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", required=True, type=Path,
                        help="directory containing audited paper16_cases.csv")
    parser.add_argument("--out-dir", type=Path,
                        help="defaults to <analysis-dir>/figures_local_rs64")
    parser.add_argument("--formats", default="pdf,svg,png")
    parser.add_argument("--redundancy-threshold", type=float, default=0.30)
    parser.add_argument("--sensitivity-threshold", type=float, default=1.10)
    parser.add_argument("--expected-cases", type=int, default=16)
    args = parser.parse_args()

    cases = args.analysis_dir / "paper16_cases.csv"
    if not cases.is_file():
        raise SystemExit("missing audited input: {}".format(cases))
    points = load_points(cases, args.redundancy_threshold,
                         args.sensitivity_threshold)
    if len(points) != args.expected_cases:
        raise SystemExit("expected {} points, found {}".format(
            args.expected_cases, len(points)))

    output = args.out_dir or args.analysis_dir / "figures_local_rs64"
    output.mkdir(parents=True, exist_ok=True)
    formats = tuple(item.strip() for item in args.formats.split(",") if item.strip())
    configure_style()
    write_points(output / "fig3_local_rs64_points.csv", points)
    render(points, output, formats, args.redundancy_threshold,
           args.sensitivity_threshold)


if __name__ == "__main__":
    main()
