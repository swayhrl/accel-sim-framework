#!/usr/bin/env python3
"""Repair three observed failed fixed ranges with bounded 32 MiB subranges."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path

from fetch_weight_ranges import fetch_chunk

JOBS = (
    ("model.safetensors-00001-of-00002.safetensors", 2567434240, 2701651967),
    ("model.safetensors-00001-of-00002.safetensors", 4983353344, 5117571071),
    ("model.safetensors-00002-of-00002.safetensors", 1486102528, 1620320255),
)


def repair(name: str, start: int, end: int) -> None:
    pieces = []
    step = 32 * 1024 * 1024
    for sub_start in range(start, end + 1, step):
        sub_end = min(sub_start + step - 1, end)
        pieces.append(fetch_chunk(name, sub_start, sub_end))
    destination = pieces[0].parent / f"{name}.range.{start}-{end}"
    temporary = Path(str(destination) + ".repairing")
    with temporary.open("wb") as output:
        for piece in pieces:
            with piece.open("rb") as source:
                while block := source.read(4 * 1024 * 1024):
                    output.write(block)
    if temporary.stat().st_size != end - start + 1:
        raise RuntimeError(f"wrong repaired size: {destination.name}")
    os.replace(temporary, destination)
    for piece in pieces:
        piece.unlink()
    print(f"REPAIRED {destination.name} {destination.stat().st_size}", flush=True)


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(repair, *job) for job in JOBS]
        for future in as_completed(futures):
            future.result()
