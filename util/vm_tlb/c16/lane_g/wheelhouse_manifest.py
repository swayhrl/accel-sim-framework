#!/usr/bin/env python3
"""Generate a hash-bound manifest from actual C16 CPython 3.10 wheel files."""
from __future__ import annotations

import argparse
import csv
import email
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from packaging.tags import compatible_tags, cpython_tags, parse_tag, sys_tags

from c16_native_common import ContractError, sha256_file


FIELDS = ("wheel_filename", "package", "version", "size_bytes", "sha256", "source", "compatibility_tag", "status")
PYTORCH_SOURCE = "https://download.pytorch.org/whl/cu124"
PYPI_SOURCE = "https://pypi.org/simple"
STATUS = "LOCAL_HASH_CLOSED_CP310_LINUX_X86_64"


def canonical_package(name: str) -> str:
    return "".join("-" if character in "_.-" else character.lower() for character in name).replace("--", "-")


def wheel_metadata(path: Path) -> tuple[str, str, str]:
    try:
        with zipfile.ZipFile(path) as archive:
            metadata_paths = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
            wheel_paths = [name for name in archive.namelist() if name.endswith(".dist-info/WHEEL")]
            if len(metadata_paths) != 1 or len(wheel_paths) != 1:
                raise ContractError(f"wheel metadata/WHEEL file is ambiguous: {path.name}")
            metadata = email.message_from_bytes(archive.read(metadata_paths[0]))
            wheel = email.message_from_bytes(archive.read(wheel_paths[0]))
    except (OSError, zipfile.BadZipFile) as exc:
        raise ContractError(f"cannot inspect wheel {path}: {exc}") from exc
    package, version = metadata.get("Name"), metadata.get("Version")
    tags = wheel.get_all("Tag") or []
    if not package or not version or not tags:
        raise ContractError(f"wheel lacks Name/Version/Tag metadata: {path.name}")
    return package, version, ";".join(sorted(tags))


def target_compatible(tag_text: str) -> bool:
    """Require a tag accepted by the fixed CPython 3.10/Linux x86_64 target.

    The tooling itself may run under a newer host interpreter, so derive 3.10
    interpreter tags from the host's Linux platform tags rather than consulting
    only the current interpreter's `sys_tags()`.
    """
    candidate_tags = set()
    for tag in tag_text.split(";"):
        candidate_tags.update(parse_tag(tag))
    platforms = sorted({tag.platform for tag in sys_tags()})
    target_tags = set(cpython_tags(python_version=(3, 10), platforms=platforms))
    target_tags.update(compatible_tags(python_version=(3, 10), platforms=platforms))
    return bool(candidate_tags.intersection(target_tags))


def requirement_roots(path: Path) -> dict[str, str]:
    roots: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ContractError(f"cannot read requirements lock: {exc}") from exc
    for line in lines:
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.count("==") != 1:
            raise ContractError(f"requirements lock is not exact-pin only: {line}")
        package, version = line.split("==")
        roots[canonical_package(package)] = version
    return roots


def rows_for(wheelhouse: Path, requirements: Path) -> list[dict[str, Any]]:
    wheels = sorted(wheelhouse.glob("*.whl"))
    if not wheels:
        raise ContractError("wheelhouse has no wheel files")
    rows: list[dict[str, Any]] = []
    discovered: dict[str, str] = {}
    for wheel in wheels:
        package, version, tag = wheel_metadata(wheel)
        if not target_compatible(tag):
            raise ContractError(f"wheel tag is not compatible with this CPython/Linux target: {wheel.name} ({tag})")
        normalized = canonical_package(package)
        if normalized in discovered:
            raise ContractError(f"wheelhouse has multiple distributions for {package}: {wheel.name}")
        discovered[normalized] = version
        rows.append({
            "wheel_filename": wheel.name,
            "package": package,
            "version": version,
            "size_bytes": str(wheel.stat().st_size),
            "sha256": sha256_file(wheel),
            "source": PYTORCH_SOURCE if normalized == "torch" and version.endswith("+cu124") else PYPI_SOURCE,
            "compatibility_tag": tag,
            "status": STATUS,
        })
    for package, version in requirement_roots(requirements).items():
        if discovered.get(package) != version:
            raise ContractError(f"wheelhouse root pin missing or mismatched: {package}=={version}")
    return sorted(rows, key=lambda row: (canonical_package(str(row["package"])), str(row["wheel_filename"])))


def write_manifest(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--requirements", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--mirror-manifest", type=Path)
    args = parser.parse_args()
    rows = rows_for(args.wheelhouse, args.requirements)
    write_manifest(args.manifest, rows)
    if args.mirror_manifest is not None:
        write_manifest(args.mirror_manifest, rows)
    print(f"PASS C16 wheelhouse manifest generation: {len(rows)} wheels")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 wheelhouse manifest generation: {exc}")
        raise SystemExit(2)
