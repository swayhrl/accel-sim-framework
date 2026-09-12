#!/usr/bin/env python3
"""D3B collector: retain the original D3 contract plus occupancy integrals."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import collect_post_fast64_observer_qual_v1 as qualified  # noqa: E402


def observed_keys(mode: str) -> tuple[str, ...]:
    if mode == "IO":
        return (
            "DTC_L1_io_alloc_to_ready_count",
            "DTC_L1_io_alloc_to_ready_sum_cycles",
            "DTC_L1_io_alloc_to_ready_max_cycles",
            "DTC_L1_io_pending_tag_evictions",
            "DTC_L1_io_pending_eviction_to_response_count",
            "DTC_L1_io_pending_eviction_to_response_sum_cycles",
            "DTC_L1_io_pending_eviction_to_response_max_cycles",
            "DTC_L1_io_observer_sample_sm_cycles",
            "DTC_L1_io_physical_allocated_line_cycles",
            "DTC_L1_io_physical_full_sm_cycles",
            "DTC_L1_io_inflight_request_cycles",
            "DTC_L1_io_observer_live_records",
        )
    if mode == "OO":
        return (
            "DTC_L1_oo_duplicate_after_eviction",
            "DTC_L1_oo_alloc_to_ready_count",
            "DTC_L1_oo_alloc_to_ready_sum_cycles",
            "DTC_L1_oo_alloc_to_ready_max_cycles",
            "DTC_L1_oo_pending_tag_evictions",
            "DTC_L1_oo_deferred_tag_eviction_to_final_reclaim_count",
            "DTC_L1_oo_deferred_tag_eviction_to_final_reclaim_sum_cycles",
            "DTC_L1_oo_deferred_tag_eviction_to_final_reclaim_max_cycles",
            "DTC_L1_oo_observer_sample_sm_cycles",
            "DTC_L1_oo_physical_allocated_line_cycles",
            "DTC_L1_oo_physical_full_sm_cycles",
            "DTC_L1_oo_inflight_request_cycles",
            "DTC_L1_oo_observer_live_records",
        )
    raise ValueError(f"unsupported observer mode {mode!r}")


qualified.SCHEMA = "POST_FAST64_OBSERVER_D3B_V1"
qualified.observed_keys = observed_keys


if __name__ == "__main__":
    raise SystemExit(qualified.main())
