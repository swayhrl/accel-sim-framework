# Codex Goal — node109 coverage qualification, scenario expansion and AWQ formal capture

## Execution identity

Use a fresh worktree/branch based on the accepted Decode producer:

`20ee2e015d3b3eb72b67d03657242887932a925d`

Suggested branch:

`hrl/c16-formal-expansion-109-v4`

Read first:

- `CURRENT_STATE_AND_SCOPE.md`
- `GLOBAL_MEMORY_PATH_COVERAGE_POLICY.md`

This is an unattended GPU Goal. Recoverable failures are sub-goals, not STOP conditions. Do not pause for intermediate approval.

## Goal

Move C16 from a single-scenario Qwen0 baseline toward robust cross-scenario and cross-model formal coverage without weakening identity/configuration standards.

Priority order is adaptive:

1. qualify the current tracer's global-memory path coverage;
2. recover a true fused AWQ deployment as soon as source is available;
3. while AWQ source is unavailable, use the GPU productively for Qwen0 S3/S4 census and only scientifically justified formal captures;
4. give raw Qwen2.5-7B one final exact-configuration admission attempt after reclaiming non-scientific GPU memory consumers.

Do not touch Qwen3-8B or DeepSeek-V2-Lite input authority in this Goal.

## Stage 0 — exact environment and GPU serialization

Before any GPU action:

- acquire the campaign GPU lock;
- confirm no unrelated CUDA compute process is active;
- record driver/CUDA/Torch/NVBit/NCU/NSYS versions and GPU UUID;
- do not overlap NVBit/NCU/NSYS with another profiler;
- do not overlap bulk transfer with formal timing/profiling;
- use fresh processes for each formal replay.

Do not change model dtype, attention backend, context length, batch size, quantization semantics or KV behavior to make a scenario fit.

## Stage 1 — global-memory path coverage audit

Perform a bounded, high-priority coverage audit on representative already-frozen Qwen0 functions before broad replication.

Required representatives:

- Prefill heavy GEMM (`cutlass::Kernel2` exact accepted code object);
- Prefill attention (`pytorch_flash::flash_fwd_kernel` exact accepted code object);
- Decode Early Heavy exact function;
- Decode KV/Attention exact function used by Early/Late.

For each function:

1. obtain complete SM89 SASS/instruction listing for the exact code object/function;
2. enumerate all memory-relevant instructions, not only rows already in `STATIC_MREF_MAP.tsv`;
3. compare against NVBit memory-space/MREF metadata;
4. classify using `GLOBAL_MEMORY_PATH_COVERAGE_POLICY.md`;
5. explicitly inspect for special global-memory paths such as global-to-shared asynchronous/copy instructions **only if present in the exact SASS**;
6. produce a per-function coverage table and coverage status.

If a special path exists and is dynamically relevant:

- attempt a small address-bearing canary;
- if necessary, extend the capture tool in a narrowly scoped way so that the path can be traced;
- qualify terminal/drop/overflow behavior before formal use;
- do not silently promote current direct-MREF evidence to all-global-memory coverage.

If no special path exists in a target function, record the proof and allow `ALL_DETECTED_GLOBAL_PATHS_COVERED` for that exact function/code object only.

Existing V2/V3 runs are not invalidated; they retain direct-GLOBAL-MREF scope.

## Stage 2 — AWQ fused source recovery

The prior blocker was source acquisition/TLS, not a demonstrated SM89 ABI failure.

Check, in order:

1. whether 174-new has already placed a hash-closed source archive under the node164 canonical asset root, suggested:
   `/root/share/mnt164/huangrulin/c16_ai_workload/assets/sources/autoawq_kernels/`
2. whether it can be copied through the established `hrl174new` route;
3. whether direct source acquisition is now possible from node109.

Do not block the entire Goal waiting on network. If source is not yet available, continue to Stage 3 and re-check later.

When source is available:

- verify archive/source SHA against its receipt;
- build in a fresh isolated environment/build directory;
- target SM89 explicitly;
- do not mutate the base Python/Torch environment;
- if a small source compatibility patch is needed, record exact diff and reason;
- produce a local wheel/artifact with SHA receipt.

Validation sequence:

1. `import awq_ext` succeeds in the isolated deployment;
2. small deterministic numerical kernel check against a trusted unfused/reference result;
3. frozen Qwen2.5-7B-AWQ S2_TEXT native smoke uses the exact historical input binding;
4. NSYS confirms the intended fused extension kernel/path is actually executed;
5. output token/checksum is stable across repeated identical runs;
6. freeze a new deployment identity such as `qwen25_7b_awq_autoawq_awqext_sm89`; do not overwrite the prior unfused control deployment.

If source compiles but the fused path is not actually used, do not label it fused.

## Stage 3 — Qwen0 S3/S4 census while AWQ is unavailable or after AWQ qualification

Use only existing historical frozen Qwen2.5-0.5B bindings. No re-tokenization.

Priority scenarios:

- `S3_TEXT`: B1 / T8192 / D16 — long-context axis;
- `S4_STRUCTURED`: B4 / T2048 / D16 — batch axis.

For each:

1. exact native resource admission;
2. stable output identity;
3. bounded NSYS phase census;
4. compare implementation signatures, function names, grid/block shapes, launch population and memory-relevant strata against S2_TEXT.

Do **not** formally trace merely because the scenario exists.

Formal capture is justified only when the census shows a materially new implementation/shape/memory opportunity relevant to the scientific axis.

Preferred formal targets if justified:

- S3: Prefill Attention; Decode KV/Attention early/late if long-context behavior materially differs; heavy compute only if implementation/shape changes materially.
- S4: Prefill Attention and/or heavy compute when batch changes launch shape/population materially; Decode only if census exposes a unique path.

Use the accepted C16WARP1 MREF-sharded mechanism, same-process `ADDRESS_CONTEXT`, and the new global-memory-path coverage qualification. Every accepted run must Pipeline-ACK before it is counted formal.

If S3/S4 map to the same implementation/shape with no meaningful new memory behavior, record a bounded control/audit result and do not duplicate full NVBit data.

## Stage 4 — AWQ S2 formal capture

Once the fused AWQ deployment is qualified, perform a cheap NSYS/static-map portfolio freeze before formal capture.

Select a compact but semantically diverse first wave, approximately:

- quantized/weight-heavy compute;
- quant/dequant or quant-metadata path if it forms a distinct meaningful stratum;
- attention core;
- Decode KV/Attention early and late when the same semantic target can expose KV growth.

For each target:

- exact function/code object/occurrence;
- full direct GLOBAL MREF static set;
- global-memory-path coverage qualification;
- per-shard same-process address context;
- terminal complete, zero overflow/drop;
- Pipeline V1 finalize/transfer/verify/ACK;
- no cross-replay absolute-VA or temporal claims.

If the AWQ fused deployment cannot be qualified after source is genuinely available and reasonable build/ABI repair is attempted, preserve the exact root cause and continue the campaign; do not substitute unfused results as fused evidence.

## Stage 5 — raw Qwen2.5-7B final exact-safe admission attempt

Prior exact recovery reduced the failure to an OOM at a 28MiB allocation. One final attempt is justified only after reclaiming **non-scientific** GPU memory consumers.

Before retry:

- enumerate GPU processes and display/compute consumers;
- terminate only clearly unrelated user-owned compute contexts that can safely be stopped;
- do not automatically kill system/display services that would destabilize the host;
- fresh Python process;
- preserve prior exact settings including FP16/SDPA, exact S2_TEXT binding, `use_cache=True`, allocator recovery, CUDA lazy loading and last-logit optimization where already proven semantically safe.

Forbidden:

- CPU layer offload;
- KV offload;
- lower precision/quantization substitution;
- shorter context/batch change;
- different attention backend merely to fit.

If it still OOMs, finalize `NOT_ADMITTED_MEMORY_CONFIRMED_16GB` with exact free/used VRAM and allocation failure evidence. Do not spend repeated GPU hours on it in this Goal.

## Pipeline and storage

All accepted formal captures go through the already accepted Pipeline V1.

- no direct overwrite of admitted raw;
- no auto-delete after transfer;
- transport failure retries transport only, never reruns a local-closed GPU workload;
- use catalog entries as authority for admitted paths rather than assuming a historical root layout;
- current asset reorganization on node164 must not cause duplicate model copies or mutation of historical snapshots.

## Review pack

Create:

`docs/vm_tlb/review_packs/C16_FORMAL_EXPANSION_109_V4/`

Include at minimum:

- `FINAL_DECISION.json`
- `GLOBAL_MEMORY_PATH_AUDIT.tsv`
- `SPECIAL_PATH_CANARY.tsv`
- `QWEN0_SCENARIO_CENSUS.tsv`
- `QWEN0_FORMAL_TRACE_INDEX.tsv`
- `AWQ_SOURCE_BUILD_RECEIPT.json`
- `AWQ_BACKEND_QUALIFICATION.tsv`
- `AWQ_TARGET_PORTFOLIO.tsv`
- `AWQ_FORMAL_TRACE_INDEX.tsv`
- `RAW7B_FINAL_ADMISSION.tsv`
- `PIPELINE_ACK_INDEX.tsv`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Files may contain `NOT_APPLICABLE`/`NOT_AVAILABLE` rows when a branch of work was legitimately unnecessary or externally unavailable; do not fabricate successful evidence.

## Final decision classes

Use one of:

- `C16_FORMAL_EXPANSION_V4_PASS`
- `C16_FORMAL_EXPANSION_V4_PASS_WITH_DEFERRED_AWQ`
- `C16_FORMAL_EXPANSION_V4_PASS_WITH_SCOPED_EVIDENCE`
- `C16_FORMAL_EXPANSION_V4_PARTIAL_WITH_ROOT_CAUSE`
- `C16_FORMAL_EXPANSION_V4_FAIL`

A PASS does not require raw7B admission. A PASS_WITH_DEFERRED_AWQ is allowed only if source remains externally unavailable after the defined routes are checked; once source is available, reasonable build/ABI recovery is part of the Goal.

Do not STOP on a single target/scenario failure. STOP only after the complete Goal is classified, the review pack is hash-closed, and the branch is pushed.
