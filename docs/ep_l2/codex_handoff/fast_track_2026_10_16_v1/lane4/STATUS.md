# Lane 4 review_r2 continuation status

Status: R1_HANDOFF_READY_DEPENDENCY_PENDING_COMMON_R1_RELEASE.
Consumed continuation: `aec01450d3c527524ee09ee59242f582fafe5354`;
original scientific contract: `6c136e2a56a008695f8c8b815723bf8f1a760db9`.
Node: huangrulin-174. Branch in both repos: `hrl/ep-l2-ft20261016-lane4-v1`.
Framework worktree: `/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane4-v1`.
Core worktree: `/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane4-v1`.
Producing candidate Core: `b8b3d55b392fcff793d0aec684bddb73ba3065a9`.
Producing runtime Framework: `438df99dd5138ec42acd7ae9d05e76b9b01e2e5e`.
New handoff/runner tooling: `83db0e3c9a6498a26d8c24538a07f85e220d0f9d`.
Candidate binary: `63f26de29e2b1932062934044cb3131fa5e2d36fa9821094939188bceb66a8ea` (reused, not rebuilt).

## R0 first; R1 separate

Lane5 should independently qualify frozen R0 and immediately run the five
B16/U_WB16 development pairs. R0 needs no Lane4 ideal flag, gate or binary.
R0 Core 126394be / Framework 37dec04d / binary 0b504f55 are protected.
R0 binary hash, inode, size and mtime are unchanged by this continuation.
Lane4 launches no simulator and takes no build lease while handing off R1.
The prior dependency wording about needing ideals applies only to R1 and does
not block R0. The older Lane5 receipt's runtime_ready=false is superseded by
Lane1's available R0; independent qualification is still Lane5's responsibility.

## Newly executed, verifiable work

- Replayed the existing r2 minimal patch against exact R0 in a private index.
  Full resulting tree `83f12a15448cfd3f2c54d0ac8cfcb0fbf848bd8b` equals candidate b8b3d55b.
  Ordinary Core index/worktree and R0 binary were unchanged.
- Strengthened the R1-only adapter: same producing source/binary/trace/epoch,
  baseline owner/key, frozen qualification bytes and derived config hash;
  each requested ideal mode consumes independent production evidence.
  Mode-by-mode qualification permits rolling execution without waiting for
  the other ideal modes. Normal R0 inspection has no ideal gate requirement.
- Executed 19 new synthetic input-binding tests: PASS. They include R0 normal
  acceptance without ideal registration/gates, mixed-source rejection,
  changed config/qualification rejection and the admitted combination scope.
  They do not qualify the model or count as performance runs.
- Rechecked both prior packs' SHA256SUMS and reused their 12 production C++,
  6 illegal-mode, 16 parser and 3 complete legacy application results.
  None of the three legacy applications was rerun; no new ideal point was added.

Actual Lane1 common R1 release: absent. Lane5-qualified R1/specs: absent at
consumed publications. R1 formal first-wave cells: 18 NOT_RUN, blank metrics
and identities. Four baselines belong to Lane5; twelve single ideals and two
convolution/FWT I_WB_META points belong to Lane4. R0 B16 cannot be the strict
matched numerator of a different R1 binary. The old 1.721259x vector reference
remains legacy evidence and is not inserted into the R1 table.

## Published evidence and exact dependencies

New: `docs/ep_l2/review_packs/FT20261016_LANE4_R1_HANDOFF_r1`.
Retained: `FT20261016_LANE4_IDEAL_DIAGNOSTICS_r2` and
`FT20261016_LANE4_OFF_EQUIVALENCE_r1` under `docs/ep_l2/review_packs/`.
Consumed Lane1 publication: `2556909e55bb43c1d819f8c0417f5fc8b93630d9`.
Consumed Lane5 publication: `c603a5634b6b3f54aec10bdb1fc804e0a648b567`.
Receipt snapshots/hash bindings are in the new pack's DEPENDENCIES.json.
Registry check: `2026-10-16T10:34:37.752089+00:00`; own active runs: zero.
No background continuation or polling daemon is running.

Next executable handoff: Lane1 applies CORE_MINIMAL.patch on a separate R1
worktree after exact 126394be and freezes actual new producing commits/binary.
Lane5 qualifies R1 normal behavior and each requested ideal mode, and supplies
same-R1-binary B16 baseline specs. Then use prepare_ft_lane4_b16.py and the
central registry to roll admitted cells and publish each completed cell.
No TVD/RO/Full EP-L2 dependency and no need to hold the R0 main experiment.
