#!/usr/bin/env python3
"""Hash-closed, non-destructive NVBit 1.7.6 bootstrap for C16 G3.

This helper is intentionally separate from the older Route-E script whose
execution gate is scoped to a different campaign.  It never overwrites a
release/build directory: a prior partial or materialized destination is a
fail-closed condition.  The only network input is the pinned public NVBit
archive below, verified before extraction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path
from typing import Any


NVBIT_VERSION = "1.7.6"
NVBIT_URL = "https://github.com/NVlabs/NVBit/releases/download/v1.7.6/nvbit-Linux-x86_64-1.7.6.tar.bz2"
NVBIT_SHA256 = "dba61708b702ff4562343716bb8b38a2d14aae5991b9719aece097afe505467f"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def plan(framework_root: Path, work_root: Path, cuda_home: Path) -> dict[str, Any]:
    return {
        "schema_version": "C16_G3_NVBIT_BOOTSTRAP_V1",
        "nvbit": {"version": NVBIT_VERSION, "url": NVBIT_URL, "sha256": NVBIT_SHA256},
        "framework_root": str(framework_root),
        "work_root": str(work_root),
        "cuda_home": str(cuda_home),
        "nvcc": str(cuda_home / "bin" / "nvcc"),
        "ptxas": str(cuda_home / "bin" / "ptxas"),
        "build_root": str(work_root / "nvbit" / f"nvbit-{NVBIT_VERSION}-c16-g3"),
        "architecture": "sm_86",
        "non_destructive": True,
    }


def require_empty_destination(path: Path) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite existing NVBit destination: {path}")
    if path.parent.exists() and not path.parent.is_dir():
        raise RuntimeError(f"NVBit destination parent is not a directory: {path.parent}")


def safe_extract(archive: Path, destination: Path) -> None:
    with tarfile.open(archive, "r:bz2") as tar:
        resolved_destination = destination.resolve()
        for member in tar.getmembers():
            member_path = (destination / member.name).resolve()
            if member_path != resolved_destination and resolved_destination not in member_path.parents:
                raise RuntimeError(f"unsafe archive member: {member.name}")
        tar.extractall(destination)


def download_verified(url: str, expected_sha256: str, archive: Path) -> None:
    if archive.exists():
        actual = sha256_file(archive)
        if actual != expected_sha256:
            raise RuntimeError(f"cached NVBit archive SHA256 mismatch: {actual}")
        return
    partial = archive.with_name(archive.name + ".partial")
    if partial.exists():
        raise RuntimeError(f"refusing to overwrite prior partial archive: {partial}")
    archive.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=60) as response, partial.open("xb") as handle:
            shutil.copyfileobj(response, handle)
    except Exception:
        # Keep any partial file as explicit diagnostic evidence; never silently
        # delete or reuse it on a later run.
        raise
    actual = sha256_file(partial)
    if actual != expected_sha256:
        raise RuntimeError(f"downloaded NVBit archive SHA256 mismatch: {actual}")
    os.replace(partial, archive)


def run(command: list[str], *, environment: dict[str, str], log: Path) -> None:
    with log.open("x", encoding="utf-8") as handle:
        process = subprocess.run(command, env=environment, stdout=handle, stderr=subprocess.STDOUT, text=True)
    if process.returncode != 0:
        raise RuntimeError(f"command failed ({process.returncode}): {' '.join(command)}")


def execute(arguments: argparse.Namespace) -> Path:
    framework_root = arguments.framework_root.resolve()
    work_root = arguments.work_root.resolve()
    cuda_home = arguments.cuda_home.resolve()
    payload = plan(framework_root, work_root, cuda_home)
    nvcc, ptxas = Path(payload["nvcc"]), Path(payload["ptxas"])
    tracer_source = framework_root / "util" / "tracer_nvbit"
    if not tracer_source.is_dir() or not nvcc.is_file() or not ptxas.is_file():
        raise RuntimeError("missing C16 tracer source or explicitly selected CUDA nvcc/ptxas")
    build_root = Path(payload["build_root"])
    require_empty_destination(build_root)
    archive = work_root / "bootstrap" / "nvbit-Linux-x86_64-1.7.6.tar.bz2"
    if not arguments.allow_network_download and not archive.is_file():
        raise RuntimeError("verified NVBit archive is absent; rerun with --allow-network-download when authorized")
    if arguments.allow_network_download:
        download_verified(NVBIT_URL, NVBIT_SHA256, archive)
    if sha256_file(archive) != NVBIT_SHA256:
        raise RuntimeError("NVBit archive does not match the fixed SHA256")
    build_root.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".nvbit-c16-g3-", dir=build_root.parent) as temporary:
        staged = Path(temporary) / build_root.name
        shutil.copytree(tracer_source, staged)
        release = staged / "nvbit_release"
        release.mkdir()
        safe_extract(archive, release)
        entries = list(release.iterdir())
        if len(entries) == 1 and entries[0].is_dir():
            nested = entries[0]
            for child in nested.iterdir():
                shutil.move(str(child), release / child.name)
            nested.rmdir()
        if not (release / "core" / "libnvbit.a").is_file():
            raise RuntimeError("NVBit release lacks core/libnvbit.a")
        environment = dict(os.environ)
        environment["PATH"] = f"{cuda_home / 'bin'}:{environment.get('PATH', '')}"
        environment["CUDA_HOME"] = str(cuda_home)
        environment["CXX"] = environment.get("CXX", "g++")
        tracer = staged / "tracer_tool"
        run([
            "make", "-C", str(tracer), "ARCH=sm_86",
            f"NVCC={nvcc} -ccbin={environment['CXX']} -D_FORCE_INLINES", f"PTXAS={ptxas}",
        ], environment=environment, log=staged / "tracer-build.log")
        run(["make", "-C", str(tracer / "traces-processing")], environment=environment, log=staged / "postprocess-build.log")
        tool = tracer / "tracer_tool.so"
        postprocessor = tracer / "traces-processing" / "post-traces-processing"
        if not tool.is_file() or not postprocessor.is_file():
            raise RuntimeError("NVBit build did not materialize tracer tool/postprocessor")
        os.replace(staged, build_root)
    payload.update({
        "status": "C16_G3_NVBIT_TOOL_BUILD_COMPLETE",
        "archive_path": str(archive),
        "archive_size_bytes": archive.stat().st_size,
        "tool_path": str(build_root / "tracer_tool" / "tracer_tool.so"),
        "tool_sha256": sha256_file(build_root / "tracer_tool" / "tracer_tool.so"),
        "postprocessor_path": str(build_root / "tracer_tool" / "traces-processing" / "post-traces-processing"),
        "postprocessor_sha256": sha256_file(build_root / "tracer_tool" / "traces-processing" / "post-traces-processing"),
        "tracer_source_commit": subprocess.check_output(["git", "-C", str(framework_root), "rev-parse", "HEAD"], text=True).strip(),
    })
    receipt = build_root / "C16_G3_NVBIT_BOOTSTRAP_RECEIPT.json"
    receipt.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--cuda-home", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--allow-network-download", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.execute:
        parser.error("choose exactly one of --dry-run or --execute")
    payload = plan(args.framework_root.resolve(), args.work_root.resolve(), args.cuda_home.resolve())
    if args.dry_run:
        print(json.dumps(payload, sort_keys=True, indent=2))
        return
    print(execute(args))


if __name__ == "__main__":
    main()
