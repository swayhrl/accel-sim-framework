# Lane 5 independent tooling and historical directed validation r1

Status: **TOOLING_TESTED / DEPENDENCY_PENDING**.

Read [STATUS](../../codex_handoff/fast_track_2026_10_16_v1/lane5/STATUS.md),
[HOST_BUDGET](../../codex_handoff/fast_track_2026_10_16_v1/lane5/HOST_BUDGET.md),
`SOURCE_MANIFEST.json`, `VALIDATION_SUMMARY.md`, and `PLOTTING_CONTRACT.md`.
Registry API/runner/data reference protocol: `util/ep_l2/ft_lane5/README.md`.

Delivered executable tools: central registry with process race tests; quota
and build leases; content-complete identity and frozen runner; independent
ordered sector data/version and lifecycle validator. 39 Python tests pass.
Three historical production-source directed scripts (four C++ executables)
also pass in private outputs under a shared resource lease. These do not
qualify the new finite-WBUF implementation or replace independent production
tests when Lane 1 releases it.

The 13 historical workload inputs exist and their list hashes match history.
`BASELINE_RESULTS.csv`, `MECHANISM_RESULTS.csv`, `DIAGNOSTIC_RESULTS.csv`, and
`RESOURCE_MOVEMENT.csv` are intentionally header-only: no new qualified runtime
has been launched. Pending rows are explicit; scientific zeroes are not invented.
`RAW_LOG_INDEX.csv` indexes historical directed validation only.

Lane 1's consumed publication is source-exact in `LANE1_*` and the manifest:
runtime_ready=false, actual binary/config identity absent. Lane 2/3/4 consumed
receipts are also retained with exact publication and content identity.

No Core branch was created or production simulator code modified. No other
project worktree, trace, running process or result was altered. No daemon is
running on behalf of this publication. Consume a qualified Lane 1 release at
the next stage transition; begin B16/U_WB16 without waiting for TVD/RO.
