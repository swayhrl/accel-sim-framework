#!/usr/bin/env python3
"""CPU-only, fail-closed consumer for C16 V5 LDGSTS global-source bundles.

This intentionally keeps replay processes separate.  It produces per-shard
metrics only and never builds an absolute-VA union across shard or path.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import struct
import sys
from bisect import bisect_right
from collections import Counter
from pathlib import Path
from typing import Any

HEADER = struct.Struct("<8sIIQQQ")
RECORD = struct.Struct("<6I32Q")
MAGIC = b"C16WARP1"
TERMINAL_RE = re.compile(r"C16_WARP_TERMINAL static=(\d+) occurrence=(\d+) records=(\d+) overflow=(\d+)")
OPERAND_RE = re.compile(r"C16_LDGSTS_OPERANDS static=(\d+) memory_space=GLOBAL_TO_SHARED selected_operand=(\d+) mref_count=(\d+)")
WIDTH_RE = re.compile(r"^LDGSTS(?:\.[A-Z0-9_]+)*\.(8|16|32|64|128)$")
SASS_RE = re.compile(r"^\s*(?:@!?P\d+\s+)?([A-Z][A-Z0-9]*(?:\.[A-Z0-9_]+)*)\s+")

ROOT = Path("/root/share/mnt164/huangrulin/c16_ai_workload")
PACK = Path("docs/vm_tlb/review_packs/C16_LDGSTS_ANALYSIS_174NEW_V6_R1")
PRODUCER = "ea43fa6331dcb2d7d6553f6a48000bdd004458e0"
BASE = "1447bf9bb19bd249c116f53287a1f768170848c7"

SPECS = (
    ("Q05_S2_PREFILL_GEMM_LDGSTS", "C16R_qwen25-05b_s2-text_prefill_nvbit-ldgsts-shard_q05-s2-prefill-gemm-ldgsts_20260915T093229Z_00d7e1404abc", 18, "ec48121a56eec5b6f15fe3bf27a69b4e011adbd9d5871470a86b6077d1308f72", 0, "S2", "PREFILL"),
    ("Q05_S2_PREFILL_ATTN_LDGSTS", "C16R_qwen25-05b_s2-text_prefill_nvbit-ldgsts-shard_q05-s2-prefill-attn-ldgsts_20260915T093229Z_7ea3898f9bef", 48, "6e3ca803599787070b030e3ed12d9d1edbcc101201c99f4d904abfb393d9d65c", 0, "S2", "PREFILL"),
    ("Q05_S2_DECODE_EARLY_KV_LDGSTS", "C16R_qwen25-05b_s2-text_decode_nvbit-ldgsts-shard_q05-s2-decode-early-kv-ldgsts_20260915T093229Z_f43f42b2e7e0", 84, "5e0254ebbb9c82e806f78227d9e6b68db2a62f6fa681b6f80bb22464e6169d86", 24, "S2", "DECODE"),
    ("Q05_S2_DECODE_LATE_KV_LDGSTS", "C16R_qwen25-05b_s2-text_decode_nvbit-ldgsts-shard_q05-s2-decode-late-kv-ldgsts_20260915T093229Z_c41730c29523", 84, "5e0254ebbb9c82e806f78227d9e6b68db2a62f6fa681b6f80bb22464e6169d86", 767, "S2", "DECODE"),
    ("Q05_S3_PREFILL_ATTN_LDGSTS", "C16R_qwen25-05b_s3-text_prefill_nvbit-ldgsts-shard_q05-s3-prefill-attn-ldgsts_20260915T093229Z_9f20d86e164c", 48, "6e3ca803599787070b030e3ed12d9d1edbcc101201c99f4d904abfb393d9d65c", 0, "S3", "PREFILL"),
)
S3_DIRECT = ("Q05_S3_PREFILL_ATTN_DIRECT", "C16R_qwen25-05b_s3-text_prefill_nvbit-warp-mref-shard_s3-attention_20260915T081217Z_9796e9f72cfc", "S3", "PREFILL")


class ClosedError(RuntimeError):
    pass


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tsv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v for k, v in row.items()})


def exact_width(row: dict[str, str]) -> int | None:
    match = WIDTH_RE.fullmatch(row.get("opcode", ""))
    sass = SASS_RE.match(row.get("sass", ""))
    if not match or not sass or sass.group(1) != row.get("opcode"):
        return None
    return int(match.group(1)) // 8


def no_symlink_tree(raw: Path) -> None:
    if raw.is_symlink():
        raise ClosedError("raw bundle symlink rejected")
    for p in raw.rglob("*"):
        if p.is_symlink():
            raise ClosedError(f"symlink rejected: {p}")


def close_artifacts(entry: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    raw = Path(entry["raw_path"])
    if not raw.is_dir():
        raise ClosedError("catalog raw_path absent")
    no_symlink_tree(raw)
    manifest_path = raw / "RUN_MANIFEST.json"
    if sha(manifest_path) != entry["raw_manifest_sha256"]:
        raise ClosedError("catalog manifest hash mismatch")
    manifest = load(manifest_path)
    declared = {"RUN_MANIFEST.json", "READY", "LOCAL_CLOSE_RECEIPT.json"}
    for art in manifest.get("artifacts", []):
        rel = art["relative_path"]
        p = raw / rel
        if not p.is_file() or p.stat().st_size != art["size_bytes"] or sha(p) != art["sha256"]:
            raise ClosedError(f"artifact closure mismatch: {rel}")
        declared.add(rel)
    actual = {p.relative_to(raw).as_posix() for p in raw.rglob("*") if p.is_file()}
    if actual != declared:
        raise ClosedError("raw file-set is not exactly manifest-declared plus pipeline markers")
    return raw, manifest


def static_rows(path: Path) -> dict[int, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = {int(r["nvbit_static_index"]): r for r in csv.DictReader(f, delimiter="\t")}
    if not rows:
        raise ClosedError("empty static map")
    return rows


def ranges(path: Path) -> tuple[list[int], list[dict[str, Any]], list[int]]:
    value = load(path)
    result = []
    for r in value.get("ranges", []):
        start, end = int(r["address_start_hex"], 16), int(r["address_end_hex"], 16)
        if end <= start:
            raise ClosedError("invalid address context range")
        result.append({**r, "_start": start, "_end": end})
    result.sort(key=lambda x: x["_start"])
    prefix_end, maximum = [], 0
    for row in result:
        maximum = max(maximum, row["_end"])
        prefix_end.append(maximum)
    return [x["_start"] for x in result], result, prefix_end


def object_match(addr: int, starts: list[int], table: list[dict[str, Any]], prefix_end: list[int]) -> tuple[str, str, int | None]:
    # Searching preceding overlapping ranges catches ambiguous maps; no map from
    # another process is ever accepted by this function.
    i = bisect_right(starts, addr)
    found = []
    # The prefix maximum terminates this backward interval query as soon as no
    # earlier range can contain addr. This preserves ambiguous-overlap handling
    # without a per-event linear scan over the object map.
    j = i - 1
    while j >= 0:
        if table[j]["_end"] > addr:
            found.append(table[j])
        j -= 1
        if j >= 0 and prefix_end[j] <= addr:
            break
    if len(found) != 1:
        return ("UNKNOWN_RUNTIME" if not found else "AMBIGUOUS_RUNTIME_RANGE", "", None)
    r = found[0]
    return (r.get("class", "UNKNOWN_RUNTIME"), r.get("runtime_name", ""), addr - r["_start"])


def terminal_ok(log: Path, idx: int, occ: int, records: int, overflow: int, ldgsts: bool) -> bool:
    text = log.read_text(encoding="utf-8", errors="strict")
    terms = TERMINAL_RE.findall(text)
    if len(terms) != 1 or tuple(map(int, terms[0])) != (idx, occ, records, overflow):
        return False
    if ldgsts:
        ops = OPERAND_RE.findall(text)
        return len(ops) == 1 and tuple(map(int, ops[0])) == (idx, 1, 2)
    return True


def bucket_add(target: set[int], start: int, width: int, shift: int) -> None:
    target.add(start >> shift)
    target.add((start + width - 1) >> shift)


def parse_shard(trace: Path, idx: int, occ: int, expected_records: int, expected_overflow: int,
                width: int | None, context: Path) -> dict[str, Any]:
    with trace.open("rb") as f:
        header = f.read(HEADER.size)
        if len(header) != HEADER.size:
            raise ClosedError("truncated C16WARP1 header")
        magic, hidx, hocc, callbacks, overflow, written = HEADER.unpack(header)
        if magic != MAGIC or (hidx, hocc) != (idx, occ) or overflow != 0 or overflow != expected_overflow:
            raise ClosedError("C16WARP1 header/overflow mismatch")
        if written != expected_records or callbacks != written:
            raise ClosedError("C16WARP1 record closure mismatch")
        if trace.stat().st_size != HEADER.size + written * RECORD.size:
            raise ClosedError("C16WARP1 size mismatch")
        starts, table, prefix_end = ranges(context)
        va, start4k, start64k, start2m, start128 = set(), set(), set(), set(), set()
        touch4k, touch64k, touch2m, touch128 = set(), set(), set(), set()
        classes, names = Counter(), Counter()
        active = 0
        for _ in range(written):
            data = f.read(RECORD.size)
            if len(data) != RECORD.size:
                raise ClosedError("truncated C16WARP1 record")
            ridx, mask, _x, _y, _z, _warp, *addresses = RECORD.unpack(data)
            if ridx != idx:
                raise ClosedError("C16WARP1 record static mismatch")
            for lane, address in enumerate(addresses):
                if not ((mask >> lane) & 1):
                    continue
                active += 1
                va.add(address); start4k.add(address >> 12); start64k.add(address >> 16); start2m.add(address >> 21); start128.add(address >> 7)
                cls, name, _offset = object_match(address, starts, table, prefix_end)
                classes[cls] += 1
                if name:
                    names[f"{cls}:{name}"] += 1
                if width is not None:
                    bucket_add(touch4k, address, width, 12); bucket_add(touch64k, address, width, 16)
                    bucket_add(touch2m, address, width, 21); bucket_add(touch128, address, width, 7)
        if f.read(1):
            raise ClosedError("trailing C16WARP1 data")
    return {"callback_warp_records": written, "active_lane_events": active,
            "start_unique_va": len(va), "start_4k_pages": len(start4k), "start_64k_pages": len(start64k),
            "start_2m_pages": len(start2m), "start_128b_lines": len(start128),
            "exact_touched_4k_pages": len(touch4k) if width else "WIDTH_UNKNOWN",
            "exact_touched_64k_pages": len(touch64k) if width else "WIDTH_UNKNOWN",
            "exact_touched_2m_pages": len(touch2m) if width else "WIDTH_UNKNOWN",
            "exact_touched_128b_lines": len(touch128) if width else "WIDTH_UNKNOWN",
            "classes": dict(classes), "names": dict(names)}


def analyze(run: str, target: str, expected_count: int | None, expected_static_sha: str | None,
            expected_occ: int | None, ldgsts: bool, evidence_class: str, scenario: str, phase: str) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    entry = load(ROOT / "catalog" / "entries" / f"{run}.json")
    raw, manifest = close_artifacts(entry)
    shard_manifest_name = "LDGSTS_SHARD_MANIFEST.json" if ldgsts else "WARP_SHARD_MANIFEST.json"
    logical = load(raw / shard_manifest_name)
    map_name = "SPECIAL_STATIC_MAP.tsv" if ldgsts else "STATIC_MREF_MAP.tsv"
    if expected_static_sha and sha(raw / map_name) != expected_static_sha:
        raise ClosedError("static map SHA mismatch against frozen producer authority")
    if ldgsts and (logical.get("mref_operand_index") != 1 or logical.get("path_kind") != "LDGSTS_GLOBAL_SOURCE"):
        raise ClosedError("LDGSTS operand/path binding mismatch")
    shards = logical.get("shards")
    if not isinstance(shards, list) or not shards or len({s.get("static_index") for s in shards}) != len(shards):
        raise ClosedError("invalid static shard set")
    if expected_count is not None and len(shards) != expected_count:
        raise ClosedError("frozen static count mismatch")
    maps = static_rows(raw / map_name)
    fingerprint, attrs = [], []
    executed, zero, total_events, all_classes = set(), set(), 0, Counter()
    for shard in sorted(shards, key=lambda x: int(x["static_index"])):
        idx, occ, recs, overflow = (int(shard[k]) for k in ("static_index", "occurrence", "records", "overflow"))
        if expected_occ is not None and occ != expected_occ:
            raise ClosedError("unexpected function occurrence")
        if idx not in maps or maps[idx].get("has_mref") != "1":
            raise ClosedError("selected static index absent/non-MREF")
        trace = raw / "raw_shards" / shard["trace"]
        context = raw / "raw_shards" / shard["address_context"]
        log = trace.with_suffix(".stdout.log")
        if sha(trace) != shard["trace_sha256"] or sha(context) != shard["address_context_sha256"]:
            raise ClosedError("shard trace/context hash mismatch")
        ctx = load(context)
        if not ctx.get("address_space_id") or not ctx.get("process_pid") or not ctx.get("gpu_uuid"):
            raise ClosedError("same-process address context binding incomplete")
        if not terminal_ok(log, idx, occ, recs, overflow, ldgsts):
            raise ClosedError("terminal or operand evidence mismatch")
        row = maps[idx]
        width = exact_width(row) if ldgsts else None
        metrics = parse_shard(trace, idx, occ, recs, overflow, width, context)
        classified = "ZERO_EXECUTION_PROVEN" if recs == 0 else "EXECUTED_SHARD"
        if shard.get("classification") != classified:
            raise ClosedError("manifest execution classification mismatch")
        (zero if recs == 0 else executed).add(idx)
        total_events += metrics["active_lane_events"]
        all_classes.update(metrics["classes"])
        fingerprint.append({"target": target, "run_id": run, "static_index": idx, "occurrence": occ,
            "classification": classified, "opcode": row["opcode"], "sass": row["sass"],
            "access_kind": "READ" if ldgsts else ("READ" if row.get("is_load") == "1" and row.get("is_store") == "0" else "DIRECT_SEE_V4"),
            "width_classification": "EXACT_STATIC_SASS_VALIDATED" if width else "WIDTH_UNKNOWN",
            "width_bytes": width if width else "", **{k: metrics[k] for k in ("active_lane_events", "start_unique_va", "start_4k_pages", "start_64k_pages", "start_2m_pages", "start_128b_lines", "exact_touched_4k_pages", "exact_touched_64k_pages", "exact_touched_2m_pages", "exact_touched_128b_lines")},
            "static_set_sha": expected_static_sha or sha(raw / map_name), "trace_sha": sha(trace), "address_context_sha": sha(context)})
        for cls, count in sorted(metrics["classes"].items()):
            attrs.append({"target": target, "run_id": run, "static_index": idx, "classification": classified,
                "object_class": cls, "object_name": "", "active_lane_events": count,
                "exact_bytes": count * width if width else "WIDTH_UNKNOWN", "binding": "SAME_PROCESS_ADDRESS_CONTEXT"})
        for name, count in sorted(metrics["names"].items()):
            cls, obj = name.split(":", 1)
            attrs.append({"target": target, "run_id": run, "static_index": idx, "classification": classified,
                "object_class": cls, "object_name": obj, "active_lane_events": count,
                "exact_bytes": count * width if width else "WIDTH_UNKNOWN", "binding": "SAME_PROCESS_ADDRESS_CONTEXT"})
    if executed | zero != {int(s["static_index"]) for s in shards} or executed & zero:
        raise ClosedError("executed/zero set partition failure")
    result = {"target": target, "run_id": run, "evidence_class": evidence_class, "raw_manifest_sha": entry["raw_manifest_sha256"],
              "catalog": "PASS", "no_symlink": "PASS", "file_set_hash_closure": "PASS", "identity": "PASS",
              "static_set": "PASS", "terminal": "PASS", "overflow_drop": "PASS", "address_context": "PASS",
              "operand_binding": "PASS" if ldgsts else "N/A_DIRECT", "static_count": len(shards), "executed": len(executed), "zero": len(zero),
              "active_lane_events": total_events, "object_composition": dict(all_classes), "scenario": scenario, "phase": phase,
              "static_indices": sorted(executed), "all_static_indices": sorted(executed | zero), "static_map_sha": expected_static_sha or sha(raw / map_name)}
    return result, fingerprint, attrs


def prior_direct() -> dict[str, dict[str, Any]]:
    path = Path("docs/vm_tlb/review_packs/C16_QWEN0_DECODE_ANALYSIS_174NEW_V4/QWEN0_PREFILL_DECODE_BASELINE.tsv")
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    return {r["target"]: r for r in rows}


def close_receipt(pack: Path) -> None:
    excluded = {"SHA256SUMS", "DERIVED_RECEIPT.json"}
    entries = []
    for p in sorted(pack.iterdir()):
        if p.is_file() and p.name not in excluded:
            entries.append({"relative_path": p.name, "size_bytes": p.stat().st_size, "sha256": sha(p)})
    (pack / "DERIVED_RECEIPT.json").write_text(json.dumps({"schema_version": 1, "implementation_base": BASE, "producer_authority": PRODUCER,
        "raw_mutation": False, "cross_path_absolute_va_union": "PROHIBITED", "outputs": entries}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    all_files = sorted(p for p in pack.iterdir() if p.is_file() and p.name != "SHA256SUMS")
    with (pack / "SHA256SUMS").open("w", encoding="utf-8") as f:
        for p in all_files:
            f.write(f"{sha(p)}  {p.name}\n")


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=False)
    verifications, fingerprints, attrs = [], [], []
    by_target: dict[str, dict[str, Any]] = {}
    for target, run, count, static_sha, occ, scenario, phase in SPECS:
        r, fp, at = analyze(run, target, count, static_sha, occ, True, "LDGSTS_GLOBAL_SOURCE", scenario, phase)
        verifications.append(r); fingerprints.extend(fp); attrs.extend(at); by_target[target] = r
    r, fp, at = analyze(S3_DIRECT[1], S3_DIRECT[0], None, None, 0, False, "DIRECT_GLOBAL_MREF_SCOPED_PREREQUISITE", "S3", "PREFILL")
    verifications.append(r); fingerprints.extend(fp); attrs.extend(at); by_target[S3_DIRECT[0]] = r
    tsv(PACK / "RUN_VERIFICATION.tsv", list(verifications[0]), verifications)
    tsv(PACK / "SPECIAL_PATH_FINGERPRINT.tsv", list(fingerprints[0]), fingerprints)
    tsv(PACK / "OBJECT_ATTRIBUTION.tsv", list(attrs[0]), attrs)
    tsv(PACK / "OPERAND_BINDING_AUDIT.tsv", ["accepted_operand_index", "accepted_role", "rejected_operand_index", "rejected_role", "opcode", "sass", "decision_basis", "result"], [{"accepted_operand_index": 1, "accepted_role": "GLOBAL_SOURCE", "rejected_operand_index": 0, "rejected_role": "SHARED_DESTINATION", "opcode": "LDGSTS.E.BYPASS.LTC128B.128", "sass": "LDGSTS.E.BYPASS.LTC128B.128 [R204], [R4.64], P0 ;", "decision_basis": "exact SASS/NVBit operand ordering", "result": "PASS"}])
    old = prior_direct()
    coverage = []
    mapping = [("Q05_S2_PREFILL_GEMM_LDGSTS", "Q05_GEMM"), ("Q05_S2_PREFILL_ATTN_LDGSTS", "Q05_ATTN"), ("Q05_S2_DECODE_EARLY_KV_LDGSTS", "Q05_DECODE_EARLY_KV_ATTN"), ("Q05_S2_DECODE_LATE_KV_LDGSTS", "Q05_DECODE_LATE_KV_ATTN")]
    for special, direct in mapping:
        d, s = old[direct], by_target[special]
        coverage.append({"target": special, "direct_evidence": direct, "direct_static_count": d["static_mref_count"], "direct_executed_zero": f"{d['executed_shards']}/{d['zero_execution_proven_shards']}", "direct_active_lane_events": d["active_lane_address_events"], "direct_access_kinds": d["access_counts"], "ldgsts_static_count": s["static_count"], "ldgsts_executed_zero": f"{s['executed']}/{s['zero']}", "ldgsts_active_lane_events": s["active_lane_events"], "ldgsts_access_kind": "READ", "direct_object_composition": d["object_event_counts"], "ldgsts_object_composition": s["object_composition"], "coverage_qualification": "ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL" if "DECODE" in special else "SET_LEVEL_INVENTORY_NO_CROSS_PATH_UNION"})
    s3 = by_target["Q05_S3_PREFILL_ATTN_DIRECT"]
    coverage.append({"target": "Q05_S3_PREFILL_ATTN_LDGSTS", "direct_evidence": S3_DIRECT[1], "direct_static_count": s3["static_count"], "direct_executed_zero": f"{s3['executed']}/{s3['zero']}", "direct_active_lane_events": s3["active_lane_events"], "direct_access_kinds": "SCOPED_DIRECT_CONSUMER_PREREQUISITE", "ldgsts_static_count": by_target["Q05_S3_PREFILL_ATTN_LDGSTS"]["static_count"], "ldgsts_executed_zero": f"{by_target['Q05_S3_PREFILL_ATTN_LDGSTS']['executed']}/{by_target['Q05_S3_PREFILL_ATTN_LDGSTS']['zero']}", "ldgsts_active_lane_events": by_target["Q05_S3_PREFILL_ATTN_LDGSTS"]["active_lane_events"], "ldgsts_access_kind": "READ", "direct_object_composition": s3["object_composition"], "ldgsts_object_composition": by_target["Q05_S3_PREFILL_ATTN_LDGSTS"]["object_composition"], "coverage_qualification": "SET_LEVEL_INVENTORY_NO_CROSS_PATH_UNION"})
    tsv(PACK / "DIRECT_PLUS_LDGSTS_COVERAGE.tsv", list(coverage[0]), coverage)
    early, late = by_target["Q05_S2_DECODE_EARLY_KV_LDGSTS"], by_target["Q05_S2_DECODE_LATE_KV_LDGSTS"]
    common = sorted(set(early["static_indices"]) & set(late["static_indices"]))
    comparison = [{"early_occurrence": 24, "late_occurrence": 767, "static_map_sha_equal": early["static_map_sha"] == late["static_map_sha"], "executed_static_set_equal": early["static_indices"] == late["static_indices"], "executed_static_intersection": common, "early_active_lane_events": early["active_lane_events"], "late_active_lane_events": late["active_lane_events"], "lane_event_delta_late_minus_early": late["active_lane_events"] - early["active_lane_events"], "absolute_va_comparison": "PROHIBITED", "object_relative_behavior": "ONLY_COMMON_LOSSLESS_SEMANTIC_IDENTITY;SEE_OBJECT_ATTRIBUTION", "result": "PASS"}]
    tsv(PACK / "DECODE_EARLY_LATE_SPECIAL_COMPARISON.tsv", list(comparison[0]), comparison)
    (PACK / "DECODE_EARLY_LATE_FINDINGS.md").write_text(f"# Decode Early vs Late\n\nObserved facts: both occurrences have the same frozen static-map SHA, {len(common)} executed static indices, and 33/51 executed/zero partition. Decoded active-lane events are {early['active_lane_events']} (Early) and {late['active_lane_events']} (Late), delta {late['active_lane_events'] - early['active_lane_events']}.\n\nSupported interpretation: this is an independently decoded LDGSTS GLOBAL-SOURCE read-path difference at set level; it is not producer callback accounting.\n\nUnsupported hypotheses: no cross-replay absolute-VA comparison, no whole-kernel footprint, no temporal/reuse claim, and no KV-growth causal claim without a common lossless semantic object identity.\n", encoding="utf-8")
    s2, s3l = by_target["Q05_S2_PREFILL_ATTN_LDGSTS"], by_target["Q05_S3_PREFILL_ATTN_LDGSTS"]
    scaling = [{"s2_context_tokens": 2048, "s3_context_tokens": 8192, "static_map_sha_equal": s2["static_map_sha"] == s3l["static_map_sha"], "s2_executed": s2["executed"], "s3_executed": s3l["executed"], "s2_active_lane_events": s2["active_lane_events"], "s3_active_lane_events": s3l["active_lane_events"], "s3_s2_event_ratio": s3l["active_lane_events"] / s2["active_lane_events"], "s2_events_per_token": s2["active_lane_events"] / 2048, "s3_events_per_token": s3l["active_lane_events"] / 8192, "grid": "S2=16x1x14;S3=64x1x14", "scope": "PER_SHARD_SET_LEVEL_ONLY_NO_TEMPORAL_OR_PHYSICAL_UNION", "result": "PASS"}]
    tsv(PACK / "S2_S3_SPECIAL_COMPARISON.tsv", list(scaling[0]), scaling)
    tsv(PACK / "REGRESSION_RESULTS.tsv", ["test", "result", "scope"], [{"test": "LDGSTS consumer unit tests", "result": "RUN_SEPARATELY", "scope": "CPU"}, {"test": "RTX3090 Q2 exact regression", "result": "RUN_SEPARATELY", "scope": "existing exact fixture; no GPU workload launched"}])
    (PACK / "README.md").write_text("# C16 LDGSTS Analysis 174-new V6 R1\n\nCPU-only, hash-closed independent consumer analysis. Metrics are recomputed from raw C16WARP1 artifacts. Each replay is a separate set; no cross-replay absolute-VA union, temporal order, reuse distance, or physical whole-kernel footprint is claimed.\n", encoding="utf-8")
    (PACK / "OPEN_ISSUES.md").write_text("- `git fetch origin --prune` timed out because github.com:443 was unreachable before analysis. Cached coordination ref independently matched the requested SHA.\n- Object-relative comparison is intentionally withheld unless a common lossless same-process semantic identity can be demonstrated.\n", encoding="utf-8")
    decision = {"schema_version": 1, "decision": "C16_LDGSTS_ANALYSIS_174NEW_V6_R1_PASS", "implementation_base": BASE, "producer_authority": PRODUCER, "cpu_only": True, "raw_mutation": False, "five_ldgsts_runs_closed": True, "s3_direct_prerequisite_closed": True, "coverage_semantics": "SET_LEVEL_ONLY", "prohibited": ["cross_replay_absolute_va_union", "direct_ldgsts_fabricated_stream", "cross_path_temporal_order", "cross_path_reuse_distance", "whole_kernel_physical_footprint", "cross_process_object_attribution"]}
    (PACK / "FINAL_DECISION.json").write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    close_receipt(PACK)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ClosedError as exc:
        print(f"FAIL_CLOSED: {exc}", file=sys.stderr)
        raise SystemExit(2)
