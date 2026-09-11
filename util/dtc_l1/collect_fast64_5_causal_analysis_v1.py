#!/usr/bin/env python3
"""Fail-closed future-only FAST64.5 measured-feature/classification join.

The measured feature builder and causal classification are intentionally
separate: this program only joins a previously accepted feature package to a
researcher/source-backed, fully evidenced classification.  It neither derives
classes nor updates the stage ledger.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import shutil
import tempfile
from pathlib import Path

import validate_fast64_5_classification_v1 as classification

ROOT = Path(__file__).resolve().parents[2]
FEATURE_FILES = (
    "fast12_summary.csv", "fast12_stalls.csv", "fast12_live_misses.csv",
    "fast12_traffic.csv", "fast12_io_oo.csv",
    "fast64_5_emitted_column_provenance.tsv", "fast64_5_input_manifest.tsv",
    "fast64_5_feature_build_status.tsv",
)


def fail(message: str) -> None:
    raise RuntimeError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path, prefix: str) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    index = next((i for i, line in enumerate(lines) if line.startswith(prefix)), None)
    if index is None:
        fail(f"TSV_SCHEMA_INVALID={path}")
    return list(csv.DictReader(lines[index:], delimiter="\t"))


def require_states(ledger: Path) -> None:
    states = {row.get("stage"): row.get("current_state", row.get("status"))
              for row in read_tsv(ledger, "stage\t")}
    missing = [stage for stage in ("FAST64.3", "FAST64.4") if states.get(stage) != "PASS"]
    if missing:
        fail("FAST64_5_PRIOR_PASS_REQUIRED=" + ",".join(missing))


def require_features(directory: Path) -> None:
    if not directory.is_dir():
        fail("FAST64_5_FEATURE_DIRECTORY_MISSING")
    missing = [name for name in FEATURE_FILES if not (directory / name).is_file()]
    if missing:
        fail("FAST64_5_FEATURE_FILES_MISSING=" + ",".join(missing))
    status = {row.get("item"): row.get("value")
              for row in read_tsv(directory / "fast64_5_feature_build_status.tsv", "item\t")}
    if status.get("status") != "MEASURED_FEATURES_PENDING_RESEARCHER_CAUSAL_CLASSIFICATION":
        fail("FAST64_5_FEATURE_STATUS_INVALID")
    manifest = read_tsv(directory / "fast64_5_input_manifest.tsv", "workload\t")
    pairs = {(row.get("workload"), row.get("mode")) for row in manifest}
    roster = set(classification.ROSTER)
    if len(manifest) != 36 or pairs != {(workload, mode) for workload in roster for mode in ("BASE", "IO", "OO")}:
        fail("FAST64_5_FEATURE_MANIFEST_EXACT_MATRIX_REQUIRED")


def write_tsv(path: Path, headings: tuple[str, ...], rows: list[tuple[object, ...]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(headings)
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage-ledger", type=Path, required=True)
    parser.add_argument("--feature-dir", type=Path, required=True)
    parser.add_argument("--classification", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        fail("OUTPUT_DIRECTORY_ALREADY_EXISTS")
    require_states(args.stage_ledger)
    require_features(args.feature_dir)
    rows = classification.validate(args.classification, args.evidence_root)
    args.output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{args.output_dir.name}.tmp.", dir=args.output_dir.parent))
    try:
        for name in FEATURE_FILES:
            shutil.copy2(args.feature_dir / name, temporary / name)
        shutil.copy2(args.classification, temporary / "fast64_5_causal_classification.tsv")
        write_tsv(temporary / "fast64_5_causal_input_manifest.tsv",
                  ("workload", "primary_class", "secondary_classes", "evidence_paths", "classification_sha256"),
                  [(row["workload"], row["primary_class"], row["secondary_classes"], row["evidence_paths"], digest(args.classification)) for row in rows])
        write_tsv(temporary / "FAST64_5_CAUSAL_ANALYSIS_STATUS.tsv", ("item", "value"),
                  [("status", "CANDIDATE_REQUIRES_FAST64_5_HANDOFF"),
                   ("feature_dir_sha256", digest(args.feature_dir / "fast64_5_input_manifest.tsv")),
                   ("classification_sha256", digest(args.classification)),
                   ("stage_ledger_sha256", digest(args.stage_ledger)),
                   ("classification_policy", "SUPPLIED_EVIDENCE_BACKED_NO_AUTOMATIC_CAUSAL_INFERENCE"),
                   ("promotion", "NONE")])
        os.chmod(temporary, 0o555)
        os.replace(temporary, args.output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    print(f"FAST64_5_CAUSAL_ANALYSIS_V1_CANDIDATE_PASS output={args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
