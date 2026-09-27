#!/usr/bin/env python3
"""Bind curated claim wording to committed review-pack artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from ingest import OUT, ROOT, committed_source

FIELDS = ("claim_id", "exact_wording", "evidence_stage", "producer", "consumer",
          "authoritative_commit", "artifact_path", "artifact_sha256", "metric",
          "claim_strength", "independent_closure_status", "caveat", "paper_ready")
STRENGTHS = {"ESTABLISHED", "SUPPORTED_PARTIAL", "DIAGNOSTIC_ONLY", "UNESTABLISHED", "PENDING_B16"}


def build(root: Path, definitions: Path) -> list[dict]:
    raw = json.loads(definitions.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("claims source must be an array")
    result, seen = [], set()
    for item in raw:
        required = {"claim_id", "exact_wording", "evidence_stage", "producer", "consumer",
                    "artifact_path", "metric", "claim_strength", "independent_closure_status",
                    "caveat", "paper_ready"}
        if not isinstance(item, dict) or set(item) != required:
            raise ValueError("claim keys must match the ledger schema exactly")
        if item["claim_id"] in seen or item["claim_strength"] not in STRENGTHS or type(item["paper_ready"]) is not bool:
            raise ValueError("duplicate claim or invalid strength/readiness")
        seen.add(item["claim_id"])
        _, sha, commit = committed_source(root, Path(item["artifact_path"]))
        result.append({**item, "authoritative_commit": commit, "artifact_sha256": sha})
    return result


def write(rows: list[dict], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "C16_E1_EVIDENCE_LEDGER.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "C16_E1_EVIDENCE_LEDGER.tsv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    lines = ["# C16 E1 evidence ledger", "", "Generated from `CLAIMS.json` and committed review-pack artifacts. The JSON/TSV retain full SHA and provenance.", ""]
    for item in rows:
        lines.extend((f"## {item['claim_id']} · {item['claim_strength']}", "",
                      item["exact_wording"], "",
                      f"Evidence: `{item['evidence_stage']}`; `{item['artifact_path']}`; metric `{item['metric']}`.", "",
                      f"Closure: {item['independent_closure_status']}. Caveat: {item['caveat']}", "",
                      f"Paper ready: {'yes' if item['paper_ready'] else 'no'}. Commit: `{item['authoritative_commit']}`.", ""))
    (output / "C16_E1_EVIDENCE_LEDGER.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--claims", type=Path, default=Path(__file__).with_name("CLAIMS.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    write(build(root, args.claims), args.output or root / OUT)


if __name__ == "__main__":
    main()
