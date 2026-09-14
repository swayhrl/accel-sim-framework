#!/usr/bin/env python3
"""Small dependency-free primitives for the C16 Pipeline V1 receiver."""
from __future__ import annotations

import ctypes
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

STATUSES = {"FORMAL", "MECHANISM_ONLY", "DIAGNOSTIC", "PRE_FIX", "OBSOLETE", "INVALID"}
RUN_ID_RE = re.compile(r"^C16R_[a-z0-9-]+_[a-z0-9-]+_[a-z0-9-]+_[a-z0-9-]+_[a-z0-9-]+_\d{8}T\d{6}Z_[a-f0-9]{12}$")
MANIFEST_FIELDS = {"schema_version", "run_id", "created_at_utc", "scientific_status", "producer", "git", "model", "input", "scenario", "runtime", "capture", "artifacts"}
META_FILENAMES = {"RUN_MANIFEST.json", "READY"}


class AdmissionError(ValueError):
    """A manifest or destination state does not meet the frozen contract."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def safe_relative_path(value: str) -> Path:
    path = Path(value)
    if not value or path.is_absolute() or ".." in path.parts or value in META_FILENAMES:
        raise AdmissionError(f"unsafe artifact relative path: {value!r}")
    return path


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AdmissionError(f"invalid JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AdmissionError(f"JSON object required at {path}")
    return value


def write_json_new(path: Path, value: dict[str, Any]) -> None:
    """Write a new immutable JSON object, failing rather than overwriting."""
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        offset = 0
        while offset < len(data):
            offset += os.write(fd, data[offset:])
        os.fsync(fd)
    finally:
        os.close(fd)


def validate_manifest(manifest: dict[str, Any]) -> None:
    missing = MANIFEST_FIELDS - set(manifest)
    if missing:
        raise AdmissionError("missing manifest fields: " + ",".join(sorted(missing)))
    if not isinstance(manifest["run_id"], str) or not RUN_ID_RE.fullmatch(manifest["run_id"]):
        raise AdmissionError("invalid generated RUN_ID")
    if manifest["scientific_status"] not in STATUSES:
        raise AdmissionError("invalid scientific_status")
    for field in ("producer", "git", "model", "input", "scenario", "runtime", "capture"):
        if not isinstance(manifest[field], dict):
            raise AdmissionError(f"manifest {field} must be an object")
    for field in ("hostname", "gpu_name", "gpu_uuid", "driver", "cuda"):
        if not manifest["producer"].get(field):
            raise AdmissionError(f"producer.{field} missing")
    for field in ("repository", "commit"):
        if not manifest["git"].get(field):
            raise AdmissionError(f"git.{field} missing")
    for field in ("model_id", "revision", "asset_receipt_sha256"):
        if not manifest["model"].get(field):
            raise AdmissionError(f"model.{field} missing")
    for field in ("binding_id", "authority_status", "receipt_sha256", "token_ids_sha256_or_semantic_hash"):
        if not manifest["input"].get(field):
            raise AdmissionError(f"input.{field} missing")
    for field in ("batch", "prefill_tokens", "decode_tokens", "input_class", "phase"):
        if field not in manifest["scenario"]:
            raise AdmissionError(f"scenario.{field} missing")
    for field in ("instrument", "tool_version", "target", "exact_argv"):
        if field not in manifest["capture"]:
            raise AdmissionError(f"capture.{field} missing")
    artifacts = manifest["artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        raise AdmissionError("non-empty artifacts list required")
    seen: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise AdmissionError("artifact must be an object")
        rel = artifact.get("relative_path")
        if not isinstance(rel, str):
            raise AdmissionError("artifact relative_path missing")
        safe_relative_path(rel)
        if rel in seen:
            raise AdmissionError("duplicate artifact: " + rel)
        seen.add(rel)
        if not isinstance(artifact.get("size_bytes"), int) or artifact["size_bytes"] < 0:
            raise AdmissionError("invalid artifact size")
        sha = artifact.get("sha256")
        if not isinstance(sha, str) or not re.fullmatch(r"[a-f0-9]{64}", sha):
            raise AdmissionError("invalid artifact SHA256")


def enumerate_regular_artifacts(bundle: Path) -> list[dict[str, Any]]:
    actual: list[dict[str, Any]] = []
    for path in sorted(bundle.rglob("*")):
        relative = path.relative_to(bundle)
        if path.is_symlink():
            raise AdmissionError(f"symlink rejected: {relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise AdmissionError(f"non-regular file rejected: {relative}")
        if relative.parent == Path(".") and relative.name in META_FILENAMES:
            continue
        actual.append({"relative_path": str(relative), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return actual


def rename_noreplace(source: Path, destination: Path) -> None:
    """Use the Phase-B-tested Linux primitive; never fall back to overwrite."""
    if destination.exists():
        raise FileExistsError(destination)
    if os.uname().machine != "x86_64":
        raise AdmissionError("renameat2 RENAME_NOREPLACE unsupported architecture")
    libc = ctypes.CDLL(None, use_errno=True)
    at_fdcwd, rename_noreplace_flag, syscall_renameat2 = -100, 1, 316
    result = libc.syscall(syscall_renameat2, at_fdcwd, os.fsencode(source), at_fdcwd, os.fsencode(destination), rename_noreplace_flag)
    if result != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(source), str(destination))
