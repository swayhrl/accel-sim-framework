#!/usr/bin/env python3
"""Prepare the sole source-correct M5 GESUMMV capture copy.

The pinned PolyBench CUDA source initializes CPU accumulators but copies
uninitialized host ``tmp``/``y`` buffers to additive GPU accumulators.  This
leaves the frozen checkout untouched and emits an exact checked copy with the
CPU-equivalent zero initialization.
"""
import hashlib, json, sys
from pathlib import Path

SOURCE_SHA256 = "717c2bc6161a1d9b478282dabe994e0184821ee100996a898aba688302f384a4"
OLD_TMP = "cudaMemcpy(tmp_gpu, tmp, sizeof(DATA_TYPE) * N, cudaMemcpyHostToDevice);"
OLD_Y = "cudaMemcpy(y_gpu, y, sizeof(DATA_TYPE) * N, cudaMemcpyHostToDevice);"
NEW_TMP = "cudaMemset(tmp_gpu, 0, sizeof(DATA_TYPE) * N);"
NEW_Y = "cudaMemset(y_gpu, 0, sizeof(DATA_TYPE) * N);"

def digest(data): return hashlib.sha256(data).hexdigest()

def repair(text):
    if text.count(OLD_TMP) != 1 or text.count(OLD_Y) != 1:
        raise RuntimeError("unexpected GESUMMV accumulator-copy source shape")
    out = text.replace(OLD_TMP, NEW_TMP).replace(OLD_Y, NEW_Y)
    if OLD_TMP in out or OLD_Y in out or out.count(NEW_TMP) != 1 or out.count(NEW_Y) != 1:
        raise RuntimeError("GESUMMV accumulator repair did not apply exactly once")
    return out

def main(argv):
    if len(argv) != 4:
        raise SystemExit("usage: prepare_m5_gesummv_source.py <source> <copy> <provenance-json>")
    source, output, provenance = map(Path, argv[1:])
    raw = source.read_bytes()
    if digest(raw) != SOURCE_SHA256:
        raise RuntimeError("wrong frozen GESUMMV source identity")
    fixed = repair(raw.decode()).encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(fixed)
    provenance.write_text(json.dumps({
        "kind": "GESUMMV_ZERO_DEVICE_ACCUMULATORS",
        "rationale": "CPU initializes tmp/y to zero before additive loops; CUDA kernel is additive",
        "original_source_sha256": digest(raw),
        "prepared_source_sha256": digest(fixed),
        "replacements": {OLD_TMP: NEW_TMP, OLD_Y: NEW_Y},
    }, sort_keys=True, indent=2) + "\n")

if __name__ == "__main__": main(sys.argv)
