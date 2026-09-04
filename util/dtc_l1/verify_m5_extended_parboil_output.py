#!/usr/bin/env python3
"""Python-3 adapter for the selected legacy Parboil output checkers.

This preserves the source-defined comparison predicates in the clean Parboil
candidate recorded by M5-E1-002.  It does not replace those checkers with a
generic tolerance, and is intended only for the E1 output-smoke contract.
"""

import argparse
import struct
from pathlib import Path


PY2_CHECKER_WORKLOADS = {"bfs", "cutcp", "mri-q", "sad", "stencil"}
WORKLOADS = PY2_CHECKER_WORKLOADS | {"histo"}


class Mismatch(Exception):
    pass


def require(condition, message):
    if not condition:
        raise Mismatch(message)


def read_exact(handle, size):
    value = handle.read(size)
    require(len(value) == size, "Unexpected end of file")
    return value


def read_u16(handle):
    return struct.unpack("<H", read_exact(handle, 2))[0]


def read_u32(handle):
    return struct.unpack("<I", read_exact(handle, 4))[0]


def read_f32(handle):
    return struct.unpack("<f", read_exact(handle, 4))[0]


def require_eof(ref, computed):
    require(ref.read(1) == b"", "Reference has trailing data")
    require(computed.read(1) == b"", "Output has trailing data")


def check_bfs(reference, computed):
    with reference.open("rt", encoding="utf-8") as ref, \
            computed.open("rt", encoding="utf-8") as out:
        try:
            size = int(ref.readline())
        except ValueError as exc:
            raise Mismatch("Malformed BFS size") from exc
        try:
            expected_first = float(ref.readline())
            actual_first = float(out.readline())
        except ValueError as exc:
            raise Mismatch("Malformed BFS first cost") from exc
        require(expected_first == actual_first,
                "Computed node cost does not match the expected values")
        for _ in range(size):
            try:
                expected = [float(value) for value in ref.readline().split()]
                actual = [float(value) for value in out.readline().split()]
            except ValueError as exc:
                raise Mismatch("Malformed BFS float output") from exc
            require(expected == actual,
                    "Computed node cost does not match the expected values")


def check_cutcp(reference, computed):
    with reference.open("rb") as ref, computed.open("rb") as out:
        expected_abs = read_f32(ref)
        actual_abs = read_f32(out)
        # Exact source predicate: abs(ref-cmp)/ref <= 0.0025.
        require(abs(expected_abs - actual_abs) / expected_abs <= 0.0025,
                "Coulombic magnitude mismatch")
        size = read_u32(ref)
        require(size == read_u32(out), "CUTCP lattice size mismatch")
        for _ in range(2 * size):
            expected = read_f32(ref)
            actual = read_f32(out)
            # Exact source predicate: 0.005 * |cmp-ref| <= |ref|.
            require(0.005 * abs(actual - expected) <= abs(expected),
                    "CUTCP lattice point mismatch")
        require_eof(ref, out)


def check_histo(reference, computed):
    require(reference.read_bytes() == computed.read_bytes(),
            "histo output differs from reference")


def check_mri_q(reference, computed):
    with reference.open("rb") as ref, computed.open("rb") as out:
        size = read_u32(ref)
        require(size == read_u32(out), "Output data size does not match expected size")
        expected = [read_f32(ref) for _ in range(2 * size)]
        actual = [read_f32(out) for _ in range(2 * size)]
        absolute_tolerance = 1e-4 * max(abs(value) for value in expected)
        for wanted, observed in zip(expected, actual):
            difference = abs(wanted - observed)
            require(difference <= absolute_tolerance or
                    difference < 0.002 * abs(wanted),
                    "Reconstructed image does not match the expected image")
        require_eof(ref, out)


def check_sad(reference, computed):
    with reference.open("rb") as ref, computed.open("rb") as out:
        macroblocks = read_u32(ref)
        require(macroblocks == read_u32(out), "SAD macroblock count mismatch")
        expected_header = read_u32(ref)
        require(expected_header == read_u32(out), "SAD header mismatch")
        for _ in range(macroblocks):
            for _ in range(41):
                for _ in range(1089):
                    require(read_u16(ref) == read_u16(out), "Mismatched SAD value")
        require_eof(ref, out)


def check_stencil(reference, computed):
    # Preserve the original checker loop bounds, including its lx-bytes loop.
    ref_data = reference.read_bytes()
    out_data = computed.read_bytes()
    require(len(ref_data) >= 4 and len(out_data) >= 4,
            "Missing stencil output header")
    expected_length = struct.unpack("i", ref_data[:4])[0]
    actual_length = struct.unpack("i", out_data[:4])[0]
    require(expected_length == actual_length,
            "Reference and compare are different in size")
    expected = ref_data[4:]
    actual = out_data[4:]
    require(len(expected) == 4 * expected_length,
            "Reference: sanity check failed")
    require(len(actual) == 4 * actual_length,
            "Compare: sanity check failed")
    for offset in range(0, expected_length, 4):
        wanted = struct.unpack("f", expected[offset:offset + 4])[0]
        observed = struct.unpack("f", actual[offset:offset + 4])[0]
        difference = abs(wanted - observed)
        require(difference <= 0.001 or difference < 0.002 * abs(wanted),
                "Stencil float mismatch")


CHECKERS = {
    "bfs": check_bfs,
    "cutcp": check_cutcp,
    "histo": check_histo,
    "mri-q": check_mri_q,
    "sad": check_sad,
    "stencil": check_stencil,
}


def check(workload, reference, computed):
    try:
        CHECKERS[workload](reference, computed)
    except (OSError, UnicodeError, struct.error, ZeroDivisionError) as exc:
        raise Mismatch(str(exc)) from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workload", choices=sorted(WORKLOADS))
    parser.add_argument("reference", type=Path)
    parser.add_argument("computed", type=Path)
    args = parser.parse_args()
    try:
        check(args.workload, args.reference, args.computed)
    except Mismatch as exc:
        raise SystemExit("FAIL workload=%s: %s" % (args.workload, exc))
    print("PASS workload=%s source_checker_semantics=preserved" % args.workload)


if __name__ == "__main__":
    main()
