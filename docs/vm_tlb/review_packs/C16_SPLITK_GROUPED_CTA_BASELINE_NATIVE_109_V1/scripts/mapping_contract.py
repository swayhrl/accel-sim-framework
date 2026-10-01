#!/usr/bin/env python3
"""Standard-library-only bijection, coverage, and frozen formula checks."""

import argparse
import hashlib
import json
import struct
from pathlib import Path

M, N, GROUP = 256, 49152, 128
M_TILES, N_TILES = 16, 384
KS, SPLITS = (3072, 4096), (8, 1)
MODES = {"ROW": 0, "GROUP_M16": 1}


def coords(linear, mode):
    row_m, row_n = linear // N_TILES, linear % N_TILES
    group_m, group_n = linear % M_TILES, linear // M_TILES
    m = row_m + mode * (group_m - row_m)
    n = row_n + mode * (group_n - row_n)
    return m, n


def input_sha(k):
    h = hashlib.sha256()
    for m in range(M):
        for col in range(k):
            h.update(struct.pack("<e", (1 + ((5 * m + 3 * col) % 7)) * (2.0 ** -10)))
    return h.hexdigest()


def run():
    expected = {(m, n) for m in range(M_TILES) for n in range(N_TILES)}
    rows = []
    for split in SPLITS:
        for name, mode in MODES.items():
            seen = [coords(i, mode) for i in range(M_TILES * N_TILES)]
            assert len(seen) == 6144 and len(set(seen)) == 6144 and set(seen) == expected
            inverse = {tile: i for i, tile in enumerate(seen)}
            distances = [inverse[(m + 1, n)] - inverse[(m, n)] for n in range(N_TILES) for m in range(M_TILES - 1)]
            expected_distance = N_TILES if name == "ROW" else 1
            assert set(distances) == {expected_distance}
            rows.append({"split": split, "mapping": name, "mode": mode,
                         "tiles": len(seen), "unique": len(set(seen)),
                         "same_ntile_adjacent_mtile_distance": expected_distance,
                         "coverage_pass": True})
    return {"status": "PASS", "fixed": {"M": M, "N": N, "m_tiles": M_TILES,
            "n_tiles": N_TILES, "K": list(KS), "split": list(SPLITS), "modes": MODES},
            "mapping_rows": rows, "input_sha256": {str(k): input_sha(k) for k in KS}}


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
