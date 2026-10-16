# Lane 1 status

Status: R0_INDEPENDENTLY_QUALIFIED_R1_PRODUCER_INTEGRATION_READY. Continuation authority aec01450d3c527524ee09ee59242f582fafe5354; scientific authority6c136e2a remains unchanged. Execution branch in both repositories hrl/ep-l2-ft20261016-lane1-v1.

## R0 primary handoff

R0 publication02982b65e87f170103b44c6dbd562a8ffb03841e, producing Framework37dec04d223ae65167c5584e56887c74f6540d27, Core126394be46b15f55b9756d43eb9ca9a9baae1c84, binary0b504f5573ea0721709bc3439334f7f97a177286eaf73a36876403c7c9228698. BASELINE_CONTRACT_V1.json remains unchanged. The binary was rehashed and made read/execute-only; no rebuild or overwrite. Review pack FT20261016_LANE1_R0_HANDOFF_r3 was pushed/read back at2556909e55bb43c1d819f8c0417f5fc8b93630d9. Lane 5 publication 221c7f65 independently qualified B16/U_WB16 and launched the first sad pair. Its exact qualification envelope and evidence hash were consumed; live registry PIDs were checked. Independent acceptance belongs to Lane 5 and covers only those two R0 vectors. No R1/TVD/RO dependency. Existing three application OFF pairs are reused, not rerun.

## Separate R1 diagnostic candidate

Isolated worktrees /workspace/worktrees/accel-sim-ep-l2-ft20261016-lane1-r1 and /workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane1-r1; separate build /workspace/build/ep-l2-ft20261016-lane1-r1; results /workspace/results/ep_l2_ft20261016/lane1/r1. Producing Frameworkfb64d9520f20a562cc0db78b838d13f4599b49ce / Corebe651ccfe7bd47c0bbd8c30fe6439ae3b60cf8de. Exact Lane 4 patch integrated; own four excluded CMake test targets added. Immutable binary and ordered config hashes are in R1_DIAGNOSTIC_CONTRACT_V1.json; R1_MATCHED_BASELINE_TEMPLATE.json is unqualified and not a runnable application spec.

Ten production test executions pass; five whole OFF fixture logs exactly match frozen R0; six intended illegal ideal combinations reject. First configure/harness diagnostics retained. No application simulation launched by Lane 1 this continuation, and no R1 application equality, performance or independent qualification claimed. Build used central two-CPU lease; tests one-CPU leases, all released. Other tasks, Lane 2/3 active leases and Lane 5 running R0 pair remain untouched.

## Subsequent integration

Lane 2/3 own minimal production adapters against exact R0; latest bounded publications are Lane 2 f38632c2 (candidate c9666ae6, tests in progress) and Lane 3 bfa193e7. Final Lane 1 R2/R3 integration and Lane 5 feature qualification await qualified minimal producer-adapter receipts. INTEGRATION_QUEUE_R2_R3.md records expected conflicts and source/metric/oracle boundaries. No polling daemon or background task is promised.

Review: docs/ep_l2/review_packs/FT20261016_LANE1_R1_DIAGNOSTIC_INTEGRATION_r1/. R0 packs are retained.

R0 original source/config worktrees are preserved by detaching at their existing heads without changing source files. The same Lane 1 execution refs advance by fast-forward only in the isolated R1 worktrees; frozen R0 binaries/results are independent of those refs.
