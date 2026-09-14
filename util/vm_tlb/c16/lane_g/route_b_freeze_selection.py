#!/usr/bin/env python3
"""Freeze Route-B selection from immutable V2 requests and active map evidence."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from route_b_selection import freeze_final_selection_v2, normalize_active_map_results_v2


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=Path, required=True)
    parser.add_argument("--active-map-results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    request_bytes = arguments.requests.read_bytes()
    requests = json.loads(request_bytes)
    active = json.loads(arguments.active_map_results.read_text(encoding="utf-8"))
    expected_request_sha = active.get("source_authority", {}).get("request_manifest_sha256")
    if expected_request_sha != sha256(request_bytes).hexdigest():
        raise ValueError("request document SHA does not match active map-results source authority")
    selection = freeze_final_selection_v2(requests, normalize_active_map_results_v2(active))
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(selection, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
