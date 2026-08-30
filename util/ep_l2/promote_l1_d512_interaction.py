#!/usr/bin/env python3
"""Promote exact, locally valid Lane-C D512 interaction results after Lane-B PASS."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


CORE = "878f80869ce212e779df20b6421e4dc7f987825d"
FRAMEWORK = "aae62b66685f15437cecf0193934f628e6fac6ae"
CELLS = ("D512-META-HR", "D512-BANK-HR")
WORKLOADS = ("vectorAdd_4M", "scan", "spmv", "convolutionSeparable", "btree", "sad", "FWT_7_21")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--workboard", type=Path, required=True)
    parser.add_argument("--workboard-repo", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    line = next((item for item in args.workboard.read_text().splitlines()
                 if item.startswith("| D512-PREFLIGHT |")), "")
    if "| DONE |" not in line or "| PASS |" not in line:
        raise SystemExit("D512-PREFLIGHT is not DONE/PASS in the supplied workboard")
    board_commit = subprocess.check_output(
        ["git", "-C", str(args.workboard_repo), "rev-parse", "HEAD"], text=True).strip()

    records: list[tuple[Path, dict]] = []
    for cell in CELLS:
        for workload in WORKLOADS:
            path = args.results / cell / workload / "run_status.json"
            record = json.loads(path.read_text())
            if record.get("status") != "COMPLETE_VALID" or record.get("maturity") != "SPECULATIVE_PENDING_GATE":
                raise SystemExit("not promotable: " + str(path))
            if record.get("candidate_core_commit") != CORE or record.get("candidate_framework_commit") != FRAMEWORK:
                raise SystemExit("candidate mismatch: " + str(path))
            records.append((path, record))

    promotion = {
        "maturity": "PROMOTED_VALID_CALIBRATION",
        "promotion_dependencies": ["D256_EQ_SCAN_PASS", "D512_PREFLIGHT_PASS"],
        "gate_source": str(args.workboard),
        "gate_workboard_commit": board_commit,
        "candidate_core_commit": CORE,
        "candidate_framework_commit": FRAMEWORK,
        "promoted_rows": len(records),
    }
    if args.dry_run:
        print(json.dumps(promotion, sort_keys=True))
        return
    for path, record in records:
        record["maturity"] = promotion["maturity"]
        record["promotion"] = promotion
        path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    (args.results / "PROMOTION.json").write_text(json.dumps(promotion, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
