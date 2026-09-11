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


def parse_transition_log(path: pathlib.Path) -> dict:
    """Stream the debug trace; retain only auditable aggregates and endpoints."""
    counts: collections.Counter[str] = collections.Counter()
    per_cache: dict[str, collections.Counter[str]] = {}
    active_owners: dict[tuple[str, str], dict[str, str]] = {}
    unmatched_final_posts: list[dict[str, str]] = []
    unmatched_final_post_count = 0
    invalidation_actual_with_work: list[dict[str, str]] = []
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
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transition-log", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    if not args.transition_log.is_file():
        raise SystemExit(f"transition log is not a regular file: {args.transition_log}")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    result = {
        "schema": "FAST64_3_2DCONVOLUTION_BASE_TRANSITION_DIAGNOSTIC_V2",
        "classification": "NONFORMAL_DIAGNOSTIC_NOT_RESULT",
        "transition_log": str(args.transition_log),
        **parse_transition_log(args.transition_log),
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
