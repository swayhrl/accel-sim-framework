#!/usr/bin/env python3
"""Fixture regression for the future-only FAST64 triplet validator."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
VALIDATOR = REPO / "util/dtc_l1/validate_fast64_triplet_v1.py"
SOURCE = REPO / "docs/dtc_l1/fast64/generated/telemetry_regression"


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="fast64-triplet-v1-") as tmp:
        root = Path(tmp)
        paths = {}
        for label, name in (("base", "FAST64_TELEMETRY_NN_BASE.json"), ("io", "FAST64_TELEMETRY_NN_IO.json"), ("oo", "FAST64_TELEMETRY_NN_OO.json")):
            row = json.loads((SOURCE / name).read_text())
            row["immutable_attempt"] = {"attempt_uuid": label, "runner_sha256": "runner", "start_receipt_sha256": "start", "terminal_receipt_sha256": "terminal"}
            row["provenance"]["runtime_binary_sha256"] = "runtime"
            row["provenance"]["observer_overlay_sha256"] = "observer"
            path = root / f"{label}.json"
            path.write_text(json.dumps(row), encoding="utf-8")
            paths[label] = path
        output = root / "output.json"
        command = [str(VALIDATOR), "--base", str(paths["base"]), "--io", str(paths["io"]), "--oo", str(paths["oo"]), "--output", str(output), "--require-immutable"]
        subprocess.run(command, check=True)
        assert json.loads(output.read_text())["status"] == "FAST64_TRIPLET_STRICT_VALID_PENDING_STAGE_ACCEPTANCE"
        bad = json.loads(paths["oo"].read_text())
        bad["metrics"]["gpu_tot_sim_insn"] += 1
        paths["oo"].write_text(json.dumps(bad), encoding="utf-8")
        failed = subprocess.run(command, capture_output=True, text=True)
        assert failed.returncode != 0 and "instruction-domain" in failed.stderr
    print("FAST64_TRIPLET_VALIDATOR_V1_REGRESSION_PASS")


if __name__ == "__main__":
    main()
