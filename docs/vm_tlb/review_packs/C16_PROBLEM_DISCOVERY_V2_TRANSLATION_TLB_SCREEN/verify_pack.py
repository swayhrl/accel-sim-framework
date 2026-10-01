#!/usr/bin/env python3
"""Validate the C16 CPU-only translation screen and deterministic rerun."""

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

PACK = Path(__file__).resolve().parent
GENERATED = ("C16_VIRTUAL_PAGE_PROXY.tsv", "PAGE_WORKING_SET_CURVES.tsv", "SOURCE_SHARD_SELECTION.tsv")
REQUIRED = (
    "README.md", "GPU_TRANSLATION_LITERATURE_TIMELINE.md", "LITERATURE_EVIDENCE_MATRIX.tsv",
    "AI_TRANSLATION_SPECIALNESS.tsv", "C16_VIRTUAL_PAGE_PROXY.tsv", "PAGE_WORKING_SET_CURVES.tsv",
    "SOURCE_SHARD_SELECTION.tsv", "MOE_PAGE_BEHAVIOR.tsv", "SEGMENTABILITY_STATIC_SCREEN.tsv",
    "TRANSLATION_HEADROOM_STATUS.md", "TOP_TRANSLATION_PROBLEMS.md", "FINAL_DECISION.json",
    "c16_translation_proxy.py", "verify_pack.py",
)


def rows(name):
    with (PACK / name).open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def expected_checksums():
    return {path.name: checksum(path) for path in PACK.iterdir()
            if path.is_file() and path.name != "SHA256SUMS"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rerun", action="store_true")
    parser.add_argument("--write-checksums", action="store_true")
    args = parser.parse_args()
    for name in REQUIRED:
        assert (PACK / name).is_file(), name
    decision = json.loads((PACK / "FINAL_DECISION.json").read_text())
    assert decision["decision"] == "NO_C16_TRANSLATION_PROBLEM_QUALIFIED_YET"
    assert decision["translation_time_headroom"] == "TRANSLATION_TIME_HEADROOM_UNKNOWN"
    assert decision["qualified_problem_count"] == 0 and not decision["future_109_contract_generated"]
    proxy = rows("C16_VIRTUAL_PAGE_PROXY.tsv")
    curves = rows("PAGE_WORKING_SET_CURVES.tsv")
    selected = rows("SOURCE_SHARD_SELECTION.tsv")
    papers = rows("LITERATURE_EVIDENCE_MATRIX.tsv")
    assert len(proxy) == 12 and len(curves) == 48 and len(selected) == 4
    assert len(papers) >= 11
    malformed = [row["paper"] for row in papers if any(value is None for value in row.values())]
    assert not malformed, f"malformed paper TSV rows: {malformed}"
    assert len(rows("AI_TRANSLATION_SPECIALNESS.tsv")) == 6
    assert len(rows("MOE_PAGE_BEHAVIOR.tsv")) == 3
    assert len(rows("SEGMENTABILITY_STATIC_SCREEN.tsv")) == 16
    assert {row["model"] for row in selected} == {"Q30", "DEEPSEEK", "OLMOE", "QWEN25_AWQ"}
    for model in {row["model"] for row in proxy}:
        group = sorted((row for row in proxy if row["model"] == model), key=lambda row: int(row["page_bytes"]))
        assert [int(row["page_bytes"]) for row in group] == [4096, 65536, 2097152]
        assert len({row["analyzed_lane_refs"] for row in group}) == 1
        assert int(group[0]["unique_pages"]) >= int(group[1]["unique_pages"]) >= int(group[2]["unique_pages"])
        if model == "QWEN25_AWQ":
            assert all(row["measurement_status"] == "UNMAPPED_OBJECT_VA_PROXY" for row in group)
            assert all(int(row["mapped_weight_lane_refs"]) == 0 for row in group)
        else:
            assert all(row["measurement_status"] == "MAPPED_WEIGHT_VA_PROXY" for row in group)
            assert all(int(row["mapped_weight_lane_refs"]) > 0 for row in group)
    if args.rerun:
        with tempfile.TemporaryDirectory(prefix="c16_translation_rerun_") as temporary:
            subprocess.run([sys.executable, str(PACK / "c16_translation_proxy.py"), "--output", temporary], check=True)
            for name in GENERATED:
                assert (PACK / name).read_bytes() == (Path(temporary) / name).read_bytes(), name
    if args.write_checksums:
        expected = expected_checksums()
        (PACK / "SHA256SUMS").write_text("".join(f"{digest}  {name}\n" for name, digest in sorted(expected.items())))
    recorded = {}
    for line in (PACK / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        recorded[name] = digest
    assert recorded == expected_checksums(), "SHA256SUMS mismatch"
    print("PASS: required files, JSON, TSV schemas/counts, page-size monotonicity, scope, SHA256SUMS" + (", deterministic rerun" if args.rerun else ""))


if __name__ == "__main__":
    main()
