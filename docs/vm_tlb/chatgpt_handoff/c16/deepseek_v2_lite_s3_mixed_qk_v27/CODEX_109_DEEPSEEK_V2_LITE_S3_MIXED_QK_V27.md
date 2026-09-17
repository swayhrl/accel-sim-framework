# C16 DeepSeek-V2-Lite S3 mixed-QK context scaling — node109 V27

## Execution mode

Execute in **GOAL MODE** using the normal node109 Linux producer workflow.

This Goal extends the accepted V26 S2 persistent-MLA evidence to S3 long context. It does not reopen the question of whether a clean single-object persistent direct-read target exists. V26 already answered that in the negative for the current runtime.

Use node109's existing Linux Git workflow/authentication. Do not install/configure `gh`, do not switch authentication, and do not use a Windows repository mirror.

Suggested implementation branch:

`hrl/c16-deepseek-v2-lite-s3-mixed-qk-109-v27`

## Accepted upstream authority

Required producer authority:

- branch: `hrl/c16-deepseek-v2-lite-persistent-mla-109-v26`
- HEAD: `afa5b3898ba33ad03f507e20b5312ef28f601c11`
- decision: `C16_DEEPSEEK_V2_LITE_PERSISTENT_MLA_109_V26_PASS_NO_DIRECT_READ_TARGET`

Exact accepted S2 formal run:

`C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v26-qk-mixed_20260917T130000Z_c26c26c26c26`

Evidence class:

`MIXED_PERSISTENT_CACHE_CONSUMER`

Accepted V26 typed dataflow:

`cache_before key/value -> cache.update -> cache_after key/value`

`cache_after key -> QK matmul key_transposed operand`

`cache_after value -> AV matmul value operand`

V26 S2 QK operand composition:

- persistent key prefix positions: 2048
- current appended positions: 1
- do not label this as a clean single-object direct-read target

Accepted S2 formal summary:

- 20 direct-GLOBAL static MREFs
- 16 executed / 4 zero
- 7,116,816 active-lane events
- drop/overflow 0
- full-scope PASS
- positive Pipeline ACK

Do not modify accepted V26 raw/catalog.

---

# Scientific objective

Establish whether the **same typed mixed QK semantic consumer** scales with long context under S3_TEXT without changing its evidence class.

Required scenario:

`S3_TEXT = B1 / T8192 / D16`

The central question is not "does DeepSeek have a direct KV-cache read?". That question is already closed as no for this runtime.

The question is:

> For the actual mixed QK consumer, how do the persistent-prefix component, current-appended component, dynamic event volume, and per-shard page/line footprints change from S2/T2048 to S3/T8192?

Expected semantic structure to test, not assume:

- S2 cache-after length 2049 = 2048 persistent prefix + 1 current append
- S3 first-decode cache-after should be 8193 = 8192 persistent prefix + 1 current append if the runtime semantics remain the same

Do not force an exact 4x claim; measure and report the actual ratios.

---

# Stage 0 — authority and canonical S3 input

Verify model/runtime identity remains the accepted DeepSeek-V2-Lite deployment from V23R1/V26.

Resolve S3_TEXT only from the existing C16 canonical/prospective input authority. Do not author a new prompt and do not retokenize from prose.

Persist:

- exact source authority/ref/path
- payload SHA256
- token count = 8192
- token-matrix/token-sequence hash using the canonical definition for that artifact
- no-retokenization proof

If a unique canonical DeepSeek S3 input cannot be resolved, fail closed before GPU execution.

Reuse C16 identity-gate policy: exact file set/per-file hashes/revision/config/custom code are hard identity; aggregate byte totals are derived sanity metadata.

---

# Stage 1 — exact S3 semantic state

Build the exact S3 first-decode semantic state for the same runtime path used by V26.

Preserve:

- true input/embedding
- true Layer0 attention state
- actual DynamicCache behavior
- actual key/value cache update
- exact first-decode query/key/value tensors
- no synthetic cache or hidden state

Record cache-before and cache-after objects with:

- key shape/dtype/stride/storage range/hash where practical
- value shape/dtype/stride/storage range/hash where practical
- append semantics
- whether append replaces storage with a larger allocation
- logical persistent-prefix span
- current appended span

Require exact/replay equivalence for the selected QK semantic operator before tracing.

---

# Stage 2 — same semantic-target qualification

Target the same semantic role as V26:

`layer0.self_attn.QK_matmul`

Evidence class must remain:

`MIXED_PERSISTENT_CACHE_CONSUMER`

unless runtime evidence forces a different typed classification. Do not upgrade it to direct-read merely because most addresses belong to the persistent prefix.

Re-establish at S3:

- exact function/code-object identity
- grid/block
- exact input/output signature
- same-process ranges for QUERY_CURRENT_TOKEN, PERSISTENT_KEY_PREFIX, CURRENT_KEY_APPEND
- output equivalence

If the function/signature changes at S3, preserve that as a real context-dependent implementation change and do not force static-set comparability.

---

# Stage 3 — fresh static/path closure

Perform fresh SM89 static/path audit for the S3 QK target.

Record:

- direct GLOBAL MREF set
- LDGSTS/global-to-shared paths
- other address-bearing special paths
- load/store semantics
- source-address register extraction derived from actual SASS where needed

Compare to V26 S2 only after exact function/code-object identity is established.

Classify the relation as one of:

- `EXACT_SAME_FUNCTION_AND_STATIC_SET`
- `SAME_FUNCTION_DIFFERENT_STATIC_SET`
- `DIFFERENT_FUNCTION_NOT_DIRECTLY_COMPARABLE`
- `UNKNOWN`

Do not inherit the S2 set by assumption.

---

# Stage 4 — formal S3 capture

Use the known-good V20/V23R1/V26 warp-regsource lifecycle.

For each static address-bearing shard:

- fresh process/output dir
- clear inherited `C16_*` and `CUDA_INJECTION64_PATH`
- explicit function/static selector
- sufficient capacity
- same-process ADDRESS_CONTEXT
- terminal closure
- drop=0
- overflow=0
- `EXECUTED_SHARD` / `ZERO_EXECUTION_PROVEN` partition

Before admission independently decode all shards and require full-scope/occurrence closure.

Typed membership must distinguish at least:

- `QUERY_CURRENT_TOKEN`
- `PERSISTENT_KEY_PREFIX`
- `CURRENT_KEY_APPEND`
- `OTHER_OR_UNCLASSIFIED`

Do not use cross-shard VA union or chronology.

Create exactly one S3 formal run for the mixed QK semantic target.

Formal admission rule:

`FORMAL_ADMISSION_CONCURRENCY=1`

Transfer, verify, admit, and wait for positive ACK before moving to final analysis.

---

# Stage 5 — independent S2 vs S3 context-scaling analysis

Use exact accepted S2 V26 run and the new S3 run.

Compare independently decoded evidence:

- static function/set relation
- executed/zero partition
- active-lane events
- query-current events
- persistent-prefix events
- current-append events
- per-shard 128B line distribution
- per-shard 4K/64K/2M page distributions
- CTA/full-scope properties
- typed NCU status

For aggregate unique counts, use per-shard distributions or explicitly label `SUM_OF_PER_SHARD_UNIQUES`. Never construct a cross-shard VA union unless semantics are separately proven.

Required ratios:

- context length ratio
- cache-after logical length ratio
- total event ratio
- persistent-prefix event ratio
- current-append event ratio
- query-current event ratio

Do not call the result exactly 4x unless the measured endpoint actually equals 4x.

Interpretation boundaries:

- allowed: context-sensitive scaling of this typed mixed QK consumer
- not allowed: whole-model cache/TLB behavior, reuse distance, temporal locality, absolute VA comparison, cache/TLB causality

---

# Stage 6 — next-step decision

After S3 closure, decide whether DeepSeek MLA lineage is sufficiently closed for C16 stratified sampling.

Preferred decision if evidence closes cleanly:

`DEEPSEEK_MLA_S2_S3_MIXED_QK_SCALING_CLOSED_FOR_C16_STRATIFICATION`

Otherwise emit a typed blocker/delta, not another coverage-density capture request.

Do not automatically run another DeepSeek operator or S4 scenario in this Goal.

---

# Required review pack

Create:

`docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_S3_MIXED_QK_109_V27/`

Include at least:

- `UPSTREAM_AUTHORITY.tsv`
- `S3_INPUT_AUTHORITY.json`
- `S3_STATE_AND_CACHE_RECEIPT.json`
- `S3_QK_TARGET_QUALIFICATION.json`
- `S3_STATIC_PATH_AUDIT.json`
- `S3_FORMAL_SUMMARY.json`
- `S3_ADMISSION_ACK.json`
- `S2_VS_S3_MIXED_QK_SCALING.json`
- `NCU_TYPED_EVIDENCE.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_AUTHORIZATION.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Full PASS may use:

`C16_DEEPSEEK_V2_LITE_S3_MIXED_QK_109_V27_PASS`

only if the S3 semantic target closes, complete formal capture is admitted, and positive ACK is received.

---

# Git / cleanup

Use existing node109 Git transport.

Do not install `gh`.

Complete:

`review pack -> hash close -> commit -> push -> canonical git ls-remote verification -> clean worktree`

GPU actions must acquire `/data/c16/locks/c16_gpu_campaign.lock` normally.

At end release lock, verify no profiler/DeepSeek CUDA process remains, confirm GPU baseline, and STOP.

Do not stop after S3 state generation if downstream formal stages remain executable.