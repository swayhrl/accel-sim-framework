#!/usr/bin/env python3
"""Create non-scientific Recovery-V3 R0 authority and storage receipts."""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json


SCHEMA = "C16_G_RETRY570_FULL_AUTHORITY_RECOVERY_V3_R0"
HANDOFF_COMMIT = "919e0cfca2017dfa5c85cbfe15aac5b8244e08f1"
BASE_CHECKPOINT = "2c52c7aa79e5dc131ffefa29bedf5b0018fcdac3"
LLAMA_CHECKPOINT = "2e955e007bcabcd3ec24a5f9d24768d27caaee27"
MIN_BULK_FREE_BYTES = 80 * 1024**3
SCENARIOS = {
    "S0": (1, 128, 4, "CANARY_ONLY"), "S1": (1, 256, 16, "REQUIRED"),
    "S2": (1, 2048, 32, "REQUIRED"), "S3": (1, 8192, 16, "REQUIRED_DENSE_IF_FITS"),
    "S4": (4, 2048, 16, "REQUIRED_DENSE_IF_FITS"),
}
DEPLOYMENTS = (
    ("llama_3p2_1b", "C16_AUTHORITATIVE", 1, "meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08", ("S0", "S1", "S2", "S3", "S4")),
    ("qwen2p5_0p5b_instruct", "C16_AUTHORITATIVE", 1, "Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775", ("S0", "S1", "S2", "S3", "S4")),
    ("qwen2p5_7b_instruct_raw", "C16_AUTHORITATIVE", 1, "RECOVER_EXACT_REVISION_FROM_C16_AUTHORITY", ("S0", "S1", "S2", "S3", "S4")),
    ("qwen2p5_7b_instruct_awq", "C16_AUTHORITATIVE", 1, "Qwen/Qwen2.5-7B-Instruct-AWQ@b25037543e9394b818fdfca67ab2a00ecc7dd641", ("S0", "S1", "S2", "S3", "S4")),
    ("qwen3_8b", "C16_AUTHORITATIVE", 2, "RECOVER_EXACT_REVISION_FROM_C16_AUTHORITY", ("S0", "S1", "S2", "S3", "S4")),
    ("qwen3_30b_a3b", "C16_AUTHORITATIVE", 2, "RECOVER_EXACT_REVISION_FROM_C16_AUTHORITY", ("S1", "S2")),
    ("deepseek_v2_lite", "C16_AUTHORITATIVE", 2, "VERIFY_CANDIDATE_deepseek-ai/DeepSeek-V2-Lite@604d5664dddd88a0433dbae533b7fe9472482de0", ("S1", "S2")),
    ("glm_extension", "USER_EXTENSION", 3, "RECOVER_FROM_PRIOR_PROJECT_TRACE_AND_METADATA", ("S0", "S1", "S2")),
)


def free_bytes(path: Path) -> int:
    value = os.statvfs(path)
    return value.f_bavail * value.f_frsize


def storage_receipt(bulk: Path) -> dict[str, Any]:
    resolved = bulk.resolve()
    if resolved != Path("/root/share/c16_recovery_v3"):
        raise ContractError("Recovery-V3 bulk root is fixed to /root/share/c16_recovery_v3")
    for name in ("raw", "models", "hf-cache", "staging", "receipts"):
        (resolved / name).mkdir(parents=True, exist_ok=True)
    sentinel = resolved / f".storage_sentinel_{os.getpid()}"
    sentinel.write_text("C16 Recovery-V3 bulk-storage writable sentinel\n", encoding="utf-8")
    if not sentinel.is_file() or sentinel.stat().st_size == 0:
        raise ContractError("bulk root sentinel write failed")
    sentinel.unlink()
    root_stat, bulk_stat = os.stat("/"), os.stat(resolved)
    root_free, bulk_free = free_bytes(Path("/")), free_bytes(resolved)
    if root_stat.st_dev == bulk_stat.st_dev:
        raise ContractError("bulk root resolves to the constrained root filesystem")
    if bulk_free < MIN_BULK_FREE_BYTES:
        raise ContractError("bulk root has less than the required 80-GiB asset guard")
    filesystem = subprocess.check_output(["stat", "-f", "-c", "%i %T", str(resolved)], text=True).strip()
    return {"schema_version": SCHEMA, "status": "LOCAL_BULK_STORAGE_PREFLIGHT_PASS", "scientific_eligible": False,
            "local_bulk_root": str(resolved), "local_raw_root": str(resolved / "raw"), "local_model_root": str(resolved / "models"),
            "local_hf_cache_root": str(resolved / "hf-cache"), "local_transfer_staging": str(resolved / "staging"), "local_bulk_receipts": str(resolved / "receipts"),
            "local_bulk_writable": True, "local_bulk_filesystem_separate_from_constrained_root": True,
            "local_bulk_filesystem_id": filesystem, "local_bulk_st_dev": bulk_stat.st_dev, "root_st_dev": root_stat.st_dev,
            "local_bulk_free_bytes_initial": bulk_free, "root_fs_free_bytes_initial": root_free,
            "large_payload_policy": {"workspace": "COMPACT_METADATA_ONLY", "root_cache": "FORBIDDEN_FOR_RECOVERY_V3_LARGE_PAYLOADS", "bulk_root": "REQUIRED"}}


def authority_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for deployment, authority, wave, identity, scenarios in DEPLOYMENTS:
        for scenario in scenarios:
            batch, tokens, decode, role = SCENARIOS[scenario]
            state = "INHERITED_COMPLETE" if deployment == "llama_3p2_1b" and scenario == "S0" else "PENDING_R1_EXACT_IDENTITY_AND_ASSET"
            rows.append({"deployment": deployment, "authority_role": authority, "wave": str(wave), "exact_identity": identity,
                         "scenario": scenario, "batch": str(batch), "requested_input_tokens": str(tokens), "decode_steps": str(decode),
                         "scenario_role": role, "r0_status": state, "accepted_source_commit": LLAMA_CHECKPOINT if state == "INHERITED_COMPLETE" else "NA"})
    return rows


def write_matrix(path: Path) -> None:
    if path.exists():
        raise ContractError("R0 matrix refuses to overwrite retained evidence")
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = authority_rows()
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bulk-root", type=Path, required=True)
    parser.add_argument("--storage-receipt", type=Path, required=True)
    parser.add_argument("--authority-matrix", type=Path, required=True)
    args = parser.parse_args()
    if args.storage_receipt.exists():
        raise ContractError("storage receipt refuses to overwrite retained evidence")
    receipt = storage_receipt(args.bulk_root)
    receipt.update({"handoff_commit": HANDOFF_COMMIT, "base_checkpoint": BASE_CHECKPOINT, "accepted_llama_s0_checkpoint": LLAMA_CHECKPOINT, "authority_row_count": len(authority_rows())})
    atomic_json(args.storage_receipt, receipt)
    write_matrix(args.authority_matrix)
    print("PASS R0_AUTHORITY_AND_LOCAL_BULK_STORAGE")


if __name__ == "__main__":
    try: main()
    except ContractError as exc: raise SystemExit(f"FAIL Recovery-V3 R0: {exc}")
