# Parallel Execution and Autonomous Recovery Policy

## Activation

The AWMA Simulation Analysis foundation is now allowed to run **in parallel** with the active Native Characterization work.

This parallelism is intentional:

```text
109 / RTX4080
  Native capture / NVBit / NCU / NSYS

174-new / separate Codex worktree
  Simulation Analysis foundation / runtime / admission / telemetry
```

A second Codex window on 174-new is allowed while the existing Qwen Decode/native-analysis Goal continues, provided all isolation rules below are obeyed.

## Isolation rules

The Simulation Goal must:

1. create a fresh Git worktree and branch;
2. never modify or clean the worktree used by the active Qwen/Native Goal;
3. never kill/restart another Goal, VS Code extension host, Codex app-server, SSHFS mount, or shared process merely to simplify this task;
4. use dedicated build/temp/run directories under its own worktree or a clearly named simulation scratch root;
5. write node164 outputs only into AWMA simulation/catalog/provenance namespaces authorized by the handoff;
6. not mutate accepted C16/native raw, parsed, feature, or catalog authority;
7. not use the 109 GPU in this stage;
8. not start large mechanism sweeps or multi-model simulation campaigns.

## Resource-coexistence rule

Before heavy build/hash/simulation work, inspect current host load and active related processes.

Use bounded parallelism. Prefer conservative build concurrency rather than consuming all CPU cores. If a build or hash operation creates material contention with the active Native-analysis Goal, lower its priority or reduce concurrency and continue; do not terminate the other Goal.

Large temporary outputs must not fill 174-new local overlay. Use the established node164/simulation scratch policy for durable or potentially large artifacts.

## Goal-mode recovery principle

This is a **solve-and-continue** Goal, not a stop-on-first-blocker checklist.

When a problem is recoverable without changing scientific meaning, Codex should diagnose it, implement the narrowest safe repair, test it, record it, and continue.

Examples that should normally be solved inline:

- missing path or stale hard-coded path;
- absent generated directory;
- minor parser/schema mismatch with unambiguous intended semantics;
- build-system portability problem;
- missing user-space Python dependency;
- missing local helper binary that can be rebuilt from authoritative source;
- legacy script expecting an obsolete worktree path;
- stale manifest field spelling that can be adapted without changing identity;
- a test fixture needing normalization to the frozen schema;
- missing small catalog/index file that can be deterministically rebuilt from immutable entries.

## Runtime/toolchain recovery ladder

If simulator build/runtime bring-up encounters a blocker, do not stop immediately. Use the following recovery ladder, preserving evidence at each step:

1. inspect local and shared toolchains, CUDA installs, headers, compilers and existing binaries;
2. inspect authoritative Git branches/commits and existing framework/core checkouts;
3. search canonical node164 historical assets and review-pack receipts for source/binary identity;
4. repair non-semantic build portability issues in the isolated branch;
5. if a dependency can be installed safely in user space, use an isolated environment rather than a system-wide mutation;
6. if exact historical runtime is unavailable, build/qualify a maintainable current candidate rather than spending the whole Goal chasing an extinct binary;
7. if one runtime candidate fails, inspect the failure and try the next evidence-backed candidate when reasonable;
8. once recovery attempts are technically exhausted or would require a scientific/modeling decision, freeze the blocker precisely and continue all independent phases.

`BLOCKED_ENVIRONMENT` is a permitted **sub-result**, not an excuse to stop the whole Goal early.

## When Codex may stop and ask for a decision

Escalation is appropriate only when proceeding would require one of the following:

- changing workload/model/input identity;
- inventing missing trace ordering/opcode/width/control semantics;
- changing simulator architectural semantics rather than portability/build plumbing;
- changing a formal scientific-status boundary;
- choosing between materially different architectural models with no existing authority;
- mutating/deleting accepted scientific raw or canonical history;
- a destructive operation with unclear recovery;
- a credential/permission barrier that has no safe alternative and blocks the whole remaining Goal.

Even then, complete and commit every independent safe phase before stopping whenever possible.

## Evidence requirements for every inline repair

For each repair that is not purely editorial, record:

```text
problem
root cause
repair
why scientific meaning is unchanged
files changed
tests/regressions
result
```

Prefer a compact `INLINE_RECOVERY_LOG.tsv` or equivalent review-pack section.

## No fake progress

Autonomous recovery does not permit weakening correctness gates.

Never:

- synthesize missing simulator trace fields;
- accept incomplete/drop/overflow trace as formal simulator input;
- mark a timed-out simulation as a complete formal run;
- silently change dtype/context/backend/input to make a workload run;
- promote diagnostic historical results to formal;
- overwrite Native evidence with Simulator evidence;
- claim historical exact reproduction from a non-matching runtime.

The objective is to solve engineering blockers aggressively while keeping scientific boundaries fail-closed.
