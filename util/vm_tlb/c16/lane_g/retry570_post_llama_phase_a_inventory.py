#!/usr/bin/env python3
"""Materialize the bounded post-Llama Phase-A identity/asset inventory.

No model, torch, GPU, or downloader is imported.  The inventory searches only
the handoff-authorized metadata roots, consumes immutable A package manifests,
and records an upstream reachability probe separately from asset retrieval.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file


SCHEMA = "C16_G_RETRY570_POST_LLAMA_PHASE_A_INVENTORY_V1"
MODEL_MARKER = re.compile(r"qwen|deepseek|glm|chatglm", re.IGNORECASE)
METADATA_NAMES = {"config.json", "generation_config.json", "adapter_config.json"}
PACKAGES = (
    ("qwen_0p5", "4e73a1d0f435ba4d1dae1a9e749b8b82e54b7f63", "C16_GPU_PACKAGE_P1", "d8ac3ca44c4344b9a5fa752ba5a6549c007e901b26b426c9713b4d7e8749eb84"),
    ("qwen_7b_awq", "168c97148ef2bbfaf9bbe199414b0e7a5fc3ed1d", "C16_GPU_PACKAGE_P3", "704dc320a131e31a6d9fd11a8ac623318777c832b0b699241c5bf3f1c8beda1c"),
)


def git_bytes(commit: str, path: str) -> bytes:
    try:
        return subprocess.check_output(["git", "show", f"{commit}:{path}"])
    except subprocess.CalledProcessError as exc:
        raise ContractError(f"authoritative project object is absent: {commit}:{path}") from exc


def package_identity(commit: str, package_id: str, expected_sha: str) -> dict[str, Any]:
    root = f"docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_a/packages/{package_id}"
    path = f"{root}/{package_id}_MANIFEST.json"; raw = git_bytes(commit, path)
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise ContractError(f"{package_id} authority manifest SHA differs")
    authority = json.loads(raw)
    tsv_row = next((row for row in authority["payloads"] if row["path"] == "C16_GPU_PACKAGE_MANIFEST.tsv"), None)
    if not isinstance(tsv_row, dict): raise ContractError(f"{package_id} authority lacks model-payload TSV")
    tsv = git_bytes(commit, f"{root}/{tsv_row['path']}")
    if len(tsv) != tsv_row["size_bytes"] or hashlib.sha256(tsv).hexdigest() != tsv_row["sha256"]:
        raise ContractError(f"{package_id} model-payload TSV differs from authority")
    rows = [line.split("\t") for line in tsv.decode("utf-8").splitlines()]
    model_rows = [row for row in rows if len(row) >= 8 and row[1] == "MODEL_ASSET"]
    identities = {row[3] for row in model_rows}
    if len(identities) != 1: raise ContractError(f"{package_id} has no unique model identity")
    model_identity = next(iter(identities)); model, revision = model_identity.split("@", 1)[0], model_identity.split("@", 1)[1].split(";", 1)[0]
    return {"package_id": package_id, "package_commit": commit, "package_manifest_sha256": expected_sha, "exact_model_id": model, "revision": revision, "payload_count": len(model_rows), "expected_model_bytes": sum(int(row[6]) for row in model_rows), "payload_manifest_sha256": tsv_row["sha256"]}


def bounded_metadata(roots: list[Path]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for root in roots:
        if not root.is_dir(): continue
        for current, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [name for name in dirs if name not in {".git", "node_modules"}]
            for name in files:
                if name not in METADATA_NAMES: continue
                path = Path(current) / name
                if not MODEL_MARKER.search(str(path)): continue
                try: found.append({"path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
                except OSError: continue
    return sorted(found, key=lambda row: row["path"])


def upstream_reachability() -> dict[str, str]:
    try:
        with urllib.request.urlopen("https://huggingface.co", timeout=5) as response:
            return {"status": "REACHABLE", "http_status": str(response.status)}
    except Exception as exc:
        return {"status": "NETWORK_UNREACHABLE", "exception_type": type(exc).__name__, "message": str(exc)[:240]}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-json", type=Path, required=True); p.add_argument("--output-tsv", type=Path, required=True); p.add_argument("--p3-attempt-stderr", type=Path, required=True)
    p.add_argument("--root", type=Path, action="append", required=True)
    args = p.parse_args()
    if args.output_json.exists() or args.output_tsv.exists(): raise ContractError("Phase-A inventory refuses to overwrite retained evidence")
    qwen = {key: package_identity(commit, package, manifest) for key, commit, package, manifest in PACKAGES}
    metadata = bounded_metadata(args.root)
    p3_error = args.p3_attempt_stderr.read_text(encoding="utf-8", errors="replace") if args.p3_attempt_stderr.is_file() else ""
    if "Network is unreachable" not in p3_error: raise ContractError("retained P3 failure evidence does not establish the network boundary")
    reachability = upstream_reachability()
    if reachability["status"] != "NETWORK_UNREACHABLE": raise ContractError("upstream reachability changed; do not publish a stale network blocker")
    deepseek = {"authoritative_static_candidate": "deepseek-ai/DeepSeek-V2-Lite@604d5664dddd88a0433dbae533b7fe9472482de0", "evidence": "C15 static-only model registry", "status": "BLOCKED_IDENTITY_UNRESOLVED_REQUIRES_USER", "reason": "No C16 exact tokenizer/input/runtime package establishes a runnable DeepSeek deployment."}
    glm = {"exact_model_id": "UNRESOLVED", "status": "BLOCKED_IDENTITY_UNRESOLVED_REQUIRES_USER", "reason": "No authoritative project model ID plus revision/content manifest was found; generic GLM is not an identity."}
    rows = [
        {"model_key": "qwen_0p5", "status": "IDENTITY_RECOVERED_ASSET_MISSING", "identity": qwen["qwen_0p5"], "reason": "Exact P1 identity recovered; no matching local config/asset; same-session upstream route is unavailable."},
        {"model_key": "qwen_7b_awq", "status": "IDENTITY_RECOVERED_ASSET_MISSING", "identity": qwen["qwen_7b_awq"], "reason": "Exact P3 AWQ identity recovered; no matching local config/asset; retained exact config fetch failed at NETWORK_UNREACHABLE."},
        {"model_key": "deepseek", "status": deepseek["status"], "identity": deepseek, "reason": deepseek["reason"]},
        {"model_key": "glm", "status": glm["status"], "identity": glm, "reason": glm["reason"]},
    ]
    value = {"schema_version": SCHEMA, "status": "PHASE_A_IDENTITY_ASSET_RECOVERY_COMPLETE_WITH_BLOCKERS", "scientific_eligible": False, "metadata_only": True, "authorized_roots": [str(root) for root in args.root], "matching_metadata": metadata, "upstream_reachability": reachability, "p3_fetch_failure": {"path": str(args.p3_attempt_stderr), "sha256": sha256_file(args.p3_attempt_stderr), "network_error_confirmed": True}, "models": rows, "no_gpu_or_model_execution": True}
    atomic_json(args.output_json, value)
    args.output_tsv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_tsv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("model_key", "status", "exact_model_id_or_candidate", "revision_or_content_manifest", "asset_source", "reason"), delimiter="\t")
        writer.writeheader()
        for row in rows:
            ident = row["identity"]
            writer.writerow({"model_key": row["model_key"], "status": row["status"], "exact_model_id_or_candidate": ident.get("exact_model_id", ident.get("authoritative_static_candidate", "UNRESOLVED")), "revision_or_content_manifest": ident.get("revision", "UNRESOLVED"), "asset_source": ident.get("package_id", ident.get("evidence", "NA")), "reason": row["reason"]})
    print("PASS PHASE_A_IDENTITY_ASSET_RECOVERY_COMPLETE_WITH_BLOCKERS")


if __name__ == "__main__":
    try: main()
    except ContractError as exc: raise SystemExit(f"FAIL post-Llama Phase-A inventory: {exc}")
