# Codex Goal — 174-new V5 LDGSTS integration

## Execution base

Start from accepted 174-new analysis state:

`1447bf9bb19bd249c116f53287a1f768170848c7`

Producer authority to consume:

`hrl/c16-ldgsts-special-path-109-v5 @ ea43fa6331dcb2d7d6553f6a48000bdd004458e0`

Suggested branch:

`hrl/c16-ldgsts-analysis-174new-v6`

Use the **mainline 174-new Codex window/worktree**, not the separate asset-readiness window.

CPU-only. No GPU workload.

## Goal

Independently ingest, rehash, decode, and scientifically integrate the five V5 LDGSTS GLOBAL-SOURCE formal bundles with the already accepted Qwen0 direct-GLOBAL-MREF analysis baseline.

The output must answer what the newly captured special path adds for:

- S2 Prefill GEMM;
- S2 Prefill Attention;
- S2 Decode Early KV/Attention;
- S2 Decode Late KV/Attention;
- S3 Prefill Attention.

## Required work

### 1. Independent V5 closure

For each of the five V5 Pipeline-ACKed runs:

- resolve catalog entry and raw path from node164;
- independently rehash RUN_MANIFEST and all declared artifacts;
- validate frozen static LDGSTS set identity/count;
- validate every shard terminal status;
- validate executed vs ZERO_EXECUTION_PROVEN classification;
- require overflow=0 and drop=0;
- verify per-shard `C16_ADDRESS_CONTEXT_V1` binding;
- verify operand qualification is bound to operand 1 as GLOBAL SOURCE.

Do not trust producer summaries without raw/manifest cross-check.

### 2. Special-path parser semantics

Decode only the GLOBAL-SOURCE address recorded from LDGSTS operand 1.

Treat LDGSTS width as exact only when the hash-bound SASS/static metadata explicitly proves the width. For `LDGSTS...128`, 16 bytes is acceptable only after exact opcode/SASS validation.

Emit per-shard:

- active lane address events;
- start-address unique VA;
- 4K/64K/2M start page buckets;
- 128B start line buckets;
- exact touched pages/lines where width is exact;
- semantic object attribution only from the same-process address context.

### 3. Object attribution

Use each shard's own same-process address context only.

Attempt conservative attribution to existing classes such as:

- WEIGHT;
- KV_CACHE;
- ACTIVATION;
- UNKNOWN_RUNTIME.

If active addresses do not lie in a hash-bound range, retain `UNKNOWN_RUNTIME`.

Never classify a shard using another CUDA process's object map.

### 4. Direct + LDGSTS set-level integration

For matching target function/occurrence, combine the accepted direct path and new LDGSTS path into a **coverage inventory**, not a fabricated physical stream.

Allowed combined statements:

- direct static set closure;
- LDGSTS static set closure;
- per-path executed/zero counts;
- per-path event counts;
- per-path read/write semantics;
- per-path object composition;
- set-level coverage label `ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL` when the V4/V5 full-function audit supports it.

Forbidden unless separately proven:

- absolute-VA union across direct and LDGSTS replays;
- cross-path order;
- cross-path reuse distance;
- physical whole-kernel footprint.

### 5. Decode Early vs Late

This is the highest-priority scientific comparison.

Compare S2 Decode Early occurrence 24 against Late occurrence 767 for the LDGSTS global-source path:

- same static-set identity;
- executed/zero set relation;
- event-count change;
- per-shard/page/line footprint change;
- object-class composition;
- object-relative offsets only if a common semantic object identity is independently proven.

Do not use absolute VA across replay processes.

### 6. S2 vs S3 Attention scaling

Compare the special-path behavior of S2 and S3 Prefill Attention, preserving the known long-context grid change.

Focus on normalized/count-based and object-relative evidence; do not merge cross-run absolute VAs.

### 7. Regression / immutability

Preserve:

- prior Qwen0 direct-path accepted results;
- RTX3090 Q2 exact regressions;
- raw immutability;
- prior accepted review packs.

Do not rewrite old packs.

## Review pack

Create:

`docs/vm_tlb/review_packs/C16_LDGSTS_ANALYSIS_174NEW_V6/`

Include at minimum:

- `RUN_VERIFICATION.tsv`
- `OPERAND_BINDING_AUDIT.tsv`
- `SPECIAL_PATH_FINGERPRINT.tsv`
- `OBJECT_ATTRIBUTION.tsv`
- `DIRECT_PLUS_LDGSTS_COVERAGE.tsv`
- `DECODE_EARLY_LATE_SPECIAL_COMPARISON.tsv`
- `S2_S3_SPECIAL_COMPARISON.tsv`
- `REGRESSION_RESULTS.tsv`
- `DERIVED_RECEIPT.json` with output path/size/SHA entries
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Expected success label:

`C16_LDGSTS_ANALYSIS_174NEW_V6_PASS`

or fail closed with a specific narrower result.

Commit/push the review pack and STOP.
