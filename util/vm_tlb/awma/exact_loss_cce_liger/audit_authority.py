#!/usr/bin/env python3
"""CPU-only authority audit for the Round16 exact-loss side lane."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


CCE_SHA = "3de376c106a1916bc5e1b619f9c77c87a461ee1c"
LIGER_SHA = "6ad077c36379eb9c7950f5572cc713f4d38e21a7"
MODEL_REVISION = "7ae557604adf67be50417f59c2c2f167def9a775"
MODEL_SHA = "fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe"
R101_COMMIT = "cfbe6503585fa1b10d979db5d26fb9be3a80e563"


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()


def sha_i64(values: list[int]) -> str:
    payload = b"".join(int(value).to_bytes(8, "little", signed=True) for value in values)
    return hashlib.sha256(payload).hexdigest()


def first_api_sha(path: Path) -> str:
    value = json.loads(path.read_text())
    sha = value.get("sha")
    if not isinstance(sha, str) or len(sha) != 40:
        raise ValueError(f"missing API commit sha in {path}")
    return sha


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def audit(root: Path, model_root: Path, r101_root: Path) -> dict[str, object]:
    receipts = root / "receipts"
    receipts.mkdir(parents=True, exist_ok=True)
    accepted = json.loads((r101_root / "R101_INPUT_RECEIPT.json").read_text())
    tokens_path = r101_root / "raw" / "TRAIN_DISCOVERY_256.json"
    tokens = json.loads(tokens_path.read_text())
    if len(tokens) != 256 or not all(isinstance(value, int) for value in tokens):
        raise ValueError("accepted R101 discovery window is not exactly 256 integer tokens")

    accepted_part = accepted["parts"]["TRAIN_DISCOVERY_256"]
    checks = {
        "model_safetensors": (model_root / "model.safetensors", MODEL_SHA),
        "config": (model_root / "config.json", "18e18afcaccafade98daf13a54092927904649e1dd4eba8299ab717d5d94ff45"),
        "tokenizer_json": (
            model_root / "tokenizer.json",
            "c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539",
        ),
        "tokenizer_config": (
            model_root / "tokenizer_config.json",
            "5b5d4f65d0acd3b2d56a35b56d374a36cbc1c8fa5cf3b3febbbfabf22f359583",
        ),
        "r101_token_file": (tokens_path, accepted_part["file_sha256"]),
        "r101_input_receipt": (
            r101_root / "R101_INPUT_RECEIPT.json",
            "0c83ef8eec90931beeea66f8802e6d4471d7b483fa94434154811c2234440fc7",
        ),
    }
    observed = {}
    for name, (path, expected) in checks.items():
        actual = sha_file(path)
        if actual != expected:
            raise ValueError(f"{name} sha mismatch: {actual} != {expected}")
        observed[name] = {"path": str(path), "sha256": actual, "size_bytes": path.stat().st_size}

    if hashlib.sha256(canonical_json(tokens)).hexdigest() != accepted_part["token_ids_json_sha256"]:
        raise ValueError("accepted token canonical hash mismatch")
    if sha_i64(tokens) != accepted_part["raw_token_tensor_sha256"]:
        raise ValueError("accepted token int64 storage hash mismatch")
    if accepted["model_revision"] != MODEL_REVISION or accepted["model_weight_sha256"] != MODEL_SHA:
        raise ValueError("R101 model identity mismatch")

    cce_main = first_api_sha(receipts / "CCE_MAIN_API.json")
    liger_main = first_api_sha(receipts / "LIGER_MAIN_API.json")
    if cce_main != CCE_SHA or liger_main != LIGER_SHA:
        raise ValueError(f"upstream main moved: CCE={cce_main} Liger={liger_main}")

    source_identity = {
        "stage": "AWMA_EXACT_LOSS_CCE_LIGER_109_V1",
        "frozen_before_gpu": True,
        "cce": {
            "repository": "apple-aiml-research/ml-cross-entropy",
            "commit": CCE_SHA,
            "main_api_sha": cce_main,
            "archive_sha256": sha_file(root / "source" / "cce.tar.gz"),
            "source_manifest_sha256": sha_file(receipts / "CCE_SOURCE_SHA256.txt"),
            "arm": "linear_cross_entropy(..., impl='cce_exact', filter_eps=None, filter_e_grad=False, filter_c_grad=False)",
        },
        "liger": {
            "repository": "linkedin/Liger-Kernel",
            "commit": LIGER_SHA,
            "main_api_sha": liger_main,
            "archive_sha256": sha_file(root / "source" / "liger.tar.gz"),
            "source_manifest_sha256": sha_file(receipts / "LIGER_SOURCE_SHA256.txt"),
            "arm": "LigerFusedLinearCrossEntropyLoss, standard auto-dispatch; SM89 available implementation must be nvidia-triton only",
            "sm90_backends_forbidden": True,
        },
    }
    write_json(receipts / "SOURCE_IDENTITY.json", source_identity)

    input_receipt = {
        "stage": "AWMA_EXACT_LOSS_CCE_LIGER_109_V1",
        "authority": "ACCEPTED_R101_TRAIN_DISCOVERY_256",
        "r101_commit": R101_COMMIT,
        "r101_input_receipt_sha256": checks["r101_input_receipt"][1],
        "model": "Qwen/Qwen2.5-0.5B-Instruct",
        "model_revision": MODEL_REVISION,
        "model_weight_sha256": MODEL_SHA,
        "model_update_performed": False,
        "token_count": len(tokens),
        "token_ids_sha256": hashlib.sha256(canonical_json(tokens)).hexdigest(),
        "input_ids_contract": "tokens[:-1]",
        "input_ids_count": len(tokens) - 1,
        "input_ids_int64_sha256": sha_i64(tokens[:-1]),
        "labels_contract": "tokens[1:]",
        "labels_count": len(tokens) - 1,
        "labels_int64_sha256": sha_i64(tokens[1:]),
        "ignore_positions": 0,
        "final_hidden_contract": "real Qwen model.model forward last_hidden_state; runtime hash added by GPU campaign",
        "assets": observed,
        "qualified": True,
    }
    write_json(receipts / "INPUT_RECEIPT.json", input_receipt)

    shape = {
        "B": 1,
        "T": 255,
        "H": 896,
        "V": 151936,
        "storage_dtype": "torch.bfloat16",
        "element_size": 2,
        "dense_logits_bytes": 255 * 151936 * 2,
        "lm_head_bytes": 151936 * 896 * 2,
        "prefix_rule_used": False,
        "shape_sweep": False,
    }
    (receipts / "SHAPE_CONTRACT.tsv").write_text(
        "B\tT\tH\tV\tstorage_dtype\telement_size\tdense_logits_bytes\tlm_head_bytes\tprefix_rule_used\n"
        f"{shape['B']}\t{shape['T']}\t{shape['H']}\t{shape['V']}\t{shape['storage_dtype']}\t"
        f"{shape['element_size']}\t{shape['dense_logits_bytes']}\t{shape['lm_head_bytes']}\tfalse\n"
    )
    preregistration = {
        "stage": "AWMA_EXACT_LOSS_CCE_LIGER_109_V1",
        "frozen_before_arm_results": True,
        "atol": 0.01,
        "rtol": 0.01,
        "reason": "contract ceiling and CCE BF16 upstream test authority; Liger's looser BF16 rtol is not adopted",
        "metrics": ["max_abs", "max_rel", "mean_abs", "cosine_similarity", "allclose"],
        "full_gradient_contract": ["loss", "grad_hidden", "grad_weight"],
        "reduction": "mean",
        "label_smoothing": 0.0,
        "softcap": None,
        "z_loss": 0.0,
    }
    write_json(receipts / "NUMERICAL_PREREGISTRATION.json", preregistration)
    return {"source_identity": source_identity, "input_receipt": input_receipt, "shape": shape}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--model-root", type=Path, required=True)
    parser.add_argument("--r101-root", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.root, args.model_root, args.r101_root)
    print(json.dumps({"qualified": True, "shape": result["shape"]}, sort_keys=True))


if __name__ == "__main__":
    main()
