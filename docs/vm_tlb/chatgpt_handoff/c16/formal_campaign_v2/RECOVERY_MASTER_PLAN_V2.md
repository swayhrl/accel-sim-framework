# C16 Formal Campaign V2 — Recovery Master Plan

Ownership: ChatGPT
Execution focus: node109 RTX4080, with node174-new analysis support in parallel
Status: authoritative recovery plan after `FORMAL_CAMPAIGN_FAIL` at `3eb1087c710a796797074dca66b1c96228d6fd45`

## 1. Objective

The next goal is not to repeat the failed all-MREF campaign unchanged. It must recover the capture method, fix the AWQ backend where practical, recover the raw Qwen2.5-7B S2 memory margin without changing model semantics, update the campaign matrix, and produce analyzable formal evidence.

The campaign is successful when it produces useful hash-closed data with explicitly stated metric-validity scope. A single-PC canary is never promoted as representative formal evidence.

## 2. Frozen facts from V1

- Qwen2.5-0.5B S2_TEXT FP16/SDPA identity and object map are good.
- RTX4080-local static MREF mapping works.
- Exact attention MREF static index 4110 terminal-closes and produces nonzero addresses.
- Full all-GLOBAL-MREF capture on the complete target launch does not terminal-close with the V1 tracer variants.
- Qwen2.5-7B-AWQ runs, but the actual backend is AutoAWQ unfused because `awq_ext` is unavailable.
- Raw Qwen2.5-7B S2_TEXT misses admission by about 74 MiB in the exact FP16/SDPA configuration.
- Pipeline V1 and the 174-new analysis parser are qualified.

Do not reinterpret these facts or overwrite V1 evidence.

## 3. Recovery workstreams

Run these as one goal, not as serial approval stages.

### A. Capture architecture recovery

Diagnose whether the all-MREF failure is event-volume/backpressure or a correctness/lifecycle bug. Use the known-good single-MREF target as the control.

Recovery order:

1. exact selected launch + all GLOBAL MREFs + single CTA;
2. geometric CTA scaling: 1, 2, 4, 8, ... until a safe terminal-close bound is found;
3. if one-CTA all-MREF still fails, partition the static GLOBAL MREF set into deterministic disjoint groups and test each group on the exact launch;
4. if both paths are insufficient, implement a compact warp-level binary record format with asynchronous bounded drain;
5. only if needed, combine CTA sharding and compact records.

Never fall back to a convenient single PC as the main formal trace.

### B. AWQ fused-kernel recovery

Inspect the exact Python/Torch/CUDA/AutoAWQ ABI first. Prefer building `autoawq-kernels` from source against the active environment and compute capability 8.9 rather than replacing the environment.

A fused AWQ deployment is a new deployment identity and must be named separately from the existing unfused deployment.

### C. Raw Qwen2.5-7B memory recovery

Recover memory without changing weights, input tokens, batch, context length, dtype, attention implementation, or KV semantics.

Use the memory-preserving ladder in `RAW7B_MEMORY_RECOVERY_V2.md`.

### D. Campaign matrix recovery

Never edit the frozen V1 matrix in place. Produce `CAPTURE_CAMPAIGN_V2.tsv` with explicit evidence type, scope, recovery method, target identity, and supported analyses.

### E. Pipeline + analysis

Every accepted formal bundle goes through Pipeline V1. Failed or diagnostic capture products remain diagnostic and are never cataloged as formal.

## 4. Scientific evidence classes

The V2 campaign may produce more than one valid formal evidence class.

### `FULL_LAUNCH_ALL_MREF_ORDERED`

All selected GLOBAL MREFs from the complete target launch terminal-close in one run.

Supports:
- page/cache-line footprint;
- object attribution;
- per-MREF and observed callback-order analysis;
- load/store/atomic composition;
- within-capture order analyses subject to the existing callback-order caveat.

### `CTA_SHARDED_ALL_MREF`

Each shard captures all selected GLOBAL MREFs for a deterministic CTA subset of the exact target launch. Shards are replayed from the same exact frozen model/input/target identity.

Supports:
- per-CTA and aggregate set footprint;
- page/cache-line/object mix;
- within-CTA/within-shard observed order;
- spatial diversity across CTA shards.

Does not support a fabricated global order across shards.

This is preferred over MREF sharding because it preserves all static MREFs within each sampled CTA.

### `MREF_SHARDED_COMPLETE_SET`

Disjoint MREF groups are captured across exact deterministic replays until the selected static GLOBAL MREF set is fully covered.

Supports:
- union footprint;
- per-MREF footprint;
- object attribution;
- load/store/width composition.

Does not support cross-group temporal order or whole-kernel reuse-distance claims.

Use this only when CTA sharding cannot terminal-close.

### `CONTROL_SINGLE_MREF`

Identity/canary only. Never representative formal data.

## 5. Progress policy

Recoverable failures do not stop the goal. Examples:

- one tracer design stalls;
- one target fails;
- one CTA shard is too large;
- `awq_ext` first build fails;
- raw7B still OOMs under one allocator configuration;
- one Pipeline transfer retries.

The goal stops early only for a global blocker that invalidates every useful path, such as persistent GPU/driver failure, corrupted model/input authority, or failure of all exact-address capture mechanisms including the known-good single-MREF control.

## 6. Priority

1. Qwen2.5-0.5B S2_TEXT Prefill Attention and heavy GEMM capture architecture recovery.
2. Qwen2.5-0.5B Decode early/late memory targets.
3. Qwen2.5-7B-AWQ fused backend recovery and S2_TEXT trace targets.
4. Raw Qwen2.5-7B S2_TEXT memory recovery and, if admitted, Prefill formal capture.
5. Llama S0 high-quality replacement capture if time remains.

## 7. Required final decision

Allowed final decisions:

- `FORMAL_CAMPAIGN_V2_PASS`
- `FORMAL_CAMPAIGN_V2_PASS_WITH_SCOPED_EVIDENCE`
- `FORMAL_CAMPAIGN_V2_PARTIAL_WITH_ROOT_CAUSE`
- `FORMAL_CAMPAIGN_V2_FAIL_GLOBAL_BLOCKER`

A PASS does not require every candidate deployment to succeed. It requires at least one high-quality Qwen0 formal target plus a scientifically useful second stratum/model target when technically attainable, with all evidence scope explicit and Pipeline ACK closure.
