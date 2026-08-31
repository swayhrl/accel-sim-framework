#!/usr/bin/env python3
"""Generate the figure-only EP-L2 utilization quicklook from frozen CSVs.

This program deliberately reads no simulator source log and launches no workload.
It fails closed on the prescribed workload order and on paired B0/Motivation
provenance, then writes the exact plotting tables before rendering the figures.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from html import escape
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PACK = Path(__file__).resolve().parents[1]
RESULTS = Path("/workspace/results/ep_l2_streaming_reuse")
TABLES = PACK / "plotting_tables"
FIGURES = PACK / "figures"

# Ordered exactly as requested for the quicklook; no benchmark-name inference.
WORKLOADS = [
    ("dwt2d", RESULTS / "formal_original_dwt2d_r1/dwt2d/on"),
    ("convolutionSeparable", RESULTS / "preflight_convolution_r4/convolutionSeparable/on"),
    ("spmv", RESULTS / "formal_original_spmv_r1/spmv/on"),
    ("scan", RESULTS / "formal_original_scan_r1/scan/on"),
    ("FWT_7_21", RESULTS / "formal_original_FWT_7_21_r1/FWT_7_21/on"),
    ("cfd_097k", RESULTS / "formal_original_cfd_097k_r1/cfd_097k/on"),
    ("btree", RESULTS / "formal_original_btree_r1/btree/on"),
]

# These are per-slice occupancy resources in this frozen B0 configuration.
# P95 is preferred where emitted.  MissQ emits AVG/MAX only, so AVG is used.
RESOURCES = [
    ("Set-reservation", "c7d_reserved_p95", "c7d_reserved_avg", 128,
     "P95", "reserved entries / slice (C7D reservation pressure)"),
    ("MSHR-entry", "line_mshr_p95", "line_mshr_avg", 128,
     "P95", "line-MSHR entries / slice"),
    ("MissQ", None, "missq_avg", 128,
     "AVG", "MissQ entries / slice; no P95 field emitted"),
    ("WB-path proxy (WAD)", "wad_p95", "wad_avg", 128,
     "P95", "live WAD entries / slice; proxy for the broader WB path, not a physical baseline WBUF"),
]

BLOCKERS = [
    ("SET_ASSOC", "set_assoc", "#4C78A8"),
    ("MSHR_META", "mshr_meta", "#F2CF5B"),
    ("MISSQ_LOWER", "missq_lower", "#59A14F"),
    ("WB_PATH", "wb_path", "#B279A2"),
    ("OTHER", "other", "#9C9C9C"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], names: list[str]) -> None:
    with path.open("w", newline="") as f:
        out = csv.DictWriter(f, fieldnames=names, lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def parse_and_validate() -> tuple[list[dict], list[dict], list[dict]]:
    util_rows, blocking_rows, source_rows = [], [], []
    expected = [w for w, _ in WORKLOADS]
    observed = []
    common_core = common_framework = None
    for workload, root in WORKLOADS:
        b0 = root / "b0"
        mot = root / "motivation"
        slice_csv = b0 / "target_slice.csv"
        block_csv = mot / "blocking_breakdown.csv"
        b0_manifest = json.loads((b0 / "manifest.json").read_text())
        mot_manifest = json.loads((mot / "manifest.json").read_text())
        required = [slice_csv, block_csv]
        if not all(p.is_file() for p in required):
            raise RuntimeError(f"missing frozen CSV for {workload}: {required}")
        if b0_manifest["schema_version"] != "EPL2B0V1" or mot_manifest["schema_version"] != "EPL2MOTV1":
            raise RuntimeError(f"schema mismatch for {workload}")
        for key in ("core_commit", "framework_commit", "source_log_sha256"):
            if b0_manifest[key] != mot_manifest[key]:
                raise RuntimeError(f"unpaired B0/Motivation provenance for {workload}: {key}")
        if common_core is None:
            common_core, common_framework = b0_manifest["core_commit"], b0_manifest["framework_commit"]
        if (b0_manifest["core_commit"], b0_manifest["framework_commit"]) != (common_core, common_framework):
            raise RuntimeError(f"cross-workload runtime provenance mismatch for {workload}")
        rows = read_csv(slice_csv)
        if len(rows) != 64 or {r["scope"] for r in rows} != {"application"}:
            raise RuntimeError(f"expected 64 application slice rows for {workload}")
        observed.append(workload)
        for label, p95_field, avg_field, capacity, preferred, meaning in RESOURCES:
            source_field = p95_field if p95_field and p95_field in rows[0] else avg_field
            stat = preferred if source_field == p95_field else "AVG"
            if source_field not in rows[0]:
                raise RuntimeError(f"missing {source_field} in {slice_csv}")
            raw = max(int(r[source_field]) for r in rows)  # hotspot / worst slice
            util_rows.append({
                "workload": workload, "resource": label, "aggregation": "max across 64 application slices",
                "source_field": source_field, "selected_stat": stat, "raw_entries": raw,
                "capacity_entries": capacity, "utilization_percent": f"{100.0 * raw / capacity:.6f}",
                "semantic_mapping": meaning,
            })
        b = [r for r in read_csv(block_csv) if r["wbuf_capacity"] == "8"]
        if len(b) != 1 or b[0]["workload"] != workload:
            raise RuntimeError(f"expected exactly one WBUF=8 blocker row for {workload}")
        row = b[0]
        eligible = int(row["eligible_miss_admission_cycles"])
        values = {name: int(row[field]) for name, field, _ in BLOCKERS}
        total = sum(values.values())
        if total != int(row["projected_blocked_miss_admission_cycles"]):
            raise RuntimeError(f"blocker closure failure for {workload}")
        blocking_rows.append({
            "workload": workload, "eligible_miss_admission_cycles": eligible,
            **{name: values[name] for name, _, _ in BLOCKERS},
            "projected_blocked_miss_admission_cycles": total,
            "overall_blocking_rate_percent": f"{100.0 * total / eligible:.6f}",
            "denominator_semantics": "eligible frontend demand-miss admission cycles",
            "wbuf_reference_capacity": 8,
        })
        for kind, path in (("B0 target_slice", slice_csv), ("Motivation blocking", block_csv)):
            source_rows.append({
                "workload": workload, "artifact": kind, "path": str(path), "sha256": sha256(path),
                "core_commit": b0_manifest["core_commit"], "framework_commit": b0_manifest["framework_commit"],
                "source_log_sha256": b0_manifest["source_log_sha256"],
            })
    if observed != expected:
        raise RuntimeError(f"workload set mismatch: {observed} != {expected}")
    return util_rows, blocking_rows, source_rows


class Canvas:
    """Small dependency-free PNG + editable-SVG plotting surface."""
    def __init__(self, width=1320, height=650):
        self.width, self.height = width, height
        self.image = Image.new("RGB", (width, height), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                    '<rect width="100%" height="100%" fill="white"/>']
        self.regular = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        self.small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        self.tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        self.title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 21)

    @staticmethod
    def rgb(hexcolor):
        hexcolor = hexcolor.lstrip("#")
        return tuple(int(hexcolor[i:i+2], 16) for i in (0, 2, 4))

    def rect(self, xy, fill, outline=None, width=1):
        self.draw.rectangle(xy, fill=self.rgb(fill), outline=self.rgb(outline) if outline else None, width=width)
        x0, y0, x1, y1 = xy
        s = f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{fill}"'
        if outline: s += f' stroke="{outline}" stroke-width="{width}"'
        self.svg.append(s + '/>')

    def line(self, xy, fill="#000000", width=1, dash=None):
        x0, y0, x1, y1 = xy
        if dash and (x0 == x1 or y0 == y1):
            # The plots only use horizontal/vertical dashed grids.
            run = 4; gap = 4; length = abs((x1-x0) + (y1-y0)); direction = 1 if (x1 > x0 or y1 > y0) else -1
            for start in range(0, int(length), run + gap):
                end = min(start + run, length)
                if y0 == y1:
                    self.draw.line((x0 + direction*start, y0, x0 + direction*end, y0), fill=self.rgb(fill), width=width)
                else:
                    self.draw.line((x0, y0 + direction*start, x0, y0 + direction*end), fill=self.rgb(fill), width=width)
        else:
            self.draw.line(xy, fill=self.rgb(fill), width=width)
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.svg.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{fill}" stroke-width="{width}"{extra}/>')

    def text(self, pos, value, font="regular", fill="#111111", anchor="start", rotate=None):
        f = getattr(self, font)
        x, y = pos
        bbox = self.draw.textbbox((0, 0), value, font=f)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if rotate is None:
            px = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
            self.draw.text((px, y - h / 2), value, fill=self.rgb(fill), font=f)
        else:
            # Pillow does not rotate ImageDraw text in-place; create a tiny alpha layer.
            tile = Image.new("RGBA", (w + 10, h + 10), (255, 255, 255, 0))
            ImageDraw.Draw(tile).text((5, 5), value, fill=self.rgb(fill) + (255,), font=f)
            tile = tile.rotate(rotate, expand=True, resample=Image.Resampling.BICUBIC)
            self.image.paste(tile, (round(x - tile.width / 2), round(y - tile.height / 2)), tile)
        size = {"title": 21, "regular": 18, "small": 15, "tiny": 13}[font]
        transform = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
        self.svg.append(f'<text x="{x}" y="{y + size*.36:.1f}" text-anchor="{anchor}" font-family="DejaVu Sans, sans-serif" font-size="{size}" fill="{fill}"{transform}>{escape(value)}</text>')

    def save(self, stem):
        self.image.save(FIGURES / f"{stem}.png")
        (FIGURES / f"{stem}.svg").write_text("\n".join(self.svg + ["</svg>"]) + "\n")


def dashed_hgrid(c, x0, x1, y0, y1, ymax, ticks):
    for tick in ticks:
        y = y1 - (tick / ymax) * (y1-y0)
        c.line((x0, y, x1, y), "#777777", 1, "4 4")
        c.text((x0-11, y), f"{tick:g}", "small", anchor="end")
    c.line((x0, y0, x0, y1), "#000000", 2); c.line((x0, y1, x1, y1), "#000000", 2)


def blend(a, b, t):
    aa, bb = Canvas.rgb(a), Canvas.rgb(b)
    return "#" + "".join(f"{round(x + (y-x)*t):02x}" for x, y in zip(aa, bb))


def render(util_rows: list[dict], blocking_rows: list[dict]) -> None:
    workload_names = [w for w, _ in WORKLOADS]
    resource_names = [x[0] for x in RESOURCES]
    matrix = np.array([[float(next(r["utilization_percent"] for r in util_rows if r["workload"] == w and r["resource"] == rr))
                        for rr in resource_names] for w in workload_names])

    # A1: heatmap, white paper framing and fully editable SVG primitives.
    c = Canvas(1280, 600); c.text((640, 33), "A1. Per-slice hotspot occupancy / pressure proxy", "title", anchor="middle")
    x0, y0, cw, ch = 245, 92, 205, 56
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            v = matrix[i, j]; color = blend("#fff7bc", "#e31a1c", v / 100.0)
            c.rect((x0+j*cw, y0+i*ch, x0+(j+1)*cw, y0+(i+1)*ch), color, "#ffffff")
            c.text((x0+(j+.5)*cw, y0+(i+.5)*ch), f"{v:.1f}%", "small", "#111111" if v < 58 else "#ffffff", "middle")
    for i, w in enumerate(workload_names): c.text((x0-12, y0+(i+.5)*ch), w, "small", anchor="end")
    for j, r in enumerate(resource_names): c.text((x0+(j+.5)*cw, y0-16), r, "small", anchor="middle")
    c.text((x0, 535), "Selected P95 (AVG for MissQ) / fixed 128-entry per-slice capacity (%)", "small")
    for k in range(0, 101, 20):
        c.rect((x0+620+k*2, 519, x0+620+(k+20)*2, 535), blend("#fff7bc", "#e31a1c", (k+10)/100), None)
        c.text((x0+620+k*2, 555), str(k), "tiny", anchor="middle")
    c.text((x0+820, 555), "100", "tiny", anchor="middle")
    c.save("FIGA1_L2_UTILIZATION_HEATMAP")

    colors = ["#4C78A8", "#F2CF5B", "#59A14F", "#B279A2"]
    # A2: grouped bars.
    c = Canvas(); c.text((660, 36), "A2. L2 resource occupancy / pressure proxy (hotspot slice)", "title", anchor="middle")
    x0, x1, y0, y1 = 105, 1250, 105, 545; ymax = 105
    dashed_hgrid(c, x0, x1, y0, y1, ymax, [0, 20, 40, 60, 80, 100])
    group = (x1-x0)/len(workload_names); width = 25
    for idx, name in enumerate(resource_names):
        for wi, value in enumerate(matrix[:, idx]):
            cx = x0 + group*(wi+.5) + (idx-1.5)*width
            top = y1 - value/ymax*(y1-y0)
            c.rect((cx-width/2, top, cx+width/2, y1), colors[idx], "#333333")
    for wi, w in enumerate(workload_names): c.text((x0+group*(wi+.5), y1+28), w, "small", anchor="middle", rotate=19)
    c.text((28, (y0+y1)/2), "Occupancy / pressure proxy (%)", "small", anchor="middle", rotate=-90)
    lx = 275
    for idx, name in enumerate(resource_names):
        c.rect((lx, 65, lx+18, 83), colors[idx], "#333333"); c.text((lx+25, 74), name, "small"); lx += 215
    c.save("FIGA2_L2_UTILIZATION_GROUPED_BARS")

    # B: exact blocker values normalized only by the documented eligible-miss denominator.
    rates = []
    for w in workload_names:
        r = next(r for r in blocking_rows if r["workload"] == w)
        rates.append([100.0 * int(r[label]) / int(r["eligible_miss_admission_cycles"]) for label, _, _ in BLOCKERS])
    totals = np.array(rates).sum(axis=1); ymax = max(10, math.ceil(float(totals.max())*1.18 / 10.0)*10)
    c = Canvas(); c.text((660, 36), "B. L2 structural blocking breakdown (WBUF=8 reference)", "title", anchor="middle")
    x0, x1, y0, y1 = 105, 1250, 105, 545; dashed_hgrid(c, x0, x1, y0, y1, ymax, range(0, int(ymax)+1, 20))
    group = (x1-x0)/len(workload_names); barw = 62
    for wi, values in enumerate(rates):
        bottom = 0.0
        cx = x0+group*(wi+.5)
        for (label, _, color), val in zip(BLOCKERS, values):
            ybot = y1-bottom/ymax*(y1-y0); ytop = y1-(bottom+val)/ymax*(y1-y0)
            c.rect((cx-barw/2, ytop, cx+barw/2, ybot), color, "#333333")
            bottom += val
        c.text((cx, y1-bottom/ymax*(y1-y0)-14), f"{bottom:.1f}%", "tiny", anchor="middle")
        c.text((cx, y1+28), workload_names[wi], "small", anchor="middle", rotate=19)
    c.text((28, (y0+y1)/2), "Share of eligible demand-miss admission cycles (%)", "small", anchor="middle", rotate=-90)
    lx = 135
    for label, _, color in BLOCKERS:
        c.rect((lx, 65, lx+18, 83), color, "#333333"); c.text((lx+25, 74), label, "small"); lx += 205
    c.save("FIGB_L2_BLOCKING_SUBSET_WBUF8")


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True); FIGURES.mkdir(parents=True, exist_ok=True)
    util_rows, blocking_rows, source_rows = parse_and_validate()
    write_csv(TABLES / "A1_A2_utilization_hotspot_table.csv", util_rows,
              ["workload", "resource", "aggregation", "source_field", "selected_stat", "raw_entries", "capacity_entries", "utilization_percent", "semantic_mapping"])
    write_csv(TABLES / "B_blocking_wbuf8_subset.csv", blocking_rows,
              ["workload", "eligible_miss_admission_cycles", "SET_ASSOC", "MSHR_META", "MISSQ_LOWER", "WB_PATH", "OTHER", "projected_blocked_miss_admission_cycles", "overall_blocking_rate_percent", "denominator_semantics", "wbuf_reference_capacity"])
    write_csv(TABLES / "frozen_source_csv_sha256.csv", source_rows,
              ["workload", "artifact", "path", "sha256", "core_commit", "framework_commit", "source_log_sha256"])
    render(util_rows, blocking_rows)


if __name__ == "__main__":
    main()
