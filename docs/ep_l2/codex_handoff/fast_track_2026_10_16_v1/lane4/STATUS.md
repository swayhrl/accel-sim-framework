# Lane 4 status

Status: IN_PROGRESS_LATEST_ALL_OFF_TRACE_EQUIVALENCE.
Node: huangrulin-174. Branch in both repositories: `hrl/ep-l2-ft20261016-lane4-v1`.
Framework worktree: `/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane4-v1`.
Core worktree: `/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane4-v1`.
Producing Core: `b8b3d55b392fcff793d0aec684bddb73ba3065a9`; producing Framework:
`438df99dd5138ec42acd7ae9d05e76b9b01e2e5e`; tooling: `61553bd07ab548616d3bcbc9e140e40e985d90ec`.

Completed: bounded historical audit, default-OFF I_WB/I_META/I_READ_HIT and
I_WB_META, release builds, 12 production-driven C++ invocations, six illegal
mode rejections, 16 parser/adapter tests, two central-registry-controlled
full-application HISTORICAL_DIAGNOSTIC modes, and exact duplicate reuse check.
VectorAdd OFF 73873 -> optimistic read reference 42918 cycles; same 56M
instructions. This is an old-static reference, not B16/EP-L2 speedup.

Formal B16 application rows: NOT_RUN. Lane1 now publishes runtime_ready=true
at 02982b65e87f170103b44c6dbd562a8ffb03841e but independent qualification remains
false; the normal binary lacks diagnostic registrations. Lane5 snapshot is
c603a5634b6b3f54aec10bdb1fc804e0a648b567. Different-source/binary rows are not
called shared baselines. Current own active simulations: one registry-owned vectorAdd all-OFF
OLD_STATIC application equivalence control for the latest diagnostic binary.
This is a historical validation control and cannot fill a B16 performance cell.
The run key and actual process identity are in RECEIPT.json.

Review pack: `docs/ep_l2/review_packs/FT20261016_LANE4_IDEAL_DIAGNOSTICS_r2`.
Next: Lane1 integrates CORE_MINIMAL.patch against its exact published parent;
Lane5 independently qualifies one common binary including default-OFF ideal
registrations and supplies B16 baseline specs. Derive/run the four first-wave
ideal sets through the central client, with only convolution/FWT combinations.
No Full EP-L2 dependency. Exact consumed publication/receipt hashes are in
DEPENDENCIES.json. This candidate has not self-declared independent acceptance.
