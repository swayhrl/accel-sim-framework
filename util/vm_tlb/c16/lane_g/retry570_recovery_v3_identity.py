#!/usr/bin/env python3
"""Materialize Recovery-V3 exact identity authority before asset transfer."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file


SCHEMA = "C16_G_RETRY570_FULL_AUTHORITY_RECOVERY_V3_IDENTITY_V1"
P2_COMMIT = "168c97148ef2bbfaf9bbe199414b0e7a5fc3ed1d"
P2_MANIFEST = "c937590dd4ea2b4f6407db7d8b077ed263af3cbc14562ef34142aa834b133f26"
P3_MANIFEST = "704dc320a131e31a6d9fd11a8ac623318777c832b0b699241c5bf3f1c8beda1c"
C15_SOURCE = "3f5cc37398183bf9d0e8043d78f83bd8c2e1757e"


IDENTITIES = (
    ("llama_3p2_1b", "meta-llama/Llama-3.2-1B", "4e20de362430cd3b72f300e6b0f18e50e7166e08", "NONE", "float16", "INHERITED_ACCEPTED_S0", "accepted Recovery-V2 Llama S0 checkpoint 2e955e..."),
    ("qwen2p5_0p5b_instruct", "Qwen/Qwen2.5-0.5B-Instruct", "7ae557604adf67be50417f59c2c2f167def9a775", "NONE", "float16", "IDENTITY_RECOVERED_READY_FOR_EXACT_FETCH", "C16 P1 immutable package manifest d8ac..."),
    ("qwen2p5_7b_instruct_raw", "Qwen/Qwen2.5-7B-Instruct", "a09a35458c702b33eeacc393d103063234e8bc28", "NONE", "bfloat16", "IDENTITY_RECOVERED_READY_FOR_EXACT_FETCH", f"C16 P2 {P2_COMMIT}, manifest {P2_MANIFEST}"),
    ("qwen2p5_7b_instruct_awq", "Qwen/Qwen2.5-7B-Instruct-AWQ", "b25037543e9394b818fdfca67ab2a00ecc7dd641", "AWQ", "float16", "IDENTITY_RECOVERED_READY_FOR_EXACT_FETCH", f"C16 P3 {P2_COMMIT}, manifest {P3_MANIFEST}"),
    ("qwen3_8b", "Qwen/Qwen3-8B", "b968826d9c46dd6066d109eabc6255188de91218", "NONE", "bfloat16", "IDENTITY_RECOVERED_READY_FOR_EXACT_FETCH", f"C15 static authority {C15_SOURCE}, config SHA256 f7c4eadfbbf522470667b797a3c89be2524832d2d599797248dc304fff447c30"),
    ("qwen3_30b_a3b", "Qwen/Qwen3-30B-A3B", "ad44e777bcd18fa416d9da3bd8f70d33ebb85d39", "NONE", "bfloat16", "IDENTITY_RECOVERED_READY_FOR_EXACT_FETCH", f"C15 static authority {C15_SOURCE}, config SHA256 2850ddb3bf7aecad20b611e2d44f3077fc8193f4827c93beddd4c02ad63c2297"),
    ("deepseek_v2_lite", "deepseek-ai/DeepSeek-V2-Lite", "604d5664dddd88a0433dbae533b7fe9472482de0", "NONE", "bfloat16", "IDENTITY_CANDIDATE_REQUIRES_RUNTIME_INPUT_CLOSURE", f"C15 static authority {C15_SOURCE}; V3 requires tokenizer/input/runtime closure before runnable label"),
    ("glm_extension", "UNRESOLVED", "UNRESOLVED", "UNRESOLVED", "UNRESOLVED", "IDENTITY_UNRESOLVED_AFTER_AUTHORITY_SEARCH", "No historical project artifact supplies an exact GLM model/revision/custom-code contract; generic GLM must not be guessed."),
)


def rows() -> list[dict[str, str]]:
    return [{"deployment": key, "model_id": model, "revision": revision, "quantization": quant, "dtype_expectation": dtype, "r1_identity_status": status, "authority_evidence": evidence} for key, model, revision, quant, dtype, status, evidence in IDENTITIES]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-tsv", type=Path, required=True)
    parser.add_argument("--storage-receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.output_json.exists() or args.output_tsv.exists():
        raise ContractError("identity authority refuses to overwrite retained evidence")
    storage = json.loads(args.storage_receipt.read_text(encoding="utf-8"))
    if storage.get("status") != "LOCAL_BULK_STORAGE_PREFLIGHT_PASS" or storage.get("local_bulk_root") != "/root/share/c16_recovery_v3":
        raise ContractError("R1 identity requires the passed Recovery-V3 local bulk-storage gate")
    value: dict[str, Any] = {"schema_version": SCHEMA, "status": "R1_IDENTITY_AUTHORITY_RECOVERED", "scientific_eligible": False,
                             "storage_receipt": {"path": str(args.storage_receipt), "sha256": sha256_file(args.storage_receipt)},
                             "identities": rows(), "unresolved_extension_count": 1,
                             "policy": "Every exact model/revision is authority-derived; GLM is deliberately unresolved rather than substituted."}
    atomic_json(args.output_json, value)
    args.output_tsv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_tsv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows()[0]), delimiter="\t")
        writer.writeheader(); writer.writerows(rows())
    print("PASS R1_IDENTITY_AUTHORITY_RECOVERED")


if __name__ == "__main__":
    try: main()
    except (ContractError, OSError, json.JSONDecodeError) as exc: raise SystemExit(f"FAIL Recovery-V3 identity: {exc}")
