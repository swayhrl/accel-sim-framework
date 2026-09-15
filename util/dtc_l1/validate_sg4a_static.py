#!/usr/bin/env python3
"""Strict, simulation-free SG4A configuration gate."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


REQUIRED = {
    "-gpgpu_dtc_l1_logical_sets": "160",
    "-gpgpu_dtc_l1_logical_ways": "4",
    "-gpgpu_dtc_l1_physical_lines": "640",
    "-gpgpu_dtc_l1_io_pib_entries": "256",
    "-gpgpu_dtc_l1_oo_pib_entries": "128",
    "-gpgpu_dtc_l1_tag_banks": "4",
    "-gpgpu_dtc_l1_lower_outstanding_cap": "8192",
}


def options(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text().splitlines()[1:]:
        fields = line.split("\t")
        if len(fields) != 3:
            raise ValueError(f"malformed resolved row in {path}: {line!r}")
        key, value, _ = fields
        if key in result:
            raise ValueError(f"duplicate option {key} in {path}")
        result[key] = value
    return result


def config_options(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or not line.startswith("-"):
            continue
        key, value, *rest = line.split()
        if rest and not rest[0].startswith("#"):
            raise ValueError(f"unexpected config syntax in {path}: {raw!r}")
        result[key] = value
    return result


def core_object(core_repo: Path, commit: str, source_path: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(core_repo), "rev-parse", f"{commit}:{source_path}"],
        text=True,
    ).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--core-repo", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    sg4a = repo / "docs/dtc_l1/iscas2027/granularity/sg4a"
    modes = {"IO": "2", "OO": "3"}
    for mode, mode_value in modes.items():
        overlay = sg4a / "config" / f"SG4A_LOGICAL80_{mode}_OVERLAY.config"
        overlay_options = config_options(overlay)
        if overlay_options != {"-gpgpu_dtc_l1_logical_sets": "160"}:
            raise AssertionError(f"{overlay}: overlay must contain only logical_sets=160")
        resolved = options(sg4a / f"SG4A_LOGICAL80_{mode}_RESOLVED_CONFIG.tsv")
        for key, expected in REQUIRED.items():
            if resolved.get(key) != expected:
                raise AssertionError(f"{mode} {key}: {resolved.get(key)!r} != {expected!r}")
        if resolved.get("-gpgpu_dtc_l1_mode") != mode_value:
            raise AssertionError(f"{mode}: wrong DTC mode")
        parent = options(sg4a / f"SG4A_LOGICAL16_{mode}_RESOLVED_CONFIG.tsv")
        changed = {key for key in set(parent) | set(resolved)
                   if parent.get(key) != resolved.get(key)}
        if changed != {"-gpgpu_dtc_l1_logical_sets"}:
            raise AssertionError(f"{mode}: resolved/parent delta is {sorted(changed)!r}")
    for point in ("32", "64"):
        for mode in modes:
            baseline = config_options(repo / "configs/dtc_l1/fast64" / f"FAST64_{mode}.config")
            candidate = config_options(repo / "configs/dtc_l1/fast64/sensitivity_frozen_v2" /
                                       f"logical_{point}" / f"FAST64_SENS_LOGICAL_{point}KB_{mode}.config")
            changed = {key for key in set(baseline) | set(candidate)
                       if baseline.get(key) != candidate.get(key)}
            if changed != {"-gpgpu_dtc_l1_logical_sets"}:
                raise AssertionError(f"logical {point} {mode}: delta is {sorted(changed)!r}")
    commit = "95ccdb7a056f2d53f740d90869785cac6d4ee0f5"
    expected = {
        "src/gpgpu-sim/gpu-sim.cc": "fca511ee16016ad230b37a021c1ca084d3d19e28",
        "src/gpgpu-sim/dtc-l1-common.h": "adf8a0ecc8ea53f26bc8984bd85d53c25514f736",
    }
    for source_path, object_id in expected.items():
        if core_object(args.core_repo, commit, source_path) != object_id:
            raise AssertionError(f"unexpected Core95 object for {source_path}")
    print("PASS SG4A static configuration isolation and Core95 geometry proof")


if __name__ == "__main__":
    main()
