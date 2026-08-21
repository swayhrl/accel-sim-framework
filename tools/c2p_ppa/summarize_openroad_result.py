#!/usr/bin/env python3
"""Emit a small, comparable summary from one C2P OpenROAD result directory."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def last_match(path: Path, pattern: str) -> str | None:
    if not path.exists():
        return None
    matches = re.findall(pattern, path.read_text(errors="replace"), re.MULTILINE)
    return matches[-1] if matches else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dir", type=Path)
    args = parser.parse_args()
    root = args.result_dir
    if not root.is_dir():
        parser.error(f"not a result directory: {root}")

    log = root / "openroad.log"
    post_cts = root / "post_cts_timing.rpt"
    post_route = root / "post_route_timing.rpt"
    post_route_area = root / "post_route_area.rpt"
    drc = root / "drc.rpt"

    version = last_match(log, r"^(OpenROAD .+)$") or "not recorded"
    pre_cts_slack = last_match(post_cts, r"^\s*(-?\d+(?:\.\d+)?)\s+slack \(")
    post_route_slack = last_match(
        post_route, r"^\s*(-?\d+(?:\.\d+)?)\s+slack \("
    )
    area = last_match(post_route_area, r"^Design area\s+(\d+(?:\.\d+)?)")
    if area is None:
        area = last_match(root / "pre_cts_area.rpt", r"^Design area\s+(\d+(?:\.\d+)?)")
    drc_count = 0
    if drc.exists():
        drc_count = len(re.findall(r"^violation type:", drc.read_text(errors="replace"), re.MULTILINE))

    print(f"result_dir: {root}")
    print(f"openroad: {version}")
    print(f"post_cts_slack_ps: {pre_cts_slack or 'not available'}")
    print(f"post_route_slack_ps: {post_route_slack or 'not available'}")
    print(f"post_route_design_area_um2: {area or 'not available'}")
    print(f"drc_entries: {drc_count if drc.exists() else 'not available'}")


if __name__ == "__main__":
    main()
