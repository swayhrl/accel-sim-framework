#!/usr/bin/env python3
"""CPU-only authority, asset SHA, tokenization, and tolerance preflight."""

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import subprocess
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import jinja2
import tokenizers
import transformers
from transformers import AutoTokenizer


RUNTIME_COMMIT = "9bd48bcc7762af4d341b51481df957b28ecb5317"
RUNTIME_TREE = "7ee04a1c572a3d9c2602a61f613d60e167bfed81"
ASSET_COMMIT = "c3f625e46adb8d5c4082ded8b61858c710e1f4e9"
ASSET_TREE = "d032d6379c5f31a6f7efb23ec966d3e0c11b849c"
TARGETS = ("QWEN_BF16", "QWEN_AWQ", "OLMOE")


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def write_tsv(path, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=tuple(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def load_rows(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def verify_qwen(key, receipt, root):
    rows = []
    for item in receipt["files"]:
        path = root / item["path"]
        actual_sha = sha_file(path) if path.is_file() else "MISSING"
        actual_size = path.stat().st_size if path.is_file() else -1
        rows.append({"model_key": key, "path": item["path"], "expected_bytes": item["size_bytes"],
                     "actual_bytes": actual_size, "expected_sha256": item["sha256"],
                     "actual_sha256": actual_sha, "status": "PASS" if actual_size == item["size_bytes"] and actual_sha == item["sha256"] else "FAIL"})
    download = root / "DOWNLOAD_RECEIPT.json"
    rows.append({"model_key": key, "path": "DOWNLOAD_RECEIPT.json", "expected_bytes": download.stat().st_size,
                 "actual_bytes": download.stat().st_size, "expected_sha256": receipt["download_receipt_sha256"],
                 "actual_sha256": sha_file(download), "status": "PASS" if sha_file(download) == receipt["download_receipt_sha256"] else "FAIL"})
    return rows


def verify_olmoe(reverify, root):
    receipt_path = root / "MODEL_ASSET_RECEIPT.json"
    if sha_file(receipt_path) != reverify["asset"]["receipt_sha256"]:
        raise RuntimeError("OLMoE asset receipt SHA mismatch")
    receipt = json.loads(receipt_path.read_text())
    rows = []
    for item in receipt["files"]:
        path = root / item["path"]
        actual_sha = sha_file(path) if path.is_file() else "MISSING"
        actual_size = path.stat().st_size if path.is_file() else -1
        rows.append({"model_key": "OLMOE", "path": item["path"], "expected_bytes": item["size"],
                     "actual_bytes": actual_size, "expected_sha256": item["sha256"],
                     "actual_sha256": actual_sha, "status": "PASS" if actual_size == item["size"] and actual_sha == item["sha256"] else "FAIL"})
    rows.append({"model_key": "OLMOE", "path": "MODEL_ASSET_RECEIPT.json", "expected_bytes": receipt_path.stat().st_size,
                 "actual_bytes": receipt_path.stat().st_size, "expected_sha256": reverify["asset"]["receipt_sha256"],
                 "actual_sha256": sha_file(receipt_path), "status": "PASS"})
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--data-root", type=Path, required=True)
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    asset_pack = args.repo / "docs/vm_tlb/review_packs/C16_MEASUREMENT_CAMPAIGN_STAGEA_ASSET_INPUT_CLOSURE_174NEW_V1"
    preflight_pack = args.repo / "docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_EXECUTION_PREFLIGHT_174NEW_V1"
    runtime_pack = args.repo / "docs/vm_tlb/review_packs/C16_MEASUREMENT_CAMPAIGN_109_RUNTIME_ENVIRONMENT_AUDIT_V1"
    runtime_draft = json.loads((runtime_pack / "C16_STAGEA_RUNTIME_QUALIFICATION_CANARY_109_DRAFT.json").read_text())
    asset_final = json.loads((asset_pack / "FINAL_DECISION.json").read_text())
    checks = {
        "runtime_head": git(args.repo, "rev-parse", "HEAD") == RUNTIME_COMMIT,
        "runtime_tree": git(args.repo, "rev-parse", "HEAD^{tree}") == RUNTIME_TREE,
        "asset_commit": git(args.repo, "rev-parse", "refs/remotes/origin/hrl/c16-measurement-campaign-stagea-asset-input-closure-174new-v1") == ASSET_COMMIT,
        "asset_tree": git(args.repo, "rev-parse", "refs/remotes/origin/hrl/c16-measurement-campaign-stagea-asset-input-closure-174new-v1^{tree}") == ASSET_TREE,
        "asset_status": asset_final["status"] == "STAGEA_ASSET_INPUT_READY",
        "runtime_draft_status": runtime_draft["status"] == "DRAFT_FOR_PROJECT_APPROVAL",
        "runtime_environment": Path(runtime_draft["runtime_environment"]).resolve() == Path("/data/c16/envs/c16-vllm-v0.30.0-sm89-v1"),
        "target_scope": [row["id"] for row in runtime_draft["targets"]] == list(TARGETS),
        "holdout_outputs_absent": asset_final["holdout_model_outputs_generated"] is False,
    }
    authority = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
                 "runtime_commit": RUNTIME_COMMIT, "runtime_tree": RUNTIME_TREE,
                 "asset_commit": ASSET_COMMIT, "asset_tree": ASSET_TREE,
                 "allowed_targets": list(TARGETS), "forbidden_points": ["MP04", "MP07", "MP08"],
                 "holdout_governance_sha256": sha_file(asset_pack / "HOLDOUT_NONEXECUTION_GOVERNANCE_V2.md")}
    (args.output_dir / "CANARY_AUTHORITY.json").write_text(json.dumps(authority, indent=2, sort_keys=True) + "\n")
    if authority["status"] != "PASS":
        raise RuntimeError("authority closure failed")

    roots = {
        "QWEN_BF16": args.data_root / "assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1",
        "QWEN_AWQ": args.data_root / "assets/qwen2.5-3b-instruct-awq/3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd",
        "OLMOE": Path("/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e"),
    }
    bf = json.loads((asset_pack / "QWEN_BF16_ASSET_RECEIPT.json").read_text())
    awq = json.loads((asset_pack / "QWEN_AWQ_ASSET_RECEIPT.json").read_text())
    olmoe = json.loads((asset_pack / "OLMOE_ASSET_REVERIFY.json").read_text())
    asset_rows = verify_qwen("QWEN_BF16", bf, roots["QWEN_BF16"])
    asset_rows += verify_qwen("QWEN_AWQ", awq, roots["QWEN_AWQ"])
    asset_rows += verify_olmoe(olmoe, roots["OLMOE"])
    if any(row["status"] != "PASS" for row in asset_rows):
        raise RuntimeError("asset SHA mismatch")
    asset_receipt = {
        "status": "PASS", "files_verified": len(asset_rows), "rows": asset_rows,
        "models": {
            "QWEN_BF16": {"path": str(roots["QWEN_BF16"]), "revision": bf["revision"], "weight_bytes": bf["weight_total_bytes"]},
            "QWEN_AWQ": {"path": str(roots["QWEN_AWQ"]), "revision": awq["revision"], "weight_bytes": awq["weight_total_bytes"], "quantization": awq["quantization_config"], "no_requantization": True},
            "OLMOE": {"path": str(roots["OLMOE"]), "revision": olmoe["revision"], "weight_bytes": olmoe["expected_weight_total_bytes"]},
        },
    }
    (args.output_dir / "ASSET_VISIBILITY_AND_SHA.json").write_text(json.dumps(asset_receipt, indent=2, sort_keys=True) + "\n")

    spec = importlib.util.spec_from_file_location("authority_tokenize", args.repo / "util/vm_tlb/c16/tokenize_stagea.py")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    authority_rows = [row for row in load_rows(asset_pack / "TOKENIZATION_RECEIPTS.tsv")
                      if row["model_key"] in TARGETS and row["source_text_id"] == "TRAIN_A_DISCOVERY_00"]
    if len(authority_rows) != 3:
        raise RuntimeError("token authority row count")
    source = preflight_pack / "input_sources/TRAIN_A_DISCOVERY_00.txt"
    text_bytes = source.read_bytes(); text = text_bytes.decode("utf-8")
    inputs_dir = args.data_root / "inputs"; inputs_dir.mkdir(parents=True, exist_ok=True)
    token_rows = []
    for expected in authority_rows:
        key = expected["model_key"]
        tok = AutoTokenizer.from_pretrained(str(roots[key]), local_files_only=True, use_fast=True, trust_remote_code=False)
        ids, prefix_chars, full_count, status = module.tokenize_prefix(tok, text, 512)
        canonical = module.canonical_ids(ids)
        input_path = inputs_dir / f"{key}_TRAIN_A_DISCOVERY_00.json"
        input_path.write_bytes(canonical + b"\n")
        observed = {
            "model_key": key, "source_text_id": "TRAIN_A_DISCOVERY_00",
            "source_utf8_sha256": sha_bytes(text_bytes), "source_byte_count": len(text_bytes),
            "tokenizer_class": type(tok).__name__,
            "tokenizer_json_sha256": sha_file(roots[key] / "tokenizer.json"),
            "tokenizer_config_sha256": sha_file(roots[key] / "tokenizer_config.json"),
            "chat_template_sha256": sha_bytes(tok.chat_template.encode("utf-8")),
            "transformers_version": transformers.__version__, "tokenizers_version": tokenizers.__version__,
            "jinja2_version": jinja2.__version__, "full_source_templated_token_count": full_count,
            "prefix_utf8_byte_count": len(text[:prefix_chars].encode("utf-8")), "prompt_token_count": len(ids),
            "truncate_rule_result": status, "token_ids_sha256": sha_bytes(canonical),
            "token_id_file_sha256": sha_file(input_path), "input_path": str(input_path),
        }
        comparisons = {
            field: str(observed[field]) == str(expected[field]) for field in (
                "source_utf8_sha256", "source_byte_count", "tokenizer_class", "tokenizer_json_sha256",
                "tokenizer_config_sha256", "chat_template_sha256", "transformers_version", "tokenizers_version",
                "jinja2_version", "full_source_templated_token_count", "prefix_utf8_byte_count", "prompt_token_count",
                "truncate_rule_result", "token_ids_sha256", "token_id_file_sha256")
        }
        authority_token_file = asset_pack / expected["token_ids_relative_path"]
        comparisons["authority_token_file_bytes"] = authority_token_file.read_bytes() == input_path.read_bytes()
        observed["status"] = "PASS" if all(comparisons.values()) else "TOKENIZATION_MISMATCH_STOP"
        observed["checks"] = json.dumps(comparisons, sort_keys=True, separators=(",", ":"))
        token_rows.append(observed)
    write_tsv(args.output_dir / "TOKENIZATION_RECHECK.tsv", token_rows)
    if any(row["status"] != "PASS" for row in token_rows):
        raise RuntimeError("TOKENIZATION_MISMATCH_STOP")

    tolerance = {
        "status": "FROZEN_BEFORE_GPU_RESULTS", "created_before_gpu_lock": True,
        "correctness": {
            "generated_token_ids": "exact equality",
            "shapes_and_semantic_order": "exact equality",
            "routing_expert_ids": "exact equality for OLMOE",
            "logprob_numeric": {"QWEN_BF16": {"atol": 0.05, "rtol": 0.01},
                                "QWEN_AWQ": {"atol": 0.05, "rtol": 0.01},
                                "OLMOE": {"atol": 0.05, "rtol": 0.01}},
        },
        "instrumentation_neutrality": {"samples_per_arm": 3,
            "wall_gate": "abs(median_on-median_off) <= max(5.0 ms, 0.10*median_off)",
            "tokens_shapes_routing_backend_kernel_inventory": "exact equality"},
        "graph_off_on": {"model_input_batch_context_decode": "exactly identical per target",
                         "tokens_shapes_semantic_order_backend_identity": "exact equality",
                         "logprob_tolerance": "per-target values above"},
    }
    (args.output_dir / "CORRECTNESS_AND_NEUTRALITY_THRESHOLDS.json").write_text(json.dumps(tolerance, indent=2, sort_keys=True) + "\n")
    plan = {"status": "READY_FOR_LOCKED_CANARY", "target_order": list(TARGETS),
            "condition_order_each": ["GRAPH_OFF_INSTRUMENT_OFF", "GRAPH_OFF_INSTRUMENT_ON", "GRAPH_ON_INSTRUMENT_OFF"],
            "model_processes": 6, "serial": True, "destroy_process_between_conditions": True,
            "gpu_active_budget_seconds": 240, "no_holdout": True,
            "qwen": {"batch": 1, "context": 512, "decode_tokens": 4},
            "olmoe": {"batch": 1, "context": 512, "decode_tokens": 32, "max_model_len": 544, "max_num_seqs": 1},
            "forbidden": ["fallback", "requantization", "CPU offload", "context/batch changes", "NCU", "NVBit", "SASS", "Accel-Sim"]}
    (args.output_dir / "GPU_CANARY_PLAN.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "asset_files": len(asset_rows), "tokenization_rows": len(token_rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
