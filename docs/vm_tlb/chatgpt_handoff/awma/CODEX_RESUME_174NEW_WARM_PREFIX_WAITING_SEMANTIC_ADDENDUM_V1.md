# CODEX RESUME — 174-new Warm Prefix Waiting Semantic Addendum V1

Status: MAINLINE SUPPORT / NO NEW SCIENCE RUN REQUIRED.

Parent execution:

```text
hrl/awma-q05-warm-prefix-replay-174new-v1
5b9d708087e8ff485f03fd561a15e08baea8ad3a
```

Current stage state remains:

`AWMA_Q05_WARM_PREFIX_REPLAY_174NEW_V1_WAITING_FOR_CONTEXT_BUNDLE`

This addendum closes documentation/source semantics only while waiting for the 109 formal 35-member context bundle.

## Why this addendum exists

The current V1.1 matrix still contains:

```text
L2_data    CONFIG_DEPENDENT
L1_L2_TLB PERSISTS_BY_SELF_WARM_DIAGNOSTIC
```

This is too compressed for later interpretation.

No new warm replay is required to fix this.

## Required source-backed closure

### 1. Actual F0 data-cache boundary

Use the accepted F0 config authority:

`configs/vm_tlb/c5_configs/C11_C5_PREFILL_F0.config`

and accepted core:

`57bb71ecd015b6ec0ab32e45b0815e5beaf69172`

Record separately:

- F0 explicitly sets `-gpgpu_flush_l1_cache 1`.
- F0 does not override `-gpgpu_flush_l2_cache`.
- accepted core registers `-gpgpu_flush_l2_cache` with default `0`.
- therefore the effective F0 kernel-boundary policy is:
  - L1 data cache flushed/invalidate-at-completion under existing source semantics;
  - L2 data cache not flushed by the kernel-completion flush option and may retain resident/replacement state across dispatch.

Do not claim real RTX4080 hardware has identical persistence.

### 2. Separate L1 and L2 TLB statements

Do not use one `L1_L2_TLB` row.

Record separately:

- L2 TLB: directly supported by self-warm result because Q05 #2 had 2922 L2 accesses / 2922 hits / 0 misses and no new walks.
- L1 TLB: use accepted source lifetime/flush audit. The translation controller owns its L1 TLB vector and is a simulator member; shader/CTA reinit does not reconstruct/flush it. Explicit translation flush functions exist for invalidation/shootdown paths and are not invoked merely by the normal F0 kernel dispatch boundary. If direct runtime L1 persistence telemetry is unavailable, label it `PERSISTS_BY_SOURCE_NOT_DIRECTLY_RUNTIME_DUMPED`, not `PERSISTS_BY_SELF_WARM_DIAGNOSTIC`.

### 3. PWC

Keep PWC conservative:

`PERSISTS_BY_SOURCE_PENDING_DIRECT_RUNTIME_OBSERVABILITY`

only if the source audit shows it is owned by the persistent translation controller and no normal kernel-boundary flush path touches it.

Do not convert this to a measured-residency claim.

### 4. Interpretation

Update self-warm interpretation to say:

- second-Q05 translation was fully warm at L2 in the modeled simulator;
- F0 also retains L2 data-cache state while flushing L1 data cache;
- therefore the 64,255-cycle reduction is a **combined modeled warm-context effect**, not a translation-only speedup.

## Deliverables

Update only:

```text
docs/vm_tlb/review_packs/AWMA_Q05_WARM_PREFIX_REPLAY_174NEW_V1/
  F0_KERNEL_BOUNDARY_STATE_MATRIX_V1_1.tsv
  SELF_WARM_INTERPRETATION_V1_1.md
  SOURCE_SEMANTIC_ADDENDUM.md
  SHA256SUMS
```

Optionally append a one-paragraph addendum to:

`docs/vm_tlb/codex_handoff/awma/Q05_WARM_PREFIX_REPLAY_174NEW_V1_REPORT.md`

Do not run a new simulation.

Do not change the WAITING status.

Commit, push, remote verify, clean worktree, STOP.
