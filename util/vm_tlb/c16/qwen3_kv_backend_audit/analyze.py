#!/usr/bin/env python3
"""CPU-only independent consumer for C16 Qwen3 KV context/backend audit."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import struct
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path

HEADER = struct.Struct("<8sIIQQQ")
RECORD = struct.Struct("<6I32Q")
SOURCE_INDICES = (237, 475, 713, 950)
DEST_INDICES = (241, 479, 717, 953)
EXPECTED_SET = set(SOURCE_INDICES + DEST_INDICES)
PRODUCER_REVIEW_COMMIT = "c94825dab9b114e468a83cdad009181f23add608"
COORDINATION_COMMIT = "f7d3be1c79c3089fe89f5668c0275654ddf55eb3"
SOURCE_COMMIT = "0720e206c6ba28887e4d60ef60a6a089f6c1cc76"
QUANTILE_DEFINITION = "nearest-rank: sorted_values[ceil(p*n)-1]; min/max exact"

SCENARIOS = {
    "S2": {
        "run": "C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v20-s2-repeat-k_20260916T162000Z_202020202020",
        "catalog_sha256": "aabeb406523d55355432b3367c6089b43a8c7b4821b97a100717a1b37480a2c8",
        "manifest_sha256": "f52fcdf0e281407f106f4f478fa1072a4ec299dde30df7c32abb089e8b7c6116",
        "grid_x": 16392,
        "event_total": 16785408,
        "k_shape": [1, 8, 2049, 128],
        "repeat_shape": [1, 32, 2049, 128],
        "k_bytes": 4196352,
        "repeat_bytes": 16785408,
    },
    "S3": {
        "run": "C16R_qwen3-8b_s3-text_decode_nvbit-warp-mref-shard_v20-s3-repeat-k_20260916T163000Z_303030303030",
        "catalog_sha256": "b85430200f520506bc2abf3165af018b628c11626d47b7c77e00eb2b03c79082",
        "manifest_sha256": "d986397b7b32dafd7efe3cfcbfaae71dd367d4c8ce0587aa8ea8e35a0acb339b",
        "grid_x": 65544,
        "event_total": 67117056,
        "k_shape": [1, 8, 8193, 128],
        "repeat_shape": [1, 32, 8193, 128],
        "k_bytes": 16779264,
        "repeat_bytes": 67117056,
    },
}

SOURCE_FILES = {
    "eager": ("src/transformers/models/qwen3/modeling_qwen3.py", "5fec83d47888e44a0f3e0ffb2b067ce08e4712d3"),
    "sdpa": ("src/transformers/integrations/sdpa_attention.py", "9c924c048ad52929a2d0f890a22295d5a56ef505"),
    "flash_attention_2": ("src/transformers/integrations/flash_attention.py", "a78166ed040b620c6e24a7e2c64c06c96f2d89d9"),
    "flex_attention": ("src/transformers/integrations/flex_attention.py", "1aa146e4a40737edd100059f05208da1a6d5e3dc"),
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def nearest_rank(values: list[int | float]) -> dict:
    if not values:
        return {key: None for key in ("min", "p25", "median", "p75", "p90", "max")}
    ordered = sorted(values)
    def pick(p):
        return ordered[max(0, math.ceil(p * len(ordered)) - 1)]
    return {"min": ordered[0], "p25": pick(.25), "median": pick(.5), "p75": pick(.75), "p90": pick(.9), "max": ordered[-1]}


def ranges_from_context(context: dict) -> list[tuple[str, int, int]]:
    result = []
    for item in context["ranges"]:
        begin = int(item["address_start_hex"], 0)
        result.append((item["class"], begin, begin + int(item["storage_bytes"])))
    if context.get("same_process_only") is not True or len(result) != 2:
        raise ValueError("context is not the expected same-process two-object map")
    return result


def interval_role(address: int, width: int, ranges) -> str:
    hits = [name for name, begin, end in ranges if begin <= address and address + width <= end]
    return hits[0] if len(hits) == 1 else "NEITHER_OR_AMBIGUOUS"


def static_audit(root: Path) -> dict:
    path = root / "STATIC_MREF_MAP.tsv"
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    selected = [row for row in rows if row["has_mref"] == "1" and row["memory_space"] in ("GLOBAL", "GLOBAL_TO_SHARED")]
    compact = []
    register_pairs = {237: "R4:R5", 475: "R4:R5", 713: "R4:R5", 950: "R2:R3"}
    for row in selected:
        index = int(row["nvbit_static_index"])
        side = "SOURCE_LDG" if index in SOURCE_INDICES else "DESTINATION_STG" if index in DEST_INDICES else "UNEXPECTED"
        expected_operand = register_pairs.get(index)
        if expected_operand:
            expected_lo = expected_operand.split(":")[0]
            operand_ok = f"[{expected_lo}.64]" in row["sass"]
            address_mode = "REGISTER_PAIR"
        else:
            operand_ok = row["opcode"].startswith("STG")
            address_mode = "MREF"
        compact.append({
            "static_index": index,
            "instruction_offset": int(row["instruction_offset"]),
            "opcode": row["opcode"],
            "memory_space": row["memory_space"],
            "is_load": row["is_load"] == "1",
            "is_store": row["is_store"] == "1",
            "sass": row["sass"],
            "side": side,
            "access_width_bytes": 2 if ".U16" in row["opcode"] else None,
            "address_mode": address_mode,
            "source_register_pair": expected_operand,
            "operand_binding_pass": operand_ok,
        })
    functions = sorted({row["function_mangled_name"] for row in selected})
    libraries = sorted({row["libtorch_cuda_sha256"] for row in selected})
    status = (
        {item["static_index"] for item in compact} == EXPECTED_SET
        and len(compact) == 8
        and all(item["memory_space"] == "GLOBAL" and item["access_width_bytes"] == 2 and item["operand_binding_pass"] for item in compact)
        and sum(item["is_load"] for item in compact) == 4
        and sum(item["is_store"] for item in compact) == 4
    )
    return {
        "status": "PASS" if status else "FAIL",
        "static_map_path": str(path),
        "static_map_sha256": sha256(path),
        "all_static_rows": len(rows),
        "direct_global_mref_count": len(compact),
        "ldgsts_global_to_shared_count": sum(item["memory_space"] == "GLOBAL_TO_SHARED" for item in compact),
        "source_indices": list(SOURCE_INDICES),
        "destination_indices": list(DEST_INDICES),
        "function_mangled_names": functions,
        "libtorch_cuda_sha256": libraries,
        "paths": compact,
        "tracer_correction_source_anchor": f"{PRODUCER_REVIEW_COMMIT}:util/vm_tlb/c16/campaign/v20_warp_tool.cu",
        "capture_register_map_anchor": f"{PRODUCER_REVIEW_COMMIT}:util/vm_tlb/c16/campaign/v20_capture.py:13",
    }


def authority_preflight(authority: Path) -> dict:
    report = {
        "status": "PASS",
        "coordination_commit": COORDINATION_COMMIT,
        "producer_review_commit": PRODUCER_REVIEW_COMMIT,
        "model": "Qwen/Qwen3-8B",
        "revision": "b968826d9c46dd6066d109eabc6255188de91218",
        "runtime": {"torch": "2.5.1+cu124", "transformers": "4.51.0", "dtype": "BF16", "attention_backend": "eager", "gpu_producer": "RTX4080/SM89"},
        "consumer_resource_use": {"cpu_only": True, "gpu_used": False, "gpu_lock_requested": False, "nvbit_ncu_nsys_run": False, "single_worker": True},
        "scenarios": {},
    }
    ack_times = {}
    for name, cfg in SCENARIOS.items():
        root = authority / "raw" / cfg["run"]
        catalog_path = authority / "catalog" / "entries" / f"{cfg['run']}.json"
        ack_path = authority / "reports" / "transfer_acks" / f"{cfg['run']}.TRANSFER_ACK.json"
        catalog = load(catalog_path)
        ack = load(ack_path)
        actual = {
            "run_id": cfg["run"],
            "raw_root": str(root),
            "catalog_sha256": sha256(catalog_path),
            "catalog_expected_sha256": cfg["catalog_sha256"],
            "run_manifest_sha256": sha256(root / "RUN_MANIFEST.json"),
            "run_manifest_expected_sha256": cfg["manifest_sha256"],
            "warp_manifest_sha256": sha256(root / "WARP_SHARD_MANIFEST.json"),
            "ack_sha256": sha256(ack_path),
            "ack_verification_status": ack.get("verification_status"),
            "ack_catalog_binding": ack.get("catalog_entry_sha256"),
            "ack_source_manifest_binding": ack.get("source_manifest_sha256"),
            "ack_verified_at_utc": ack.get("verified_at_utc"),
            "catalog_transfer_status": catalog.get("transfer_status"),
            "catalog_model": catalog.get("model"),
            "catalog_revision": catalog.get("revision"),
            "catalog_target": catalog.get("target"),
        }
        actual["pass"] = (
            actual["catalog_sha256"] == actual["catalog_expected_sha256"]
            and actual["run_manifest_sha256"] == actual["run_manifest_expected_sha256"]
            and actual["ack_verification_status"] == "PASS"
            and actual["ack_catalog_binding"] == actual["catalog_sha256"]
            and actual["ack_source_manifest_binding"] == actual["run_manifest_sha256"]
            and actual["catalog_transfer_status"] == "TRANSFER_ACKED"
            and actual["catalog_model"] == "Qwen/Qwen3-8B"
            and actual["catalog_revision"] == "b968826d9c46dd6066d109eabc6255188de91218"
        )
        report["scenarios"][name] = actual
        ack_times[name] = datetime.fromisoformat(actual["ack_verified_at_utc"].replace("Z", "+00:00"))
        if not actual["pass"]:
            report["status"] = "FAIL"
    report["serial_admission_order"] = {
        "s2_ack": report["scenarios"]["S2"]["ack_verified_at_utc"],
        "s3_ack": report["scenarios"]["S3"]["ack_verified_at_utc"],
        "s2_precedes_s3": ack_times["S2"] < ack_times["S3"],
    }
    if not report["serial_admission_order"]["s2_precedes_s3"]:
        report["status"] = "FAIL"
    return report


def parse_shard(root: Path, item: dict, expected_grid: int) -> dict:
    index = int(item["static_index"])
    trace = root / item["trace"]
    context_path = root / item["address_context"]
    stdout_path = trace.with_suffix(".stdout.log")
    context = load(context_path)
    if int(context["static_index"]) != index or context["function_occurrence"] != "0":
        raise ValueError(f"context identity mismatch for {index}")
    ranges = ranges_from_context(context)
    expected_role = "KV_POST_UPDATE_K" if index in SOURCE_INDICES else "KV_DERIVED_REPEAT_K"
    expected_mode = "REGISTER_PAIR" if index in SOURCE_INDICES else "MREF"
    terminal_text = stdout_path.read_text(encoding="utf-8", errors="replace")
    operand = re.search(rf"C16_V20_WARP_OPERANDS static={index} .*address_mode=(\S+)", terminal_text)
    terminal = re.search(rf"C16_WARP_TERMINAL static={index} occurrence=(\d+) records=(\d+) overflow=(\d+)", terminal_text)
    if not operand or operand.group(1) != expected_mode or not terminal:
        raise ValueError(f"terminal/address-mode proof missing for {index}")
    role_counts = Counter()
    units = {128: set(), 4096: set(), 65536: set(), 2 * 1024 * 1024: set()}
    ctas = set()
    warps = set()
    active_events = 0
    address_min = None
    address_max = None
    record_count = 0
    digest = hashlib.sha256()
    with trace.open("rb") as stream:
        raw_header = stream.read(HEADER.size)
        digest.update(raw_header)
        if len(raw_header) != HEADER.size:
            raise ValueError(f"short trace header {trace}")
        header = HEADER.unpack(raw_header)
        magic, header_index, occurrence, callback, overflow, written = header
        if magic != b"C16WARP1" or header_index != index or occurrence != 0 or overflow != 0:
            raise ValueError(f"header identity/overflow mismatch for {index}")
        while True:
            raw = stream.read(RECORD.size)
            if not raw:
                break
            digest.update(raw)
            if len(raw) != RECORD.size:
                raise ValueError(f"unaligned trace record for {index}")
            record = RECORD.unpack(raw)
            if record[0] != index:
                raise ValueError(f"record static mismatch for {index}")
            mask = record[1]
            addresses = record[6:] if mask == 0xFFFFFFFF else tuple(address for lane, address in enumerate(record[6:]) if mask >> lane & 1)
            ctas.add((record[2], record[3], record[4]))
            warps.add(record[5])
            active_events += len(addresses)
            record_count += 1
            for address in addresses:
                role_counts[interval_role(address, 2, ranges)] += 1
                address_min = address if address_min is None else min(address_min, address)
                address_max = address if address_max is None else max(address_max, address)
                for size, seen in units.items():
                    seen.add(address // size)
                    seen.add((address + 1) // size)
    trace_sha = digest.hexdigest()
    declared_records = int(item["records"])
    terminal_records = int(terminal.group(2))
    terminal_overflow = int(terminal.group(3))
    terminal_occurrence = int(terminal.group(1))
    checks = {
        "trace_sha_match": trace_sha == item["trace_sha256"],
        "context_sha_match": sha256(context_path) == item["address_context_sha256"],
        "record_count_match": record_count == declared_records == written == callback == terminal_records,
        "overflow_zero": overflow == int(item["overflow"]) == terminal_overflow == 0,
        "occurrence_zero": occurrence == int(item["occurrence"]) == terminal_occurrence == 0,
        "classification_executed": item["classification"] == "EXECUTED_SHARD" and record_count > 0,
        "typed_object_join": role_counts[expected_role] == active_events and sum(role_counts.values()) == active_events,
        "full_cta_extent": min(x for x, _, _ in ctas) == 0 and max(x for x, _, _ in ctas) == expected_grid - 1 and len(ctas) == expected_grid,
    }
    if not all(checks.values()):
        raise ValueError(f"shard closure failed for {index}: {checks}, roles={role_counts}")
    return {
        "static_index": index,
        "side": "SOURCE_LDG" if index in SOURCE_INDICES else "DESTINATION_STG",
        "expected_object": expected_role,
        "classification": item["classification"],
        "record_count": record_count,
        "active_lane_events": active_events,
        "overflow": overflow,
        "terminal_consistent": True,
        "address_mode": expected_mode,
        "unique_cta_coords": len(ctas),
        "cta_x_min": min(x for x, _, _ in ctas),
        "cta_x_max": max(x for x, _, _ in ctas),
        "warp_ids": ",".join(str(value) for value in sorted(warps)),
        "unique_128B_lines": len(units[128]),
        "unique_4K_pages": len(units[4096]),
        "unique_64K_pages": len(units[65536]),
        "unique_2M_pages": len(units[2 * 1024 * 1024]),
        "address_min_hex": hex(address_min),
        "address_max_hex": hex(address_max),
        "access_width_bytes": 2,
        "trace_sha256": trace_sha,
        "address_context_sha256": sha256(context_path),
        "object_counts": dict(role_counts),
        "expected_object_count": role_counts[expected_role],
        "neither_or_ambiguous_count": role_counts["NEITHER_OR_AMBIGUOUS"],
        "join_fraction": role_counts[expected_role] / active_events,
        "cta_coords": ctas,
    }


def analyze_scenario(name: str, authority: Path) -> dict:
    cfg = SCENARIOS[name]
    root = authority / "raw" / cfg["run"]
    manifest = load(root / "WARP_SHARD_MANIFEST.json")
    items = manifest["shards"]
    if len(items) != 8 or {int(item["static_index"]) for item in items} != EXPECTED_SET:
        raise ValueError(f"{name}: manifest static set mismatch")
    static = static_audit(root)
    if static["status"] != "PASS":
        raise ValueError(f"{name}: static audit failed")
    fingerprints = []
    union_ctas = set()
    for item in sorted(items, key=lambda x: int(x["static_index"])):
        print(json.dumps({"event": "shard_start", "scenario": name, "static_index": item["static_index"]}), flush=True)
        row = parse_shard(root, item, cfg["grid_x"])
        union_ctas.update(row.pop("cta_coords"))
        fingerprints.append(row)
        print(json.dumps({"event": "shard_complete", "scenario": name, "static_index": row["static_index"], "records": row["record_count"], "events": row["active_lane_events"]}), flush=True)
    total_events = sum(row["active_lane_events"] for row in fingerprints)
    full_scope = {
        "status": "PASS",
        "expected_grid_x": cfg["grid_x"],
        "executed_shards": len(fingerprints),
        "zero_shards": 0,
        "every_shard_cta_x_min_zero": all(row["cta_x_min"] == 0 for row in fingerprints),
        "every_shard_cta_x_max_expected": all(row["cta_x_max"] == cfg["grid_x"] - 1 for row in fingerprints),
        "unique_cta_union": len(union_ctas),
        "unique_cta_union_expected": cfg["grid_x"],
        "all_overflow_zero": all(row["overflow"] == 0 for row in fingerprints),
        "all_terminal_consistent": all(row["terminal_consistent"] for row in fingerprints),
        "all_typed_joins_lossless": all(row["join_fraction"] == 1.0 and row["neither_or_ambiguous_count"] == 0 for row in fingerprints),
        "no_cta_slicing_evidence": all(row["unique_cta_coords"] == cfg["grid_x"] for row in fingerprints),
        "function_occurrence": 0,
        "total_active_lane_events": total_events,
        "expected_active_lane_events": cfg["event_total"],
    }
    if not (
        full_scope["every_shard_cta_x_min_zero"]
        and full_scope["every_shard_cta_x_max_expected"]
        and full_scope["unique_cta_union"] == full_scope["unique_cta_union_expected"]
        and full_scope["all_overflow_zero"]
        and full_scope["all_terminal_consistent"]
        and full_scope["all_typed_joins_lossless"]
        and full_scope["no_cta_slicing_evidence"]
        and total_events == cfg["event_total"]
    ):
        raise ValueError(f"{name}: full-scope gate failed {full_scope}")
    receipt = load(root / "KPOST_RECEIPT.json")
    storage = {
        "k_post": {"shape": receipt["k_post"]["shape"], "storage_bytes": receipt["k_post"]["storage_bytes"], "dtype": receipt["k_post"]["dtype"]},
        "repeat_k": {"shape": receipt["repeat_k"]["shape"], "storage_bytes": receipt["repeat_k"]["storage_bytes"], "dtype": receipt["repeat_k"]["dtype"]},
        "attention_backend": receipt["attention_backend"],
        "transformers": receipt["transformers"],
    }
    if storage["k_post"]["shape"] != cfg["k_shape"] or storage["repeat_k"]["shape"] != cfg["repeat_shape"] or storage["k_post"]["storage_bytes"] != cfg["k_bytes"] or storage["repeat_k"]["storage_bytes"] != cfg["repeat_bytes"]:
        raise ValueError(f"{name}: storage receipt mismatch")
    return {"name": name, "static": static, "fingerprints": fingerprints, "full_scope": full_scope, "storage": storage}


def source_audit(source_repo: Path) -> tuple[dict, list[dict]]:
    commit = git(source_repo, "rev-parse", SOURCE_COMMIT)
    rows = []
    contents = {}
    for backend, (path, expected_blob) in SOURCE_FILES.items():
        tree_line = git(source_repo, "ls-tree", SOURCE_COMMIT, path)
        actual_blob = tree_line.split()[2]
        text = git(source_repo, "cat-file", "blob", actual_blob)
        contents[backend] = text
        rows.append({"backend": backend, "ref": "v4.51.0", "tree_commit": SOURCE_COMMIT, "path": path, "expected_blob": expected_blob, "actual_blob": actual_blob, "blob_match": actual_blob == expected_blob})
    eager = contents["eager"]
    sdpa = contents["sdpa"]
    flash = contents["flash_attention_2"]
    flex = contents["flex_attention"]
    behavior = {
        "eager": {
            "explicit_hf_repeat_kv": "key_states = repeat_kv(key, module.num_key_value_groups)" in eager and "value_states = repeat_kv(value, module.num_key_value_groups)" in eager,
            "anchor_lines": "modeling_qwen3.py:132-141,154-155,178,229-239",
            "classification": "EXPLICIT_MATERIALIZATION",
        },
        "sdpa": {
            "explicit_hf_repeat_kv": "key = repeat_kv(key, module.num_key_value_groups)" in sdpa and "value = repeat_kv(value, module.num_key_value_groups)" in sdpa,
            "anchor_lines": "sdpa_attention.py:6-15,29-31,54-62",
            "classification": "EXPLICIT_MATERIALIZATION_BEFORE_PYTORCH_SDPA",
        },
        "flash_attention_2": {
            "explicit_hf_repeat_kv": "repeat_kv" in flash,
            "passes_original_kv_heads": "_flash_attention_forward(" in flash and "key = key.transpose(1, 2)" in flash,
            "anchor_lines": "flash_attention.py:11-29,49-60",
            "classification": "NO_EXPLICIT_HF_REPEAT_KV_PASSES_ORIGINAL_KV_HEAD_COUNT",
        },
        "flex_attention": {
            "has_repeat_fallback": "key = repeat_kv(key, query.shape[1] // key.shape[1])" in flex,
            "normal_path_enable_gqa": "enable_gqa = True" in flex and "enable_gqa=enable_gqa" in flex,
            "fallback_non_power_of_two": "if not ((num_local_query_heads & (num_local_query_heads - 1)) == 0):" in flex,
            "accepted_qwen3_fallback_fires": False,
            "anchor_lines": "flex_attention.py:168-177,180-190,210-226",
            "classification": "ENABLE_GQA_NO_EXPLICIT_REPEAT_FOR_ACCEPTED_POWER_OF_TWO_32_LOCAL_QUERY_HEADS",
        },
    }
    source_identity = {
        "status": "PASS" if commit == SOURCE_COMMIT and all(row["blob_match"] for row in rows) else "FAIL",
        "declared_tag": "v4.51.0",
        "tree_commit": commit,
        "exact_blob_count": len(rows),
        "all_blob_ids_match": all(row["blob_match"] for row in rows),
        "remote_tag_ref_roundtrip": "NOT_REPEATED_AFTER_EXACT_COMMIT_AND_TREE_BLOB_MATCH; initial ls-remote timed out",
        "accepted_qwen3_head_binding": {"num_attention_heads": 32, "num_key_value_heads": 8, "num_key_value_groups": 4, "authority": "accepted K-post/repeat-K receipt shapes [1,8,T,128] -> [1,32,T,128]"},
        "behavior": behavior,
    }
    if source_identity["status"] != "PASS" or not behavior["eager"]["explicit_hf_repeat_kv"] or not behavior["sdpa"]["explicit_hf_repeat_kv"] or behavior["flash_attention_2"]["explicit_hf_repeat_kv"] or not behavior["flex_attention"]["normal_path_enable_gqa"]:
        raise ValueError(f"backend source classification failed: {source_identity}")
    for row in rows:
        row.update(behavior[row["backend"]])
    return source_identity, rows


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build(authority: Path, out: Path, preflight: dict, results: dict, source_identity: dict, backend_rows: list[dict]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    preflight["status"] = "PASS"
    preflight["raw_streaming_validation"] = {}
    for name, result in results.items():
        preflight["raw_streaming_validation"][name] = {
            "shard_count": len(result["fingerprints"]),
            "all_trace_hashes_match": True,
            "all_context_hashes_match": True,
            "all_header_counts_close": True,
            "all_typed_joins_lossless": True,
        }
    preflight["exact_transformers_source"] = source_identity
    dump(out / "AUTHORITY_AUDIT.json", preflight)
    static = results["S2"]["static"]
    static["s2_s3_static_map_sha_equal"] = results["S2"]["static"]["static_map_sha256"] == results["S3"]["static"]["static_map_sha256"]
    static["s3_static_map_sha256"] = results["S3"]["static"]["static_map_sha256"]
    dump(out / "STATIC_PATH_AUDIT.json", static)
    fingerprint_fields = ["static_index", "side", "expected_object", "classification", "record_count", "active_lane_events", "overflow", "terminal_consistent", "address_mode", "unique_cta_coords", "cta_x_min", "cta_x_max", "warp_ids", "unique_128B_lines", "unique_4K_pages", "unique_64K_pages", "unique_2M_pages", "address_min_hex", "address_max_hex", "access_width_bytes", "trace_sha256", "address_context_sha256"]
    join_fields = ["static_index", "side", "expected_object", "active_lane_events", "expected_object_count", "neither_or_ambiguous_count", "join_fraction", "address_context_sha256"]
    for name, result in results.items():
        write_tsv(out / f"{name}_SHARD_FINGERPRINTS.tsv", result["fingerprints"], fingerprint_fields)
        write_tsv(out / f"{name}_OBJECT_JOIN.tsv", result["fingerprints"], join_fields)
        dump(out / f"{name}_FULL_SCOPE_AUDIT.json", result["full_scope"])
    s2, s3 = results["S2"], results["S3"]
    event_ratio = s3["full_scope"]["total_active_lane_events"] / s2["full_scope"]["total_active_lane_events"]
    grid_ratio = SCENARIOS["S3"]["grid_x"] / SCENARIOS["S2"]["grid_x"]
    scaling = {
        "status": "PASS",
        "semantic_target": "layer0.self_attn.repeat_kv(K)",
        "evidence_class": "KV_STORAGE_DIRECT_READ",
        "static_set_identical": True,
        "static_indices": sorted(EXPECTED_SET),
        "S2": {"grid_x": SCENARIOS["S2"]["grid_x"], "total_active_lane_events": s2["full_scope"]["total_active_lane_events"], "storage": s2["storage"]},
        "S3": {"grid_x": SCENARIOS["S3"]["grid_x"], "total_active_lane_events": s3["full_scope"]["total_active_lane_events"], "storage": s3["storage"]},
        "ratios": {"grid_s3_over_s2": grid_ratio, "events_s3_over_s2": event_ratio, "k_post_storage_s3_over_s2": SCENARIOS["S3"]["k_bytes"] / SCENARIOS["S2"]["k_bytes"], "repeat_k_storage_s3_over_s2": SCENARIOS["S3"]["repeat_bytes"] / SCENARIOS["S2"]["repeat_bytes"]},
        "per_executed_shard_event_distributions": {
            "S2": nearest_rank([row["active_lane_events"] for row in s2["fingerprints"]]),
            "S3": nearest_rank([row["active_lane_events"] for row in s3["fingerprints"]]),
        },
        "typed_object_membership_fractions": {"source_KV_POST_UPDATE_K": 1.0, "destination_KV_DERIVED_REPEAT_K": 1.0},
        "page_and_line_distribution_table": "PAGE_FOOTPRINT_DESCRIPTORS.tsv",
        "endpoint_note": "approximately 4x, not exactly 4x: sequence extent is 2049 -> 8193",
        "tensor_expansion": {"num_attention_heads": 32, "num_key_value_heads": 8, "repeat_k_over_k_post_S2": 4.0, "repeat_k_over_k_post_S3": 4.0, "classification": "model/backend tensor-shape transformation; not measured traffic"},
        "prohibitions": ["no cross-replay VA union", "no cross-shard chronology", "no reconstructed reuse distance", "no DRAM bytes inferred from lane events", "page descriptors are not TLB miss rates"],
    }
    dump(out / "S2_VS_S3_CONTEXT_SCALING.json", scaling)
    amplification = []
    for name, result in results.items():
        for side, indices, tensor_key in (("SOURCE_LDG", SOURCE_INDICES, "k_bytes"), ("DESTINATION_STG", DEST_INDICES, "repeat_bytes")):
            subset = [row for row in result["fingerprints"] if row["side"] == side]
            events = sum(row["active_lane_events"] for row in subset)
            logical = events * 2
            amplification.append({
                "scenario": name, "side": side, "static_indices": ",".join(map(str, indices)), "static_count": len(subset),
                "record_count": sum(row["record_count"] for row in subset), "active_lane_events": events,
                "access_width_bytes": 2, "logical_lane_bytes_not_dram": logical, "corresponding_tensor_bytes": SCENARIOS[name][tensor_key],
                "logical_lane_bytes_over_tensor_bytes": logical / SCENARIOS[name][tensor_key],
                "s3_over_s2_event_ratio": event_ratio if name == "S3" else "NA",
            })
    write_tsv(out / "SOURCE_DESTINATION_AMPLIFICATION.tsv", amplification, ["scenario", "side", "static_indices", "static_count", "record_count", "active_lane_events", "access_width_bytes", "logical_lane_bytes_not_dram", "corresponding_tensor_bytes", "logical_lane_bytes_over_tensor_bytes", "s3_over_s2_event_ratio"])
    page_rows = []
    for side, tensor_key in (("SOURCE_LDG", "k_bytes"), ("DESTINATION_STG", "repeat_bytes")):
        for size, field in ((128, "unique_128B_lines"), (4096, "unique_4K_pages"), (65536, "unique_64K_pages"), (2 * 1024 * 1024, "unique_2M_pages")):
            values_by_scenario = {}
            for name, result in results.items():
                values = [row[field] for row in result["fingerprints"] if row["side"] == side]
                values_by_scenario[name] = values
            sum_ratio = sum(values_by_scenario["S3"]) / sum(values_by_scenario["S2"])
            for name in ("S2", "S3"):
                values = values_by_scenario[name]
                denom_mib = (SCENARIOS[name][tensor_key] * len(values)) / (1024 * 1024)
                page_rows.append({"scenario": name, "side": side, "unit_bytes": size, "per_shard_distribution": json.dumps(nearest_rank(values), sort_keys=True, separators=(",", ":")), "sum_of_per_shard_uniques": sum(values), "tensor_mib_denominator_across_shards": denom_mib, "units_per_tensor_mib": sum(values) / denom_mib, "s3_over_s2_sum_ratio": sum_ratio})
    write_tsv(out / "PAGE_FOOTPRINT_DESCRIPTORS.tsv", page_rows, ["scenario", "side", "unit_bytes", "per_shard_distribution", "sum_of_per_shard_uniques", "tensor_mib_denominator_across_shards", "units_per_tensor_mib", "s3_over_s2_sum_ratio"])
    write_tsv(out / "BACKEND_SOURCE_AUDIT.tsv", backend_rows, ["backend", "ref", "tree_commit", "path", "expected_blob", "actual_blob", "blob_match", "classification", "explicit_hf_repeat_kv", "passes_original_kv_heads", "normal_path_enable_gqa", "has_repeat_fallback", "fallback_non_power_of_two", "accepted_qwen3_fallback_fires", "anchor_lines"])
    ncu = {
        "status": "PRESERVED_BOUNDED_NOT_NUMERICALLY_COMPARED",
        "producer_pack": f"{PRODUCER_REVIEW_COMMIT}:docs/vm_tlb/review_packs/C16_QWEN3_S3_KV_SCALING_109_V20/NCU_TYPED_EVIDENCE.json",
        "reports": [
            {"scenario": "S2_TEXT", "report": "ncu/S2_TEXT_isolated_ncu.ncu-rep", "report_git_blob": "4184b6cf2a2f8dd37678d8ca2304cf806124f9f9", "report_size_bytes": 3789189, "log": "ncu/S2_TEXT_isolated_ncu.log", "log_git_blob": "6d943139953caf327383b9385fdc6dbf7d94351b", "log_size_bytes": 1251, "cache_control": "none", "warning": "uncontrolled GPU caches"},
            {"scenario": "S3_TEXT", "report": "ncu/S3_TEXT_isolated_ncu.ncu-rep", "report_git_blob": "cce72b3b9c10be3bf94220948c0c1d214038af43", "report_size_bytes": 3789189, "log": "ncu/S3_TEXT_isolated_ncu.log", "log_git_blob": "a635760681d1408945392ac8ae905e14114e4f9a", "log_size_bytes": 1255, "cache_control": "none", "warning": "uncontrolled GPU caches"},
        ],
        "numeric_cross_scenario_comparison": "NOT_COMPARABLE_FROM_TYPED_TEXT_AUTHORITY",
        "reason": "preserved text logs identify application replay and explicitly warn that GPU caches are uncontrolled; no typed metric values/units are present in the logs, and this CPU-only Goal does not invoke NCU on binary reports",
        "ncu_executed_this_goal": False,
        "claim_boundary": "no cache/TLB causal or byte-traffic claim",
    }
    dump(out / "NCU_EVIDENCE_AUDIT.json", ncu)
    backend_md = """# Backend representativeness\n\nThe audit is bound to Transformers `v4.51.0`, tree commit `0720e206c6ba28887e4d60ef60a6a089f6c1cc76`, and the four blob IDs listed in `BACKEND_SOURCE_AUDIT.tsv`. No current-main behavior is substituted.\n\n| backend | exact 4.51.0 behavior for Qwen3-8B | explicit HF repeat materialization |\n|---|---|---|\n| eager | Qwen3 eager calls `repeat_kv` on key and value with `num_key_value_groups` | yes |\n| SDPA | integration repeats key/value before PyTorch SDPA when the module has groups | yes |\n| FlashAttention2 | integration transposes and passes original key/value head counts to FA2 | no |\n| FlexAttention | with 32 local query heads (power of two), keeps `enable_gqa=True`; repeat is only the non-power-of-two fallback | no for accepted configuration |\n\nAccepted receipts bind K-post `[1,8,T,128]` to repeat-K `[1,32,T,128]`, hence 32 attention heads, 8 KV heads, and four groups. The V20 capture is therefore representative of the eager path and the same explicit-HF-repeat aspect of SDPA, but not of FA2 or normal-path FlexAttention. This source classification is not a performance ranking.\n"""
    (out / "BACKEND_REPRESENTATIVENESS.md").write_text(backend_md, encoding="utf-8")
    interpretation = f"""# Scientific interpretation\n\n## Independent raw closure\n\nBoth accepted authorities pass independently: all 16 C16WARP1 shards close their header/manifest/terminal counts and hashes, all have overflow zero, and every shard covers its full CTA extent. Source indices `{','.join(map(str, SOURCE_INDICES))}` join only the replay-local `KV_POST_UPDATE_K`; destination indices `{','.join(map(str, DEST_INDICES))}` join only `KV_DERIVED_REPEAT_K`. No cross-replay VA relation is used.\n\nS2 has 16,785,408 active-lane events and grid 16,392; S3 has 67,117,056 events and grid 65,544. Both ratios are `{event_ratio:.15f}`. This is approximately fourfold, not exact, because the sequence extent is 2049 -> 8193. Source reads and destination writes each scale by the same ratio. At width-qualified U16, logical lane bytes on either side equal the expanded repeat-K tensor bytes; these are instruction-level logical bytes, not DRAM bytes.\n\n## Backend classification\n\nTransformers 4.51.0 eager and SDPA explicitly materialize repeated K/V. FlashAttention2 does not use the HF repeat path, and FlexAttention uses `enable_gqa=True` for the accepted power-of-two 32-head configuration. Thus the measured repeat-K kernel is an eager/SDPA-style backend implementation path, not a model-intrinsic KV-cache requirement. The backend-independent component is narrower: compact K-post storage `[1,8,T,128]` and its long-context growth, plus the model's 32/8 GQA relationship.\n\n## Page descriptors and boundaries\n\n`PAGE_FOOTPRINT_DESCRIPTORS.tsv` reports only per-shard values and `SUM_OF_PER_SHARD_UNIQUES`. They scale with tensor/context extent but are not TLB miss rates. This Goal proves no cache/TLB cause, reuse distance, global chronology, DRAM traffic, all-attention behavior, direct QK/AV reads from original KV storage, or backend performance ordering.\n\n## Decision\n\nPrimary label: `EAGER_REPEAT_KV_AMPLIFICATION_INDEPENDENTLY_CLOSED_BACKEND_SPECIFIC`. Qualifications: `REPEAT_KV_MATERIALIZATION_SHARED_BY_EAGER_AND_SDPA_NOT_FLASH`, `QWEN3_KV_CONTEXT_SCALING_CLOSED_NO_ARCHITECTURE_GENERALIZATION`, and a precisely limited backend-independent compact-KV component. No cache/TLB mechanism or GPU follow-up is authorized. A future same-input eager-versus-legal-optimized-backend comparison is conditionally scientifically justified only if deployment relevance or measured performance becomes a project question.\n"""
    (out / "SCIENTIFIC_INTERPRETATION.md").write_text(interpretation, encoding="utf-8")
    final = {
        "goal": "C16_QWEN3_KV_CONTEXT_BACKEND_AUDIT_174NEW_V1",
        "status": "EAGER_REPEAT_KV_AMPLIFICATION_INDEPENDENTLY_CLOSED_BACKEND_SPECIFIC",
        "labels": ["EAGER_REPEAT_KV_AMPLIFICATION_INDEPENDENTLY_CLOSED_BACKEND_SPECIFIC", "REPEAT_KV_MATERIALIZATION_SHARED_BY_EAGER_AND_SDPA_NOT_FLASH", "QWEN3_KV_CONTEXT_SCALING_CLOSED_NO_ARCHITECTURE_GENERALIZATION", "QWEN3_KV_CONTEXT_SCALING_HAS_BACKEND_INDEPENDENT_COMPONENT"],
        "raw_closure": {"S2": "PASS", "S3": "PASS"},
        "event_and_grid_s3_over_s2": event_ratio,
        "source_scaling": event_ratio,
        "destination_scaling": event_ratio,
        "backend_independent_component": "compact KV_POST_UPDATE_K storage [1,8,T,128], its 2049->8193 context growth, and the 32-query-head/8-KV-head GQA semantic relationship; not explicit repeat materialization",
        "backend_specific_component": "explicit 4x repeat-K/KV materialization kernel observed under eager and shared by Transformers 4.51.0 SDPA integration, but absent from FA2 and normal power-of-two FlexAttention integration paths",
        "future_gpu_comparison": {"status": "CONDITIONALLY_SCIENTIFICALLY_JUSTIFIED_NOT_AUTHORIZED", "condition": "only if deployment relevance or measured backend performance becomes a project question", "minimal_question": "same accepted input and model: exact eager versus one legal optimized backend"},
        "new_gpu_work_authorized": False,
        "new_tlb_cache_mechanism_authorized": False,
    }
    dump(out / "FINAL_DECISION.json", final)
    open_issues = """# Open issues\n\n- No matched runtime performance measurement exists across eager, SDPA, FA2, and Flex for this accepted input; source behavior alone is not a performance ranking.\n- The producer's NCU reports remain bounded native artifacts with uncontrolled-cache warnings and no typed text metrics suitable for numerical S2/S3 comparison.\n- Remote `v4.51.0` tag ref round-trip timed out on 174-new, but exact source identity is closed by the fetched declared tree commit plus all four required path/blob matches.\n\nNone is a blocker for the backend-specific classification. No GPU work or cache/TLB mechanism is authorized.\n"""
    (out / "OPEN_ISSUES.md").write_text(open_issues, encoding="utf-8")
    sums = []
    for path in sorted(out.iterdir(), key=lambda p: p.name):
        if path.is_file() and path.name != "SHA256SUMS":
            sums.append(f"{sha256(path)}  {path.name}")
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority-root", type=Path, required=True)
    parser.add_argument("--source-repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    preflight = authority_preflight(args.authority_root)
    if preflight["status"] != "PASS":
        raise SystemExit(json.dumps(preflight, indent=2))
    source_identity, backend_rows = source_audit(args.source_repo)
    results = {}
    for name in ("S2", "S3"):
        print(json.dumps({"event": "scenario_start", "scenario": name}), flush=True)
        results[name] = analyze_scenario(name, args.authority_root)
        print(json.dumps({"event": "scenario_complete", "scenario": name, "full_scope": results[name]["full_scope"]}), flush=True)
    build(args.authority_root, args.out, preflight, results, source_identity, backend_rows)
    print(json.dumps({"event": "complete", "status": "PASS", "out": str(args.out)}), flush=True)


if __name__ == "__main__":
    main()
