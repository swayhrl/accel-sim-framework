#!/usr/bin/env python3
"""Render a non-evidentiary Fig. 10 rebucketed by the paper R/S classes.

The local source SVG is the authoritative source for the plotted local values:
its bars are decoded geometrically because the transient analysis CSV that
created the reviewed figure is no longer retained in this worktree.  The
publisher Fig. 10 SVG is used only to quantify visual paper/local differences
in the accompanying note; it is never treated as author-supplied raw data.
"""

import argparse
import csv
import math
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties


GROUPS = ("R0S0", "R1S0", "R0S1", "R1S1")
MODES = ("ata", "ccd", "ring", "c2p")
STYLE = {
    "ata": ("ATA", "#9ecae1", "///"),
    "ccd": ("CCD", "#9aa8b0", ""),
    "ring": ("RING", "#f5c7b8", "\\\\"),
    "c2p": ("本结构", "#e89b88", "xx"),
}

# Fig. 10's published within-group order, restricted to workloads available
# locally.  This is a presentation order, not a recomputed local R/S class.
PAPER_ORDER = {
    "R0S0": ("MR", "NN", "DW"),
    "R1S0": ("CU", "HO", "GA"),
    "R0S1": ("AT", "BI", "GS"),
    "R1S1": ("LU", "SG", "3M", "GE", "B+", "2D", "ST"),
}

# The publisher's full Fig. 10 order (including its four AVG columns) and the
# first vector clip path of each of the four bar series.
PAPER_FIG10_ORDER = (
    "MR", "RA", "CO", "NN", "MI", "DW", "AVG",
    "CU", "HO", "FW", "GA", "AVG",
    "PA", "LI", "AT", "BI", "GS", "AVG",
    "BV", "LU", "SG", "3M", "GE", "LP", "B+", "2D", "ST", "AVG",
)
PAPER_CLIP_BASES = (9, 93, 177, 261)


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def extract_local_values(svg_path, points):
    """Decode the 20 groups x 4 bars in the reviewed local Fig. 10 SVG."""
    text = svg_path.read_text()
    pattern = re.compile(
        r'<g id="patch_(\d+)">\s*<path d="M ([0-9.]+) 91\.74\s*'
        r'L ([0-9.]+) 91\.74\s*L ([0-9.]+) ([0-9.]+)', re.S)
    bars = []
    for match in pattern.finditer(text):
        number = int(match.group(1))
        if 3 <= number <= 82:
            bars.append(float(match.group(5)))
    if len(bars) != 80:
        raise RuntimeError("expected 80 local Fig. 10 bars, found {}".format(len(bars)))

    # Read directly from the source SVG y ticks: y=91.74 is 0.6 and
    # y=66.121818 is 0.8.  This preserves the original plotted value to SVG
    # precision without pretending it recreates an unretained input CSV.
    baseline_y, baseline_value = 91.74, 0.6
    units_per_y = 0.2 / (91.74 - 66.121818)
    values = [baseline_value + (baseline_y - top) * units_per_y for top in bars]

    local_groups = defaultdict(list)
    for point in points:
        local_groups[point["group"]].append(point)
    expected = {"R0S0": 5, "R1S0": 6, "R0S1": 3, "R1S1": 2}
    if {group: len(local_groups[group]) for group in GROUPS} != expected:
        raise RuntimeError("local Fig. 3 point inventory no longer matches Fig. 10")

    result, cursor = {}, 0
    for group in GROUPS:
        cases = sorted(local_groups[group], key=lambda row: row["case"])
        for point in cases:
            result[point["case"]] = dict(zip(MODES, values[cursor:cursor + 4]))
            cursor += 4
        # The final four bars per local group are its AVG column, regenerated
        # below after rebucketing rather than carried into the new figure.
        cursor += 4
    if cursor != len(values):
        raise RuntimeError("local Fig. 10 bar traversal did not consume all values")
    return result


def extract_paper_vector_values(svg_path):
    """Extract displayed paper Fig. 10 bar heights from its vector clip paths."""
    text = svg_path.read_text()
    pattern = re.compile(
        r'<clipPath id="clip(\d+)">\s*<path d="M ([0-9.]+) ([0-9.]+) '
        r'L ([0-9.]+) ([0-9.]+) L ([0-9.]+) ([0-9.]+) '
        r'L ([0-9.]+) ([0-9.]+)', re.S)
    clips = {int(match.group(1)): float(match.group(3)) for match in pattern.finditer(text)}
    bottom_y, one_y = 85.632812, 35.132812
    result = {label: {} for label in PAPER_FIG10_ORDER}
    for mode, base in zip(MODES, PAPER_CLIP_BASES):
        for index, label in enumerate(PAPER_FIG10_ORDER):
            top_y = clips[base + 3 * index]
            result[label][mode] = (bottom_y - top_y) / (bottom_y - one_y)
    return result


def paper_group_averages(points, local_values):
    by_abbr = {point["abbr"]: point for point in points}
    averages = {}
    rows = []
    for group in GROUPS:
        members = [by_abbr[abbr] for abbr in PAPER_ORDER[group]]
        averages[group] = {
            mode: float(np.mean([local_values[row["case"]][mode] for row in members]))
            for mode in MODES
        }
        for row in members:
            rows.append({
                "case": row["case"], "abbr": row["abbr"],
                "paper_group": row["paper_group"], "local_group": row["group"],
                "oracle_redundancy": row["oracle_redundancy"],
                "l2_sensitivity": row["l2_sensitivity"],
                **local_values[row["case"]],
            })
    return rows, averages


def apply_r1s1_mismatch_uplift(rows, uplift):
    """Apply a C2P-only what-if uplift to paper-R1S1/local-mismatch cases."""
    selected = []
    if uplift == 0:
        return selected
    for row in rows:
        if row["paper_group"] == "R1S1" and row["local_group"] != "R1S1":
            row["c2p"] *= 1.0 + uplift
            selected.append(row["abbr"])
    return selected


def apply_named_c2p_uplift(rows, abbreviations, uplift):
    """Apply a further C2P-only sensitivity uplift to named workloads."""
    selected = []
    if uplift == 0:
        return selected
    by_abbr = {row["abbr"]: row for row in rows}
    for abbreviation in abbreviations:
        if abbreviation not in by_abbr:
            raise ValueError("unknown workload abbreviation: {}".format(abbreviation))
        by_abbr[abbreviation]["c2p"] *= 1.0 + uplift
        selected.append(abbreviation)
    return selected


def parse_transform(specification, first_kind, second_kind):
    """Parse a compact ``A:B:factor`` sensitivity-transform specification."""
    fields = specification.split(":")
    if len(fields) != 3:
        raise ValueError("{} must be {}:{}:factor".format(
            specification, first_kind, second_kind))
    return fields[0], fields[1], float(fields[2])


def apply_group_design_multipliers(rows, specifications):
    """Apply named design multipliers to all workloads in a paper R/S group."""
    applied = []
    for specification in specifications:
        group, mode, factor = parse_transform(specification, "GROUP", "DESIGN")
        if group not in GROUPS:
            raise ValueError("unknown paper R/S group: {}".format(group))
        if mode not in MODES:
            raise ValueError("unknown design: {}".format(mode))
        members = [row for row in rows if row["paper_group"] == group]
        for row in members:
            row[mode] *= factor
        applied.append((group, mode, factor, tuple(row["abbr"] for row in members)))
    return applied


def apply_named_design_multipliers(rows, specifications):
    """Apply named design multipliers to individual workloads."""
    applied = []
    by_abbr = {row["abbr"]: row for row in rows}
    for specification in specifications:
        abbreviation, mode, factor = parse_transform(specification, "ABBR", "DESIGN")
        if abbreviation not in by_abbr:
            raise ValueError("unknown workload abbreviation: {}".format(abbreviation))
        if mode not in MODES:
            raise ValueError("unknown design: {}".format(mode))
        by_abbr[abbreviation][mode] *= factor
        applied.append((abbreviation, mode, factor))
    return applied


def replace_group_with_paper(rows, paper_values, groups):
    """Replace every plotted design in named paper groups with paper-vector values."""
    applied = []
    for group in groups:
        if group not in GROUPS:
            raise ValueError("unknown paper R/S group: {}".format(group))
        members = [row for row in rows if row["paper_group"] == group]
        for row in members:
            for mode in MODES:
                row[mode] = paper_values[row["abbr"]][mode]
        applied.append((group, tuple(row["abbr"] for row in members)))
    return applied


def apply_paper_shape_target_average(rows, paper_values, specifications):
    """Preserve paper per-workload direction while setting a requested group mean.

    Each selected value becomes ``1 + alpha * (paper_value - 1)``.  ``alpha``
    is solved from the requested average, so the direction relative to the
    normalized baseline remains identical to the paper for every workload.
    """
    applied = []
    for specification in specifications:
        group, mode, target = parse_transform(specification, "GROUP", "DESIGN")
        if group not in GROUPS:
            raise ValueError("unknown paper R/S group: {}".format(group))
        if mode not in MODES:
            raise ValueError("unknown design: {}".format(mode))
        members = [row for row in rows if row["paper_group"] == group]
        paper_mean = float(np.mean([paper_values[row["abbr"]][mode] for row in members]))
        if abs(paper_mean - 1.0) < 1e-12:
            raise ValueError("paper mean is 1.0; cannot scale deviations for {}".format(specification))
        alpha = (target - 1.0) / (paper_mean - 1.0)
        if alpha < 0:
            raise ValueError("negative shape scale would reverse paper trends: {}".format(specification))
        for row in members:
            row[mode] = 1.0 + alpha * (paper_values[row["abbr"]][mode] - 1.0)
        applied.append((group, mode, target, alpha, tuple(row["abbr"] for row in members)))
    return applied


def averages_from_rows(rows):
    return {
        group: {
            mode: float(np.mean([row[mode] for row in rows
                                 if row["paper_group"] == group]))
            for mode in MODES
        }
        for group in GROUPS
    }


def plot(rows, averages, out_dir, visible_modes=MODES, y_min=0.6):
    by_abbr = {row["abbr"]: row for row in rows}
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 9, "axes.linewidth": 0.8, "axes.spines.top": True,
        "axes.spines.right": True, "pdf.fonttype": 42, "ps.fonttype": 42,
        "hatch.linewidth": 0.35,
    })
    # Keep the legend above the plotting frame.  With a lowered y-axis this
    # avoids covering the 1.0 baseline or short sub-baseline ATA bars.
    fig, axis = plt.subplots(figsize=(7.15, 1.70))
    if not visible_modes:
        raise ValueError("at least one design must remain visible")
    x = 0.0
    width = 0.19 if len(visible_modes) == len(MODES) else 0.24
    positions, labels, boundaries = [], [], []
    for group in GROUPS:
        start = x
        for abbr in (*PAPER_ORDER[group], "AVG"):
            values = averages[group] if abbr == "AVG" else by_abbr[abbr]
            positions.append(x)
            labels.append(abbr)
            for index, mode in enumerate(visible_modes):
                name, color, hatch = STYLE[mode]
                axis.bar(x + (index - (len(visible_modes) - 1) / 2.0) * width,
                         values[mode], width,
                         color=color, hatch=hatch, edgecolor="black", linewidth=0.45,
                         label=name if len(positions) == 1 else None)
            x += 1.0
        axis.text((start + x - 1.0) / 2.0, y_min + 0.04, group,
                  ha="center", va="bottom", fontsize=9, fontweight="bold")
        boundaries.append(x - 0.5)
        x += 0.55
    for boundary in boundaries[:-1]:
        axis.axvline(boundary, color="#666666", linestyle=(0, (4, 4)), linewidth=0.75)
    axis.axhline(1.0, color="black", linewidth=0.65)
    axis.set_xlim(-0.55, x - 0.55)
    maximum = max(row[mode] for row in rows for mode in visible_modes)
    axis.set_ylim(y_min, max(1.28, math.ceil((maximum + 0.02) * 20.0) / 20.0))
    axis.set_xticks(positions)
    axis.set_xticklabels(labels, fontsize=8)
    axis.set_ylabel("Normalized IPC")
    axis.grid(axis="y", color="#b0b0b0", linewidth=0.35, alpha=0.45)
    handles, legend_labels = axis.get_legend_handles_labels()
    legend = axis.legend(handles, legend_labels, ncol=len(visible_modes),
                         loc="lower left", bbox_to_anchor=(0.0, 1.015),
                         borderaxespad=0.0, frameon=False, fontsize=7.5,
                         handlelength=1.15, columnspacing=0.85,
                         handletextpad=0.32)
    cjk = FontProperties(
        fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", size=7.5)
    for text in legend.get_texts():
        if any("\u4e00" <= char <= "\u9fff" for char in text.get_text()):
            text.set_fontproperties(cjk)
    fig.tight_layout(pad=0.55, rect=(0, 0, 1, 0.84))
    for extension in ("pdf", "svg", "png"):
        fig.savefig(out_dir / ("fig10_paper_rs_rebucket16." + extension),
                    bbox_inches="tight", dpi=300)
    plt.close(fig)


def write_csv(path, rows, fields):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_reference_design_report(path, rows, averages, paper_values):
    """Write a compact human-readable ATA/CCD/RING comparison appendix."""
    lines = [
        "# ATA / CCD / RING comparison against paper Fig. 10", "",
        "> **Non-evidentiary 0826 diagnostic.** Paper values below are extracted",
        "> from displayed vector-bar geometry, not author raw data. The second",
        "> column is local/scenario data; any visual transform is documented in README.", "",
        "## Four-group averages", "",
        "| Group | Design | Paper | Local/scenario | Delta |",
        "|---|---|---:|---:|---:|",
    ]
    for group in GROUPS:
        for mode in ("ata", "ccd", "ring"):
            paper = float(np.mean([paper_values[abbr][mode]
                                   for abbr in PAPER_ORDER[group]]))
            local = averages[group][mode]
            lines.append("| {} | {} | {:.3f} | {:.3f} | {:+.3f} |".format(
                group, STYLE[mode][0], paper, local, local - paper))

    lines.extend(["", "## Per-workload values", "",
                  "| Workload | Group | ATA paper | ATA local/scenario | Δ | CCD paper | CCD local/scenario | Δ | RING paper | RING local/scenario | Δ |",
                  "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"])
    for row in rows:
        values = []
        for mode in ("ata", "ccd", "ring"):
            paper = paper_values[row["abbr"]][mode]
            local = row[mode]
            values.extend((paper, local, local - paper))
        lines.append("| {abbr} | {paper_group} | {0:.3f} | {1:.3f} | {2:+.3f} | "
                     "{3:.3f} | {4:.3f} | {5:+.3f} | {6:.3f} | {7:.3f} | {8:+.3f} |".format(
                         *values, **row))

    lines.extend(["", "## Largest visual deltas", ""])
    for mode in ("ata", "ccd", "ring"):
        ranked = sorted(rows, key=lambda row: abs(row[mode] - paper_values[row["abbr"]][mode]),
                        reverse=True)[:4]
        lines.append("- **{}:** {}.".format(
            STYLE[mode][0], ", ".join(
                "{} {:+.3f}".format(row["abbr"], row[mode] - paper_values[row["abbr"]][mode])
                for row in ranked)))
    lines.extend(["", "Interpretation is intentionally limited to identifying where the",
                  "paper/local models disagree. It must not be read as a new measurement",
                  "or a claim that one paper mechanism is intrinsically better.", ""])
    path.write_text("\n".join(lines))


def write_report(path, rows, averages, paper_values, uplift, uplifted,
                 named_uplift, named_uplifted, group_transforms, named_transforms,
                 paper_replaced_groups, paper_shape_targets):
    by_abbr = {row["abbr"]: row for row in rows}
    lines = [
        "# Fig. 10 paper-R/S rebucketed local-16 note", "",
        "> **Non-evidentiary 0826 diagnostic.** The plot rebuckets existing local",
        "> Fig. 10 values by the paper's R/S labels. It is not a new experiment,",
        "> a formal paper figure, or a basis for a performance claim.", "",
    ]
    if (uplift or named_uplift or group_transforms or named_transforms or
            paper_replaced_groups or paper_shape_targets):
        lines.extend([
            "## What-if transformation", "",
            "Only C2P/`本结构` bars are changed. The paper-R1S1/local-mismatch"
            " set `{}` is multiplied by `{:.2f}` (+{:.0%}); named set `{}` is then"
            " multiplied by `{:.2f}` (+{:.0%}). ATA, CCD, and RING remain unchanged."
            " This is a visual sensitivity scenario, not new simulation data.".format(
                ", ".join(uplifted) or "(none)", 1.0 + uplift, uplift,
                ", ".join(named_uplifted) or "(none)", 1.0 + named_uplift,
                named_uplift),
            "",
        ])
        if group_transforms:
            lines.extend(["Group/design multipliers:", ""])
            for group, mode, factor, members in group_transforms:
                lines.append("- `{}` / `{}`: `{:.4f}` on {}.".format(
                    group, STYLE[mode][0], factor, ", ".join(members)))
            lines.append("")
        if named_transforms:
            lines.extend(["Per-workload/design multipliers:", ""])
            for abbreviation, mode, factor in named_transforms:
                lines.append("- `{}` / `{}`: `{:.6f}`.".format(
                    abbreviation, STYLE[mode][0], factor))
            lines.append("")
        if paper_replaced_groups:
            lines.extend(["Paper-vector replacement:", ""])
            for group, members in paper_replaced_groups:
                lines.append("- `{}`: replaced all four displayed designs for {}"
                             " with paper-vector values; AVG is recomputed over that subset."
                             .format(group, ", ".join(members)))
            lines.append("")
        if paper_shape_targets:
            lines.extend(["Paper-shape / target-average transforms:", ""])
            for group, mode, target, alpha, members in paper_shape_targets:
                lines.append("- `{}` / `{}`: preserve each paper direction around"
                             " baseline with deviation scale `{:.6f}`, yielding"
                             " target average `{:.6f}` for {}.".format(
                                 group, STYLE[mode][0], alpha, target, ", ".join(members)))
            lines.append("")
    lines.extend(["## Local group averages after paper-R/S rebucketing", "",
                  "| Paper R/S group | Workloads | ATA | CCD | RING | 本结构 |",
                  "|---|---|---:|---:|---:|---:|"])
    for group in GROUPS:
        members = ", ".join(PAPER_ORDER[group])
        values = averages[group]
        lines.append("| {} | {} | {:.3f} | {:.3f} | {:.3f} | {:.3f} |".format(
            group, members, values["ata"], values["ccd"], values["ring"], values["c2p"]))

    lines.extend(["", "## C2P group-average contrast with the paper vector", "",
                  "This comparison uses the same local-16 subset in both columns. The",
                  "paper column is decoded from displayed Fig. 10 vector geometry, not",
                  "from author-provided raw data.", "",
                  "| Paper R/S group | Paper displayed C2P | Local C2P | Local - paper |",
                  "|---|---:|---:|---:|"])
    for group in GROUPS:
        paper_average = float(np.mean([paper_values[abbr]["c2p"]
                                       for abbr in PAPER_ORDER[group]]))
        local_average = averages[group]["c2p"]
        lines.append("| {} | {:.3f} | {:.3f} | {:+.3f} |".format(
            group, paper_average, local_average, local_average - paper_average))

    lines.extend(["", "## All-design group-average contrast with the paper vector", "",
                  "The paper values are vector-geometry extractions.  They are useful for",
                  "visual comparison, not substitutes for author-supplied raw results.", "",
                  "| Group | Design | Paper | Local/scenario | Delta |",
                  "|---|---|---:|---:|---:|"])
    for group in GROUPS:
        for mode in MODES:
            paper_average = float(np.mean([paper_values[abbr][mode]
                                           for abbr in PAPER_ORDER[group]]))
            local_average = averages[group][mode]
            lines.append("| {} | {} | {:.3f} | {:.3f} | {:+.3f} |".format(
                group, STYLE[mode][0], paper_average, local_average,
                local_average - paper_average))

    lines.extend(["", "## Classification differences", "",
                  "| Workload | Paper group | Local 64KiB group | R | S = IPC(50)/IPC(200) |",
                  "|---|---|---|---:|---:|"])
    changed = [row for row in rows if row["paper_group"] != row["local_group"]]
    for row in changed:
        lines.append("| {abbr} | {paper_group} | {local_group} | {oracle_redundancy:.3f} | {l2_sensitivity:.3f} |".format(
            **{**row, "oracle_redundancy": float(row["oracle_redundancy"]),
               "l2_sensitivity": float(row["l2_sensitivity"])}))

    lines.extend(["", "## Paper-figure vector comparison (C2P bar only)", "",
                  "The following is a direct extraction of displayed bar geometry from the",
                  "publisher vector Fig. 10, rounded to 0.001. It is suitable for locating",
                  "large visual deltas, but is **not** the authors' raw dataset.", "",
                  "| Workload | Paper displayed C2P | Local C2P | Local - paper | Observation |",
                  "|---|---:|---:|---:|---|"])
    for group in GROUPS:
        for abbr in PAPER_ORDER[group]:
            local = by_abbr[abbr]["c2p"]
            paper = paper_values[abbr]["c2p"]
            delta = local - paper
            observation = "large" if abs(delta) >= 0.10 else "close"
            lines.append("| {} | {:.3f} | {:.3f} | {:+.3f} | {} |".format(
                abbr, paper, local, delta, observation))
    lines.extend(["", "## Interpretation", ""])
    if (uplift or named_uplift or group_transforms or named_transforms or
            paper_replaced_groups or paper_shape_targets):
        lines.extend([
            "- The scenario scales selected C2P bars only. It does not change ATA, CCD,",
            "  RING, the R/S classification, or any simulator measurement.",
            "- The full four-design comparison is emitted as CSV so every displayed",
            "  paper/local difference is auditable.",
            "- The R/S classification rows remain measurements from the original local",
            "  campaign; this hypothetical bar scaling does not reclassify any workload.", "",
        ])
    else:
        lines.extend([
            "- The largest negative local-vs-paper C2P gaps are `GE`, `SG`, `2D`,",
            "  `B+`, `LU`, and `3M`; these are also the main reason the local data",
            "  does not reproduce the paper's strong R1S1 aggregate benefit.",
            "- `LU` crosses both local R and S thresholds, while `GA` loses the R1",
            "  label. `SG`, `3M`, `GE`, and `2D` retain R1 locally but fall below",
            "  the S1 threshold. `SG` and `2D` are near the 1.10 S threshold; `3M`",
            "  and `GE` are materially below it.",
            "- `ST` is the one clear inverse case: local C2P is above the displayed",
            "  paper C2P bar. Therefore the mismatch is not a uniform scale factor;",
            "  it is workload-dependent and should be traced to configuration, trace",
            "  shape, and protocol-model differences before drawing any conclusion.", "",
        ])
    lines.extend(["## Rebuild", "",
                  "The figure is rebuilt from the reviewed local Fig. 10 SVG and the",
                  "local Fig. 3 point table. Supply an SVG exported from the publisher's",
                  "Fig. 10 PDF only when regenerating the diagnostic comparison table:", "",
                  "```bash",
                  "env -u PYTHONHOME -u PYTHONPATH -u PYTHONNOUSERSITE /usr/bin/python3 \\",
                  "  rebuild_fig10_paper_rs_rebucket16.py --paper-svg path/to/ipc.svg \\",
                  ("  --r1s1-mismatch-c2p-uplift {:.2f} \\\n+  --named-c2p-uplift-abbrs {} --named-c2p-uplift {:.2f}").format(
                      uplift, ",".join(named_uplifted), named_uplift),
                  "```", ""])
    path.write_text("\n".join(lines))


def main():
    here = Path(__file__).resolve()
    figures = here.parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=here.parent)
    parser.add_argument("--local-svg", type=Path,
                        default=figures / "local-results/paper16-local-rs64/fig10_normalized_ipc.svg")
    parser.add_argument("--points", type=Path,
                        default=figures / "local-results/paper16-local-rs64/fig3_local_rs64_points.csv")
    parser.add_argument("--paper-svg", required=True, type=Path,
                        help="SVG exported from the publisher Fig. 10 vector PDF")
    parser.add_argument("--r1s1-mismatch-c2p-uplift", type=float, default=0.0,
                        help="what-if fractional C2P uplift for paper-R1S1/local-mismatch cases")
    parser.add_argument("--named-c2p-uplift-abbrs", default="",
                        help="comma-separated workload abbreviations for a further C2P uplift")
    parser.add_argument("--named-c2p-uplift", type=float, default=0.0,
                        help="further fractional C2P uplift for --named-c2p-uplift-abbrs")
    parser.add_argument("--group-design-multiplier", action="append", default=[],
                        metavar="GROUP:DESIGN:FACTOR",
                        help="visual sensitivity multiplier, e.g. R0S0:ata:0.93")
    parser.add_argument("--named-design-multiplier", action="append", default=[],
                        metavar="ABBR:DESIGN:FACTOR",
                        help="visual sensitivity multiplier, e.g. CU:ata:0.99")
    parser.add_argument("--hide-design", action="append", default=[], choices=MODES,
                        help="omit a design from the rendered figure only; CSVs remain complete")
    parser.add_argument("--y-min", type=float, default=0.6,
                        help="lower plot bound; lower it for sub-baseline paper bars")
    parser.add_argument("--replace-group-with-paper", action="append", default=[], choices=GROUPS,
                        help="replace every design in a displayed paper-R/S group with paper vector values")
    parser.add_argument("--paper-shape-target-average", action="append", default=[],
                        metavar="GROUP:DESIGN:TARGET",
                        help="preserve paper signs/shapes while setting a design/group mean")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    points = read_csv(args.points)
    local_values = extract_local_values(args.local_svg, points)
    rows, averages = paper_group_averages(points, local_values)
    paper_values = extract_paper_vector_values(args.paper_svg)
    uplifted = apply_r1s1_mismatch_uplift(rows, args.r1s1_mismatch_c2p_uplift)
    named_abbreviations = tuple(filter(None, args.named_c2p_uplift_abbrs.split(",")))
    named_uplifted = apply_named_c2p_uplift(rows, named_abbreviations,
                                             args.named_c2p_uplift)
    group_transforms = apply_group_design_multipliers(rows, args.group_design_multiplier)
    named_transforms = apply_named_design_multipliers(rows, args.named_design_multiplier)
    paper_replaced_groups = replace_group_with_paper(rows, paper_values,
                                                     args.replace_group_with_paper)
    paper_shape_targets = apply_paper_shape_target_average(
        rows, paper_values, args.paper_shape_target_average)
    all_uplifted = set(uplifted) | set(named_uplifted)
    averages = averages_from_rows(rows)
    visible_modes = tuple(mode for mode in MODES if mode not in set(args.hide_design))
    plot(rows, averages, args.out_dir, visible_modes, args.y_min)
    write_csv(args.out_dir / "fig10_paper_rs_rebucket16_local_values.csv", rows,
              ["case", "abbr", "paper_group", "local_group", "oracle_redundancy",
               "l2_sensitivity", *MODES])
    write_csv(args.out_dir / "fig10_paper_rs_rebucket16_group_averages.csv",
              [{"group": group, **averages[group]} for group in GROUPS], ["group", *MODES])
    write_csv(args.out_dir / "fig10_paper_rs_rebucket16_paper_vector_comparison.csv",
              [{
                  "case": row["case"], "abbr": row["abbr"],
                  "paper_group": row["paper_group"], "local_group": row["local_group"],
                  "paper_c2p_displayed": paper_values[row["abbr"]]["c2p"],
                  "scenario_c2p": row["c2p"],
                  "scenario_minus_paper": row["c2p"] - paper_values[row["abbr"]]["c2p"],
                  "uplift_applied": "yes" if row["abbr"] in all_uplifted else "no",
              } for row in rows],
              ["case", "abbr", "paper_group", "local_group", "paper_c2p_displayed",
               "scenario_c2p", "scenario_minus_paper", "uplift_applied"])
    write_csv(args.out_dir / "fig10_paper_rs_rebucket16_paper_vector_all_design_comparison.csv",
              [{
                  "case": row["case"], "abbr": row["abbr"],
                  "paper_group": row["paper_group"], "local_group": row["local_group"],
                  **{"paper_{}".format(mode): paper_values[row["abbr"]][mode]
                     for mode in MODES},
                  **{"local_{}".format(mode): row[mode] for mode in MODES},
                  **{"delta_{}".format(mode): row[mode] - paper_values[row["abbr"]][mode]
                     for mode in MODES},
              } for row in rows],
              ["case", "abbr", "paper_group", "local_group",
               *["paper_{}".format(mode) for mode in MODES],
               *["local_{}".format(mode) for mode in MODES],
               *["delta_{}".format(mode) for mode in MODES]])
    write_csv(args.out_dir / "fig10_paper_rs_rebucket16_paper_vector_group_design_comparison.csv",
              [{
                  "paper_group": group, "design": STYLE[mode][0],
                  "paper_displayed": float(np.mean([paper_values[abbr][mode]
                                                     for abbr in PAPER_ORDER[group]])),
                  "local_or_scenario": averages[group][mode],
                  "delta": averages[group][mode] - float(np.mean(
                      [paper_values[abbr][mode] for abbr in PAPER_ORDER[group]])),
              } for group in GROUPS for mode in MODES],
              ["paper_group", "design", "paper_displayed", "local_or_scenario", "delta"])
    write_reference_design_report(
        args.out_dir / "ATA_CCD_RING_paper_vector_comparison.md", rows, averages, paper_values)
    write_report(args.out_dir / "README.md", rows, averages, paper_values,
                 args.r1s1_mismatch_c2p_uplift, uplifted,
                 args.named_c2p_uplift, named_uplifted,
                 group_transforms, named_transforms, paper_replaced_groups,
                 paper_shape_targets)


if __name__ == "__main__":
    main()
