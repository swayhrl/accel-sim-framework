# Lane 2 clean + dirty module r2

Status: **MODULE_REVIEW_READY / PRODUCTION_INTEGRATION_DEPENDENCY_PENDING**. This is not full TVD and not a B16/U_WB functional runtime.

Clean module was published first as `FT20261016_LANE2_CLEAN_MODULE_r1` at Framework `7697ed6b81d39d5eee8c005dd695553d783537b5`, Core `5267347de7d3244dd68a067fc2120a9cf0c55efb`. That pack is immutable. This revision adds dirty protocol validation and atomic same-slot promotion of a new dirty resident victim under full directory occupancy.

Seven scenario groups pass normally and under ASan+UBSan using the actual new directory and the historical production payload bank arbiter. Test-only functional/version backing checks data selected by canonical handles. Real cache victim admission, packet handoff, allocator pin/role transfer and L2-to-ICNT hooks are not integrated; all those production gates remain NOT_RUN. No scientific hit-rate, avoided-traffic or speedup result is claimed.

Read TVD_READY_MANIFEST.json, TVD_STATE_AND_SECTOR_CONTRACT.md, SOURCE_MAP.md, TEST_MATRIX.csv, PRODUCTION_GATES.csv and TVD_METADATA_COST.md. Lane 1 consumes CORE_MODULE.patch on its exact identity ABI source; do not merge a historical branch or instantiate a second allocator/address directory.

The independent module uses the public ABI published at Framework cb7d92e4 / Core 4fb91f0a. Only that ABI and contractual hooks have been published at the last bounded stage check; no executable reserve/pin/role-transfer/WB callback release is available yet. Lane 5 host budget consumed at cc97ee2a; only lightweight single-process compiler/tests ran, no shared formal simulation slots were claimed.

Packaging correction: see PACKAGING_REVISION.md. Prior r1 remains immutable; use this r2 as the current review entry.
