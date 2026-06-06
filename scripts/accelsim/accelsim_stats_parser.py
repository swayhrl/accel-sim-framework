#!/usr/bin/env python3
"""Small conservative parser for Accel-Sim/GPGPU-Sim text logs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class StatOccurrence:
    key: str
    value: str
    unit: str
    line_no: int
    kernel_hint: str


_ASSIGN_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_./-]*)\s*(?:=|:)\s*(.+?)\s*$")
_SPACE_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_./-]*)\s+([-+]?[0-9][0-9.eE+-]*)(?:\s+|$)")
_NUMBER_RE = re.compile(r"[-+]?(?:\d+\.\d+|\d+|\.\d+)(?:[eE][-+]?\d+)?")


def clean_field(value: object) -> str:
    return str(value or "").replace("\r", "").replace("\n", "").strip()


def normalize_key(key: str) -> str:
    key = clean_field(key).lower()
    key = re.sub(r"[^a-z0-9]+", "_", key).strip("_")
    aliases = {
        "l2_total_cache_accesses": "l2_total_cache_accesses",
        "l2_total_cache_misses": "l2_total_cache_misses",
        "gpgpu_simulation_rate": "gpgpu_simulation_rate",
    }
    return aliases.get(key, key)


def split_value_unit(raw: str) -> tuple[str, str]:
    text = clean_field(raw)
    paren = re.search(r"\(([^)]*)\)", text)
    unit = paren.group(1).strip() if paren else ""
    number = _NUMBER_RE.search(text)
    value = number.group(0) if number else text.split()[0] if text else ""
    return value, unit


def numeric(value: str) -> float | None:
    match = _NUMBER_RE.search(clean_field(value))
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def parse_log(log_path: str | Path) -> list[StatOccurrence]:
    path = Path(clean_field(log_path))
    if not path.exists():
        return []
    occurrences: list[StatOccurrence] = []
    kernel_hint = "global"
    for line_no, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        low = line.lower()
        if "kernel" in low and ("launch" in low or "stream" in low or "trace" in low):
            kernel_hint = f"line_{line_no}"
        match = _ASSIGN_RE.match(line)
        if not match:
            match = _SPACE_RE.match(line)
        if not match:
            continue
        key = clean_field(match.group(1))
        value, unit = split_value_unit(match.group(2))
        if not key or not value:
            continue
        if len(key) > 96 or key.startswith("-"):
            continue
        occurrences.append(StatOccurrence(key=key, value=value, unit=unit, line_no=line_no, kernel_hint=kernel_hint))
    return occurrences


def select_by_mode(occurrences: Iterable[StatOccurrence], mode: str) -> list[tuple[StatOccurrence, int, int, str]]:
    by_key: dict[str, list[StatOccurrence]] = {}
    for occ in occurrences:
        by_key.setdefault(normalize_key(occ.key), []).append(occ)
    rows: list[tuple[StatOccurrence, int, int, str]] = []
    for norm_key, items in sorted(by_key.items()):
        if mode == "first":
            rows.append((items[0], len(items), 1, ""))
        elif mode == "last":
            rows.append((items[-1], len(items), len(items), ""))
        elif mode == "aggregate_sum":
            values = [numeric(i.value) for i in items]
            if values and all(v is not None for v in values):
                base = items[-1]
                summed = StatOccurrence(base.key, str(sum(v for v in values if v is not None)), base.unit, base.line_no, base.kernel_hint)
                rows.append((summed, len(items), len(items), "numeric_sum"))
            else:
                rows.append((items[-1], len(items), len(items), "non_numeric_not_summed"))
        elif mode == "per_kernel":
            for idx, item in enumerate(items, 1):
                rows.append((item, len(items), idx, "kernel_boundaries_best_effort"))
        else:
            raise ValueError(f"unknown stats mode: {mode}")
    return rows


def parse_selected_stats(log_path: str | Path, modes: Iterable[str]) -> list[dict[str, str]]:
    occurrences = parse_log(log_path)
    output: list[dict[str, str]] = []
    for mode in modes:
        for occ, count, selected, notes in select_by_mode(occurrences, mode):
            output.append({
                "stats_mode": mode,
                "stat_key": occ.key,
                "normalized_stat_key": normalize_key(occ.key),
                "stat_value": occ.value,
                "stat_unit": occ.unit,
                "occurrence_count": str(count),
                "selected_occurrence": str(selected),
                "kernel_hint": occ.kernel_hint if mode == "per_kernel" else "",
                "notes": notes,
            })
    return output


def first_stat(log_path: str | Path, normalized_key: str, mode: str = "last") -> str:
    for row in parse_selected_stats(log_path, [mode]):
        if row["normalized_stat_key"] == normalized_key:
            return row["stat_value"]
    return "NA"
