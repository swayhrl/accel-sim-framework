#!/usr/bin/env python3
"""Read-only ordered pre-existing-stat audit for final Lane-D compact rows."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import re
import sys


SCHEMA = "POST_FAST64_OBSERVER_ORDERED_STAT_AUDIT_V1"
CLASSIFICATION = "POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT"
STAT = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*) = (.+)$")


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        result = list(csv.DictReader(handle, delimiter="\t"))
    if not result:
        raise ValueError(f"empty TSV: {path}")
    return result


def sequence(path: pathlib.Path, keys: set[str]) -> tuple[bytes, int]:
    selected: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = STAT.match(line)
        if match and match.group(1) in keys:
            selected.append(match.group(1) + "\t" + match.group(2) + "\n")
    encoded = "".join(selected).encode()
    return encoded, len(selected)


def write(path: pathlib.Path, data: list[dict[str, str]], overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise ValueError(f"refusing to overwrite: {path}")
    mode = "w" if overwrite else "x"
    with path.open(mode, encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compact-dir", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        compact: list[dict[str, str]] = []
        for path in sorted(args.compact_dir.glob("*.tsv")):
            rows = read_tsv(path)
            if len(rows) != 1:
                raise ValueError(f"compact row must be singular: {path}")
            compact.append(rows[0])
        if len(compact) != 30:
            raise ValueError(f"expected 30 compact rows, found {len(compact)}")
        output: list[dict[str, str]] = []
        for row in compact:
            if row["classification"] != CLASSIFICATION:
                raise ValueError("invalid compact classification")
            summary_path = pathlib.Path(row["accepted_summary"])
            accepted = json.loads(summary_path.read_text(encoding="utf-8"))
            metrics = accepted.get("metrics")
            artifacts = accepted.get("external_artifacts")
            provenance = accepted.get("provenance")
            if not isinstance(metrics, dict) or not isinstance(artifacts, dict) or not isinstance(provenance, dict):
                raise ValueError(f"invalid accepted summary: {summary_path}")
            source = pathlib.Path(provenance["source_log"])
            expected_source_sha = artifacts["simulator_stdout_sha256"]
            if not source.is_file():
                raise ValueError(f"accepted source log unavailable: {source}")
            source_sha = sha256(source)
            if source_sha != expected_source_sha:
                raise ValueError(f"accepted source log hash mismatch: {source}")
            observer = pathlib.Path(row["raw_run_directory"]) / "simulator.stdout"
            if not observer.is_file():
                raise ValueError(f"terminal observer stdout unavailable: {observer}")
            source_seq, source_count = sequence(source, set(metrics))
            observer_seq, observer_count = sequence(observer, set(metrics))
            if source_seq != observer_seq:
                raise ValueError(f"ordered pre-existing stat sequence mismatch: {row['raw_run_directory']}")
            source_seq_sha = hashlib.sha256(source_seq).hexdigest()
            observer_seq_sha = hashlib.sha256(observer_seq).hexdigest()
            output.append({
                "schema": SCHEMA,
                "classification": CLASSIFICATION,
                "wave": row["wave"],
                "workload": row["workload"],
                "mode": row["mode"],
                "source_row_kind": (
                    "D3B_EXACT_REUSE"
                    if row["raw_run_directory"].endswith("/btree_oo_on")
                    else "NEW_DIAGNOSTIC_RUN"
                ),
                "accepted_summary": str(summary_path),
                "accepted_summary_sha256": row["accepted_summary_sha256"],
                "accepted_source_log": str(source),
                "accepted_source_log_sha256": source_sha,
                "observer_terminal_log": str(observer),
                "observer_terminal_log_sha256": sha256(observer),
                "preexisting_metric_key_count": str(len(metrics)),
                "accepted_ordered_selected_stat_count": str(source_count),
                "observer_ordered_selected_stat_count": str(observer_count),
                "accepted_ordered_stat_sequence_sha256": source_seq_sha,
                "observer_ordered_stat_sequence_sha256": observer_seq_sha,
                "ordered_preexisting_stat_sequence_exact": "true",
            })
        output.sort(key=lambda r: (r["wave"], r["workload"], r["mode"]))
        write(args.output, output, args.overwrite)
        print("POST_FAST64_OBSERVER_ORDERED_STAT_AUDIT_PASS\trows=30")
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"POST_FAST64_OBSERVER_ORDERED_STAT_AUDIT_ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
