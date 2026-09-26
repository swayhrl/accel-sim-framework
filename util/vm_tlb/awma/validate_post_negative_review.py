#!/usr/bin/env python3
"""Validate scientific and hash closure of the post-negative review pack."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


REPO = Path("/root/workspace/accel-sim-framework-awma-post-negative-problem-pivot-v1")
PACK = REPO / "docs/vm_tlb/review_packs/AWMA_POST_NEGATIVE_PROBLEM_PIVOT_V1"
REQUIRED = {
    "README.md", "POST_NEGATIVE_EVIDENCE_INDEX.tsv", "RULED_OUT_SPACE.md",
    "CANDIDATE_SCREEN.tsv", "CLOSEST_WORK_MAP.md", "PROBLEM_CARD_1.md",
    "CONTEXT_DIAGNOSTIC_PREREGISTRATION.md", "CONTEXT_PREFIX_DIAGNOSTIC.tsv",
    "CONTEXT_MATCHED_PAIR_RESULTS.tsv", "CONTEXT_CORRELATION_SUMMARY.tsv",
    "CONTEXT_DIAGNOSTIC_RECEIPT.json", "CONTEXT_DIAGNOSTIC_DECISION.md",
    "FINAL_CANDIDATE_DECISION.tsv", "FINAL_DECISION.md", "RAW_DATA_INDEX.tsv", "SHA256SUMS",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tsv(name: str) -> list[dict[str, str]]:
    with (PACK / name).open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def main() -> int:
    errors = []
    existing = {path.name for path in PACK.iterdir() if path.is_file()}
    if REQUIRED - existing:
        errors.append(f"missing: {sorted(REQUIRED-existing)}")
    if "NEW_NATIVE_EVIDENCE_REQUEST.md" in existing:
        errors.append("unexpected Native request")
    if any(PACK.glob("PROBLEM_CARD_2.md")):
        errors.append("more than one problem card")
    if "AWMA_POST_NEGATIVE_NO_NEW_PROBLEM_V1" not in (PACK / "FINAL_DECISION.md").read_text():
        errors.append("final status missing")
    candidates = tsv("CANDIDATE_SCREEN.tsv")
    if len(candidates) != 3 or sum(row["phase1_status"] == "CANDIDATE_DIAGNOSTIC_SUPPORTED" for row in candidates) != 1:
        errors.append("candidate screen shape mismatch")
    final = tsv("FINAL_CANDIDATE_DECISION.tsv")
    if len(final) != 3 or any(row["prototype_authorized"] != "NO" for row in final):
        errors.append("final candidate gate mismatch")
    receipt = json.loads((PACK / "CONTEXT_DIAGNOSTIC_RECEIPT.json").read_text())
    if receipt.get("decision") != "REJECT_NO_LOCALIZED_CAUSE" or receipt.get("falsifying_pairs") != ["P8_P16_PRIMARY"]:
        errors.append("context diagnostic decision mismatch")
    if receipt.get("new_simulation_runs") != 0 or receipt.get("new_native_runs") != 0:
        errors.append("unexpected new run")
    pairs = tsv("CONTEXT_MATCHED_PAIR_RESULTS.tsv")
    p8p16 = next((row for row in pairs if row["contrast"] == "P8_P16_PRIMARY"), None)
    if not p8p16 or p8p16["falsifies_localized_state_hypothesis"] != "True":
        errors.append("P8/P16 falsifier missing")

    raw = tsv("RAW_DATA_INDEX.tsv")
    for row in raw:
        artifact = row["artifact"]
        if artifact.startswith("git:"):
            _, commit, path = artifact.split(":", 2)
            data = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=REPO)
        else:
            path = Path(artifact)
            if not path.is_file():
                errors.append(f"missing raw: {artifact}"); continue
            data = path.read_bytes()
        if len(data) != int(row["bytes"]) or sha(data) != row["sha256"]:
            errors.append(f"raw mismatch: {artifact}")
    manifest_names = []
    for line in (PACK / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1); manifest_names.append(name)
        path = PACK / name
        if not path.is_file() or sha(path.read_bytes()) != expected:
            errors.append(f"manifest mismatch: {name}")
    expected_names = sorted(path.name for path in PACK.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    if sorted(manifest_names) != expected_names:
        errors.append("manifest coverage mismatch")
    print(f"required={len(REQUIRED)} candidates={len(candidates)} final={len(final)} raw={len(raw)} errors={len(errors)}")
    for error in errors: print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
