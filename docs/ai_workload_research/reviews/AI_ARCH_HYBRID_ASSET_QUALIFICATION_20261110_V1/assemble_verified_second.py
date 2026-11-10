#!/usr/bin/env python3
"""Assemble and SHA-256-check complete shard two while shard one repairs."""

from fetch_weight_ranges import ROOT, FILES, CHUNK_BYTES, assemble

NAME, TOTAL, SHA256 = FILES[1]
PREFIX_BYTES = 412360704

if __name__ == "__main__":
    parts = [ROOT / f"{NAME}.range.{start}-{min(start + CHUNK_BYTES, TOTAL) - 1}"
             for start in range(PREFIX_BYTES, TOTAL, CHUNK_BYTES)]
    for part in parts:
        expected = int(part.name.rsplit(".", 1)[1].split("-")[1]) - int(part.name.rsplit(".", 1)[1].split("-")[0]) + 1
        if not part.is_file() or part.stat().st_size != expected:
            raise RuntimeError(f"incomplete fixed range: {part.name}")
    assemble(NAME, TOTAL, SHA256, parts)
