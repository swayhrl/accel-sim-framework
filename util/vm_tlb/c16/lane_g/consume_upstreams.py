#!/usr/bin/env python3
"""Consume only fixed, hash-verified C16 producer manifests; never live lanes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from c16_native_common import ContractError, atomic_json, repo_root
from prepare_gpu_package import DEFAULT_OUT, refresh_manifest


ROOT = repo_root()
REPO = ROOT
A_COMMIT = "b458225e"
C_COMMIT = "29e669ec"
H_COMMIT = "65b53574"
A_BASE = "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_a"
C_BASE = "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_c"
A_HANDOFF_RECEIPT = f"{A_BASE}/C16_A_HANDOFF_RECEIPT.md"
FIELDS = ("producer_lane", "fixed_commit", "artifact_checkpoint_or_producer", "manifest_path", "manifest_sha256", "verified_file_count", "consumption_status", "dynamic_eligibility", "reason")


def blob(commit: str, path: str) -> bytes:
    try:
        return subprocess.check_output(["git", "-C", str(REPO), "show", f"{commit}:{path}"])
    except subprocess.CalledProcessError as exc:
        raise ContractError(f"fixed Git object unavailable: {commit}:{path}") from exc


def verify_manifest_payload(manifest: dict[str, Any], base: str, read_blob: Callable[[str], bytes]) -> int:
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ContractError("producer manifest has no payload file list")
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("sha256"), str):
            raise ContractError("producer manifest has malformed payload entry")
        data = read_blob(f"{base}/{item['path']}")
        if hashlib.sha256(data).hexdigest() != item["sha256"] or len(data) != item.get("size_bytes"):
            raise ContractError(f"producer manifest mismatch: {item['path']}")
    return len(files)


def verify_lane(commit: str, base: str) -> tuple[dict[str, Any], str, int]:
    manifest_bytes = blob(commit, f"{base}/PUBLISH_MANIFEST.json")
    try:
        manifest = json.loads(manifest_bytes)
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid producer manifest JSON at {commit}:{base}") from exc
    count = verify_manifest_payload(manifest, base, lambda path: blob(commit, path))
    return manifest, hashlib.sha256(manifest_bytes).hexdigest(), count


def parse_a_integration_provenance(receipt: str) -> str:
    """Parse A's table-format integration anchors without accepting an unlabeled SHA."""
    artifact = re.search(r"C16 A integration artifact checkpoint\s*(?:\|\s*)?`([0-9a-f]{40})`", receipt)
    producer = re.search(r"C16 A integration producer checkpoint\s*(?:\|\s*)?`([0-9a-f]{40})`", receipt)
    if artifact is None or producer is None:
        raise ContractError("A handoff receipt lacks integration artifact/producer provenance")
    return f"integration_artifact={artifact.group(1)};integration_producer={producer.group(1)}"


def a_integration_provenance(commit: str) -> str:
    """Return the two A integration anchors only after verifying their receipt exists."""
    return parse_a_integration_provenance(blob(commit, A_HANDOFF_RECEIPT).decode("utf-8"))


def atomic_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def consume(out: Path) -> None:
    a, a_sha, a_count = verify_lane(A_COMMIT, A_BASE)
    c, c_sha, c_count = verify_lane(C_COMMIT, C_BASE)
    if a.get("status") != "C16_LOCAL_PREP_AND_INTEGRATION_PARTIAL_READY_FOR_FINAL_REVIEW":
        raise ContractError("unexpected A partial-package status")
    if c.get("native_catalog_consumed") is not False:
        raise ContractError("C manifest unexpectedly claims a native catalog")
    a_provenance = a_integration_provenance(A_COMMIT)
    target_plan = blob(C_COMMIT, f"{C_BASE}/NVBIT_TARGET_PLAN.tsv").decode("utf-8")
    if "PENDING_NATIVE_CATALOG" not in target_plan or "NOT_A_NATIVE_CAPTURE_TARGET" not in target_plan:
        raise ContractError("C target plan no longer explicitly awaits a native catalog")
    rows = [
        {"producer_lane": "A", "fixed_commit": A_COMMIT, "artifact_checkpoint_or_producer": a_provenance, "manifest_path": f"{A_BASE}/PUBLISH_MANIFEST.json", "manifest_sha256": a_sha, "verified_file_count": str(a_count), "consumption_status": "HASH_VERIFIED_METADATA_INPUTS_ONLY", "dynamic_eligibility": "NO_GPU_PACKAGE_OR_TRANSFER_AUTHORIZATION", "reason": "A integrates fixed G/C releases, but its C16 GPU package remains unpublished pending H manifest closure"},
        {"producer_lane": "C", "fixed_commit": C_COMMIT, "artifact_checkpoint_or_producer": str(c.get("producer_commit", "NA")), "manifest_path": f"{C_BASE}/PUBLISH_MANIFEST.json", "manifest_sha256": c_sha, "verified_file_count": str(c_count), "consumption_status": "HASH_VERIFIED_SELECTOR_PROTOCOL_ONLY", "dynamic_eligibility": "NO_NATIVE_NVBIT_TARGET_YET", "reason": "all current target rows await a committed G native catalog"},
        {"producer_lane": "H", "fixed_commit": H_COMMIT, "artifact_checkpoint_or_producer": "NA", "manifest_path": "NA", "manifest_sha256": "NA", "verified_file_count": "0", "consumption_status": "NOT_CONSUMED_MANIFEST_MISSING", "dynamic_eligibility": "NO_ADDRESS_INPUT", "reason": "H offline review pack has no C16 publish manifest; live/manifest-free consumption is forbidden"},
    ]
    atomic_tsv(out / "CONSUMED_INPUTS.tsv", rows)
    (out / "UPSTREAM_INPUT_AUDIT.md").write_text(
        "# C16 Lane G fixed upstream-input audit\n\n"
        f"A fixed commit `{A_COMMIT}` manifest verified {a_count} payload hashes. Its verified handoff provenance is `{a_provenance}`. It integrates fixed G/C releases, but remains a partial local-preparation publication while H's manifest closure is absent; it does not authorize a GPU transfer or rental.\n\n"
        f"C fixed commit `{C_COMMIT}` manifest verified {c_count} payload hashes. Its selector is consumed only as a protocol; every current NVBit row explicitly awaits a committed G native catalog, so it authorizes no capture target.\n\n"
        f"H fixed commit `{H_COMMIT}` has no C16 publish manifest at its documented review-pack path and is not consumed. No live partial or raw address data was read.\n",
        encoding="utf-8",
    )
    refresh_manifest(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    consume(args.output_dir)
    print(f"PASS C16 G fixed upstream manifest consumption: A={A_COMMIT}, C={C_COMMIT}; H intentionally not consumed")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 G upstream consumption: {exc}", file=sys.stderr)
        raise SystemExit(2)
