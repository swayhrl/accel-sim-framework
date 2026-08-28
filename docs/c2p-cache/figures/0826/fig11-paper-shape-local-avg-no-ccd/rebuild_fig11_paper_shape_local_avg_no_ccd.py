#!/usr/bin/env python3
"""Build an explicitly synthetic Fig. 11 paper-shape/local-mean diagnostic.

This is not a new simulation result.  For every visible mechanism and paper
R/S group, it retains the arithmetic mean of the local measured normalized-L2
accesses but replaces the workload-to-workload shape with the displayed shape
of the corresponding bars in the C2P paper's Fig. 11.  CCD is retained in the
audit CSV only and omitted from the rendered chart at the user's request.
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties


GROUPS = ("R1S0", "R1S1")
ALL_MODES = ("ata", "ccd", "ring", "c2p")
VISIBLE_MODES = ("ata", "ring", "c2p")
STYLE = {
    "ata": ("ATA", "#9ecae1", "///"),
    "ccd": ("CCD", "#9aa8b0", ""),
    "ring": ("RING", "#f5c7b8", "\\\\"),
    "c2p": ("本结构", "#e89b88", "xx"),
}
PAPER_ORDER = {
    "R1S0": ("CU", "HO", "GA"),
    "R1S1": ("LU", "SG", "3M", "GE", "B+", "2D", "ST"),
}

# Approximate displayed bar heights, reconstructed from the publisher PDF
# vector rendering (Fig. 11) using its y=0 and y=1 grid lines.  These numbers
# are a shape reference only, not author-provided raw measurements.  The
# missing paper-only workloads FW/BV/LP are intentionally not synthesized.
PAPER_DISPLAYED = {
    "CU": {"ata": 0.272, "ring": 0.152, "c2p": 0.079},
    "HO": {"ata": 0.899, "ring": 0.899, "c2p": 0.610},
    "GA": {"ata": 0.705, "ring": 0.668, "c2p": 0.669},
    "LU": {"ata": 0.601, "ring": 0.711, "c2p": 0.421},
    "SG": {"ata": 0.621, "ring": 0.618, "c2p": 0.396},
    "3M": {"ata": 1.236, "ring": 0.944, "c2p": 0.924},
    "GE": {"ata": 1.185, "ring": 0.944, "c2p": 0.927},
    "B+": {"ata": 0.699, "ring": 0.899, "c2p": 0.584},
    "2D": {"ata": 0.944, "ring": 0.952, "c2p": 0.778},
    "ST": {"ata": 0.806, "ring": 0.927, "c2p": 0.764},
}

# Section 5.2.2 explicitly reports these C2P averages for the paper's *full*
# groups: R1S0 has CU/HO/FW/GA and R1S1 has BV/LU/SG/3M/GE/LP/B+/2D/ST.
PAPER_REPORTED_C2P_AVERAGE = {"R1S0": 0.534, "R1S1": 0.698}


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def collect_measured(cases, modes):
    by_modes = defaultdict(dict)
    for row in modes:
        if row["mode"] in ALL_MODES:
            by_modes[row["case"]][row["mode"]] = row

    records = []
    for group in GROUPS:
        for abbreviation in PAPER_ORDER[group]:
            case_rows = [row for row in cases if row["abbr"] == abbreviation]
            if len(case_rows) != 1:
                raise RuntimeError("expected exactly one case for {}".format(abbreviation))
            case = case_rows[0]
            modes_for_case = by_modes[case["case"]]
            if any(mode not in modes_for_case for mode in ALL_MODES):
                raise RuntimeError("incomplete mode set for {}".format(case["case"]))
            records.append({
                "case": case["case"],
                "abbr": abbreviation,
                "paper_group": group,
                "local_group": case["group"],
                **{mode + "_measured": float(modes_for_case[mode]["l2_access_normalized"])
                   for mode in ALL_MODES},
            })
    return records


def shape_to_local_means(records):
    """Apply ``1 + alpha * (paper - 1)`` per visible group/mode.

    The chosen alpha gives exactly the current local arithmetic mean while
    preserving every paper bar's direction relative to the normalized
    baseline, and its workload-to-workload ordering.
    """
    audit = []
    for group in GROUPS:
        members = [row for row in records if row["paper_group"] == group]
        for mode in VISIBLE_MODES:
            paper_mean = float(np.mean([PAPER_DISPLAYED[row["abbr"]][mode] for row in members]))
            local_mean = float(np.mean([row[mode + "_measured"] for row in members]))
            if not paper_mean < 1.0 or not local_mean < 1.0:
                raise RuntimeError("shape transform requires below-baseline means")
            alpha = (local_mean - 1.0) / (paper_mean - 1.0)
            for row in members:
                paper = PAPER_DISPLAYED[row["abbr"]][mode]
                row[mode + "_paper_shape"] = 1.0 + alpha * (paper - 1.0)
            audit.append({
                "paper_group": group,
                "mode": mode,
                "paper_subset_mean": paper_mean,
                "local_measured_mean": local_mean,
                "shape_scale_alpha": alpha,
            })
    return audit


def parse_group_factors(specifications):
    factors = {group: 1.0 for group in GROUPS}
    for specification in specifications:
        fields = specification.split(":")
        if len(fields) != 2 or fields[0] not in factors:
            raise ValueError("C2P factor must be R1S0:factor or R1S1:factor")
        factor = float(fields[1])
        if factor <= 0:
            raise ValueError("C2P factor must be positive")
        factors[fields[0]] = factor
    return factors


def apply_c2p_group_factors(records, factors):
    """Apply an explicitly requested post-shape C2P-only scaling."""
    for row in records:
        row["c2p_paper_shape"] *= factors[row["paper_group"]]


def group_averages(records):
    output = []
    for group in GROUPS:
        members = [row for row in records if row["paper_group"] == group]
        output.append({
            "paper_group": group,
            "workloads": ", ".join(row["abbr"] for row in members),
            **{mode + "_measured": float(np.mean([row[mode + "_measured"] for row in members]))
               for mode in ALL_MODES},
            **{mode + "_paper_shape": float(np.mean([row[mode + "_paper_shape"] for row in members]))
               for mode in VISIBLE_MODES},
        })
    return output


def plot(records, avgs, output):
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 9, "axes.linewidth": 0.8, "axes.spines.top": True,
        "axes.spines.right": True, "pdf.fonttype": 42, "ps.fonttype": 42,
        "hatch.linewidth": 0.35,
    })
    by_group = {row["paper_group"]: row for row in avgs}
    fig, axis = plt.subplots(figsize=(4.15, 1.60))
    position, width, tick_x, tick_labels, boundaries = 0.0, 0.22, [], [], []
    for group in GROUPS:
        members = [row for row in records if row["paper_group"] == group]
        start = position
        for row in members:
            tick_x.append(position)
            tick_labels.append(row["abbr"])
            for index, mode in enumerate(VISIBLE_MODES):
                label, color, hatch = STYLE[mode]
                axis.bar(position + (index - 1.0) * width, row[mode + "_paper_shape"], width,
                         color=color, hatch=hatch, edgecolor="black", linewidth=0.45,
                         label=label if len(tick_x) == 1 else None)
            position += 1.0
        tick_x.append(position)
        tick_labels.append("AVG")
        for index, mode in enumerate(VISIBLE_MODES):
            _, color, hatch = STYLE[mode]
            axis.bar(position + (index - 1.0) * width,
                     by_group[group][mode + "_paper_shape"], width,
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
    cjk_serif = FontProperties(
        fname="/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", size=5.8)
    handles, labels = axis.get_legend_handles_labels()
    axis.legend(handles, labels, ncol=3, loc="upper left", frameon=False,
                prop=cjk_serif, handlelength=0.95, columnspacing=0.28,
                handletextpad=0.2)
    fig.tight_layout(pad=0.55)
    for extension in ("svg", "pdf", "png"):
        fig.savefig(output / ("fig11_paper_shape_local_avg_no_ccd." + extension),
                    bbox_inches="tight", dpi=300)
    plt.close(fig)


def write_readme(path, source, records, avgs, audit, c2p_factors):
    lines = [
        "# Fig. 11 paper-shape / local-average / no-CCD note",
        "",
        "> **Non-evidentiary 0826 visual sensitivity.** This chart is a synthetic",
        "> construction, not simulation output. It begins by preserving each visible",
        "> design's measured local group average while imposing the displayed paper",
        "> Fig. 11 workload ordering and above/below-baseline direction. CCD is",
        "> deliberately omitted from rendering only.",
        "",
        "## Construction",
        "",
        "For a paper displayed value `p`, local measured group mean `m`, and",
        "paper subset mean `p_bar`, the rendered value is:",
        "",
        "`1 + ((m - 1) / (p_bar - 1)) * (p - 1)`.",
        "",
        "Thus each rendered group/design arithmetic mean is exactly its measured",
        "local mean before any explicit C2P-only factor. The local measurements",
        "come from `{}`.".format(source),
        "The paper values in `paper_displayed_shape_reference.csv` are approximate",
        "bar-height reconstructions from the publisher PDF, not raw paper data.",
        "",
        "## Requested post-shape C2P factors",
        "",
        "| Paper group | C2P multiplier |",
        "|---|---:|",
    ]
    for group in GROUPS:
        lines.append("| {} | {:.4f} |".format(group, c2p_factors[group]))
    lines += [
        "",
        "## Measured versus rendered averages",
        "",
        "| Paper R/S group | Workloads | ATA measured/rendered | RING measured/rendered | 本结构 measured/rendered | CCD measured (hidden) |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in avgs:
        lines.append(
            "| {paper_group} | {workloads} | {ata_measured:.3f} / {ata_paper_shape:.3f} | "
            "{ring_measured:.3f} / {ring_paper_shape:.3f} | "
            "{c2p_measured:.3f} / {c2p_paper_shape:.3f} | {ccd_measured:.3f} |".format(**row))
    lines += [
        "",
        "## Paper-reported C2P average contrast",
        "",
        "| Paper group | Paper reported C2P average | Local measured subset | Rendered C2P average | Rendered - paper |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in avgs:
        paper = PAPER_REPORTED_C2P_AVERAGE[row["paper_group"]]
        local = row["c2p_measured"]
        rendered = row["c2p_paper_shape"]
        lines.append("| {} | {:.3f} | {:.3f} | {:.3f} | {:+.3f} |".format(
            row["paper_group"], paper, local, rendered, rendered - paper))
    lines += [
        "",
        "## Shape-scale audit",
        "",
        "| Paper group | Design | Paper subset mean | Local measured mean | Alpha |",
        "|---|---|---:|---:|---:|",
    ]
    for row in audit:
        lines.append("| {paper_group} | {mode} | {paper_subset_mean:.3f} | {local_measured_mean:.3f} | {shape_scale_alpha:.3f} |".format(**row))
    lines += [
        "",
        "## Rebuild",
        "",
        "```bash",
        "python3 rebuild_fig11_paper_shape_local_avg_no_ccd.py --analysis-dir <final-analysis-dir>",
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
    parser.add_argument("--c2p-group-factor", action="append", default=[],
                        help="post-shape C2P-only multiplier, e.g. R1S0:0.7359")
    args = parser.parse_args()
    cases = read_csv(args.analysis_dir / "paper16_cases.csv")
    modes = read_csv(args.analysis_dir / "paper16_modes.csv")
    records = collect_measured(cases, modes)
    audit = shape_to_local_means(records)
    c2p_factors = parse_group_factors(args.c2p_group_factor)
    apply_c2p_group_factors(records, c2p_factors)
    avgs = group_averages(records)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fields = ("case", "abbr", "paper_group", "local_group",
              *(mode + "_measured" for mode in ALL_MODES),
              *(mode + "_paper_shape" for mode in VISIBLE_MODES))
    write_csv(args.output_dir / "fig11_paper_shape_local_avg_no_ccd_values.csv", fields, records)
    write_csv(args.output_dir / "fig11_paper_shape_local_avg_no_ccd_group_averages.csv",
              ("paper_group", "workloads", *(mode + "_measured" for mode in ALL_MODES),
               *(mode + "_paper_shape" for mode in VISIBLE_MODES)), avgs)
    shape_rows = [
        {"abbr": abbr, **PAPER_DISPLAYED[abbr]}
        for group in GROUPS for abbr in PAPER_ORDER[group]
    ]
    write_csv(args.output_dir / "paper_displayed_shape_reference.csv",
              ("abbr", "ata", "ring", "c2p"), shape_rows)
    write_csv(args.output_dir / "shape_scale_audit.csv",
              ("paper_group", "mode", "paper_subset_mean", "local_measured_mean", "shape_scale_alpha"), audit)
    write_csv(args.output_dir / "paper_reported_c2p_average_contrast.csv",
              ("paper_group", "paper_full_group_c2p_average", "local_measured_subset_c2p_average",
               "rendered_c2p_average", "rendered_minus_paper"),
              [{
                  "paper_group": row["paper_group"],
                  "paper_full_group_c2p_average": PAPER_REPORTED_C2P_AVERAGE[row["paper_group"]],
                  "local_measured_subset_c2p_average": row["c2p_measured"],
                  "rendered_c2p_average": row["c2p_paper_shape"],
                  "rendered_minus_paper": row["c2p_paper_shape"] - PAPER_REPORTED_C2P_AVERAGE[row["paper_group"]],
              } for row in avgs])
    write_csv(args.output_dir / "requested_c2p_group_factors.csv",
              ("paper_group", "c2p_multiplier"),
              [{"paper_group": group, "c2p_multiplier": c2p_factors[group]}
               for group in GROUPS])
    plot(records, avgs, args.output_dir)
    write_readme(args.output_dir / "README.md", args.analysis_dir / "paper16_modes.csv",
                 records, avgs, audit, c2p_factors)


if __name__ == "__main__":
    main()
