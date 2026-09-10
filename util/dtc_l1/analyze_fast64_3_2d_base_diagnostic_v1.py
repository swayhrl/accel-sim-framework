#!/usr/bin/env python3
"""Read-only analyzer for the future 2DConvolution/Base ownership diagnostic.

This intentionally does not determine a functional repair.  It mechanically
relates reserved conventional-L1 lines to the baseline-cache root fill owners
printed by the observational diagnostic Core, so a later root-cause decision is
based on the terminal dump rather than manual log transcription.
"""

import argparse
import json
import pathlib
import re
import sys


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


def parse(path: pathlib.Path) -> dict:
    owners = {}
    reserved = {}
    current_cache = None
    in_owners_for = None
    deadlock_cores = []
    owner_headers = 0

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        # A retry diagnostic starts with "Cache L1D_xxx set ..." and also has
        # a trailing colon. Match that more-specific form first.
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
            in_owners_for = current_cache
            owners[in_owners_for] = []
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

    if owner_headers == 0:
        raise ValueError("no observational 'Outstanding fill ownership' dump found")

    caches = {}
    for cache in sorted(set(owners) | set(reserved)):
        if not cache.startswith("L1D_"):
            continue
        owner_by_block = {entry["block"]: entry for entry in owners.get(cache, [])}
        lines = []
        for line in reserved.get(cache, []):
            owner = owner_by_block.get(line["block"])
            lines.append({
                **line,
                "owner_state": "OWNER_PRESENT" if owner else "OWNER_ABSENT",
                "owner": owner,
            })
        caches[cache] = {
            "reserved_lines": lines,
            "owners": owners.get(cache, []),
            "owners_with_pending_children": [entry for entry in owners.get(cache, []) if entry["pending_read"] > 0],
        }

    return {
        "schema": "FAST64_3_2DCONVOLUTION_BASE_DIAGNOSTIC_V1",
        "classification": "NONFORMAL_DIAGNOSTIC_NOT_RESULT",
        "input": str(path),
        "deadlock_cores": deadlock_cores,
        "l1d": caches,
        "interpretation": "OBSERVATION_ONLY: owner presence and pending child counts require source-backed follow-up; this file does not select a repair or promote a FAST64 result.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    if not args.input.is_file():
        raise SystemExit(f"input is not a regular file: {args.input}")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    result = parse(args.input)
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
        print(f"FAST64_3_2D_DIAGNOSTIC_ANALYZE_FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
