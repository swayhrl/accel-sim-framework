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
    for name in ("fast12_summary.csv", "fast12_stalls.csv", "fast12_live_misses.csv", "fast12_traffic.csv", "fast12_io_oo.csv", "fast64_5_emitted_column_provenance.tsv"):
        (feature / name).write_text("fixture\n", encoding="utf-8")
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
