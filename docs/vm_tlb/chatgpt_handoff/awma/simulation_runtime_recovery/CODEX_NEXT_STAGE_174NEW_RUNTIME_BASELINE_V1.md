# CODEX NEXT STAGE — 174-new NEW_SIM_BASELINE_V1 Runtime Recovery

## Status

Executable stage specification for a **new Codex window** on 174-new.

Primary node:

`root@10.208.130.174 -p 2239`

GPU use: none.

This stage may run in parallel with the existing Native/Qwen analysis work as long as it uses a fresh worktree and bounded CPU/I/O.

Suggested execution branch:

`hrl/awma-new-sim-baseline-174new-v1`

## Base authority

Start from the accepted Simulation Foundation remote branch:

`hrl/awma-simulation-foundation-174new-v1`

Remote authoritative commit:

`11990917cbae60f99ab629bfdf24265ad6e9cb64`

Tree:

`09cc2f029022c660a3f827af9abded0fb34bdb41`

Consume this handoff branch as task specification:

`hrl/awma-simulation-runtime-recovery-v1-coordination`

## Read first

Read in order:

1. `docs/vm_tlb/chatgpt_handoff/awma/simulation_runtime_recovery/README.md`
2. `FOUNDATION_V1_REVIEW.md`
3. `RUNTIME_RECOVERY_STRATEGY.md`
4. `ACCEPTANCE_REQUIREMENTS.md`
5. this file.

Also review:

- `docs/vm_tlb/review_packs/AWMA_SIMULATION_FOUNDATION_174NEW_V1/`
- `docs/vm_tlb/review_packs/C12_C15_174NEW_CANONICAL_INHERITANCE_V2/`
- `util/vm_tlb/awma/simulation/`
- current `run_m4c_replay.sh`, telemetry/export tools, VM/TLB configs and relevant Core source/build scripts.

## Goal

Do not stop at environment inventory. Resolve the runtime/toolchain problem as far as safely possible and either:

1. qualify a maintainable `NEW_SIM_BASELINE_V1`, or
2. exhaust the defined recovery ladder and prove a genuinely external dependency.

Treat recoverable build/toolchain/path issues as subproblems to solve, test, document and continue.

## Phase A — Re-anchor and protect parallel work

Create a fresh worktree from the Simulation Foundation authority.

Record:

- hostname;
- worktree path;
- base commit/tree;
- node164 mount identity;
- active unrelated worktrees/processes only as read-only awareness.

Do not modify, clean, restart or kill the active Qwen/native worktree/processes.

## Phase B — Full toolchain discovery and compatibility matrix

Build a concise matrix of candidate toolchains and source pairs.

Search:

- local CUDA roots and `nvcc`;
- shared filesystems and package caches;
- conda/mamba/user-space environments;
- authorized-node toolchains reachable without disturbing workloads, including 109 if useful;
- repo build documentation/scripts for CUDA/GCC compatibility assumptions.

For each candidate record:

- source/location;
- CUDA/nvcc version;
- GCC/G++ version;
- required libs/headers;
- expected compatibility with selected Framework/Core;
- whether use is read-only/copy/user-space;
- reason accepted/rejected.

Do not assume CUDA 12.8 is suitable solely because 109 has it.

## Phase C — Isolated toolchain provisioning

If no local compatible toolkit exists, autonomously provision one in an isolated user-space/node164-backed location.

Permitted approaches include:

- copying a verified compatible toolkit subset/full toolkit from an authorized node;
- using an existing package cache;
- creating an isolated conda/user-space toolkit environment;
- downloading a vendor toolkit if network access and integrity verification permit.

Do not perform a system-wide CUDA replacement.

Hash/version-close the chosen toolchain.

If one candidate fails for a recoverable incompatibility, try the next justified candidate rather than stopping immediately.

## Phase D — Select maintainable Framework/Core baseline candidate

Audit available source candidates for the required simulation semantics:

- trace-driven `.traceg.xz` input;
- VM/TLB/PTW/PWC support;
- cache/memory hierarchy support;
- telemetry needed by AWMA;
- compatibility with current M4C/M4B config concepts or a documented migration.

The exact historical Core `57bb71...` is not required if unavailable.

Choose a current maintainable source pair and freeze SHAs.

If small compilation/portability fixes are needed and do not alter simulator semantics, fix inline with directed regression tests.

If a change affects TLB/PTW/cache/timing semantics, document the semantic delta explicitly and do not treat it as a cosmetic build fix.

## Phase E — Build and binary closure

Build in isolation with bounded parallelism (default `-j2`).

Capture:

- complete build command/env;
- Framework SHA;
- Core SHA;
- patch/diff identities;
- toolchain versions/hashes;
- binary path, size and SHA256;
- relevant config/telemetry schema versions.

A successful compile alone does not qualify the baseline.

## Phase F — Consumer-contract hardening

Before current-model use, fix the two review gaps inline:

1. require explicit synchronization/control semantics in `SIM_COMPAT_CAPTURE_V1` admission, with a negative fixture when omitted;
2. strengthen trace admission using a real traceg parser/grammar smoke when the runtime/parser is available, including at least one malformed-record rejection test.

Preserve the existing fail-closed C16WARP1/MREF rejection.

Run all existing Simulation Foundation tests plus new directed tests.

## Phase G — Smoke ladder

Execute in increasing-cost order:

1. simulator binary startup/config parse;
2. known tiny traceg parser smoke;
3. VM-disabled/reference smoke;
4. VM-enabled minimal smoke with required telemetry;
5. bounded C12 Prefill historical anchor;
6. bounded C12 Decode historical anchor.

For each attempt record command, config SHA, SIM_INPUT identity, binary SHA, runtime, exit state, raw log SHA and normalized telemetry SHA.

Do not run the full historical C12 matrix.

## Phase H — Historical calibration

For Prefill and Decode anchors, compare the new baseline with historical C12 references only where metric definitions align.

At minimum inspect:

- completion/parser record invariants;
- VM/TLB/PTW/PWC telemetry presence;
- L1/L2/DRAM/memory traffic where definitions align;
- cycles/IPC/runtime metric definitions if comparable.

Classify every compared metric/result using the categories in `RUNTIME_RECOVERY_STRATEGY.md`.

Unexplained mismatch prevents qualification.

Do not tune unrelated architecture parameters merely to force historical numerical equality.

## Phase I — Freeze NEW_SIM_BASELINE_V1

If all acceptance gates pass, create a canonical baseline descriptor and catalog entry containing at least:

- `SIM_BASELINE_ID`;
- Framework/Core SHAs;
- semantic patch SHAs;
- toolchain identity;
- binary SHA;
- base/trace/VM overlay config hashes;
- telemetry schema;
- supported claim scope;
- known deviations from historical C12 runtime;
- calibration anchor receipts.

Store only small metadata in node164 AWMA simulation catalog/provenance namespaces.

## Phase J — Prepare producer-facing handoff

If the baseline is qualified, emit a producer-facing compatibility receipt specifying exactly what 109 `SIM_COMPAT_CAPTURE_V1` output must satisfy for admission and first smoke.

Do not use 109 GPU in this stage.

If the baseline remains externally blocked after the full recovery ladder, emit the exact artifact/version/source requirement that must be provided next.

## Required tests/regressions

At minimum:

- all existing `test_simulation_foundation.py` tests;
- explicit sync/control omission rejection;
- malformed traceg parser rejection;
- toolchain/binary identity determinism;
- SIM_INPUT hash mismatch rejection;
- baseline catalog idempotence/conflict rejection;
- telemetry normalization deterministic regression;
- historical status preservation;
- C16WARP1/MREF simulator-ineligible regression.

Do not weaken tests to obtain PASS.

## Required review pack

Create:

`docs/vm_tlb/review_packs/AWMA_NEW_SIM_BASELINE_174NEW_V1/`

Required contents at minimum:

- `README.md`
- `SOURCE_ANCHORS.md`
- `EXECUTION_CONTEXT.md`
- `TOOLCHAIN_COMPATIBILITY_MATRIX.tsv`
- `TOOLCHAIN_RECEIPT.md`
- `SOURCE_BASELINE_SELECTION.md`
- `SEMANTIC_PATCH_AUDIT.md`
- `BUILD_RECEIPT.md`
- `BINARY_RECEIPT.md`
- `SIM_INPUT_ADMISSION_REGRESSION.tsv`
- `SMOKE_LADDER_RESULTS.tsv`
- `C12_PREFILL_CALIBRATION.tsv`
- `C12_DECODE_CALIBRATION.tsv`
- `BASELINE_QUALIFICATION_DECISION.json`
- `SIM_COMPAT_CAPTURE_CONSUMER_V2.md`
- `PRODUCER_HANDOFF.md` if qualified, otherwise `EXTERNAL_BLOCKER.md`
- `TEST_AND_REGRESSION_SUMMARY.md`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Codex report:

`docs/vm_tlb/codex_handoff/awma/NEW_SIM_BASELINE_174NEW_REPORT.md`

## Autonomous recovery rule

For missing dependencies, compile errors, stale paths, incompatible compiler versions, minor parser issues or obvious portability problems:

`diagnose → choose safe recovery → implement → test → document → continue`

Do not STOP merely to ask how to install/provision a recoverable build dependency.

STOP early only for a scientific-semantic conflict, a destructive action that requires authorization, or a genuinely external artifact after the complete recovery ladder is exhausted.

## STOP boundary

STOP after either:

- `NEW_SIM_BASELINE_V1_QUALIFIED`, or
- `AWMA_SIM_RUNTIME_RECOVERY_BLOCKED_EXTERNAL_DEPENDENCY` with all acceptance conditions for that status satisfied.

Do not proceed to current-model GPU capture or mechanism sweeps in this Goal.
