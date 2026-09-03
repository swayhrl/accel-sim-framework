#!/usr/bin/env python3
"""Python-3-compatible verifier for the canonical Parboil SpMV output format.

This implements the tolerance and binary layout in Parboil's
benchmarks/spmv/tools/compare-output: little-endian uint32 vector length,
followed by that many float32 values, with no trailing bytes.
"""

import argparse
import math
import struct
from pathlib import Path


def read_output(path):
    data = path.read_bytes()
    if len(data) < 4:
        raise ValueError("missing uint32 length")
    count = struct.unpack_from("<I", data)[0]
    expected_size = 4 + count * 4
    if len(data) != expected_size:
        raise ValueError(
            "size mismatch: header requires %d bytes, found %d" %
            (expected_size, len(data))
        )
    return struct.unpack_from("<%df" % count, data, 4)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("computed", type=Path)
    args = parser.parse_args()

    reference = read_output(args.reference)
    computed = read_output(args.computed)
    if len(reference) != len(computed):
        raise SystemExit("FAIL length mismatch")
    maximum = max((abs(value) for value in reference), default=0.0)
    absolute_tolerance = 1e-4 * maximum
    mismatches = []
    for index, (expected, observed) in enumerate(zip(reference, computed)):
        if not (math.isfinite(expected) and math.isfinite(observed)):
            mismatches.append((index, expected, observed))
        elif abs(expected - observed) > absolute_tolerance and \
                abs(expected - observed) >= 0.002 * abs(expected):
            mismatches.append((index, expected, observed))
    if mismatches:
        first = mismatches[0]
        raise SystemExit(
            "FAIL %d mismatches; first index=%d expected=%g observed=%g" %
            (len(mismatches), first[0], first[1], first[2])
        )
    print("PASS count=%d absolute_tolerance=%g" % (len(reference), absolute_tolerance))


if __name__ == "__main__":
    main()
