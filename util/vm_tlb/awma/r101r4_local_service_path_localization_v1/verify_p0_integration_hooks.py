#!/usr/bin/env python3
"""Fail-closed source checks for the fixed P0 pre-L1 service."""

from pathlib import Path


ROOT = Path(
    "/root/awma_r101r4_local_service_path_localization_174_v1_runtime/"
    "src/gpgpu-sim"
)
SHADER = (ROOT / "src/gpgpu-sim/shader.cc").read_text()
SHADER_H = (ROOT / "src/gpgpu-sim/shader.h").read_text()
CACHE = (ROOT / "src/gpgpu-sim/gpu-cache.cc").read_text()
CACHE_H = (ROOT / "src/gpgpu-sim/gpu-cache.h").read_text()
POLICY = (ROOT / "src/gpgpu-sim/awma_r101r4_local_service.h").read_text()

memory = SHADER[SHADER.index("bool ldst_unit::memory_cycle"):]
service = SHADER[
    SHADER.index("awma_r101r4::admission_result ldst_unit::awma_pre_l1_try_admit"):
    SHADER.index("bool ldst_unit::constant_cycle")
]
checks = {
    "fixed_scheduled_capacity": "kScheduledCapacity = 1" in POLICY,
    "fixed_ready_capacity": "kReadyCapacity = 16" in POLICY,
    "opt_in_selector": 'getenv("AWMA_R101R4_SERVICE_MODE")' in CACHE,
    "separate_diagnostics": 'getenv("AWMA_R101R4_DIAGNOSTICS")' in CACHE,
    "default_none": "SERVICE_MODE_NONE" in CACHE,
    "p0_mode": "SERVICE_MODE_FINITE_PREL1" in CACHE_H,
    "post_translation_pre_l1": (
        memory.index("awma_pre_l1_try_admit")
        < memory.index("if (bypassL1D)")
        and memory.index("awma_pre_l1_try_admit")
        < memory.index("process_memory_access_queue_l1cache")
    ),
    "scheduled_capacity_enforced":
        "scheduled_full(m_awma_o2_scheduled.size())" in service,
    "scheduled_backpressure_result":
        "ADMISSION_BACKPRESSURED" in service,
    "natural_instruction_stall": (
        "local_service == awma_r101r4::ADMISSION_BACKPRESSURED" in memory
        and "stall_reason = COAL_STALL" in memory
    ),
    "no_full_fallback": (
        service.index("ADMISSION_BACKPRESSURED")
        < service.index("m_mf_allocator->alloc")
    ),
    "ready_capacity_enforced":
        "ready_full(m_awma_o2_ready.size())" in service,
    "ready_full_retains_scheduled": (
        "note_p0_ready_full" in service and "break;" in service
    ),
    "one_cycle_ready": "one_cycle_ready(admitted)" in SHADER_H,
    "eligibility_accounting": "note_p0_ready_eligible" in service,
    "original_ldg_writeback_client":
        "m_next_wb = entry.mf->get_inst();" in SHADER,
    "ldgsts_dependency_preserved":
        "READ_LDGSTS_DEPBAR" in SHADER,
    "ldgsts_depbar_preserved": "m_core->unset_depbar(m_next_wb);" in SHADER,
    "store_ack_preserved": "m_core->store_ack(entry.mf);" in SHADER,
    "duplicate_guard": "invalid O2 ready response state" in SHADER,
    "terminal_capacity_equations":
        "m_p0_ready_eligible == m_service_scheduled" in CACHE,
    "no_new_response_client": "m_num_writeback_clients" not in service,
}
failed = sorted(name for name, passed in checks.items() if not passed)
if failed:
    raise SystemExit("AWMA_R101R4_P0_HOOKS FAIL " + ",".join(failed))
print(f"AWMA_R101R4_P0_HOOKS PASS checks={len(checks)}")
