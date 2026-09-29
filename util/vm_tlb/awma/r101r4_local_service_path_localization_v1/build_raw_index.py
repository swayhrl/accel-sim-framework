#!/usr/bin/env python3
"""Hash-close R101R4 raw evidence, frozen runtimes, tools and review files."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from dataclasses import dataclass
from pathlib import Path
import tempfile
from typing import Iterable


STAGE = "AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_V1"
REPO = Path("/root/workspace/accel-sim-framework-awma-r101r4-local-service-path-localization-174-v1")
PACK = REPO / "docs/vm_tlb/review_packs/AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_174_V1"
TOOLS = REPO / "util/vm_tlb/awma/r101r4_local_service_path_localization_v1"
NODE = Path("/root/share/mnt164/huangrulin/awma_r101r4_local_service_path_localization_174_v1")
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


def require(value: bool, message: str) -> None:
    if not value:
        raise ClosureError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink() and "__pycache__" not in path.parts:
            yield path


def row(role: str, path: Path, status: str, notes: str) -> Row:
    require(path.is_file() and not path.is_symlink(), f"invalid artifact: {path}")
    require(not any(c in notes for c in "\t\r\n"), "unsafe TSV notes")
    return Row(role, path.name, str(path.resolve()), path.stat().st_size,
               sha256(path), status, notes)


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def validate() -> tuple[dict, dict]:
    formal = []
    for arm, expected in (("P0", 55), ("P1", None)):
        root = NODE / "raw/formal" / arm
        summary = json.loads((root / "RUN_SUMMARY.json").read_text())
        gates = summary.get("gates", {})
        require(summary.get("stage") == STAGE and summary.get("status") == "PASS",
                f"{arm} status failed")
        require(summary.get("rc") == 0 and summary.get("stderr_bytes") == 0,
                f"{arm} process failed")
        require(gates and all(value is True for value in gates.values()),
                f"{arm} gates failed")
        if expected is not None:
            require(len(gates) == expected, f"{arm} gate count drift")
        require((root / "rc.txt").read_text().strip() == "0", f"{arm} rc drift")
        require((root / "run.stderr").stat().st_size == 0, f"{arm} stderr nonempty")
        formal.append(summary)
    require(not any((NODE / "raw/formal" / name).exists() for name in ("H1", "FULL5")),
            "forbidden formal arm exists")
    require(not list((NODE / "raw/formal").glob(".inflight.*")), "inflight formal data remains")
    for directory in (NODE / "raw/regressions", NODE / "raw/regressions_p1"):
        for raw in (directory / "SHA256SUMS").read_text().splitlines():
            expected, name = raw.split(maxsplit=1)
            require(sha256(directory / name.lstrip("*")) == expected,
                    f"regression hash drift: {directory.name}/{name}")
    for name, key in (("default_off", "P1_SMOKE.json"),
                      ("explicit_none", "P1_SMOKE.json"),
                      ("p0_positive", "P0_SMOKE.json"),
                      ("p1_positive", "P1_SMOKE.json")):
        result = json.loads((NODE / "raw/smoke" / name / key).read_text())
        require(result.get("status") == "PASS", f"smoke failed: {name}")
    return formal[0], formal[1]


def main() -> int:
    p0, p1 = validate()
    rows: list[Row] = []
    for directory, role, status, notes in (
        (NODE / "raw/regressions", "P0_L1_REGRESSION", "PASS", "P0 directed and inherited regression evidence"),
        (NODE / "raw/regressions_p1", "P1_L1_REGRESSION", "PASS", "P1 directed and inherited regression evidence"),
        (NODE / "raw/smoke", "L1_INTEGRATED_SMOKE", "PASS", "default OFF, explicit none and positive six-kernel evidence"),
        (NODE / "raw/diagnostic", "ENGINEERING_DIAGNOSTIC", "PASS", "bounded L1-instance scope and liveness evidence; not a performance result"),
        (NODE / "raw/formal/P0", "P0_FORMAL", "PASS", "completed rc0 P0 CONTEXT2 evidence"),
        (NODE / "raw/formal/P1", "P1_FORMAL", "PASS", "completed rc0 P1 CONTEXT2 evidence"),
        (NODE / "raw/formal/failed", "ENGINEERING_ATTEMPT", "NOT_SCIENTIFIC_RESULT", "failed pre-scope-fix P1 attempt retained and excluded from the decision"),
        (NODE / "raw/orchestration", "ORCHESTRATION", "RECEIPT", "runner stdout and PID receipts"),
        (NODE / "runtime/P0_frozen", "P0_FROZEN_RUNTIME", "FROZEN", "exact P0 source, binary, library and build manifest"),
        (NODE / "runtime/P1_frozen", "P1_FROZEN_RUNTIME", "FROZEN", "exact P1 source, binary, library and build manifest"),
        (NODE / "runtime/P1_superseded_pre_l1_scope_fix", "P1_SUPERSEDED_RUNTIME", "SUPERSEDED", "pre-L1-instance-gate runtime retained for engineering provenance"),
        (TOOLS, "REPRODUCIBILITY_TOOL", "SOURCE", "committed stage tool"),
    ):
        for path in files(directory):
            rows.append(row(role, path, status, notes))
    for path in files(PACK):
        if path.name not in {"RAW_DATA_INDEX.tsv", "SHA256SUMS"}:
            rows.append(row("REVIEW_ARTIFACT", path, "REVIEW", "compact review-pack artifact"))
    rows.sort(key=lambda item: (item.role, item.path))
    out = io.StringIO(newline="")
    writer = csv.writer(out, delimiter="\t", lineterminator="\n")
    writer.writerow(("role", "artifact", "path", "size_bytes", "sha256", "status", "notes"))
    for item in rows:
        writer.writerow((item.role, item.artifact, item.path, item.size_bytes,
                         item.sha256, item.status, item.notes))
    index_blob = out.getvalue().encode()
    node_files = [path for path in files(NODE) if path != MANIFEST
                  and "review_pack" not in path.parts and "report" not in path.parts]
    manifest_blob = "".join(
        f"{sha256(path)}  {path.relative_to(NODE)}\n" for path in node_files
    ).encode()
    atomic_write(INDEX, index_blob)
    atomic_write(MANIFEST, manifest_blob)
    print(json.dumps({
        "stage": STAGE,
        "status": "PASS",
        "p0_roi_cycles": p0["roi_cycles"],
        "p1_roi_cycles": p1["roi_cycles"],
        "raw_index_rows": len(rows),
        "raw_index_sha256": hashlib.sha256(index_blob).hexdigest(),
        "node_manifest_entries": len(node_files),
        "node_manifest_sha256": hashlib.sha256(manifest_blob).hexdigest(),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
