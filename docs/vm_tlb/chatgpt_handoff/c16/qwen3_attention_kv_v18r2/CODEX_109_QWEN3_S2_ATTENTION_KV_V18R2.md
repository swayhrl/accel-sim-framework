# CODEX GOAL — C16 Qwen3-8B S2 Attention/KV Dataflow Qualification V18R2 (node109)

## Execution mode

IMPORTANT: execute this task in GOAL MODE. This is not planning-only, review-only, or a request to merely summarize the blocker.

Continue the existing Qwen3 S2 Attention/KV scientific target from V18/V18R1. Do not create a different semantic target merely to obtain PASS.

Base producer evidence:
- V18R1 HEAD: `d6553329064968f266e2decf27e594a4d695cdea`
- exact model/revision: `Qwen/Qwen3-8B` / `b968826d9c46dd6066d109eabc6255188de91218`
- exact S2 V2 input payload SHA256: `5913c573054d23a444477394a60f3f280311325e81175663b4ae2abd5ef6aafb`
- corrected first-decode layer0 self-attention replay is already bitwise PASS with cache length 2048 -> 2049.
- preexisting KV ranges are already captured and hash-bound.

Suggested implementation branch:
`hrl/c16-qwen3-s2-attention-kv-109-v18r2`

Expected review pack:
`docs/vm_tlb/review_packs/C16_QWEN3_S2_ATTENTION_KV_109_V18R2/`

## Why V18R1 blocked

Do not treat V18R1 as proof that Attention/KV is scientifically impossible.

Transformers 4.51.0 eager Qwen3 attention has this semantic dataflow:

1. `past_key_value.update(...)`
2. `repeat_kv(key, num_key_value_groups)`
3. `repeat_kv(value, num_key_value_groups)`
4. `torch.matmul(query, key_states.transpose(2,3))`
5. softmax/dropout
6. `torch.matmul(attn_weights, value_states)`

Therefore the core QK / AV kernels may consume KV-derived repeated working buffers rather than the original preexisting DynamicCache storage directly.

V18R1 only proved that the whole `self_attn` NVTX range contains mixed kernels and that no non-projection core kernel could be losslessly joined directly to the original K/V storage range.

V18R2 must determine the actual dataflow instead of assuming direct original-storage consumption.

## P0 — Preserve accepted evidence

Preserve V18 and V18R1 BLOCKED packs as immutable history.

Do not:
- recapture/re-admit the accepted MLP target;
- mutate accepted raw/catalog;
- reinterpret launch order as semantics;
- switch attention backend, precision, model, scenario, or input;
- use S3.

## P1 — Prove local implementation contract

Using the exact installed Transformers 4.51.0 runtime, record and hash-close:
- source file SHA256 for `modeling_qwen3.py`;
- exact source/AST or inspected lines for `Qwen3Attention.forward`, `eager_attention_forward`, and `repeat_kv`;
- `_attn_implementation` actually used in the qualified run;
- `num_attention_heads`, `num_key_value_heads`, `num_key_value_groups`, `head_dim`.

Require the actual deployment to be eager attention before using the eager-specific semantic subranges below. Otherwise BLOCK with the concrete implementation mismatch.

## P2 — Instrument semantic subranges without changing math

Create an instrumentation-only wrapper for the exact eager attention function. It must execute the same tensor operations in the same order as the accepted Transformers 4.51.0 function, with only NVTX/metadata collection added.

Use separate nested NVTX ranges at minimum:
- `C16_V18R2_KV_REPEAT_K`
- `C16_V18R2_KV_REPEAT_V`
- `C16_V18R2_ATTN_QK_MATMUL`
- `C16_V18R2_ATTN_SOFTMAX`
- `C16_V18R2_ATTN_AV_MATMUL`

Record before/after every relevant operation:
- tensor shape/dtype/stride;
- `data_ptr`;
- underlying storage data pointer and storage byte size where supported;
- whether tensors alias the original cache tensor/storage;
- whether `repeat_kv` output aliases or materializes a new buffer;
- SHA256 of tensor bytes for deterministic small/control artifacts when practical.

Also instrument/record the return tensors of `past_key_value.update` so the chain distinguishes:
- `PREEXISTING_KV_STORAGE`
- `POST_UPDATE_KV_STORAGE`
- `KV_DERIVED_REPEAT_BUFFER`

Do not call a KV-derived repeated buffer the original KV cache.

## P3 — Instrumentation equivalence gate

Run the exact previously-qualified first-decode layer0 self-attention twice:
1. uninstrumented corrected baseline;
2. instrumentation-only wrapper.

Require:
- bitwise output equality;
- `max_abs = 0`;
- identical cache length progression;
- same semantic input/state hashes;
- no backend/config change.

Use NSYS to compare the kernel sequence/signatures for each semantic subrange. NVTX-only instrumentation must not introduce a different scientific implementation.

If instrumentation changes the scientific kernel implementation materially, BLOCK.

## P4 — Establish typed KV dataflow evidence

Produce a machine-readable dataflow graph/receipt showing, separately for K and V:

`PREEXISTING_KV_STORAGE -> POST_UPDATE_KV_STORAGE -> KV_DERIVED_REPEAT_BUFFER -> ATTENTION_CORE_OPERAND`

For each edge, label evidence as one of:
- `DIRECT_ALIAS`
- `EXACT_TENSOR_DERIVATION`
- `COPY_MATERIALIZATION_PROVEN`
- `PENDING`
- `NOT_APPLICABLE`

Key questions to answer experimentally, not by assumption:
- Does `DynamicCache.update` allocate/materialize a new 2049-token cache tensor?
- Does `repeat_kv` for 8 -> 32 heads materialize a new working buffer?
- Does QK matmul consume the K repeated buffer?
- Does AV matmul consume the V repeated buffer?

## P5 — Candidate qualification policy

There are now two scientifically distinct admissible evidence classes.

### Class A — `KV_STORAGE_DIRECT_READ`
A kernel is eligible if its dynamic source addresses losslessly overlap the directly-captured KV storage range for the exact same process/state.

Examples may include cache-update / repeat materialization source reads if they are proven to read the old K/V cache.

### Class B — `KV_DERIVED_ATTENTION_CORE_READ`
A QK or AV attention-core kernel is eligible if all of the following are proven:
1. the operand tensor is an exact same-process `KV_DERIVED_REPEAT_BUFFER` produced from the captured K/V state;
2. semantic subrange NVTX isolates QK or AV without launch-order inference;
3. dynamic source addresses losslessly overlap that derived buffer range;
4. instrumentation equivalence passes;
5. the target is not q/k/v/o projection GEMV.

Class B must be labeled as KV-derived working-buffer traffic, not direct cache-storage traffic.

This policy is intentionally stricter and more accurate than pretending the core kernel reads the original DynamicCache storage directly.

## P6 — Dynamic address qualification

For each candidate semantic subrange:
- perform a scoped dynamic address probe sufficient to identify source address-bearing instructions and ranges;
- bind source ranges to the typed objects from P4;
- do not rely on kernel launch ordinal as semantic identity;
- use the semantic NVTX subrange + exact tensor/range identity.

Prefer, in order:
1. one K-backed QK core target (`KV_DERIVED_ATTENTION_CORE_READ`), if qualified;
2. one V-backed AV core target (`KV_DERIVED_ATTENTION_CORE_READ`), if qualified;
3. if core targets cannot be qualified but direct cache-storage materialization reads are losslessly proven, preserve them as `KV_STORAGE_DIRECT_READ` evidence but do not silently relabel them as QK/AV.

At least one qualified attention/KV evidence target is required for PASS. A direct-storage materialization target may support a scoped PASS only if the review pack explicitly states that no QK/AV core target was formalized.

## P7 — Fresh static/global-address-path audit

For every target promoted beyond qualification:
- fresh SASS/static audit;
- enumerate direct GLOBAL MREF;
- independently identify LDGSTS GLOBAL_SOURCE if present;
- classify control-only instructions separately;
- no reuse of MLP static sets;
- complete set rule: executed + `ZERO_EXECUTION_PROVEN` = full static address-bearing set.

Any unexpected uninstrumented address-bearing path blocks that target.

## P8 — Formal capture/admission

Only after P2-P7 pass for a target:
- perform complete formal capture;
- drop/overflow must be zero;
- same-process context must bind the typed storage/derived ranges used for the target;
- local close first;
- `FORMAL_ADMISSION_CONCURRENCY=1`;
- acquire the global admission lock;
- wait for positive Pipeline ACK before any optional second admission.

Do not create a formal bundle for an unqualified target.

## P9 — NCU and compact fingerprint

For every formally accepted target:
- application replay;
- cache-control none;
- retain exact metric descriptors;
- preserve raw displayed values/units exactly;
- no inferred unit conversion;
- produce compact event/page/line/object fingerprint under established C16 evidence boundaries.

## P10 — Final outputs

The review pack must include at minimum:
- `IMPLEMENTATION_CONTRACT.json`
- `INSTRUMENTATION_EQUIVALENCE.json`
- `KV_DATAFLOW_GRAPH.json`
- `KV_TENSOR_RANGES.tsv`
- `SEMANTIC_SUBRANGE_KERNEL_CENSUS.tsv`
- `TARGET_QUALIFICATION.tsv/json`
- if formalized: fresh static audit, shard closure, context receipt, Pipeline ACK receipt, NCU/fingerprint artifacts
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Allowed outcomes:
- `C16_QWEN3_S2_ATTENTION_KV_109_V18R2_PASS`
- `C16_QWEN3_S2_ATTENTION_KV_109_V18R2_PASS_WITH_SCOPED_EVIDENCE`
- `C16_QWEN3_S2_ATTENTION_KV_109_V18R2_BLOCKED_<specific_gate>`

`PASS_WITH_SCOPED_EVIDENCE` is allowed only when at least one real KV evidence target is formally accepted and remaining scope is explicitly narrower (for example direct KV-storage materialization accepted but QK/AV core unqualified, or K accepted but optional V not distinct).

If no target satisfies Class A or Class B qualification, BLOCK.

## GOAL MODE stop rule

Do not stop after instrumentation implementation, dataflow discovery, or candidate census if downstream qualification/formal stages remain executable.

Continue automatically through the full Goal until PASS/scoped PASS or a genuine fail-closed blocker.

Commit/push the final implementation branch and review pack, report branch/HEAD/decision and the exact qualified target class(es), then STOP.
