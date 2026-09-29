#!/usr/bin/env python3
"""Standard-library-only frozen mapping, footprint, and formula checks."""

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

K, N, GROUP, N_TILES = 4096, 12288, 128, 96
MS, SPLITS = (1, 16, 32, 64), (8, 1)


def input_sha(m):
    h = hashlib.sha256()
    for row in range(m):
        for col in range(K):
            h.update(struct.pack("<e", (1 + ((5 * row + 3 * col) % 7)) * (2.0 ** -10)))
    return h.hexdigest()


def run():
    qweight = K * (N // 8) * 4
    qzeros = (K // GROUP) * (N // 8) * 4
    scales = (K // GROUP) * N * 2
    assert (qweight, qzeros, scales, qweight + qzeros + scales) == (25165824, 196608, 786432, 26148864)
    rows = []
    for m in MS:
        mt = math.ceil(m / 16)
        expected = {(mi, ni) for mi in range(mt) for ni in range(N_TILES)}
        seen = [(linear % mt, linear // mt) for linear in range(mt * N_TILES)]
        assert len(seen) == len(set(seen)) and set(seen) == expected
        for split in SPLITS:
            grid = mt * N_TILES * split
            scratch = split * m * N * 2
            reduction = math.ceil(m * N / 512) if split == 8 else 0
            rows.append({"M": m, "m_tiles": mt, "split": split, "gemm_grid": grid,
                         "scratch_bytes": scratch, "reduction_grid": reduction,
                         "coverage_pass": True})
    return {"status": "PASS", "version": "C16_GROUPED_RESIDUAL_SYNTH_V1",
            "fixed": {"K": K, "N": N, "group": GROUP, "M": list(MS), "split": list(SPLITS)},
            "weight_side_bytes": {"qweight": qweight, "qzeros": qzeros, "scales": scales,
                                  "total": qweight + qzeros + scales},
            "input_sha256": {str(m): input_sha(m) for m in MS}, "launch_rows": rows}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    text = json.dumps(run(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
