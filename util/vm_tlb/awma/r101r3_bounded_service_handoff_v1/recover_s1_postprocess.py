#!/usr/bin/env python3
"""Hash-bound postprocess-only recovery for the completed S1 formal run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any


STAGE = "AWMA_R101R3_BOUNDED_SERVICE_HANDOFF_V1"
FORMAL_RUNNER_SHA = "52b4d37534257421eef37ec1e2138ff5a158731e441ec2eff3356870b55a21e6"
FORMAL_SUMMARIZER_SHA = "af69ab68e08a8f8ae871c162b4088ac332372ff6dbb6932c7a7cc7735d6427c3"
REPO = Path(
    "/root/workspace/accel-sim-framework-"
    "awma-r101r3-bounded-service-handoff-174-v1"
)
SUMMARIZER = REPO / (
    "util/vm_tlb/awma/r101r3_bounded_service_handoff_v1/"
    "summarize_s1_context2.py"
)
IMMUTABLE = (
    "command.json",
    "start_utc.txt",
    "end_utc.txt",
    "rc.txt",
    "wall_seconds.txt",
    "run.log",
    "run.stderr",
    "gpgpu_inst_stats.txt",
)


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

    if not source.is_dir():
        raise SystemExit(f"source is not a directory: {source}")
    if destination.exists():
        raise SystemExit(f"destination already exists: {destination}")
    if destination.parent != source.parent.parent:
        raise SystemExit("destination is not the formal root sibling")
    if source.parent.name != "failed" or destination.name != "S1":
        raise SystemExit("unexpected recovery source/destination identity")

    command = json.loads((source / "command.json").read_text())
    if command.get("stage") != STAGE or command.get("arm") != "S1":
        raise SystemExit("formal command identity mismatch")
    tools = command.get("formal_tools", {})
    if (
        tools.get("runner_sha256") != FORMAL_RUNNER_SHA
        or tools.get("summarizer_sha256") != FORMAL_SUMMARIZER_SHA
    ):
        raise SystemExit("formal-at-run tool hashes mismatch")
    if (source / "rc.txt").read_text().strip() != "0":
        raise SystemExit("simulator did not complete rc=0")
    if (source / "run.stderr").stat().st_size != 0:
        raise SystemExit("simulator stderr is nonempty")

    before = {
        name: {
            "bytes": (source / name).stat().st_size,
            "sha256": sha256(source / name),
        }
        for name in IMMUTABLE
    }
    failed_summary_sha = sha256(source / "RUN_SUMMARY.json")

    completed = subprocess.run(
        ["/usr/bin/python3", str(SUMMARIZER), str(source)],
        cwd=REPO,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode:
        raise SystemExit(
            "recovery summarizer failed:\n"
            + completed.stdout + completed.stderr
        )
    summary = json.loads((source / "RUN_SUMMARY.json").read_text())
    if summary.get("status") != "PASS":
        raise SystemExit("recovery summary is not PASS")
    gates = summary.get("gates", {})
    if not gates or not all(value is True for value in gates.values()):
        raise SystemExit("recovery summary contains a failed/nonboolean gate")

    after = {
        name: {
            "bytes": (source / name).stat().st_size,
            "sha256": sha256(source / name),
        }
        for name in IMMUTABLE
    }
    if before != after:
        raise SystemExit("immutable simulator artifacts changed in recovery")

    receipt = {
        "stage": STAGE,
        "arm": "S1",
        "status": "PASS",
        "evidence_class": "POSTPROCESS_ONLY_RECOVERY",
        "reason": (
            "formal-at-run summarizer used two non-preregistered assumptions: "
            "an R2-only interpretation of the inherited combined service-mode "
            "print label and an assumed queue depth of 8 instead of recording "
            "the existing finite queue observations"
        ),
        "simulator_rerun": False,
        "scientific_result_changed": False,
        "raw_command_log_rc_stderr_immutable": True,
        "formal_at_run": {
            "runner_sha256": FORMAL_RUNNER_SHA,
            "summarizer_sha256": FORMAL_SUMMARIZER_SHA,
            "failed_summary_sha256": failed_summary_sha,
        },
        "recovery": {
            "summarizer_path": str(SUMMARIZER),
            "summarizer_sha256": sha256(SUMMARIZER),
            "pass_summary_sha256": sha256(source / "RUN_SUMMARY.json"),
            "stdout": completed.stdout.strip(),
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
        "recovery_receipt_sha256": sha256(
            destination / "ORCHESTRATION_RECOVERY.json"
        ),
        "simulator_rerun": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
