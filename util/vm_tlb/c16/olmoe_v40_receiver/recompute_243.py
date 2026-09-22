#!/usr/bin/env python3
"""Independent CPU recompute for a destination-side OLMoE V40 bundle.

Only a selector TSV and raw per-shard evidence are read.  In particular, this
program never opens FORMAL_243_SUMMARY.json or FORMAL_243_ANALYSIS.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
from collections import Counter
from pathlib import Path
from typing import Any

from selector_canonical_v1 import SelectorError, canonicalize_tsv, write_new

HEADER = struct.Struct("<8sIIQQQ")
RECORD = struct.Struct("<6I32Q")
TERMINAL = re.compile(r"C16_WARP_TERMINAL static=(\d+) occurrence=(\d+) records=(\d+) overflow=(\d+)")
ACCOUNTING = re.compile(r"C16_P5_ACCOUNTING producer=(\d+) receiver=(\d+) serialized=(\d+) overflow=(\d+)")
SELECT = re.compile(r"C16_TARGET_OCCURRENCE observed=(\d+) action=SELECT")
SELECT_COUNT = re.compile(r"C16_TARGET_OCCURRENCE_COUNT selected=(\d+) observed=(\d+)")
EXPECTED_ANCHORS = {101, 103, 1085}
PAGE_SIZES = (128, 4096, 65536, 2 * 1024 * 1024)


class RecomputeError(ValueError):
    pass


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RecomputeError(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RecomputeError(f"JSON object required: {path}")
    return value


def require_file(path: Path) -> Path:
    if not path.is_file() or path.is_symlink():
        raise RecomputeError(f"missing/nonregular artifact: {path}")
    return path


def parse_ranges(path: Path) -> list[tuple[str, int, int]]:
    context = load_object(require_file(path))
    ranges = context.get("ranges")
    if not isinstance(ranges, list) or not ranges:
        raise RecomputeError("ADDRESS_CONTEXT has no ranges")
    parsed = []
    for item in ranges:
        if not isinstance(item, dict) or not isinstance(item.get("semantic_role"), str):
            raise RecomputeError("invalid ADDRESS_CONTEXT range")
        try:
            low = int(item["ptr"], 0) if isinstance(item.get("ptr"), str) else int(item["ptr"])
            size = int(item["bytes"])
        except (KeyError, TypeError, ValueError) as exc:
            raise RecomputeError("invalid ADDRESS_CONTEXT pointer/range") from exc
        if size <= 0:
            raise RecomputeError("nonpositive ADDRESS_CONTEXT range")
        parsed.append((item["semantic_role"], low, low + size))
    return parsed


def role_for(address: int, ranges: list[tuple[str, int, int]]) -> str:
    return next((role for role, low, high in ranges if low <= address < high), "OTHER")


def check_supervisor(receipt: dict[str, Any], static_index: int) -> tuple[str, str, str]:
    if receipt.get("selected_static") != static_index or receipt.get("occurrence") != 0:
        raise RecomputeError("supervisor selected static/occurrence mismatch")
    if receipt.get("phase") != "CLEAN_EXIT" or receipt.get("timed_out") is not False or receipt.get("returncode") != 0:
        raise RecomputeError("supervisor lifecycle is not CLEAN_EXIT")
    residual = receipt.get("residual_process_check")
    if not isinstance(residual, dict) or residual.get("no_target_residual_process") is not True:
        raise RecomputeError("supervisor lacks residual-process closure")
    values = (receipt.get("tool_sha256"), receipt.get("canonical_replay_sha256"), receipt.get("function_identity_sha256"))
    if not all(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) for value in values):
        raise RecomputeError("supervisor lacks tool/replay/function SHA closure")
    return values  # type: ignore[return-value]


def validate_shard(root: Path, static_index: int) -> dict[str, Any]:
    supervisor_path = require_file(root / "SUPERVISOR_RECEIPT.json")
    trace_path = require_file(root / "trace.bin")
    stdout_path = require_file(root / "stdout.log")
    context_path = require_file(root / "ADDRESS_CONTEXT.json")
    supervisor = load_object(supervisor_path)
    tool_sha, replay_sha, function_sha = check_supervisor(supervisor, static_index)
    if Path(str(supervisor.get("c16_output_path", ""))).name != trace_path.name:
        raise RecomputeError("supervisor trace path does not bind trace.bin")
    raw = trace_path.read_bytes()
    if len(raw) < HEADER.size or (len(raw) - HEADER.size) % RECORD.size:
        raise RecomputeError("C16WARP1 header/record alignment failure")
    magic, static, occurrence, callback, overflow, written = HEADER.unpack_from(raw)
    record_count = (len(raw) - HEADER.size) // RECORD.size
    if magic != b"C16WARP1" or static != static_index or occurrence != 0:
        raise RecomputeError("C16WARP1 header identity failure")
    if overflow != 0 or callback != written or written != record_count:
        raise RecomputeError("C16WARP1 header counter/overflow failure")
    stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
    terminals, accounting = TERMINAL.findall(stdout), ACCOUNTING.findall(stdout)
    if len(terminals) != 1 or len(accounting) != 1:
        raise RecomputeError("requires exactly one terminal and accounting record")
    if SELECT.findall(stdout) != ["0"] or SELECT_COUNT.findall(stdout) != [("0", "1")]:
        raise RecomputeError("exact occurrence proof failed")
    terminal = tuple(map(int, terminals[0]))
    closure = tuple(map(int, accounting[0]))
    if terminal != (static_index, 0, record_count, 0) or closure != (record_count, record_count, record_count, 0):
        raise RecomputeError("terminal/accounting closure failure")
    ranges = parse_ranges(context_path)
    roles: Counter[str] = Counter()
    unique = {size: set() for size in PAGE_SIZES}
    lanes = 0
    for offset in range(HEADER.size, len(raw), RECORD.size):
        record = RECORD.unpack_from(raw, offset)
        if record[0] != static_index:
            raise RecomputeError("per-record static identity failure")
        mask = record[1]
        for lane, address in enumerate(record[6:]):
            if mask >> lane & 1:
                lanes += 1
                roles[role_for(address, ranges)] += 1
                for size, values in unique.items():
                    values.add(address // size)
    return {
        "static_index": static_index,
        "classification": "EXECUTED" if record_count else "ZERO_EXECUTION_PROVEN",
        "record_count": record_count,
        "active_lane_events": lanes,
        "role_events": dict(sorted(roles.items())),
        "unique_128B_lines": len(unique[128]),
        "unique_4K_pages": len(unique[4096]),
        "unique_64K_pages": len(unique[65536]),
        "unique_2M_pages": len(unique[2 * 1024 * 1024]),
        "trace_sha256": hashlib.sha256(raw).hexdigest(),
        "address_context_sha256": hashlib.sha256(context_path.read_bytes()).hexdigest(),
        "tool_sha256": tool_sha,
        "canonical_replay_sha256": replay_sha,
        "function_identity_sha256": function_sha,
    }


def discover_shards(root: Path) -> dict[int, Path]:
    found: dict[int, Path] = {}
    for receipt_path in root.rglob("SUPERVISOR_RECEIPT.json"):
        if receipt_path.is_symlink():
            raise RecomputeError(f"symlink receipt rejected: {receipt_path}")
        receipt = load_object(receipt_path)
        index = receipt.get("selected_static")
        if not isinstance(index, int):
            raise RecomputeError(f"receipt lacks integer selected_static: {receipt_path}")
        if index in found:
            raise RecomputeError(f"multiple raw shards for selected static {index}")
        found[index] = receipt_path.parent
    return found


def recompute(selector_tsv: Path, shards_root: Path, all_statics_tsv: Path | None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    _, selector = canonicalize_tsv(selector_tsv)
    selected = set(selector["static_indices"])
    if len(selected) != 243 or EXPECTED_ANCHORS - selected:
        raise RecomputeError("selector must have 243 unique statics including typed anchors")
    if all_statics_tsv:
        _, domain = canonicalize_tsv(all_statics_tsv)
        if len(domain["static_indices"]) != 1096 or not selected <= set(domain["static_indices"]):
            raise RecomputeError("selected set is not within the 1096-static actual-A domain")
    found = discover_shards(shards_root)
    if set(found) != selected:
        raise RecomputeError(f"selector/shard membership differs missing={sorted(selected-set(found))} extra={sorted(set(found)-selected)}")
    rows, roles = [], Counter()
    sums = {"128B_lines": 0, "4K_pages": 0, "64K_pages": 0, "2M_pages": 0}
    tool_shas, replay_shas, function_shas = set(), set(), set()
    failures = []
    for static_index in sorted(selected):
        try:
            row = validate_shard(found[static_index], static_index)
        except RecomputeError as exc:
            failures.append({"static_index": static_index, "classification": "FAILED_EXCLUDED", "reason": str(exc)})
            continue
        rows.append(row)
        roles.update(row["role_events"])
        sums["128B_lines"] += row["unique_128B_lines"]
        sums["4K_pages"] += row["unique_4K_pages"]
        sums["64K_pages"] += row["unique_64K_pages"]
        sums["2M_pages"] += row["unique_2M_pages"]
        tool_shas.add(row["tool_sha256"]); replay_shas.add(row["canonical_replay_sha256"]); function_shas.add(row["function_identity_sha256"])
    rows.extend(failures)
    executed = sum(row["classification"] == "EXECUTED" for row in rows)
    zero = sum(row["classification"] == "ZERO_EXECUTION_PROVEN" for row in rows)
    failed = sum(row["classification"] == "FAILED_EXCLUDED" for row in rows)
    uniform = len(tool_shas) == len(replay_shas) == len(function_shas) == 1
    status = "PASS" if not failed and len(rows) == 243 and uniform else "FAIL"
    total_lanes = sum(roles.values())
    return {"schema_version": 1, "status": status, "evidence_condition": "actual-JIT variant A",
            "selector_raw_tsv_sha256": selector["raw_tsv_sha256"], "selector_canonical_v1_sha256": selector["canonical_sha256"],
            "total_selected": len(selected), "executed_count": executed, "zero_count": zero, "failed_excluded_count": failed,
            "dynamic_warp_records": sum(row.get("record_count", 0) for row in rows), "active_lane_events": total_lanes,
            "role_events": dict(sorted(roles.items())), "role_fractions": {key: value / total_lanes for key, value in sorted(roles.items())} if total_lanes else {},
            "SUM_OF_PER_SHARD_UNIQUES": sums, "uniform_tool_sha256": sorted(tool_shas), "uniform_replay_sha256": sorted(replay_shas),
            "uniform_function_identity_sha256": sorted(function_shas),
            "prohibited_analyses": ["cross-shard absolute VA union", "cross-shard global chronology", "cross-shard reuse distance", "fresh-process absolute VA comparison", "cache/TLB causality"]}, rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selector-tsv", type=Path, required=True)
    parser.add_argument("--shards-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--all-statics-tsv", type=Path)
    args = parser.parse_args()
    try:
        summary, rows = recompute(args.selector_tsv, args.shards_root, args.all_statics_tsv)
        if args.output_dir.exists():
            raise RecomputeError(f"output directory already exists: {args.output_dir}")
        args.output_dir.mkdir(parents=True)
        write_new(args.output_dir / "RECEIVER_243_SHARDS.jsonl", "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows).encode("utf-8"))
        write_new(args.output_dir / "RECEIVER_243_RECOMPUTE.json", (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        print(json.dumps({"status": summary["status"], "output_dir": str(args.output_dir)}, sort_keys=True))
        return 0 if summary["status"] == "PASS" else 2
    except (RecomputeError, SelectorError, OSError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
