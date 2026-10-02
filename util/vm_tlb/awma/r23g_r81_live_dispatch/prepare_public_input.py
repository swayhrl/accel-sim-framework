#!/usr/bin/env python3
"""CPU-only deterministic public-input extraction for AWMA R23G."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
from collections import Counter
from pathlib import Path

import xgrammar as xgr


TEMPLATE_VERSION = "R23G_PROMPT_V1"
TEMPLATE = (
    "You may call function {name}. {description}\n"
    "User request: {user_message}\n"
    "Return only the JSON arguments object for this function."
)


def canonical(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_json_field(value, field: str):
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, list):
        raise ValueError(f"{field}_not_list")
    return value


def structural_record(row: dict, row_index: int, revision: str):
    messages = parse_json_field(row.get("messages"), "messages")
    functions = parse_json_field(row.get("functions"), "functions")
    if len(functions) != 1:
        raise ValueError("function_count_not_one")
    function = functions[0]
    if not isinstance(function, dict):
        raise ValueError("function_not_object")
    name = function.get("name")
    description = function.get("description")
    schema = function.get("parameters")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("function_name_missing")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("function_description_missing")
    if not isinstance(schema, dict):
        raise ValueError("parameters_not_object")
    if schema.get("type") != "object" or not isinstance(schema.get("properties"), dict):
        raise ValueError("parameters_not_object_schema")
    call_positions = [
        i for i, message in enumerate(messages)
        if isinstance(message, dict) and message.get("role") == "function_call"
    ]
    if not call_positions:
        raise ValueError("function_call_missing")
    first_call = call_positions[0]
    users = [
        (i, message.get("content"))
        for i, message in enumerate(messages[:first_call])
        if isinstance(message, dict) and message.get("role") == "user"
    ]
    if not users:
        raise ValueError("user_before_call_missing")
    user_message = users[0][1]
    if not isinstance(user_message, str) or not user_message.strip():
        raise ValueError("first_user_message_missing")
    function = json.loads(canonical(function).decode("utf-8"))
    identity = {
        "dataset_revision": revision,
        "original_row_index": row_index,
        "function_definition": function,
        "first_user_message": user_message,
        "prompt_template_version": TEMPLATE_VERSION,
    }
    record_hash = sha_bytes(canonical(identity))
    prompt = TEMPLATE.format(
        name=name.strip(),
        description=description.strip(),
        user_message=user_message.strip(),
    )
    return {
        "record_sha256": record_hash,
        "original_row_index": row_index,
        "function_name": name.strip(),
        "function_description": description.strip(),
        "first_user_message": user_message,
        "function_definition": function,
        "schema": schema,
        "schema_sha256": sha_bytes(canonical(schema)),
        "prompt": prompt,
        "prompt_sha256": sha_bytes(prompt.encode("utf-8")),
        "prompt_template_version": TEMPLATE_VERSION,
    }


def write_tsv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=Path, required=True)
    ap.add_argument("--dataset-revision", required=True)
    ap.add_argument("--dataset-api", type=Path, required=True)
    ap.add_argument("--tokenizer-info", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    compiled_dir = args.output_dir / "compiled_grammar"
    compiled_dir.mkdir(exist_ok=True)

    rows = json.loads(args.dataset.read_text())
    if not isinstance(rows, list):
        raise ValueError("dataset root is not a list")
    tokenizer_info = xgr.TokenizerInfo.deserialize_json(args.tokenizer_info.read_text())
    compiler = xgr.GrammarCompiler(tokenizer_info, max_threads=4, cache_enabled=True)

    eligible = []
    rejected = Counter()
    for row_index, row in enumerate(rows):
        try:
            if not isinstance(row, dict):
                raise ValueError("row_not_object")
            record = structural_record(row, row_index, args.dataset_revision)
            compiler.compile_json_schema(
                record["schema"], strict_mode=True, any_whitespace=True
            )
            eligible.append(record)
        except Exception as exc:
            reason = str(exc).split("\n", 1)[0] or type(exc).__name__
            rejected[reason] += 1

    eligible.sort(key=lambda row: row["record_sha256"])
    pool = eligible[:24]
    if len(pool) < 24:
        raise RuntimeError(f"only {len(pool)} structurally eligible rows")

    compile_receipts = []
    for row in pool:
        compiled = compiler.compile_json_schema(
            row["schema"], strict_mode=True, any_whitespace=True
        )
        path = compiled_dir / f"{row['schema_sha256']}.json"
        if not path.exists():
            path.write_text(compiled.serialize_json())
        compile_receipts.append(
            {
                "record_sha256": row["record_sha256"],
                "schema_sha256": row["schema_sha256"],
                "compiled_path": str(path),
                "compiled_bytes": path.stat().st_size,
                "compiled_sha256": sha_file(path),
            }
        )

    pool_payload = {
        "stage": "AWMA_R23G_R81_LIVE_DISPATCH_109_V1",
        "authority_class": "PUBLIC_HUGGING_FACE_PARSED_DERIVATIVE_VALIDATION_POOL",
        "dataset_id": "korotkov/glaive-function-calling-v2-parsed",
        "dataset_revision": args.dataset_revision,
        "split": "test",
        "prompt_template_version": TEMPLATE_VERSION,
        "records": pool,
    }
    pool_path = args.output_dir / "QUALIFICATION_POOL.json"
    pool_path.write_text(json.dumps(pool_payload, indent=2, sort_keys=True) + "\n")
    pool_rows = [
        {
            "pool_rank": rank,
            "record_sha256": row["record_sha256"],
            "original_row_index": row["original_row_index"],
            "schema_sha256": row["schema_sha256"],
            "prompt_sha256": row["prompt_sha256"],
            "function_name": row["function_name"],
        }
        for rank, row in enumerate(pool)
    ]
    write_tsv(args.output_dir / "QUALIFICATION_POOL.tsv", pool_rows)

    authority = {
        "stage": "AWMA_R23G_R81_LIVE_DISPATCH_109_V1",
        "dataset_id": "korotkov/glaive-function-calling-v2-parsed",
        "dataset_revision": args.dataset_revision,
        "split": "test",
        "dataset_file": str(args.dataset),
        "dataset_file_bytes": args.dataset.stat().st_size,
        "dataset_file_sha256": sha_file(args.dataset),
        "dataset_api_receipt_sha256": sha_file(args.dataset_api),
        "local_cache_files": [],
        "local_cache_status": "DIRECT_PINNED_JSON_DOWNLOAD; no datasets-library cache",
        "source_row_count": len(rows),
        "structurally_eligible_and_compilable_count": len(eligible),
        "rejection_counts": dict(sorted(rejected.items())),
        "qualification_pool_count": len(pool),
        "qualification_pool_sha256": sha_file(pool_path),
        "qualification_pool_record_hashes": [row["record_sha256"] for row in pool],
        "compiled_grammar_receipts": compile_receipts,
        "xgrammar_version": importlib.metadata.version("xgrammar"),
        "tokenizer_info_sha256": sha_file(args.tokenizer_info),
        "selection_used_union_fraction": False,
        "selection_used_output_length": False,
        "selection_used_timing": False,
    }
    (args.output_dir / "PUBLIC_INPUT_PREQUAL_AUTHORITY.json").write_text(
        json.dumps(authority, indent=2, sort_keys=True) + "\n"
    )
    print(
        json.dumps(
            {
                "source_rows": len(rows),
                "eligible": len(eligible),
                "pool": len(pool),
                "dataset_sha256": authority["dataset_file_sha256"],
                "pool_sha256": authority["qualification_pool_sha256"],
                "rejections": authority["rejection_counts"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
