# Lane 4 status

Status: READY_FOR_REVIEW_DEPENDENCY_PENDING_SHARED_B16_RELEASE.
Node: huangrulin-174. Task: FT20261016_LANE4_V1.
Branch in both repositories: `hrl/ep-l2-ft20261016-lane4-v1`.
Framework worktree: `/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane4-v1`.
Core worktree: `/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane4-v1`.
Producing Core: `b8b3d55b392fcff793d0aec684bddb73ba3065a9`.
Producing runtime Framework: `438df99dd5138ec42acd7ae9d05e76b9b01e2e5e`.
Latest verification tooling: `744c467274d0a74a53b265af1fd1bf9f3a7d7b71`.
Candidate binary SHA256: `63f26de29e2b1932062934044cb3131fa5e2d36fa9821094939188bceb66a8ea`.

Completed: bounded historical audit (38 Framework refs, 25 Core refs, 4176
node metadata files; 295 audit rows), default-OFF I_WB / I_META / I_READ_HIT
and I_WB_META, isolated builds, 12 production-driven C++ invocations, 6 illegal
mode rejections, 16 parser/adapter tests, 3 central-registry-controlled full
application runs, and an exact duplicate claim with no new process.

Historical OLD_D512_STATIC vectorAdd comparison: OFF 73873 -> optimistic
read reference 42918 cycles, both 56000000 instructions (1.721259x).
This is neither B16 performance nor implementable EP-L2 speedup or a strict
upper bound. No old shadow-WBUF or MSHR256 sensitivity fills an ideal cell.

Latest candidate all-OFF application control: COMPLETE_VALID, 73873 cycles,
56000000 instructions, all seven CSV families byte-identical to the older
control. The older control's seven CSVs also match retained node history.
This is an old-static validation control, not a B16 application baseline.
Known-byte/producer-version and finite-WBUF tests are distinct evidence from
SASS application performance, which has no numerical output image.

Formal B16 application rows: NOT_RUN (18 explicit pending cells including
Lane5-owned baselines and the two selected combinations). Lane1 publication
`02982b65e87f170103b44c6dbd562a8ffb03841e` now publishes runtime_ready=true
at Core `126394be46b15f55b9756d43eb9ca9a9baae1c84`. This parent is consumed
and tested in the Lane4 candidate. Independent qualification remains false;
its exact normal binary was hash-checked and lacks all three ideal flags.
Consumed Lane5 publication: `c603a5634b6b3f54aec10bdb1fc804e0a648b567`;
no independently qualified common diagnostic binary/B16 baseline spec exists.
Different-source/binary results are not called exact shared-baseline reuse.

Review packs:
- `docs/ep_l2/review_packs/FT20261016_LANE4_IDEAL_DIAGNOSTICS_r2/`
- `docs/ep_l2/review_packs/FT20261016_LANE4_OFF_EQUIVALENCE_r1/`

Current own active simulations: zero (actual central registry).
No unreported background continuation or polling daemon is running.
Next executable action: Lane1 applies the r2 CORE_MINIMAL.patch after exact
parent 126394be, then Lane5 independently qualifies one common binary with
the default-OFF diagnostic registrations and supplies its B16 baseline specs.
Lane4's prepared-spec adapter then derives/runs four first-wave workloads;
I_WB_META is restricted to convolution/FWT. There is no Full EP-L2 dependency.
This source/test candidate does not self-declare independent acceptance.
