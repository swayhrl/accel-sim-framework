#!/usr/bin/env python3
"""Positive and precondition-negative tests for FAST64.7 v2 collection."""
from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "util/dtc_l1/collect_fast64_7_review_pack_v2.py"
ROSTER = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree", "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")


def write(path: Path, text: str = "workload\tvalue\nfixture\t1\n") -> None:
    path.write_text(text, encoding="utf-8")


with tempfile.TemporaryDirectory() as raw:
    root = Path(raw); stage3 = root / "s3"; stage4 = root / "s4"; stage5 = root / "s5"; stage6 = root / "s6"
    for directory in (stage3, stage4, stage5, stage6): directory.mkdir()
    for name in ("fast64_3_structural_pressure.tsv", "fast64_3_live_misses.tsv", "fast64_3_identity_manifest.tsv"): write(stage3 / name)
    for name in ("fast64_4_triplets.tsv", "fast64_4_speedup.tsv", "fast64_4_accounting.tsv", "fast64_4_identity_manifest.tsv", "fast64_4_raw_log_index.tsv"): write(stage4 / name)
    summary = "workload,base_cycles,io_cycles,oo_cycles,speedup_io,speedup_oo,instructions\n" + "\n".join(f"{w},100,80,70,1.25,1.42,10" for w in ROSTER) + "\nGM-FAST12,n/a,n/a,n/a,1.25,1.42,exact_12_members\n"
    write(stage5 / "fast12_summary.csv", summary)
    for name in ("fast12_stalls.csv", "fast12_live_misses.csv", "fast12_traffic.csv", "fast12_io_oo.csv"): write(stage5 / name, "fixture,value\na,1\n")
    class_rows = "workload\tprimary_class\tsecondary_classes\tevidence_paths\tevidence_backed_rationale\tvalidator_status\n" + "\n".join(f"{w}\tLOW_STRUCTURAL_PRESSURE\t\tevidence\tfixture\tREADY" for w in ROSTER) + "\n"
    write(stage5 / "fast64_5_causal_classification.tsv", class_rows)
    write(stage5 / "FAST64_5_CAUSAL_ANALYSIS_STATUS.tsv", "item\tvalue\nclassification_policy\tSUPPLIED_EVIDENCE_BACKED_NO_AUTOMATIC_CAUSAL_INFERENCE\n")
    for name in ("fast64_6_cells.tsv", "fast64_6_logical_plot.tsv", "fast64_6_physical_plot.tsv", "fast64_6_pib_plot.tsv", "fast64_6_raw_manifest.tsv", "fast64_6_collector_status.tsv"): write(stage6 / name)
    for name in ("limits.md", "tier_a.tsv", "tier_c.tsv"): write(root / name)
    ledger = root / "ledger.tsv"; write(ledger, "stage\tcurrent_state\n" + "\n".join(f"FAST64.{n}\tPASS" for n in range(7)) + "\n")
    command = [sys.executable, str(TOOL), "--stage-ledger", str(ledger), "--stage3-dir", str(stage3), "--stage4-dir", str(stage4), "--stage5-dir", str(stage5), "--stage6-dir", str(stage6), "--limitations-boundary", str(root / "limits.md"), "--tier-a-index", str(root / "tier_a.tsv"), "--tier-c-index", str(root / "tier_c.tsv"), "--output-dir", str(root / "out")]
    good = subprocess.run(command, text=True, capture_output=True); assert good.returncode == 0, good.stderr
    assert (root / "out" / "FAST64_7_INPUT_MANIFEST.tsv").is_file()
    write(ledger, "stage\tcurrent_state\n" + "\n".join(f"FAST64.{n}\t{'ACTIVE' if n == 6 else 'PASS'}" for n in range(7)) + "\n")
    bad = subprocess.run(command[:-1] + [str(root / "bad")], text=True, capture_output=True)
    assert bad.returncode != 0 and "PRIOR_PASS_REQUIRED" in bad.stderr
print("FAST64_7_REVIEW_PACK_V2_REGRESSION_PASS")
