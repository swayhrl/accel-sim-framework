# C16 V12.7 — merged remaining recovery and final copyback closeout

## Entry authority

- Scientific branch remains `hrl/vm-c16-g-retry570-v0` at reviewed HEAD `ef0d89b1ce297518f86c51cddce190abd47e7364`.
- Recovery branch is `hrl/vm-c16-g-post-restart-recovery-v12-6`.
- P1 is closed by commit `c1cf391aacadb84d1416c4cbadf4301a57c57ef8`:
  - `P1_DISCOVERED=62`
  - `P1_LOCAL_SHA_CLOSED=62`
  - 18 Llama S0 G1 tree files
  - 4 Q2 compact artifacts
  - 6 CUTLASS owner diagnostics
  - 34 Route-B V2 mapped-exact static maps
  - `REMOTE_DELETION_COUNT=0`

Do not redo P0 or P1 and do not re-transfer any artifact already closed by a published receipt unless a later audit proves corruption.

## One merged remaining Goal

There are no further user-visible transfer "rounds" after this document.  Treat everything after P1 as one continuous `P2_FINAL` Goal and continue until the final global reconciliation closes.

The transfer lane must not stop merely because one artifact class completes.  It should move to the next class automatically, preserving the priority order below.

## P2_FINAL priority order

### A. Qwen0 S3 formal dynamic evidence

Recover every retained `COPYBACK_READY` artifact belonging to the successful Qwen2.5-0.5B-Instruct S3 Prefill formal R6 capture, including all retained raw traces and every compact-tree constituent required to reproduce the published tree manifest.  Bind to the already published R6 authority and existing queue paths; do not infer filenames when the queue has exact paths.

### B. Qwen0 S3 R5 / independent repro / Decode retained evidence

Recover every retained scientific artifact from:

- successful S3 Prefill target-V2 discriminator;
- permitted independent reproduction;
- retained static maps / logs / source-to-NVBit join evidence needed to interpret them;
- Decode static-map / target-V1 / discriminator evidence, including the closed `PREDICATED_OFF_TARGET` path.

These remain scientifically useful even though Decode did not admit a formal R6 capture.

### C. Remaining campaign G1 profiler evidence

Recover all remaining `COPYBACK_READY` campaign G1 `.nsys-rep`, SQLite/export files, validation outputs, and phase-linked catalogs for Qwen0 and Qwen7 raw rows that were actually run under current campaign authority.

Do not regenerate a missing campaign row merely for copyback.  This lane only preserves existing retained evidence.

### D. All other unique scientific `COPYBACK_READY` artifacts

After A-C, reconcile the complete existing copyback queue and compact Git receipts.  Recover every remaining artifact that is BOTH:

1. scientific or provenance evidence that cannot be reproduced byte-for-byte from Git alone; and
2. still remote-only or not locally SHA-closed.

Typical examples include retained NVBit raw/map/log payloads, nsys reports/SQLite exports, exact-function static maps, parse manifests, parent receipts, source-catalog payloads, and unique campaign diagnostics.

Do not copy replaceable model packages, wheelhouses, package caches, pip caches, build trees, or downloaded checkpoints merely to make the queue empty.  If one of those is the sole carrier of an immutable scientific identity, record that exception explicitly before copying it.

## Endpoint independence gate

Before declaring final recovery complete, prove what `LOCAL_SHA_CLOSED` means physically.

Publish these fields in the final receipt:

- `remote_hostname`
- `remote_machine_identity` (best stable available non-secret identifier)
- `local_destination_hostname`
- `local_destination_root`
- `local_mount_source`
- `local_filesystem_type`
- `local_device_or_filesystem_identity` when available
- `endpoint_independence_status`

Acceptance requires one of:

- `INDEPENDENT_SELF_OWNED_OR_SEPARATE_PERSISTENT_ENDPOINT`, with evidence that the destination is not merely the same ephemeral rental filesystem; OR
- `PROVIDER_PERSISTENT_ENDPOINT_ONLY`, explicitly saying the scientific artifacts are safe across instance power-off but have not yet reached a self-owned machine.

If `/root/share/c16_recovery_v3` is only another filesystem on the same rental instance and not independently persistent, do NOT call global recovery complete.  Use the already configured canonical external/self-owned destination if one exists; do not invent a new destination or credentials.

## Per-artifact closure contract

For every newly recovered artifact:

1. consume exact remote path and frozen identity from `COPYBACK_QUEUE`, compact authority, or a prior remote-SHA receipt;
2. confirm remote regular-file existence and frozen byte size before copy when the server is available;
3. use resumable verified transfer (`rsync --partial --append-verify` or an existing equivalent);
4. compute local byte count and local SHA-256;
5. require exact equality with the frozen authority SHA before `LOCAL_SHA_CLOSED`;
6. never delete the sole remote copy;
7. if no frozen SHA exists, compute and freeze remote SHA first, publish that identity, then copy and compare;
8. on any mismatch, retain both copies and fail closed.

## Global reconciliation

After A-D, do a fresh full reconciliation rather than trusting cumulative counters.

Build `GLOBAL_SCIENTIFIC_COPYBACK_RECONCILIATION_V1.json` from:

- current `COPYBACK_QUEUE`;
- Llama shutdown/recovery receipts;
- Qwen0 R5/R6 compact receipts and tree manifests;
- campaign G1 receipts;
- any other Git-published `COPYBACK_READY` scientific records.

Every discovered scientific artifact must end in exactly one state:

- `LOCAL_SHA_CLOSED`
- `DUPLICATE_OF_LOCAL_SHA_CLOSED_ARTIFACT`
- `COMPACT_GIT_ONLY_NO_REMOTE_RAW_REQUIRED`
- `EXPLICITLY_REPLACEABLE_NOT_REQUIRED_FOR_SCIENTIFIC_RECOVERY`
- `FAILED_CLOSED_<reason>`

The global closeout must report:

```text
P1_DISCOVERED=62
P1_LOCAL_SHA_CLOSED=62
P2_FINAL_DISCOVERED=<n>
P2_FINAL_LOCAL_SHA_CLOSED=<n>
P2_FINAL_DUPLICATE=<n>
P2_FINAL_REPLACEABLE_SKIPPED=<n>
P2_FINAL_FAILED=<n>
SCIENTIFIC_REMOTE_ONLY_REQUIRED=<n>
REMOTE_DELETION_COUNT=0
ENDPOINT_INDEPENDENCE_STATUS=<status>
```

Target acceptance is:

```text
P2_FINAL_FAILED=0
SCIENTIFIC_REMOTE_ONLY_REQUIRED=0
REMOTE_DELETION_COUNT=0
```

If the only remaining issue is endpoint independence (for example data copied only to a provider-persistent mount), report that explicitly and keep the Goal open until the configured self-owned destination is also SHA-closed or the user explicitly accepts provider-only retention.

## Receipts and commits

Continue using the independent recovery branch.  Publish:

- `P2_FINAL_SCIENTIFIC_COPYBACK_RECEIPT_V1.json`
- `GLOBAL_SCIENTIFIC_COPYBACK_RECONCILIATION_V1.json`

Update `POST_RESTART_RECOVERY_RECEIPT_V1.json` with a compact final summary; do not rewrite or delete prior closed entries.

Commit and push incremental receipt checkpoints after each major artifact class, but remain in the same Goal until global reconciliation reaches the acceptance condition.

## GPU / science policy

This merged recovery Goal is transfer-only.  It does not authorize new GPU work and does not weaken any scientific gate.  Current science state remains:

- Llama Q1 PASS;
- Llama Q2 Prefill/Decode dynamic address evidence captured and locally closed;
- Q2 Route-A structural bridge still lacks materialized `C16_ROUTE_A_BRIDGE_REFERENCE_V1`;
- CUTLASS actual-owner closure remains fail-closed;
- representative selection / canary / formal / Route-C remain blocked under the current contract.

Whether to resume rented-GPU scientific work after recovery is a user decision.
