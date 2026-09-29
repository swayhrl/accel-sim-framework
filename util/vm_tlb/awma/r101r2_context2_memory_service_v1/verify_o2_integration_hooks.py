#!/usr/bin/env python3
from pathlib import Path


RUNTIME = Path(
    "/root/awma_r101r2_context2_memory_service_174_v1_runtime/src/gpgpu-sim"
)
SHADER = (RUNTIME / "src/gpgpu-sim/shader.cc").read_text()
CACHE = (RUNTIME / "src/gpgpu-sim/gpu-cache.cc").read_text()

checks = {
    "post_translation_pre_l1_hook": (
        SHADER.index("if (awma_o2_try_admit(inst, access, bypassL1D))")
        < SHADER.index("if (bypassL1D) {", SHADER.index("bool ldst_unit::memory_cycle"))
    ),
    "ldgsts_not_excluded_from_global_read": (
        "access.get_type() == GLOBAL_ACC_R;" in SHADER
        and "access.get_type() == GLOBAL_ACC_R && !inst.m_is_ldgsts" not in SHADER
    ),
    "oracle_load_reuses_client3_writeback": (
        "m_next_wb = entry.mf->get_inst();" in SHADER
    ),
    "shared_dependency_classifier_is_consumed": (
        "entry.dependency == awma_r101r2_o2::READ_LDGSTS_DEPBAR" in SHADER
    ),
    "ldgsts_pending_decrement_preserved": (
        "m_pending_ldgsts[m_next_wb.warp_id()][m_next_wb.pc]" in SHADER
    ),
    "ldgsts_depbar_release_preserved": "m_core->unset_depbar(m_next_wb);" in SHADER,
    "oracle_does_not_directly_release_depbar": (
        "unset_depbar" not in SHADER[
            SHADER.index("bool ldst_unit::awma_o2_try_admit") :
            SHADER.index("bool ldst_unit::constant_cycle")
        ]
    ),
    "store_uses_normal_ack": "m_core->store_ack(entry.mf);" in SHADER,
    "service_ready_calls_set_reply": "entry.mf->set_reply();" in SHADER,
    "selector_isolated_none_or_oracle": (
        '"none"' in CACHE
        and '"oracle_1c"' in CACHE
        and "O2 service oracle cannot be combined with an L2 mechanism" in CACHE
    ),
    "context2_markers_are_parsed": all(
        marker in CACHE for marker in ('"CONTEXT_END"', '"ROI_START"', '"ROI_END"')
    ),
    "measured_roi_marker_aliases_are_parsed": (
        '"MEASURED_ROI_START"' in CACHE
        and '"MEASURED_ROI_END"' in CACHE
    ),
    "pre_roi_receipt_precedes_kernel4_pre": (
        CACHE.index("m_pre_roi_lifecycle_hash = lifecycle_hash();")
        < CACHE.index("++m_launched_kernels;", CACHE.index("void awma_transient_l2_controller::kernel_launched"))
    ),
    "terminal_equation_covers_oracle_queues": all(
        term in CACHE
        for term in (
            "m_service_outstanding == 0",
            "qualified == m_service_scheduled",
            "m_service_scheduled == m_service_one_cycle_ready",
            "m_service_one_cycle_ready == retired",
        )
    ),
}

failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("O2 integration hook failure: " + ", ".join(failed))
print(f"AWMA_R101R2_O2_INTEGRATION_HOOKS PASS checks={len(checks)}")
