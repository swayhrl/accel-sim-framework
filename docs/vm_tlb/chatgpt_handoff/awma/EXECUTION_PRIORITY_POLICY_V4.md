# AWMA Execution Priority Policy V4

Date: 2026-09-22
Ownership: ChatGPT
Status: ACTIVE POLICY

This supersedes V3 for all new/continued AWMA execution.

## 1. Core priority

AWMA mainline has priority over candidate side lanes.

All existing scientific identity, provenance, fail-closed, remote-publication,
and resource-aware parallelism requirements from V3 remain active unless
explicitly superseded below.

## 2. BLOCKED is a last-resort state

Codex MUST NOT mark a Goal `blocked` merely because an engineering step
fails.

The default behavior for ordinary engineering failures is:

`DIAGNOSE -> REPAIR/RECREATE -> VALIDATE -> CONTINUE`

Routine engineering work is solve-and-continue.

Examples that are NOT sufficient reason to BLOCK:

- missing compiler/tool when an accepted toolchain can be restored;
- configure/CMake/Make dependency failures;
- stale generated files;
- missing `SIM_OBJ_FILES_DIR` or other generated build directories;
- wrong output-root or subdirectory build invocation;
- path/environment-variable mistakes;
- missing makedepend/m4/bison/flex/zlib/header plumbing when recoverable;
- local branch/worktree/build-cache corruption;
- transient SSH/mount/network failure with a safe retry/recovery path;
- Git publication/path mistakes;
- parser/build-script incompatibilities that do not alter the scientific
  contract;
- insufficient parallelism or process placement;
- a previous failed engineering attempt.

These should trigger an autonomous recovery ladder, not a Goal stop.

## 3. Allowed BLOCKED conditions

A Goal may be marked `blocked` only after the recovery ladder is exhausted and
one of the following is true:

### B1 — unavailable external dependency

A required artifact, credential, permission, host capability, hardware
resource, or externally administered service is genuinely unavailable and
cannot be restored or replaced by an already approved equivalent.

Examples:

- required immutable trace/model artifact does not exist in any approved
  location;
- admin-only mount/permission cannot be repaired from the current account;
- required GPU/host is physically unavailable and no approved substitute exists.

### B2 — scientific contract boundary

Continuing would require changing any of:

- workload/target identity;
- model revision;
- trace identity;
- simulation functional/timing semantics beyond the authorized diagnostic;
- evidence class;
- claim boundary;
- accepted baseline authority.

This is a scientific STOP, not an engineering BLOCK workaround.

### B3 — destructive/irreversible action requiring user approval

Continuation would require deleting or overwriting accepted evidence, changing
shared/system state outside the authorized sandbox, or another irreversible
action not already authorized.

### B4 — hard resource impossibility

Disk/quota/memory/runtime policy makes the task impossible and there is no
safe approved alternative, compaction, relocation, or staged execution path.

## 4. Mandatory recovery ladder before BLOCKED

For an engineering failure, Codex must attempt as applicable:

1. inspect the exact failing command and first causal error;
2. separate source state from generated/build state;
3. checkpoint/hash any valuable source diff or uncommitted scientific work;
4. discard only generated/cache/output artifacts when they are stale;
5. recreate a clean isolated staging from immutable accepted source;
6. reapply the minimal candidate/source patch;
7. restore the accepted toolchain/dependencies;
8. use the repository-authoritative top-level configure/build path;
9. run the smallest compile/directed smoke that isolates the failure;
10. retry with corrected environment/path/dependency graph;
11. use a previously accepted equivalent build path/container only if its
    provenance is already authorized;
12. continue automatically after PASS.

Do not accumulate ad-hoc repairs indefinitely.  Prefer clean reconstruction
over patching a poisoned build tree.

## 5. Recovery reporting

During recovery, report status as:

- `ENGINEERING_RECOVERY_IN_PROGRESS`;
- `ENGINEERING_RECOVERY_PASS`;
- `SCIENTIFIC_STOP_REQUIRED`; or
- one of the legitimate BLOCKED classes B1/B3/B4.

Do not use `blocked` as a synonym for "the current command failed".

## 6. Dependency-first parallel execution

V3 dependency/resource rules remain active.

Before serializing multiple runs, classify tasks as:

- INDEPENDENT;
- SPECULATIVE_DEPENDENT;
- STRICT_DEPENDENT;
- SERIALIZED_MUTABLE_RESOURCE.

After resource audit, launch the maximum safe set of executable tasks and
continuously refill free capacity.

Scientific admission ordering is not automatically an execution dependency.

## 7. Preserve accepted state

Recovery must never mutate:

- accepted baseline binaries;
- accepted immutable run directories;
- accepted trace/model assets;
- node164 evidence roots;
- historical reports/review packs.

Use separate staging/worktrees and opt-in candidate modes.

## 8. Stop boundary

Ordinary engineering problems should be solved autonomously.

Stop and return to ChatGPT only for:

- scientific contract/identity/claim change;
- promotion/replacement of an accepted baseline;
- implementation of a new architecture mechanism when not authorized;
- legitimate B1/B3/B4 blocker after recovery ladder exhaustion.
