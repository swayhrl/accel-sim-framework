#!/usr/bin/env python3
"""Repair one failed 128 MiB fixed range using four bounded 32 MiB ranges."""

import os
from pathlib import Path
from fetch_weight_ranges import fetch_chunk

NAME = "model.safetensors-00001-of-00002.safetensors"
START = 3104305152
END = 3238522879

if __name__ == "__main__":
    pieces = []
    step = 32 * 1024 * 1024
    for start in range(START, END + 1, step):
        end = min(start + step - 1, END)
        pieces.append(fetch_chunk(NAME, start, end))
    destination = pieces[0].parent / f"{NAME}.range.{START}-{END}"
    temporary = Path(str(destination) + ".repairing")
    with temporary.open("wb") as output:
        for piece in pieces:
            with piece.open("rb") as source:
                while block := source.read(4 * 1024 * 1024):
                    output.write(block)
    if temporary.stat().st_size != END - START + 1:
        raise RuntimeError("repaired range has wrong byte count")
    os.replace(temporary, destination)
    for piece in pieces:
        piece.unlink()
    print(f"REPAIRED {destination.name} {destination.stat().st_size}", flush=True)
