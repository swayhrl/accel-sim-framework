#!/usr/bin/env python3
"""Regression: Stage5 validator accepts supplied evidence, never invents it."""
from __future__ import annotations
import csv, subprocess, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "util/dtc_l1/validate_fast64_5_classification_v1.py"
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "class.tsv"
    fields = ("workload", "primary_class", "secondary_classes", "evidence_paths", "evidence_backed_rationale", "validator_status")
    with path.open("w", encoding="utf-8", newline="") as stream:
        out = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n"); out.writeheader()
        for workload in ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree", "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q"):
            out.writerow(dict(zip(fields, (workload, "LOW_STRUCTURAL_PRESSURE", "", "evidence.json", "source-backed review", "READY"))))
    ok = subprocess.run([str(TOOL), "--classification", str(path)], text=True, capture_output=True)
    assert ok.returncode == 0, ok.stderr
    text = path.read_text(encoding="utf-8").replace("LOW_STRUCTURAL_PRESSURE", "", 1); path.write_text(text, encoding="utf-8")
    bad = subprocess.run([str(TOOL), "--classification", str(path)], text=True, capture_output=True)
    assert bad.returncode != 0 and "ENUM_INVALID" in bad.stderr
print("FAST64_5_CLASSIFICATION_V1_REGRESSION_PASS")
