#!/usr/bin/env python3
"""Create deterministic source and delivery SHA closure after ingest/ledger/plot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ingest import OUT, ROOT


def main() -> None:
    output = ROOT / OUT
    table = json.loads((output / "PAPER_RESULTS_CURRENT.json").read_text(encoding="utf-8"))
    ledger = json.loads((output / "C16_E1_EVIDENCE_LEDGER.json").read_text(encoding="utf-8"))
    sources = {}
    for row in table["rows"]:
        if row["status"] == "ACCEPTED":
            key = row["source_path"]
            value = {"sha256": row["source_sha256"], "commit": row["source_commit"]}
            if key in sources and sources[key] != value:
                raise ValueError(f"inconsistent source identity: {key}")
            sources[key] = value
    for claim in ledger:
        key = claim["artifact_path"]
        value = {"sha256": claim["artifact_sha256"], "commit": claim["authoritative_commit"]}
        if key in sources and sources[key] != value:
            raise ValueError(f"inconsistent claim identity: {key}")
        sources[key] = value
    closure = {"schema": "C16_E1_PAPER_SOURCE_CLOSURE_V1",
               "authority_framework_head": table["authority_framework_head"],
               "source_count": len(sources), "sources": sources,
               "accepted_result_rows": sum(row["status"] == "ACCEPTED" for row in table["rows"]),
               "pending_result_rows": sum(row["status"] == "PENDING" for row in table["rows"]),
               "claim_count": len(ledger)}
    (output / "SOURCE_CLOSURE.json").write_text(json.dumps(closure, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    code = ROOT / "util/vm_tlb/c16/paper_result_ingest"
    files = [path for path in output.rglob("*") if path.is_file() and path.name != "SHA256SUMS"]
    files.extend(path for path in code.iterdir() if path.is_file() and path.suffix in (".py", ".json"))
    lines = []
    for path in sorted(files, key=lambda item: item.as_posix()):
        relative = path.relative_to(ROOT).as_posix()
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {relative}")
    (output / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
