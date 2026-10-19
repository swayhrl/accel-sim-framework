# Immutable evidence consumed

No previous test is rerun or counted as a new SEM1 result.

| Evidence | Commit | Files and bounded interpretation |
|---|---|---|
| Entry | `46df82670a56a4498b6d6e23ad57859eb7c36945` | AGENTS.md; evidence_closure_20261019_v1 README, MASTER_PLAN, PLAN_CONTRACT.json, SEM1_GOAL; prep-only while AG4 active |
| V2 | `59db64ce6af73c9585e0588723325d97975c23dc` | DTC_LANE_V2_VALUE_SCOPE_V1/{LATEST_REPORT.md,VALUE_VISIBILITY_SCOPE.md,SOURCE_ROUTING_CROSSWALK.md}; 25 synthetic witnesses, production values=0; do not recreate external oracle |
| Y2 | `d085f98c10010d641ba4cfffa1f58fb8db3b56ee` | DTC_LANE_Y2_K1_REQUAL_V1/LATEST_REPORT.md and scripts/abi_ldst_probe.cc; real LDST ABI lifecycle; architectural values explicitly unproven |
| X2 | `46df82670a56a4498b6d6e23ad57859eb7c36945` | inherited DTC_LANE_X2_TERMINAL_EXPORT_V1/NORMAL_EXPORT_CONTRACT.md; print-only normal export, not payload proof; original Core baseline c0a5e2c3, X2 Core e32afdcf ancestry cited by AG3 |
| AG3 | `2f3a8c4b27780e2bf3818949a6e5356d9fd62327` | DTC_LANE_AG3_AE_AD_SCREEN_V1/{LATEST_REPORT.md,ACTUAL-LDST-FINAL_RESULT.json,ACTUAL-LDST-FINAL_COMMANDS.json}; actual LDST identity/finite/WB evidence; architectural_value_correctness=UNPROVEN |
| Prior source-access audit A | `f5c37d6edcce832a72cb0830021bffa78df6cc13` | iscas2027/service_closure_174_v1/review_pack/trace_body_v1/{WORKLOAD_SUMMARY.tsv,KERNEL_BODY_AUDIT.tsv}; published tables only, no trace body scan; full grid/typed routes, no source shape or alias proof |
| Current source | Core `c8090115bd57512b1b23fca7d925301fa620c751` | mem_fetch.h; shader.cc; dtc-l1-common.h; abstract_hardware_model.h; tests/dtc_l1_progressive_ldst_test.cc. Last fixture explicitly prints payload_values=UNPROVEN; not executed here |
| Authority observation | coordinator `2026-10-19T12:27:02Z` | coordinator reported AG4 dispatcher PID 779009, simulator descendant 795912, held AG_execution.lock. SEM1 did no live check and never read active raw stdout/maps. ACK initial snapshot was pending; this later observation confirms active gate |

Paths under `DTC_LANE_*` are relative to `docs/dtc_l1/review_packs/`. Worker-only transient source copies are under `/workspace/dtc-evidence-closure-20261019-v1/sem1/` and never replace immutable Git identities. COV1's immutable source/access handoff is consumed when published; conversational source hypotheses cannot qualify captured inputs.

COV1 immutable handoff `2cba9b193b091db8dd4550c4c3120b1d82d57ec6` is now consumed; see COV1_HANDOFF.md. Core/Framework source object inventories are CORE_SOURCE_BLOBS.tsv and FRAMEWORK_SOURCE_BLOBS.tsv. These are Git blob identities, not binary/library ABI equivalence claims.

R1 continuation: isolated diagnostic Core `1fcf5113c08a27b64ccca872c4a8fba4c12c1ece` and its source blobs are published under implementation_r1; no compile/run receipts exist. Coordinator supplied AG4 terminal `d8d0401dab0a1d9cb949302bcc05148328421cc2` and retained sole subsequent dispatch authority. COV1 `d986ba4db47b296c27b68541b2b867e294a652e6:N3_SOURCE_ONLY_DECODER_REVIEW.md` was read, including exact5000constant-table, prefetch, index/permutation and vector-width limits; unchanged source/access index remains2cba9b19. COV1 reference tests are independent evidence, not SEM1/native/production passes.
