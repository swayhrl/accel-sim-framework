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
    # Figure 10/11 use direction-specific hatching in addition to the pastel
    # fills: ATA '/', RING '\\', and C2P-Cache cross-hatched.  Do not reduce
    # this to colour alone; the paper uses the texture vocabulary in print.
    "ata": ("ATA", "#9ecae1", "///"),
    "ccd": ("CCD", "#9aa8b0", ""),
    "ring": ("RING", "#f5c7b8", "\\\\"),
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
        fig.savefig(root / (stem + "." + extension), bbox_inches="tight", dpi=300)
    plt.close(fig)


def write_style_audit(root, formats):
    """Record how every published plot maps to its paper counterpart.

    The plot pixels alone do not prove that a similar-looking chart used the
    intended data.  Keep this next to the vector/raster artifacts so review
    can check both the presentation convention and the input CSV field.
    """
    root.joinpath("figure_style_audit.md").write_text("""# C2P paper-figure style and data audit

All figures use the manuscript's compact Times-style typography, closed axes,
black bar outlines, dashed workload-group separators, and the same stable
mechanism vocabulary: ATA light blue with forward hatching, CCD blue-gray,
RING pale salmon with back hatching, and C2P-Cache salmon with cross-hatching.
Published formats: %s.

| Local artifact | Paper counterpart | Data source | Required visual convention |
|---|---|---|---|
| `fig10_normalized_ipc` | Fig. 10 | `paper16_modes.csv: ipc_normalized` | Full-width grouped four-bar strip; ATA/CCD/RING/C2P order; C2P cross-hatch; R0S0/R1S0/R0S1/R1S1 separators and in-strip labels. |
| `fig11_l2_access` | Fig. 11 | `paper16_modes.csv: l2_access_normalized` | Compact R1S0/R1S1 four-bar strip using the same mechanism colors, order, hatch, and group separators. |
| `fig12_filtering_accuracy` | Fig. 12 | `paper16_cases.csv: ccd_*_rate`, `snapshot_*_rate` | Full-width stacked CCD/C2P pair per case; eight-entry TP/FN/FP/TN legend; blue-gray CCD and salmon C2P families with the manuscript's hatch distinction. |
| `fig13_ipc_vs_fp_ratio` | Fig. 13 | `fp_sweep_binned.csv` | Compact four-group FP-ratio strip; median IPC line and P25--P75 band; manuscript group colors, markers and line styles.  Only measured, populated bins are drawn. |
| `fig14_peer_probe_distribution` | Fig. 14 | `paper16_modes.csv: c2p_peer_access_{hit,miss}_{p90,p95,p99,max}` | Two compact `(a) Hit` / `(b) Miss` panels; P90/P95/P99/MAX x-axis; four manuscript group line/marker styles, shared 8-access-referenced scale, and no cropping of a measured local MAX. |

The local traces are not the authors' unpublished trace inputs; visual
matching does not imply numerical identity.  The strict analyzer and final
report provide the corresponding mechanism/provenance audit.
""" % ", ".join(formats))


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


def strip_bars(rows, metric, ylabel, filename, out, formats, groups=GROUPS,
               lower=0.0, upper=None, figsize=(7.15, 1.52)):
    data = grouped_cases(rows, metric, groups)
    fig, axis = plt.subplots(figsize=figsize)
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
    axis.grid(axis="y", color="#b0b0b0", linewidth=0.35, alpha=0.45)
    handles, legend_labels = axis.get_legend_handles_labels()
    axis.legend(handles, legend_labels, ncol=2, loc="upper left", frameon=False,
                fontsize=8, handlelength=1.2, columnspacing=0.8, handletextpad=0.35)
    save(fig, out, filename, formats)


def filtering_accuracy(cases, out, formats):
    systems = (
        ("CCD", "ccd", (("tp_rate", "CCD TP", "#6fa8c5", "///"),
                        ("fn_rate", "CCD FN", "#b9cbd5", ""),
                        ("fp_rate", "CCD FP", "#92a6b0", "\\\\"),
                        ("tn_rate", "CCD TN", "#edf1f3", ""))),
        ("C2P-Cache", "snapshot", (("tp_rate", "C2P-Cache TP", "#e89b88", "xx"),
                                      ("fn_rate", "C2P-Cache FN", "#f4c5b6", ""),
                                      ("fp_rate", "C2P-Cache FP", "#d9897e", "\\\\"),
                                      ("tn_rate", "C2P-Cache TN", "#fae9e3", ""))),
    )
    # A blank Figure 12 is not evidence.  In-progress analyses lack the
    # dedicated CCD replay by design, so defer this artifact until real
    # TP/FN/FP/TN data exists.
    if not any(all(number(row, prefix + "_tp_rate") is not None
                   for _, prefix, _ in systems) for row in cases):
        return False
    fig, axis = plt.subplots(figsize=(7.15, 1.68))
    # Fig. 12's original legend distinguishes CCD and C2P classes rather
    # than only TP/FN/FP/TN.  Keep that eight-entry vocabulary: blue/gray for
    # CCD, salmon/peach for C2P, and hatching on the positive/filter-error
    # pieces so the rendered plot also remains legible in grayscale.
    x, positions, boundaries = 0.0, [], []
    for group in GROUPS:
        data = [row for row in cases if row["group"] == group and
                all(number(row, prefix + "_tp_rate") is not None
                    for _, prefix, _ in systems)]
        start = x
        for row in data:
            positions.append(x)
            for system_index, (system_name, prefix, fields) in enumerate(systems):
                bottom = 0.0
                bar_x = x + (-0.19 if system_index == 0 else 0.19)
                for suffix, name, color, hatch in fields:
                    amount = number(row, prefix + "_" + suffix) or 0.0
                    axis.bar(bar_x, amount, bottom=bottom, width=0.36, color=color,
                             hatch=hatch,
                             edgecolor="black", linewidth=0.35,
                             label=name if len(positions) == 1 else None)
                    bottom += amount
            x += 1.0
        if data:
            axis.text((start + x - 1.0) / 2.0, -0.145, group, ha="center",
                      va="top", fontsize=9, fontweight="bold", clip_on=False)
            boundaries.append(x - 0.5)
        x += 0.55
    for boundary in boundaries[:-1]:
        axis.axvline(boundary, color="#666666", linestyle=(0, (4, 4)), linewidth=0.75)
    axis.set_ylim(0, 1.08)
    axis.set_xlim(-0.55, max(0.55, x - 0.55))
    # Fig. 12 shows workload groups, not an extra CCD/C2P label below every
    # stacked pair.  The per-case identity stays in the CSV/provenance audit.
    axis.set_xticks([])
    axis.tick_params(axis="x", bottom=False, labelbottom=False)
    axis.set_ylabel("System Ratio")
    handles, legend_labels = axis.get_legend_handles_labels()
    # Matplotlib fills a multi-column legend down columns.  Interleave the
    # source order so it renders the paper's first CCD TP/FN/FP/TN row and
    # second C2P TP/FN/FP/TN row.
    if len(handles) == 8:
        order = (0, 4, 1, 5, 2, 6, 3, 7)
        handles = [handles[index] for index in order]
        legend_labels = [legend_labels[index] for index in order]
    axis.legend(handles, legend_labels, ncol=4, loc="upper left",
                frameon=False, fontsize=6.7, handlelength=1.15,
                columnspacing=0.48, handletextpad=0.28)
    save(fig, out, "fig12_filtering_accuracy", formats)
    return True


def peer_percentiles(rows, out, formats):
    fig, axes = plt.subplots(1, 2, figsize=(3.55, 1.48), sharey=True)
    metric_names = ("P90", "P95", "P99", "MAX")
    peer_fields = ["c2p_peer_access_{}_{}".format(outcome, suffix)
                   for outcome in ("hit", "miss")
                   for suffix in ("p90", "p95", "p99", "max")]
    observed = [number(row, field) for row in rows for field in peer_fields]
    observed = [item for item in observed if item is not None]
    # The paper's traces fit its shared 0--24 scale.  Preserve that exact
    # scale when local data does too, but never crop a measured MAX merely to
    # make a different trace set look visually identical.  Both panels still
    # share one eight-access-referenced scale.
    y_upper = max(24, int(np.ceil((max(observed, default=0) + 4) / 8.0)) * 8)
    y_ticks = tuple(range(0, y_upper + 1, 8))
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
        # Figure 14 uses one common access-count scale and an eight-peer
        # reference, rather than separate autoscaling per panel.
        axis.set_ylim(0, y_upper)
        axis.set_yticks(y_ticks)
        # The manuscript puts the panel marker at the upper-left and the
        # Hit/Miss label at the upper-right *inside* each small panel.
        axis.text(0.02, 0.97, "({})".format("a" if outcome == "hit" else "b"),
                  transform=axis.transAxes, ha="left", va="top", fontsize=9)
        axis.text(0.98, 0.97, "Hit" if outcome == "hit" else "Miss",
                  transform=axis.transAxes, ha="right", va="top", fontsize=9)
        axis.grid(axis="y", color="#b0b0b0", linewidth=0.35, alpha=0.45)
    axes[0].set_ylabel("Access Count")
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        axes[0].legend(handles, labels, ncol=2, frameon=False, fontsize=7.5,
                       loc="upper left", bbox_to_anchor=(0.02, 0.89),
                       handlelength=1.4, columnspacing=0.8)
    save(fig, out, "fig14_peer_probe_distribution", formats)


def fp_impact(rows, out, formats):
    # Paper Fig. 13: each workload group has its own FP-ratio interval strip;
    # the line is median IPC and the band encloses the middle 50% of points.
    fig, axis = plt.subplots(figsize=(3.55, 1.48))
    x, boundaries, tick_positions, tick_labels = 0.0, [], [], []
    for group in GROUPS:
        group_rows = sorted((row for row in rows if row["group"] == group),
                            key=lambda row: number(row, "fp_bin"))
        if not group_rows:
            x += 1.2
            continue
        start = x
        values_x = []
        medians, lower, upper = [], [], []
        for row in group_rows:
            values_x.append(x)
            tick_positions.append(x)
            tick_labels.append("{:.2g}".format(number(row, "fp_bin")))
            medians.append(number(row, "ipc_median"))
            lower.append(number(row, "ipc_p25"))
            upper.append(number(row, "ipc_p75"))
            x += 1.0
        color, marker, linestyle = GROUP_STYLE[group]
        axis.fill_between(values_x, lower, upper, color=color, alpha=0.25,
                          linewidth=0)
        axis.plot(values_x, medians, color=color, marker=marker, markersize=4.2,
                  markeredgecolor="black", markeredgewidth=0.35,
                  linestyle=linestyle, linewidth=1.35)
        axis.text((start + x - 1.0) / 2.0, 1.47, group, ha="center", va="top",
                  fontsize=8.5, fontweight="bold")
        boundaries.append(x - 0.5)
        x += 0.45
    for boundary in boundaries[:-1]:
        axis.axvline(boundary, color="#666666", linestyle=(0, (4, 4)), linewidth=0.75)
    # Include only bins actually populated by the sweep; Figure 13 must not
    # manufacture evenly spaced points for unavailable FP intervals.
    axis.set_xticks(tick_positions)
    axis.set_xticklabels(tick_labels, fontsize=8)
    axis.set_ylim(0.80, 1.50)
    axis.set_xlim(-0.4, max(0.6, x - 0.45))
    axis.set_ylabel("Normalized IPC")
    axis.set_xlabel("FP ratio")
    axis.axhline(1.0, color="#666666", linewidth=0.65)
    axis.grid(axis="y", color="#b0b0b0", linewidth=0.35, alpha=0.45)
    save(fig, out, "fig13_ipc_vs_fp_ratio", formats)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", required=True, type=Path)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--formats", default="pdf,svg,png")
    args = parser.parse_args()
    output = args.out_dir or args.analysis_dir / "figures"
    output.mkdir(parents=True, exist_ok=True)
    formats = tuple(item.strip() for item in args.formats.split(",") if item.strip())
    setup()
    write_style_audit(output, formats)
    modes = read_csv(args.analysis_dir / "paper16_modes.csv")
    cases = read_csv(args.analysis_dir / "paper16_cases.csv")
    strip_bars(modes, "ipc_normalized", "Normalized IPC", "fig10_normalized_ipc",
               output, formats, lower=0.0, upper=1.65)
    strip_bars(modes, "l2_access_normalized", "Norm. L2 access", "fig11_l2_access",
               output, formats, groups=("R1S0", "R1S1"), lower=0.0, upper=1.25,
               figsize=(3.55, 1.48))
    filtering_accuracy(cases, output, formats)
    fp_bins = args.analysis_dir / "fp_sweep_binned.csv"
    if fp_bins.is_file():
        fp_impact(read_csv(fp_bins), output, formats)
    peer_percentiles(modes, output, formats)


if __name__ == "__main__":
    main()
