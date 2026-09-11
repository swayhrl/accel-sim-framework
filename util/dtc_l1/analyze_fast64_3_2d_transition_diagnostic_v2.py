#!/usr/bin/env python3
"""Read-only, streaming analyzer for the Core-dc6062 2D transition diagnostic.

This diagnostic is intentionally observational.  It records the source-level
tag/owner/fill/invalidation transition stream emitted by the opt-in Core debug
build, without selecting a repair or creating a FAST64 result.
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys


PREFIX = "FAST64_2D_TRANSITION "
FIELDS = re.compile(r"([^= ]+)=([^ ]+)")
ALLOWED_EVENTS = {
    "TAG_ALLOC",
    "OWNER_CREATE",
    "FILL_FINAL_PRE",
    "FILL_FINAL_POST",
    "INVALIDATE_REQUEST",
    "INVALIDATE_ACTUAL",
}
CACHE_HEADER = re.compile(r"^Cache (?P<cache>[^:]+):$")
SET_HEADER = re.compile(r"^Cache (?P<cache>[^ ]+) set \d+ for addr=0x[0-9a-fA-F]+:$")
RESERVED = re.compile(r"^  way (?P<way>\d+): RESERVED tag=0x[0-9a-fA-F]+ block=0x(?P<block>[0-9a-fA-F]+)$")
OWNER_HEADER = re.compile(r"^Outstanding fill ownership \((?P<count>\d+) entries\):$")
OWNER = re.compile(
    r"^  root_mf=\S+ request_uid=(?P<uid>\d+) valid=(?P<valid>[01]) "
    r"block=0x(?P<block>[0-9a-fA-F]+) addr=0x(?P<addr>[0-9a-fA-F]+) "
    r"cache_index=(?P<index>\d+) data_size=(?P<size>\d+) pending_read=(?P<pending>\d+)$"
)
DEADLOCK_CORES = re.compile(r"^GPGPU-Sim uArch: DEADLOCK  (?P<cores>.+)$")
CORE_ENTRY = re.compile(r"(?P<core>\d+)\(\d+\)")


def cache_name_for_core(value: str) -> str:
    return f"L1D_{int(value):03d}"


def parse_terminal_dump(path: pathlib.Path) -> dict:
    """Mechanically capture the fatal snapshot, with no causal inference."""
    owners: dict[str, list[dict]] = {}
    reserved: dict[str, list[dict]] = {}
    current_cache: str | None = None
    in_owners_for: str | None = None
    deadlock_cores: list[int] = []
    owner_headers = 0
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = SET_HEADER.match(raw)
        if match:
            current_cache = match.group("cache")
            in_owners_for = None
            continue
        match = CACHE_HEADER.match(raw)
        if match:
            current_cache = match.group("cache")
            in_owners_for = None
            continue
        match = DEADLOCK_CORES.match(raw)
        if match:
            deadlock_cores = [int(item.group("core")) for item in CORE_ENTRY.finditer(match.group("cores"))]
            continue
        match = OWNER_HEADER.match(raw)
        if match and current_cache:
            owners[current_cache] = []
            in_owners_for = current_cache
            owner_headers += 1
            continue
        match = OWNER.match(raw)
        if match and in_owners_for:
            owners[in_owners_for].append({
                "request_uid": int(match.group("uid")),
                "valid": bool(int(match.group("valid"))),
                "block": "0x" + match.group("block").lower(),
                "address": "0x" + match.group("addr").lower(),
                "cache_index": int(match.group("index")),
                "data_size": int(match.group("size")),
                "pending_read": int(match.group("pending")),
            })
            continue
        match = RESERVED.match(raw)
        if match and current_cache:
            reserved.setdefault(current_cache, []).append({
                "way": int(match.group("way")),
                "block": "0x" + match.group("block").lower(),
            })
    if not deadlock_cores:
        return {"present": False, "deadlock_cores": [], "l1d": {}}
    if owner_headers == 0:
        raise ValueError("deadlock dump lacks Outstanding fill ownership state")
    l1d = {}
    for cache in sorted(set(owners) | set(reserved)):
        if not cache.startswith("L1D_"):
            continue
        by_block = {item["block"]: item for item in owners.get(cache, [])}
        l1d[cache] = {
            "owners": owners.get(cache, []),
            "reserved_lines": [
                {**line, "owner_state": "OWNER_PRESENT" if line["block"] in by_block else "OWNER_ABSENT", "owner": by_block.get(line["block"])}
                for line in reserved.get(cache, [])
            ],
        }
    return {"present": True, "deadlock_cores": deadlock_cores, "l1d": l1d}


def parse_transition_log(path: pathlib.Path, terminal: dict) -> dict:
    """Stream the debug trace; retain only auditable aggregates and endpoints."""
    counts: collections.Counter[str] = collections.Counter()
    per_cache: dict[str, collections.Counter[str]] = {}
    active_owners: dict[tuple[str, str], dict[str, str]] = {}
    unmatched_final_posts: list[dict[str, str]] = []
    unmatched_final_post_count = 0
    invalidation_actual_with_work: list[dict[str, str]] = []
    terminal_blocks = {
        (cache, line["block"])
        for cache, cache_state in terminal["l1d"].items()
        for line in cache_state["reserved_lines"]
    }
    terminal_transition_facts: dict[tuple[str, str], dict[str, object]] = {
        key: {"tag_alloc_count": 0, "tag_alloc_sample": [], "owner_create_count": 0,
              "owner_create_sample": [], "fill_final_post_count": 0,
              "fill_final_post_sample": []}
        for key in terminal_blocks
    }
    first_cycle: int | None = None
    last_cycle: int | None = None
    events = 0

    with path.open("r", encoding="utf-8", errors="replace") as stream:
        for raw in stream:
            if not raw.startswith(PREFIX):
                continue
            fields = dict(FIELDS.findall(raw[len(PREFIX):]))
            event = fields.get("event")
            if event not in ALLOWED_EVENTS:
                raise ValueError(f"unexpected transition event {event!r}")
            try:
                cycle = int(fields["cycle"])
            except (KeyError, ValueError) as error:
                raise ValueError(f"bad transition cycle: {raw.rstrip()}") from error
            if first_cycle is None:
                first_cycle = cycle
            last_cycle = cycle
            events += 1
            counts[event] += 1
            cache = fields.get("cache")
            if cache:
                per_cache.setdefault(cache, collections.Counter())[event] += 1

            if event == "OWNER_CREATE":
                if not cache or "uid" not in fields:
                    raise ValueError(f"owner-create lacks cache/uid: {raw.rstrip()}")
                key = (cache, fields["uid"])
                if key in active_owners:
                    raise ValueError(f"duplicate active owner {key}")
                active_owners[key] = fields
            elif event == "FILL_FINAL_POST":
                if not cache or "uid" not in fields:
                    raise ValueError(f"final-fill lacks cache/uid: {raw.rstrip()}")
                key = (cache, fields["uid"])
                if active_owners.pop(key, None) is None:
                    unmatched_final_post_count += 1
                    if len(unmatched_final_posts) < 32:
                        unmatched_final_posts.append(fields)
            elif event == "INVALIDATE_ACTUAL":
                # This is only a trace fact: the analyzer does not infer a
                # cause from an invalidate event or retry classification.
                if fields.get("owners") not in {None, "0"} or fields.get("mshr_active") not in {None, "0"}:
                    if len(invalidation_actual_with_work) < 32:
                        invalidation_actual_with_work.append(fields)

            cache_for_block = cache
            if event == "TAG_ALLOC":
                cache_for_block = cache_name_for_core(fields.get("core", ""))
            address = fields.get("addr")
            if cache_for_block and address:
                try:
                    block = f"0x{int(address, 16) & ~0x7f:x}"
                except ValueError as error:
                    raise ValueError(f"bad transition address: {raw.rstrip()}") from error
                facts = terminal_transition_facts.get((cache_for_block, block))
                if facts is not None:
                    key_name = {
                        "TAG_ALLOC": "tag_alloc",
                        "OWNER_CREATE": "owner_create",
                        "FILL_FINAL_POST": "fill_final_post",
                    }.get(event)
                    if key_name:
                        facts[f"{key_name}_count"] += 1
                        sample = facts[f"{key_name}_sample"]
                        if len(sample) < 16:
                            sample.append(fields)

    if events == 0:
        raise ValueError("no FAST64_2D_TRANSITION events found")
    for required in ("TAG_ALLOC", "OWNER_CREATE", "FILL_FINAL_POST"):
        if counts[required] == 0:
            raise ValueError(f"required transition event absent: {required}")

    return {
        "transition_event_count": events,
        "transition_cycle_first": first_cycle,
        "transition_cycle_last": last_cycle,
        "events_by_type": dict(sorted(counts.items())),
        "events_by_cache": {key: dict(sorted(value.items())) for key, value in sorted(per_cache.items())},
        "active_owner_count_at_log_end": len(active_owners),
        "active_owners_at_log_end_sample": [
            {"cache": cache, **fields}
            for (cache, _), fields in list(sorted(active_owners.items()))[:32]
        ],
        "unmatched_fill_final_post_count": unmatched_final_post_count,
        "unmatched_fill_final_post_sample": unmatched_final_posts,
        "invalidate_actual_with_owner_or_mshr_sample": invalidation_actual_with_work,
        "terminal_reserved_transition_facts": [
            {"cache": cache, "block": block, **facts}
            for (cache, block), facts in sorted(terminal_transition_facts.items())
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transition-log", type=pathlib.Path, required=True)
    parser.add_argument("--terminal-dump", type=pathlib.Path, required=True)
    parser.add_argument("--require-deadlock-snapshot", action="store_true")
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    for label, path in (("transition log", args.transition_log), ("terminal dump", args.terminal_dump)):
        if not path.is_file():
            raise SystemExit(f"{label} is not a regular file: {path}")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    terminal = parse_terminal_dump(args.terminal_dump)
    if args.require_deadlock_snapshot and not terminal["present"]:
        raise SystemExit("terminal exit 1 requires a parseable deadlock snapshot")
    result = {
        "schema": "FAST64_3_2DCONVOLUTION_BASE_TRANSITION_DIAGNOSTIC_V2",
        "classification": "NONFORMAL_DIAGNOSTIC_NOT_RESULT",
        "transition_log": str(args.transition_log),
        "terminal_dump": terminal,
        **parse_transition_log(args.transition_log, terminal),
        "interpretation": (
            "OBSERVATION_ONLY: transition ordering and owner-balance facts require "
            "source-backed follow-up; this file selects no functional repair and "
            "cannot promote a FAST64 result."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_name(args.output.name + ".tmp")
    if temp.exists():
        raise SystemExit(f"temporary output already exists: {temp}")
    temp.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(args.output)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(f"FAST64_3_2D_TRANSITION_ANALYZE_FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
