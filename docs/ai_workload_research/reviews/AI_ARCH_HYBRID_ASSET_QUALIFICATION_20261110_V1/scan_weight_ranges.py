#!/usr/bin/env python3
"""List only complete fixed ranges, excluding partial .tmp files."""

from fetch_weight_ranges import ROOT, FILES, CHUNK_BYTES

PREFIX_BYTES = {
    "model.safetensors-00001-of-00002.safetensors": 956821504,
    "model.safetensors-00002-of-00002.safetensors": 412360704,
}

for name, total, _ in FILES:
    spans = [(start, min(start + CHUNK_BYTES, total) - 1)
             for start in range(PREFIX_BYTES[name], total, CHUNK_BYTES)]
    missing = []
    for start, end in spans:
        path = ROOT / f"{name}.range.{start}-{end}"
        if not path.exists() or path.stat().st_size != end - start + 1:
            missing.append([start, end])
    print(name, "complete", len(spans) - len(missing), "expected", len(spans),
          "missing", missing, flush=True)
