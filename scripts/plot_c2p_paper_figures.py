#!/usr/bin/env python3
"""Render reusable paper-style figures from analyze_c2p_paper16.py output."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


GROUPS = ("R0S0", "R1S0", "R0S1", "R1S1")
MODE_LABEL = {"ata": "ATA", "ccd": "CCD", "ring": "RING", "c2p": "C2P",
              "ideal": "Ideal"}
COLORS = {"ata": "#4c78a8", "ccd": "#f58518", "ring": "#54a24b",
          "c2p": "#e45756", "ideal": "#b279a2"}


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def number(row, field):
    try:
        return float(row[field])
    except (KeyError, TypeError, ValueError):
        return None


def save(fig, root, stem, formats):
    fig.tight_layout()
    for extension in formats:
        fig.savefig(root / (stem + "." + extension), bbox_inches="tight")
    plt.close(fig)


def grouped_ipc(rows, out, formats):
    fig, axes = plt.subplots(2, 2, figsize=(12, 6), sharey=True)
    for axis, group in zip(axes.flat, GROUPS):
        cases = sorted({row["case"] for row in rows if row["group"] == group and
                        row["mode"] == "baseline"})
        modes = ("ata", "ccd", "ring", "c2p")
        values = {mode: [] for mode in modes}
        kept = []
        for case in cases:
            per_mode = {row["mode"]: number(row, "ipc_normalized") for row in rows
                        if row["case"] == case and row["mode"] in modes}
            if any(per_mode.get(mode) is None for mode in modes):
                continue
            kept.append(case)
            for mode in modes:
                values[mode].append(per_mode[mode])
        x = np.arange(len(kept))
        width = 0.19
        for index, mode in enumerate(modes):
            axis.bar(x + (index - 1.5) * width, values[mode], width,
                     label=MODE_LABEL[mode], color=COLORS[mode], edgecolor="black",
                     linewidth=0.35)
        axis.axhline(1.0, color="black", linewidth=0.7)
        axis.set_title("{} (n={})".format(group, len(kept)), fontweight="bold")
        axis.set_xticks(x)
        axis.set_xticklabels(kept, rotation=35, ha="right", fontsize=8)
        axis.grid(axis="y", linewidth=0.35, alpha=0.35)
    axes[0, 0].set_ylabel("Normalized IPC")
    axes[1, 0].set_ylabel("Normalized IPC")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False)
    fig.suptitle("C2P paper16: normalized IPC by reuse/latency class", y=1.03)
    save(fig, out, "fig10_normalized_ipc", formats)


def l2_access(rows, out, formats):
    fig, axis = plt.subplots(figsize=(7.5, 3.8))
    modes = ("ideal", "ata", "ccd", "ring", "c2p")
    width = 0.15
    x = np.arange(len(GROUPS))
    for index, mode in enumerate(modes):
        averages = []
        for group in GROUPS:
            values = [number(row, "l2_access_normalized") for row in rows
                      if row["group"] == group and row["mode"] == mode]
            values = [value for value in values if value is not None]
            averages.append(np.mean(values) if values else np.nan)
        axis.bar(x + (index - 2) * width, averages, width, label=MODE_LABEL[mode],
                 color=COLORS[mode], edgecolor="black", linewidth=0.35)
    axis.axhline(1.0, color="black", linewidth=0.7)
    axis.set_xticks(x)
    axis.set_xticklabels(GROUPS)
    axis.set_ylabel("Normalized total L2 accesses")
    axis.set_title("C2P paper16: L2 access variation")
    axis.grid(axis="y", linewidth=0.35, alpha=0.35)
    axis.legend(ncol=5, frameon=False, fontsize=8)
    save(fig, out, "fig11_l2_access", formats)


def filtering_accuracy(cases, out, formats):
    fig, axes = plt.subplots(2, 2, figsize=(12, 5.8), sharey=True)
    fields = (("snapshot_tp_rate", "TP", "#59a14f"),
              ("snapshot_fn_rate", "FN", "#4c78a8"),
              ("snapshot_fp_rate", "FP", "#e15759"),
              ("snapshot_tn_rate", "TN", "#bab0ab"))
    for axis, group in zip(axes.flat, GROUPS):
        data = [row for row in cases if row["group"] == group and
                number(row, "snapshot_tp_rate") is not None]
        x = np.arange(len(data))
        bottom = np.zeros(len(data))
        for field, label, color in fields:
            values = np.array([number(row, field) or 0 for row in data])
            axis.bar(x, values, bottom=bottom, label=label, color=color,
                     edgecolor="black", linewidth=0.25)
            bottom += values
        axis.set_title("{} (n={})".format(group, len(data)), fontweight="bold")
        axis.set_xticks(x)
        axis.set_xticklabels([row["case"] for row in data], rotation=35,
                             ha="right", fontsize=8)
        axis.grid(axis="y", linewidth=0.35, alpha=0.35)
    axes[0, 0].set_ylabel("Fraction of L1 misses")
    axes[1, 0].set_ylabel("Fraction of L1 misses")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False)
    fig.suptitle("C2P paper16: miss-time Snapshot filtering accuracy", y=1.03)
    save(fig, out, "fig12_filtering_accuracy", formats)


def peer_distribution(rows, out, formats):
    fig, axes = plt.subplots(2, 2, figsize=(11, 5.8), sharex=True, sharey=True)
    for axis, group in zip(axes.flat, GROUPS):
        for outcome, style in (("hit", "-"), ("miss", "--")):
            bins = defaultdict(int)
            for row in rows:
                if row["group"] == group and row["mode"] == "c2p" and \
                        row["outcome"] == outcome:
                    bins[int(row["peer_probes"])] += int(row["count"])
            total = sum(bins.values())
            if total:
                x = sorted(bins)
                y = [bins[item] / total for item in x]
                axis.step(x, y, where="mid", label=outcome, linestyle=style,
                          linewidth=1.7)
        axis.set_title("{}".format(group), fontweight="bold")
        axis.grid(linewidth=0.35, alpha=0.35)
    axes[1, 0].set_xlabel("Peer L1s consulted")
    axes[1, 1].set_xlabel("Peer L1s consulted")
    axes[0, 0].set_ylabel("Fraction of requests")
    axes[1, 0].set_ylabel("Fraction of requests")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False)
    fig.suptitle("C2P paper16: peer-L1 access-count distribution", y=1.03)
    save(fig, out, "fig14_peer_probe_distribution", formats)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", required=True, type=Path)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--formats", default="pdf,png",
                        help="comma-separated matplotlib extensions")
    args = parser.parse_args()
    output = args.out_dir or args.analysis_dir / "figures"
    output.mkdir(parents=True, exist_ok=True)
    formats = tuple(item.strip() for item in args.formats.split(",") if item.strip())
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False,
                         "axes.spines.right": False, "pdf.fonttype": 42,
                         "ps.fonttype": 42})
    modes = read_csv(args.analysis_dir / "paper16_modes.csv")
    cases = read_csv(args.analysis_dir / "paper16_cases.csv")
    histogram = read_csv(args.analysis_dir / "paper16_probe_histogram.csv")
    grouped_ipc(modes, output, formats)
    l2_access(modes, output, formats)
    filtering_accuracy(cases, output, formats)
    peer_distribution(histogram, output, formats)


if __name__ == "__main__":
    main()
