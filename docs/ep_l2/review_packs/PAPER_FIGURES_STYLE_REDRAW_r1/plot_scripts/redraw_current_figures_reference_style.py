#!/usr/bin/env python3
"""Style-only redraw from the current frozen quicklook plotting tables.

The layout conventions are adapted from PAPER_FIGURES_DRAFT_v5's
plot_blocking_composition_reference_style.py.  This script neither launches a
simulator nor reads/rewrites a scientific result CSV.
"""
from __future__ import annotations

import csv
import hashlib
from html import escape
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT.parents[0] / "UTILIZATION_QUICKLOOK_r1"
UTIL_SOURCE = CURRENT / "plotting_tables" / "A1_A2_utilization_hotspot_table.csv"
BLOCK_SOURCE = CURRENT / "plotting_tables" / "B_blocking_wbuf8_subset.csv"
REFERENCE_SCRIPT = Path("/workspace/worktrees/accel-sim-ep-l2-streaming-reuse/docs/ep_l2/review_packs/PAPER_FIGURES_DRAFT_v5/plot_scripts/plot_blocking_composition_reference_style.py")
OUT = ROOT / "figures"
TABLES = ROOT / "plotting_tables"
WORKLOADS = ["dwt2d", "convolutionSeparable", "spmv", "scan", "FWT_7_21", "cfd_097k", "btree"]
UTILS = ["Set-reservation", "MSHR-entry", "MissQ", "WB-path proxy (WAD)"]
UTIL_COLORS = ["#285394", "#f1ead0", "#a61c4c", "#6e9d5b"]
BLOCKERS = ["SET_ASSOC", "MSHR_META", "MISSQ_LOWER", "WB_PATH", "OTHER"]
BLOCK_COLORS = ["#285394", "#f1ead0", "#a61c4c", "#6e9d5b", "#8a8a8a"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for data in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(data)
    return digest.hexdigest()


class PaperCanvas:
    """Minimal, dependency-free renderer producing raster PNG and editable SVG."""
    def __init__(self, width=1480, height=720):
        self.width, self.height = width, height
        self.image = Image.new("RGB", (width, height), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        self.small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        self.title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                    '<rect width="100%" height="100%" fill="white"/>']

    @staticmethod
    def rgb(color):
        color = color.lstrip("#")
        return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

    def rect(self, x0, y0, x1, y1, fill, stroke="#333333", sw=1):
        self.draw.rectangle((round(x0), round(y0), round(x1), round(y1)), fill=self.rgb(fill), outline=self.rgb(stroke) if stroke else None, width=sw)
        s = f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1-x0:.2f}" height="{y1-y0:.2f}" fill="{fill}"'
        self.svg.append(s + (f' stroke="{stroke}" stroke-width="{sw}"/>' if stroke else '/>'))

    def line(self, x0, y0, x1, y1, color="#000000", sw=1, dashed=False):
        if dashed and (x0 == x1 or y0 == y1):
            length = int(abs((x1-x0) + (y1-y0))); sign = 1 if (x1 > x0 or y1 > y0) else -1
            for start in range(0, length, 11):
                end = min(start + 6, length)
                if y0 == y1:
                    self.draw.line((x0+sign*start, y0, x0+sign*end, y0), fill=self.rgb(color), width=sw)
                else:
                    self.draw.line((x0, y0+sign*start, x0, y0+sign*end), fill=self.rgb(color), width=sw)
        else:
            self.draw.line((x0, y0, x1, y1), fill=self.rgb(color), width=sw)
        dash = ' stroke-dasharray="6,5"' if dashed else ""
        self.svg.append(f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" stroke="{color}" stroke-width="{sw}"{dash}/>')

    def text(self, x, y, value, kind="font", anchor="start", rotate=None):
        font = getattr(self, kind)
        bb = self.draw.textbbox((0, 0), value, font=font)
        w, h = bb[2]-bb[0], bb[3]-bb[1]
        if rotate is None:
            px = x - (w/2 if anchor == "middle" else w if anchor == "end" else 0)
            self.draw.text((round(px), round(y-h/2)), value, font=font, fill="black")
        else:
            tile = Image.new("RGBA", (w+10, h+10), (255, 255, 255, 0))
            ImageDraw.Draw(tile).text((5, 5), value, font=font, fill=(0, 0, 0, 255))
            tile = tile.rotate(rotate, expand=True, resample=Image.Resampling.BICUBIC)
            self.image.paste(tile, (round(x-tile.width/2), round(y-tile.height/2)), tile)
        sizes = {"font": 16, "small": 14, "title": 20}
        tf = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
        self.svg.append(f'<text x="{x:.2f}" y="{y+sizes[kind]*.34:.2f}" text-anchor="{anchor}" font-family="DejaVu Sans, sans-serif" font-size="{sizes[kind]}"{tf}>{escape(value)}</text>')

    def legend(self, names, colors, x=148, y=36, step=235):
        for i, (name, color) in enumerate(zip(names, colors)):
            px = x + i*step
            self.rect(px, y, px+18, y+18, color, "#333333")
            self.text(px+25, y+9, name, "small")

    def finish(self, filename):
        self.svg.append("</svg>")
        self.image.save(OUT / f"{filename}.png")
        (OUT / f"{filename}.svg").write_text("\n".join(self.svg) + "\n")


def axes(c, x0, y0, width, height, ymax, ylabel, ticks):
    c.rect(x0, y0-height, x0+width, y0, "#ffffff", "#000000", 2)
    for tick in ticks:
        y = y0-height*tick/ymax
        c.line(x0, y, x0+width, y, "#999999", 1, dashed=True)
        c.text(x0-17, y, f"{tick:g}", "small", anchor="end")
    c.text(34, y0-height/2, ylabel, "font", anchor="middle", rotate=-90)


def draw_utilization(rows):
    values = {(r["workload"], r["resource"]): float(r["utilization_percent"]) for r in rows}
    c = PaperCanvas(); x0, y0, pw, ph = 140, 565, 1240, 390
    c.text(740, 22, "Figure 1S. L2 resource occupancy / pressure proxy", "title", anchor="middle")
    c.legend(UTILS, UTIL_COLORS, step=290)
    axes(c, x0, y0, pw, ph, 100, "Hotspot-slice occupancy / pressure proxy (%)", range(0, 101, 20))
    step = pw/len(WORKLOADS); barw = 43
    for wi, workload in enumerate(WORKLOADS):
        center = x0+step*(wi+.5)
        for mi, (metric, color) in enumerate(zip(UTILS, UTIL_COLORS)):
            value = values[(workload, metric)]
            left = center+(mi-1.5)*barw
            top = y0-ph*value/100
            c.rect(left-barw/2, top, left+barw/2, y0, color, "#222222")
        c.text(center, y0+29, workload, "small", anchor="middle", rotate=18)
        if wi and wi % 2 == 0:
            sep = x0+step*wi
            c.line(sep, y0-ph, sep, y0+58, "#777777", 1, dashed=True)
    c.text(x0+pw/2, y0+102, "Selected exact workload set (no name-inferred archetype labels)", "font", anchor="middle")
    c.finish("FIG1S_L2_UTILIZATION_REFERENCE_STYLE_DRAFT")


def draw_blocking(rows):
    c = PaperCanvas(); x0, y0, pw, ph = 140, 565, 1240, 390
    rates = [float(r["overall_blocking_rate_percent"]) for r in rows]
    ymax = 80
    c.text(740, 22, "Figure 2. L2 structural blocking breakdown (WBUF=8 reference)", "title", anchor="middle")
    c.legend(BLOCKERS, BLOCK_COLORS, step=232)
    axes(c, x0, y0, pw, ph, ymax, "Share of eligible demand-miss admission cycles (%)", range(0, ymax+1, 20))
    step = pw/len(WORKLOADS); barw = 78
    for wi, row in enumerate(rows):
        center = x0+step*(wi+.5); denom = int(row["eligible_miss_admission_cycles"]); bottom = 0.0
        for name, color in zip(BLOCKERS, BLOCK_COLORS):
            value = 100.0*int(row[name])/denom
            yb = y0-ph*bottom/ymax; yt = y0-ph*(bottom+value)/ymax
            c.rect(center-barw/2, yt, center+barw/2, yb, color, "#222222")
            bottom += value
        c.text(center, y0-ph*bottom/ymax-15, f"{bottom:.1f}%", "small", anchor="middle")
        c.text(center, y0+29, row["workload"], "small", anchor="middle", rotate=18)
        if wi and wi % 2 == 0:
            sep = x0+step*wi
            c.line(sep, y0-ph, sep, y0+58, "#777777", 1, dashed=True)
    c.text(x0+pw/2, y0+102, "Selected exact workload set (all stack heights retain the reviewed overall blocking rate)", "font", anchor="middle")
    c.finish("FIG2_L2_STRUCTURAL_BLOCKING_REFERENCE_STYLE_DRAFT")


def write_csv(path, rows, fields):
    with path.open("w", newline="") as f:
        out = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        out.writeheader(); out.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True); TABLES.mkdir(parents=True, exist_ok=True)
    util = list(csv.DictReader(UTIL_SOURCE.open()))
    block = list(csv.DictReader(BLOCK_SOURCE.open()))
    if [r["workload"] for r in block] != WORKLOADS or {r["workload"] for r in util} != set(WORKLOADS):
        raise RuntimeError("current reviewed workload set mismatch")
    if len(util) != len(WORKLOADS)*len(UTILS):
        raise RuntimeError("current utilization table is incomplete")
    for row in block:
        if sum(int(row[x]) for x in BLOCKERS) != int(row["projected_blocked_miss_admission_cycles"]):
            raise RuntimeError(f"blocking closure failed for {row['workload']}")
    write_csv(TABLES / "FIG1S_L2_UTILIZATION_REFERENCE_STYLE_DRAFT.csv", util, list(util[0]))
    write_csv(TABLES / "FIG2_L2_STRUCTURAL_BLOCKING_REFERENCE_STYLE_DRAFT.csv", block, list(block[0]))
    write_csv(TABLES / "source_table_sha256.csv", [
        {"artifact": "current utilization plotting table", "path": str(UTIL_SOURCE), "sha256": sha256(UTIL_SOURCE)},
        {"artifact": "current blocking plotting table", "path": str(BLOCK_SOURCE), "sha256": sha256(BLOCK_SOURCE)},
        {"artifact": "reference-style plotting script studied", "path": str(REFERENCE_SCRIPT), "sha256": sha256(REFERENCE_SCRIPT)},
    ], ["artifact", "path", "sha256"])
    draw_utilization(util); draw_blocking(block)


if __name__ == "__main__":
    main()
