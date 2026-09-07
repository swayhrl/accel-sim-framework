#!/usr/bin/env python3
"""Emit the last-wins option resolution and a strict FAST64 mode diff.

Accel-Sim options are parsed sequentially, so a later occurrence in a config
overlays an inherited value.  This tool records that resolved identity without
attempting to reimplement semantic validation performed by the simulator.
"""
from __future__ import annotations

import argparse
import pathlib
import sys


def resolved(path: pathlib.Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or not line.startswith("-"):
            continue
        line = line.split("#", 1)[0].rstrip()
        fields = line.split(None, 1)
        values[fields[0]] = fields[1] if len(fields) == 2 else ""
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, type=pathlib.Path)
    parser.add_argument("--io", required=True, type=pathlib.Path)
    parser.add_argument("--oo", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    args = parser.parse_args()

    configs = {"BASE": resolved(args.base), "IO": resolved(args.io), "OO": resolved(args.oo)}
    keys = sorted(set().union(*configs.values()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    unrelated = []
    with args.output.open("w", encoding="utf-8") as out:
        out.write("option\tBASE\tIO\tOO\tclassification\n")
        for key in keys:
            vals = tuple(configs[mode].get(key, "<ABSENT>") for mode in ("BASE", "IO", "OO"))
            if vals[0] == vals[1] == vals[2]:
                classification = "COMMON"
            elif key == "-gpgpu_dtc_l1_mode" and vals == ("1", "2", "3"):
                classification = "REQUIRED_DTC_MODE_SELECTOR"
            else:
                classification = "UNRELATED_DIFFERENCE"
                unrelated.append((key, vals))
            out.write("\t".join((key, *vals, classification)) + "\n")
    if unrelated:
        for key, vals in unrelated:
            print(f"unrelated resolved difference: {key}: {vals}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
