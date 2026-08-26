#!/usr/bin/env python3
"""Create a deterministic format-compatible fallback for Pannotia fw_block.

The public suite names ``256_16384.gr`` but its original distribution is only
available inside a very large archive.  This helper deliberately does *not*
claim byte identity with that file.  It produces the same DIMACS shape
(256 vertices and 16,384 weighted, directed edges) so acquisition and tracer
validation can proceed while the exact archive remains outstanding.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    vertices = 256
    edges = 16_384
    # A full-period affine walk over the vertex-pair space, with self loops
    # skipped.  This is deterministic across Python versions and hosts.
    pairs = vertices * vertices
    value = 0x5A17
    chosen: set[tuple[int, int]] = set()
    lines = [
        "c GENERATED CANDIDATE: format-compatible fallback; not the upstream byte-identical input\n",
        f"p sp {vertices} {edges}\n",
    ]
    while len(chosen) < edges:
        value = (value * 1103515245 + 12345) & 0x7FFFFFFF
        index = value % pairs
        head, tail = divmod(index, vertices)
        if head == tail:
            continue
        edge = (head + 1, tail + 1)
        if edge in chosen:
            continue
        chosen.add(edge)
        weight = 1 + ((value >> 8) % 100)
        lines.append(f"a {edge[0]} {edge[1]} {weight}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
