#!/usr/bin/env python3
"""Publish hash-closed Llama recovery-v2 S0--S6 evidence (never raw traces)."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file

SCHEMA = "C16_G_NVBIT175_LLAMA_RECOVERY_PUBLICATION_V2"
PACK_FILES = (
    "L0_REVALIDATION.json", "L1_RECOVERY_SCOPE.json", "LARGE_INDEX_PREFILL_TARGET.json",
    "DECODE_PATH_CENSUS.json", "DECODE_STATIC_MAP_RECEIPT.json", "DECODE_SMALLINDEX_STATIC_MAP.tsv",
    "DECODE_INDEX_TARGET.json", "S3_S4_REPRODUCIBILITY.json", "S5_FULL_WORKLOAD_SUMMARY.json",
    "S5_STORAGE_ESTIMATE.json", "RAW_ARTIFACT_INDEX.json", "LLAMA_RECOVERY_REPORT.md",
)


def read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read retained receipt: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError("receipt must be a JSON object")
    return value


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def one_trace(receipt: dict[str, Any]) -> dict[str, Any]:
    try:
        traces = receipt["child"]["capture"]["traces"]
    except (KeyError, TypeError) as exc:
        raise ContractError("formal receipt lacks child capture evidence") from exc
    if len(traces) != 1:
        raise ContractError("prefill formal capture must have exactly one target trace")
    row = traces[0]
    if row["record_count"] <= 0 or row["address_record_count"] <= 0:
        raise ContractError("formal trace lacks records/address evidence")
    return row


def trace_list(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        rows = receipt["child"]["capture"]["traces"]
    except (KeyError, TypeError) as exc:
        raise ContractError("decode formal receipt lacks child capture evidence") from exc
    if len(rows) != 3 or any(row["record_count"] <= 0 or row["address_record_count"] <= 0 for row in rows):
        raise ContractError("decode capture must close three address-bearing actual-forward traces")
    return rows


def require_local(remote: dict[str, Any], local: Path) -> dict[str, Any]:
    if not local.is_file() or local.stat().st_size != remote["size_bytes"] or sha256_file(local) != remote["sha256"]:
        raise ContractError("remote/local trace SHA closure differs")
    return {"remote": remote, "local_path": str(local), "local_size_bytes": local.stat().st_size, "local_sha256": sha256_file(local), "sha_equal": True}


def make_manifest(directory: Path) -> dict[str, Any]:
    payloads = [{"path": name, "size_bytes": (directory / name).stat().st_size, "sha256": sha256_file(directory / name)} for name in PACK_FILES]
    return {"schema_version": SCHEMA, "status": "LLAMA_FULL_TARGET_TRACE_COMPLETE", "producer_code_commit": git_head(), "raw_trace_payloads_committed": False, "payloads": payloads}


def validate(directory: Path, data: dict[str, Any]) -> dict[str, Any]:
    seen: set[str] = set()
    for row in data["payloads"]:
        path = row["path"]
        if path in seen or not (directory / path).is_file() or (directory / path).stat().st_size != row["size_bytes"] or sha256_file(directory / path) != row["sha256"]:
            raise ContractError("publication manifest payload closure failed")
        seen.add(path)
    return {"schema_version": SCHEMA, "status": "PUBLISH_MANIFEST_VALIDATION_PASS", "payload_count": len(seen), "all_payloads_exist_size_sha256_match": True, "no_duplicate_path": True, "manifest_sha256": sha256_file(directory / "PUBLISH_MANIFEST.json")}


def copy_source(source: Path, destination: Path) -> None:
    destination.write_bytes(source.read_bytes())


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("output", "scope", "s1", "s2", "large-target", "s3", "s4", "s5-prefill", "s5-decode-large", "storage-estimate", "decode-census", "decode-map-receipt", "decode-map", "decode-target", "s5-decode-small"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--s3-local-trace", type=Path, required=True); p.add_argument("--s4-local-trace", type=Path, required=True); p.add_argument("--s5-prefill-local-trace", type=Path, required=True)
    p.add_argument("--s5-decode-small-local-trace", type=Path, action="append", required=True)
    args = p.parse_args()
    if args.output.exists():
        raise ContractError("refusing to overwrite Llama recovery publication")
    scope, s1, s2, large, s3, s4, s5p, s5large, storage, census, map_receipt, decode_target, s5small = map(read, (args.scope, args.s1, args.s2, args.large_target, args.s3, args.s4, args.s5_prefill, args.s5_decode_large, args.storage_estimate, args.decode_census, args.decode_map_receipt, args.decode_target, args.s5_decode_small))
    if scope.get("status") != "RECOVERY_BUDGET_NAMESPACE_READY" or scope.get("new_deployment_id") != "c16_nvbit175_recovery_llama32_1b_v1" or not scope["historical_ledger"].get("rows_preserved"):
        raise ContractError("recovery namespace evidence is not closed")
    if s1.get("status") != "S1_FULL_MODEL_NO_TRACE_PASS" or s2.get("status") != "S2_FULL_MODEL_STATIC_MAP_PASS":
        raise ContractError("S1/S2 inherited evidence invalid")
    if large["target_instruction"]["nvbit_static_index"] != 101 or large["target_instruction"]["opcode"] != "LDG.E.U16" or 34 not in large["excluded_static_indices"]:
        raise ContractError("prefill LargeIndex target differs from inherited S2 evidence")
    if storage.get("status") != "PASS":
        raise ContractError("S5 storage gate did not pass")
    if census.get("status") != "DECODE_INDEXSELECT_CANDIDATE_OBSERVED" or census.get("actual_decode_indexselect_classes") != ["SmallIndex"]:
        raise ContractError("decode census did not directly establish the SmallIndex dispatch")
    if any(not census["phases"][f"DECODE{i}"]["index_select_kernels"] for i in range(2, 5)):
        raise ContractError("decode census lacks direct evidence for an actual decode forward")
    if map_receipt.get("status") != "DECODE_NVBIT_STATIC_MAP_PASS" or map_receipt["static_map"]["sha256"] != sha256_file(args.decode_map):
        raise ContractError("decode NVBit map receipt/hash is not closed")
    if decode_target.get("status") != "NVBIT_NATIVE_STATIC_INDEX_SELECTED" or decode_target["map_sha256"] != sha256_file(args.decode_map):
        raise ContractError("decode target does not bind the exact native static map")
    if decode_target["target_instruction"]["nvbit_static_index"] != 17 or decode_target["target_instruction"]["opcode"] != "LDG.E" or "indexSelectSmallIndex" not in decode_target["function"]["mangled_name"]:
        raise ContractError("decode target is not the independent SmallIndex LDG.E/[17,18) selection")
    s3t, s4t, s5pt = one_trace(s3), one_trace(s4), one_trace(s5p)
    large_function = large["function"]["mangled_name"]
    if any(item["function"] != large_function for item in (s3t, s4t, s5pt)) or s3t["record_count"] != s4t["record_count"]:
        raise ContractError("S3/S4 prefill identity/structural reproducibility differs")
    large_decode = s5large["child"]["capture"]
    if s5large.get("status") != "FORMAL_CAPTURE_COMPLETE" or large_decode["decode_steps_executed"] != 4 or any(large_decode["phase_trace_summary"][f"DECODE{i}"]["record_count"] != 0 for i in range(1, 5)):
        raise ContractError("LargeIndex structural-zero decode receipt is incomplete")
    small_rows = trace_list(s5small)
    small_capture = s5small["child"]["capture"]
    if s5small.get("status") != "FORMAL_CAPTURE_COMPLETE" or small_capture["output_checksum"] != large_decode["output_checksum"] or small_capture["target_receipt"]["target_role"] != "DECODE_INDEX_TARGET":
        raise ContractError("SmallIndex decode capture identity/role closure differs")
    if any(small_capture["phase_trace_summary"][f"DECODE{i}"]["record_count"] <= 0 for i in range(2, 5)):
        raise ContractError("SmallIndex decode capture lacks one of the actual decode forwards")
    if len(args.s5_decode_small_local_trace) != len(small_rows):
        raise ContractError("decode local trace arguments do not bind every remote trace")
    small_local = [require_local(remote, local) for remote, local in zip(small_rows, args.s5_decode_small_local_trace)]
    index = {"schema_version": SCHEMA, "status": "REMOTE_LOCAL_SHA_CLOSED", "raw_trace_payloads_committed": False, "traces": [
        {"stage": "S3_LARGE_INDEX_PREFILL", **require_local(s3t, args.s3_local_trace)},
        {"stage": "S4_LARGE_INDEX_PREFILL", **require_local(s4t, args.s4_local_trace)},
        {"stage": "S5_LARGE_INDEX_PREFILL", **require_local(s5pt, args.s5_prefill_local_trace)},
        *[{"stage": f"S5_DECODE_SMALLINDEX_{number + 2}", **item} for number, item in enumerate(small_local)],
    ], "structural_zero_nonraw_evidence": {"status": "STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED", "large_target_function": large_function, "logical_decode_counts": {f"DECODE{i}": large_decode["phase_trace_summary"][f"DECODE{i}"]["record_count"] for i in range(1, 5)}, "source_receipt_sha256": sha256_file(args.s5_decode_large)}}
    args.output.mkdir(parents=True)
    l0 = {"schema_version": SCHEMA, "status": "L0_REVALIDATION_PASS", "scientific_eligible": False, "inherited": {"s1_sha256": sha256_file(args.s1), "s2_sha256": sha256_file(args.s2), "large_target_sha256": sha256_file(args.large_target), "decode_target_sha256": sha256_file(args.decode_target), "model_id": s1["identity"]["model_id"], "revision": s1["identity"]["model_revision"], "workload": "S0/B1/T128/Decode4/TEXT", "historical_34_forbidden": True, "historical_348_not_reused": True}}
    atomic_json(args.output / "L0_REVALIDATION.json", l0)
    copy_source(args.scope, args.output / "L1_RECOVERY_SCOPE.json"); copy_source(args.large_target, args.output / "LARGE_INDEX_PREFILL_TARGET.json")
    copy_source(args.decode_census, args.output / "DECODE_PATH_CENSUS.json"); copy_source(args.decode_map_receipt, args.output / "DECODE_STATIC_MAP_RECEIPT.json"); copy_source(args.decode_map, args.output / "DECODE_SMALLINDEX_STATIC_MAP.tsv"); copy_source(args.decode_target, args.output / "DECODE_INDEX_TARGET.json")
    repro = {"schema_version": SCHEMA, "status": "S3_S4_REPRODUCIBILITY_PASS", "scientific_eligible": True, "target_role": "LARGE_INDEX_PREFILL_TARGET", "function": large_function, "static_range": [101, 102], "s3": s3t, "s4": s4t, "same_record_count": True, "raw_sha_equality_not_required": True, "prewarm_trace_count": [s3["child"]["capture"]["prewarm_trace_count"], s4["child"]["capture"]["prewarm_trace_count"]]}
    atomic_json(args.output / "S3_S4_REPRODUCIBILITY.json", repro)
    s5 = {"schema_version": SCHEMA, "status": "S5_FULL_WORKLOAD_CAPTURE_PASS", "scientific_eligible": True, "prefill_target": {"role": "LARGE_INDEX_PREFILL_TARGET", "function": large_function, "static_range": [101, 102], "record_count": s5pt["record_count"], "trace": s5pt}, "large_index_decode_outcome": {"status": "STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED", "logical_decode_coverage": large_decode["logical_decode_coverage"], "logical_decode_counts": {f"DECODE{i}": large_decode["phase_trace_summary"][f"DECODE{i}"] for i in range(1, 5)}}, "decode_target": {"role": "DECODE_INDEX_TARGET", "function": decode_target["function"]["mangled_name"], "static_range": [17, 18], "opcode": "LDG.E", "actual_forward_records": {f"DECODE{i}": small_capture["phase_trace_summary"][f"DECODE{i}"] for i in range(2, 5)}, "logical_decode1": small_capture["phase_trace_summary"]["DECODE1"]}, "output_checksum": small_capture["output_checksum"], "prewarm_trace_count": small_capture["prewarm_trace_count"]}
    atomic_json(args.output / "S5_FULL_WORKLOAD_SUMMARY.json", s5)
    copy_source(args.storage_estimate, args.output / "S5_STORAGE_ESTIMATE.json"); atomic_json(args.output / "RAW_ARTIFACT_INDEX.json", index)
    report = "# Llama NVBit 1.7.5 recovery capture\n\n`LLAMA_FULL_TARGET_TRACE_COMPLETE`. The frozen Llama S0/B1/T128/decode4 contract is unchanged.\n\n- `LARGE_INDEX_PREFILL_TARGET`: exact `indexSelectLargeIndex`, direct NVBit static range `[101,102)`, `LDG.E.U16`. Historical 34 is forbidden and historical 348 was not reused.\n- `DECODE_INDEX_TARGET`: independently observed shape-dependent exact `indexSelectSmallIndex`, direct NVBit-native static range `[17,18)`, `LDG.E`. It was mapped from the current model/runtime, not copied from LargeIndex.\n\nLargeIndex emitted 8,192 address-bearing records in each S3/S4 prefill run and in S5 Prefill. Its S5 logical Decode1--4 counts are zero because that exact function did not launch during decode: `STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED`, not a claim that decode had no memory access. The profiler census observed SmallIndex in all three actual cache-correct decode forwards; the SmallIndex S5 capture produced 64 address-bearing records in each of logical Decode2--4. Logical Decode1 remains the prefill-derived greedy token under the immutable four-token workload, with no separate CUDA forward.\n\nAll raw traces are remote-to-local SHA closed and remain outside Git.\n"
    (args.output / "LLAMA_RECOVERY_REPORT.md").write_text(report, encoding="utf-8")
    data = make_manifest(args.output); atomic_json(args.output / "PUBLISH_MANIFEST.json", data); atomic_json(args.output / "PUBLISH_VALIDATION.json", validate(args.output, data))
    print("PASS LLAMA_FULL_TARGET_TRACE_COMPLETE")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Llama recovery publication: {exc}")
