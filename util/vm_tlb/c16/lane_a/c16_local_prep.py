#!/usr/bin/env python3
"""CPU-only C16 lane-A asset and input closure helpers.

This tool deliberately has no model-loading, CUDA, profiler, NVBit, or
simulator path.  It records immutable model assets and tokenizer-derived token
IDs that a separately authorized native-GPU lane may later consume.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


OUTPUT_ROOT = Path("docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_a")
METADATA_ROOT = Path("/workspace/c16_assets/c16-a/metadata")
LLAMA_ROOT = Path("/workspace/model/meta-llama__Llama-3.2-1B_main")
TOKEN_TARGETS = (128, 256, 2048, 8192)
INPUTS = (
    ("TEXT", "TEXT.txt"),
    ("CODE", "CODE.py"),
    ("STRUCTURED", "STRUCTURED.json"),
)
WAVE1_DEPLOYMENT_IDS = frozenset(
    {
        "c16_llama32_1b_frozen_compatible",
        "c16_qwen25_05b_native_reference",
        "c16_qwen25_7b_raw_reference",
        "c16_qwen25_7b_awq",
    }
)
PLANNING_SHA = "f222e66f49af56cfd4ded671c4a50c6811237cc2"
STAGE_ACCEPTANCE = Path("docs/vm_tlb/chatgpt_handoff/c16_multimodel_native/C16_STAGE_ACCEPTANCE.tsv")
G_FINAL_COMMIT = "45e293b84940ef59b7b134bcda48aca7d0b99b2f"
C_FINAL_COMMIT = "29e669eca19ac3b2a1350bf2d097569a41f123e1"
H_FINAL_COMMIT = "932c6fa44a4896265214fc2136e34698402a5c7f"
G_PUBLISH_PATH = Path("docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_g/PUBLISH_MANIFEST.json")
C_PUBLISH_PATH = Path("docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_c/PUBLISH_MANIFEST.json")
H_PUBLISH_PATH = Path("docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/PUBLISH_MANIFEST.json")
G_LANE_ROOT = G_PUBLISH_PATH.parent
C_LANE_ROOT = C_PUBLISH_PATH.parent
H_LANE_ROOT = H_PUBLISH_PATH.parent
G_WHEELHOUSE_ROOT = Path("/workspace/c16_assets/wheelhouse/c16-g-cp310-cu124")


@dataclass(frozen=True)
class Deployment:
    deployment_id: str
    model_id: str
    revision: str
    variant: str
    local_path: Path
    local_origin: str


DEPLOYMENTS = (
    Deployment(
        "c16_llama32_1b_frozen_compatible",
        "meta-llama/Llama-3.2-1B",
        "4e20de362430cd3b72f300e6b0f18e50e7166e08",
        "frozen-compatible-runtime",
        LLAMA_ROOT,
        "PREEXISTING_LOCAL_FROZEN_CHECKPOINT",
    ),
    Deployment(
        "c16_qwen25_05b_native_reference",
        "Qwen/Qwen2.5-0.5B-Instruct",
        "7ae557604adf67be50417f59c2c2f167def9a775",
        "native_reference",
        METADATA_ROOT / "Qwen__Qwen2.5-0.5B-Instruct__7ae557604adf67be50417f59c2c2f167def9a775",
        "LOCAL_CHECKPOINT_DOWNLOADED_AND_SHA256_VERIFIED",
    ),
    Deployment(
        "c16_qwen25_7b_raw_reference",
        "Qwen/Qwen2.5-7B-Instruct",
        "a09a35458c702b33eeacc393d103063234e8bc28",
        "raw_reference",
        METADATA_ROOT / "Qwen__Qwen2.5-7B-Instruct__a09a35458c702b33eeacc393d103063234e8bc28",
        "LOCAL_CHECKPOINT_DOWNLOAD_IN_PROGRESS_PENDING_WHOLE_FILE_SHA256",
    ),
    Deployment(
        "c16_qwen25_7b_awq",
        "Qwen/Qwen2.5-7B-Instruct-AWQ",
        "b25037543e9394b818fdfca67ab2a00ecc7dd641",
        "awq",
        METADATA_ROOT / "Qwen__Qwen2.5-7B-Instruct-AWQ__b25037543e9394b818fdfca67ab2a00ecc7dd641",
        "LOCAL_CHECKPOINT_DOWNLOAD_PARTIAL_PENDING_REMAINING_WHOLE_FILE_SHA256",
    ),
    Deployment(
        "c16_qwen3_8b_native_reference",
        "Qwen/Qwen3-8B",
        "b968826d9c46dd6066d109eabc6255188de91218",
        "native_reference",
        METADATA_ROOT / "Qwen__Qwen3-8B__b968826d9c46dd6066d109eabc6255188de91218",
        "HF_METADATA_TOKENIZER_ONLY",
    ),
    Deployment(
        "c16_qwen3_30b_a3b_native_moe",
        "Qwen/Qwen3-30B-A3B",
        "ad44e777bcd18fa416d9da3bd8f70d33ebb85d39",
        "native_moe",
        METADATA_ROOT / "Qwen__Qwen3-30B-A3B__ad44e777bcd18fa416d9da3bd8f70d33ebb85d39",
        "HF_METADATA_TOKENIZER_ONLY",
    ),
    Deployment(
        "c16_deepseek_v2_lite_native_runtime",
        "deepseek-ai/DeepSeek-V2-Lite",
        "604d5664dddd88a0433dbae533b7fe9472482de0",
        "native_runtime",
        Path("/root/share/workspace_migrated_20260905/model-cache/DeepSeek-V2-Lite"),
        "PREEXISTING_LOCAL_CHECKPOINT_REQUIRES_SHA_AND_REVISION_CROSSCHECK",
    ),
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical_json_bytes(value) + b"\n")
    temporary.replace(path)


def atomic_tsv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def repeat_to_length(token_ids: list[int], target: int) -> list[int]:
    if not token_ids:
        raise ValueError("tokenizer produced no token IDs")
    if target <= 0:
        raise ValueError("target must be positive")
    return (token_ids * ((target + len(token_ids) - 1) // len(token_ids)))[:target]


def source_inputs(output_root: Path) -> list[tuple[str, Path, bytes]]:
    result = []
    for input_class, filename in INPUTS:
        path = output_root / "inputs" / filename
        data = path.read_bytes()
        result.append((input_class, path, data))
    return result


def local_asset_files(deployment: Deployment) -> list[Path]:
    if not deployment.local_path.is_dir():
        raise FileNotFoundError(deployment.local_path)
    allowed = {
        "config.json",
        "generation_config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "merges.txt",
        "vocab.json",
        "tokenizer.model",
        "model.safetensors.index.json",
        "configuration_deepseek.py",
        "modeling_deepseek.py",
        "tokenization_deepseek_fast.py",
        "model.safetensors",
    }
    return sorted(
        path
        for path in deployment.local_path.iterdir()
        if path.is_file()
        and (path.name in allowed or path.name.endswith(".safetensors"))
    )


def asset_role(filename: str) -> str:
    if filename.endswith(".safetensors"):
        return "CHECKPOINT_FILE"
    if filename.endswith(".index.json"):
        return "WEIGHT_INDEX"
    if filename.endswith(".py"):
        return "REMOTE_IMPLEMENTATION_SOURCE"
    if filename.startswith("tokenizer") or filename in {"merges.txt", "vocab.json", "special_tokens_map.json"}:
        return "TOKENIZER_ASSET"
    return "CONFIGURATION_ASSET"


def remote_weight_rows(deployment: Deployment) -> list[dict[str, str]]:
    if deployment.model_id == "meta-llama/Llama-3.2-1B":
        return []
    try:
        from huggingface_hub import HfApi
    except ImportError as exc:  # pragma: no cover - operator setup error
        raise SystemExit("huggingface_hub is required for --record-assets") from exc
    api = HfApi()
    paths = []
    for item in api.list_repo_tree(deployment.model_id, revision=deployment.revision, recursive=True):
        path = getattr(item, "path", "")
        if path.endswith(".safetensors"):
            paths.append(path)
    infos = []
    for start in range(0, len(paths), 32):
        infos.extend(api.get_paths_info(deployment.model_id, paths=paths[start : start + 32], revision=deployment.revision, expand=True))
    rows = []
    for item in sorted(infos, key=lambda candidate: candidate.path):
        if item.lfs is None or not item.lfs.sha256:
            raise RuntimeError(f"missing immutable LFS SHA-256 for {deployment.model_id}:{item.path}")
        rows.append(
            {
                "deployment_id": deployment.deployment_id,
                "asset_role": "CHECKPOINT_FILE",
                "source_repo": deployment.model_id,
                "source_revision": deployment.revision,
                "tokenizer_revision": deployment.revision,
                "asset_path": item.path,
                "local_path": "NA",
                "size_bytes": str(item.size),
                "sha256": item.lfs.sha256,
                "verification_status": "REMOTE_LFS_SHA256_DECLARED_NOT_LOCAL",
                "transfer_required": "YES",
                "notes": "NOT_YET_ACCEPTED_AS_LOCAL_CHECKPOINT_AT_MANIFEST_WRITE",
            }
        )
    return rows


def record_assets(output_root: Path) -> None:
    fields = [
        "deployment_id", "asset_role", "source_repo", "source_revision", "tokenizer_revision", "asset_path", "local_path",
        "size_bytes", "sha256", "verification_status", "transfer_required", "notes",
    ]
    all_rows: list[dict[str, str]] = []
    receipt_root = output_root / "MODEL_ASSET_RECEIPTS"
    for deployment in DEPLOYMENTS:
        local_rows = []
        for path in local_asset_files(deployment):
            local_rows.append(
                {
                    "deployment_id": deployment.deployment_id,
                    "asset_role": asset_role(path.name),
                    "source_repo": deployment.model_id,
                    "source_revision": deployment.revision,
                    "tokenizer_revision": deployment.revision,
                    "asset_path": path.name,
                    "local_path": str(path),
                    "size_bytes": str(path.stat().st_size),
                    "sha256": sha256_file(path),
                    "verification_status": "LOCAL_SHA256_VERIFIED",
                    "transfer_required": "YES",
                    "notes": deployment.local_origin,
                }
            )
        declared_remote_rows = remote_weight_rows(deployment)
        local_checkpoint_rows = {row["asset_path"]: row for row in local_rows if row["asset_role"] == "CHECKPOINT_FILE"}
        if local_checkpoint_rows:
            for local_row in local_rows:
                local_row["notes"] = f"{deployment.local_origin}; LOCAL_CHECKPOINT_FILES_PRESENT"
        remote_rows = []
        for remote_row in declared_remote_rows:
            local_row = local_checkpoint_rows.get(remote_row["asset_path"])
            if local_row is None:
                remote_rows.append(remote_row)
                continue
            if local_row["sha256"] != remote_row["sha256"] or local_row["size_bytes"] != remote_row["size_bytes"]:
                raise RuntimeError(
                    f"local checkpoint does not match immutable LFS declaration: "
                    f"{deployment.model_id}:{remote_row['asset_path']}"
                )
            local_row["verification_status"] = "LOCAL_SHA256_VERIFIED_AGAINST_IMMUTABLE_REMOTE_LFS"
            local_row["notes"] = (
                f"{deployment.local_origin}; LOCAL_CHECKPOINT_FILES_PRESENT; "
                "REMOTE_LFS_SHA256_MATCHED"
            )
        if deployment.model_id != "meta-llama/Llama-3.2-1B" and not (local_checkpoint_rows or remote_rows):
            raise RuntimeError(f"no checkpoint identity found for {deployment.model_id}")
        local_checkpoint_bytes = sum(
            int(row["size_bytes"])
            for row in local_rows
            if row["asset_role"] == "CHECKPOINT_FILE"
        )
        remote_checkpoint_bytes = sum(int(row["size_bytes"]) for row in remote_rows)
        receipt = {
            "schema_version": "C16_MODEL_ASSET_RECEIPT_V1",
            "planning_sha": PLANNING_SHA,
            "deployment_id": deployment.deployment_id,
            "model_id": deployment.model_id,
            "revision": deployment.revision,
            "tokenizer_revision": deployment.revision,
            "local_rows": local_rows,
            "remote_weight_rows": remote_rows,
            "local_file_total_bytes": sum(int(row["size_bytes"]) for row in local_rows),
            "local_checkpoint_total_bytes": local_checkpoint_bytes,
            "remote_checkpoint_total_bytes": remote_checkpoint_bytes,
            "checkpoint_presence": (
                "LOCAL_CHECKPOINT_FILES_PRESENT"
                if local_checkpoint_bytes
                else "NO_LOCAL_CHECKPOINT_FILES_PRESENT"
            ),
            "execution_boundary": "CPU_ONLY_ASSET_HASHING_NO_GPU_PROFILER_NVBIT_OR_SIMULATOR",
        }
        atomic_json(receipt_root / f"{deployment.deployment_id}.json", receipt)
        all_rows.extend(local_rows + remote_rows)
    atomic_tsv(output_root / "MODEL_ASSET_MANIFEST.tsv", fields, all_rows)


def tokenize(output_root: Path) -> None:
    try:
        import transformers
        from transformers import AutoTokenizer
    except ImportError as exc:  # pragma: no cover - operator setup error
        raise SystemExit("transformers is required for --tokenize") from exc
    corpus_rows = []
    for input_class, path, raw in source_inputs(output_root):
        corpus_rows.append(
            {
                "input_id": f"c16_{input_class.lower()}_v1",
                "input_class": input_class,
                "raw_path": str(path.relative_to(output_root)),
                "raw_sha256": sha256_bytes(raw),
                "raw_size_bytes": str(len(raw)),
                "tokenization_policy": "AutoTokenizer local_files_only=true; trust_remote_code=false; add_special_tokens=false; repeat_then_trim",
            }
        )
    atomic_tsv(
        output_root / "INPUT_CORPUS.tsv",
        ["input_id", "input_class", "raw_path", "raw_sha256", "raw_size_bytes", "tokenization_policy"],
        corpus_rows,
    )
    for deployment in DEPLOYMENTS:
        tokenizer = AutoTokenizer.from_pretrained(deployment.local_path, local_files_only=True, trust_remote_code=False)
        tokenizer_hashes = {path.name: sha256_file(path) for path in local_asset_files(deployment) if asset_role(path.name) == "TOKENIZER_ASSET"}
        for input_class, path, raw in source_inputs(output_root):
            source_ids = tokenizer.encode(raw.decode("utf-8"), add_special_tokens=False)
            if not source_ids:
                raise RuntimeError(f"empty source tokenization: {deployment.deployment_id}/{input_class}")
            for target in TOKEN_TARGETS:
                target_ids = repeat_to_length(source_ids, target)
                receipt = {
                    "schema_version": "C16_TOKEN_RECEIPT_V1",
                    "planning_sha": PLANNING_SHA,
                    "deployment_id": deployment.deployment_id,
                    "model_id": deployment.model_id,
                    "model_revision": deployment.revision,
                    "tokenizer_class": tokenizer.__class__.__name__,
                    "transformers_version": transformers.__version__,
                    "input_id": f"c16_{input_class.lower()}_v1",
                    "input_class": input_class,
                    "raw_path": str(path.relative_to(output_root)),
                    "raw_sha256": sha256_bytes(raw),
                    "add_special_tokens": False,
                    "derivation": "repeat encoded source token IDs then trim exactly to target_prefill_tokens",
                    "source_token_ids": source_ids,
                    "source_token_ids_sha256": sha256_bytes(canonical_json_bytes(source_ids)),
                    "target_prefill_tokens": target,
                    "target_token_ids": target_ids,
                    "target_token_ids_sha256": sha256_bytes(canonical_json_bytes(target_ids)),
                    "tokenizer_asset_sha256": tokenizer_hashes,
                }
                atomic_json(receipt_root := output_root / "TOKEN_RECEIPTS" / deployment.deployment_id / f"{input_class}_T{target}.json", receipt)


def validate_assets(output_root: Path) -> list[str]:
    failures = []
    manifest_path = output_root / "MODEL_ASSET_MANIFEST.tsv"
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows:
        failures.append("asset manifest is empty")
    for row in rows:
        if len(row["source_revision"]) != 40:
            failures.append(f"bad revision {row['deployment_id']}:{row['asset_path']}")
        if len(row["sha256"]) != 64:
            failures.append(f"bad SHA-256 {row['deployment_id']}:{row['asset_path']}")
        if row["verification_status"].startswith("LOCAL_SHA256_VERIFIED"):
            path = Path(row["local_path"])
            if not path.is_file() or sha256_file(path) != row["sha256"]:
                failures.append(f"local asset hash mismatch {path}")
        elif row["verification_status"] != "REMOTE_LFS_SHA256_DECLARED_NOT_LOCAL":
            failures.append(f"unknown asset verification status {row['verification_status']}")
    return failures


def validate_tokens(output_root: Path) -> list[str]:
    failures = []
    expected = len(DEPLOYMENTS) * len(INPUTS) * len(TOKEN_TARGETS)
    receipts = sorted((output_root / "TOKEN_RECEIPTS").glob("*/*.json"))
    if len(receipts) != expected:
        failures.append(f"expected {expected} token receipts, found {len(receipts)}")
    for path in receipts:
        value = json.loads(path.read_text(encoding="utf-8"))
        source = value["source_token_ids"]
        target = value["target_token_ids"]
        wanted = value["target_prefill_tokens"]
        raw_path = output_root / value["raw_path"]
        if len(target) != wanted or target != repeat_to_length(source, wanted):
            failures.append(f"invalid token derivation {path}")
        if sha256_bytes(canonical_json_bytes(target)) != value["target_token_ids_sha256"]:
            failures.append(f"target SHA mismatch {path}")
        if not raw_path.is_file() or sha256_file(raw_path) != value["raw_sha256"]:
            failures.append(f"raw input SHA mismatch {path}")
    return failures


def validate_wave1_local(output_root: Path) -> list[str]:
    """Require actual local, whole-file-verified checkpoint coverage for Wave-1.

    This is intentionally stricter than generic asset validation: remote LFS
    declarations remain useful identity records for optional Wave-2 assets, but
    cannot close the primary transfer package.
    """
    failures = []
    with (output_root / "MODEL_ASSET_MANIFEST.tsv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    by_deployment = {deployment_id: [] for deployment_id in WAVE1_DEPLOYMENT_IDS}
    for row in rows:
        if row["deployment_id"] in by_deployment and row["asset_role"] == "CHECKPOINT_FILE":
            by_deployment[row["deployment_id"]].append(row)
    for deployment_id, checkpoint_rows in by_deployment.items():
        if not checkpoint_rows:
            failures.append(f"missing Wave-1 checkpoint rows for {deployment_id}")
            continue
        for row in checkpoint_rows:
            if row["verification_status"] == "REMOTE_LFS_SHA256_DECLARED_NOT_LOCAL":
                failures.append(f"Wave-1 checkpoint is remote-only {deployment_id}:{row['asset_path']}")
                continue
            if not row["verification_status"].startswith("LOCAL_SHA256_VERIFIED"):
                failures.append(f"Wave-1 checkpoint has unaccepted status {deployment_id}:{row['asset_path']}")
                continue
            local_path = Path(row["local_path"])
            if not local_path.is_file() or local_path.stat().st_size != int(row["size_bytes"]):
                failures.append(f"Wave-1 checkpoint local path/size mismatch {deployment_id}:{row['asset_path']}")
    return failures


def write_stage_status(output_root: Path) -> None:
    """Materialize one honest integration-status row per common C16 stage."""
    with STAGE_ACCEPTANCE.open(encoding="utf-8", newline="") as handle:
        stages = list(csv.DictReader(handle, delimiter="\t"))
    package_ready = all(
        (output_root / filename).is_file()
        for filename in ("C16_GPU_PACKAGE_MANIFEST.tsv", "EXPECTED_HASHES.tsv", "TRANSFER_PLAN.md")
    )
    p0_ready = (output_root / "packages" / "C16_GPU_PACKAGE_P0" / "PACKAGE_IDENTITY.json").is_file()
    status = {
        "C16-0.0": ("EXECUTED_PASS", "PROVENANCE_CLOSED", "C16_BASELINE_MANIFEST.json;C15_A_CLOSEOUT_RECEIPT.md", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "C15 remains read-only static/offline evidence"),
        "C16-0.1": ("EXECUTED_PASS", "SELECTION_FROZEN_NO_RESULTS", "MODEL_MATRIX.tsv;MODEL_SELECTION_RATIONALE.md", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "no candidate outcome used for selection"),
        "C16-0.2": ("IN_PROGRESS_LOCAL_WAVE1_DOWNLOAD", "ASSET_IDENTITY_PARTIAL", "MODEL_ASSET_MANIFEST.tsv;MODEL_ASSET_RECEIPTS/;EXECUTION_RECEIPTS.md", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "each Wave-1 checkpoint file must be locally present and SHA-256-verified before PASS; remote LFS declarations alone are insufficient"),
        "C16-0.3": ("EXECUTED_PASS", "OFFLINE_WHEEL_ENV_CLOSURE_ONLY", "G@45e293b84940ef59b7b134bcda48aca7d0b99b2f; manifest=7c18c2a8; 17/17 release payloads and 66/66 local wheel hashes pass", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "offline wheel/env closure is not a GPU runtime or native measurement"),
        "C16-0.4": ("EXECUTED_PASS", "OFFLINE_RUNNER_CLOSURE_ONLY", "G@45e293b84940ef59b7b134bcda48aca7d0b99b2f; manifest=7c18c2a8; 17/17 release payloads pass", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "runner wrapper closure is not permission to launch a GPU instance"),
        "C16-0.5": ("EXECUTED_PASS", "OFFLINE_ADMISSION_PROTOCOL_ONLY", "H@932c6fa44a4896265214fc2136e34698402a5c7f; manifest=b7821231; 5/5 payloads pass", "NA", "H hardening is final-consumed only as an offline protocol; it has no dynamic scientific rows"),
        "C16-0.6": ("EXECUTED_PASS", "INPUT_IDENTITY_CLOSED", "INPUT_CORPUS.tsv;TOKEN_RECEIPTS/", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "token IDs are CPU tokenizer results, not runtime outputs"),
        "C16-0.7": ("EXECUTED_PASS", "SCENARIOS_FROZEN_NOT_EXECUTED", "SCENARIO_MATRIX.tsv;SCENARIO_POLICY.md", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "resource admission and actual backend identity remain G duties"),
        "C16-0.8": ("EXECUTED_PASS", "OFFLINE_PROTOCOL_FINAL_CONSUMED", "G@45e293b84940ef59b7b134bcda48aca7d0b99b2f;C@29e669eca19ac3b2a1350bf2d097569a41f123e1;H@932c6fa44a4896265214fc2136e34698402a5c7f", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "all three fixed manifests are hash-validated; this is offline tool closure, not a dynamic result"),
        "C16-0.9": (
            ("EXECUTED_PASS", "TRANSFER_PACKAGE_HASH_CLOSED", "C16_GPU_PACKAGE_MANIFEST.tsv;EXPECTED_HASHES.tsv;TRANSFER_PLAN.md", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "package closure is transfer preparation only; it starts no GPU, profiler, NVBit, simulator, SASS, or full-ROI work")
            if package_ready
            else ("EXECUTED_PARTIAL_P0", "LLAMA_ONLY_TRANSFER_PACKAGE", "packages/C16_GPU_PACKAGE_P0/", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "immutable P0 contains only the fully local Llama checkpoint and may support only separately authorized Llama import/canary work; it does not close multi-model C16-0.9")
            if p0_ready
            else ("WAITING_WAVE1_LOCAL_ASSET_CLOSURE", "NOT_EXECUTED", "C16_GPU_PACKAGE_READINESS.md;TRANSFER_PREREQUISITES.tsv;EXECUTION_RECEIPTS.md", "NA", "G/C/H fixed reconsumption is complete, but package publication, PASS, and AutoDL advice remain prohibited until every Wave-1 checkpoint file is local and whole-file SHA-256-verified")
        ),
        "C16-3.1": ("EXECUTED_PASS", "OFFLINE_SCHEMA_BOUNDARY_ONLY", "C@29e669eca19ac3b2a1350bf2d097569a41f123e1; manifest=14a7c029", "NA", "final-consumed offline selector schema; no native fact table"),
        "C16-3.2": ("EXECUTED_PASS", "OFFLINE_SELECTOR_BOUNDARY_ONLY", "C@29e669eca19ac3b2a1350bf2d097569a41f123e1; manifest=14a7c029", "NA", "no candidate outcome used; future application needs a committed Wave-1 catalog"),
        "C16-3.3": ("EXECUTED_PASS", "OFFLINE_ESTIMATOR_BOUNDARY_ONLY", "C@29e669eca19ac3b2a1350bf2d097569a41f123e1; manifest=14a7c029", "NA", "fixture conservation does not qualify a native metric"),
        "C16-3.4": ("EXECUTED_PASS", "OFFLINE_BUDGET_BOUNDARY_ONLY", "C@29e669eca19ac3b2a1350bf2d097569a41f123e1; manifest=14a7c029", "NA", "capture cost fields are not observed provider costs"),
        "C16-3.5": ("EXECUTED_PASS", "RETROSPECTIVE_ORACLE_BOUNDARY_ONLY", "C@29e669eca19ac3b2a1350bf2d097569a41f123e1; manifest=14a7c029", "NA", "C12/C13 mode=0 only; no blind or native claim"),
        "C16-3.6": ("WAITING_WAVE1_PACKAGE", "PENDING", "C@29e669eca19ac3b2a1350bf2d097569a41f123e1; manifest=14a7c029", "NA", "requires A's committed Wave-1 package before a prospective holdout catalog exists"),
        "C16-4.2": ("WAITING_WAVE1_PACKAGE", "PENDING", "G@45e293b84940ef59b7b134bcda48aca7d0b99b2f;C@29e669eca19ac3b2a1350bf2d097569a41f123e1;H@932c6fa44a4896265214fc2136e34698402a5c7f", "NA", "offline inputs are final-consumed, but no native target identity exists"),
        "C16-5.4": ("WAITING_INPUT", "NOT_QUALIFIED", "COMMON_PATTERN_AUDIT.tsv", "NA", "no fixed C16 native/fingerprint/qualification inputs; no common pattern claimed"),
        "C16-6.1": ("EXECUTED_PASS", "METRIC_BY_METRIC_BOUNDARY_PUBLISHED", "C@29e669eca19ac3b2a1350bf2d097569a41f123e1; manifest=14a7c029", "NA", "final-consumed qualification schema; no global sampler PASS and no native metric qualification"),
        "C16-6.2": ("WAITING_INPUT", "PARTIAL_COST_LEDGER_ONLY", "C16_COST_MODEL.tsv", "NA", "G 2.6/4.3 and C 6.1 are unavailable; all unknown costs are NA"),
        "C16-6.3": ("WAITING_INPUT", "UNCLUSTERED_NOT_QUALIFIED", "BEHAVIOR_CLASSES.md", "NA", "no qualified cross-model metrics; no forced taxonomy"),
        "C16-6.4": ("PARTIAL_READY_FOR_FINAL_REVIEW", "NO_NEW_DYNAMIC_CONCLUSION", "FINAL_REPORT.md;NEXT_HIGH_FIDELITY_REQUESTS.md", "NA", "future high-fidelity requests require new authorization; no auto-launch"),
    }
    fields = ["stage_id", "owner", "execution_status", "scientific_status", "evidence_commit_or_receipt", "cost_status", "limitation"]
    rows = []
    for stage in stages:
        stage_id = stage["stage_id"]
        values = status.get(
            stage_id,
            (
                "WAITING_PRODUCER_PUBLISH",
                "NOT_EXECUTED",
                "NO_FIXED_C16_G_C_H_PRODUCER_ARTIFACT",
                "NA",
                "producer branch currently resolves only to common planning SHA; live partial is not consumed",
            ),
        )
        rows.append({"stage_id": stage_id, "owner": stage["owner"], "execution_status": values[0], "scientific_status": values[1], "evidence_commit_or_receipt": values[2], "cost_status": values[3], "limitation": values[4]})
    atomic_tsv(output_root / "C16_STAGE_STATUS.tsv", fields, rows)


def validate_stage_status(output_root: Path) -> list[str]:
    failures = []
    with STAGE_ACCEPTANCE.open(encoding="utf-8", newline="") as handle:
        expected = [row["stage_id"] for row in csv.DictReader(handle, delimiter="\t")]
    with (output_root / "C16_STAGE_STATUS.tsv").open(encoding="utf-8", newline="") as handle:
        observed = [row["stage_id"] for row in csv.DictReader(handle, delimiter="\t")]
    if expected != observed:
        failures.append("stage-status rows do not exactly match C16_STAGE_ACCEPTANCE.tsv")
    return failures


def read_tsv_bytes(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(data.decode("utf-8").splitlines(), delimiter="\t"))


def git_blob(commit: str, path: Path | str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"])


def require_git_blob(commit: str, path: Path | str, expected_sha256: str, expected_size: int | None = None) -> bytes:
    data = git_blob(commit, path)
    actual_sha256 = sha256_bytes(data)
    if actual_sha256 != expected_sha256:
        raise RuntimeError(f"git payload SHA-256 mismatch {commit}:{path}: {actual_sha256}")
    if expected_size is not None and len(data) != expected_size:
        raise RuntimeError(f"git payload size mismatch {commit}:{path}: {len(data)}")
    return data


def validate_final_fixed_releases() -> dict[str, object]:
    """Validate only the three final commit-bound C16 producer releases.

    This function intentionally reads Git objects and the already-prepared local
    G wheelhouse. It does not look at a live producer worktree and has no GPU
    execution path.
    """
    releases = {
        "G": (G_FINAL_COMMIT, G_PUBLISH_PATH, G_LANE_ROOT),
        "C": (C_FINAL_COMMIT, C_PUBLISH_PATH, C_LANE_ROOT),
        "H": (H_FINAL_COMMIT, H_PUBLISH_PATH, H_LANE_ROOT),
    }
    values: dict[str, object] = {}
    for lane, (commit, publish_path, lane_root) in releases.items():
        manifest_bytes = git_blob(commit, publish_path)
        manifest = json.loads(manifest_bytes)
        if manifest.get("planning_sha") != PLANNING_SHA:
            raise RuntimeError(f"{lane} planning SHA mismatch")
        if lane in {"G", "C"}:
            for item in manifest["files"]:
                require_git_blob(commit, lane_root / item["path"], item["sha256"], item["size_bytes"])
        else:
            for path, expected_sha256 in manifest["code_sha256"].items():
                require_git_blob(commit, path, expected_sha256)
            receipt = manifest["test_receipt"]
            require_git_blob(commit, lane_root / receipt["path"], receipt["sha256"])
        values[lane] = {
            "commit": commit,
            "manifest_path": str(publish_path),
            "manifest_sha256": sha256_bytes(manifest_bytes),
            "manifest": manifest,
        }

    g_manifest = values["G"]["manifest"]  # type: ignore[index]
    g_package_bytes = git_blob(G_FINAL_COMMIT, G_LANE_ROOT / "C16_GPU_PACKAGE_MANIFEST.tsv")
    g_package_rows = read_tsv_bytes(g_package_bytes)
    source_sizes = {}
    for row in g_package_rows:
        if row["package_component"].startswith("G_SOURCE_"):
            source_sizes[row["package_component"]] = len(require_git_blob(
                G_FINAL_COMMIT, row["path_or_ref"], row["sha256"]
            ))
    wheel_manifest_bytes = (G_WHEELHOUSE_ROOT / "WHEELHOUSE_MANIFEST.tsv").read_bytes()
    expected_wheel_manifest_sha256 = next(
        row["sha256"] for row in g_package_rows if row["package_component"] == "G_LOCAL_WHEELHOUSE_MANIFEST"
    )
    if sha256_bytes(wheel_manifest_bytes) != expected_wheel_manifest_sha256:
        raise RuntimeError("local G wheelhouse manifest SHA-256 mismatch")
    wheel_rows = read_tsv_bytes(wheel_manifest_bytes)
    for row in wheel_rows:
        path = G_WHEELHOUSE_ROOT / row["wheel_filename"]
        if not path.is_file() or path.stat().st_size != int(row["size_bytes"]) or sha256_file(path) != row["sha256"]:
            raise RuntimeError(f"local G wheel mismatch {path}")
    values["G"]["package_rows"] = g_package_rows  # type: ignore[index]
    values["G"]["source_sizes"] = source_sizes  # type: ignore[index]
    values["G"]["wheel_rows"] = wheel_rows  # type: ignore[index]
    values["G"]["wheel_manifest_sha256"] = expected_wheel_manifest_sha256  # type: ignore[index]
    return values


def package_row(
    artifact_id: str,
    kind: str,
    requiredness: str,
    source_ref: str,
    local_path: str,
    destination_relpath: str,
    size_bytes: str,
    sha256: str,
    verification_status: str,
    transfer_action: str,
    notes: str,
) -> dict[str, str]:
    return {
        "artifact_id": artifact_id,
        "kind": kind,
        "requiredness": requiredness,
        "source_ref": source_ref,
        "local_path": local_path,
        "destination_relpath": destination_relpath,
        "size_bytes": size_bytes,
        "sha256": sha256,
        "verification_status": verification_status,
        "transfer_action": transfer_action,
        "notes": notes,
    }


def local_row_package_entry(row: dict[str, str], requiredness: str) -> dict[str, str]:
    path = Path(row["local_path"])
    if not path.is_file() or path.stat().st_size != int(row["size_bytes"]) or sha256_file(path) != row["sha256"]:
        raise RuntimeError(f"local rolling-package asset mismatch {row['deployment_id']}:{row['asset_path']}")
    if not row["verification_status"].startswith("LOCAL_SHA256_VERIFIED"):
        raise RuntimeError(f"unaccepted rolling-package asset {row['deployment_id']}:{row['asset_path']}")
    return package_row(
        f"{row['deployment_id']}:{row['asset_path']}", "MODEL_ASSET", requiredness,
        f"{row['source_repo']}@{row['source_revision']};tokenizer@{row['tokenizer_revision']}", row["local_path"],
        f"models/{row['deployment_id']}/{row['asset_path']}", row["size_bytes"], row["sha256"], row["verification_status"],
        "RSYNC_FILE_WITH_SHA256_RECHECK", row["notes"],
    )


def write_rolling_gpu_package(output_root: Path, package_id: str, deployment_id: str) -> None:
    """Publish one immutable, single-deployment rolling GPU package delta.

    P0 is intentionally permitted to include only Llama's already-accepted
    assets while Qwen downloads continue. The function refuses any local
    temporary file, remote-only row, or pre-existing package directory.
    """
    if package_id not in {"C16_GPU_PACKAGE_P0", "C16_GPU_PACKAGE_P1", "C16_GPU_PACKAGE_P2", "C16_GPU_PACKAGE_P3"}:
        raise RuntimeError(f"unsupported rolling package identity {package_id}")
    package_root = output_root / "packages" / package_id
    if package_root.exists():
        raise RuntimeError(f"immutable rolling package already exists: {package_root}")
    with (output_root / "MODEL_ASSET_MANIFEST.tsv").open(encoding="utf-8", newline="") as handle:
        asset_rows = list(csv.DictReader(handle, delimiter="\t"))
    model_rows = [row for row in asset_rows if row["deployment_id"] == deployment_id]
    if not model_rows:
        raise RuntimeError(f"unknown deployment for rolling package {deployment_id}")
    if any(row["local_path"] == "NA" for row in model_rows):
        raise RuntimeError(f"rolling package has remote-only asset rows for {deployment_id}")
    checkpoint_rows = [row for row in model_rows if row["asset_role"] == "CHECKPOINT_FILE"]
    if not checkpoint_rows:
        raise RuntimeError(f"rolling package has no checkpoint rows for {deployment_id}")
    rows = [local_row_package_entry(row, "REQUIRED_DEPLOYMENT_DELTA") for row in model_rows]
    for path in sorted((output_root / "inputs").glob("*")):
        if path.is_file():
            rows.append(package_row(f"A_INPUT:{path.name}", "FROZEN_INPUT", "REQUIRED_DEPLOYMENT_DELTA", "A_FIXED_INPUT", str(path), f"a_assets/inputs/{path.name}", str(path.stat().st_size), sha256_file(path), "LOCAL_SHA256_VERIFIED", "RSYNC_FILE_WITH_SHA256_RECHECK", "frozen raw input"))
    control_paths = [output_root / "INPUT_CORPUS.tsv", output_root / "SCENARIO_MATRIX.tsv", output_root / "SCENARIO_POLICY.md"]
    control_paths.extend(sorted((output_root / "TOKEN_RECEIPTS" / deployment_id).glob("*.json")))
    for path in control_paths:
        if not path.is_file():
            raise RuntimeError(f"missing rolling-package input/scenario receipt {path}")
        rows.append(package_row(f"A_RECEIPT:{path.relative_to(output_root)}", "A_INPUT_OR_SCENARIO_RECEIPT", "REQUIRED_DEPLOYMENT_DELTA", "A_FIXED_RECEIPT", str(path), f"a_assets/{path.relative_to(output_root)}", str(path.stat().st_size), sha256_file(path), "LOCAL_SHA256_VERIFIED", "RSYNC_FILE_WITH_SHA256_RECHECK", "frozen CPU-only input/scenario evidence"))
    releases = validate_final_fixed_releases()
    for row in releases["G"]["package_rows"]:  # type: ignore[index]
        component = row["package_component"]
        if component.startswith("G_SOURCE_"):
            source_path = row["path_or_ref"]
            rows.append(package_row(component, "G_COMMITTED_SOURCE", "REQUIRED_DEPLOYMENT_DELTA", f"git:{G_FINAL_COMMIT}:{source_path}", "NA", f"g_source/{source_path}", str(releases["G"]["source_sizes"][component]), row["sha256"], "GIT_BLOB_SHA256_VERIFIED", "GIT_ARCHIVE_OR_RSYNC_NAMED_SOURCE", "final fixed G runner/environment source"))  # type: ignore[index]
    rows.append(package_row("G_WHEELHOUSE_MANIFEST", "G_WHEELHOUSE_MANIFEST", "REQUIRED_DEPLOYMENT_DELTA", "G_FINAL_WHEELHOUSE", str(G_WHEELHOUSE_ROOT / "WHEELHOUSE_MANIFEST.tsv"), "wheelhouse/WHEELHOUSE_MANIFEST.tsv", str((G_WHEELHOUSE_ROOT / "WHEELHOUSE_MANIFEST.tsv").stat().st_size), releases["G"]["wheel_manifest_sha256"], "LOCAL_SHA256_VERIFIED", "RSYNC_FILE_WITH_SHA256_RECHECK", "all 66 wheel entries are separately validated by the fixed G release validator"))  # type: ignore[index]
    for lane in ("G", "C", "H"):
        release = releases[lane]
        rows.append(package_row(f"{lane}_PUBLISH_MANIFEST", "FIXED_RELEASE_PROVENANCE", "REQUIRED_PROVENANCE", f"git:{release['commit']}:{release['manifest_path']}", "NA", f"provenance/{lane}_PUBLISH_MANIFEST.json", "NA", release["manifest_sha256"], "GIT_BLOB_SHA256_VERIFIED", "GIT_ARCHIVE_OR_RSYNC_NAMED_SOURCE", "fixed cross-lane release manifest; no live partial input"))
    fields = ["artifact_id", "kind", "requiredness", "source_ref", "local_path", "destination_relpath", "size_bytes", "sha256", "verification_status", "transfer_action", "notes"]
    package_root.mkdir(parents=True)
    atomic_tsv(package_root / "C16_GPU_PACKAGE_MANIFEST.tsv", fields, rows)
    expected_rows = [
        {"artifact_id": row["artifact_id"], "kind": row["kind"], "requiredness": row["requiredness"], "path_or_ref": row["local_path"] if row["local_path"] != "NA" else row["source_ref"], "size_bytes": row["size_bytes"], "sha256": row["sha256"], "closure_status": row["verification_status"], "note": row["notes"]}
        for row in rows
    ]
    atomic_tsv(package_root / "EXPECTED_HASHES.tsv", ["artifact_id", "kind", "requiredness", "path_or_ref", "size_bytes", "sha256", "closure_status", "note"], expected_rows)
    atomic_text(package_root / "TRANSFER_PLAN.md", f"# {package_id} transfer plan\n\nThis immutable rolling package is limited to `{deployment_id}`. It contains no `.incomplete`, `.curl.download`, remote-only, live-worktree, GPU, profiler, NVBit, simulator, SASS, or full-ROI artifact.\n\n1. Materialize Git rows only from their exact commits in `EXPECTED_HASHES.tsv`; rsync local rows to their listed relative destination.\n2. Recheck every size and SHA-256 in `EXPECTED_HASHES.tsv` before model import. A mismatch is quarantined and blocks import.\n3. This P0/P1/P2/P3 plan is transfer/import preparation only. It does not itself launch a GPU workload or make a dynamic scientific claim.\n")
    payloads = []
    for path in sorted(package_root.iterdir()):
        if path.is_file():
            payloads.append({"path": path.name, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    package_manifest = {
        "schema_version": "C16_A_ROLLING_GPU_PACKAGE_V1",
        "package_id": package_id,
        "planning_sha": PLANNING_SHA,
        "deployment_id": deployment_id,
        "model_revision": model_rows[0]["source_revision"],
        "tokenizer_revision": model_rows[0]["tokenizer_revision"],
        "cross_lane_fixed_inputs": {lane: {"commit": releases[lane]["commit"], "manifest_sha256": releases[lane]["manifest_sha256"]} for lane in ("G", "C", "H")},
        "g_wheelhouse_manifest_sha256": releases["G"]["wheel_manifest_sha256"],
        "payloads": payloads,
        "execution_boundary": "TRANSFER_ONLY_NO_GPU_PROFILER_NVBIT_SIMULATOR_SASS_OR_FULL_ROI",
    }
    manifest_path = package_root / f"{package_id}_MANIFEST.json"
    atomic_json(manifest_path, package_manifest)
    atomic_json(package_root / "PACKAGE_IDENTITY.json", {
        "schema_version": "C16_A_ROLLING_PACKAGE_IDENTITY_V1",
        "package_id": package_id,
        "package_manifest": manifest_path.name,
        "package_manifest_sha256": sha256_file(manifest_path),
        "immutable_rule": "never modify this package directory; publish later model closures as a new P-numbered delta",
    })
    write_stage_status(output_root)


def validate_rolling_gpu_package(output_root: Path, package_id: str) -> list[str]:
    root = output_root / "packages" / package_id
    failures = []
    identity_path = root / "PACKAGE_IDENTITY.json"
    if not identity_path.is_file():
        return [f"missing rolling package identity {package_id}"]
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    manifest_path = root / identity["package_manifest"]
    if not manifest_path.is_file() or sha256_file(manifest_path) != identity["package_manifest_sha256"]:
        failures.append("rolling package manifest identity mismatch")
        return failures
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for payload in manifest["payloads"]:
        path = root / payload["path"]
        if not path.is_file() or path.stat().st_size != payload["size_bytes"] or sha256_file(path) != payload["sha256"]:
            failures.append(f"rolling package payload mismatch {payload['path']}")
    with (root / "C16_GPU_PACKAGE_MANIFEST.tsv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        if row["local_path"] != "NA":
            path = Path(row["local_path"])
            if not path.is_file() or path.stat().st_size != int(row["size_bytes"]) or sha256_file(path) != row["sha256"]:
                failures.append(f"rolling package local payload mismatch {row['artifact_id']}")
    return failures


def write_gpu_package(output_root: Path) -> None:
    """Write the C16-0.9 transfer package after strict local/offline gates.

    The function is purposefully CPU-only: it hashes local files and final
    fixed Git objects, but never imports a model or invokes CUDA tooling.
    """
    failures = validate_assets(output_root) + validate_tokens(output_root) + validate_wave1_local(output_root)
    if failures:
        raise RuntimeError("cannot publish C16 GPU package: " + "; ".join(failures))
    releases = validate_final_fixed_releases()
    with (output_root / "MODEL_ASSET_MANIFEST.tsv").open(encoding="utf-8", newline="") as handle:
        asset_rows = list(csv.DictReader(handle, delimiter="\t"))
    deployment_wave = {deployment.deployment_id: ("W1" if deployment.deployment_id in WAVE1_DEPLOYMENT_IDS else "W2") for deployment in DEPLOYMENTS}
    rows: list[dict[str, str]] = []
    for row in asset_rows:
        wave = deployment_wave[row["deployment_id"]]
        if row["local_path"] == "NA":
            if wave == "W1":
                raise RuntimeError(f"Wave-1 remote-only asset reached package writer: {row['deployment_id']}:{row['asset_path']}")
            rows.append(package_row(
                f"{row['deployment_id']}:{row['asset_path']}", "MODEL_ASSET", "OPTIONAL_WAVE2", f"{row['source_repo']}@{row['source_revision']}",
                "NA", "NA", row["size_bytes"], row["sha256"], row["verification_status"], "DO_NOT_TRANSFER_NOT_LOCAL",
                "optional Wave-2 remote identity only; not treated as a local asset",
            ))
            continue
        requiredness = "REQUIRED_WAVE1" if wave == "W1" else "OPTIONAL_WAVE2"
        rows.append(package_row(
            f"{row['deployment_id']}:{row['asset_path']}", "MODEL_ASSET", requiredness,
            f"{row['source_repo']}@{row['source_revision']};tokenizer@{row['tokenizer_revision']}", row["local_path"],
            f"models/{row['deployment_id']}/{row['asset_path']}", row["size_bytes"], row["sha256"], row["verification_status"],
            "RSYNC_FILE_WITH_SHA256_RECHECK", row["notes"],
        ))
    for path in sorted((output_root / "inputs").glob("*")):
        if path.is_file():
            rows.append(package_row(f"A_INPUT:{path.name}", "FROZEN_INPUT", "REQUIRED_WAVE1", "A_FIXED_INPUT", str(path), f"a_assets/inputs/{path.name}", str(path.stat().st_size), sha256_file(path), "LOCAL_SHA256_VERIFIED", "RSYNC_FILE_WITH_SHA256_RECHECK", "frozen raw input"))
    for path in [output_root / "INPUT_CORPUS.tsv", output_root / "SCENARIO_MATRIX.tsv", output_root / "SCENARIO_POLICY.md"] + sorted((output_root / "TOKEN_RECEIPTS").glob("*/*.json")):
        rows.append(package_row(f"A_RECEIPT:{path.relative_to(output_root)}", "A_INPUT_OR_SCENARIO_RECEIPT", "REQUIRED_WAVE1", "A_FIXED_RECEIPT", str(path), f"a_assets/{path.relative_to(output_root)}", str(path.stat().st_size), sha256_file(path), "LOCAL_SHA256_VERIFIED", "RSYNC_FILE_WITH_SHA256_RECHECK", "CPU-only frozen input/scenario evidence"))

    g_rows = releases["G"]["package_rows"]  # type: ignore[index]
    for row in g_rows:
        component = row["package_component"]
        if component.startswith("G_SOURCE_"):
            source_path = row["path_or_ref"]
            source_size = releases["G"]["source_sizes"][component]  # type: ignore[index]
            rows.append(package_row(component, "G_COMMITTED_SOURCE", "REQUIRED_WAVE1", f"git:{G_FINAL_COMMIT}:{source_path}", "NA", f"g_source/{source_path}", str(source_size), row["sha256"], "GIT_BLOB_SHA256_VERIFIED", "GIT_ARCHIVE_OR_RSYNC_NAMED_SOURCE", "final fixed G runner/environment source"))
    for row in releases["G"]["wheel_rows"]:  # type: ignore[index]
        filename = row["wheel_filename"]
        path = G_WHEELHOUSE_ROOT / filename
        rows.append(package_row(f"G_WHEEL:{filename}", "G_OFFLINE_WHEEL", "REQUIRED_WAVE1", "G_FINAL_WHEELHOUSE", str(path), f"wheelhouse/{filename}", row["size_bytes"], row["sha256"], "LOCAL_SHA256_VERIFIED", "RSYNC_FILE_WITH_SHA256_RECHECK", "fixed G CP310 Linux x86_64 wheel"))
    for lane in ("G", "C", "H"):
        release = releases[lane]
        rows.append(package_row(f"{lane}_PUBLISH_MANIFEST", "FIXED_RELEASE_PROVENANCE", "REQUIRED_PROVENANCE", f"git:{release['commit']}:{release['manifest_path']}", "NA", f"provenance/{lane}_PUBLISH_MANIFEST.json", "NA", release["manifest_sha256"], "GIT_BLOB_SHA256_VERIFIED", "GIT_ARCHIVE_OR_RSYNC_NAMED_SOURCE", "fixed cross-lane manifest; no live partial input"))

    fields = ["artifact_id", "kind", "requiredness", "source_ref", "local_path", "destination_relpath", "size_bytes", "sha256", "verification_status", "transfer_action", "notes"]
    atomic_tsv(output_root / "C16_GPU_PACKAGE_MANIFEST.tsv", fields, rows)
    expected_rows = [
        {
            "artifact_id": row["artifact_id"], "kind": row["kind"], "requiredness": row["requiredness"], "path_or_ref": row["local_path"] if row["local_path"] != "NA" else row["source_ref"],
            "size_bytes": row["size_bytes"], "sha256": row["sha256"], "closure_status": row["verification_status"], "note": row["notes"],
        }
        for row in rows
        if row["transfer_action"] != "DO_NOT_TRANSFER_NOT_LOCAL"
    ]
    atomic_tsv(output_root / "EXPECTED_HASHES.tsv", ["artifact_id", "kind", "requiredness", "path_or_ref", "size_bytes", "sha256", "closure_status", "note"], expected_rows)
    atomic_text(
        output_root / "TRANSFER_PLAN.md",
        "# C16 transfer plan — hash-closed local package\n\n"
        "Status: `C16_LOCAL_GPU_PACKAGE_READY`; this document authorizes no GPU, profiler, NVBit, simulator, SASS, or full-ROI execution. It only names files that a separately authorized transfer/import procedure must verify.\n\n"
        "Fixed cross-lane inputs: G `45e293b84940ef59b7b134bcda48aca7d0b99b2f` / manifest `7c18c2a806ac37b974702050567430f83f10bbdacc78c5af2fe09ea871896087`; "
        "C `29e669eca19ac3b2a1350bf2d097569a41f123e1` / manifest `14a7c02985d13203bf90d251751ae6ab50c3159ce28e439b51917e05204f9f04`; "
        "H `932c6fa44a4896265214fc2136e34698402a5c7f` / manifest `b78212310628b479e78636c3d7b42ea4a4d5d9d635115e8b7af79e05b4a88d9c`.\n\n"
        "1. Transfer only rows in `C16_GPU_PACKAGE_MANIFEST.tsv` whose action is `RSYNC_FILE_WITH_SHA256_RECHECK` or `GIT_ARCHIVE_OR_RSYNC_NAMED_SOURCE`; preserve the listed destination relative path.\n"
        "2. On the destination, compare every transferred local file against `EXPECTED_HASHES.tsv` before any model import. Git-sourced rows must be materialized from their exact recorded commit and rehashed.\n"
        "3. Retain optional Wave-2 rows only when their local source is present; `DO_NOT_TRANSFER_NOT_LOCAL` means remote identity only and must not be silently downloaded on rented GPU.\n"
        "4. A mismatch is quarantined and blocks model import. This A package supplies no GPU launch decision or scientific conclusion.\n",
    )
    write_stage_status(output_root)


def validate_gpu_package(output_root: Path) -> list[str]:
    failures = []
    package_path = output_root / "C16_GPU_PACKAGE_MANIFEST.tsv"
    expected_path = output_root / "EXPECTED_HASHES.tsv"
    transfer_path = output_root / "TRANSFER_PLAN.md"
    if not all(path.is_file() for path in (package_path, expected_path, transfer_path)):
        return ["missing one or more formal C16-0.9 package artifacts"]
    with package_path.open(encoding="utf-8", newline="") as handle:
        package_rows = list(csv.DictReader(handle, delimiter="\t"))
    with expected_path.open(encoding="utf-8", newline="") as handle:
        expected_rows = list(csv.DictReader(handle, delimiter="\t"))
    if not package_rows or not expected_rows:
        failures.append("empty package or expected-hash ledger")
    expected_ids = {row["artifact_id"] for row in expected_rows}
    for row in package_rows:
        if row["transfer_action"] == "DO_NOT_TRANSFER_NOT_LOCAL":
            if row["requiredness"] == "REQUIRED_WAVE1":
                failures.append(f"remote-only required Wave-1 row {row['artifact_id']}")
            continue
        if row["artifact_id"] not in expected_ids:
            failures.append(f"missing expected-hash row {row['artifact_id']}")
        if row["local_path"] != "NA":
            path = Path(row["local_path"])
            if not path.is_file() or path.stat().st_size != int(row["size_bytes"]) or sha256_file(path) != row["sha256"]:
                failures.append(f"local package payload mismatch {row['artifact_id']}")
    failures.extend(validate_wave1_local(output_root))
    failures.extend(validate_final_fixed_releases_error())
    if "no GPU, profiler, NVBit, simulator, SASS, or full-ROI execution" not in transfer_path.read_text(encoding="utf-8"):
        failures.append("transfer-plan execution boundary missing")
    return failures


def validate_final_fixed_releases_error() -> list[str]:
    try:
        validate_final_fixed_releases()
    except (RuntimeError, subprocess.CalledProcessError, KeyError, OSError) as exc:
        return [f"final fixed release validation failed: {exc}"]
    return []


def write_publish_manifest(output_root: Path, artifact_checkpoint: str) -> None:
    """Publish only this hash-bound local-prep review package.

    This is intentionally distinct from the contract's future GPU-package
    manifest: unavailable G/C/H gates remain unavailable after publication.
    """
    files = []
    for path in sorted(output_root.rglob("*")):
        if not path.is_file() or path.name == "PUBLISH_MANIFEST.json":
            continue
        files.append(
            {
                "path": str(path.relative_to(output_root)),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    manifest = {
        "schema_version": "C16_A_LOCAL_PREP_PUBLISH_V1",
        "status": "C16_A_ASSET_DOWNLOAD_AND_ROLLING_PACKAGE_IN_PROGRESS",
        "planning_sha": PLANNING_SHA,
        "local_prep_artifact_checkpoint": "42d12e149314d00c230ecfa9b8e9e3c39084bf5d",
        "integration_base_checkpoint": "2a06944c359a9873ae72c89015eb5235dda2d2ee",
        "integration_producer_checkpoint": artifact_checkpoint,
        "scope": "C15 provenance closure, fixed G/C/H offline integration, immutable Wave-1 rolling packages, and continuing local Wave-1/Wave-2 asset download; C16-0.9 remains blocked until locally verified Wave-1 assets are simultaneously available",
        "files": files,
        "gates_not_satisfied": ["C16-0.2", "C16-0.9", "C16-5.4", "C16-6.2", "C16-6.3"],
        "prohibitions_honored": [
            "NO_UNVERIFIED_CHECKPOINT_ACCEPTANCE",
            "NO_GPU_OR_CUDA_MODEL_EXECUTION",
            "NO_PROFILER_NVBIT_SIMULATOR_SASS_OR_FULL_ROI",
            "NO_LIVE_PARTIAL_CROSS_LANE_CONSUMPTION",
        ],
    }
    atomic_json(output_root / "PUBLISH_MANIFEST.json", manifest)


def validate_publish_manifest(output_root: Path) -> list[str]:
    failures = []
    manifest_path = output_root / "PUBLISH_MANIFEST.json"
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    if value.get("status") != "C16_A_ASSET_DOWNLOAD_AND_ROLLING_PACKAGE_IN_PROGRESS":
        failures.append("unexpected publish status")
    for key in ("local_prep_artifact_checkpoint", "integration_base_checkpoint", "integration_producer_checkpoint"):
        if len(value.get(key, "")) != 40:
            failures.append(f"{key} is not immutable")
    for item in value.get("files", []):
        path = output_root / item["path"]
        if not path.is_file() or path.stat().st_size != item["size_bytes"] or sha256_file(path) != item["sha256"]:
            failures.append(f"publish payload mismatch {item['path']}")
    return failures


def selftest() -> list[str]:
    failures = []
    if repeat_to_length([1, 2, 3], 8) != [1, 2, 3, 1, 2, 3, 1, 2]:
        failures.append("repeat_to_length positive case")
    for ids, target in (([], 1), ([1], 0)):
        try:
            repeat_to_length(ids, target)
        except ValueError:
            pass
        else:
            failures.append("repeat_to_length rejected input")
    if sha256_bytes(canonical_json_bytes([1, 2, 3])) != sha256_bytes(b"[1,2,3]"):
        failures.append("canonical JSON identity")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--record-assets", action="store_true")
    parser.add_argument("--tokenize", action="store_true")
    parser.add_argument("--write-stage-status", action="store_true")
    parser.add_argument("--write-publish-manifest", metavar="ARTIFACT_CHECKPOINT")
    parser.add_argument("--write-gpu-package", action="store_true")
    parser.add_argument("--write-rolling-package", nargs=2, metavar=("PACKAGE_ID", "DEPLOYMENT_ID"))
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--validate-wave1-local", action="store_true")
    parser.add_argument("--validate-gpu-package", action="store_true")
    parser.add_argument("--validate-rolling-package", metavar="PACKAGE_ID")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if not any((args.record_assets, args.tokenize, args.write_stage_status, args.write_publish_manifest, args.write_gpu_package, args.write_rolling_package, args.validate, args.validate_wave1_local, args.validate_gpu_package, args.validate_rolling_package, args.selftest)):
        parser.error("choose at least one operation")
    failures = []
    if args.selftest:
        failures.extend(selftest())
        print("C16A_T01", "PASS" if not failures else "FAIL")
    if args.record_assets:
        record_assets(args.output_root)
        print("C16A_T02 PASS")
    if args.tokenize:
        tokenize(args.output_root)
        print("C16A_T03 PASS")
    if args.write_stage_status:
        write_stage_status(args.output_root)
        print("C16A_T05 PASS")
    if args.write_publish_manifest:
        write_publish_manifest(args.output_root, args.write_publish_manifest)
        print("C16A_T09 PASS")
    if args.write_gpu_package:
        write_gpu_package(args.output_root)
        print("C16A_T07 PASS")
    if args.write_rolling_package:
        write_rolling_gpu_package(args.output_root, *args.write_rolling_package)
        print("C16A_T07_ROLLING PASS")
    if args.validate:
        failures.extend(validate_assets(args.output_root))
        failures.extend(validate_tokens(args.output_root))
        failures.extend(validate_stage_status(args.output_root))
        if (args.output_root / "PUBLISH_MANIFEST.json").is_file():
            failures.extend(validate_publish_manifest(args.output_root))
        print("C16A_T04", "PASS" if not failures else "FAIL")
    if args.validate_wave1_local:
        wave1_failures = validate_wave1_local(args.output_root)
        failures.extend(wave1_failures)
        print("C16A_T06", "PASS" if not wave1_failures else "FAIL")
    if args.validate_gpu_package:
        package_failures = validate_gpu_package(args.output_root)
        failures.extend(package_failures)
        print("C16A_T08", "PASS" if not package_failures else "FAIL")
    if args.validate_rolling_package:
        rolling_failures = validate_rolling_gpu_package(args.output_root, args.validate_rolling_package)
        failures.extend(rolling_failures)
        print("C16A_T08_ROLLING", "PASS" if not rolling_failures else "FAIL")
    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
