#!/usr/bin/env python3
"""Pure-CPU contract checks.  This module must never import Torch/CUDA."""

import argparse
import hashlib
import json
import struct
from pathlib import Path

M = 256
N = 49152
GROUP = 128
REPLICAS = 16
KS = (2560, 3072)
SPLITS = (8, 1)
STATES = {"SHARED": 0, "PER_MTILE": 15}
QWEIGHT_WORD = -324508640  # bit pattern 0xeca86420
QZERO_WORD = 2004318071    # bit pattern 0x77777777
SCALE = 2.0 ** -8


def tensor_bytes(k):
    return {
        "qweight": k * (N // 8) * 4,
        "qzeros": (k // GROUP) * (N // 8) * 4,
        "scales": (k // GROUP) * N * 2,
    }


def repeated_sha(word, count, chunk_elems=1 << 18):
    h = hashlib.sha256()
    while count:
        n = min(count, chunk_elems)
        h.update(word * n)
        count -= n
    return h.hexdigest()


def input_sha(k):
    h = hashlib.sha256()
    for m in range(M):
        for col in range(k):
            value = (1 + ((5 * m + 3 * col) % 7)) * (2.0 ** -10)
            h.update(struct.pack("<e", value))
    return h.hexdigest()


def contract():
    out = {"status": "PASS", "fixed": {"M": M, "N": N, "group": GROUP,
           "replicas": REPLICAS, "K": list(KS), "split": list(SPLITS),
           "states": STATES}, "points": []}
    qword = struct.pack("<i", QWEIGHT_WORD)
    zword = struct.pack("<i", QZERO_WORD)
    sword = struct.pack("<e", SCALE)
    assert [((QWEIGHT_WORD & 0xffffffff) >> (4 * i)) & 0xf for i in range(8)] == list(range(0, 16, 2))
    assert all((((QZERO_WORD & 0xffffffff) >> (4 * i)) & 0xf) == 7 for i in range(8))
    for k in KS:
        b = tensor_bytes(k)
        full = sum(b.values())
        assert k % GROUP == 0 and N % 128 == 0
        assert full in (65372160, 78446592)
        hashes = {
            "qweight": repeated_sha(qword, k * (N // 8)),
            "qzeros": repeated_sha(zword, (k // GROUP) * (N // 8)),
            "scales": repeated_sha(sword, (k // GROUP) * N),
        }
        for split in SPLITS:
            grid = (M // 16) * (N // 128) * split
            scratch = split * M * N * 2
            assert grid == (49152 if split == 8 else 6144)
            assert scratch == (201326592 if split == 8 else 25165824)
        shared_ids = [(m & STATES["SHARED"]) for m in range(16)]
        per_ids = [(m & STATES["PER_MTILE"]) for m in range(16)]
        assert shared_ids == [0] * 16 and per_ids == list(range(16))
        out["points"].append({
            "K": k,
            "per_replica_bytes": b,
            "weight_side_bytes_per_replica": full,
            "weight_side_bytes_all_replicas": full * REPLICAS,
            "semantic_sha256_per_replica": hashes,
            "input_sha256": input_sha(k),
        })
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = contract()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()

