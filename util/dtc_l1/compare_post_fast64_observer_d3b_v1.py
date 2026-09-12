#!/usr/bin/env python3
"""D3B comparator: extend exact observer equivalence to cycle integrals."""

from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import compare_post_fast64_observer_qual_v1 as qualified  # noqa: E402


qualified.NEW_OBSERVER = re.compile(
    r"^DTC_L1_(?:oo_duplicate_after_eviction|(?:io|oo)_alloc_to_ready_"
    r"(?:count|sum_cycles|max_cycles)|(?:io|oo)_pending_tag_evictions|"
    r"io_pending_eviction_to_response_(?:count|sum_cycles|max_cycles)|"
    r"oo_deferred_tag_eviction_to_final_reclaim_"
    r"(?:count|sum_cycles|max_cycles)|(?:io|oo)_(?:observer_sample_sm_cycles|"
    r"physical_allocated_line_cycles|physical_full_sm_cycles|"
    r"inflight_request_cycles|observer_live_records))$"
)


if __name__ == "__main__":
    raise SystemExit(qualified.main())
