#!/usr/bin/env python3
"""Pure-CPU frozen-target and representation-byte tests."""

import hashlib
import json
import struct

TARGETS = {"discovery": (256, 4096, 49152), "validation": (256, 3072, 49152)}


def input_sha(m, k):
    h = hashlib.sha256()
    for row in range(m):
        for col in range(k):
            h.update(struct.pack("<e", (1 + ((5 * row + 3 * col) % 7)) * 2**-10))
    return h.hexdigest()


def main():
    rows = []
    for name, (m, k, n) in TARGETS.items():
        qweight = k * (n // 8) * 4
        qzeros = (k // 128) * (n // 8) * 4
        scales = (k // 128) * n * 2
        expanded = k * n * 2
        rows.append({"target": name, "M": m, "K": k, "N": n,
                     "gemm_grid": (m // 16) * (n // 128), "block": [32, 2, 1],
                     "compressed_weight_bytes": qweight + qzeros + scales,
                     "expanded_weight_bytes": expanded,
                     "expansion_ratio": expanded / (qweight + qzeros + scales),
                     "input_sha256": input_sha(m, k)})
    assert rows[0]["gemm_grid"] == rows[1]["gemm_grid"] == 6144
    assert rows[0]["expanded_weight_bytes"] == 402653184
    assert rows[1]["expanded_weight_bytes"] == 301989888
    print(json.dumps({"status": "PASS", "targets": rows}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
