#!/usr/bin/env python3
"""Synthetic regression for the observation-only transition-log analyzer."""

from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
ANALYZER = ROOT / "util/dtc_l1/analyze_fast64_3_2d_transition_diagnostic_v2.py"
GOOD = """\
FAST64_2D_TRANSITION cycle=1 event=TAG_ALLOC core=3 uid=7 addr=0x100 index=1 sector=0x1 write=0 status=MISS
FAST64_2D_TRANSITION cycle=1 event=OWNER_CREATE cache=L1D_003 uid=7 addr=0x120 index=1 sector=0x1 pending_before=0 pending_after=0 owners=1 missq=0 mshr_active=1 invalidate_pending=0
FAST64_2D_TRANSITION cycle=2 event=FILL_FINAL_PRE cache=L1D_003 uid=7 addr=0x120 index=1 sector=0x1 pending_before=0 pending_after=0 owners=1 missq=0 mshr_active=1 invalidate_pending=0
FAST64_2D_TRANSITION cycle=2 event=FILL_FINAL_POST cache=L1D_003 uid=7 addr=0x120 index=1 sector=0x1 pending_before=0 pending_after=0 owners=0 missq=0 mshr_active=0 invalidate_pending=0
FAST64_2D_TRANSITION cycle=3 event=INVALIDATE_REQUEST cache=L1D_003 uid=0 addr=0x0 index=4294967295 sector=0x0 pending_before=0 pending_after=0 owners=0 missq=0 mshr_active=0 invalidate_pending=0
FAST64_2D_TRANSITION cycle=3 event=INVALIDATE_ACTUAL cache=L1D_003 uid=0 addr=0x0 index=4294967295 sector=0x0 pending_before=0 pending_after=0 owners=0 missq=0 mshr_active=0 invalidate_pending=1
"""


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="fast64-3-2d-transition-v2-") as temporary:
        directory = pathlib.Path(temporary)
        good = directory / "good.stderr"
        result = directory / "result.json"
        good.write_text(GOOD, encoding="utf-8")
        subprocess.run([str(ANALYZER), "--transition-log", str(good), "--output", str(result)], check=True)
        parsed = json.loads(result.read_text(encoding="utf-8"))
        assert parsed["classification"] == "NONFORMAL_DIAGNOSTIC_NOT_RESULT"
        assert parsed["transition_event_count"] == 6
        assert parsed["active_owner_count_at_log_end"] == 0
        assert parsed["unmatched_fill_final_post_count"] == 0
        assert parsed["events_by_cache"]["L1D_003"]["OWNER_CREATE"] == 1
        bad = directory / "bad.stderr"
        bad.write_text("unrelated output\n", encoding="utf-8")
        failed = subprocess.run([str(ANALYZER), "--transition-log", str(bad), "--output", str(directory / "bad.json")])
        assert failed.returncode != 0
    print("FAST64_3_2D_TRANSITION_DIAGNOSTIC_V2_REGRESSION_PASS")


if __name__ == "__main__":
    main()
