#!/usr/bin/env python3
"""Reconstruct a source-addressed 2D Base structural companion without rerun.

The historical V1 collector computes valid structural counters from a temporary
strict-summary file before atomically publishing that summary.  Its counters
and summary digest remain useful, but its ``source_summary`` pathname names the
now-removed temporary file.  This tool preserves V1 and publishes a distinct
V2 companion only when the immutable final summary has the exact same digest
that V1 recorded.  It never runs a simulator or modifies an existing result.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "docs/dtc_l1/fast64/generated/fast64_3_tag_identity_repair_v2"
RUN = Path("/workspace/fast64-stage3-tag-identity-repair-v2/fast64_3_2DConvolution_base_core6587238c_a1_v1")
SUMMARY = GENERATED / "fast64_3_2DConvolution_base_core6587238c_a1_v1.json"
V1 = GENERATED / "FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V1.json"
V2 = GENERATED / "FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V2.json"
EXTRACTOR = ROOT / "util/dtc_l1/extract_fast64_3_base_structural_metrics_v1.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if V2.exists():
        raise RuntimeError("FAST64_3_2D_STRUCTURAL_V2_ALREADY_EXISTS")
    if not SUMMARY.is_file() or not V1.is_file():
        raise RuntimeError("FAST64_3_2D_STRUCTURAL_V2_REQUIRES_V1_AND_FINAL_SUMMARY")
    if not EXTRACTOR.is_file():
        raise RuntimeError("FAST64_3_2D_STRUCTURAL_V2_EXTRACTOR_MISSING")
    v1 = json.loads(V1.read_text(encoding="utf-8"))
    if (v1.get("schema") != "FAST64_3_BASE_STRUCTURAL_METRICS_V1"
            or v1.get("source_summary_sha256") != digest(SUMMARY)):
        raise RuntimeError("FAST64_3_2D_STRUCTURAL_V1_DIGEST_DOES_NOT_BIND_FINAL_SUMMARY")
    perf = sorted(RUN.glob("perf_counter_*.csv.gz"))
    if len(perf) != 1:
        raise RuntimeError("FAST64_3_2D_STRUCTURAL_V2_EXPECTS_ONE_PERF_STREAM")
    fd, temporary_name = tempfile.mkstemp(prefix=f".{V2.name}.tmp.", dir=GENERATED)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        subprocess.run(("python3", str(EXTRACTOR), "--summary", str(SUMMARY),
                        "--perf", str(perf[0]), "--output", str(temporary)), check=True)
        rebuilt = json.loads(temporary.read_text(encoding="utf-8"))
        if (rebuilt.get("schema") != "FAST64_3_BASE_STRUCTURAL_METRICS_V1"
                or rebuilt.get("source_summary") != str(SUMMARY)
                or rebuilt.get("source_summary_sha256") != digest(SUMMARY)
                or rebuilt.get("source_perf") != str(perf[0])
                or rebuilt.get("source_perf_sha256") != digest(perf[0])):
            raise RuntimeError("FAST64_3_2D_STRUCTURAL_V2_REBUILD_PROVENANCE_MISMATCH")
        os.chmod(temporary, 0o444)
        os.link(temporary, V2)
    finally:
        temporary.unlink(missing_ok=True)
    print("FAST64_3_2D_TAG_IDENTITY_STRUCTURAL_V2_PASS output=" + str(V2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
