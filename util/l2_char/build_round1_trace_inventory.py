#!/usr/bin/env python3
"""Create a read-only physical trace inventory for L2 characterization preflight.

This intentionally records missing provenance as ``MISSING``.  It never invents
an archive checksum from a path name and it does not hash multi-gigabyte trace
trees during a preflight scan.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re


DEFAULT_ROOTS = (
    Path("/workspace/worktrees/accel-sim-decoupled-l2/hw_run"),
    Path("/workspace/worktrees/accel-sim-tls-cache/hw_run"),
    Path("/workspace/worktrees/accel-sim-c2p-cache/hw_run"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def first_kernel_metadata(trace_dir: Path, kernel_files: list[str]) -> tuple[str, str]:
    """Return unique kernel symbols and observed SASS binary versions."""
    names: set[str] = set()
    versions: set[str] = set()
    for name in kernel_files:
        path = trace_dir / name
        try:
            with path.open("rt", errors="replace") as handle:
                for _ in range(16):
                    line = handle.readline()
                    if not line:
                        break
                    if line.startswith("-kernel name ="):
                        names.add(line.split("=", 1)[1].strip())
                    elif line.startswith("-binary version ="):
                        versions.add(line.split("=", 1)[1].strip())
        except OSError:
            names.add("<missing-trace-file>")
    return ";".join(sorted(names)) or "MISSING", ";".join(sorted(versions)) or "MISSING"


def nearest_provenance(trace_dir: Path, root: Path) -> tuple[Path | None, dict]:
    current = trace_dir
    while True:
        candidate = current / "provenance.json"
        if candidate.is_file():
            try:
                return candidate, json.loads(candidate.read_text())
            except (OSError, json.JSONDecodeError):
                return candidate, {}
        if current == root or current.parent == current:
            return None, {}
        current = current.parent


def provenance_text(doc: dict, key: str) -> str:
    value = doc.get(key)
    if value is None:
        return "MISSING"
    if isinstance(value, str):
        return " ".join(value.split())
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def family(path: Path) -> str:
    text = str(path).lower()
    if "trace-fraction" in text or "1of40" in text or "1of10" in text:
        return "trimmed-derived"
    if ".incomplete" in text or ".interrupted" in text or ".failed" in text or ".partial" in text:
        return "incomplete-or-failed"
    if "tls-c2p" in text or "tls-cache" in text or "c2p-" in text:
        return "V100-NVBit-staged"
    if "bank-diagnosis" in text:
        return "historical-diagnosis-copy"
    if "pretraces" in text:
        return "public-pretrace"
    return "other-local-copy"


def suite_and_input(trace_dir: Path) -> tuple[str, str, str]:
    parts = trace_dir.parts
    joined = "/".join(parts).lower()
    suite = "UNKNOWN"
    for token, name in (
        ("/cudasdk/", "CUDA SDK"),
        ("/ubench/", "Accel-Sim ubench"),
        ("/rodinia", "Rodinia"),
        ("/parboil/", "Parboil"),
        ("/polybench/", "PolyBench"),
        ("/cutlass/", "CUTLASS"),
        ("/tls-shoc-", "SHOC"),
        ("/tls-mars-", "Mars"),
        ("/c2p-ispass-", "ISPASS"),
        ("/c2p-pannotia-", "Pannotia"),
    ):
        if token in joined:
            suite = name
            break
    app = trace_dir.parent.name
    input_name = trace_dir.name
    # Standard extracted archive layout ends .../<application>/<input>/traces.
    if trace_dir.name == "traces":
        app = trace_dir.parent.parent.name
        input_name = trace_dir.parent.name
    return suite, app, input_name


def trace_sha_from_sums(trace_dir: Path, root: Path) -> str:
    """Use only an explicit SHA256SUMS entry; otherwise truthfully mark missing."""
    current = trace_dir
    while True:
        sums = current / "SHA256SUMS"
        if sums.is_file():
            try:
                entries = sums.read_text(errors="replace")
            except OSError:
                entries = ""
            matches = re.findall(r"^([0-9a-fA-F]{64})\s+\*?(.+)$", entries, re.M)
            trace_names = {p.name for p in trace_dir.glob("*.traceg")}
            found = [digest.lower() for digest, name in matches if Path(name).name in trace_names]
            if found:
                return ";".join(sorted(found))
        if current == root or current.parent == current:
            break
        current = current.parent
    return "MISSING (no recorded per-trace SHA256)"


def trace_instruction_metadata(trace_dir: Path) -> tuple[int | str, str]:
    """Return NVBit's trace-side reported instruction total when available."""
    stats = trace_dir / "stats.csv"
    if not stats.is_file():
        return "MISSING", "MISSING stats.csv"
    total = 0
    rows = 0
    try:
        with stats.open(newline="", errors="replace") as handle:
            for row in csv.DictReader(handle):
                normalized = {(key or "").strip(): value for key, value in row.items()}
                value = normalized.get("total_reported_insts") or normalized.get("total_insts")
                if value is None:
                    continue
                total += int(value.strip())
                rows += 1
    except (OSError, ValueError):
        return "MISSING", "unparseable stats.csv"
    return (total if rows else "MISSING"), ("available" if rows else "empty stats.csv")


def same_tree_result(trace_dir: Path) -> str:
    """Do not infer a cross-campaign match; record only an adjacent result file."""
    for candidate in (trace_dir.parent / "result.txt", trace_dir.parent / "run.out",
                      trace_dir.parent / "summary.txt"):
        if candidate.is_file():
            return str(candidate)
    return "MISSING (no result adjacent to this trace asset)"


def record(klist: Path, root: Path) -> dict[str, str | int]:
    trace_dir = klist.parent
    lines = klist.read_text(errors="replace").splitlines()
    kernel_files = [line.strip() for line in lines if line.strip().endswith(".traceg")]
    present = [trace_dir / name for name in kernel_files if (trace_dir / name).is_file()]
    kernel_names, binary_versions = first_kernel_metadata(trace_dir, kernel_files)
    provenance_path, provenance = nearest_provenance(trace_dir, root)
    suite, app, input_name = suite_and_input(trace_dir)
    bytes_total = sum(item.stat().st_size for item in present)
    trace_reported_insts, stats_status = trace_instruction_metadata(trace_dir)
    missing_files = len(kernel_files) - len(present)
    status = "directly runnable" if not missing_files else "NOT runnable: referenced trace missing"
    if family(trace_dir) == "incomplete-or-failed":
        status = "DO NOT RUN without review: incomplete/failed staging copy"
    return {
        "suite": suite,
        "application": app,
        "input_or_dataset": input_name,
        "asset_family": family(trace_dir),
        "trace_list": str(klist),
        "trace_tree_bytes": bytes_total,
        "kernel_count": len(kernel_files),
        "trace_reported_insts": trace_reported_insts,
        "trace_stats_status": stats_status,
        "same_tree_historical_result": same_tree_result(trace_dir),
        "kernel_symbols": kernel_names,
        "sass_binary_version": binary_versions,
        "trace_sha256": trace_sha_from_sums(trace_dir, root),
        "kernelslist_sha256": sha256(klist),
        "runnable_status": status,
        "missing_kernel_files": missing_files,
        "provenance_path": str(provenance_path) if provenance_path else "MISSING",
        "tracer_sha256": provenance_text(provenance, "tracer_sha256"),
        "cuda_nvcc": provenance_text(provenance, "nvcc"),
        "capture_gpu": provenance_text(provenance, "nvidia_smi"),
        "capture_case": provenance_text(provenance, "case"),
        "framework_at_capture": provenance_text(provenance, "framework_commit"),
        "provenance_missing": "yes" if provenance_path is None else "no",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", action="append", type=Path, default=[])
    args = parser.parse_args()
    roots = args.root or list(DEFAULT_ROOTS)
    rows = []
    for root in roots:
        if not root.is_dir():
            continue
        for klist in sorted(root.rglob("kernelslist.g")):
            rows.append(record(klist, root))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)
    print(f"wrote {len(rows)} trace roots to {args.output}")


if __name__ == "__main__":
    main()
