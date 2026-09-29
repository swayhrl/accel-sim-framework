#!/usr/bin/env python3
"""Fail-closed placement checks for P1."""

from pathlib import Path

ROOT = Path("/root/awma_r101r4_p1_post_l1_local_service_174_v1_runtime/src/gpgpu-sim")
SHADER = (ROOT / "src/gpgpu-sim/shader.cc").read_text()
CACHE = (ROOT / "src/gpgpu-sim/gpu-cache.cc").read_text()
HEADER = (ROOT / "src/gpgpu-sim/shader.h").read_text()

cycle = CACHE[CACHE.index("void baseline_cache::cycle()"):]
p1 = SHADER[SHADER.index("bool ldst_unit::awma_p1_candidate_impl"):]
checks = {
    "after_l1_miss_queue": "awma_r101r4_p1_candidate(mf)" in cycle,
    "l1_cache_instance_only": (
        "m_level == L1_GPU_CACHE && "
        "awma_r101r4_p1_candidate(mf)" in cycle
    ),
    "before_normal_memport": (
        cycle.index("awma_r101r4_p1_candidate(mf)")
        < cycle.index("m_memport->push(mf)")
    ),
    "l1_lookup_preserved": "m_L1D->access(mf_next->get_addr()" in SHADER,
    "mshr_allocation_preserved": "m_mshrs.add(mshr_addr, mf);" in CACHE,
    "miss_queue_preserved": "m_miss_queue.push_back(mf);" in CACHE,
    "l1_hit_not_routed": (
        SHADER.index("if (status == HIT)") <
        SHADER.index("void ldst_unit::awma_p1_service_cycle")
    ),
    "local_set_reply": "entry.mf->set_reply();" in p1,
    "normal_ldst_fill": "fill(entry.mf);" in p1,
    "normal_l1_fill": "m_L1D->fill(mf" in SHADER,
    "normal_mshr_ready": "m_mshrs.mark_ready" in CACHE,
    "client4_completion": "m_L1D && m_L1D->access_ready()" in SHADER,
    "scheduled_cap1": "scheduled_full(m_awma_p1_scheduled.size())" in p1,
    "ready_cap16": "ready_full(m_awma_p1_ready.size())" in p1,
    "scheduled_backpressure": "note_p1_scheduled_full" in p1,
    "ready_backpressure": "note_p1_ready_full" in p1,
    "one_cycle_ready": "one_cycle_ready(admitted)" in HEADER,
    "response_fifo_capacity": "!response_buffer_full()" in p1,
    "no_request_icnt_on_hit": "awma_r101r4_p1_push(mf);" in cycle,
    "ldgsts_preserved": "m_is_ldgsts" in p1 and "unset_depbar" in SHADER,
    "write_ack_preserved": "m_core->store_ack(mf);" in SHADER,
    "default_opt_in": 'getenv("AWMA_R101R4_SERVICE_MODE")' in CACHE,
    "terminal_equations": "m_p1_outstanding == 0" in CACHE,
}
failed = sorted(k for k,v in checks.items() if not v)
if failed: raise SystemExit("AWMA_R101R4_P1_HOOKS FAIL "+",".join(failed))
print(f"AWMA_R101R4_P1_HOOKS PASS checks={len(checks)}")
