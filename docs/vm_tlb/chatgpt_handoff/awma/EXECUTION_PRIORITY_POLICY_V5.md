# AWMA Execution Priority Policy V5

Date: 2026-09-22
Ownership: ChatGPT
Status: ACTIVE POLICY

This supersedes V4 for all new/continued AWMA execution.

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

### B1 — irrecoverable substantive dependency

B1 applies only when the missing item is substantively required for the
scientific execution and cannot be exactly recovered, deterministically
reconstructed from accepted provenance, or replaced by an already approved
equivalent without changing identity/semantics.

Before declaring B1, Codex MUST classify the missing item into one of four
classes:

#### P1 — SCIENTIFIC_PAYLOAD

The bytes/content themselves are part of the scientific identity or evidence.

Examples:

- immutable trace payload;
- model weights/revision;
- input tensor/data payload;
- native capture payload;
- exact simulator source/binary authority when no reproducible source/build
  chain exists.

If a P1 artifact has no accepted replica and its exact identity/content cannot
be recovered, B1 may be valid.

#### P2 — DERIVED_CONTROL_ARTIFACT

A runner/control artifact deterministically derived from already accepted
payload/provenance.

Examples:

- `kernelslist.g` or equivalent runner index;
- file-order list;
- symlink farm;
- launch list;
- generated overlay/config wrapper;
- checksum list;
- deterministic manifest projection;
- generated parser input that contains no new scientific payload.

Missing P2 artifacts are NOT B1 if they can be regenerated deterministically
from accepted authority.

Reconstruction rules:

1. derive only from accepted immutable payload/provenance;
2. preserve exact ordering, naming, encoding and newline/serialization rules;
3. reconstruct in isolated staging, never by mutating the durable authority;
4. if a historical hash exists, exact hash equality is the preferred gate;
5. if no historical hash exists, bind the derivation algorithm/source,
   accepted inputs and newly generated hash;
6. label the result as a derived/reconstructed artifact rather than falsely
   claiming it is the historical original;
7. require a legacy reproduction/identity gate before scientific admission.

#### P3 — PROVENANCE_WRAPPER

A receipt/catalog/index/manifest whose purpose is to point to or summarize
accepted evidence rather than constitute the scientific payload itself.

Its absence is NOT automatically B1.

Codex must first determine whether the same scientific identity can be closed
from other accepted authorities, replicas, hashes, run logs, manifests or
producer receipts.

If the missing wrapper is the only surviving information that disambiguates
scientific identity, then its loss may become B1 or a scientific STOP.

#### P4 — EXECUTION_EPHEMERA

Generated build/run convenience state.

Examples:

- build/cache/object directories;
- temporary output roots;
- generated dependency files;
- local runner directories;
- transient environment snapshots.

P4 is never B1 by itself; recreate it.

### B1 decision test

B1 is legitimate only if all of the following are true:

1. the missing capability/artifact is substantively required now;
2. accepted replicas/authorities have been searched;
3. deterministic reconstruction has been evaluated;
4. approved equivalent paths have been evaluated;
5. reconstruction/equivalence would either be impossible or would change
   scientific identity/semantics;
6. the recovery ladder is exhausted.

Examples of legitimate B1:

- required immutable trace/model payload has no accepted surviving replica;
- the only provenance needed to identify which of multiple non-equivalent
  payloads was used is lost;
- admin-only permission/mount cannot be restored from the current account;
- required hardware/host is physically unavailable and no approved substitute
  exists.

A missing filename, list, manifest, wrapper, path, generated config, or runner
index is not enough to establish B1.

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

For missing-input/artifact failures, Codex must first:

1. classify the missing item as P1/P2/P3/P4;
2. identify the accepted scientific payload and identity authority;
3. search accepted replicas, durable stores, review packs, receipts and logs;
4. determine whether exact/deterministic reconstruction is possible;
5. reconstruct only derived/wrapper artifacts in isolated staging;
6. hash-bind the reconstruction and compare with historical hash when
   available;
7. run an accepted legacy reproduction/identity gate before scientific use.

Only after this artifact-recovery analysis should ordinary engineering recovery
continue.

For an engineering failure, Codex must attempt as applicable:

1. inspect the exact failing command and first causal error;
2. separate scientific payload from derived wrapper/control state;
3. separate source state from generated/build state;
4. checkpoint/hash any valuable source diff or uncommitted scientific work;
5. discard only generated/cache/output artifacts when they are stale;
6. recreate a clean isolated staging from immutable accepted source;
7. reapply the minimal candidate/source patch;
8. restore the accepted toolchain/dependencies;
9. use the repository-authoritative top-level configure/build path;
10. run the smallest compile/directed smoke that isolates the failure;
11. retry with corrected environment/path/dependency graph;
12. use a previously accepted equivalent build path/container only if its
    provenance is already authorized;
13. continue automatically after PASS.

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
