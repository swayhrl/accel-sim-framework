#!/usr/bin/env python3
"""Hash-bound postprocess-only recovery for the completed P1 formal run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any


STAGE = "AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_V1"
FORMAL_RUNNER_SHA = "fb6014a3aae7f0504be7ba24c22175430e07b784e5e4ca6a4bb6d7707cff58b5"
FORMAL_SUMMARIZER_SHA = "d41819083525cb7eed826f98459dfc5c22aa7d88b873f1520116aeb6970b342d"
REPO = Path("/root/workspace/accel-sim-framework-awma-r101r4-local-service-path-localization-174-v1")
SUMMARIZER = REPO / "util/vm_tlb/awma/r101r4_local_service_path_localization_v1/summarize_p1_context2.py"
IMMUTABLE = (
    "command.json", "start_utc.txt", "end_utc.txt", "rc.txt",
    "wall_seconds.txt", "run.log", "run.stderr", "gpgpu_inst_stats.txt",
)
EXPECTED_FAILED_GATES = {
    "p1_ldg_ldgsts_write_nonzero",
    "p1_normal_l1_activity",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    destination = args.destination.resolve()
    if not source.is_dir() or destination.exists():
        raise SystemExit("invalid recovery source/destination state")
    if source.parent.name != "failed" or destination.name != "P1":
        raise SystemExit("unexpected recovery identity")
    if destination.parent != source.parent.parent:
        raise SystemExit("destination is not the formal-root sibling")

    command = json.loads((source / "command.json").read_text())
    if command.get("stage") != STAGE or command.get("arm") != "P1":
        raise SystemExit("formal command identity mismatch")
    tools = command.get("formal_tools", {})
    if (tools.get("runner_sha256") != FORMAL_RUNNER_SHA
            or tools.get("summarizer_sha256") != FORMAL_SUMMARIZER_SHA):
        raise SystemExit("formal-at-run tool hashes mismatch")
    if (source / "rc.txt").read_text().strip() != "0":
        raise SystemExit("simulator did not complete rc=0")
    if (source / "run.stderr").stat().st_size != 0:
        raise SystemExit("simulator stderr is nonempty")

    prior = json.loads((source / "RUN_SUMMARY.json").read_text())
    failed = {key for key, value in prior.get("gates", {}).items()
              if value is not True}
    if failed != EXPECTED_FAILED_GATES:
        raise SystemExit(f"unexpected formal-at-run failed gates: {sorted(failed)}")
    before = {name: {"bytes": (source / name).stat().st_size,
                     "sha256": sha256(source / name)} for name in IMMUTABLE}
    failed_summary_sha = sha256(source / "RUN_SUMMARY.json")

    completed = subprocess.run(
        ["/usr/bin/python3", str(SUMMARIZER), str(source)], cwd=REPO,
        check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    if completed.returncode:
        raise SystemExit("recovery summarizer failed:\n" + completed.stdout
                         + completed.stderr)
    summary = json.loads((source / "RUN_SUMMARY.json").read_text())
    gates = summary.get("gates", {})
    if summary.get("status") != "PASS" or not gates \
            or not all(value is True for value in gates.values()):
        raise SystemExit("recovery summary did not close all gates")
    after = {name: {"bytes": (source / name).stat().st_size,
                    "sha256": sha256(source / name)} for name in IMMUTABLE}
    if before != after:
        raise SystemExit("immutable simulator artifacts changed")

    receipt = {
        "stage": STAGE,
        "arm": "P1",
        "status": "PASS",
        "evidence_class": "POSTPROCESS_ONLY_RECOVERY",
        "reason": (
            "formal-at-run summarizer imposed two non-preregistered nonzero "
            "assumptions: LDGSTS must be locally serviced and L1 pending-hit "
            "telemetry must increase; both zero observations are legal and "
            "are retained explicitly"
        ),
        "simulator_rerun": False,
        "scientific_result_changed": False,
        "raw_command_log_rc_stderr_immutable": True,
        "formal_at_run": {
            "runner_sha256": FORMAL_RUNNER_SHA,
            "summarizer_sha256": FORMAL_SUMMARIZER_SHA,
            "failed_summary_sha256": failed_summary_sha,
            "failed_gates": sorted(EXPECTED_FAILED_GATES),
        },
        "recovery": {
            "summarizer_path": str(SUMMARIZER),
            "summarizer_sha256": sha256(SUMMARIZER),
            "pass_summary_sha256": sha256(source / "RUN_SUMMARY.json"),
            "gate_count": len(gates),
        },
        "immutable_artifacts": before,
        "destination": str(destination),
        "atomic_promote": True,
    }
    atomic_json(source / "ORCHESTRATION_RECOVERY.json", receipt)
    os.replace(source, destination)
    print(json.dumps({
        "stage": STAGE,
        "status": "PASS",
        "destination": str(destination),
        "summary_sha256": sha256(destination / "RUN_SUMMARY.json"),
        "recovery_receipt_sha256": sha256(destination / "ORCHESTRATION_RECOVERY.json"),
        "gate_count": len(gates),
        "simulator_rerun": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
