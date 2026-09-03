#!/usr/bin/env python3
"""Require the canonical PolyBench/GPU CPU-versus-GPU verdict to be zero.

The M5 PolyBench sources used for BICG, ATAX, GEMVER, MVT, SYRK, GESUMMV,
SYR2K, 2MM, and 2DConvolution print one final comparison count.  A simulator
exit status alone is insufficient evidence: this checker requires exactly one
source-defined verdict and rejects a nonzero count.
"""

import argparse
import re
from pathlib import Path


MISS_WORKLOADS = {"gemv"}
COMPARE_WORKLOADS = {
    "atax", "bicg", "mvt", "syrk", "gesu", "syr2k", "2mm", "conv2d",
}

MISS = re.compile(r"^\s*Number of misses:\s*(\d+)\s*$", re.MULTILINE)
COMPARE = re.compile(
    r"^\s*Non-Matching CPU-GPU Outputs Beyond Error Threshold of "
    r"[0-9.]+ Percent:\s*(\d+)\s*$",
    re.MULTILINE,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workload", choices=sorted(MISS_WORKLOADS | COMPARE_WORKLOADS))
    parser.add_argument("log", type=Path)
    args = parser.parse_args()

    text = args.log.read_text(encoding="utf-8", errors="replace")
    pattern = MISS if args.workload in MISS_WORKLOADS else COMPARE
    verdicts = [int(match.group(1)) for match in pattern.finditer(text)]
    if len(verdicts) != 1:
        raise SystemExit(
            "FAIL workload=%s expected exactly one source comparison verdict, found %d"
            % (args.workload, len(verdicts))
        )
    if verdicts[0] != 0:
        raise SystemExit(
            "FAIL workload=%s source comparison mismatches=%d"
            % (args.workload, verdicts[0])
        )
    print("PASS workload=%s source_comparison_mismatches=0" % args.workload)


if __name__ == "__main__":
    main()
