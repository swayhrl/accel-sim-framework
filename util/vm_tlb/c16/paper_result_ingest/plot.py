#!/usr/bin/env python3
"""Dependency-free SVG plots from PAPER_RESULTS_CURRENT.json only."""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from ingest import OUT, ROOT


def lookup(rows: list[dict], domain: str, condition: str, metric: str):
    matches = [r for r in rows if (r["domain"], r["condition"], r["metric"]) ==
               (domain, condition, metric)]
    if len(matches) != 1:
        raise ValueError(f"missing/duplicate metric: {domain}/{condition}/{metric}")
    row = matches[0]
    if row["status"] == "PENDING":
        if row["value"] is not None:
            raise ValueError("PENDING row carries a value")
        return None
    if row["status"] != "ACCEPTED" or row["value"] is None or not row["source_sha256"] or not row["source_commit"]:
        raise ValueError("unqualified plot row")
    return float(row["value"])


def bars(title: str, subtitle: str, labels: list[str], values: list[float], unit: str) -> str:
    if not values or len(labels) != len(values):
        raise ValueError("empty or mismatched plot data")
    width, left, right, top, step = 920, 270, 120, 100, 58
    height = top + len(values) * step + 65
    scale = max(abs(x) for x in values) or 1.0
    extent = (width - left - right) / 2
    zero = left + extent
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
             f'<title>{escape(title)}</title>',
             f'<desc>{escape(subtitle)}. Bars show signed values in {escape(unit)}; blue is positive and orange is negative.</desc>',
             '<rect width="100%" height="100%" fill="white"/>',
             '<style>text{font-family:Arial,sans-serif;fill:#172033} .title{font-size:22px;font-weight:bold} .sub{font-size:13px;fill:#526072} .label{font-size:14px} .value{font-size:13px;font-weight:bold}</style>',
             f'<text class="title" x="30" y="38">{escape(title)}</text>',
             f'<text class="sub" x="30" y="63">{escape(subtitle)}</text>',
             f'<line x1="{zero:.1f}" y1="80" x2="{zero:.1f}" y2="{height-35}" stroke="#526072"/>']
    for index, (label, value) in enumerate(zip(labels, values)):
        y = top + index * step
        length = abs(value) / scale * extent
        x = zero if value >= 0 else zero - length
        color = "#1976a3" if value >= 0 else "#c45c42"
        value_x = x + length + 8 if value >= 0 else x - 8
        anchor = "start" if value >= 0 else "end"
        lines.extend((f'<text class="label" x="30" y="{y+21}">{escape(label)}</text>',
                      f'<rect x="{x:.1f}" y="{y+5}" width="{length:.1f}" height="25" fill="{color}"/>',
                      f'<text class="value" text-anchor="{anchor}" x="{value_x:.1f}" y="{y+23}">{value:.4g} {escape(unit)}</text>'))
    lines.append('</svg>')
    return "\n".join(lines) + "\n"


def generate(table: dict, output: Path) -> list[str]:
    if table.get("schema") != "C16_E1_PAPER_RESULTS_V1" or not isinstance(table.get("rows"), list):
        raise ValueError("wrong results schema")
    rows = table["rows"]
    output.mkdir(parents=True, exist_ok=True)
    written = []

    sizes = [lookup(rows, "footprint", "M1", key) / (1024 * 1024)
             for key in ("AWQ_packed_storage_bytes", "device_L2_bytes", "RAW_FP16_dense_weight_bytes")]
    name = "FIG_FOOTPRINT.svg"
    (output / name).write_text(bars("Packed weight residency opportunity", "Accepted M1 semantic NCU capacity evidence; consistency, not causality",
                                    ["Packed AWQ storage", "RTX 4080 L2", "Dense FP16 weight"], sizes, "MiB"), encoding="utf-8")
    written.append(name)

    decomposition = (("mlp_top_saving_ms", "MLP top level"),
                     ("self_attn_saving_ms", "Self-attention top level"),
                     ("norm_saving_ms", "Norm top level"),
                     ("final_stage_saving_ms", "Final stage"),
                     ("unexplained_residual_ms", "Unexplained residual"),
                     ("observed_decode_saving_ms", "Observed decode"))
    name = "FIG_COST_DECOMPOSITION.svg"
    (output / name).write_text(bars("BFULL native top-level timing decomposition",
                                    "Run-aligned categories; plotted medians need not sum exactly",
                                    [label for _, label in decomposition],
                                    [lookup(rows, "native_budget", "BFULL", metric) for metric, _ in decomposition],
                                    "ms"), encoding="utf-8")
    written.append(name)

    labels, values = [], []
    for budget in ("B8", "B16", "B24", "BFULL"):
        for metric, label in (("direct_up_saving_ms", "local up saving"),
                              ("observed_decode_saving_ms", "decode saving"),
                              ("self_attn_saving_ms", "self-attn saving")):
            labels.append(f"{budget} {label}")
            values.append(lookup(rows, "native_budget", budget, metric))
    name = "FIG_NATIVE_BUDGET.svg"
    (output / name).write_text(bars("Native residency: local and system timing", "Positive = faster under CUDA policy; negative = slower; seven-run medians",
                                    labels, values, "ms"), encoding="utf-8")
    written.append(name)

    labels, values = [], []
    for condition, local_metric in (("UP28", "direct_up_saving_ms"), ("GUD84", "direct_ffn_saving_ms")):
        for metric, label in ((local_metric, "local saving"), ("outside_ffn_residual_ms", "outside-FFN residual")):
            labels.append(f"{condition} {label}")
            values.append(lookup(rows, "operator_family", condition, metric))
    name = "FIG_OPERATOR_FAMILY.svg"
    (output / name).write_text(bars("Operator-family expansion", "Accepted native run-aligned medians; residual cause remains open",
                                    labels, values, "ms"), encoding="utf-8")
    written.append(name)

    sim = [(budget, lookup(rows, "simulator", budget, "window_speedup"))
           for budget in ("B8", "B16", "B24", "BFULL")]
    accepted = [(budget, value) for budget, value in sim if value is not None]
    sim_path = output / "FIG_SIM_BUDGET.svg"
    if accepted:
        sim_path.write_text(bars("Accepted simulator budget comparison", "Baseline cycles / candidate cycles; only independently accepted points",
                                 [x[0] for x in accepted], [x[1] for x in accepted], "×"), encoding="utf-8")
        written.append(sim_path.name)
    elif sim_path.exists():
        sim_path.unlink()
    return written


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=ROOT / OUT / "PAPER_RESULTS_CURRENT.json")
    parser.add_argument("--output", type=Path, default=ROOT / OUT / "figures")
    args = parser.parse_args()
    generate(json.loads(args.results.read_text(encoding="utf-8")), args.output)


if __name__ == "__main__":
    main()
