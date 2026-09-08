#!/usr/bin/env python3
"""Generate the two data-asserted figures for the LLM-memory one-page PPT.

This program only reads frozen A/C4 closeout TSVs.  It deliberately does not
invoke Accel-Sim, read traces, or modify the authority inputs.  SVG is emitted
directly for PowerPoint; PNG is drawn from the same computed values with Pillow
for quick review.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import os
import sys
import xml.sax.saxutils
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = ROOT / "docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT"
TOTALS = AUTHORITY / "TRANSLATION_TOTALS.tsv"
LOCALITY = AUTHORITY / "C4_TRACE_LOCALITY_SUMMARY.tsv"
REPLACEMENTS = AUTHORITY / "L2_TLB_REPLACEMENT_MATRIX.tsv"
REFERENCE = ROOT / "docs/vm_tlb/codex_handoff/ppt_onepage/FIGURES_AB_REFERENCE_DATA.tsv"
OUT = ROOT / "docs/vm_tlb/ppt_figures/llm_memory_onepage"

WIDTH, HEIGHT = 1920, 1080
FONT_FAMILY = "Noto Sans CJK SC, Microsoft YaHei, sans-serif"
FONT_REGULAR_CANDIDATES = (
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
)
FONT_BOLD_CANDIDATES = (
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
)

# High-contrast, print-safe technical-report palette.  Color is never the only
# category encoding: the labels and the path column headers carry the identity.
NAVY = "#17324D"
TEXT = "#203040"
MUTED = "#657587"
GRID = "#D8E0E8"
PALE_BLUE = "#EAF3FA"
PALE_ORANGE = "#FFF1E5"
BLUE = "#277DA1"
ORANGE = "#D66A2C"
TEAL = "#2A9D8F"
WHITE = "#FFFFFF"
PAPER = "#FBFCFE"


@dataclass(frozen=True)
class Metric:
    figure: str
    metric: str
    roi: str
    numerator: int
    denominator: int | None
    value: float
    display: str
    formula: str
    source: Path
    source_rows: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require_one(rows: Iterable[Dict[str, str]], label: str) -> Dict[str, str]:
    matches = list(rows)
    if len(matches) != 1:
        raise AssertionError(f"{label}: expected exactly one row, found {len(matches)}")
    return matches[0]


def int_value(row: Dict[str, str], field: str, label: str) -> int:
    try:
        return int(row[field])
    except (KeyError, ValueError) as exc:
        raise AssertionError(f"{label}: invalid integer field {field!r}") from exc


def font_path(bold: bool) -> str:
    for candidate in FONT_BOLD_CANDIDATES if bold else FONT_REGULAR_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    raise RuntimeError("Noto Sans CJK SC font is required for Chinese PPT labels")


class PngCanvas:
    def __init__(self, width: int = WIDTH, height: int = HEIGHT,
                 background: str | None = WHITE, scale: float = 1.0) -> None:
        self.width, self.height, self.scale = width, height, scale
        if background is None:
            self.image = Image.new("RGBA", (round(width * scale), round(height * scale)),
                                   (255, 255, 255, 0))
        else:
            self.image = Image.new("RGB", (round(width * scale), round(height * scale)), background)
        self.draw = ImageDraw.Draw(self.image)
        self._fonts: Dict[Tuple[int, bool], ImageFont.FreeTypeFont] = {}

    def scaled(self, value: float) -> int:
        return round(value * self.scale)

    def font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        key = (size, bold)
        if key not in self._fonts:
            self._fonts[key] = ImageFont.truetype(font_path(bold), size=self.scaled(size), index=0)
        return self._fonts[key]

    def rect(self, x: float, y: float, w: float, h: float, fill: str,
             outline: str | None = None, radius: int = 0, width: int = 2) -> None:
        box = (self.scaled(x), self.scaled(y), self.scaled(x + w), self.scaled(y + h))
        if radius:
            self.draw.rounded_rectangle(box, radius=self.scaled(radius), fill=fill,
                                        outline=outline, width=self.scaled(width))
        else:
            self.draw.rectangle(box, fill=fill, outline=outline, width=self.scaled(width))

    def line(self, points: Sequence[Tuple[float, float]], fill: str, width: int = 2) -> None:
        self.draw.line([(self.scaled(x), self.scaled(y)) for x, y in points], fill=fill,
                       width=self.scaled(width))

    def polygon(self, points: Sequence[Tuple[float, float]], fill: str) -> None:
        self.draw.polygon([(self.scaled(x), self.scaled(y)) for x, y in points], fill=fill)

    def text(self, x: float, y: float, text: str, size: int, fill: str = TEXT,
             bold: bool = False, anchor: str = "la") -> None:
        self.draw.text((self.scaled(x), self.scaled(y)), text, font=self.font(size, bold),
                       fill=fill, anchor=anchor)

    def save(self, path: Path) -> None:
        self.image.save(path, format="PNG", optimize=True)


class SvgCanvas:
    def __init__(self, width: int = WIDTH, height: int = HEIGHT,
                 background: str | None = WHITE) -> None:
        self.parts: List[str] = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img">',
        ]
        if background is not None:
            self.parts.append(f'<rect width="100%" height="100%" fill="{background}"/>')

    @staticmethod
    def esc(value: str) -> str:
        return xml.sax.saxutils.escape(value)

    def rect(self, x: float, y: float, w: float, h: float, fill: str,
             outline: str | None = None, radius: int = 0, width: int = 2) -> None:
        attrs = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'width="{w:.1f}"',
                 f'height="{h:.1f}"', f'fill="{fill}"']
        if radius:
            attrs.extend((f'rx="{radius}"', f'ry="{radius}"'))
        if outline:
            attrs.extend((f'stroke="{outline}"', f'stroke-width="{width}"'))
        self.parts.append("<rect " + " ".join(attrs) + "/>")

    def line(self, points: Sequence[Tuple[float, float]], fill: str, width: int = 2) -> None:
        coord = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        self.parts.append(f'<polyline points="{coord}" fill="none" stroke="{fill}" '
                          f'stroke-width="{width}" stroke-linecap="round"/>')

    def polygon(self, points: Sequence[Tuple[float, float]], fill: str) -> None:
        coord = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        self.parts.append(f'<polygon points="{coord}" fill="{fill}"/>')

    def text(self, x: float, y: float, text: str, size: int, fill: str = TEXT,
             bold: bool = False, anchor: str = "la") -> None:
        mapping = {"la": "start", "ma": "middle", "ra": "end", "lm": "start",
                   "mm": "middle", "rm": "end"}
        align = mapping.get(anchor, "start")
        baseline = "middle" if anchor.endswith("m") else "alphabetic"
        weight = "700" if bold else "400"
        self.parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{align}" '
            f'dominant-baseline="{baseline}" font-family="{FONT_FAMILY}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}">{self.esc(text)}</text>'
        )

    def save(self, path: Path) -> None:
        path.write_text("\n".join(self.parts + ["</svg>", ""]), encoding="utf-8")


def both(canvases: Sequence[object], method: str, *args, **kwargs) -> None:
    for canvas in canvases:
        getattr(canvas, method)(*args, **kwargs)


def compute_metrics() -> List[Metric]:
    totals = read_tsv(TOTALS)
    locality = read_tsv(LOCALITY)
    replacements = read_tsv(REPLACEMENTS)
    reference = read_tsv(REFERENCE)
    reference_by_key = {(r["figure"], r["metric"], r["roi"]): r for r in reference}

    def total(roi: str, metric: str) -> int:
        row = require_one(
            (r for r in totals if r["roi"] == roi and r["profile"] == "generic" and
             r["metric"] == metric),
            f"TRANSLATION_TOTALS {roi}/{metric}",
        )
        return int_value(row, "value", f"TRANSLATION_TOTALS {roi}/{metric}")

    def locality_row(roi: str, object_class: str) -> Dict[str, str]:
        return require_one(
            (r for r in locality if r["roi"] == roi and r["object_class"] == object_class),
            f"C4_TRACE_LOCALITY_SUMMARY {roi}/{object_class}",
        )

    def checked(figure: str, name: str, roi: str, numerator: int,
                denominator: int | None, display: str, formula: str, source: Path,
                source_rows: str) -> Metric:
        key = (figure, name, roi)
        if key not in reference_by_key:
            raise AssertionError(f"reference TSV lacks {key}")
        ref = reference_by_key[key]
        if int(ref["numerator"]) != numerator:
            raise AssertionError(f"{key} numerator mismatch: {numerator} != {ref['numerator']}")
        ref_den = None if ref["denominator"] == "NA" else int(ref["denominator"])
        if ref_den != denominator:
            raise AssertionError(f"{key} denominator mismatch: {denominator} != {ref_den}")
        value = float(numerator) if denominator is None else numerator * 100.0 / denominator
        if name.endswith("per_1M_translation_requests"):
            value = numerator * 1_000_000.0 / denominator  # type: ignore[operator]
        if not math.isclose(value, float(ref["exact_value"]), rel_tol=0.0, abs_tol=1e-6):
            raise AssertionError(f"{key} value mismatch: {value} != {ref['exact_value']}")
        return Metric(figure, name, roi, numerator, denominator, value, display, formula,
                      source, source_rows)

    metrics: List[Metric] = []
    for roi in ("prefill", "decode1"):
        l1_accesses = total(roi, "vm_l1_tlb_accesses")
        l1_misses = total(roi, "vm_l1_tlb_misses")
        l2_misses = total(roi, "vm_l2_tlb_misses")
        mshr_full = total(roi, "vm_translation_mshr_full_events")
        metrics.append(checked("A", "L1_TLB_miss_rate_pct", roi, l1_misses, l1_accesses,
                               f"{l1_misses * 100.0 / l1_accesses:.4f}%",
                               "vm_l1_tlb_misses / vm_l1_tlb_accesses × 100",
                               TOTALS,
                               f"roi={roi};profile=generic;metric=vm_l1_tlb_misses|vm_l1_tlb_accesses"))
        metrics.append(checked("A", "L2_continued_miss_pct", roi, l2_misses, l1_misses,
                               f"{l2_misses * 100.0 / l1_misses:.4f}%",
                               "vm_l2_tlb_misses / vm_l1_tlb_misses × 100",
                               TOTALS,
                               f"roi={roi};profile=generic;metric=vm_l2_tlb_misses|vm_l1_tlb_misses"))
        metrics.append(checked("A", "MSHR_full_events_full_roi", roi, mshr_full, None,
                               "0" if mshr_full == 0 else "2.30M",
                               "vm_translation_mshr_full_events (event counter)", TOTALS,
                               f"roi={roi};profile=generic;metric=vm_translation_mshr_full_events"))
        metrics.append(checked("A", "MSHR_full_events_per_1M_translation_requests", roi,
                               mshr_full, l1_accesses,
                               "0 events / 1M translation requests" if mshr_full == 0 else
                               "30.35K events / 1M translation requests",
                               "vm_translation_mshr_full_events / vm_translation_lookup_requests × 1,000,000",
                               TOTALS,
                               f"roi={roi};profile=generic;metric=vm_translation_mshr_full_events|vm_translation_lookup_requests"))
        if total(roi, "vm_translation_lookup_requests") != l1_accesses:
            raise AssertionError(f"{roi}: lookup-request and L1-access totals must agree")

        rows = [locality_row(roi, kind) for kind in ("WEIGHT", "KV_CACHE", "UNKNOWN")]
        weight = locality_row(roi, "WEIGHT")
        lane_den = sum(int_value(r, "sum_lane_references", f"{roi} lane") for r in rows)
        page_den = sum(int_value(r, "roi_union_unique_64kb_pages", f"{roi} pages") for r in rows)
        metrics.append(checked("B", "Weight_lane_reference_share_pct", roi,
                               int_value(weight, "sum_lane_references", f"{roi} weight lane"), lane_den,
                               f"{int_value(weight, 'sum_lane_references', f'{roi} weight lane') * 100.0 / lane_den:.0f}%",
                               "WEIGHT sum_lane_references / all object classes × 100", LOCALITY,
                               f"roi={roi};object_class=WEIGHT,KV_CACHE,UNKNOWN;field=sum_lane_references"))
        metrics.append(checked("B", "Weight_64KB_unique_page_share_pct", roi,
                               int_value(weight, "roi_union_unique_64kb_pages", f"{roi} weight pages"), page_den,
                               f"{int_value(weight, 'roi_union_unique_64kb_pages', f'{roi} weight pages') * 100.0 / page_den:.0f}%",
                               "WEIGHT roi_union_unique_64kb_pages / all object classes × 100", LOCALITY,
                               f"roi={roi};object_class=WEIGHT,KV_CACHE,UNKNOWN;field=roi_union_unique_64kb_pages"))

    decode_matrix = [r for r in replacements if r["roi"] == "decode1" and r["profile"] == "generic"]
    if len(decode_matrix) != 9:
        raise AssertionError(f"decode1 generic replacement matrix must have 9 rows, got {len(decode_matrix)}")
    ww = require_one((r for r in decode_matrix if r["incoming_object"] == "WEIGHT" and
                      r["victim_object"] == "WEIGHT"), "decode1 WEIGHT→WEIGHT")
    total_replacements = sum(int_value(r, "count", "decode1 replacement") for r in decode_matrix)
    if total_replacements != total("decode1", "vm_l2_tlb_evictions"):
        raise AssertionError("decode1 replacement-matrix total must equal vm_l2_tlb_evictions")
    metrics.append(checked("B", "L2_TLB_Weight_to_Weight_replacement_share_pct", "decode1",
                           int_value(ww, "count", "decode1 WEIGHT→WEIGHT"), total_replacements,
                           "97.1%",
                           "WEIGHT→WEIGHT replacements / all L2 TLB replacements × 100",
                           REPLACEMENTS,
                           "roi=decode1;profile=generic;incoming_object=WEIGHT;victim_object=WEIGHT;all 9 matrix cells"))
    if len(metrics) != len(reference):
        raise AssertionError(f"expected {len(reference)} asserted metrics, built {len(metrics)}")
    return metrics


def metric(metrics: Sequence[Metric], figure: str, name: str, roi: str) -> Metric:
    return next(m for m in metrics if (m.figure, m.metric, m.roi) == (figure, name, roi))


def arrow(canvases: Sequence[object], x: float, y1: float, y2: float, color: str) -> None:
    both(canvases, "line", [(x, y1), (x, y2 - 16)], color, 5)
    both(canvases, "polygon", [(x - 12, y2 - 17), (x + 12, y2 - 17), (x, y2)], color)


def draw_title(canvases: Sequence[object], title: str, subtitle: str) -> None:
    both(canvases, "text", 90, 83, title, 43, NAVY, True, "la")
    both(canvases, "line", [(90, 112), (1830, 112)], NAVY, 3)
    both(canvases, "text", 90, 151, subtitle, 23, MUTED, False, "la")


def draw_figure_a(metrics: Sequence[Metric], png_path: Path, svg_path: Path) -> None:
    png, svg = PngCanvas(), SvgCanvas()
    canvases: Sequence[object] = (png, svg)
    draw_title(canvases, "预填充与解码阶段的 TLB 压力来源不同",
               "同一翻译路径的三个层级；每一级使用各自的语义与量纲")
    columns = [
        (150, "预填充（Prefill）", "prefill", BLUE, PALE_BLUE),
        (1010, "解码（Decode）", "decode1", ORANGE, PALE_ORANGE),
    ]
    y_boxes = (260, 465, 670)
    for x, heading, roi, color, pale in columns:
        both(canvases, "rect", x, 185, 760, 55, color, color, 12, 1)
        both(canvases, "text", x + 380, 213, heading, 28, WHITE, True, "mm")
        for y in y_boxes:
            both(canvases, "rect", x, y, 760, 155, PAPER, GRID, 16, 2)
            both(canvases, "rect", x, y, 11, 155, color, color, 10, 1)
        arrow(canvases, x + 380, 418, 458, color)
        arrow(canvases, x + 380, 623, 663, color)

        l1 = metric(metrics, "A", "L1_TLB_miss_rate_pct", roi)
        l2 = metric(metrics, "A", "L2_continued_miss_pct", roi)
        mshr_total = metric(metrics, "A", "MSHR_full_events_full_roi", roi)
        mshr_norm = metric(metrics, "A", "MSHR_full_events_per_1M_translation_requests", roi)
        both(canvases, "text", x + 38, 300, "L1 TLB 未命中率", 27, TEXT, True, "la")
        both(canvases, "text", x + 722, 300, l1.display, 38, color, True, "ra")
        both(canvases, "text", x + 38, 352,
             f"{l1.numerator:,} / {l1.denominator:,}", 22, MUTED, False, "la")
        both(canvases, "text", x + 38, 505, "进入 L2 后继续未命中", 27, TEXT, True, "la")
        both(canvases, "text", x + 722, 505, l2.display, 38, color, True, "ra")
        both(canvases, "text", x + 38, 557,
             f"{l2.numerator:,} / {l2.denominator:,}", 22, MUTED, False, "la")
        both(canvases, "text", x + 38, 710, "Translation MSHR-full 事件", 27, TEXT, True, "la")
        total_text = "full-ROI 累计：0" if mshr_total.numerator == 0 else "full-ROI 累计：2.30M"
        both(canvases, "text", x + 38, 758, total_text, 28, color, True, "la")
        norm_text = "0 events / 1M translation requests" if mshr_norm.numerator == 0 else \
            "30.35K events / 1M translation requests"
        both(canvases, "text", x + 38, 795, norm_text, 21, TEXT, False, "la")
    both(canvases, "rect", 150, 888, 1620, 86, "#F3F6F9", GRID, 14, 1)
    both(canvases, "text", 960, 931,
         "结论：Prefill 更偏翻译覆盖范围/容量压力；Decode 更偏高代价未命中、并发与长尾压力。",
         26, NAVY, True, "mm")
    both(canvases, "text", 150, 1022,
         "注：MSHR-full 为事件计数，归一化仅用于表示每百万 translation requests 的事件密度，不是请求发生率。",
         19, MUTED, False, "la")
    png.save(png_path)
    svg.save(svg_path)


def draw_figure_b(metrics: Sequence[Metric], png_path: Path, svg_path: Path) -> None:
    png, svg = PngCanvas(), SvgCanvas()
    canvases: Sequence[object] = (png, svg)
    draw_title(canvases, "Weight 动态访问占比低，但主导页级翻译工作集",
               "动态 lane 访问与 64KB 唯一页工作集回答的是不同的翻译压力问题")
    # Keep the 99% Decode label clear of the replacement callout above it.
    plot_left, plot_right, plot_top, plot_bottom = 220, 1740, 350, 820
    plot_height = plot_bottom - plot_top
    for pct in range(0, 101, 25):
        y = plot_bottom - plot_height * pct / 100.0
        both(canvases, "line", [(plot_left, y), (plot_right, y)], GRID, 2 if pct == 0 else 1)
        both(canvases, "text", plot_left - 25, y, f"{pct}%", 21, MUTED, False, "rm")
    both(canvases, "line", [(plot_left, plot_top), (plot_left, plot_bottom)], NAVY, 2)
    both(canvases, "line", [(plot_left, plot_bottom), (plot_right, plot_bottom)], NAVY, 2)
    both(canvases, "text", 98, 560, "占比（%）", 23, NAVY, True, "mm")

    groups = [(650, "预填充（Prefill）", "prefill"), (1310, "解码（Decode）", "decode1")]
    bar_width, gap = 132, 42
    for center, label, roi in groups:
        access = metric(metrics, "B", "Weight_lane_reference_share_pct", roi)
        pages = metric(metrics, "B", "Weight_64KB_unique_page_share_pct", roi)
        for x, item, color in ((center - gap / 2 - bar_width, access, BLUE),
                               (center + gap / 2, pages, TEAL)):
            h = plot_height * item.value / 100.0
            y = plot_bottom - h
            both(canvases, "rect", x, y, bar_width, h, color, NAVY, 5, 1)
            # Middle/middle anchoring fixes the label's full glyph box above the
            # bar, including the 99% Decode bar close to the 100% grid line.
            both(canvases, "text", x + bar_width / 2, y - 23, item.display, 29, color, True, "mm")
        both(canvases, "text", center, 872, label, 27, NAVY, True, "ma")

    # This callout sits above the Decode bars; its leader ends below the text and
    # above the 99% bar label so no annotation covers a data label.
    both(canvases, "rect", 1087, 177, 445, 64, PALE_ORANGE, ORANGE, 12, 2)
    both(canvases, "text", 1309, 209, "97.1% 的 L2 TLB 替换为 Weight → Weight", 22,
         TEXT, True, "mm")
    both(canvases, "line", [(1309, 242), (1309, 266)], ORANGE, 3)
    both(canvases, "polygon", [(1299, 264), (1319, 264), (1309, 278)], ORANGE)

    legend_y = 965
    both(canvases, "rect", 485, legend_y - 19, 25, 25, BLUE, NAVY, 3, 1)
    both(canvases, "text", 525, legend_y, "Weight 动态 lane 访问占比", 23, TEXT, False, "lm")
    both(canvases, "rect", 1035, legend_y - 19, 25, 25, TEAL, NAVY, 3, 1)
    both(canvases, "text", 1075, legend_y, "Weight 占 64KB 唯一页比例", 23, TEXT, False, "lm")
    both(canvases, "text", 220, 1030,
         "注：页工作集为 ROI 内各 object class 的 64KB 唯一页并集；UNKNOWN 未重命名为 Activation。",
         19, MUTED, False, "la")
    png.save(png_path)
    svg.save(svg_path)


def draw_figure_a_asset(metrics: Sequence[Metric], png_path: Path, svg_path: Path) -> None:
    """Draw a tightly cropped, title-free pressure-path figure asset."""
    logical_width, logical_height = 1800, 650
    png = PngCanvas(logical_width, logical_height, background=None, scale=2.0)
    svg = SvgCanvas(logical_width, logical_height, background=None)
    canvases: Sequence[object] = (png, svg)
    columns = [
        (80, "预填充  Prefill", "prefill", BLUE, PALE_BLUE),
        (970, "解码  Decode", "decode1", ORANGE, PALE_ORANGE),
    ]
    row_y = (125, 305, 485)
    for x, stage, roi, color, pale in columns:
        # A short stage chip and one thin rail encode the column/path identity;
        # unlike the original slide, neither is a title band or a large card.
        both(canvases, "rect", x, 35, 250, 42, color, color, 10, 1)
        both(canvases, "text", x + 125, 56, stage, 23, WHITE, True, "mm")
        rail_x = x + 25
        both(canvases, "line", [(rail_x, 109), (rail_x, 573)], color, 3)
        arrow(canvases, rail_x, 212, 276, color)
        arrow(canvases, rail_x, 392, 456, color)
        for index, y in enumerate(row_y, start=1):
            both(canvases, "rect", x + 3, y - 18, 44, 44, pale, color, 22, 2)
            both(canvases, "text", x + 25, y + 4, str(index), 19, color, True, "mm")
            if index < 3:
                both(canvases, "line", [(x + 68, y + 85), (x + 745, y + 85)], GRID, 2)

        l1 = metric(metrics, "A", "L1_TLB_miss_rate_pct", roi)
        l2 = metric(metrics, "A", "L2_continued_miss_pct", roi)
        mshr_total = metric(metrics, "A", "MSHR_full_events_full_roi", roi)
        label_x, value_x = x + 74, x + 766
        both(canvases, "text", label_x, 126, "L1 TLB 未命中率", 28, TEXT, True, "la")
        both(canvases, "text", value_x, 126, l1.display, 34, color, True, "ra")
        both(canvases, "text", label_x, 171, f"{l1.numerator:,} / {l1.denominator:,}",
             20, MUTED, False, "la")
        both(canvases, "text", label_x, 306, "L2 继续未命中率", 28, TEXT, True, "la")
        both(canvases, "text", value_x, 306, l2.display, 34, color, True, "ra")
        both(canvases, "text", label_x, 351, f"{l2.numerator:,} / {l2.denominator:,}",
             20, MUTED, False, "la")
        both(canvases, "text", label_x, 486, "Translation MSHR-full", 28, TEXT, True, "la")
        if mshr_total.numerator == 0:
            total_text = "full-ROI：0"
            norm_text = "0 events / 1M translation requests"
        else:
            total_text = "full-ROI：~2.30M"
            norm_text = "30.35K events / 1M translation requests"
        both(canvases, "text", label_x, 532, total_text, 29, color, True, "la")
        both(canvases, "text", label_x, 575, norm_text, 19, TEXT, False, "la")
    png.save(png_path)
    svg.save(svg_path)


def draw_figure_b_asset(metrics: Sequence[Metric], png_path: Path, svg_path: Path) -> None:
    """Draw a compact bar-chart asset with direct labels instead of a legend."""
    logical_width, logical_height = 1600, 720
    png = PngCanvas(logical_width, logical_height, background=None, scale=2.0)
    svg = SvgCanvas(logical_width, logical_height, background=None)
    canvases: Sequence[object] = (png, svg)
    plot_left, plot_right, plot_top, plot_bottom = 130, 1540, 135, 535
    plot_height = plot_bottom - plot_top
    for pct in (0, 50, 100):
        y = plot_bottom - plot_height * pct / 100.0
        both(canvases, "line", [(plot_left, y), (plot_right, y)], GRID, 2 if pct == 0 else 1)
        both(canvases, "text", plot_left - 18, y, f"{pct}%", 18, MUTED, False, "rm")
    both(canvases, "line", [(plot_left, plot_top), (plot_left, plot_bottom)], NAVY, 2)
    both(canvases, "line", [(plot_left, plot_bottom), (plot_right, plot_bottom)], NAVY, 2)
    groups = [(510, "预填充（Prefill）", "prefill"), (1170, "解码（Decode）", "decode1")]
    bar_width, gap = 112, 40
    for center, group_label, roi in groups:
        access = metric(metrics, "B", "Weight_lane_reference_share_pct", roi)
        pages = metric(metrics, "B", "Weight_64KB_unique_page_share_pct", roi)
        bar_items = (
            (center - gap / 2 - bar_width, access, BLUE, "动态访问"),
            (center + gap / 2, pages, TEAL, "64KB页工作集"),
        )
        for x, item, color, direct_label in bar_items:
            h = plot_height * item.value / 100.0
            y = plot_bottom - h
            both(canvases, "rect", x, y, bar_width, h, color, NAVY, 4, 1)
            both(canvases, "text", x + bar_width / 2, y - 18, f"{item.value:.2f}%",
                 25, color, True, "mm")
            both(canvases, "text", x + bar_width / 2, 584, direct_label,
                 18, color, True, "mm")
        both(canvases, "text", center, 643, group_label, 23, NAVY, True, "mm")

    # A plain annotation rather than a slide-sized callout card.  Its arrow
    # lands in the Decode group gap, away from the 98.96% label.
    both(canvases, "text", 1168, 49, "97.1% L2 TLB 替换：Weight → Weight", 22,
         ORANGE, True, "mm")
    both(canvases, "line", [(1168, 69), (1168, 101)], ORANGE, 3)
    both(canvases, "polygon", [(1159, 99), (1177, 99), (1168, 111)], ORANGE)
    png.save(png_path)
    svg.save(svg_path)


def write_data_used(metrics: Sequence[Metric], path: Path) -> None:
    headers = [
        "figure", "metric", "roi", "numerator", "denominator", "computed_value",
        "unit", "display_value", "formula", "authority_tsv", "authority_sha256",
        "authority_rows", "reference_tsv", "reference_sha256", "assertion",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for item in metrics:
            unit = "events / 1M translation requests" if item.metric.endswith("per_1M_translation_requests") \
                else "events" if item.metric.endswith("events_full_roi") else "percent"
            writer.writerow({
                "figure": item.figure,
                "metric": item.metric,
                "roi": item.roi,
                "numerator": item.numerator,
                "denominator": "NA" if item.denominator is None else item.denominator,
                "computed_value": f"{item.value:.10f}",
                "unit": unit,
                "display_value": item.display,
                "formula": item.formula,
                "authority_tsv": item.source.relative_to(ROOT),
                "authority_sha256": sha256(item.source),
                "authority_rows": item.source_rows,
                "reference_tsv": REFERENCE.relative_to(ROOT),
                "reference_sha256": sha256(REFERENCE),
                "assertion": "PASS: parsed numerator/denominator/computed value equal reference TSV",
            })


def verify_outputs(paths: Sequence[Path]) -> None:
    for path in paths:
        if not path.exists() or path.stat().st_size == 0:
            raise AssertionError(f"missing output: {path}")
    for path in (paths[0], paths[2]):
        with Image.open(path) as image:
            if image.size != (WIDTH, HEIGHT):
                raise AssertionError(f"{path}: unexpected PNG dimensions {image.size}")
            if image.getbbox() is None:
                raise AssertionError(f"{path}: blank PNG")
    for path in (paths[1], paths[3]):
        text = path.read_text(encoding="utf-8")
        if not (text.startswith("<?xml") and text.rstrip().endswith("</svg>")):
            raise AssertionError(f"{path}: malformed SVG envelope")


def verify_asset_outputs(paths: Sequence[Path]) -> None:
    """Check asset-specific dimensions, transparent backgrounds, and required text."""
    expected_sizes = ((3600, 1300), (3200, 1440))
    for path in paths:
        if not path.exists() or path.stat().st_size == 0:
            raise AssertionError(f"missing asset output: {path}")
    for path, expected in zip((paths[0], paths[2]), expected_sizes):
        with Image.open(path) as image:
            if image.size != expected or image.mode != "RGBA":
                raise AssertionError(f"{path}: expected transparent high-res PNG {expected}, got "
                                     f"{image.mode} {image.size}")
            if image.getpixel((0, 0))[3] != 0:
                raise AssertionError(f"{path}: corner is not transparent")
            if image.getbbox() is None:
                raise AssertionError(f"{path}: blank PNG")
    required_text = {
        paths[1]: ("预填充  Prefill", "解码  Decode", "Translation MSHR-full",
                   "full-ROI：~2.30M", "30.35K events / 1M translation requests"),
        paths[3]: ("15.98%", "87.41%", "7.86%", "98.96%",
                   "97.1% L2 TLB 替换：Weight → Weight"),
    }
    for path, phrases in required_text.items():
        text = path.read_text(encoding="utf-8")
        if not (text.startswith("<?xml") and text.rstrip().endswith("</svg>")):
            raise AssertionError(f"{path}: malformed SVG envelope")
        # There is no root background rectangle in an asset SVG.
        if '<rect width="100%" height="100%"' in text:
            raise AssertionError(f"{path}: asset SVG background is not transparent")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"{path}: missing required label {phrase!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    parser.add_argument("--asset-only", action="store_true",
                        help="generate only the title-free compact figure assets")
    args = parser.parse_args()
    for required in (TOTALS, LOCALITY, REPLACEMENTS, REFERENCE):
        if not required.is_file():
            raise FileNotFoundError(required)
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    metrics = compute_metrics()
    write_data_used(metrics, output / "FIGURE_DATA_USED.tsv")
    if args.asset_only:
        a_png = output / "FIG_A_PREFILL_DECODE_TLB_PRESSURE_ASSET.png"
        a_svg = output / "FIG_A_PREFILL_DECODE_TLB_PRESSURE_ASSET.svg"
        b_png = output / "FIG_B_WEIGHT_ACCESS_VS_TRANSLATION_WORKING_SET_ASSET.png"
        b_svg = output / "FIG_B_WEIGHT_ACCESS_VS_TRANSLATION_WORKING_SET_ASSET.svg"
        draw_figure_a_asset(metrics, a_png, a_svg)
        draw_figure_b_asset(metrics, b_png, b_svg)
        verify_asset_outputs((a_png, a_svg, b_png, b_svg))
        print("PPT_FIGURES_AB_ASSET_ASSERTIONS PASS")
    else:
        a_png = output / "FIG_A_PREFILL_DECODE_TLB_PRESSURE.png"
        a_svg = output / "FIG_A_PREFILL_DECODE_TLB_PRESSURE.svg"
        b_png = output / "FIG_B_WEIGHT_ACCESS_VS_TRANSLATION_WORKING_SET.png"
        b_svg = output / "FIG_B_WEIGHT_ACCESS_VS_TRANSLATION_WORKING_SET.svg"
        draw_figure_a(metrics, a_png, a_svg)
        draw_figure_b(metrics, b_png, b_svg)
        verify_outputs((a_png, a_svg, b_png, b_svg))
        print("PPT_FIGURES_AB_DATA_ASSERTIONS PASS")
    for item in (a_svg, a_png, b_svg, b_png, output / "FIGURE_DATA_USED.tsv"):
        print(item.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"PPT_FIGURES_AB_DATA_ASSERTIONS FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
