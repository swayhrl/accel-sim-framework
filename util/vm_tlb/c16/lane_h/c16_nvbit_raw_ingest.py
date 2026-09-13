#!/usr/bin/env python3
"""Hash-closed, non-destructive staging for future C16 NVBit model traces.

Raw address traces are intentionally stored outside the repository.  This
utility never issues a remote delete, never removes a verified local raw file,
and writes receipts with exclusive creation plus read-only permissions.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any


SCHEMA_REMOTE_FACTS = "C16_NVBIT_REMOTE_RAW_FACTS_V1"
SCHEMA_INGEST = "C16_NVBIT_LOCAL_RAW_INGEST_RECEIPT_V1"
SCHEMA_COMPRESSION = "C16_NVBIT_COMPRESSION_RECEIPT_V1"
SCHEMA_SCRATCH = "C16_NVBIT_PARSER_SCRATCH_RECEIPT_V1"
SCHEMA_DERIVED = "C16_NVBIT_DERIVED_ARTIFACT_RECEIPT_V1"
REAL_TRACE_KIND = "REAL_MODEL_TRACE"
FIXTURE_TRACE_KIND = "NVBIT18_PARSER_QUALIFICATION_FIXTURE_ONLY"


class IngestError(ValueError):
    """A retention invariant or receipt identity was violated."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def outside_repository(path: Path, what: str) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(repository_root().resolve())
    except ValueError:
        return resolved
    raise IngestError(f"{what} must be outside the Git worktree: {resolved}")


def _nonempty(value: str, name: str) -> str:
    if not value.strip():
        raise IngestError(f"{name} must be nonempty")
    return value


def _sha(value: str, name: str) -> str:
    value = value.lower()
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise IngestError(f"{name} must be a SHA-256 hex digest")
    return value


def _new_receipt(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, sort_keys=True)
        output.write("\n")
    path.chmod(0o444)
    return path


def _load_receipt(path: Path, schema: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise IngestError(f"cannot read receipt {path}: {error}") from error
    if not isinstance(payload, dict) or payload.get("schema_version") != schema:
        raise IngestError(f"receipt {path} must have schema_version={schema}")
    return payload


def _facts_receipt_path(root: Path, remote_sha: str) -> Path:
    return root / "receipts" / f"REMOTE_FACTS_{remote_sha}.json"


def _remote_facts(host: str, remote_path: str) -> tuple[int, str]:
    """Read remote size/SHA without changing remote state.

    ``LOCAL`` is an explicit test/development transport.  Production callers
    pass an SSH host; both routes use the same size/SHA closure rules.
    """
    if host == "LOCAL":
        path = Path(remote_path).expanduser().resolve()
        if not path.is_file():
            raise IngestError(f"local fixture source does not exist: {path}")
        return path.stat().st_size, sha256_file(path)
    command = (
        "set -eu; "
        f"LC_ALL=C stat -c '%s' -- {shlex.quote(remote_path)}; "
        f"sha256sum -- {shlex.quote(remote_path)}"
    )
    try:
        completed = subprocess.run(["ssh", host, command], text=True, capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", "")
        raise IngestError(f"remote read-only size/SHA probe failed for {host}:{remote_path}: {detail}") from error
    lines = completed.stdout.splitlines()
    if len(lines) != 2:
        raise IngestError("remote size/SHA probe returned an unexpected number of lines")
    try:
        size = int(lines[0], 10)
    except ValueError as error:
        raise IngestError(f"remote size is not decimal: {lines[0]!r}") from error
    digest = lines[1].split(maxsplit=1)[0]
    return size, _sha(digest, "remote SHA256")


def probe(args: argparse.Namespace) -> Path:
    root = outside_repository(args.local_root, "local raw root")
    host = _nonempty(args.remote_host, "remote host")
    remote_path = _nonempty(args.remote_path, "remote path")
    size, digest = _remote_facts(host, remote_path)
    if size < 0:
        raise IngestError("remote size cannot be negative")
    payload = {
        "schema_version": SCHEMA_REMOTE_FACTS,
        "status": "REMOTE_SIZE_SHA256_CAPTURED",
        "created_utc": utc_now(),
        "trace_kind": args.trace_kind,
        "fixture_label": FIXTURE_TRACE_KIND if args.trace_kind == FIXTURE_TRACE_KIND else None,
        "scientific_model_evidence": args.trace_kind == REAL_TRACE_KIND,
        "run_id": _nonempty(args.run_id, "run_id"),
        "target_identity": _nonempty(args.target_identity, "target_identity"),
        "tool_identity": _nonempty(args.tool_identity, "tool_identity"),
        "remote": {"host": host, "path": remote_path, "size_bytes": size, "sha256": digest},
        "remote_delete_permitted": False,
        "local_uncompressed_delete_permitted": False,
        "retention_rule": "Remote raw remains retained; this tool has no remote deletion command.",
    }
    return _new_receipt(_facts_receipt_path(root, digest), payload)


def _quarantine(root: Path, partial: Path, reason: str, context: dict[str, Any]) -> Path | None:
    quarantined: Path | None = None
    if partial.exists():
        failed_dir = root / "failed"
        failed_dir.mkdir(parents=True, exist_ok=True)
        quarantined = failed_dir / f"{partial.name}.{uuid.uuid4().hex}.failed"
        os.replace(partial, quarantined)
    payload = {
        "schema_version": SCHEMA_INGEST,
        "status": "FAILED_OR_PARTIAL_QUARANTINED",
        "created_utc": utc_now(),
        "reason": reason,
        "quarantined_partial_path": str(quarantined) if quarantined else None,
        "remote_delete_permitted": False,
        "local_uncompressed_delete_permitted": False,
        **context,
    }
    marker = hashlib.sha256((reason + str(context)).encode("utf-8")).hexdigest()
    return _new_receipt(root / "receipts" / f"FAILED_{marker}_{uuid.uuid4().hex}.json", payload)


def _rsync_to_partial(host: str, remote_path: str, partial: Path) -> None:
    partial.parent.mkdir(parents=True, exist_ok=True)
    source = str(Path(remote_path).expanduser().resolve()) if host == "LOCAL" else f"{host}:{remote_path}"
    try:
        # No --remove-source-files, --delete, or remote mutation flag is ever used.
        subprocess.run(["rsync", "-a", "--partial", "--protect-args", source, str(partial)], check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        raise IngestError(f"rsync into .partial failed: {error}") from error


def _compress(raw_path: Path, algorithm: str, root: Path, ingest_receipt: Path, ingest: dict[str, Any]) -> Path | None:
    if algorithm == "none":
        return None
    suffix = {"zstd": ".zst", "xz": ".xz"}.get(algorithm)
    if suffix is None:
        raise IngestError("compression must be one of: none, zstd, xz")
    final = root / "compressed" / f"{raw_path.name}{suffix}"
    partial = final.with_name(final.name + ".partial")
    if final.exists() or partial.exists():
        raise IngestError(f"refusing to overwrite existing compressed target: {final}")
    final.parent.mkdir(parents=True, exist_ok=True)
    command = ["zstd", "-q", "-c", "--", str(raw_path)] if algorithm == "zstd" else ["xz", "-z", "-c", "--", str(raw_path)]
    try:
        with partial.open("xb") as output:
            subprocess.run(command, stdout=output, check=True)
        compressed_sha = sha256_file(partial)
        compressed_size = partial.stat().st_size
        os.replace(partial, final)
    except (OSError, subprocess.CalledProcessError) as error:
        _quarantine(root, partial, "compression failed", {"ingest_receipt": str(ingest_receipt), "algorithm": algorithm})
        raise IngestError(f"compression failed; partial has been quarantined: {error}") from error
    payload = {
        "schema_version": SCHEMA_COMPRESSION,
        "status": "COMPRESSED_SHA256_CLOSED",
        "created_utc": utc_now(),
        "ingest_receipt": str(ingest_receipt),
        "raw": ingest["local"],
        "fixture_label": ingest.get("fixture_label"),
        "compressed": {"path": str(final), "size_bytes": compressed_size, "sha256": compressed_sha, "algorithm": algorithm},
        "compression_ratio_compressed_over_raw": compressed_size / ingest["local"]["size_bytes"],
        "remote_delete_permitted": False,
        "local_uncompressed_delete_permitted": False,
        "retention_rule": "Raw remains retained; compressed SHA closure is necessary but not sufficient for deletion.",
    }
    return _new_receipt(root / "receipts" / f"COMPRESSION_{compressed_sha}.json", payload)


def ingest(args: argparse.Namespace) -> tuple[Path, Path | None]:
    root = outside_repository(args.local_root, "local raw root")
    facts_path = Path(args.remote_facts).expanduser().resolve()
    facts = _load_receipt(facts_path, SCHEMA_REMOTE_FACTS)
    remote = facts.get("remote")
    if not isinstance(remote, dict):
        raise IngestError("remote facts receipt lacks remote object")
    host, remote_path = str(remote.get("host", "")), str(remote.get("path", ""))
    remote_size = int(remote.get("size_bytes", -1))
    remote_sha = _sha(str(remote.get("sha256", "")), "remote SHA256")
    if remote_size < 0:
        raise IngestError("remote size cannot be negative")
    safe_basename = Path(remote_path).name
    if safe_basename in {"", ".", ".."}:
        raise IngestError("remote raw path must name a file")
    raw_final = root / "raw" / f"{remote_sha}_{safe_basename}"
    raw_partial = raw_final.with_name(raw_final.name + ".partial")
    if raw_final.exists() or raw_partial.exists():
        raise IngestError(f"refusing to overwrite/resume an existing raw target: {raw_final}")
    local_available_before = shutil.disk_usage(root.parent if root.parent.exists() else root).free
    context = {"remote_facts_receipt": str(facts_path), "remote": remote, "local_root": str(root)}
    try:
        _rsync_to_partial(host, remote_path, raw_partial)
        local_size = raw_partial.stat().st_size
        local_sha = sha256_file(raw_partial)
        if local_size != remote_size or local_sha != remote_sha:
            _quarantine(root, raw_partial, "local size/SHA does not close remote receipt", context)
            raise IngestError("local size/SHA did not close remote receipt; raw was quarantined and remote retained")
        os.replace(raw_partial, raw_final)
    except IngestError:
        if raw_partial.exists():
            _quarantine(root, raw_partial, "rsync transfer failed before SHA closure", context)
        raise
    payload = {
        "schema_version": SCHEMA_INGEST,
        "status": "LOCAL_RAW_SHA256_CLOSED",
        "created_utc": utc_now(),
        "remote_facts_receipt": str(facts_path),
        "trace_kind": facts["trace_kind"],
        "fixture_label": facts.get("fixture_label"),
        "scientific_model_evidence": facts["scientific_model_evidence"],
        "run_id": facts["run_id"],
        "target_identity": facts["target_identity"],
        "tool_identity": facts["tool_identity"],
        "remote": remote,
        "local": {"path": str(raw_final), "size_bytes": remote_size, "sha256": remote_sha},
        "local_available_before_bytes": local_available_before,
        "local_available_after_bytes": shutil.disk_usage(root).free,
        "remote_local_sha256_closed": True,
        "remote_delete_permitted": False,
        "local_uncompressed_delete_permitted": False,
        "retention_rule": "Never delete remote raw in this pipeline. Local raw remains retained after any compression.",
    }
    receipt = _new_receipt(root / "receipts" / f"INGEST_{remote_sha}.json", payload)
    compression_receipt = _compress(raw_final, args.compression, root, receipt, payload)
    return receipt, compression_receipt


def _decompress_to(source: Path, algorithm: str, destination: Path) -> None:
    if algorithm == "none":
        shutil.copyfile(source, destination)
        return
    command = ["zstd", "-q", "-d", "-c", "--", str(source)] if algorithm == "zstd" else ["xz", "-d", "-c", "--", str(source)]
    with destination.open("xb") as output:
        subprocess.run(command, stdout=output, check=True)


def prepare_scratch(args: argparse.Namespace) -> Path:
    root = outside_repository(args.local_root, "local raw root")
    scratch_root = outside_repository(args.scratch_root, "parser scratch root")
    ingest_receipt = Path(args.ingest_receipt).expanduser().resolve()
    ingest_payload = _load_receipt(ingest_receipt, SCHEMA_INGEST)
    local = ingest_payload.get("local")
    if not isinstance(local, dict):
        raise IngestError("ingest receipt lacks local raw identity")
    raw_path = Path(str(local.get("path", "")))
    expected_sha = _sha(str(local.get("sha256", "")), "local raw SHA256")
    expected_size = int(local.get("size_bytes", -1))
    source = raw_path
    algorithm = "none"
    if args.compression_receipt:
        compression = _load_receipt(Path(args.compression_receipt).expanduser().resolve(), SCHEMA_COMPRESSION)
        compressed = compression.get("compressed")
        if not isinstance(compressed, dict):
            raise IngestError("compression receipt lacks compressed identity")
        source = Path(str(compressed.get("path", "")))
        algorithm = str(compressed.get("algorithm", ""))
        if sha256_file(source) != _sha(str(compressed.get("sha256", "")), "compressed SHA256"):
            raise IngestError("compressed input SHA256 no longer matches its receipt")
    elif not raw_path.is_file():
        raise IngestError("raw input missing; provide a SHA-closed compression receipt instead")
    target = scratch_root / f"{expected_sha}_{raw_path.name}"
    partial = target.with_name(target.name + ".partial")
    if target.exists() or partial.exists():
        raise IngestError(f"refusing to overwrite parser scratch target: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        _decompress_to(source, algorithm, partial)
        if partial.stat().st_size != expected_size or sha256_file(partial) != expected_sha:
            raise IngestError("parser scratch did not close the ingest raw identity")
        os.replace(partial, target)
    except (OSError, subprocess.CalledProcessError, IngestError) as error:
        _quarantine(root, partial, "parser scratch materialization failed", {"ingest_receipt": str(ingest_receipt)})
        raise IngestError(f"parser scratch failed; partial was quarantined: {error}") from error
    payload = {
        "schema_version": SCHEMA_SCRATCH,
        "status": "PARSER_SCRATCH_RAW_SHA256_CLOSED",
        "created_utc": utc_now(),
        "ingest_receipt": str(ingest_receipt),
        "fixture_label": ingest_payload.get("fixture_label"),
        "scratch": {"path": str(target), "size_bytes": expected_size, "sha256": expected_sha},
        "source_kind": "COMPRESSED" if algorithm != "none" else "UNCOMPRESSED_RAW",
        "remote_delete_permitted": False,
        "local_uncompressed_delete_permitted": False,
    }
    return _new_receipt(root / "receipts" / f"SCRATCH_{expected_sha}_{uuid.uuid4().hex}.json", payload)


def register_derived(args: argparse.Namespace) -> Path:
    root = outside_repository(args.local_root, "local raw root")
    ingest_receipt = Path(args.ingest_receipt).expanduser().resolve()
    ingest_payload = _load_receipt(ingest_receipt, SCHEMA_INGEST)
    derived = Path(args.derived_path).expanduser().resolve()
    outside_repository(derived, "derived compact artifact")
    if not derived.is_file():
        raise IngestError(f"derived compact artifact does not exist: {derived}")
    digest = sha256_file(derived)
    payload = {
        "schema_version": SCHEMA_DERIVED,
        "status": "DERIVED_COMPACT_ARTIFACT_SHA256_CLOSED",
        "created_utc": utc_now(),
        "ingest_receipt": str(ingest_receipt),
        "fixture_label": ingest_payload.get("fixture_label"),
        "run_id": ingest_payload["run_id"],
        "target_identity": ingest_payload["target_identity"],
        "tool_identity": ingest_payload["tool_identity"],
        "derived_kind": _nonempty(args.derived_kind, "derived kind"),
        "derived": {"path": str(derived), "size_bytes": derived.stat().st_size, "sha256": digest},
        "raw_in_git": False,
        "remote_delete_permitted": False,
        "local_uncompressed_delete_permitted": False,
    }
    return _new_receipt(root / "receipts" / f"DERIVED_{digest}.json", payload)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    probe_parser = commands.add_parser("probe", help="capture remote size/SHA in an immutable receipt")
    probe_parser.add_argument("--local-root", type=Path, required=True)
    probe_parser.add_argument("--remote-host", required=True, help="SSH host, or LOCAL for a test-only local source")
    probe_parser.add_argument("--remote-path", required=True)
    probe_parser.add_argument("--run-id", required=True)
    probe_parser.add_argument("--target-identity", required=True)
    probe_parser.add_argument("--tool-identity", required=True)
    probe_parser.add_argument("--trace-kind", default=REAL_TRACE_KIND)
    ingest_parser = commands.add_parser("ingest", help="rsync to .partial, close SHA, then optionally compress")
    ingest_parser.add_argument("--local-root", type=Path, required=True)
    ingest_parser.add_argument("--remote-facts", type=Path, required=True)
    ingest_parser.add_argument("--compression", default="none", choices=("none", "zstd", "xz"))
    scratch_parser = commands.add_parser("prepare-parser-scratch", help="materialize a hash-verified parser scratch copy")
    scratch_parser.add_argument("--local-root", type=Path, required=True)
    scratch_parser.add_argument("--scratch-root", type=Path, required=True)
    scratch_parser.add_argument("--ingest-receipt", type=Path, required=True)
    scratch_parser.add_argument("--compression-receipt", type=Path)
    derived_parser = commands.add_parser("register-derived", help="hash-close a compact derived artifact without adding raw to Git")
    derived_parser.add_argument("--local-root", type=Path, required=True)
    derived_parser.add_argument("--ingest-receipt", type=Path, required=True)
    derived_parser.add_argument("--derived-path", type=Path, required=True)
    derived_parser.add_argument("--derived-kind", required=True)
    args = parser.parse_args()
    try:
        if args.command == "probe":
            receipt = probe(args)
            print(f"PASS c16-nvbit-raw-ingest remote_facts_receipt={receipt}")
        elif args.command == "ingest":
            receipt, compression = ingest(args)
            print(f"PASS c16-nvbit-raw-ingest ingest_receipt={receipt} compression_receipt={compression}")
        elif args.command == "prepare-parser-scratch":
            receipt = prepare_scratch(args)
            print(f"PASS c16-nvbit-raw-ingest scratch_receipt={receipt}")
        else:
            receipt = register_derived(args)
            print(f"PASS c16-nvbit-raw-ingest derived_receipt={receipt}")
    except (IngestError, OSError, ValueError) as error:
        raise SystemExit(f"FAIL c16-nvbit-raw-ingest: {error}") from error


if __name__ == "__main__":
    main()
