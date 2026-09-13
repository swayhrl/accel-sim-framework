#!/usr/bin/env python3
"""Bounded, metadata-first exact-asset search before any Recovery-V3 fetch.

The search never moves or deletes a source.  It only recognizes a candidate
when a caller-provided exact config SHA256 is present.  HF snapshots are
reported as cache roots (not movable snapshot leaves), preventing broken
../../blobs symlinks during later materialization.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file, valid_sha256


SCHEMA = "C16_G_RETRY570_RECOVERY_V3_ASSET_SEARCH_V1"
MAX_DEPTH = 8


def ancestors(path: Path, root: Path) -> int:
    try: return len(path.relative_to(root).parts)
    except ValueError: return MAX_DEPTH + 1


def directory_metrics(root: Path) -> tuple[int, int]:
    count = total = 0
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [name for name in dirs if name != ".git"]
        for name in files:
            path = Path(current) / name
            try:
                count += 1; total += path.stat().st_size
            except OSError:
                continue
    return count, total


def hf_cache_root(config: Path, root: Path) -> Path:
    """Return models--... cache root, never a snapshot leaf."""
    for parent in (config.parent, *config.parents):
        if parent.name.startswith("models--"):
            return parent
        if parent == root:
            break
    return config.parent


def search(roots: list[Path], expected_config_sha256: str) -> list[dict[str, Any]]:
    if not valid_sha256(expected_config_sha256):
        raise ContractError("exact asset search requires a 64-hex expected config SHA256")
    matches: list[dict[str, Any]] = []
    for root in roots:
        if not root.is_dir():
            continue
        for current, dirs, files in os.walk(root, followlinks=False):
            current_path = Path(current)
            if ancestors(current_path, root) > MAX_DEPTH:
                dirs[:] = []; continue
            dirs[:] = [name for name in dirs if name not in {".git", "node_modules"}]
            if "config.json" not in files:
                continue
            config = current_path / "config.json"
            try:
                actual = sha256_file(config)
            except OSError:
                continue
            if actual != expected_config_sha256:
                continue
            source_root = hf_cache_root(config, root)
            count, total = directory_metrics(source_root)
            is_hf = source_root.name.startswith("models--")
            matches.append({"config_path": str(config), "config_sha256": actual, "source_root": str(source_root),
                            "source_kind": "HUGGINGFACE_CACHE_REQUIRES_WHOLE_CACHE_COPY_OR_MATERIALIZATION" if is_hf else "MATERIALIZED_MODEL_DIRECTORY",
                            "file_count": count, "total_bytes": total, "destructive_move_forbidden": True,
                            "reuse_action": "COPY_OR_REFLINK_THEN_FILE_SHA_CLOSE" if not is_hf else "COPY_WHOLE_REPO_CACHE_OR_MATERIALIZE_THEN_FILE_SHA_CLOSE"})
    return sorted(matches, key=lambda row: row["config_path"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deployment", required=True); parser.add_argument("--model-id", required=True); parser.add_argument("--revision", required=True)
    parser.add_argument("--expected-config-sha256", required=True); parser.add_argument("--root", type=Path, action="append", required=True); parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ContractError("asset search refuses to overwrite retained evidence")
    if not args.revision or args.revision == "UNRESOLVED": raise ContractError("asset search requires an exact immutable revision")
    value = {"schema_version": SCHEMA, "status": "EXACT_ASSET_SOURCE_FOUND" if (matches := search(args.root, args.expected_config_sha256)) else "NO_LOCAL_EXACT_ASSET_FOUND",
             "scientific_eligible": False, "deployment": args.deployment, "model_id": args.model_id, "revision": args.revision,
             "expected_config_sha256": args.expected_config_sha256, "bounded_roots": [str(root) for root in args.root], "matches": matches,
             "next_action": "REUSE_WITH_NONDESTRUCTIVE_COPY_AND_FULL_MANIFEST_CLOSURE" if matches else "AUTHORIZED_EXACT_NETWORK_FETCH_ONLY_AFTER_THIS_RECEIPT"}
    atomic_json(args.output, value); print(f"PASS {value['status']}")


if __name__ == "__main__":
    try: main()
    except ContractError as exc: raise SystemExit(f"FAIL Recovery-V3 asset search: {exc}")
