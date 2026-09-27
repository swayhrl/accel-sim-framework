# C16 E1 evidence ledger

Generated from `CLAIMS.json` and committed review-pack artifacts. The JSON/TSV retain full SHA and provenance.

## E1-001 · ESTABLISHED

With byte-identical FP16 inputs, the tested deployed low-bit implementation shows an operator-by-M-shape interaction.

Evidence: `E1 clean baseline`; `docs/vm_tlb/review_packs/C16_E1_CLEAN_BASELINE_CONSUMER_174NEW_V1/FINAL_DECISION.json`; metric `same_fp16_input_interaction_proven`.

Closure: PASS. Caveat: This does not isolate quantization or a traffic cause.

Paper ready: yes. Commit: `59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca`.

## E1-002 · ESTABLISHED

The packed AWQ storage in the tested M1 semantic profile is smaller than the device L2 capacity, while the dense FP16 weight is larger.

Evidence: `Semantic NCU V2`; `docs/vm_tlb/review_packs/C16_E1_SEMANTIC_NCU_V2_CONSUMER_174NEW_V1/CAPACITY_RESIDENCY_CONSISTENCY.json`; metric `AWQ_packed_storage_bytes;device_L2_bytes;RAW_FP16_dense_weight_bytes`.

Closure: PASS. Caveat: Capacity consistency is not cache causality.

Paper ready: yes. Commit: `cdd3ec7afbb1611cc52a4b74d32b38a3edabd131`.

## E1-003 · SUPPORTED_PARTIAL

A controlled pre-target memory-state intervention materially perturbs the tested AWQ target, with only partial preregistered reversibility support.

Evidence: `residency intervention`; `docs/vm_tlb/review_packs/C16_E1_RESIDENCY_INTERVENTION_CONSUMER_174NEW_V1/FINAL_DECISION.json`; metric `MATERIAL_TIMING_PERTURBATION;MATERIAL_DRAM_PERTURBATION;REVERSIBLE`.

Closure: RESIDENCY_INTERVENTION_PARTIALLY_SUPPORTED. Caveat: The primary warm recovery fails the strict equality-style gate; no unique L2 cause follows.

Paper ready: yes. Commit: `5b11dd41e98044fcad76da4a906c7ba8609eb828`.

## E1-004 · ESTABLISHED

Natural full-model execution disrupts the isolated warm-residency behavior at tested layer-zero FFN targets, with role-dependent timing response.

Evidence: `natural reuse`; `docs/vm_tlb/review_packs/C16_E1_NATURAL_REUSE_RESIDENCY_CONSUMER_174NEW_V1/FINAL_DECISION.json`; metric `classification;layer14_isolated_authority`.

Closure: CASE_B_WITH_CASE_D_ROLE_DEPENDENCE. Caveat: Layer 14 has no exact isolated reference; tested dose brackets are not physical cache knees.

Paper ready: yes. Commit: `4f9242d177220721cb9e669aad5dd9e29f04407d`.

## E1-005 · SUPPORTED_PARTIAL

CUDA targeted L2 persistence recovers material timing benefit in the tested isolated and natural local targets.

Evidence: `targeted CUDA L2 persistence`; `docs/vm_tlb/review_packs/C16_E1_L2_PERSISTENCE_INTERVENTION_CONSUMER_174NEW_V1/FINAL_DECISION.json`; metric `policy_qualification;strict_consumer_state`.

Closure: CLOSURE_PASS_WITH_STRICT_GATE_DIVERGENCE. Caveat: This software policy experiment does not reveal NVIDIA replacement policy; natural DRAM materiality gate did not pass.

Paper ready: yes. Commit: `1dcab9c8d932973399c5811dc817802bfb3b9dfe`.

## E1-006 · ESTABLISHED

Rotating protection retains multi-target local benefit, but its tested stable whole-decode gain remains below the preregistered materiality threshold.

Evidence: `shared residency`; `docs/vm_tlb/review_packs/C16_E1_SHARED_RESIDENCY_DESIGN_REVIEW_174NEW_V1/FINAL_DESIGN_REVIEW.json`; metric `multi_target_retained;material_decode_benefit`.

Closure: SHARED_RESIDENCY_LOCAL_ONLY. Caveat: The small system effect is consistent with limited protected coverage, not failed realization of each local saving.

Paper ready: yes. Commit: `5481d85951180dae90776442c3e0620af96a4712`.

## E1-007 · ESTABLISHED

Protecting all selected up-projection modules preserves local benefit and gives a positive but subthreshold whole-decode effect at N28.

Evidence: `coverage scaling`; `docs/vm_tlb/review_packs/C16_E1_COVERAGE_SCALING_CONSUMER_174NEW_V1/FINAL_DECISION.json`; metric `independent_stage_label`.

Closure: COVERAGE_SCALING_POSITIVE_BUT_SUBTHRESHOLD. Caveat: The negative outside-selected timing residual is measured accounting, not an identified cache slowdown.

Paper ready: yes. Commit: `eb4e737e24c27d1908a2fdf43f465ed5e0cfc66f`.

## E1-008 · ESTABLISHED

Extending protection across all FFN operator families does not yield a material whole-decode benefit in the tested native matrix.

Evidence: `operator-family closure`; `docs/vm_tlb/review_packs/C16_E1_OPERATOR_FAMILY_EXPANSION_CONSUMER_174NEW_V1/FINAL_DECISION.json`; metric `independent_stage_label;raw_evidence_match`.

Closure: OPERATOR_FAMILY_NOT_SUPPORTED. Caveat: Only the up-projection family has material selected local benefit; the residual cause is unknown.

Paper ready: yes. Commit: `278964bfb243a93adf43e748eb3e067e34b16b8a`.

## E1-009 · ESTABLISHED

Across all tested native persistence budgets, material local up-projection savings coexist with no material whole-decode benefit; run-aligned top-level accounting localizes the offset to other semantic work.

Evidence: `residency cost/benefit closure; RESIDENCY_OFFSET_LOCALIZED`; `docs/vm_tlb/review_packs/C16_E1_RESIDENCY_COST_BENEFIT_CLOSURE_CONSUMER_174NEW_V1/INDEPENDENT_BUDGET_EFFECT_ANALYSIS.json`; metric `budgets.*.medians;material_local_up_count`.

Closure: RESIDENCY_OFFSET_LOCALIZED. Caveat: The budget experiment is native CUDA policy evidence; the source of each semantic offset is not uniquely identified.

Paper ready: yes. Commit: `0ccd19d4511e8d55c31eb9d8899d33c35da8778c`.

## E1-010 · DIAGNOSTIC_ONLY

The representative layer-zero self-attention NCU range does not reproduce the aggregate full-model self-attention slowdown.

Evidence: `residency cost/benefit closure`; `docs/vm_tlb/review_packs/C16_E1_RESIDENCY_COST_BENEFIT_CLOSURE_CONSUMER_174NEW_V1/FINAL_DECISION.json`; metric `claim_boundary;representative_ncu_profile_count`.

Closure: PASS. Caveat: No single kernel or unique microarchitectural cause is established.

Paper ready: yes. Commit: `0ccd19d4511e8d55c31eb9d8899d33c35da8778c`.

## E1-011 · SUPPORTED_PARTIAL

The bounded D1-D3 full-SASS trace is qualified and admitted for this specific workload and trace scope.

Evidence: `bounded D1-D3 trace qualification`; `docs/vm_tlb/review_packs/C16_E1_TRACE_ADDRESS_NAMESPACE_INTEGRATION_174NEW_V1/UPSTREAM_TRACE_ADMISSION_AUDIT.json`; metric `qualification;node164_admission;kernel_count`.

Closure: UPSTREAM_ACCEPTED_AND_174_AUDIT_PASS. Caveat: The producer trace pack lives on the admitted remote store; this branch carries its qualified audit, not the full raw trace.

Paper ready: yes. Commit: `2fa207fbc37a48f12641d810319b03ba1cf4e381`.

## E1-012 · ESTABLISHED

The oracle elastic qweight residency implementation passes CPU-only semantic, quota-full, invariants and baseline-OFF neutrality tests.

Evidence: `oracle elastic implementation; quota-full semantic addendum`; `docs/vm_tlb/review_packs/C16_E1_ORACLE_ELASTIC_QWEIGHT_RESIDENCY_IMPLEMENTATION_PREP_174NEW_V1/FINAL_DECISION.json`; metric `semantic_addendum_implemented;baseline_off_neutrality_pass;real_c16_simulation_performed`.

Closure: IMPLEMENTATION_READY_FOR_TRACE_INTEGRATION. Caveat: CPU-only synthetic qualification does not establish timing benefit.

Paper ready: yes. Commit: `a1f709c4cc5628aca9ff68ffe06572b79ca5fd4d`.

## E1-013 · ESTABLISHED

For this admitted trace and platform configuration, the target addresses preserve the same numeric namespace through simulator L2 oracle lookup.

Evidence: `trace-to-sim L2 namespace qualification`; `docs/vm_tlb/review_packs/C16_E1_TRACE_ADDRESS_NAMESPACE_INTEGRATION_174NEW_V1/TRACE_ADDRESS_NAMESPACE_FINAL_DECISION.json`; metric `exact_address_chain_closed;all_28_regions_observed`.

Closure: C16_E1_TRACE_TO_SIM_L2_NAMESPACE_QUALIFIED_V1. Caveat: Address integration canaries do not measure performance or full Ada microarchitecture fidelity.

Paper ready: yes. Commit: `2fa207fbc37a48f12641d810319b03ba1cf4e381`.

## E1-014 · PENDING_B16

The current B16 canary defines an R0 baseline, M1 B16 candidate and separate diagnostic configuration; performance admission is still pending.

Evidence: `current B16 performance-canary design`; `docs/vm_tlb/review_packs/C16_E1_ORACLE_ELASTIC_B16_REUSE_PERFORMANCE_CANARY_174NEW_V1/RUN_MATRIX.json`; metric `runs.R0_BASELINE;runs.M1_B16;runs.M1_B16_DIAGNOSTIC`.

Closure: DESIGN_ONLY. Caveat: No accepted B16 timing, speedup or mechanism counter result is available in this snapshot.

Paper ready: no. Commit: `be11dd34c24d569f6e002eedbe2e2fa0fa14db1b`.

## E1-015 · UNESTABLISHED

A unique L2 replacement or self-attention kernel cause for the aggregate offset has not been established.

Evidence: `claim boundary`; `docs/vm_tlb/review_packs/C16_E1_RESIDENCY_COST_BENEFIT_CLOSURE_CONSUMER_174NEW_V1/FINAL_DECISION.json`; metric `claim_boundary`.

Closure: CAUSE_UNRESOLVED. Caveat: This is a limitation, not a positive causal claim.

Paper ready: yes. Commit: `0ccd19d4511e8d55c31eb9d8899d33c35da8778c`.
