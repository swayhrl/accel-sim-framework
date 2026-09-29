#!/usr/bin/env python3
"""Fail-closed source-placement checks for the R101R3 S1 implementation."""

from pathlib import Path


ROOT = Path("/root/awma_r101r3_bounded_service_handoff_174_v1_runtime/src/gpgpu-sim")
FILES = {
    "l2": (ROOT / "src/gpgpu-sim/l2cache.cc").read_text(),
    "cache": (ROOT / "src/gpgpu-sim/gpu-cache.cc").read_text(),
    "cache_h": (ROOT / "src/gpgpu-sim/gpu-cache.h").read_text(),
    "shader": (ROOT / "src/gpgpu-sim/shader.cc").read_text(),
    "policy": (ROOT / "src/gpgpu-sim/awma_transient_l2_policy.h").read_text(),
    "access": (ROOT / "src/abstract_hardware_model.h").read_text(),
}
checks = {
    "opt_in_selector": 'getenv("AWMA_R101R3_SERVICE_MODE")' in FILES["cache"],
    "default_none": "SERVICE_MODE_NONE" in FILES["cache"],
    "separate_diagnostics": 'getenv("AWMA_R101R3_DIAGNOSTICS")' in FILES["cache"],
    "post_l1_partition_hook":
        "S1 observes only the normal post-L1/post-request-ICNT partition head"
        in FILES["l2"],
    "normal_request_icnt_queue": "m_icnt_L2_queue->top()" in FILES["l2"],
    "existing_data_port": "m_bandwidth_management.use_data_port(mf, HIT, events)"
        in FILES["cache"],
    "existing_return_queue": "m_L2_icnt_queue->push(mf)" in FILES["l2"],
    "normal_fallback": "m_L2cache->access(mf->get_addr(), mf, access_cycle, events)"
        in FILES["l2"],
    "no_shader_s1_hook": "awma_s1" not in FILES["shader"]
        and "R101R3" not in FILES["shader"],
    "no_s1_side_queue": "m_awma_s1" not in FILES["cache_h"],
    "no_extra_response_port": "awma_s1_partition_hit" in FILES["cache"]
        and "push(" not in FILES["cache"].split(
            "l2_cache::awma_s1_partition_hit", 1
        )[1].split("}", 1)[0],
    "no_tag_allocation": "m_tag_array" not in FILES["cache"].split(
        "l2_cache::awma_s1_partition_hit", 1
    )[1].split("}", 1)[0],
    "identity_assertion": "mf->get_sim_va() == mf->get_sim_pa()" in FILES["l2"],
    "exactly_once_marker": "mark_awma_r101r3_s1_observed" in FILES["l2"]
        and "duplicate S1 partition-hit application" in FILES["l2"],
    "roi_only": "s1_window_active()" in FILES["l2"],
    "sector_geometry": "get_atom_sz() == SECTOR_SIZE" in FILES["l2"],
    "ordinary_l2_stats": "m_stats.inc_stats(mf->get_access_type(), HIT"
        in FILES["cache"],
    "fail_closed": "note_s1_fallback" in FILES["l2"],
}
failed = sorted(name for name, passed in checks.items() if not passed)
if failed:
    raise SystemExit("AWMA_R101R3_S1_HOOKS FAIL " + ",".join(failed))
print(f"AWMA_R101R3_S1_HOOKS PASS checks={len(checks)}")
