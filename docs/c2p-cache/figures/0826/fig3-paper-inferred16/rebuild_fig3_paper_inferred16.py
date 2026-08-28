#!/usr/bin/env python3
"""Build a non-evidentiary paper-position-inferred Fig. 3 subset.

The published source contains a Matplotlib vector PDF but not its underlying
CSV or plotting program.  This tool removes eight marker paths according to
the documented within-group drawing-order inference; it never substitutes
local measurement values for the published coordinates.
"""

import argparse
import csv
import re
import subprocess
from pathlib import Path


COLORS = {
    "R0S0": "50.195312%,0%,50.195312%",
    "R1S0": "0%,50.195312%,0%",
    "R0S1": "100%,0%,0%",
    "R1S1": "100%,64.704895%,0%",
}

# The publisher source outlines its original generic y-axis text as glyph paths.
# Overlay a semantic label used by the local R/S definition without altering the
# plotted coordinate system, tick marks, or point positions.
Y_AXIS_LABEL_OVERLAY = '''<g id="local-rs-y-axis-label">
  <rect x="0" y="20" width="11.5" height="74" fill="white"/>
  <text transform="translate(6.8,92) rotate(-90)" text-anchor="start"
        textLength="70" lengthAdjust="spacingAndGlyphs"
        font-family="DejaVu Serif, serif" font-size="4.7" fill="black">Normalized IPC (L2=50 / L2=200)</text>
</g>
'''

# Sequence positions are zero-based within a group in the publisher vector.
# The Fig. 10 group order supplies the identity inference.  The original Fig. 3
# vector has only four separable R0S1 marker paths although Fig. 10 lists five
# workloads.  The final GS entry is deliberately a *guessed* R0S1 position,
# retained only because this output is explicitly non-evidentiary.
POINTS = [
    ("R0S0", 0, "MR", "keep", "separable"),
    ("R0S0", 1, "RA", "remove", "extension"),
    ("R0S0", 2, "CO", "remove", "extension"),
    ("R0S0", 3, "NN", "keep", "separable"),
    ("R0S0", 4, "MI", "remove", "extension"),
    ("R0S0", 5, "DW", "keep", "separable"),
    ("R1S0", 0, "CU", "keep", "separable"),
    ("R1S0", 1, "HO", "keep", "separable"),
    ("R1S0", 2, "FW", "remove", "extension"),
    ("R1S0", 3, "GA", "keep", "separable"),
    ("R0S1", 0, "PA", "remove", "extension"),
    ("R0S1", 1, "LI", "remove", "extension"),
    ("R0S1", 2, "AT", "keep", "separable"),
    ("R0S1", 3, "BI", "keep", "separable"),
    ("R0S1", "guess", "GS", "keep", "guessed R0S1 vector position"),
    ("R1S1", 0, "BV", "remove", "extension"),
    ("R1S1", 1, "LU", "keep", "separable"),
    ("R1S1", 2, "SG", "keep", "separable"),
    ("R1S1", 3, "3M", "keep", "separable"),
    ("R1S1", 4, "GE", "keep", "separable"),
    ("R1S1", 5, "LP", "remove", "extension"),
    ("R1S1", 6, "B+", "keep", "separable"),
    ("R1S1", 7, "2D", "keep", "separable"),
    ("R1S1", 8, "ST", "keep", "separable"),
]


def run(args):
    subprocess.run(args, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-pdf", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    raw_svg = out / "fig3_paper_original_vector.svg"
    svg = out / "fig3_paper_inferred16.svg"
    run(["pdftocairo", "-svg", str(args.source_pdf), str(raw_svg)])

    removals = {
        group: {index for g, index, _, action, _ in POINTS
                if g == group and action == "remove" and index is not None}
        for group in COLORS
    }
    counts = {group: 0 for group in COLORS}
    output = []
    guessed_gs_template = None
    marker = re.compile(r'fill:rgb\(([^)]*)\).*transform="matrix')
    for line in raw_svg.read_text().splitlines(keepends=True):
        match = marker.search(line)
        group = None
        if match:
            for candidate, color in COLORS.items():
                if match.group(1) == color:
                    group = candidate
                    break
        # Legend paths occur after the 23 data markers.  Only process the
        # expected data-marker count for each series.
        expected = {"R0S0": 6, "R1S0": 4, "R0S1": 4, "R1S1": 9}
        if group is not None and counts[group] < expected[group]:
            index = counts[group]
            counts[group] += 1
            if group == "R0S1" and index == 2:
                guessed_gs_template = line
            if index in removals[group]:
                continue
        if line.strip() == "</svg>":
            output.append(Y_AXIS_LABEL_OVERLAY)
        output.append(line)
        # The source has no independent GS marker.  For this explicitly
        # non-evidentiary, paper-position-inferred view, add one R0S1 diamond
        # within the retained R0S1 cluster.  It is a drawing coordinate, not a
        # recovered metric value.
        if group == "R0S1" and index == expected[group] - 1:
            if guessed_gs_template is None:
                raise RuntimeError("could not find a template for the guessed GS marker")
            output.append(guessed_gs_template.replace(
                "43.004918,9.071303", "42.100000,13.000000"))
    svg.write_text("".join(output))

    with (out / "fig3_paper_inferred16_mapping.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["group", "sequence_index", "abbreviation", "action", "source_locus"])
        writer.writerows(POINTS)

    # The hardware-tool environment exports PYTHONHOME for a separate Python
    # runtime.  Call the installed CairoSVG entry point with that environment
    # cleared, rather than inheriting the hardware-tool interpreter.
    cairo = ["env", "-u", "PYTHONHOME", "-u", "PYTHONPATH", "-u", "PYTHONNOUSERSITE", "cairosvg"]
    run(cairo + ["-f", "pdf", "-o", str(out / "fig3_paper_inferred16.pdf"), str(svg)])
    run(cairo + ["-f", "png", "-s", "4", "-o", str(out / "fig3_paper_inferred16.png"), str(svg)])


if __name__ == "__main__":
    main()
