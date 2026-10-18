#!/usr/bin/env python3
"""Fail closed when a candidate/high-cap pair differs beyond its cap value."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ALLOWED_METRIC_DIFFERENCES = {"DTC_L1_lower_outstanding_cap"}


def load(path: pathlib.Path) -> dict:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=pathlib.Path)
    parser.add_argument("--high", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    args = parser.parse_args()

    candidate = load(args.candidate)
    high = load(args.high)
    left = candidate["metrics"]
    right = high["metrics"]
    differing = []
    for key in sorted(set(left) | set(right)):
        a = left.get(key, "<ABSENT>")
        b = right.get(key, "<ABSENT>")
        if a != b:
            differing.append((key, a, b, key in ALLOWED_METRIC_DIFFERENCES))

    disallowed = [item for item in differing if not item[3]]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as out:
        out.write("field\tcandidate\thigh\tclassification\n")
        for key, a, b, allowed in differing:
            out.write(f"{key}\t{a}\t{b}\t{'EXPECTED_CONFIG_IDENTITY' if allowed else 'DIFFERENCE'}\n")
        if not differing:
            out.write("<none>\t<none>\t<none>\tEXACT_METRIC_MATCH\n")
    if disallowed:
        for key, a, b, _ in disallowed:
            print(f"non-binding comparison differs: {key}: {a!r} != {b!r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
