# Lane 2 clean module r1

Status: **CLEAN_MODULE_REVIEW_READY / PRODUCTION_INTEGRATION_DEPENDENCY_PENDING**.

Four clean scenario groups pass normally and with ASan+UBSan: exact-sector serial read, historical real bank contention + held response, clean write/atomic same-handle promotion, 128 combined-address capacity and failed/stale reservations/epoch cleanup, plus canonical-handle version oracle coverage. Tests cover the new production-linkable module; they do not drive a real cache victim hook yet. Full TVD is not asserted.

Read TVD_STATE_AND_SECTOR_CONTRACT.md, SOURCE_MAP.md, TVD_METADATA_COST.md and TVD_READY_MANIFEST.json. `CORE_MODULE.patch` applies on Lane 1 public ABI Core `4fb91f0a5c9eb3bf494a154ea1f24b9a56b34617`; includes only Lane 2 module/test/runner. Lane 1 is the final integrator. Dirty candidate code is present but not qualified by this clean-only pack.

Command: `EP_L2_SANITIZE=1 tests/ep_l2/run_tvd_directory.sh`; then EP_L2_SANITIZE=0. Logs preserve legacy -Wreorder warnings; all new warnings remain errors. Initial fixture compilation found that existing warning under -Werror; the test runner correction is a separate recorded commit, with no assertion deleted.

No formal experiments or canary simulations were launched. Raw compact logs: `/workspace/results/ep_l2_ft20261016/lane2/clean_module_r1/`.
