#!/usr/bin/env python3
"""Regression fixtures for the future-only FAST64.5 causal join."""
from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "util/dtc_l1/collect_fast64_5_causal_analysis_v1.py"
ROSTER = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree", "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")


def tsv(path: Path, fields: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


with tempfile.TemporaryDirectory() as raw:
    root = Path(raw); feature = root / "feature"; feature.mkdir()
    feature_headers = {
        "fast12_summary.csv": "workload,base_cycles\nfixture,1\n",
        "fast12_stalls.csv": "workload,pib_full_events\nfixture,1\n",
        "fast12_live_misses.csv": "workload,mode\nfixture,BASE\n",
        "fast12_traffic.csv": "workload,mode\nfixture,BASE\n",
        "fast12_io_oo.csv": "workload,mode\nfixture,IO\n",
    }
    for name, contents in feature_headers.items():
        (feature / name).write_text(contents, encoding="utf-8")
    provenance_rows = [(name, column, "fixture", "fixture", "identity", "fixture", "SOURCE_DEFINED")
                       for name, contents in feature_headers.items()
                       for column in contents.splitlines()[0].split(",")]
    with (feature / "fast64_5_emitted_column_provenance.tsv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("output_file", "output_column", "source_artifact", "source_metric_keys", "formula", "units_or_normalization", "missing_disposition"))
        writer.writerows(provenance_rows)
    tsv(feature / "fast64_5_input_manifest.tsv", ("workload", "mode"),
        [{"workload": workload, "mode": mode} for workload in ROSTER for mode in ("BASE", "IO", "OO")])
    tsv(feature / "fast64_5_feature_build_status.tsv", ("item", "value"), [{"item": "status", "value": "MEASURED_FEATURES_PENDING_RESEARCHER_CAUSAL_CLASSIFICATION"}])
    evidence = root / "evidence.txt"; evidence.write_text("source-backed fixture\n", encoding="utf-8")
    classification = root / "classification.tsv"
    fields = ("workload", "primary_class", "secondary_classes", "evidence_paths", "evidence_backed_rationale", "validator_status")
    tsv(classification, fields, [dict(zip(fields, (workload, "LOW_STRUCTURAL_PRESSURE", "", "evidence.txt", "fixture evidence", "READY"))) for workload in ROSTER])
    ledger = root / "ledger.tsv"; tsv(ledger, ("stage", "current_state"), [{"stage": "FAST64.3", "current_state": "PASS"}, {"stage": "FAST64.4", "current_state": "PASS"}])
    command = [sys.executable, str(TOOL), "--stage-ledger", str(ledger), "--feature-dir", str(feature), "--classification", str(classification), "--evidence-root", str(root), "--output-dir", str(root / "out")]
    good = subprocess.run(command, text=True, capture_output=True); assert good.returncode == 0, good.stderr
    assert (root / "out" / "FAST64_5_CAUSAL_ANALYSIS_STATUS.tsv").is_file()
    tsv(ledger, ("stage", "current_state"), [{"stage": "FAST64.3", "current_state": "PASS"}, {"stage": "FAST64.4", "current_state": "ACTIVE"}])
    bad = subprocess.run(command[:-1] + [str(root / "bad")], text=True, capture_output=True)
    assert bad.returncode != 0 and "PRIOR_PASS_REQUIRED" in bad.stderr
print("FAST64_5_CAUSAL_ANALYSIS_V1_REGRESSION_PASS")
