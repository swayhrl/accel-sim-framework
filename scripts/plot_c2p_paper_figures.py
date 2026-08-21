#!/usr/bin/env python3
"""Render paper-style C2P figures from analyze_c2p_paper16.py output.

The composition deliberately follows C2P-Cache Figures 10--14: a single
workload strip divided by R/S class, mechanism-stable colors and hatches, and
the Hit/Miss P90--MAX probe summary. It is a reusable plotting baseline, not
a claim that local traces are the paper's original inputs.
"""

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


GROUPS = ("R0S0", "R1S0", "R0S1", "R1S1")
MODES = ("ata", "ccd", "ring", "c2p")
STYLE = {
    "ata": ("ATA", "#9ecae1", ""),
    "ccd": ("CCD", "#9aa8b0", ""),
    "ring": ("RING", "#f5c7b8", ""),
    "c2p": ("C2P-Cache", "#e89b88", "xx"),
}
GROUP_STYLE = {
    "R0S0": ("#4c9ed9", "o", "-"),
    "R1S0": ("#e4a72c", "s", "--"),
    "R0S1": ("#51b7a8", "^", ":"),
    "R1S1": ("#dc8a7b", "D", "-"),
}


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def number(row, field):
    try:
        return float(row[field])
    except (KeyError, TypeError, ValueError):
        return None


def setup():
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 9, "axes.linewidth": 0.8, "axes.spines.top": True,
        "axes.spines.right": True, "pdf.fonttype": 42, "ps.fonttype": 42,
        "hatch.linewidth": 0.35,
    })


def save(fig, root, stem, formats):
    fig.tight_layout(pad=0.55)
    for extension in formats:
        fig.savefig(root / (stem + "." + extension), bbox_inches="tight")
    plt.close(fig)


def grouped_cases(rows, metric, groups=GROUPS):
    result = []
    for group in groups:
        cases, labels = [], []
        names = sorted({row["case"] for row in rows if row["group"] == group})
        for case in names:
            values = {row["mode"]: number(row, metric) for row in rows
                      if row["case"] == case}
            if all(values.get(mode) is not None for mode in MODES):
                cases.append(values)
                labels.append(next(row["abbr"] for row in rows if row["case"] == case))
        if cases:
            cases.append({mode: float(np.mean([case[mode] for case in cases]))
                          for mode in MODES})
            labels.append("AVG")
        result.append((group, labels, cases))
    return result


def strip_bars(rows, metric, ylabel, title, filename, out, formats, groups=GROUPS,
               lower=0.0, upper=None):
    data = grouped_cases(rows, metric, groups)
    fig, axis = plt.subplots(figsize=(12.2, 2.55))
    x, width, positions, labels, boundaries = 0.0, 0.19, [], [], []
    for group, group_labels, cases in data:
        start = x
        for label, values in zip(group_labels, cases):
            positions.append(x)
            labels.append(label)
            for index, mode in enumerate(MODES):
                name, color, hatch = STYLE[mode]
                axis.bar(x + (index - 1.5) * width, values[mode], width,
                         color=color, hatch=hatch, edgecolor="black", linewidth=0.45,
                         label=name if len(positions) == 1 else None)
            x += 1.0
        if cases:
            axis.text((start + x - 1.0) / 2.0, lower + 0.04, group,
                      ha="center", va="bottom", fontsize=9, fontweight="bold")
            boundaries.append(x - 0.5)
        x += 0.55
    for boundary in boundaries[:-1]:
        axis.axvline(boundary, color="#666666", linestyle=(0, (4, 4)), linewidth=0.75)
    axis.axhline(1.0, color="black", linewidth=0.65)
    axis.set_xlim(-0.55, max(0.55, x - 0.55))
    axis.set_ylim(lower, upper or max(1.15, axis.get_ylim()[1]))
    axis.set_xticks(positions)
    axis.set_xticklabels(labels, fontsize=8)
    axis.set_ylabel(ylabel)
    axis.set_title(title, fontsize=10, pad=5)
    axis.grid(axis="y", color="#b0b0b0", linewidth=0.35, alpha=0.45)
    handles, legend_labels = axis.get_legend_handles_labels()
    axis.legend(handles, legend_labels, ncol=2, loc="upper left", frameon=False,
                fontsize=8, handlelength=1.2, columnspacing=0.8, handletextpad=0.35)
    save(fig, out, filename, formats)


def filtering_accuracy(cases, out, formats):
    fig, axis = plt.subplots(figsize=(12.2, 2.7))
    fields = (("snapshot_tp_rate", "C2P-Cache TP", "#e89b88", "xx"),
              ("snapshot_fn_rate", "C2P-Cache FN", "#dbe7ea", ""),
              ("snapshot_fp_rate", "C2P-Cache FP", "#f3c2b4", "\\\\"),
              ("snapshot_tn_rate", "C2P-Cache TN", "#efefef", ""))
    x, positions, labels, boundaries = 0.0, [], [], []
    for group in GROUPS:
        data = [row for row in cases if row["group"] == group and
                number(row, "snapshot_tp_rate") is not None]
        start = x
        for row in data:
            positions.append(x)
            labels.append(row["abbr"])
            bottom = 0.0
            for field, name, color, hatch in fields:
                amount = number(row, field) or 0.0
                axis.bar(x, amount, bottom=bottom, width=0.72, color=color,
                         hatch=hatch, edgecolor="black", linewidth=0.35,
                         label=name if len(positions) == 1 else None)
                bottom += amount
            x += 1.0
        if data:
            axis.text((start + x - 1.0) / 2.0, 0.04, group, ha="center",
                      va="bottom", fontsize=9, fontweight="bold")
            boundaries.append(x - 0.5)
        x += 0.55
    for boundary in boundaries[:-1]:
        axis.axvline(boundary, color="#666666", linestyle=(0, (4, 4)), linewidth=0.75)
    axis.set_ylim(0, 1.08)
    axis.set_xlim(-0.55, max(0.55, x - 0.55))
    axis.set_xticks(positions)
    axis.set_xticklabels(labels, fontsize=8)
    axis.set_ylabel("System Ratio")
    axis.set_title("C2P-Cache miss-time TP/FN/FP/TN", fontsize=10, pad=5)
    axis.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.18),
                frameon=False, fontsize=8, handlelength=1.2, columnspacing=0.7)
    save(fig, out, "fig12_filtering_accuracy", formats)


def peer_percentiles(rows, out, formats):
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 2.65), sharey=True)
    metric_names = ("P90", "P95", "P99", "MAX")
    for axis, outcome in zip(axes, ("hit", "miss")):
        for group in GROUPS:
            data = [row for row in rows if row["group"] == group and row["mode"] == "c2p"]
            fields = ["c2p_peer_access_{}_{}".format(outcome, suffix.lower())
                      for suffix in ("p90", "p95", "p99", "max")]
            values = []
            for field in fields:
                samples = [number(row, field) for row in data]
                samples = [sample for sample in samples if sample is not None]
                values.append(float(np.mean(samples)) if samples else np.nan)
            if not np.all(np.isnan(values)):
                color, marker, linestyle = GROUP_STYLE[group]
                axis.plot(range(4), values, color=color, marker=marker, markersize=4.2,
                          markeredgecolor="black", markeredgewidth=0.35,
                          linestyle=linestyle, linewidth=1.35, label=group)
        axis.axhline(8.0, color="#666666", linestyle=(0, (4, 3)), linewidth=0.7)
        axis.set_xticks(range(4))
        axis.set_xticklabels(metric_names)
        axis.set_title("({}) {}".format("a" if outcome == "hit" else "b",
                                         "Hit" if outcome == "hit" else "Miss"),
                       loc="left", fontsize=10)
        axis.grid(axis="y", color="#b0b0b0", linewidth=0.35, alpha=0.45)
    axes[0].set_ylabel("Access Count")
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        axes[0].legend(handles, labels, ncol=2, frameon=False, fontsize=7.5,
                       loc="upper left", handlelength=1.4, columnspacing=0.8)
    fig.suptitle("Peer-L1 access-count distribution", y=1.03, fontsize=10)
    save(fig, out, "fig14_peer_probe_distribution", formats)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", required=True, type=Path)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--formats", default="pdf,png")
    args = parser.parse_args()
    output = args.out_dir or args.analysis_dir / "figures"
    output.mkdir(parents=True, exist_ok=True)
    formats = tuple(item.strip() for item in args.formats.split(",") if item.strip())
    setup()
    modes = read_csv(args.analysis_dir / "paper16_modes.csv")
    cases = read_csv(args.analysis_dir / "paper16_cases.csv")
    strip_bars(modes, "ipc_normalized", "Normalized IPC",
               "Normalized IPC across workload groups", "fig10_normalized_ipc",
               output, formats, lower=0.0, upper=1.65)
    strip_bars(modes, "l2_access_normalized", "Norm. L2 access",
               "Normalized L2 accesses for R1S0 and R1S1", "fig11_l2_access",
               output, formats, groups=("R1S0", "R1S1"), lower=0.0, upper=1.25)
    filtering_accuracy(cases, output, formats)
    peer_percentiles(modes, output, formats)


if __name__ == "__main__":
    main()
