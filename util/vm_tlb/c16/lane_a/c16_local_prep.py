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
PLANNING_SHA = "f222e66f49af56cfd4ded671c4a50c6811237cc2"
STAGE_ACCEPTANCE = Path("docs/vm_tlb/chatgpt_handoff/c16_multimodel_native/C16_STAGE_ACCEPTANCE.tsv")


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
        "HF_METADATA_TOKENIZER_ONLY",
    ),
    Deployment(
        "c16_qwen25_7b_raw_reference",
        "Qwen/Qwen2.5-7B-Instruct",
        "a09a35458c702b33eeacc393d103063234e8bc28",
        "raw_reference",
        METADATA_ROOT / "Qwen__Qwen2.5-7B-Instruct__a09a35458c702b33eeacc393d103063234e8bc28",
        "HF_METADATA_TOKENIZER_ONLY",
    ),
    Deployment(
        "c16_qwen25_7b_awq",
        "Qwen/Qwen2.5-7B-Instruct-AWQ",
        "b25037543e9394b818fdfca67ab2a00ecc7dd641",
        "awq",
        METADATA_ROOT / "Qwen__Qwen2.5-7B-Instruct-AWQ__b25037543e9394b818fdfca67ab2a00ecc7dd641",
        "HF_METADATA_TOKENIZER_ONLY",
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
        METADATA_ROOT / "deepseek-ai__DeepSeek-V2-Lite__604d5664dddd88a0433dbae533b7fe9472482de0",
        "HF_METADATA_TOKENIZER_ONLY",
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
        "model.safetensors",
    }
    return sorted(path for path in deployment.local_path.iterdir() if path.is_file() and path.name in allowed)


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
                "asset_path": item.path,
                "local_path": "NA",
                "size_bytes": str(item.size),
                "sha256": item.lfs.sha256,
                "verification_status": "REMOTE_LFS_SHA256_DECLARED_NOT_LOCAL",
                "transfer_required": "YES",
                "notes": "FULL_WEIGHT_NOT_DOWNLOADED_BY_C16_A",
            }
        )
    return rows


def record_assets(output_root: Path) -> None:
    fields = [
        "deployment_id", "asset_role", "source_repo", "source_revision", "asset_path", "local_path",
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
                    "asset_path": path.name,
                    "local_path": str(path),
                    "size_bytes": str(path.stat().st_size),
                    "sha256": sha256_file(path),
                    "verification_status": "LOCAL_SHA256_VERIFIED",
                    "transfer_required": "YES",
                    "notes": deployment.local_origin,
                }
            )
        remote_rows = remote_weight_rows(deployment)
        if deployment.model_id != "meta-llama/Llama-3.2-1B" and not remote_rows:
            raise RuntimeError(f"no remote weight files found for {deployment.model_id}")
        receipt = {
            "schema_version": "C16_MODEL_ASSET_RECEIPT_V1",
            "planning_sha": PLANNING_SHA,
            "deployment_id": deployment.deployment_id,
            "model_id": deployment.model_id,
            "revision": deployment.revision,
            "local_rows": local_rows,
            "remote_weight_rows": remote_rows,
            "prohibition": "NO_FULL_WEIGHT_DOWNLOAD_PERFORMED_BY_C16_A",
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
        if row["verification_status"] == "LOCAL_SHA256_VERIFIED":
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


def write_stage_status(output_root: Path) -> None:
    """Materialize one honest integration-status row per common C16 stage."""
    with STAGE_ACCEPTANCE.open(encoding="utf-8", newline="") as handle:
        stages = list(csv.DictReader(handle, delimiter="\t"))
    status = {
        "C16-0.0": ("EXECUTED_PASS", "PROVENANCE_CLOSED", "C16_BASELINE_MANIFEST.json;C15_A_CLOSEOUT_RECEIPT.md", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "C15 remains read-only static/offline evidence"),
        "C16-0.1": ("EXECUTED_PASS", "SELECTION_FROZEN_NO_RESULTS", "MODEL_MATRIX.tsv;MODEL_SELECTION_RATIONALE.md", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "no candidate outcome used for selection"),
        "C16-0.2": ("EXECUTED_PASS", "ASSET_IDENTITY_CLOSED", "MODEL_ASSET_MANIFEST.tsv;MODEL_ASSET_RECEIPTS/", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "non-Llama full weights are remote-SHA-addressable but not local"),
        "C16-0.6": ("EXECUTED_PASS", "INPUT_IDENTITY_CLOSED", "INPUT_CORPUS.tsv;TOKEN_RECEIPTS/", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "token IDs are CPU tokenizer results, not runtime outputs"),
        "C16-0.7": ("EXECUTED_PASS", "SCENARIOS_FROZEN_NOT_EXECUTED", "SCENARIO_MATRIX.tsv;SCENARIO_POLICY.md", "CPU_ONLY_NO_BILLABLE_RATE_RECORDED", "resource admission and actual backend identity remain G duties"),
        "C16-0.9": ("WAITING_INPUT", "NOT_EXECUTED", "C16_GPU_PACKAGE_READINESS.md;TRANSFER_PREREQUISITES.tsv", "NA", "fixed G 0.3/0.4 and C/H 0.8 releases are unavailable; package is intentionally unpublished"),
        "C16-5.4": ("WAITING_INPUT", "NOT_QUALIFIED", "COMMON_PATTERN_AUDIT.tsv", "NA", "no fixed C16 native/fingerprint/qualification inputs; no common pattern claimed"),
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
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if not any((args.record_assets, args.tokenize, args.write_stage_status, args.validate, args.selftest)):
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
    if args.validate:
        failures.extend(validate_assets(args.output_root))
        failures.extend(validate_tokens(args.output_root))
        failures.extend(validate_stage_status(args.output_root))
        print("C16A_T04", "PASS" if not failures else "FAIL")
    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
