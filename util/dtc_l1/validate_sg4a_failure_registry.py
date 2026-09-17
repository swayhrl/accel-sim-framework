#!/usr/bin/env python3
"""Fail closed on the preserved SG4A nonnumeric deadlock registry."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def kv(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, value = line.split("\t", 1)
        # Immutable campaign manifests append selected terminal receipt fields.
        # Repetition is legal only when it preserves the original value.
        if key in result and result[key] != value:
            raise AssertionError(f"conflicting receipt key {key} in {path}")
        result[key] = value
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    args = parser.parse_args()
    registry = rows(args.registry)
    assert len(registry) == 1, "registry must contain exactly the observed failure"
    row = registry[0]
    assert row["schema"] == "SG4A_FAILURE_REGISTRY_V1"
    assert row["classification"] == "SOURCE_MODEL_DEADLOCK_PRESERVED"
    assert row["acceptance"] == "NONACCEPTED"
    assert row["simulator_exit_status"] == "1"
    run = Path(row["run_dir"])
    names = {
        "manifest_sha256": "RUN_MANIFEST.tsv",
        "start_sha256": "RUN_START.tsv",
        "terminal_sha256": "RUN_TERMINAL.tsv",
        "stdout_sha256": "simulator.stdout",
        "stderr_sha256": "simulator.stderr",
    }
    for field, name in names.items():
        assert digest(run / name) == row[field], f"{name} digest mismatch"
    manifest, terminal = kv(run / "RUN_MANIFEST.tsv"), kv(run / "RUN_TERMINAL.tsv")
    assert terminal["simulator_exit_status"] == "1"
    assert manifest["attempt_uuid"] == terminal["attempt_uuid"] == row["attempt_uuid"]
    for field in ("workload", "mode", "logical_kib"):
        assert manifest[field] == row[field]
    text = (run / "simulator.stdout").read_text(encoding="utf-8", errors="replace")
    assert "GPGPU-Sim uArch: ERROR ** deadlock detected:" in text
    assert "(58842 cycles ago)" in text
    assert f"gpu_tot_sim_cycle = {row['cycles']}" in text
    assert f"gpu_tot_sim_insn = {row['instructions']}" in text
    plan_rows = rows(args.plan)
    matched = [candidate for candidate in plan_rows if all(
        candidate[field] == row[field] for field in ("workload", "mode", "logical_kib")
    )]
    assert len(matched) == 1 and matched[0]["physical_pool_lines"] == "640"
    print("SG4A preserved failure registry: PASS (one immutable nonaccepted Core95 deadlock)")


if __name__ == "__main__":
    main()
