#!/usr/bin/env python3
"""Hash-close R101R3 raw evidence and compact review artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from dataclasses import dataclass
from pathlib import Path
import tempfile
from typing import Iterable


STAGE = "AWMA_R101R3_BOUNDED_SERVICE_HANDOFF_V1"
REPO = Path(
    "/root/workspace/accel-sim-framework-"
    "awma-r101r3-bounded-service-handoff-174-v1"
)
PACK = REPO / (
    "docs/vm_tlb/review_packs/"
    "AWMA_R101R3_BOUNDED_SERVICE_HANDOFF_174_V1"
)
TOOLS = REPO / "util/vm_tlb/awma/r101r3_bounded_service_handoff_v1"
NODE = Path(
    "/root/share/mnt164/huangrulin/"
    "awma_r101r3_bounded_service_handoff_174_v1"
)
INDEX = PACK / "RAW_DATA_INDEX.tsv"
MANIFEST = NODE / "NODE164_EVIDENCE_SHA256SUMS"


class ClosureError(RuntimeError):
    pass


@dataclass(frozen=True)
class Row:
    role: str
    artifact: str
    path: str
    size_bytes: int
    sha256: str
    status: str
    notes: str


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ClosureError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def regular_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            continue
        if path.is_file():
            yield path


def make_row(role: str, path: Path, status: str, notes: str) -> Row:
    require(path.is_file() and not path.is_symlink(),
            f"missing/nonregular evidence: {path}")
    require(not any(character in notes for character in "\t\r\n"),
            f"unsafe notes: {notes!r}")
    return Row(role, path.name, str(path.resolve()), path.stat().st_size,
               sha256(path), status, notes)


def validate() -> dict:
    s1 = json.loads((NODE / "raw/formal/S1/RUN_SUMMARY.json").read_text())
    require(s1.get("stage") == STAGE and s1.get("status") == "PASS",
            "formal S1 status failed")
    gates = s1.get("gates", {})
    require(len(gates) == 56 and all(value is True for value in gates.values()),
            "formal S1 gates failed")
    require((NODE / "raw/formal/S1/rc.txt").read_text().strip() == "0",
            "formal S1 rc failed")
    require((NODE / "raw/formal/S1/run.stderr").stat().st_size == 0,
            "formal S1 stderr nonempty")
    require(not (NODE / "raw/formal/H1").exists(), "H1 must not exist")
    require(not (NODE / "raw/formal/FULL5").exists(), "FULL5 must not exist")
    stage_a = json.loads(
        (NODE / "raw/stage_a/STAGE_A_RECEIPT.json").read_text()
    )
    require(stage_a.get("status") == "PASS", "Stage A receipt failed")
    for smoke in ("default_off", "explicit_none", "s1_positive"):
        result = json.loads(
            (NODE / "raw/smoke" / smoke / "S1_SMOKE.json").read_text()
        )
        require(result.get("status") == "PASS", f"smoke failed: {smoke}")
    with (NODE / "raw/regressions/SHA256SUMS").open() as stream:
        for raw in stream:
            expected, name = raw.strip().split(maxsplit=1)
            name = name.lstrip("*")
            require(
                sha256(NODE / "raw/regressions" / name) == expected,
                f"regression hash drift: {name}",
            )
    return s1


def render_index(rows: list[Row]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
    writer.writerow(
        ("role", "artifact", "path", "size_bytes", "sha256", "status", "notes")
    )
    for row in rows:
        writer.writerow((
            row.role, row.artifact, row.path, row.size_bytes, row.sha256,
            row.status, row.notes,
        ))
    return stream.getvalue().encode()


def render_manifest(files: list[Path]) -> bytes:
    return "".join(
        f"{sha256(path)}  {path.relative_to(NODE)}\n" for path in files
    ).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    s1 = validate()
    rows: list[Row] = []

    for path in regular_files(NODE / "raw/stage_a"):
        rows.append(make_row(
            "STAGE_A_RAW", path, "FORMAL_OFFLINE",
            "accepted B0/O2 plus immutable-trace decomposition; no simulator rerun",
        ))
    for path in regular_files(NODE / "raw/regressions"):
        rows.append(make_row(
            "L1_REGRESSION", path, "PASS", "S1 directed/accepted regression evidence",
        ))
    for path in regular_files(NODE / "raw/smoke"):
        rows.append(make_row(
            "L1_INTEGRATED_SMOKE", path, "PASS",
            "default OFF, explicit none, or positive S1 small-run evidence",
        ))
    for path in regular_files(NODE / "raw/formal/S1"):
        rows.append(make_row(
            "S1_FORMAL", path, "PASS",
            "completed rc0 S1 CONTEXT2; postprocess-only recovery is explicit",
        ))
    for path in regular_files(NODE / "raw/formal/failed"):
        rows.append(make_row(
            "ENGINEERING_ATTEMPT", path, "NOT_SCIENTIFIC_RESULT",
            "early manually terminated formal attempt retained; not used in decision",
        ))
    for path in regular_files(NODE / "raw/orchestration"):
        rows.append(make_row(
            "ORCHESTRATION", path, "RECEIPT",
            "runner stdout/PID receipt including bounded attempt history",
        ))
    for path in regular_files(NODE / "runtime/S1_frozen"):
        rows.append(make_row(
            "S1_FROZEN_RUNTIME", path, "FROZEN",
            "exact S1 source/binary/library/build archive",
        ))

    for path in regular_files(TOOLS):
        if "__pycache__" in path.parts:
            continue
        rows.append(make_row(
            "REPRODUCIBILITY_TOOL", path, "SOURCE", "committed stage tool",
        ))
    for path in regular_files(PACK):
        if path.name in {"RAW_DATA_INDEX.tsv", "SHA256SUMS"}:
            continue
        rows.append(make_row(
            "REVIEW_ARTIFACT", path, "REVIEW", "compact review-pack artifact",
        ))

    rows.sort(key=lambda row: (row.role, row.path))
    index_blob = render_index(rows)
    node_files = [
        path for path in regular_files(NODE)
        if path != MANIFEST
        and "review_pack" not in path.parts
        and "report" not in path.parts
    ]
    manifest_blob = render_manifest(node_files)
    if args.write:
        atomic_write(INDEX, index_blob)
        atomic_write(MANIFEST, manifest_blob)
    print(json.dumps({
        "stage": STAGE,
        "status": "PASS",
        "decision": "R101R3_S1_BELOW_5_PERCENT_H1_NOT_TRIGGERED",
        "formal_summary_sha256": sha256(
            NODE / "raw/formal/S1/RUN_SUMMARY.json"
        ),
        "raw_index_rows": len(rows),
        "raw_index_sha256": hashlib.sha256(index_blob).hexdigest(),
        "node_manifest_entries": len(node_files),
        "node_manifest_sha256": hashlib.sha256(manifest_blob).hexdigest(),
        "write_performed": args.write,
        "h1_run": False,
        "full5_run": False,
        "s1_roi_cycles": s1["roi_cycles"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
